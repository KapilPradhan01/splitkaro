import enum
from sqlalchemy import Column, String, Float, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class SettlementStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    from_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(SettlementStatus), default=SettlementStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)