from typing import Optional
from uuid import UUID

from models.base import OrjsonBaseModel
from models.genre import Genre
from models.person import Person


class Film(OrjsonBaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float] = None


class FilmDetail(Film):
    description: Optional[str] = None
    genres: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
