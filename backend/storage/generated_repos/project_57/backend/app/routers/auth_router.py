from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.routers import auth_service
from app.routers.auth_service import User, UserCreate, TokenData, Token # Import models

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> User:
    """Register a new user."""
    db_user = auth_service.register_user(user_data)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    return db_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """Authenticate user and return an access token."""
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Dependency to get the current authenticated user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = auth_service.verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    # In a real app, you might fetch the full user from a DB here using token_data.username
    # For this mock, we'll just return a basic User object
    user_in_db = auth_service.fake_users_db.get(token_data.username)
    if user_in_db is None:
        raise credentials_exception
    
    return User(**user_in_db.dict(exclude={'hashed_password'}))

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Dependency to get the current active authenticated user."""
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
