import logging
from typing import Optional

import pika
from pika import BlockingConnection
from pika.adapters.blocking_connection import BlockingChannel

from .config import RabbitMqConfig

logger = logging.getLogger(__name__)


class RabbitMqConnection:
    def __init__(self, config: RabbitMqConfig) -> None:
        self._config = config
        self._connection: Optional[BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    def channel(self) -> BlockingChannel:
        if self._channel is None or self._channel.is_closed:
            self._channel = self._connection_instance().channel()
        return self._channel

    def _connection_instance(self) -> BlockingConnection:
        if self._connection is None or self._connection.is_closed:
            credentials = pika.PlainCredentials(
                self._config.user,
                self._config.password,
            )
            parameters = pika.ConnectionParameters(
                host=self._config.host,
                port=self._config.port,
                virtual_host=self._config.vhost,
                credentials=credentials,
            )
            self._connection = pika.BlockingConnection(parameters)
        return self._connection

    def close(self) -> None:
        if self._channel and not self._channel.is_closed:
            self._channel.close()
        if self._connection and not self._connection.is_closed:
            self._connection.close()

    def declare_exchange(self, name: str, exchange_type: str = "topic") -> None:
        self.channel().exchange_declare(
            exchange=name,
            exchange_type=exchange_type,
            durable=True,
        )

    def declare_queue(
        self,
        name: str,
        arguments: Optional[dict] = None,
    ) -> None:
        self.channel().queue_declare(
            queue=name,
            durable=True,
            arguments=arguments or {},
        )

    def declare_queue_with_dlx(
        self,
        queue_name: str,
        dead_letter_exchange: str,
        dead_letter_routing_key: Optional[str] = None,
        message_ttl: Optional[int] = None,
    ) -> None:
        arguments: dict[str, str | int] = {
            "x-dead-letter-exchange": dead_letter_exchange,
        }
        if dead_letter_routing_key:
            arguments["x-dead-letter-routing-key"] = dead_letter_routing_key
        if message_ttl:
            arguments["x-message-ttl"] = message_ttl

        self.declare_queue(queue_name, arguments)

    def bind_queue(self, queue: str, exchange: str, routing_key: str) -> None:
        self.channel().queue_bind(
            queue=queue,
            exchange=exchange,
            routing_key=routing_key,
        )

    def _reconnect(self) -> None:
        logger.warning("RabbitMQ connection lost, reconnecting...")
        self._channel = None
        self._connection = None
        self._connection_instance()

    def publish(
        self,
        exchange: str,
        routing_key: str,
        body: str,
        message_id: str,
        _retries: int = 2,
    ) -> None:
        properties = pika.BasicProperties(
            message_id=message_id,
            content_type="application/json",
            content_encoding="utf-8",
            delivery_mode=2,
        )
        for attempt in range(_retries + 1):
            try:
                self.channel().basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=body.encode("utf-8"),
                    properties=properties,
                )
                return
            except (
                pika.exceptions.StreamLostError,
                pika.exceptions.AMQPConnectionError,
                pika.exceptions.AMQPChannelError,
                ConnectionResetError,
                BrokenPipeError,
            ):
                if attempt < _retries:
                    self._reconnect()
                else:
                    raise
