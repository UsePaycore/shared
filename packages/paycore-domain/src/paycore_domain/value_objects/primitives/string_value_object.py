from abc import ABC
from dataclasses import dataclass

from .value_object import ValueObject


@dataclass(frozen=True)
class StringValueObject(ValueObject, ABC):
    value: str

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"
