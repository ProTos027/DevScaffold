from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.database import create_db_and_tables, close_db_connection
from app.core.exceptions import ChessEngineException
from app.games.router import router as games_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Creating database tables...")
    create_db_and_tables()
    yield
    # Shutdown logic
    print("Closing database connection...")
    close_db_connection()


app = FastAPI(
    title="Chess Variant Engine API",
    description="API for managing chess variants, games, and piece movements.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(games_router, prefix="/games", tags=["Games"])


# Global exception handler for custom exceptions
@app.exception_handler(ChessEngineException)
async def chess_engine_exception_handler(request: Request, exc: ChessEngineException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the Chess Variant Engine API!"}
