from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from services.film import FilmService, get_film_service
import logging

# Initialize router and logger
router = APIRouter()
logger = logging.getLogger(__name__)

# Response models
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

# API endpoints

@router.get('/', response_model=SearchResponse)
async def get_films(
    sort: str = Query('-imdb_rating', description="Sort by field, default is -imdb_rating"),
    genre: Optional[UUID] = Query(None, description="Filter by genre UUID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    film_service: FilmService = Depends(get_film_service)
) -> SearchResponse:
    """
    Retrieve a list of films with pagination, sorting, and optional genre filtering.
    """
    try:
        total, films = await film_service.get_films(sort=sort, genre=genre, page=page, size=size)
        return SearchResponse(
            total=total,
            page=page,
            size=size,
            results=[FilmResponse(id=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
        )
    except Exception as e:
        logger.error(f"Error fetching films: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to fetch films.")

@router.get('/{film_id}', response_model=FilmDetailResponse)
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> FilmDetailResponse:
    """
    Retrieve detailed information about a specific film by its UUID.
    """
    try:
        film = await film_service.get_by_id(film_id)
        if not film:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Film not found')

        # Handle genres - ensure they are in the correct format (with id and name)
        genres = [
            GenreResponse(id=genre['id'], name=genre['name']) 
            for genre in film.get('genres', [])
        ]

        # Handle actors - fallback to names if ids are not provided
        actors = [
            PersonResponse(id=actor['id'], full_name=actor['name']) 
            for actor in film.get('actors', [])
        ] if 'actors' in film else [
            PersonResponse(id=None, full_name=name) 
            for name in film.get('actors_names', [])
        ]

        # Handle writers - fallback to names if ids are not provided
        writers = [
            PersonResponse(id=writer['id'], full_name=writer['name']) 
            for writer in film.get('writers', [])
        ] if 'writers' in film else [
            PersonResponse(id=None, full_name=name) 
            for name in film.get('writers_names', [])
        ]

        # Handle directors - fallback to names if ids are not provided
        directors = [
            PersonResponse(id=director['id'], full_name=director['name']) 
            for director in film.get('directors', [])
        ] if 'directors' in film else [
            PersonResponse(id=None, full_name=name) 
            for name in film.get('directors_names', [])
        ]

        # Return the response
        return FilmDetailResponse(
            id=film['id'],
            title=film['title'],
            imdb_rating=film.get('imdb_rating'),
            description=film.get('description'),
            genres=genres,
            actors=actors,
            writers=writers,
            directors=directors
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching film details: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to fetch film details.")


@router.get('/search', response_model=SearchResponse)
async def search_films(
    query: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    film_service: FilmService = Depends(get_film_service)
) -> SearchResponse:
    """
    Search for films by title, description, or other fields.
    """
    try:
        total, films = await film_service.search_films(query=query, page=page, size=size)
        return SearchResponse(
            total=total,
            page=page,
            size=size,
            results=[FilmResponse(id=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
        )
    except Exception as e:
        logger.error(f"Error searching films: {str(e)}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail="Failed to search films.")

