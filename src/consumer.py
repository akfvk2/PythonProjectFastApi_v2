import asyncio
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.config import settings
from src.student_event_schemas import StudentEvent
from src.student_event_handler import StudentEventService
import json
from pydantic import ValidationError
from src.database import SessionFactory

logger = logging.getLogger(__name__)

_handler = StudentEventService()


async def _process_once(message) -> None:
    data = json.loads(message.value.decode("utf-8"))
    event = StudentEvent.model_validate(data)
    async with SessionFactory() as session:
        await _handler.handle(event, session)

async def _process_message(message, dlq_producer: AIOKafkaProducer) -> None:
    for attempt in range(1, settings.max_attempts + 1):
        try:
            await _process_once(message)
            return
        except (json.JSONDecodeError, ValidationError):
            logger.exception(f"Non-retryable error for offset {message.offset}, sending straight to DLQ")
            await dlq_producer.send_and_wait(
                settings.student_events_dlq_topic,
                key=message.key,
                value=message.value)
            return
        except Exception:
            logger.exception(f"Attempt {attempt}/{settings.max_attempts} failed for offset {message.offset}")
            if attempt == settings.max_attempts:
                await dlq_producer.send_and_wait(
                    settings.student_events_dlq_topic,
                    key=message.key,
                    value=message.value)
                return
            await asyncio.sleep(1)


async def run_student_events_consumer() -> None:
    consumer = AIOKafkaConsumer(
        settings.student_events_topic,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.student_events_group_id,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )
    dlq_producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await consumer.start()
    await dlq_producer.start()
    try:
        async for message in consumer:
            await _process_message(message, dlq_producer)
            await consumer.commit()
    finally:
        await consumer.stop()
        await dlq_producer.stop()