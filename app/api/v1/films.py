from http import HTTPStatus
from typing import Annotated, List, Literal, Optional
from uuid import UUID

from core import config
from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException, Query
from models.base import OrjsonBaseModel
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class FilmResponse(OrjsonBaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


class PersonResponse(BaseModel):
    id: Optional[str]
    full_name: str


class GenreResponse(BaseModel):
    id: Optional[str]
    name: str


class FilmDetailResponse(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genres: List[GenreResponse]
    actors: List[PersonResponse]
    writers: List[PersonResponse]
    directors: List[PersonResponse]


@router.get(
    "/",
    response_model=list[FilmResponse],
    summary="Список фильмов",
    description="Получить список фильмов",
)
async def films_list(
    sort: Annotated[
        list[Literal["imdb_rating", "-imdb_rating"]],
        Query(description="Sort by imdb_rating"),
    ] = [],
    genre: Annotated[Optional[UUID], Query(description="Filter by genre UUID")] = None,
    film_service: FilmService = Depends(get_film_service),
    page_size: Annotated[int, Query(description="Фильмов на страницу", ge=1)] = 50,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
) -> FilmResponse:
    films = await film_service.get_list(sort, genre, page_size, page_number)
    return [
        FilmResponse(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]


@router.get(
    "/search",
    response_model=list[FilmResponse],
    summary="Поиск фильмов",
    description="Получить список найденных фильмов",
)
async def search_film(
    query: Annotated[str, Query(description="Запрос")],
    film_service: FilmService = Depends(get_film_service),
):
    films = await film_service.search_film(query)
    return [
        FilmResponse(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating)
        for film in films
    ]
