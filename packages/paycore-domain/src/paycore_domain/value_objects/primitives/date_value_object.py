from abc import ABC
from dataclasses import dataclass
from datetime import date

from .value_object import ValueObject


@dataclass(frozen=True)
class DateValueObject(ValueObject, ABC):
    value: date

    def __post_init__(self) -> None:
        if isinstance(self.value, str):
            object.__setattr__(self, "value", date.fromisoformat(self.value))

    def __str__(self) -> str:
        return self.value.isoformat()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value.isoformat()})"

    def __lt__(self, other: "DateValueObject") -> bool:
        return self.value < other.value

    def __le__(self, other: "DateValueObject") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "DateValueObject") -> bool:
        return self.value > other.value

    def __ge__(self, other: "DateValueObject") -> bool:
        return self.value >= other.value

    @property
    def year(self) -> int:
        return self.value.year

    @property
    def month(self) -> int:
        return self.value.month

    @property
    def day(self) -> int:
        return self.value.day
