import pytest
import pytest_asyncio
import asyncio
import time
from uuid import uuid4
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from testcontainers.kafka import KafkaContainer
from sqlalchemy import select, func
from src.config import settings
from src.students.consumer import (
    _header, _attempt_number, _meta_headers, _remaining_delay,
    _process_message, _default_handler_factory,)
from src.students.student_event_schemas import StudentEvent
from src.inbox.processed_event_model import ProcessedEventModel


class _FakeMessage:
    def __init__(self, headers=None, topic="t", partition=0, offset=0, key=b"k", value=b"v"):
        self.headers = headers or []
        self.topic = topic
        self.partition = partition
        self.offset = offset
        self.key = key
        self.value = value


class TestHeaderHelpers:
    def test_header_returns_value_when_present(self):
        assert _header(_FakeMessage(headers=[("attempts", b"3")]), "attempts") == "3"

    def test_header_returns_none_when_absent(self):
        assert _header(_FakeMessage(headers=[]), "attempts") is None

    def test_attempt_number_defaults_to_one(self):
        assert _attempt_number(_FakeMessage(headers=[])) == 1

    def test_attempt_number_increments_existing(self):
        assert _attempt_number(_FakeMessage(headers=[("attempts", b"2")])) == 3

    def test_attempt_number_raises_on_malformed_header(self):
        with pytest.raises(ValueError):
            _attempt_number(_FakeMessage(headers=[("attempts", b"not-a-number")]))

    def test_remaining_delay_zero_when_no_header(self):
        assert _remaining_delay(_FakeMessage(headers=[])) == 0.0

    def test_remaining_delay_computed_from_header(self):
        future = time.time() + 100
        msg = _FakeMessage(headers=[("retry_at", str(future).encode())])
        assert 90 < _remaining_delay(msg) <= 100

    def test_meta_headers_prefers_original_source_over_current_message(self):
        msg = _FakeMessage(
            headers=[("source_topic", b"orig-topic"), ("source_partition", b"5"), ("source_offset", b"42")],
            topic="retry-topic", partition=0, offset=999)
        headers = {k: v.decode() for k, v in _meta_headers(msg, Exception("boom"), 2)}
        assert headers["source_topic"] == "orig-topic"
        assert headers["source_partition"] == "5"
        assert headers["source_offset"] == "42"
        assert headers["attempts"] == "2"


class _NonClosingBegin:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _SessionFactoryStub:
    def __init__(self, session):
        self._session = session

    def begin(self):
        return _NonClosingBegin(self._session)


@pytest.fixture(scope="session")
def kafka_container():
    with KafkaContainer() as container:
        yield container


@pytest.fixture(scope="session")
def kafka_bootstrap_servers(kafka_container):
    return kafka_container.get_bootstrap_server()


@pytest_asyncio.fixture(autouse=True)
def _isolate_topics(monkeypatch):
    monkeypatch.setattr(settings, "student_events_dlq_topic", f"dlq-test-{uuid4()}")
    monkeypatch.setattr(settings, "student_events_retry_topic", f"retry-test-{uuid4()}")


@pytest_asyncio.fixture
async def producer(kafka_bootstrap_servers, monkeypatch):
    monkeypatch.setattr(settings, "kafka_bootstrap_servers", kafka_bootstrap_servers)
    p = AIOKafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
    await p.start()
    yield p
    await p.stop()


async def _consume_one(bootstrap_servers: str, topic: str, timeout: float = 15):
    consumer = AIOKafkaConsumer(
        topic, bootstrap_servers=bootstrap_servers,
        group_id=f"test-{uuid4()}", auto_offset_reset="earliest")
    await consumer.start()
    try:
        return await asyncio.wait_for(consumer.__anext__(), timeout=timeout)
    finally:
        await consumer.stop()


def make_event() -> StudentEvent:
    return StudentEvent(event="student_created", event_id=uuid4(), student_id=uuid4(), name="Ivan")


class TestProcessMessage:
    async def test_success_marks_event_processed(self, session, producer):
        event = make_event()
        message = _FakeMessage(value=event.model_dump_json().encode("utf-8"), key=str(event.student_id).encode())
        await _process_message(message, producer, _default_handler_factory, _SessionFactoryStub(session))
        result = await session.execute(
            select(func.count()).select_from(ProcessedEventModel).where(ProcessedEventModel.event_id == event.event_id))
        assert result.scalar_one() == 1

    async def test_malformed_json_goes_straight_to_dlq(self, session, producer, kafka_bootstrap_servers):
        message = _FakeMessage(value=b"not-json", key=b"k")
        await _process_message(message, producer, _default_handler_factory, _SessionFactoryStub(session))
        dlq_message = await _consume_one(kafka_bootstrap_servers, settings.student_events_dlq_topic)
        assert dlq_message.value == b"not-json"

    async def test_malformed_attempts_header_goes_straight_to_dlq(self, session, producer, kafka_bootstrap_servers):
        message = _FakeMessage(value=b"whatever", key=b"k", headers=[("attempts", b"not-a-number")])
        await _process_message(message, producer, _default_handler_factory, _SessionFactoryStub(session))
        dlq_message = await _consume_one(kafka_bootstrap_servers, settings.student_events_dlq_topic)
        headers = dict(dlq_message.headers)
        assert headers["attempts"] == b"1"