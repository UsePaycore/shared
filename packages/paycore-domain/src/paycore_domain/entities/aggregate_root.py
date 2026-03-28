from typing import List

from paycore_domain.events import DomainEvent

from .entity import Entity, TId


class AggregateRoot(Entity[TId]):
    def __init__(self, id: TId) -> None:
        super().__init__(id)
        self._domain_events: List[DomainEvent] = []

    @property
    def domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()

    def add_domain_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def clear_domain_events(self) -> None:
        self._domain_events.clear()

    def pop_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
