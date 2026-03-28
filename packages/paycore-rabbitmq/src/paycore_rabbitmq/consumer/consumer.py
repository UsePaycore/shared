import json
import logging
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from paycore_rabbitmq.connection import RabbitMqConnection

HEARTBEAT_PATH = Path("/tmp/worker-heartbeat")  # noqa: S108
HEARTBEAT_INTERVAL = 30

logger = logging.getLogger(__name__)


class RabbitMqConsumer(ABC):
    def __init__(
        self,
        connection: RabbitMqConnection,
        exchange_name: str,
        queue_name: str,
        routing_keys: List[str],
    ) -> None:
        self._connection = connection
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_keys = routing_keys
        self._running = False

    def _start_heartbeat(self) -> None:
        def _heartbeat_loop() -> None:
            while self._running:
                HEARTBEAT_PATH.touch()
                threading.Event().wait(HEARTBEAT_INTERVAL)

        self._heartbeat_thread = threading.Thread(target=_heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def start(self) -> None:
        self._setup()
        self._running = True
        self._start_heartbeat()
        logger.info(f"Starting consumer for queue: {self._queue_name}")
        self._connection.channel().start_consuming()

    def stop(self) -> None:
        self._running = False
        self._connection.channel().stop_consuming()
        logger.info(f"Stopped consumer for queue: {self._queue_name}")

    def _setup(self) -> None:
        self._connection.declare_exchange(self._exchange_name, "topic")
        self._connection.declare_queue(self._queue_name)

        for routing_key in self._routing_keys:
            self._connection.bind_queue(
                self._queue_name,
                self._exchange_name,
                routing_key,
            )
            logger.debug(
                f"Bound queue {self._queue_name} to {self._exchange_name} with key {routing_key}"
            )

        self._connection.channel().basic_qos(prefetch_count=1)
        self._connection.channel().basic_consume(
            queue=self._queue_name,
            on_message_callback=self._on_message,
            auto_ack=False,
        )

    def _on_message(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
    ) -> None:
        try:
            message = json.loads(body.decode("utf-8"))
            event_name = message.get("meta", {}).get("event_name", method.routing_key)

            logger.info(f"Received event: {event_name}")
            self.handle_event(event_name, message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Acknowledged event: {event_name}")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    @abstractmethod
    def handle_event(self, event_name: str, message: Dict[str, Any]) -> None:
        pass
