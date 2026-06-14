import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_case.create_order import CreateOrderUseCase
from src.domain.entities.order import Order
from src.application.use_case.commands import CreateOrderCommand

@pytest.fixture
def mock_repo():
    return AsyncMock()


async def test_create_order_saves_to_repo(mock_repo):
    mock_repo.create.return_value = Order(title="New", price=50.0, description="desc")

    result = await CreateOrderUseCase(mock_repo).execute(
        CreateOrderCommand(title="New", price=50.0, description="desc", user_id=uuid4())
    )

    mock_repo.create.assert_called_once()
    assert result.title == "New"



async def test_create_order_with_user_id(mock_repo):
    user_id = uuid4()
    mock_repo.create.return_value = Order(title="Order", price=10.0, user_id=user_id)

    result = await CreateOrderUseCase(mock_repo).execute(CreateOrderCommand(
        title="Order", price=10.0, user_id=user_id
    ))

    assert result.user_id == user_id


async def test_create_order_passes_correct_data_to_repo(mock_repo):
    mock_repo.create.return_value = Order(title="A", price=1.0)

    await CreateOrderUseCase(mock_repo).execute(
        CreateOrderCommand(title="A", price=1.0, description="B", user_id=uuid4())
    )

    created_order = mock_repo.create.call_args[0][0]
    assert created_order.title == "A"
    assert created_order.price == 1.0
    assert created_order.description == "B"