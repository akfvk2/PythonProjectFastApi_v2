from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateOrderCommand:
    title: str
    price: float
    user_id: UUID
    description: str = ""