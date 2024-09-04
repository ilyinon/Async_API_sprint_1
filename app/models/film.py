from typing import Optional
from uuid import UUID

from models.base import OrjsonBaseModel
from models.genre import Genre
from models.person import Person


class Film(OrjsonBaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: list[Genre]
    persons: list[Person]
