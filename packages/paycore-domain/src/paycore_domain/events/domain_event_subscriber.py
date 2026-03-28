from abc import ABC, abstractmethod
from typing import List, Type

from .domain_event import DomainEvent


class DomainEventSubscriber(ABC):
    @staticmethod
    @abstractmethod
    def subscribed_to() -> List[Type[DomainEvent]]:
        pass

    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        pass
