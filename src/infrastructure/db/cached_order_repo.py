import json
from uuid import UUID
from datetime import datetime
from redis.asyncio import Redis
from src.domain.entities.order import Order, OrderStatus
from src.domain.repositories.order_repository import AbstractOrderRepository
from src.infrastructure.config import settings





class CachedOrderRepository(AbstractOrderRepository):
    def __init__(self, repo: AbstractOrderRepository, redis: Redis):
        self._repo = repo
        self._redis = redis

    def _key(self, order_id: UUID) -> str:
        return f"order:{order_id}"

    def _serialize(self, order: Order) -> str:
        return json.dumps({
            "id": str(order.id),
            "title": order.title,
            "price": order.price,
            "description": order.description,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "user_id": str(order.user_id) if order.user_id else None,
        })

    def _deserialize(self, data: str) -> Order:
        d = json.loads(data)
        return Order(
            id=UUID(d["id"]),
            title=d["title"],
            price=d["price"],
            description=d["description"],
            status=OrderStatus(d["status"]),
            created_at=datetime.fromisoformat(d["created_at"]),
            user_id=UUID(d["user_id"]) if d.get("user_id") else None,
        )

    async def get_by_id(self, order_id: UUID) -> Order | None:
        try:
            cached = await self._redis.get(self._key(order_id))
            if cached:
                return self._deserialize(cached)
        except Exception:
            pass
        order = await self._repo.get_by_id(order_id)
        if order:
            try:
                await self._redis.set(self._key(order_id), self._serialize(order), ex=settings.cache_ttl)
            except Exception:
                pass
        return order

    async def create(self, order: Order) -> Order:
        created = await self._repo.create(order)
        try:
            await self._redis.set(self._key(created.id), self._serialize(created), ex=settings.cache_ttl)
        except Exception:
            pass
        return created

    async def get_all(self) -> list[Order]:
        return await self._repo.get_all()

    async def get_by_user_id(self, user_id: UUID) -> list[Order]:
        return await self._repo.get_by_user_id(user_id)