import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_case.get_order_by_user import GetOrdersByUserUseCase
from src.domain.entities.order import Order


@pytest.fixture
def mock_repo():
    return AsyncMock()


async def test_get_orders_by_user_returns_list(mock_repo):
    user_id = uuid4()
    orders = [Order(title="Test", price=100.0, user_id=user_id)]
    mock_repo.get_by_user_id.return_value = orders

    result = await GetOrdersByUserUseCase(mock_repo).execute(user_id)

    assert len(result) == 1
    assert result[0].title == "Test"


async def test_get_orders_by_user_returns_empty_list(mock_repo):
    mock_repo.get_by_user_id.return_value = []

    result = await GetOrdersByUserUseCase(mock_repo).execute(uuid4())

    assert result == []


async def test_get_orders_by_user_calls_repo_with_correct_id(mock_repo):
    user_id = uuid4()
    mock_repo.get_by_user_id.return_value = []

    await GetOrdersByUserUseCase(mock_repo).execute(user_id)

    mock_repo.get_by_user_id.assert_called_once_with(user_id)