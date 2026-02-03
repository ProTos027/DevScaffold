from fastapi import FastAPI
from app.database import init_db
from app.routers import users

app = FastAPI(
    title="FastAPI Boilerplate API",
    description="A minimal FastAPI project boilerplate with user authentication and SQLite.",
    version="0.1.0",
)

@app.on_event("startup")
async def startup_event():
    print("Initializing database...")
    init_db()
    print("Database initialized.")

# Include routers
app.include_router(users.router)

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the FastAPI Boilerplate API! Visit /docs for API documentation."}
