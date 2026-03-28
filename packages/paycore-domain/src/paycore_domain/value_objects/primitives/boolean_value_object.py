from abc import ABC
from dataclasses import dataclass

from .value_object import ValueObject


@dataclass(frozen=True)
class BooleanValueObject(ValueObject, ABC):
    value: bool

    def __post_init__(self) -> None:
        if not isinstance(self.value, bool):
            object.__setattr__(self, "value", bool(self.value))

    def __bool__(self) -> bool:
        return self.value

    def __str__(self) -> str:
        return str(self.value).lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value})"

    def is_true(self) -> bool:
        return self.value is True

    def is_false(self) -> bool:
        return self.value is False
