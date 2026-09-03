from uuid import UUID

from src.orders.exceptions import OrderNotFoundError
from src.orders.models import OrderModel
from src.orders.schemas import OrderCreate, OrderRead
from src.orders.repository import AbstractOrderRepository


class OrderService:
    def __init__(self, repository: AbstractOrderRepository):
        self.repository = repository

    def _to_model(self, order_in: OrderCreate) -> OrderModel:
        return OrderModel(
            title=order_in.title,
            price=order_in.price,
            description=order_in.description,
            user_id=order_in.user_id,
            reference_id=order_in.reference_id,
        )


    async def create_order(self, order_in: OrderCreate) -> OrderRead:
        order = self._to_model(order_in)
        db_order = await self.repository.create(order)
        return OrderRead.model_validate(db_order)

    async def get_orders_by_user(self, user_id: UUID) -> list[OrderRead]:
        orders = await self.repository.get_by_user_id(user_id)
        if not orders:
            raise OrderNotFoundError(user_id)
        return [OrderRead.model_validate(o) for o in orders]

    async def get_order_by_reference_id(self, reference_id: UUID) -> OrderRead | None:
        order = await self.repository.get_by_reference_id(reference_id)
        if not order:
            return None
        return OrderRead.model_validate(order)