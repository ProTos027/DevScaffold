from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import auth as auth_schemas
from app.crud import users as crud_users
from app.core import security
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=auth_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_users.create_user(db=db, user=user)

@router.post("/token", response_model=auth_schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=auth_schemas.UserResponse)
async def read_users_me(
    current_user_email: str = Depends(security.get_current_user_email),
    db: Session = Depends(get_db)
):
    user = crud_users.get_user_by_email(db, email=current_user_email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user