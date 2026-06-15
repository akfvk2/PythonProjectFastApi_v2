from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.infrastructure.db.session import get_session
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.application.use_case.create_order import CreateOrderUseCase
from src.application.use_case.get_order_by_user import GetOrdersByUserUseCase


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractOrderRepository:
    return SQLAlchemyOrderRepository(session)


def get_create_order_use_case(
    repository: AbstractOrderRepository = Depends(get_repository),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repository)

def get_orders_by_user_case(
        repository: AbstractOrderRepository = Depends(get_repository),
) -> GetOrdersByUserUseCase:
    return GetOrdersByUserUseCase(repository)

