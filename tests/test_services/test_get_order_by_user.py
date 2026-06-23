import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from types import SimpleNamespace
from datetime import datetime, timezone
from src.orders.service import OrderService
from src.orders.models import OrderStatus


@pytest.fixture
def mock_repo():
    return AsyncMock()


def make_order_model(title, price, user_id=None):
    return SimpleNamespace(
        id=uuid4(),
        title=title,
        price=price,
        description="",
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        user_id=user_id,
    )


async def test_get_orders_by_user_returns_list(mock_repo):
    user_id = uuid4()
    mock_repo.get_by_user_id.return_value = [make_order_model("Test", 100.0, user_id)]

    result = await OrderService(mock_repo).get_orders_by_user(user_id)

    assert len(result) == 1
    assert result[0].title == "Test"


async def test_get_orders_by_user_returns_empty_list(mock_repo):
    mock_repo.get_by_user_id.return_value = []

    result = await OrderService(mock_repo).get_orders_by_user(uuid4())

    assert result == []


async def test_get_orders_by_user_calls_repo_with_correct_id(mock_repo):
    user_id = uuid4()
    mock_repo.get_by_user_id.return_value = []

    await OrderService(mock_repo).get_orders_by_user(user_id)

    mock_repo.get_by_user_id.assert_called_once_with(user_id)