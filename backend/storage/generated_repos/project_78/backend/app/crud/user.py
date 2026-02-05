from sqlalchemy.orm import Session

from app.models.user import User as DBUser
from app.schemas.user import UserCreate
from app.core import security

def get_user(db: Session, user_id: int):
    return db.query(DBUser).filter(DBUser.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = security.get_password_hash(user.password)
    db_user = DBUser(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user