from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.chat_session import ChatSession
from app.models.user import User
from app.schemas.session import ChatSessionCreate
from typing import List

def create_session(db: Session, session_data: ChatSessionCreate) -> ChatSession:
    # Check user exists
    user = db.get(User, session_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {session_data.user_id} not found"
        )

    new_session = ChatSession(
        user_id=session_data.user_id,
        title=session_data.title
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


def get_session_by_id(db: Session, session_id: int) -> ChatSession | None:
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found"
        )
    return session


def list_sessions_for_user(db: Session, user_id: int) -> List[ChatSession]:
    stmt = select(ChatSession).where(ChatSession.user_id == user_id)
    return db.execute(stmt).scalars().all()