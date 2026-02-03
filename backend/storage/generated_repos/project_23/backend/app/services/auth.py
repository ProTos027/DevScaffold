from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import UserCreate, User
from app.crud import user as crud_user
from app.core.security import verify_password, create_access_token
from datetime import timedelta
from app.config import settings

def authenticate_user(db: Session, email: str, password: str):
    user = crud_user.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_account(db: Session, user_in: UserCreate):
    user = crud_user.get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud_user.create_user(db=db, user=user_in)

def create_user_access_token(user: User) -> str:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        subject=user.email, expires_delta=access_token_expires
    )
