from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import Token, User, UserCreate, UserInDB
from app.crud import user as crud_user
from app.core import security, dependencies
from app.core.exceptions import CredentialException
from app.config import settings

router = APIRouter()

# Helper function for authentication
def authenticate_user(db: Session, username: str, password: str):
    user = crud_user.get_user_by_username(db, username=username)
    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return crud_user.create_user(db=db, user=user_in)

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CredentialException()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
def read_users_me(current_user: Annotated[User, Depends(dependencies.get_current_active_user)]):
    return current_user