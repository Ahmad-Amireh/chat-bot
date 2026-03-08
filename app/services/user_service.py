from sqlalchemy.orm import Session
from app.models.user import User
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from typing import List

def create_user(db: Session, user_data: UserCreate) -> User:
    stmt = select(User).where(func.lower(User.name) == user_data.name.lower())
    user_exist = db.execute(stmt).scalar_one_or_none()
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    stmt = select(User).where(func.lower(User.email) == user_data.email.lower())
    email_exist = db.execute(stmt).scalar_one_or_none()
    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    new_user = User(name=user_data.name, email=user_data.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def list_users(db: Session) -> List[User]:
    stmt = select(User)
    return db.execute(stmt).scalars().all()