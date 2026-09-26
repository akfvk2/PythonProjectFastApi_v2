import asyncio
import logging
import time
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.config import settings
from src.students.student_event_schemas import StudentEvent
from src.students.student_event_service import StudentEventService
import json
from pydantic import ValidationError
from src.database import SessionFactory
from src.exceptions import RetryException
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from aiokafka import TopicPartition
from src.inbox.processed_event_repository import ProcessedEventRepository

logger = logging.getLogger(__name__)

def _default_handler_factory(session: AsyncSession) -> StudentEventService:
    return StudentEventService(ProcessedEventRepository(session))

def _header(message, name: str) -> str | None:
    for key, value in message.headers or ():
        if key == name:
            return value.decode("utf-8")
    return None

def _attempt_number(message) -> int:
    attempts_made = _header(message, "attempts")
    return int(attempts_made) + 1 if attempts_made is not None else 1

def _meta_headers(message, exc: Exception, attempt: int) -> list[tuple[str, bytes]]:
    return [
        ("error_reason", str(exc).encode("utf-8")),
        ("source_topic", (_header(message, "source_topic") or message.topic).encode("utf-8")),
        ("source_partition", (_header(message, "source_partition") or str(message.partition)).encode("utf-8")),
        ("source_offset", (_header(message, "source_offset") or str(message.offset)).encode("utf-8")),
        ("attempts", str(attempt).encode("utf-8")),
    ]
def _check_retry_budget() -> None:
    limit_seconds = settings.max_poll_interval_seconds
    if settings.max_retry_delay_seconds >= limit_seconds * 0.5:
        raise ValueError(
            f"Retry budget ({settings.max_retry_delay_seconds}s) is too close to "
            f"max_poll_interval_seconds ({limit_seconds}s) — consumer would lose its partition."
            f"Lower max_attempts / max_retry_delay_seconds or raise max_poll_interval_seconds."
        )

async def _process_once(message, handler_factory: Callable[[AsyncSession], StudentEventService],
                        session_factory: async_sessionmaker[AsyncSession],) -> None:
    data = json.loads(message.value.decode("utf-8"))
    event = StudentEvent.model_validate(data)
    async with session_factory.begin() as session:
        handler = handler_factory(session)
        await  handler.handle(event)

async def _send_to_dlq(producer: AIOKafkaProducer, message, exc: Exception, attempt: int) -> None:
    await producer.send_and_wait(
        settings.student_events_dlq_topic,
        key=message.key,
        value=message.value,
        headers=_meta_headers(message, exc, attempt),
    )

async def _schedule_retry(producer: AIOKafkaProducer, message, exc: RetryException, attempt: int) -> None:
    requested_delay = exc.retry_delay if exc.retry_delay is not None else settings.retry_delay_seconds
    delay = min(requested_delay, settings.max_retry_delay_seconds)
    headers = _meta_headers(message, exc, attempt) + [("retry_at", str(time.time() + delay).encode("utf-8"))]
    await producer.send_and_wait(
        settings.student_events_retry_topic,
        key=message.key,
        value=message.value,
        headers=headers,
    )

async def _process_message(message, producer: AIOKafkaProducer, handler_factory: Callable[[AsyncSession], StudentEventService],
                           session_factory: async_sessionmaker[AsyncSession],) -> None:
    attempt = _attempt_number(message)
    try:
        await _process_once(message, handler_factory, session_factory)
        return
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.exception(f"Non-retryable error for offset {message.offset}, sending straight to DLQ")
        await _send_to_dlq(producer, message, exc, attempt)
    except RetryException as exc:
        logger.exception(f"Attempt {attempt}/{settings.max_attempts} failed for offset {message.offset}")
        if attempt >= settings.max_attempts:
            await _send_to_dlq(producer, message, exc, attempt)
            return
        else:
            await _schedule_retry(producer, message, exc, attempt)


async def _wait_until_due(message) -> None:
    retry_at = _header(message, "retry_at")
    if retry_at is None:
        return
    remaining = float(retry_at) - time.time()
    if remaining > 0:
        await asyncio.sleep(min(remaining, settings.max_retry_delay_seconds))


async def _consume(
    topic: str,
    group_id: str,
    handler_factory: Callable[[AsyncSession], StudentEventService],
    session_factory: async_sessionmaker[AsyncSession],
    wait_for_retry_at: bool,
) -> None:
    _check_retry_budget()
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        max_poll_interval_ms=settings.max_poll_interval_seconds * 1000,
    )
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await consumer.start()
    await producer.start()
    try:
        async for message in consumer:
            if wait_for_retry_at:
                await _wait_until_due(message)
            await _process_message(message, producer, handler_factory, session_factory)
            tp = TopicPartition(message.topic, message.partition)
            await consumer.commit({tp: message.offset + 1})
    finally:
        await consumer.stop()
        await producer.stop()


async def run_student_events_consumer(
        handler_factory: Callable[[AsyncSession], StudentEventService] = _default_handler_factory,
        session_factory: async_sessionmaker[AsyncSession] = SessionFactory,) -> None:
    await _consume(
        settings.student_events_topic, settings.student_events_group_id,
        handler_factory, session_factory, wait_for_retry_at=False)

async def run_student_events_retry_consumer(
    handler_factory: Callable[[AsyncSession], StudentEventService] = _default_handler_factory,
    session_factory: async_sessionmaker[AsyncSession] = SessionFactory,
) -> None:
    await _consume(
        settings.student_events_retry_topic, settings.student_events_retry_group_id,
        handler_factory, session_factory, wait_for_retry_at=True)