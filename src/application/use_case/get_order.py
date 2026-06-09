from uuid import UUID
from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.domain.exceptions import OrderNotFoundError


class GetOrderUseCase:
    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    async def execute(self, order_id: UUID) -> Order:
        order = await self.repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order