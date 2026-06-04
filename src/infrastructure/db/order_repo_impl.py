from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.domain.entities.order import Order, OrderStatus
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.infrastructure.db.models import OrderModel


class SQLAlchemyOrderRepository(AbstractOrderRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            title=order.title,
            description=order.description,
            price=order.price,
            status=order.status,
            created_at=order.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    async def get_by_id(self, order_id: UUID) -> Order | None:
        model = await self.session.get(OrderModel, order_id)
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self) -> list[Order]:
        result = await self.session.execute(select(OrderModel))
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            title=model.title,
            description=model.description,
            price=model.price,
            status=model.status,
            created_at=model.created_at,
        )