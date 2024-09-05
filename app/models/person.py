from typing import Optional
from uuid import UUID
from .base import OrjsonBaseModel


class Person(OrjsonBaseModel):
    id: UUID
    full_name: str
    role: Optional[str] = None