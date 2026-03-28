from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import TypeVar

from .value_object import ValueObject

E = TypeVar("E", bound=Enum)


@dataclass(frozen=True)
class EnumValueObject(ValueObject, ABC):
    value: Enum

    def __str__(self) -> str:
        return str(self.value.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    @property
    def name(self) -> str:
        return self.value.name

    def equals(self, other: Enum) -> bool:
        return self.value == other
