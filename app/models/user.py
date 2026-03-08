from __future__ import annotations
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    sessions:Mapped[list["ChatSession"]]= relationship("ChatSession", 
                                                     back_populates="user", 
                                                     cascade="all, delete-orphan")
    

    
    



