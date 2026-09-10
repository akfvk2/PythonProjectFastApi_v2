import logging
from src.students.student_event_schemas import StudentEvent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from src.students.processed_event_model import ProcessedEventModel
from src.students.exceptions import RetryException
from sqlalchemy.dialects.postgresql import insert as pg_insert

logger = logging.getLogger(__name__)

class StudentEventService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def handle(self, event: StudentEvent) -> None:
        stmt = (
            pg_insert(ProcessedEventModel)
            .values(event_id=event.event_id)
            .on_conflict_do_nothing(index_elements=["event_id"])
        )
        try:
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                await self.session.rollback()
                logger.info(f"Event {event.event_id} already processed, skipping duplicate")
                return
            logger.info(f"New student created: {event}")
            await self.session.commit()
        except OperationalError as exc:
            await self.session.rollback()
            raise RetryException(f"Temporary DB error while processing event {event.event_id}") from exc