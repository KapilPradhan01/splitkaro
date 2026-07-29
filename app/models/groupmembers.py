from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base  # ← this line is missing
import uuid

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)