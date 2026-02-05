from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import schemas, security
from app.auth.models import User
from app.core.config import settings
from app.core.dependencies import GetDB
from app.core.exceptions import ChessEngineException, ConflictException, UnauthorizedException

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: schemas.UserCreate, db: GetDB):
    db_user = db.query(User).filter(User.username == user_create.username).first()
    if db_user:
        raise ConflictException(f"Username '{user_create.username}' already registered")

    hashed_password = security.get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: GetDB):
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException("Incorrect username or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

