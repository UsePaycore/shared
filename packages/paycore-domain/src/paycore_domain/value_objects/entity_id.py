from dataclasses import dataclass
from typing import TypeVar
from uuid import uuid4

from .primitives import UuidValueObject

T = TypeVar("T", bound="EntityId")


@dataclass(frozen=True)
class EntityId(UuidValueObject):
    @classmethod
    def generate(cls: type[T]) -> T:
        return cls(value=uuid4())
