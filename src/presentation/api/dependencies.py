from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from src.infrastructure.db.session import get_session
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository


def get_repository(
    session: AsyncSession = Depends(get_session),
) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(session)