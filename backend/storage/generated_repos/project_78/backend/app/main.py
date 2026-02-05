from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers.auth import router as auth_router
from app.routers.todos import router as todo_router

app = FastAPI(
    title="Todo App API",
    description="API for managing user authentication and todo items."
)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(todo_router, prefix="/todos", tags=["Todos"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Todo App API! Visit /docs for API documentation."}