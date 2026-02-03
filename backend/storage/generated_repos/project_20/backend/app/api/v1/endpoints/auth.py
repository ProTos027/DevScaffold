from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.api.v1.schemas import token as schemas_token
from app.api.v1.schemas import user as schemas_user
from app.core.config import settings
from app.core.exceptions import CREDENTIALS_EXCEPTION, USER_ALREADY_EXISTS_EXCEPTION
from app.services import auth_service, user_service

router = APIRouter()


@router.post("/login", response_model=schemas_token.Token)
async def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = auth_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise CREDENTIALS_EXCEPTION
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": auth_service.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=schemas_user.User)
async def register_user(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas_user.UserCreate
) -> Any:
    """Register a new user"""
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise USER_ALREADY_EXISTS_EXCEPTION
    
    user = auth_service.register_user(db, user_in=user_in)
    return user


@router.post("/test-token", response_model=schemas_user.User)
async def test_token(
    current_user: schemas_user.User = Depends(deps.get_current_user)
) -> Any:
    """Test access token"""
    return current_user
