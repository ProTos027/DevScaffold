from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.db import models
from app.api.v1.schemas import user as schemas_user
from app.core import security
from app.core.config import settings


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[models.User]:
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    return security.create_access_token(
        data={"sub": str(user_id)},
        expires_delta=expires_delta
    )


def register_user(
    db: Session,
    user_in: schemas_user.UserCreate
) -> models.User:
    hashed_password = security.get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        hashed_password=hashed_password,
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
