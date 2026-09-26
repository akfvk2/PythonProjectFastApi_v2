import pytest
from src.inbox.processed_event_repository import ProcessedEventRepository
from uuid import uuid4



@pytest.fixture
def repo(session):
    return ProcessedEventRepository(session)


async def test_try_mark_processed_returns_true_for_new_event(repo):
    result = await repo.try_mark_processed(uuid4())
    assert result is True


async def test_try_mark_processed_returns_false_for_duplicate(repo):
    event_id = uuid4()
    await repo.try_mark_processed(event_id)
    result = await repo.try_mark_processed(event_id)
    assert result is False