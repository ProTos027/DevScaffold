from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings


# SQLite database URL
DATABASE_URL = settings.DATABASE_URL

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if DATABASE_URL.startswith("sqlite") else {},
)

# Create a SessionLocal class
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# Base class for declarative models
class Base(DeclarativeBase):
    pass


def create_db_and_tables():
    """Creates all database tables based on Base metadata."""
    Base.metadata.create_all(engine)


def close_db_connection():
    """Closes the database connection (for SQLite to ensure file handles are released)."""
    # For SQLite, disposing the engine can help release file locks.
    # For other databases, connection pooling usually manages this.
    if DATABASE_URL.startswith("sqlite"):
        engine.dispose()


# Dependency to get a database session
def get_db():
    """Provides a database session for a single request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
