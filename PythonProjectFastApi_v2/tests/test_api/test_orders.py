import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.presentation.api.application import get_app
from src.domain.entities.order import Order, OrderStatus
from src.domain.exceptions import OrderNotFoundError, ExternalServiceError
from datetime import datetime, timezone


@pytest.fixture
def order_id():
    return uuid4()


@pytest.fixture
def sample_order(order_id):
    return Order(
        id=order_id,
        title="Test",
        price=100.0,
        description="desc",
        status=OrderStatus.PENDING,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def client():
    app = get_app()
    mock_client = AsyncMock()
    app.state.first_service_client = mock_client
    with TestClient(app) as c:
        yield c


def test_get_order_returns_200(client, sample_order, order_id):
    with patch(
        "src.application.use_case.get_order.GetOrderUseCase.execute",
        new=AsyncMock(return_value=sample_order),
    ):
        response = client.get(f"/v1/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Test"


def test_get_order_returns_404(client, order_id):
    with patch(
        "src.application.use_case.get_order.GetOrderUseCase.execute",
        new=AsyncMock(side_effect=OrderNotFoundError(order_id)),
    ):
        response = client.get(f"/v1/orders/{order_id}")

    assert response.status_code == 404


def test_get_order_returns_503(client, order_id):
    with patch(
        "src.application.use_case.get_order.GetOrderUseCase.execute",
        new=AsyncMock(side_effect=ExternalServiceError()),
    ):
        response = client.get(f"/v1/orders/{order_id}")

    assert response.status_code == 503


def test_create_order_returns_201(client, sample_order, order_id):
    with patch(
        "src.application.use_case.create_order.CreateOrderUseCase.execute",
        new=AsyncMock(return_value=sample_order),
    ):
        response = client.post("/v1/orders/", json={"order_id": str(order_id)})

    assert response.status_code == 201


def test_create_order_returns_503(client, order_id):
    with patch(
        "src.application.use_case.create_order.CreateOrderUseCase.execute",
        new=AsyncMock(side_effect=ExternalServiceError()),
    ):
        response = client.post("/v1/orders/", json={"order_id": str(order_id)})

    assert response.status_code == 503


def test_create_order_invalid_uuid(client):
    response = client.post("/v1/orders/", json={"order_id": "not-a-uuid"})
    assert response.status_code == 422