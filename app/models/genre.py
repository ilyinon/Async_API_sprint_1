from typing import Optional
from uuid import UUID
from .base import OrjsonBaseModel


class Genre(OrjsonBaseModel):
    id: UUID
    name: str
    description: Optional[str] = None