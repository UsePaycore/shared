from dataclasses import dataclass
from uuid import uuid4

from .entity_id import EntityId


@dataclass(frozen=True)
class UserId(EntityId):
    @classmethod
    def generate(cls) -> "UserId":
        return cls(value=uuid4())
