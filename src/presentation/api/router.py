from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from src.infrastructure.db.session import get_session
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository
from src.application.use_case.create_order import CreateOrderUseCase
from src.application.use_case.get_order import GetOrderUseCase
from src.presentation.api.shemas import OrderCreate, OrderRead
from src.domain.exceptions import OrderNotFoundError
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


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    repository: CachedOrderRepository = Depends(get_repository),
):
    use_case = CreateOrderUseCase(repository)
    return await use_case.execute(
        title=order_in.title,
        price=order_in.price,
        description=order_in.description,
        user_id=order_in.user_id,
    )


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    repository: CachedOrderRepository = Depends(get_repository),
):
    use_case = GetOrderUseCase(repository)
    try:
        order = await use_case.execute(order_id)
    except OrderNotFoundError:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/by-user/{user_id}", response_model=list[OrderRead])
async def get_orders_by_user(
    user_id: UUID,
    repository: CachedOrderRepository = Depends(get_repository),
):
    orders = await repository.get_by_user_id(user_id)
    return orders