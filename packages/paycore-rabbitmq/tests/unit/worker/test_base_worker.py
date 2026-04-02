import signal
import threading
import time
from unittest.mock import MagicMock, patch

from paycore_rabbitmq.worker.base_worker import BaseWorker


def _create_mock_consumer():
    consumer = MagicMock()
    consumer.start = MagicMock()
    consumer.stop = MagicMock()
    return consumer


class TestBaseWorkerHeartbeat:
    def test_heartbeat_file_is_created_on_start(self, tmp_path):
        heartbeat_file = tmp_path / "worker-heartbeat"
        consumer = _create_mock_consumer()
        started = threading.Event()

        def blocking_start():
            started.set()
            time.sleep(0.2)

        consumer.start.side_effect = blocking_start
        worker = BaseWorker(name="test-worker", consumer=consumer)

        with patch(
            "paycore_rabbitmq.worker.base_worker.HEARTBEAT_PATH", heartbeat_file
        ):
            worker.start()

        assert heartbeat_file.exists()

    def test_heartbeat_loop_writes_file_while_running(self, tmp_path):
        heartbeat_file = tmp_path / "worker-heartbeat"
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)
        worker._running = True

        with patch(
            "paycore_rabbitmq.worker.base_worker.HEARTBEAT_PATH", heartbeat_file
        ):
            stop_event = threading.Event()
            original_wait = threading.Event.wait

            def quick_wait(self_event, timeout=None):
                stop_event.set()
                worker._running = False
                return original_wait(self_event, 0)

            with patch.object(threading.Event, "wait", quick_wait):
                worker._heartbeat_loop()

        assert heartbeat_file.exists()


class TestBaseWorkerGracefulShutdown:
    def test_stop_sets_running_to_false(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)
        worker._running = True

        worker.stop()

        assert worker.running is False

    def test_stop_calls_consumer_stop(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)
        worker._running = True

        worker.stop()

        consumer.stop.assert_called_once()

    def test_sigterm_triggers_graceful_shutdown(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)
        worker._running = True

        worker._handle_signal(signal.SIGTERM, None)

        assert worker.running is False
        consumer.stop.assert_called_once()

    def test_sigint_triggers_graceful_shutdown(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)
        worker._running = True

        worker._handle_signal(signal.SIGINT, None)

        assert worker.running is False
        consumer.stop.assert_called_once()


class TestBaseWorkerLifecycle:
    def test_start_sets_running_to_true_and_calls_consumer_start(self):
        consumer = _create_mock_consumer()
        consumer.start.side_effect = lambda: None
        worker = BaseWorker(name="test-worker", consumer=consumer)

        worker.start()

        consumer.start.assert_called_once()
        assert worker.running is False

    def test_start_registers_signal_handlers(self):
        consumer = _create_mock_consumer()
        consumer.start.side_effect = lambda: None
        worker = BaseWorker(name="test-worker", consumer=consumer)

        with patch.object(worker, "_setup_signal_handlers") as mock_setup:
            worker.start()
            mock_setup.assert_called_once()

    def test_start_starts_heartbeat(self):
        consumer = _create_mock_consumer()
        consumer.start.side_effect = lambda: None
        worker = BaseWorker(name="test-worker", consumer=consumer)

        with patch.object(worker, "_start_heartbeat") as mock_heartbeat:
            worker.start()
            mock_heartbeat.assert_called_once()

    def test_running_is_false_after_consumer_raises(self):
        consumer = _create_mock_consumer()
        consumer.start.side_effect = RuntimeError("connection lost")
        worker = BaseWorker(name="test-worker", consumer=consumer)

        try:
            worker.start()
        except RuntimeError:
            pass

        assert worker.running is False

    def test_name_property_returns_worker_name(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="my-worker", consumer=consumer)

        assert worker.name == "my-worker"

    def test_setup_signal_handlers_registers_sigterm_and_sigint(self):
        consumer = _create_mock_consumer()
        worker = BaseWorker(name="test-worker", consumer=consumer)

        with patch("paycore_rabbitmq.worker.base_worker.signal.signal") as mock_signal:
            worker._setup_signal_handlers()

            calls = [c.args for c in mock_signal.call_args_list]
            assert (signal.SIGTERM, worker._handle_signal) in calls
            assert (signal.SIGINT, worker._handle_signal) in calls
