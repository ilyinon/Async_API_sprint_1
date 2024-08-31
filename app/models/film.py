from datetime import datetime
from typing import Optional
from uuid import UUID
from models.base import OrjsonBaseModel

class Genre(OrjsonBaseModel):
    id: str
    name: str
    description: Optional[str] = None

class Person(OrjsonBaseModel):
    id: str
    full_name: str
    role: Optional[str] = None

class Film(OrjsonBaseModel):
    id: str
    title: str
    description: Optional[str] = None
    creation_date: Optional[datetime] = None
    file_path: Optional[str] = None
    rating: Optional[float] = None
    type: str
    genres: list[Genre]
    persons: list[Person]
