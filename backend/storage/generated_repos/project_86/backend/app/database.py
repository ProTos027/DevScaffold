from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSessionnfrom sqlalchemy.orm import DeclarativeBase, sessionmakernfrom app.config import settingsnn# Create async engine for SQLite (or other async DB drivers)nengine = create_async_engine(settings.DATABASE_URL, echo=True)nn# Create a sessionmaker for async sessionsnAsyncSessionLocal = async_sessionmaker(n    autocommit=False,n    autoflush=False,n    bind=engine,n    class_=AsyncSession,n    expire_on_commit=False # Important for keeping objects in session after commit
)

class Base(DeclarativeBase):n    passnnasync def get_db():n    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()