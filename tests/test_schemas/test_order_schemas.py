import pytest
from uuid import uuid4, UUID
from pydantic import ValidationError
from src.presentation.api.schemas import OrderCreate, OrderRead
from src.domain.entities.order import OrderStatus
from datetime import datetime, timezone


def test_order_create_with_required_fields():
    user_id = uuid4()
    order = OrderCreate(title="Test Order", price=99.9, user_id=user_id)
    assert order.title == "Test Order"
    assert order.price == 99.9
    assert order.description == ""
    assert order.user_id == user_id


def test_order_create_with_all_fields():
    user_id = uuid4()
    order = OrderCreate(title="Full Order", price=50.0, description="desc", user_id=user_id)
    assert isinstance(order.user_id, UUID)
    assert order.description == "desc"


def test_order_create_invalid_user_id():
    with pytest.raises(ValidationError):
        OrderCreate(title="Test", price=10.0, user_id="not-a-uuid")


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
    }
    order = OrderRead(**data)
    assert order.title == "Test"
    assert order.status == OrderStatus.PENDING


def test_order_read_user_id_defaults_to_none():
    data = {
        "id": uuid4(),
        "title": "Test",
        "price": 10.0,
        "description": "",
        "status": OrderStatus.PENDING,
        "created_at": datetime.now(timezone.utc),
    }
    order = OrderRead(**data)
    assert order.user_id is None
