import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import OperationalError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.students.processed_event_model import ProcessedEventModel
from src.students.exceptions import RetryException

logger = logging.getLogger(__name__)


class ProcessedEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def try_mark_processed(self, event_id: UUID) -> bool:
        stmt = (
            pg_insert(ProcessedEventModel)
            .values(event_id=event_id)
            .on_conflict_do_nothing(index_elements=["event_id"])
        )
        try:
            result = await self.session.execute(stmt)
        except OperationalError as exc:
            raise RetryException(
                f"Temporary DB error while marking event {event_id} as processed", retry_delay=5.0,
            ) from exc
        return result.rowcount > 0