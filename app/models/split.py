from sqlalchemy import Column, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base  # ← this line is missing
import uuid

class Split(Base):
    __tablename__ = "splits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    expense_id = Column(String, ForeignKey("expenses.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount_owed = Column(Float, nullable=False)
    is_settled = Column(Boolean, default=False)