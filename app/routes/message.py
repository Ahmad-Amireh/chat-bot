from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.schemas.message import MessageCreate, MessageResponse
from app.services.message import create_message as create_message_service, list_messages_for_session, get_message_by_id
from app.core.database import get_db

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message_data: MessageCreate, db: Annotated[Session, Depends(get_db)]):
    return create_message_service(db, message_data)


@router.get("/session/{session_id}", response_model=List[MessageResponse])
def list_session_messages(session_id: int, db: Annotated[Session, Depends(get_db)]):
    return list_messages_for_session(db, session_id)


@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_message_by_id(db, message_id)