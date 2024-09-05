import logging
from functools import lru_cache
from typing import List, Optional
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film
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
    
    async def search_films(self, query: str, page: int = 1, size: int = 10):
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description", "actors.name", "genres.name"]
                }
            },
            "from": (page - 1) * size,
            "size": size
        }

        response = await self.elastic.search(index='movies', body=search_query)
        total = response['hits']['total']['value']
        hits = response['hits']['hits']
        return total, [Film(**hit['_source']) for hit in hits]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
            logger.info(f"Elasticsearch response for film {film_id}: {doc}")

            genres = doc["_source"].get("genres", [])
            if isinstance(genres, str):
                genres = []

            actors = doc["_source"].get("actors", [])
            if isinstance(actors, str):
                actors = []

            writers = doc["_source"].get("writers", [])
            if isinstance(writers, str):
                writers = []

            directors = doc["_source"].get("directors", [])
            if isinstance(directors, str):
                directors = []

            film_data = {
                "id": doc["_source"].get("id"),
                "title": doc["_source"].get("title"),
                "imdb_rating": doc["_source"].get("imdb_rating"),
                "description": doc["_source"].get("description", ""),
                "genres": [
                    {"id": genre.get("id"), "name": genre.get("name")}
                    for genre in genres
                    if isinstance(genre, dict)
                ],
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
                ]
            }

            return Film(**film_data)

        except NotFoundError:
            logger.error(f"Film with ID {film_id} not found in Elasticsearch")
            return None
        except Exception as e:
            logger.error(f"Elasticsearch fetch error for film {film_id}: {str(e)}")
            return None

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
