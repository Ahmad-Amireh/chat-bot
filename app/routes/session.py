from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated, List

from app.schemas.session import ChatSessionCreate, ChatSessionResponse
from app.services.session import create_session as create_session_service, get_session_by_id, list_sessions_for_user
from app.core.database import get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: ChatSessionCreate, db: Annotated[Session, Depends(get_db)]):
    return create_session_service(db, session_data)


@router.get("/{session_id}", response_model=ChatSessionResponse)
def get_session(session_id: int, db: Annotated[Session, Depends(get_db)]):
    return get_session_by_id(db, session_id)


@router.get("/user/{user_id}", response_model=List[ChatSessionResponse])
def list_user_sessions(user_id: int, db: Annotated[Session, Depends(get_db)]):
    return list_sessions_for_user(db, user_id)