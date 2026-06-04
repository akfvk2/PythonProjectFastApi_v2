import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_case.create_order import CreateOrderUseCase
from src.domain.entities.order import Order
from src.domain.exceptions import ExternalServiceError


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_client():
    return AsyncMock()


async def test_create_order_saves_to_db(mock_repo, mock_client):
    order_id = uuid4()
    mock_client.get_order.return_value = {"title": "New", "price": 50.0, "description": "desc"}
    mock_repo.create.return_value = Order(id=order_id, title="New", price=50.0)

    result = await CreateOrderUseCase(mock_repo, mock_client).execute(order_id)

    mock_repo.create.assert_called_once()
    assert result.title == "New"


async def test_create_order_raises_external_service_error(mock_repo, mock_client):
    mock_client.get_order.side_effect = Exception("timeout")

    with pytest.raises(ExternalServiceError):
        await CreateOrderUseCase(mock_repo, mock_client).execute(uuid4())