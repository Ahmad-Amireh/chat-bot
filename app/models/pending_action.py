from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class PendingAction(Base):
    __tablename__ = "pending_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(50), nullable=False)
    tool_args: Mapped[str] = mapped_column(String(500), nullable=False)  # stored as JSON string
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="pending_actions")