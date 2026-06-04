from sqlalchemy import String, Float, Enum as SAEnum, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import UUID, uuid4
from datetime import datetime
from src.domain.entities.order import OrderStatus


class Base(DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, default="")
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[OrderStatus] = mapped_column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)