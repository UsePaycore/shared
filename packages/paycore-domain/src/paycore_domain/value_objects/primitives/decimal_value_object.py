from abc import ABC
from dataclasses import dataclass
from decimal import Decimal

from .value_object import ValueObject


@dataclass(frozen=True)
class DecimalValueObject(ValueObject, ABC):
    value: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.value, Decimal):
            object.__setattr__(self, "value", Decimal(str(self.value)))

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def __lt__(self, other: "DecimalValueObject") -> bool:
        return self.value < other.value

    def __le__(self, other: "DecimalValueObject") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "DecimalValueObject") -> bool:
        return self.value > other.value

    def __ge__(self, other: "DecimalValueObject") -> bool:
        return self.value >= other.value

    def __add__(self, other: "DecimalValueObject") -> Decimal:
        return self.value + other.value

    def __sub__(self, other: "DecimalValueObject") -> Decimal:
        return self.value - other.value

    def __mul__(self, other: "DecimalValueObject") -> Decimal:
        return self.value * other.value

    def __truediv__(self, other: "DecimalValueObject") -> Decimal:
        return self.value / other.value
