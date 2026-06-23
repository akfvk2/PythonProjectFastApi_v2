from fastapi import APIRouter, Depends, status
from uuid import UUID
from src.orders.schemas import OrderCreate, OrderRead
from src.orders.service import OrderService
from src.orders.dependencies import get_order_service

router = APIRouter()


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return await service.create_order(order_in)


@router.get("/by-user/{user_id}", response_model=list[OrderRead])
async def get_orders_by_user(
    user_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    return await service.get_orders_by_user(user_id)
