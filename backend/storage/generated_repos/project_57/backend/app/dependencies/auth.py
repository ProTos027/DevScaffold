from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.schemas.user import TokenData
from app.core.security import verify_token
from app.core.exceptions import CredentialException, UnauthorizedException
from app.database import get_db
from app.crud.user import get_user_by_username
from app.models.user import User

# OAuth2PasswordBearer specifies that the token will be provided in the header
# as Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    token_data = verify_token(token)
    
    user = get_user_by_username(db, username=token_data.get("sub"))
    if user is None:
        raise CredentialException(detail="Could not find user")
    
    if not user.is_active:
        raise UnauthorizedException(detail="Inactive user")
    
    return user