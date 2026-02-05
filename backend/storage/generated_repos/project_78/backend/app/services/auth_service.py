from datetime import datetime, timedelta, timezone
from typing import Dict, Union

import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.models.user import User
from app.schemas.user import UserCreate # Assuming this schema exists

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Union[str, int]], expires_delta: Union[timedelta, None] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: Exception) -> Dict[str, Union[str, int]]:
    """Verify a JWT token and extract its payload. Raises credentials_exception on failure."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # You can add more validation here if needed, e.g., token type
        return payload
    except jwt.PyJWTError:
        raise credentials_exception

def create_user(
    db: Session, user_create_schema: UserCreate
) -> User:
    """Create a new user record in the database."""
    hashed_password = get_password_hash(user_create_schema.password)
    db_user = User(
        username=user_create_schema.username,
        hashed_password=hashed_password,
        email=user_create_schema.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(
    db: Session, username: str, password: str
) -> Union[User, None]:
    """Authenticate a user by verifying credentials."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
