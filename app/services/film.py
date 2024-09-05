import logging
from functools import lru_cache
from typing import List, Optional, Tuple
from uuid import UUID
from app.db.elastic import get_elastic
from app.db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from app.models.film import Film
from app.models.genre import Genre
from app.models.person import Person
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 minutes

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
        # Convert UUID to string for cache and Elasticsearch
        film_id_str = str(film_id)

        # Attempt to get film data from cache first
        film = await self._film_from_cache(film_id_str)
        if not film:
            # If film is not in cache, get it from Elasticsearch
            film = await self._get_film_from_elastic(film_id_str)
            if not film:
                # If film is not in Elasticsearch, it does not exist
                return None
            # Save film data to cache
            await self._put_film_to_cache(film)

        return film

    async def get_films(
        self,
        sort: str = "-imdb_rating",
        genre: Optional[UUID] = None,
        page: int = 1,
        size: int = 10,
    ) -> Tuple[int, List[Film]]:
        """
        Retrieve a list of films with pagination, sorting, and optional genre filtering.
        """
        # Create the search query
        search_query = {
            "query": {"bool": {"must": [], "filter": []}},
            "sort": [{sort: {"order": "desc" if sort.startswith("-") else "asc"}}],
            "from": (page - 1) * size,
            "size": size,
        }

        # Apply genre filter if provided
        if genre:
            search_query["query"]["bool"]["filter"].append(
                {"term": {"genres.id": str(genre.id)}}
            )

        # Perform the search
        response = await self.elastic.search(index="movies", body=search_query)
        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]
        return total, [Film(**hit["_source"]) for hit in hits]

    async def search_films(self, query: str, page: int = 1, size: int = 10):
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description", "actors.name", "genres.name"],
                }
            },
            "from": (page - 1) * size,
            "size": size,
        }

        response = await self.elastic.search(index="movies", body=search_query)
        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]
        return total, [Film(**hit["_source"]) for hit in hits]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        # try:
            doc = await self.elastic.get(index="movies", id=film_id)
            genres = doc["_source"].get("genres", [])
            logger.info("genres list: %s", genres)
            genres_list = []
            for genre in genres:
                response = await self.elastic.search(
                    index="genres", query={"multi_match": {"query": genre}}
                )

                genres_list.append(response["hits"]["hits"][0]["_source"])
            actors = doc["_source"].get("actors", [])
            if isinstance(actors, str):
                actors = []

            writers = doc["_source"].get("writers", [])
            if isinstance(writers, str):
                writers = []

            directors = doc["_source"].get("directors", [])
            if isinstance(directors, str):
                directors = []
        except NotFoundError:
            logger.error(f"Film with ID {film_id} not found in Elasticsearch")
            return None

        film_data = {
            "id": doc["_source"].get("id"),
            "title": doc["_source"].get("title"),
            "imdb_rating": doc["_source"].get("imdb_rating"),
            "description": doc["_source"].get("description", ""),
            "genres": genres_list,
            "actors": [
                {"id": actor.get("id"), "full_name": actor.get("name")}
                for actor in actors
                if isinstance(actor, dict)
            ],
            "writers": [
                {"id": writer.get("id"), "full_name": writer.get("name")}
                for writer in writers
                if isinstance(writer, dict)
            ],
            "directors": [
                {"id": director.get("id"), "full_name": director.get("name")}
                for director in directors
                if isinstance(director, dict)
            ],
        }
        logger.info("Film details | %s", film_data)
        return FilmDetail(**film_data)

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        # Attempt to retrieve the film data from the cache
        data = await self.redis.get(film_id)
        if not data:
            return None

        # Parse the cached JSON data into a Film model
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Save the film data to the cache with an expiration time
        await self.redis.set(str(film.id), film.json(), ex=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
