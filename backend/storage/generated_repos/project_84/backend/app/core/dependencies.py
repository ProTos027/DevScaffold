from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.security import verify_access_token
from app.core.database import get_db
from app.core.exceptions import UnauthorizedException


# Re-export get_db for convenience
GetDB = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: GetDB) -> User:
    """Dependency to get the current authenticated user."""
    credentials_exception = UnauthorizedException("Could not validate credentials")
    try:
        payload = verify_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


CurrentActiveUser = Annotated[User, Depends(get_current_user)]
