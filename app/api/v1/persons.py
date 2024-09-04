from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from models.base import OrjsonBaseModel
from services.person import PersonService, get_person_service

router = APIRouter()


class PersonFilm(OrjsonBaseModel):
    id: UUID  # ID of film
    roles: list[str]


class Person(OrjsonBaseModel):
    uuid: UUID
    full_name: str
    films: list[PersonFilm]


@router.get(
    '',
    response_model=list[Person],
    summary='Список персонажей',
    description='Получить список персонажей'
)
async def person_list(person_service: PersonService = Depends(get_person_service)):
    persons = await person_service.get_list()
    persons_response = []
    for person in persons:
        films = []
        for film in person.films:
            films.append(PersonFilm(id=film.id, roles=film.roles))
        persons_response.append(Person(uuid=person.id, full_name=person.full_name, films=films))
    return persons_response


@router.get(
    '/{person_id}',
    response_model=Person,
    summary='Страница персонажа',
    description='Данные по конкретному персонажу'
)
async def person_details(person_id: UUID, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"person with id {person_id} not found"
        )
    films = []
    for film in person.films:
        films.append(PersonFilm(id=film.id, roles=film.roles))

    return Person(uuid=person.id, full_name=person.full_name, films=films)
