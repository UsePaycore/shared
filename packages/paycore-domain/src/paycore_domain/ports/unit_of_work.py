from abc import ABC, abstractmethod
from typing import Any

from paycore_domain.entities import AggregateRoot


class UnitOfWork(ABC):
    @abstractmethod
    def __enter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass

    @abstractmethod
    def register_aggregate(self, aggregate: AggregateRoot) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
