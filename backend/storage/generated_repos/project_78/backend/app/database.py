from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Configure SQLite database URL
# For SQLite, the database file will be created in the same directory as the application.
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Create the SQLAlchemy engine
# connect_args is needed for SQLite when using multiple threads (which FastAPI does).
# It ensures that each request gets its own connection.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Configure a SessionLocal class
# This class will be an actual database session per request.
# autoflush=False means that objects won't be flushed to the database until .commit() is called.
# autocommit=False means transactions are not committed automatically.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our ORM models
# All ORM models will inherit from this Base.
Base = declarative_base()

# Dependency callable for database session management
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables defined in Base's metadata
def create_all_tables():
    Base.metadata.create_all(bind=engine)
