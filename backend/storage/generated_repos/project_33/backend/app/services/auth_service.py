from datetime import timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.core import security
from app.models.user import User as DBUser
from app.schemas.user import UserCreate
from app.core.config import settings

def authenticate_user(db: Session, username: str, password: str) -> Optional[DBUser]:
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return security.create_access_token(data, expires_delta)

def register_new_user(db: Session, user_in: UserCreate) -> DBUser:
    hashed_password = security.get_password_hash(user_in.password)
    db_user = DBUser(username=user_in.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
