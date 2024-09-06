from typing import Optional, List
from .genre import Genre
from .person import Person
from .base import OrjsonBaseModel

class Film(OrjsonBaseModel):
    id: str
    title: str
    description: Optional[str] = None
    imdb_rating: Optional[float] = None
    genres: List[Genre]
    actors: List[Person]
    directors: List[Person]
    writers: List[Person]
