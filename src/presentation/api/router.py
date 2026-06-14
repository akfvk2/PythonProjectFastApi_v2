from fastapi import APIRouter, Depends, status
from uuid import UUID
from src.application.use_case.create_order import CreateOrderUseCase
from src.presentation.api.shemas import OrderCreate, OrderRead
from src.presentation.api.dependencies import get_repository
from src.infrastructure.db.order_repo_impl import SQLAlchemyOrderRepository
from src.application.use_case.get_order_by_user import GetOrdersByUserUseCase
from src.application.use_case.commands import CreateOrderCommand

router = APIRouter()



@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    repository: SQLAlchemyOrderRepository = Depends(get_repository),
):
    use_case = CreateOrderUseCase(repository)
    command = CreateOrderCommand(
        title=order_in.title,
        price=order_in.price,
        description=order_in.description,
        user_id=order_in.user_id,
    )
    return await use_case.execute(command)

@router.get("/by-user/{user_id}", response_model=list[OrderRead])
async def get_orders_by_user(
    user_id: UUID,
    repository: SQLAlchemyOrderRepository = Depends(get_repository),
):
    use_case = GetOrdersByUserUseCase(repository)
    return await use_case.execute(user_id)