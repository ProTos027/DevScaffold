from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.schemas.user import User, UserCreate
from app.database import get_db
from app.dependencies.auth import get_current_active_user
from app.services import auth_service, user_service
from app.core.exceptions import APIException

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Annotated[Session, Depends(get_db)]):
    db_user = user_service.get_user_by_username(db, username=user_in.username)
    if db_user:
        raise APIException(status_code=400, detail="Username already registered")
    return auth_service.register_new_user(db=db, user_in=user_in)

@router.get("/me", response_model=User)
def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user
