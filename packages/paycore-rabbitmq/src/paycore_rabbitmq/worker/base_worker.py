import logging
import signal
import threading
from pathlib import Path
from typing import Union

from paycore_rabbitmq.consumer.consumer import RabbitMqConsumer
from paycore_rabbitmq.consumer.consumer_with_retry import RabbitMqConsumerWithRetry

HEARTBEAT_PATH = Path("/tmp/worker-heartbeat")  # noqa: S108
HEARTBEAT_INTERVAL = 30

logger = logging.getLogger(__name__)


class BaseWorker:
    def __init__(
        self,
        name: str,
        consumer: Union[RabbitMqConsumer, RabbitMqConsumerWithRetry],
    ) -> None:
        self._name = name
        self._consumer = consumer
        self._running = False
        self._heartbeat_thread: threading.Thread | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def running(self) -> bool:
        return self._running

    def start(self) -> None:
        self._setup_signal_handlers()
        self._running = True
        self._start_heartbeat()
        logger.info(f"Worker '{self._name}' starting")
        try:
            self._consumer.start()
        except Exception:
            logger.exception(f"Worker '{self._name}' crashed")
            raise
        finally:
            self._running = False
            logger.info(f"Worker '{self._name}' stopped")

    def stop(self) -> None:
        logger.info(f"Worker '{self._name}' shutting down")
        self._running = False
        self._consumer.stop()

    def _setup_signal_handlers(self) -> None:
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum: int, frame: object) -> None:
        signal_name = signal.Signals(signum).name
        logger.info(f"Worker '{self._name}' received {signal_name}")
        self.stop()

    def _start_heartbeat(self) -> None:
        self._heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self._heartbeat_thread.start()

    def _heartbeat_loop(self) -> None:
        while self._running:
            HEARTBEAT_PATH.touch()
            threading.Event().wait(HEARTBEAT_INTERVAL)
