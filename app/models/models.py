from datetime import datetime
from typing import Optional
from uuid import UUID
from models.base import OrjsonBaseModel

class Genre(OrjsonBaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

class Person(OrjsonBaseModel):
    id: UUID
    full_name: str
    role: Optional[str] = None

class Film(OrjsonBaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    creation_date: Optional[datetime] = None
    imdb_rating: Optional[float] = None
    genres: list[Genre]
    persons: list[Person]
