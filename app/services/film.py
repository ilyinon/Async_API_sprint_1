import logging
from functools import lru_cache
from typing import Optional
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from models.film import Film
from redis.asyncio import Redis

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

logger = logging.getLogger(__name__)


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: UUID) -> Optional[Film]:
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

    async def get_list(self):
        try:
            films_list = await self.elastic.search(
                index="movies", query={"match_all": {}}
            )
        except NotFoundError:
            return None
        logger.info("%s", films_list)
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

    async def _get_film_from_elastic(self, film_id: UUID) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index="movies", id=film_id)
        except NotFoundError:
            return None
        answer = {}
        answer["id"] = doc["_source"]["id"]
        answer["title"] = doc["_source"]["title"]
        answer["imdb_rating"] = doc["_source"]["imdb_rating"]
        # return Film(**doc['_source'])
        return Film(**answer)

    async def _film_from_cache(self, film_id: UUID) -> Optional[Film]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(str(film_id))
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(str(film.id), film.json(), FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
