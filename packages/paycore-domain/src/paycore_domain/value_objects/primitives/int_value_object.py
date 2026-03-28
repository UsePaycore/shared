from abc import ABC
from dataclasses import dataclass

from .value_object import ValueObject


@dataclass(frozen=True)
class IntValueObject(ValueObject, ABC):
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            object.__setattr__(self, "value", int(self.value))

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __lt__(self, other: "IntValueObject") -> bool:
        return self.value < other.value

    def __le__(self, other: "IntValueObject") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "IntValueObject") -> bool:
        return self.value > other.value

    def __ge__(self, other: "IntValueObject") -> bool:
        return self.value >= other.value
