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
        id=str(film.id),
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genres=genres,
        actors=actors,
        writers=writers,
        directors=directors
    )

    # except HTTPException:
    #     raise
    # except Exception as e:
    #     logger.error(f"Error fetching film details: {str(e)}")
    #     raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to fetch film details.")

@router.get('/', response_model=SearchResponse)
async def get_films(
    sort: str = Query('-imdb_rating', description="Sort by field, default is -imdb_rating"),
    genre: Optional[UUID] = Query(None, description="Filter by genre UUID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    film_service: FilmService = Depends(get_film_service)
) -> SearchResponse:
    # try:
    total, films = await film_service.get_films(sort=sort, genre=genre, page=page, size=size)
    return SearchResponse(
        total=total,
        page=page,
        size=size,
        results=[FilmResponse(id=str(film.id), title=film.title, imdb_rating=film.imdb_rating) for film in films]
    )

    # except Exception as e:
    #     logger.error(f"Error fetching films: {str(e)}")
    #     raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to fetch films.")


@router.get('/search', response_model=SearchResponse)
async def search_films(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    film_service: FilmService = Depends(get_film_service)
) -> SearchResponse:
    # try:
    total, films = await film_service.search_films(query=query, page=page, size=size)
    return SearchResponse(
        total=total,
        page=page,
        size=size,
        results=[FilmResponse(id=str(film.id), title=film.title, imdb_rating=film.imdb_rating) for film in films]
    )

    # except Exception as e:
    #     logger.error(f"Error searching films: {str(e)}")
    #     raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to search films.")