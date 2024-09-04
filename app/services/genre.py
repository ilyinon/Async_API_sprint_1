import logging
from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5

logger = logging.getLogger(__name__)


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: UUID) -> Optional[Genre]:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def get_list(self):
        try:
            genres_list = await self.elastic.search(
                index="genres", query={"match_all": {}}
            )
        except NotFoundError:
            return None
        logger.info("%s", genres_list)
        return [Genre(**get_genre["_source"]) for get_genre in genres_list["hits"]["hits"]]

    async def _get_genre_from_elastic(self, genre_id: UUID) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        answer = {}
        answer["id"] = doc["_source"]["id"]
        answer["name"] = doc["_source"]["name"]
        return Genre(**answer)

    async def _genre_from_cache(self, genre_id: UUID) -> Optional[Genre]:
        data = await self.redis.get(str(genre_id))
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, genre: Genre):
        await self.redis.set(str(genre.id), genre.json(), GENRE_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
