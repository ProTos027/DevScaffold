from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import User, UserUpdate
from app.database import get_db
from app.api.deps import get_current_active_user
from app.crud import user as crud_user

router = APIRouter()

@router.get("/me", response_model=User)
def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user

@router.put("/me", response_model=User)
def update_users_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    updated_user = crud_user.update_user(db, current_user, user_in)
    return updated_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    crud_user.delete_user(db, current_user)
    return
