from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
from app.config import settingsnnpwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")nALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEYnACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTESnREFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTESnndef verify_password(plain_password: str, hashed_password: str) -> bool:n    return pwd_context.verify(plain_password, hashed_password)nndef get_password_hash(password: str) -> str:n    return pwd_context.hash(password)nndef create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:n    to_encode = data.copy()
    if expires_delta:n        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:n        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
