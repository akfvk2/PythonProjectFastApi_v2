import logging
from src.student_event_schemas import StudentEvent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from src.processed_event_model import ProcessedEventModel

logger = logging.getLogger(__name__)

class StudentEventService:
    async def handle(self, event: StudentEvent, session: AsyncSession) -> None:
        session.add(ProcessedEventModel(event_id=event.event_id))
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            logger.info(f"Event {event.event_id} already processed, skipping duplicate")
            return
        logger.info(f"New student created: {event}")
