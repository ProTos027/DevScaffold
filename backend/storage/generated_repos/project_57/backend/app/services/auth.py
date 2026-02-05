from sqlalchemy.orm import Session

from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate, User
from app.core.security import verify_password
from app.core.exceptions import UserAlreadyExistsException, CredentialException

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def register_new_user(db: Session, user_data: UserCreate) -> User:
    db_user = get_user_by_username(db, username=user_data.username)
    if db_user:
        raise UserAlreadyExistsException()
    
    return create_user(db=db, user=user_data)