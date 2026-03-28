import json
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from paycore_rabbitmq.connection import RabbitMqConnection

HEARTBEAT_PATH = Path("/tmp/worker-heartbeat")  # noqa: S108
HEARTBEAT_INTERVAL = 30

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetryConfig:
    max_retries: int = 3
    retry_ttl_ms: int = 5000
    dead_letter_ttl_ms: int = 86400000


class RabbitMqConsumerWithRetry(ABC):
    RETRY_COUNT_HEADER = "x-retry-count"

    def __init__(
        self,
        connection: RabbitMqConnection,
        exchange_name: str,
        queue_name: str,
        routing_keys: List[str],
        retry_config: Optional[RetryConfig] = None,
    ) -> None:
        self._connection = connection
        self._exchange_name = exchange_name
        self._queue_name = queue_name
        self._routing_keys = routing_keys
        self._retry_config = retry_config or RetryConfig()
        self._running = False

        self._retry_exchange = f"{exchange_name}.retry"
        self._retry_queue = f"{queue_name}.retry"
        self._dead_letter_exchange = f"{exchange_name}.dead_letter"
        self._dead_letter_queue = f"{queue_name}.dead_letter"

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
        self._setup_dead_letter_infrastructure()
        self._setup_retry_infrastructure()
        self._setup_main_queue()
        self._setup_consumer()

    def _setup_dead_letter_infrastructure(self) -> None:
        self._connection.declare_exchange(self._dead_letter_exchange, "topic")
        self._connection.declare_queue(self._dead_letter_queue)
        self._connection.bind_queue(
            self._dead_letter_queue,
            self._dead_letter_exchange,
            "#",
        )
        logger.info(f"Dead letter queue configured: {self._dead_letter_queue}")

    def _setup_retry_infrastructure(self) -> None:
        self._connection.declare_exchange(self._retry_exchange, "topic")
        self._connection.declare_queue_with_dlx(
            queue_name=self._retry_queue,
            dead_letter_exchange=self._exchange_name,
            message_ttl=self._retry_config.retry_ttl_ms,
        )
        for routing_key in self._routing_keys:
            self._connection.bind_queue(
                self._retry_queue,
                self._retry_exchange,
                routing_key,
            )
        logger.info(
            f"Retry queue configured: {self._retry_queue} "
            f"(TTL: {self._retry_config.retry_ttl_ms}ms)"
        )

    def _setup_main_queue(self) -> None:
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

    def _setup_consumer(self) -> None:
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
        retry_count = self._get_retry_count(properties)

        try:
            message = json.loads(body.decode("utf-8"))
            event_name = message.get("event_name", method.routing_key)

            logger.info(f"Received event: {event_name} (retry: {retry_count})")
            self.handle_event(event_name, message)

            channel.basic_ack(delivery_tag=method.delivery_tag)
            logger.debug(f"Acknowledged event: {event_name}")

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self._handle_failure(channel, method, properties, body, retry_count)

    def _get_retry_count(self, properties: BasicProperties) -> int:
        if properties.headers and self.RETRY_COUNT_HEADER in properties.headers:
            return int(properties.headers[self.RETRY_COUNT_HEADER])
        return 0

    def _handle_failure(
        self,
        channel: BlockingChannel,
        method: Basic.Deliver,
        properties: BasicProperties,
        body: bytes,
        retry_count: int,
    ) -> None:
        channel.basic_ack(delivery_tag=method.delivery_tag)

        new_retry_count = retry_count + 1

        if new_retry_count > self._retry_config.max_retries:
            logger.warning(
                f"Max retries ({self._retry_config.max_retries}) exceeded. "
                f"Sending to dead letter queue: {self._dead_letter_queue}"
            )
            self._send_to_dead_letter(method.routing_key, properties, body)
        else:
            logger.info(
                f"Scheduling retry {new_retry_count}/{self._retry_config.max_retries} "
                f"in {self._retry_config.retry_ttl_ms}ms"
            )
            self._send_to_retry(method.routing_key, properties, body, new_retry_count)

    def _send_to_retry(
        self,
        routing_key: str,
        original_properties: BasicProperties,
        body: bytes,
        retry_count: int,
    ) -> None:
        headers = dict(original_properties.headers or {})
        headers[self.RETRY_COUNT_HEADER] = retry_count
        headers["x-original-routing-key"] = routing_key

        properties = pika.BasicProperties(
            message_id=original_properties.message_id,
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=2,
            headers=headers,
        )

        self._connection.channel().basic_publish(
            exchange=self._retry_exchange,
            routing_key=routing_key,
            body=body,
            properties=properties,
        )

    def _send_to_dead_letter(
        self,
        routing_key: str,
        original_properties: BasicProperties,
        body: bytes,
    ) -> None:
        headers = dict(original_properties.headers or {})
        headers["x-original-routing-key"] = routing_key
        headers["x-dead-letter-reason"] = "max_retries_exceeded"

        properties = pika.BasicProperties(
            message_id=original_properties.message_id,
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=2,
            headers=headers,
        )

        self._connection.channel().basic_publish(
            exchange=self._dead_letter_exchange,
            routing_key=routing_key,
            body=body,
            properties=properties,
        )

    @abstractmethod
    def handle_event(self, event_name: str, message: Dict[str, Any]) -> None:
        pass
