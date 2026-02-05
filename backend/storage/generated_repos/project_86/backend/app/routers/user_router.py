from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Configuration (in a real app, this would be loaded from environment variables or a config file) ---
SECRET_KEY = "super-secret-key" # Replace with a strong, securely stored key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Password Hashing Context ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- In-memory "database" for demonstration purposes ---
# In a real application, this would interact with a persistent database (e.g., PostgreSQL, MongoDB).
fake_users_db: Dict[str, Dict[str, Any]] = {} # Stores {email: {id, email, hashed_password}}
next_user_id = 1 # Simple auto-incrementing ID

# --- Utility Functions for Auth (would typically be in a dedicated auth_service or utils module) ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes a JWT access token and returns its payload, or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# --- Pydantic Models for Request and Response Bodies ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: EmailStr

# --- Dependencies ---
# This dependency extracts and validates the token from the Authorization header
# and retrieves the current user from our fake DB.
async def get_current_user(token: str = Depends(lambda request: request.headers.get("Authorization", "").replace("Bearer ", ""))):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_email = payload.get("sub")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials: Missing user email in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real app, fetch user from a database based on user_email
    user_data = fake_users_db.get(user_email)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(id=user_data["id"], email=user_data["email"])

# --- APIRouter Instance ---
router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- REST API Endpoints ---

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """Registers a new user with email and password."""
    global next_user_id
    if user_data.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user_id = str(next_user_id)
    next_user_id += 1
    
    fake_users_db[user_data.email] = {
        "id": new_user_id,
        "email": user_data.email,
        "hashed_password": hashed_password
    }
    
    return UserResponse(id=new_user_id, email=user_data.email)

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: UserLoginRequest):
    """Authenticates a user and returns an access token."""
    user = fake_users_db.get(form_data.email)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """Retrieves the profile of the currently authenticated user."""
    return current_user
