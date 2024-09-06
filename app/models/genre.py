from .base import OrjsonBaseModel


class Genre(OrjsonBaseModel):
    id: str
    name: str