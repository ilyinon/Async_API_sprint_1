import logging
from functools import lru_cache
from typing import Optional
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film, FilmDetail
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> Optional[FilmDetail]:
        film = await self._get_film_from_elastic(film_id)
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self._put_film_to_cache(film)

        return film

    async def get_list(self, sort, genre, page_size, page_number):
        query = {"match_all": {}}
        logger.info("Search type %s", sort)
        sort_type = "asc"
        if sort[0].startswith("-"):
            sort_type = "desc"
        genre_response = await self.elastic.search(
            index="genres", query={"multi_match": {"query": genre}}
        )
        genre_names = " ".join(
            [genre["_source"]["name"] for genre in genre_response["hits"]["hits"]]
        )

        logger.info("Genre list %s", genre_names)

        query = {"match": {"genres": genre_names}}

        try:
            films_list = await self.elastic.search(
                index="movies",
                body={
                    "query": query,
                    "sort": [{"imdb_rating": {"order": sort_type}}],
                    "from": (page_size - 1) * page_number,
                    "size": page_size,
                },
            )
            logger.info("Found %s", films_list)
        except NotFoundError:
            return None
        return [Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]]

    async def search_film(self, query):
        try:
            films_list = await self.elastic.search(
                index="movies", query={"multi_match": {"query": query}}
            )
        except NotFoundError:
            return None
        logger.info("%s", films_list)
        return [Film(**get_film["_source"]) for get_film in films_list["hits"]["hits"]]

    async def _get_film_from_elastic(self, film_id: UUID) -> Optional[FilmDetail]:
        try:
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

    async def _film_from_cache(self, film_id: UUID) -> Optional[Film]:
        data = await self.redis.get(str(film_id))
        if not data:
            return None

        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)