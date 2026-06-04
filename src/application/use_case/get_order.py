from uuid import UUID
from src.domain.entities.order import Order
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.application.ports.first_service_client import AbstractFirstServiceClient
from src.domain.exceptions import OrderNotFoundError, ExternalServiceError


class GetOrderUseCase:
    def __init__(
        self,
        repository: AbstractOrderRepository,
        client: AbstractFirstServiceClient,
    ):
        self.repository = repository
        self.client = client

    async def execute(self, order_id: UUID) -> Order | None:
        # 1. Идём в первый сервис за обогащением
        try:
            external_data = await self.client.get_order(order_id)
        except Exception as e:
            raise ExternalServiceError() from e

        # 2. Достаём из своей БД
        order = await self.repository.get_by_id(order_id)

        if order is None:
            raise OrderNotFoundError(order_id)

        # 3. Соединяем
        order.external_data = external_data
        return order