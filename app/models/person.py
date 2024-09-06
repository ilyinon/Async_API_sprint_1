from .base import OrjsonBaseModel


class Person(OrjsonBaseModel):
    id: str
    full_name: str