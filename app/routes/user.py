from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserPublicResponse, UserCreate, UserPrivateResponse, Token
from app.services.user_service import list_users, get_user_by_id, create_user as create_user_service
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import create_user_access_token, authenticate_user, CurrentUser


router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserPublicResponse])
def get_all_users(db: Annotated[Session,Depends(get_db)]):
    return list_users(db)

@router.get("/me", response_model=UserPrivateResponse)
def get_me(
    db: Annotated[Session, Depends(get_db)],
    user: CurrentUser
):
    return user


@router.get("/{user_id}", response_model=UserPublicResponse)
def get_user(user_id: int, db: Annotated[Session,Depends(get_db)]):
    return get_user_by_id(user_id= user_id, db= db)

@router.post("", response_model=UserPublicResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Annotated[Session, Depends(get_db)]):
    return create_user_service(db, user_data)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """
    Authenticate user and return access token.
    """

    user = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password
    )

    access_token = create_user_access_token(user.id)

    return Token(
        access_token=access_token,
        token_type="bearer"
    )