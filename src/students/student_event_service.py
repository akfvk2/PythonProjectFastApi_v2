import logging
from src.students.student_event_schemas import StudentEvent
from src.inbox.processed_event_repository import ProcessedEventRepository

logger = logging.getLogger(__name__)

class StudentEventService:
    def __init__(self, repo: ProcessedEventRepository):
        self.repo = repo

    async def handle(self, event: StudentEvent) -> None:
        is_new = await self.repo.try_mark_processed(event.event_id)
        if not is_new:
            logger.info(f"Event {event.event_id} already processed, skipping duplicate")
            return
        logger.info(f"New student created: {event}")