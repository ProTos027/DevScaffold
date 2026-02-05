from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User as DBUser
from app.schemas.user import TokenData
from app.crud import user as crud_user
from app.core import security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token") # Changed to match login endpoint

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> DBUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud_user.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: DBUser = Depends(get_current_user)) -> DBUser:
    # Add any checks for active user status if necessary
    return current_user