from typing import Generatornfrom fastapi import Depends, HTTPException, statusnfrom fastapi.security import OAuth2PasswordBearernfrom jose import jwt, JWTErrornfrom sqlalchemy.ext.asyncio import AsyncSessionnfrom app.database import get_db
from app.crud.user import get_user_by_id
from app.models.user import User
from app.core.security import ALGORITHM
from app.config import settings
from app.schemas.token import TokenDatannoauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")nnasync def get_current_user(n    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:n    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )n    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    user = await get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user