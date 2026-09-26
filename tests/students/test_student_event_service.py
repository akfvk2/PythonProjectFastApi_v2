import pytest
from uuid import uuid4
from src.students.student_event_service import StudentEventService
from src.students.student_event_schemas import StudentEvent
from sqlalchemy import select, func
from src.inbox.processed_event_repository import ProcessedEventRepository
from src.inbox.processed_event_model import ProcessedEventModel

@pytest.fixture
def service(session):
    return StudentEventService(ProcessedEventRepository(session))

def make_event() -> StudentEvent:
    return StudentEvent(
        event="student_created",
        event_id=uuid4(),
        student_id=uuid4(),
        name="Ivan",
    )

async def count_processed(session, event_id) -> int:
    result = await session.execute(
        select(func.count()).select_from(ProcessedEventModel).where(ProcessedEventModel.event_id == event_id)
    )
    return result.scalar_one()

async def test_handle_new_event_marks_it_processed(service, session):
    event = make_event()
    await service.handle(event)
    assert await count_processed(session, event.event_id) == 1


async def test_handle_new_event_logs_created(service, caplog):
    with caplog.at_level("INFO"):
        await service.handle(make_event())
    assert "New student created" in caplog.text

async def test_handle_duplicate_event_is_skipped(service, session, caplog):
    event = make_event()
    await service.handle(event)
    with caplog.at_level("INFO"):
        await service.handle(event)
    assert await count_processed(session, event.event_id) == 1
    assert "already processed" in caplog.text