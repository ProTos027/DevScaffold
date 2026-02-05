from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create the SQLAlchemy engine
# For SQLite, 'check_same_thread' must be False to allow multiple threads to interact with the database connection
# This is needed for FastAPI's default behavior where each request might be handled in a different thread.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
# This class will be an actual database session per request
# 'autocommit=False' means transactions are not committed automatically
# 'autoflush=False' prevents immediate flushing of changes to the database
# 'bind=engine' connects the session to our database engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a DeclarativeBase instance
# All SQLAlchemy models will inherit from this Base class
Base = declarative_base()

# Dependency to get a database session
# This function will be used by FastAPI endpoints to obtain a database session
# It ensures that the session is closed after the request is finished, even if errors occur
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()