import logging
from typing import Dict, List, Optional

from pika.exceptions import AMQPConnectionError

from paycore_domain.events import DomainEvent, DomainEventSubscriber, EventBus

from .connection import RabbitMqConnection
from .serializer import DomainEventJsonSerializer

logger = logging.getLogger(__name__)


class RabbitMqEventBus(EventBus):
    def __init__(
        self,
        connection: RabbitMqConnection,
        exchange_name: str,
        failover_publisher: Optional[EventBus] = None,
    ) -> None:
        self._connection = connection
        self._exchange_name = exchange_name
        self._failover_publisher = failover_publisher
        self._exchange_declared = False
        self._subscribers: Dict[str, List[DomainEventSubscriber]] = {}

    def subscribe(self, subscriber: DomainEventSubscriber) -> None:
        for event_type in subscriber.subscribed_to():
            event_name = event_type.event_name()
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(subscriber)
            logger.info(f"Registered subscriber {subscriber.__class__.__name__} for {event_name}")

    def publish(self, events: List[DomainEvent]) -> None:
        for event in events:
            self._dispatch_to_local_subscribers(event)
            self._publish_event(event)

    def _dispatch_to_local_subscribers(self, event: DomainEvent) -> None:
        event_name = event.event_name()
        subscribers = self._subscribers.get(event_name, [])
        for subscriber in subscribers:
            try:
                subscriber.handle(event)
            except Exception as e:
                logger.error(
                    f"Error handling event {event_name} in {subscriber.__class__.__name__}: {e}"
                )

    def _publish_event(self, event: DomainEvent) -> None:
        try:
            self._ensure_exchange_exists()
            body = DomainEventJsonSerializer.serialize(event)
            routing_key = event.event_name()
            message_id = str(event.event_id)

            self._connection.publish(
                exchange=self._exchange_name,
                routing_key=routing_key,
                body=body,
                message_id=message_id,
            )
            logger.debug(f"Published event {event.event_name()} with id {event.event_id}")
        except AMQPConnectionError as e:
            logger.error(f"Failed to publish event {event.event_name()}: {e}")
            if self._failover_publisher:
                self._failover_publisher.publish([event])
            else:
                raise

    def _ensure_exchange_exists(self) -> None:
        if not self._exchange_declared:
            self._connection.declare_exchange(self._exchange_name, "topic")
            self._exchange_declared = True
