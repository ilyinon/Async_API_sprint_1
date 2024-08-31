from typing import Optional
from uuid import UUID

from models.base import OrjsonBaseModel


class Film(OrjsonBaseModel):
    id: UUID
    title: str
    imdb_rating: Optional[float]
