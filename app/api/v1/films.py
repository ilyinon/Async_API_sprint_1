from http import HTTPStatus
from typing import Optional
from uuid import UUID

from core import config
from core.logger import logger
from fastapi import APIRouter, Depends, HTTPException
from models.base import OrjsonBaseModel
from pydantic import BaseModel
from services.film import FilmService, get_film_service

router = APIRouter()


class Film(OrjsonBaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


@router.get("", response_model=str)
async def film_list():
    return "list of films"


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
