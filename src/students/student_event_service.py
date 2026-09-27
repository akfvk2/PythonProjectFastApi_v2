import logging
from src.students.student_event_schemas import StudentEvent
from src.inbox.processed_event_repository import ProcessedEventRepository
from sqlalchemy.exc import OperationalError
from src.exceptions import RetryException

logger = logging.getLogger(__name__)

class StudentEventService:
    def __init__(self, repo: ProcessedEventRepository):
        self.repo = repo

    async def handle(self, event: StudentEvent) -> None:
        try:
            is_new = await self.repo.try_mark_processed(event.event_id)
        except OperationalError as exc:
            raise RetryException(
                f"Temporary DB error while processing event {event.event_id}", retry_delay=5.0,
            ) from exc
        if not is_new:
            logger.info(f"Event {event.event_id} already processed, skipping duplicate")
            return
        logger.info(f"New student created: {event}")