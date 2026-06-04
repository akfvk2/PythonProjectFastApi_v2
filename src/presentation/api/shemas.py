from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from src.domain.entities.order import OrderStatus


class OrderCreate(BaseModel):
    order_id: UUID

class OrderRead(BaseModel):
    id: UUID
    title: str
    price: float
    description: str
    status: OrderStatus
    created_at: datetime
    external_data: dict = {}

    model_config = ConfigDict(from_attributes=True)