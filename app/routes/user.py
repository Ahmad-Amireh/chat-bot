from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserResponse, UserCreate
from app.services.user_service import list_users, get_user_by_id, create_user
from typing import Annotated
from app.services.user_service import create_user as create_user_service

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserResponse])
def get_all_users(db: Annotated[Session,Depends(get_db)]):
    return list_users(db)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session,Depends(get_db)]):
    return get_user_by_id(user_id= user_id, db= db)

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return create_user_service(db, user_data)