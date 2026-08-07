from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from src.orders.models import OrderStatus


class OrderCreate(BaseModel):
    title: str
    price: float
    description: str = ""
    user_id: UUID
    reference_id: UUID | None = None

class OrderRead(BaseModel):
    id: UUID
    title: str
    price: float
    description: str
    status: OrderStatus
    created_at: datetime
    user_id: UUID | None = None
    reference_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)