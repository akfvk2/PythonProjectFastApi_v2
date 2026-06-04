import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from src.application.use_case.get_order import GetOrderUseCase
from src.domain.entities.order import Order
from src.domain.exceptions import OrderNotFoundError, ExternalServiceError


@pytest.fixture
def mock_repo():
    return AsyncMock()


@pytest.fixture
def mock_client():
    return AsyncMock()


async def test_get_order_returns_order_with_external_data(mock_repo, mock_client):
    order_id = uuid4()
    order = Order(id=order_id, title="Test", price=100.0)
    mock_repo.get_by_id.return_value = order
    mock_client.get_order.return_value = {"title": "Test", "extra": "data"}

    result = await GetOrderUseCase(mock_repo, mock_client).execute(order_id)

    assert result.id == order_id
    assert result.external_data == {"title": "Test", "extra": "data"}


async def test_get_order_raises_not_found(mock_repo, mock_client):
    mock_repo.get_by_id.return_value = None
    mock_client.get_order.return_value = {}

    with pytest.raises(OrderNotFoundError):
        await GetOrderUseCase(mock_repo, mock_client).execute(uuid4())


async def test_get_order_raises_external_service_error(mock_repo, mock_client):
    mock_client.get_order.side_effect = Exception("connection error")

    with pytest.raises(ExternalServiceError):
        await GetOrderUseCase(mock_repo, mock_client).execute(uuid4())