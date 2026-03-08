from __future__ import annotations
from sqlalchemy import String, DateTime, func, INTEGER, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(100), default="New Chat")
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="sessions")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="session", cascade="all, delete-orphan")