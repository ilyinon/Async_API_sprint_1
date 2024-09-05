from typing import Optional
from uuid import UUID
from .genre import Genre
from .person import Person
from .base import OrjsonBaseModel


class Film(OrjsonBaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: list[Genre]
    persons: list[Person]