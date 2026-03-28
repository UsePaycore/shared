from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from .command import Command

TCommand = TypeVar("TCommand", bound=Command)
TResult = TypeVar("TResult")


class CommandHandler(ABC, Generic[TCommand, TResult]):
    @abstractmethod
    def handle(self, command: TCommand) -> TResult:
        raise NotImplementedError
