import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.students.student_event_service import StudentEventService
from src.students.student_event_schemas import StudentEvent


@pytest.fixture
def mock_repo():
    return AsyncMock()

def make_event() -> StudentEvent:
    return StudentEvent(
        event="student_created",
        event_id=uuid4(),
        student_id=uuid4(),
        name="Ivan",
    )

async def test_handle_new_event_calls_repo_with_event_id(mock_repo):
    mock_repo.try_mark_processed.return_value = True
    event = make_event()
    await StudentEventService(mock_repo).handle(event)
    mock_repo.try_mark_processed.assert_called_once_with(event.event_id)

async def test_handle_new_event_logs_created(mock_repo, caplog):
    mock_repo.try_mark_processed.return_value = True
    event = make_event()
    with caplog.at_level("INFO"):
        await StudentEventService(mock_repo).handle(event)
    assert "New student created" in caplog.text

async def test_handle_duplicate_event_skips_without_creating(mock_repo, caplog):
    mock_repo.try_mark_processed.return_value = False
    event = make_event()
    with caplog.at_level("INFO"):
        await StudentEventService(mock_repo).handle(event)
    assert "already processed" in caplog.text
    assert "New student created" not in caplog.text