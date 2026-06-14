from uuid import UUID
from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository


class GetOrdersByUserUseCase:
    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    async def execute(self, user_id: UUID) -> list[Order]:
        return await self.repository.get_by_user_id(user_id)