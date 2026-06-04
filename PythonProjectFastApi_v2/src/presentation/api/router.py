from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.infrastructure.db.session import get_session
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository
from src.application.ports.first_service_client import AbstractFirstServiceClient
from src.application.use_case.create_order import CreateOrderUseCase
from src.application.use_case.get_order import GetOrderUseCase
from src.presentation.api.shemas import OrderCreate, OrderRead
from src.domain.exceptions import OrderNotFoundError, ExternalServiceError
from redis.asyncio import Redis
from src.infrastructure.db.cached_order_repo import CachedOrderRepository

router = APIRouter()


def get_redis(request: Request) -> Redis:
    return request.app.state.redis

def get_repository(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
) -> CachedOrderRepository:
    raw_repo = SQLAlchemyOrderRepository(session)
    return CachedOrderRepository(raw_repo, redis)


def get_client(request: Request) -> AbstractFirstServiceClient:
    return request.app.state.first_service_client


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    repository: CachedOrderRepository = Depends(get_repository),
    client: AbstractFirstServiceClient = Depends(get_client),
):
    use_case = CreateOrderUseCase(repository, client)
    try:
        return await use_case.execute(order_in.order_id)
    except ExternalServiceError:
        raise HTTPException(status_code=503, detail="First service unavailable")


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    repository: CachedOrderRepository = Depends(get_repository),
    client: AbstractFirstServiceClient = Depends(get_client),
):
    use_case = GetOrderUseCase(repository, client)
    try:
        order = await use_case.execute(order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    except ExternalServiceError:
        raise HTTPException(status_code=503, detail="First service unavailable")
    return order