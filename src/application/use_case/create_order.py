from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.application.use_case.commands import CreateOrderCommand


class CreateOrderUseCase:
    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    async def execute(self, command: CreateOrderCommand) -> Order:
        order = Order(
            title=command.title,
            price=command.price,
            description=command.description,
            user_id=command.user_id,
        )
        return await self.repository.create(order)