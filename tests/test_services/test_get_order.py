import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_case.get_order import GetOrderUseCase
from src.domain.entities.order import Order
from src.domain.exceptions import OrderNotFoundError


@pytest.fixture
def mock_repo():
    return AsyncMock()


async def test_get_order_returns_order(mock_repo):
    order_id = uuid4()
    order = Order(id=order_id, title="Test", price=100.0)
    mock_repo.get_by_id.return_value = order

    result = await GetOrderUseCase(mock_repo).execute(order_id)

    assert result.id == order_id
    assert result.title == "Test"


async def test_get_order_raises_not_found(mock_repo):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundError):
        await GetOrderUseCase(mock_repo).execute(uuid4())


async def test_get_order_calls_repo_with_correct_id(mock_repo):
    order_id = uuid4()
    mock_repo.get_by_id.return_value = Order(id=order_id, title="T", price=1.0)

    await GetOrderUseCase(mock_repo).execute(order_id)

    mock_repo.get_by_id.assert_called_once_with(order_id)
