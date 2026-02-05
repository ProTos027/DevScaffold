from fastapi import FastAPI

# Assuming these routers will be created in app/routers/
# from app.routers import auth as auth_router
# from app.routers import todos as todos_router

app = FastAPI(
    title="My FastAPI Application",
    description="A sample FastAPI application with authentication and todo management.",
    version="0.0.1"
)

@app.on_event("startup")
async def startup_event():
    # Placeholder for database connection or other startup tasks
    print("Application starting up...")
    # Example: db_connection = await connect_to_database()

@app.on_event("shutdown")
async def shutdown_event():
    # Placeholder for closing database connection or other shutdown tasks
    print("Application shutting down...")
    # Example: await db_connection.close()

# Include routers
# app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
# app.include_router(todos_router.router, prefix="/todos", tags=["Todos"])

@app.get("/", summary="Root endpoint", response_model=dict)
async def read_root():
    """A simple root endpoint to confirm the application is running."""
    return {"message": "Welcome to the FastAPI application!"}
