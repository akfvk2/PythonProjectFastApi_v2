from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.orders.repository import OrderRepository, AbstractOrderRepository
from src.orders.service import OrderService


def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractOrderRepository:
    return OrderRepository(session)


def get_order_service(
    repository: AbstractOrderRepository = Depends(get_order_repository),
) -> OrderService:
    return OrderService(repository)