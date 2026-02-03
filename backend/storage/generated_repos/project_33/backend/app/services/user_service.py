from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User as DBUser

def get_user_by_username(db: Session, username: str) -> Optional[DBUser]:
    return db.query(DBUser).filter(DBUser.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[DBUser]:
    return db.query(DBUser).filter(DBUser.id == user_id).first()
