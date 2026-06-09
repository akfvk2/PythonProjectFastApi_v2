from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository
from uuid import UUID


class CreateOrderUseCase:
    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    async def execute(self, title: str, price: float, description: str = "", user_id: UUID | None = None) -> Order:
        order = Order(title=title, price=price, description=description, user_id=user_id)
        return await self.repository.create(order)
