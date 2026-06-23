import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from types import SimpleNamespace
from datetime import datetime, timezone
from src.orders.service import OrderService
from src.orders.schemas import OrderCreate
from src.orders.models import OrderStatus


@pytest.fixture
def mock_repo():
    return AsyncMock()


def make_order_model(title, price, description="", user_id=None):
    return SimpleNamespace(
        id=uuid4(),
        title=title,
        price=price,
        description=description,
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        user_id=user_id,
    )


async def test_create_order_saves_to_repo(mock_repo):
    mock_repo.create.return_value = make_order_model("New", 50.0, "desc")

    result = await OrderService(mock_repo).create_order(
        OrderCreate(title="New", price=50.0, description="desc", user_id=uuid4())
    )

    mock_repo.create.assert_called_once()
    assert result.title == "New"


async def test_create_order_with_user_id(mock_repo):
    user_id = uuid4()
    mock_repo.create.return_value = make_order_model("Order", 10.0, user_id=user_id)

    result = await OrderService(mock_repo).create_order(
        OrderCreate(title="Order", price=10.0, user_id=user_id)
    )

    assert result.user_id == user_id


async def test_create_order_passes_correct_data_to_repo(mock_repo):
    mock_repo.create.return_value = make_order_model("A", 1.0, "B")

    await OrderService(mock_repo).create_order(
        OrderCreate(title="A", price=1.0, description="B", user_id=uuid4())
    )

    created_order = mock_repo.create.call_args[0][0]
    assert created_order.title == "A"
    assert created_order.price == 1.0
    assert created_order.description == "B"