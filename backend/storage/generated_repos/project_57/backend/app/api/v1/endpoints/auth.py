from datetime import timedelta

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.user import Token, UserCreate, User
from app.database import get_db
from app.core.security import create_access_token
from app.services.auth import authenticate_user, register_new_user
from app.config import settings
from app.core.exceptions import CredentialException

router = APIRouter()

@router.post("/token", response_model=Token, summary="User Login", description="Authenticate user and receive an access token.")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CredentialException()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED, summary="Register New User", description="Register a new user account.")
async def create_user_registration(user: UserCreate, db: Session = Depends(get_db)):
    new_user = register_new_user(db, user)
    return new_user

@router.get("/users/me", response_model=User, summary="Get Current User", description="Retrieve details of the currently authenticated user.")
async def read_users_me(current_user: User = Depends("app.dependencies.auth.get_current_user")):
    return current_user