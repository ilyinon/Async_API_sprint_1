from http import HTTPStatus
from typing import Annotated, Literal, Optional
from uuid import UUID

from core import config
from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException, Query
from models.base import OrjsonBaseModel
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(OrjsonBaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


@router.get(
    "",
    response_model=list[Film],
    summary="Список фильмов",
    description="Получить список фильмов",
)
async def films_list(film_service: FilmService = Depends(get_film_service)):
    films = await film_service.get_list()
    return [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    "/search",
    response_model=list[Film],
    summary="Поиск фильмов",
    description="Получить список найденных фильмов",
)
async def search_film(
    query: Annotated[str, Query(description="Запрос")],
    film_service: FilmService = Depends(get_film_service),
):
    films = await film_service.search_film(query)
    return [
        Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get("/{film_id}", response_model=Film)
async def film_details(
    film_id: UUID, film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)

    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail=f"film with id {film_id} not found"
        )

    return Film(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
