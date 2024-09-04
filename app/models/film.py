from typing import Optional
from uuid import UUID
from app.models.genre import Genre
from app.models.person import Person
from models.base import OrjsonBaseModel

class Film(OrjsonBaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: list[Genre]
    persons: list[Person]