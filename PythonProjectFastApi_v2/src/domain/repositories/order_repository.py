from abc import ABC, abstractmethod
from uuid import UUID
from src.domain.entities.order import Order


class AbstractOrderRepository(ABC):

    @abstractmethod
    async def create(self, order: Order) -> Order:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> Order | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[Order]:
        raise NotImplementedError