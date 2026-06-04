import pytest
from uuid import uuid4, UUID
from pydantic import ValidationError
from src.presentation.api.shemas import OrderCreate, OrderRead
from src.domain.entities.order import OrderStatus
from datetime import datetime, timezone

def test_order_create_valid_uuid():
    order = OrderCreate(order_id=uuid4())
    assert isinstance(order.order_id, UUID)

def test_order_create_invalid_uuid():
    with pytest.raises(ValidationError):
        OrderCreate(order_id="not-a-uuid")

def test_order_create_missing_field():
    with pytest.raises(ValidationError):
        OrderCreate()


def test_order_read_from_dict():
    data = {
        "id": uuid4(),
        "title": "Test",
        "price": 99.9,
        "description": "desc",
        "status": OrderStatus.PENDING,
        "created_at": datetime.now(timezone.utc),
        "external_data": {},
    }
    order = OrderRead(**data)
    assert order.title == "Test"
    assert order.status == OrderStatus.PENDING

def test_order_read_external_data_defaults_to_empty():
    data = {
        "id": uuid4(),
        "title": "Test",
        "price": 10.0,
        "description": "",
        "status": OrderStatus.PENDING,
        "created_at": datetime.now(timezone.utc),
    }
    order = OrderRead(**data)
    assert order.external_data == {}