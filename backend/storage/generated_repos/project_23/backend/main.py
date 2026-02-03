from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.database import Base, engine
from app.api.v1.api import api_router
from app.config import settings

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI boilerplate for user authentication and profile management.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

app.include_router(api_router, prefix="/api/v1")

# Basic error handling (can be expanded)
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # In a real application, you'd return a proper JSON error response
    # For minimal complexity, we'll just redirect to docs or return a simple message
    return RedirectResponse(url="/docs")
