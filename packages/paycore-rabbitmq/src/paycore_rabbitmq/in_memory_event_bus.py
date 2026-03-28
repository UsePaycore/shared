import logging
from typing import Dict, List

from paycore_domain.events import DomainEvent, DomainEventSubscriber, EventBus

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[DomainEventSubscriber]] = {}
        self._published_events: List[DomainEvent] = []

    def publish(self, events: List[DomainEvent]) -> None:
        for event in events:
            self._published_events.append(event)
            self._dispatch(event)

    def subscribe(self, subscriber: DomainEventSubscriber) -> None:
        for event_type in subscriber.subscribed_to():
            event_name = event_type.event_name()
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(subscriber)

    def _dispatch(self, event: DomainEvent) -> None:
        event_name = event.event_name()
        subscribers = self._subscribers.get(event_name, [])
        for subscriber in subscribers:
            try:
                subscriber.handle(event)
            except Exception as e:
                logger.error(
                    f"Error handling event {event_name} in {subscriber.__class__.__name__}: {e}"
                )

    def published_events(self) -> List[DomainEvent]:
        return self._published_events.copy()

    def clear(self) -> None:
        self._published_events.clear()
