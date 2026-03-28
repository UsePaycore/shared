from abc import ABC
from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4

from .value_object import ValueObject


@dataclass(frozen=True)
class UuidValueObject(ValueObject, ABC):
    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            object.__setattr__(self, "value", UUID(str(self.value)))

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> Self:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
