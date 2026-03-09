from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import List

from app.models.message import Message
from app.models.chat_session import ChatSession
from app.schemas.message import MessageCreate
from app.models.user import User

def create_message(db: Session, user: User, message_data: MessageCreate) -> Message:
    # Check if session exists
    session = db.get(ChatSession, message_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat session with id {message_data.session_id} not found"
        )
    
    # Authorization check
    if session.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )

    new_message = Message(
        session_id=message_data.session_id,
        role="user",
        content=message_data.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def list_messages_for_session(db: Session, user: User, session_id: int) -> List[Message]:
    session = db.get(ChatSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if int(session.user_id) != int(user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    stmt = select(Message).where(Message.session_id == session_id)
    return db.execute(stmt).scalars().all()


def get_message_by_id(db: Session, user:User, message_id: int) -> Message:
    message = db.get(Message, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with id {message_id} not found"
        )
    if message.session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return message