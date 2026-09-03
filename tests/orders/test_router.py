import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.application import get_app
from src.orders.schemas import OrderRead
from src.orders.models import OrderStatus
from datetime import datetime, timezone



@pytest.fixture
def order_id():
    return uuid4()


@pytest.fixture
def sample_order(order_id):
    return OrderRead(
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
    with TestClient(app) as c:
        yield c



def test_create_order_returns_201(client, sample_order):
    with patch(
        "src.orders.service.OrderService.create_order",
        new=AsyncMock(return_value=sample_order),
    ):
        response = client.post("/v1/orders/", json={
            "title": "Test",
            "price": 100.0,
            "user_id": str(uuid4())
        })

    assert response.status_code == 201


def test_create_order_missing_required_fields(client):
    response = client.post("/v1/orders/", json={})
    assert response.status_code == 422


def test_create_order_invalid_user_id(client):
    response = client.post(
        "/v1/orders/",
        json={"title": "Test", "price": 10.0, "user_id": "not-a-uuid"},
    )
    assert response.status_code == 422
