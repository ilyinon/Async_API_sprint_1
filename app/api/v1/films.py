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
async def films_list(
    film_service: FilmService = Depends(get_film_service),
    page_size: Annotated[int, Query(description="Фильмов на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
) -> Film:
    films = await film_service.get_list(page_size, page_number)
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
