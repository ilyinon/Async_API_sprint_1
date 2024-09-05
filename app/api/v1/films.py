from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.services.film import FilmService, get_film_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class GenreResponse(BaseModel):
    id: Optional[str]
    name: str

class PersonResponse(BaseModel):
    id: Optional[str]
    full_name: str

class FilmDetailResponse(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genres: List[GenreResponse]
    actors: List[PersonResponse]
    writers: List[PersonResponse]
    directors: List[PersonResponse]

class FilmResponse(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float] = None

class SearchResponse(BaseModel):
    total: int
    page: int
    size: int
    results: List[FilmResponse]

@router.get('/{film_id}', response_model=FilmDetailResponse)
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> FilmDetailResponse:
    # try:
    film = await film_service.get_by_id(film_id)
    
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

    # Convert film model to response model
    genres = [GenreResponse(id=str(genre.id), name=genre.name) for genre in film.genres]
    
    actors = [PersonResponse(id=str(actor.id), full_name=actor.full_name) for actor in film.actors]
    writers = [PersonResponse(id=str(writer.id), full_name=writer.full_name) for writer in film.writers]
    directors = [PersonResponse(id=str(director.id), full_name=director.full_name) for director in film.directors]

    return FilmDetailResponse(
        id=str(film_detail.id),
        title=film_detail.title,
        imdb_rating=film_detail.imdb_rating,
        description=film_detail.description,
        genres=[
            GenreResponse(id=str(genre.id), name=genre.name)
            for genre in film_detail.genres
        ],
        actors=[
            PersonResponse(id=str(actor.id), full_name=actor.full_name)
            for actor in film_detail.actors
        ],
        writers=[
            PersonResponse(id=str(writer.id), full_name=writer.full_name)
            for writer in film_detail.writers
        ],
        directors=[
            PersonResponse(id=str(director.id), full_name=director.full_name)
            for director in film_detail.directors
        ],
    )
