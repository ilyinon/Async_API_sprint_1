from uuid import UUID

from models.base import OrjsonBaseModel


class Genre(OrjsonBaseModel):
    id: UUID
    name: str
