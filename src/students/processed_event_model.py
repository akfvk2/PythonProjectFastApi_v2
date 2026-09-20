from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from uuid import UUID
from datetime import datetime
from src.orders.models import Base
from sqlalchemy import func

class ProcessedEventModel(Base):
    __tablename__ = "student_processed_events"
    event_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())