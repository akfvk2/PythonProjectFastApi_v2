from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.orders.models import OrderModel


class AbstractOrderRepository(ABC):

    @abstractmethod
    async def create(self, order: OrderModel) -> OrderModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_all(self) -> list[OrderModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> list[OrderModel]:
        raise NotImplementedError


class SQLAlchemyOrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        return order

    async def get_by_id(self, order_id: UUID) -> OrderModel | None:
        return await self.session.get(OrderModel, order_id)

    async def get_all(self) -> list[OrderModel]:
        result = await self.session.execute(select(OrderModel))
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: UUID) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.user_id == user_id)
        )
        return list(result.scalars().all())