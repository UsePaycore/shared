from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from .domain_event import DomainEvent

if TYPE_CHECKING:
    from .domain_event_subscriber import DomainEventSubscriber


class EventBus(ABC):
    @abstractmethod
    def publish(self, events: List[DomainEvent]) -> None:
        pass

    def subscribe(self, subscriber: "DomainEventSubscriber") -> None:
        pass
