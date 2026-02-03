from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Annotated

from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedException
from app.database import get_db
from app.models.user import User as DBUser # Avoid name collision with pydantic schema
from app.schemas.user import User as UserSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/token")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = UnauthorizedException()
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: Annotated[DBUser, Depends(get_current_user)]):
    # Add any additional checks for active status if applicable
    return current_user
