from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.api.v1.schemas import user as schemas_user
from app.db import models
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=schemas_user.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Get current authenticated user"""
    return current_user


@router.put("/me", response_model=schemas_user.User)
async def update_user_me(
    *, 
    db: Session = Depends(deps.get_db),
    user_in: schemas_user.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user)
) -> Any:
    """Update current authenticated user"""
    user = user_service.update_user(db, db_obj=current_user, obj_in=user_in)
    return user
