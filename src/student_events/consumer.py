import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.config import settings
from src.cache import redis_client

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3


def _handle_event(data: dict) -> None:
    logger.info(f"New student created: {data}")


async def _process_message(message, dlq_producer: AIOKafkaProducer) -> None:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            data = json.loads(message.value.decode("utf-8"))
            event_id = data.get("event_id")
            if event_id is not None:
                already_processed = await redis_client.get(f"processed_event:{event_id}")
                if already_processed:
                    logger.info(f"Event {event_id} already processed, skipping duplicate")
                    return
            _handle_event(data)
            if event_id is not None:
                await redis_client.setex(f"processed_event:{event_id}", settings.dedup_ttl_seconds, "1")
            return
        except Exception:
            logger.exception(f"Attempt {attempt}/{MAX_ATTEMPTS} failed for offset {message.offset}")
            if attempt == MAX_ATTEMPTS:
                await dlq_producer.send_and_wait(
                    settings.student_events_dlq_topic,
                    key=message.key,
                    value=message.value,
                )
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