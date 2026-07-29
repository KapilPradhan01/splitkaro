import enum
from sqlalchemy import Column, String, Float, DateTime, Enum ,ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class SplitType(str, enum.Enum):
    EQUAL = "equal"
    EXACT = "exact"
    PERCENTAGE = "percentage"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("groups.id"), nullable=False)
    paid_by = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True)
    split_type = Column(Enum(SplitType), default=SplitType.EQUAL)
    expense_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())