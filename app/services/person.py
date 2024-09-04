import logging
from functools import lru_cache
from typing import Optional
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis
from uuid import UUID

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person, PersonFilm

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5

logger = logging.getLogger(__name__)


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person_films(self, person_id: UUID):
        film_list = await self.elastic.search(
            index='movies',
            query={
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {
                                    "term": {
                                        "directors.id": person_id
                                    }
                                }
                            },
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "term": {
                                        "actors.id": person_id
                                    }
                                }
                            },
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "term": {
                                        "writers.id": person_id
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        )
        person_films = []
        for film in film_list["hits"]["hits"]:
            logger.info("%s", film.get("_source"))
            person_film = PersonFilm(id=film.get("_source").get("id"), roles=[])
            for director in film.get("_source").get("directors"):
                if director["id"] == person_id and "director" not in person_film.roles:
                    person_film.roles.append("director")
            for actor in film.get("_source").get("actors"):
                if actor["id"] == person_id and "actor" not in person_film.roles:
                    person_film.roles.append("actor")
            for writer in film.get("_source").get("writers"):
                if writer["id"] == person_id and "writer" not in person_film.roles:
                    person_film.roles.append("writer")
            person_films.append(person_film)
        return person_films

    async def get_by_id(self, person_id: UUID) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def get_list(self):
        try:
            persons_list = await self.elastic.search(
                index="persons", query={"match_all": {}}
            )
        except NotFoundError:
            return None
        for get_person in persons_list["hits"]["hits"]:
            logger.info(get_person["_source"])
            get_person["_source"]["films"] = await self.get_person_films(get_person["_source"]["id"])
        return [Person(**get_person["_source"]) for get_person in persons_list["hits"]["hits"]]

    async def _get_person_from_elastic(self, person_id: UUID) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        answer = {}
        answer["id"] = doc["_source"]["id"]
        answer["full_name"] = doc["_source"]["full_name"]

        films = await self.get_person_films(person_id)
        answer["films"] = films
        return Person(**answer)

    async def _person_from_cache(self, person_id: UUID) -> Optional[Person]:
        data = await self.redis.get(str(person_id))
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(str(person.id), person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
