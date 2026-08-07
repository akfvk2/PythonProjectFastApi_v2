from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.orders.models import OrderModel


class AbstractOrderRepository(ABC):

    @abstractmethod
    async def get_by_reference_id(self, reference_id: UUID) -> OrderModel | None:
        raise NotImplementedError

    @abstractmethod
    async def create(self, order: OrderModel) -> OrderModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_user_id(self, order_id: UUID) -> OrderModel | None:
        raise NotImplementedError



class OrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_reference_id(self, reference_id: UUID) -> OrderModel | None:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.reference_id == reference_id)
        )
        return result.scalar_one_or_none()

    async def create(self, order: OrderModel) -> OrderModel:
        self.session.add(order)
        await self.session.flush()
        return order


    async def get_by_user_id(self, user_id: UUID) -> list[OrderModel]:
        result = await self.session.execute(
            select(OrderModel).where(OrderModel.user_id == user_id)
        )
        return list(result.scalars().all())