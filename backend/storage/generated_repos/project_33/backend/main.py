from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import APIException, http_exception_handler
from app.database import engine, Base, get_db
from app.services import auth_service
from app.schemas.token import Token

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

@app.on_event("startup")
async def startup_event():
    # Create database tables if they don't exist
    # In a real project, use Alembic for migrations
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

@app.exception_handler(APIException)
async def custom_api_exception_handler(request, exc: APIException):
    return await http_exception_handler(request, exc)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.post(f"{settings.API_V1_STR}/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400, detail="Incorrect username or password"
        )
    access_token = auth_service.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}
