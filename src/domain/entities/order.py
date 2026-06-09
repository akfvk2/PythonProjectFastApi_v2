from dataclasses import dataclass, field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional


class OrderStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Order:
    title: str
    price: float
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    description: str = ""
    user_id: Optional[UUID] = None