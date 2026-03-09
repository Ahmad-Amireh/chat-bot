from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from app import models
from app.core.auth import verify_password, create_access_token, verify_access_token
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.core.database import get_db
from typing import Annotated


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

def authenticate_user(db: Session, email: str, password: str):
    stmt = select(models.User).where(func.lower(models.User.email) == email.lower())
    user =  db.execute(stmt).scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Email or Password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def create_user_access_token(user_id: int):
    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRED_MINUTES)

    access_token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=access_token_expire,
    )

    return access_token


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:

    user_id = verify_access_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

CurrentUser = Annotated[models.User, Depends(get_current_user)]