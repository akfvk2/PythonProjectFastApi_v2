import asyncio
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.config import settings
from src.students.student_event_schemas import StudentEvent
from src.students.student_event_service import StudentEventService
import json
from pydantic import ValidationError
from src.database import SessionFactory
from src.students.exceptions import RetryException
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession
from aiokafka import TopicPartition
from src.students.processed_event_repository import ProcessedEventRepository

logger = logging.getLogger(__name__)

def _default_handler_factory(session: AsyncSession) -> StudentEventService:
    return StudentEventService(ProcessedEventRepository(session))

def _dlq_headers(message, exc: Exception, attempt: int) -> list[tuple[str, bytes]]:
    return [
        ("error_reason", str(exc).encode("utf-8")),
        ("source_topic", message.topic.encode("utf-8")),
        ("source_partition", str(message.partition).encode("utf-8")),
        ("source_offset", str(message.offset).encode("utf-8")),
        ("attempts", str(attempt).encode("utf-8")),
    ]
def _check_retry_budget() -> None:
    worst_case_seconds = settings.max_attempts * settings.retry_delay_seconds
    limit_seconds = settings.max_poll_interval_seconds
    if worst_case_seconds >= limit_seconds * 0.5:
        logger.warning(
            f"Retry budget ({worst_case_seconds}s) is too close to "
            f"max_poll_interval_seconds ({limit_seconds}s) — risk of consumer group rebalance"
        )

async def _process_once(message, handler_factory: Callable[[AsyncSession], StudentEventService]) -> None:
    data = json.loads(message.value.decode("utf-8"))
    event = StudentEvent.model_validate(data)
    async with SessionFactory() as session:
        handler = handler_factory(session)
        try:
            await handler.handle(event)
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()

async def _process_message(message, dlq_producer: AIOKafkaProducer, handler_factory: Callable[[AsyncSession], StudentEventService],) -> None:
    for attempt in range(1, settings.max_attempts + 1):
        try:
            await _process_once(message, handler_factory)
            return
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.exception(f"Non-retryable error for offset {message.offset}, sending straight to DLQ")
            await dlq_producer.send_and_wait(
                settings.student_events_dlq_topic,
                key=message.key,
                value=message.value,
                headers=_dlq_headers(message, exc, attempt),
            )
            return
        except RetryException as exc:
            logger.exception(f"Attempt {attempt}/{settings.max_attempts} failed for offset {message.offset}")
            if attempt == settings.max_attempts:
                await dlq_producer.send_and_wait(
                    settings.student_events_dlq_topic,
                    key=message.key,
                    value=message.value,
                    headers=_dlq_headers(message, exc, attempt),
                )
                return
            delay = exc.retry_delay if exc.retry_delay is not None else settings.retry_delay_seconds
            await asyncio.sleep(delay)


async def run_student_events_consumer(handler_factory: Callable[[AsyncSession], StudentEventService] = _default_handler_factory,) -> None:
    _check_retry_budget()
    consumer = AIOKafkaConsumer(
        settings.student_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.student_events_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        max_poll_interval_ms=settings.max_poll_interval_seconds * 1000,
    )
    dlq_producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await consumer.start()
    await dlq_producer.start()
    try:
        async for message in consumer:
            await _process_message(message, dlq_producer, handler_factory)
            tp = TopicPartition(message.topic, message.partition)
            await consumer.commit({tp: message.offset + 1})
    finally:
        await consumer.stop()
        await dlq_producer.stop()