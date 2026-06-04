from uuid import UUID
from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.application.ports.first_service_client import AbstractFirstServiceClient
from src.domain.exceptions import ExternalServiceError


class CreateOrderUseCase:
    def __init__(
        self,
        repository: AbstractOrderRepository,
        client: AbstractFirstServiceClient,
    ):
        self.repository = repository
        self.client = client

    async def execute(self, order_id: UUID) -> Order:
        try:
            external_data = await self.client.get_order(order_id)
        except Exception as e:
            raise ExternalServiceError() from e
        order = Order(
            id=order_id,
            title=external_data.get("title", ""),
            price=external_data.get("price", 0.0),
            description=external_data.get("description", ""),
        )
        return await self.repository.create(order)
