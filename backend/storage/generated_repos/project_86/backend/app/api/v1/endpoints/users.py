from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from app.services.auth_service import auth_service
from app.dependencies import get_current_userno

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(db, user_in)
    return UserResponse.model_validate(user)

@router.post("/login", response_model=Token)
async def login_for_access_token(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    tokens = await auth_service.create_tokens(user)
    return tokens

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user