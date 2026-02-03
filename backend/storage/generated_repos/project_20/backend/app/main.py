from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import Base, engine, get_db
from app.api.v1.endpoints import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    # In a real production environment, you'd use Alembic for migrations
    # For this minimal boilerplate, we create tables directly.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])


@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the FastAPI boilerplate! Access /docs for API documentation."}
