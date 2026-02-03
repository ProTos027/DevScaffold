from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api import auth, users

app = FastAPI(
    title="FastAPI User Management API",
    description="A minimal FastAPI project for managing users with authentication and CRUD operations.",
    version="0.1.0",
)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    print("Database tables created (if not exist).")

app.include_router(auth.router)
app.include_router(users.router)

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the FastAPI User Management API!"}
