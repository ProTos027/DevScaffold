from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Optional

# --- Placeholder Models (to be replaced by actual models from 'app/models' in a real project) ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel:
    access_token: str
    token_type: str

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(TodoBase):
    pass

class TodoInDB(TodoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True # Use orm_mode=True for older Pydantic versions


# --- Placeholder Security and Data (to be replaced by actual database and authentication logic) ---

# Simulate a simple user database
fake_users_db = {
    "user1": {"username": "user1", "hashed_password": "hashed_password1"},
    "user2": {"username": "user2", "hashed_password": "hashed_password2"}
}

# Simulate a simple todo database
fake_todos_db: Dict[int, TodoInDB] = {}
next_todo_id = 1

# Simulate current active user for dependency injection
def get_current_user():
    # In a real application, this would decode a JWT token, verify it, and fetch the user from a DB.
    # For this placeholder, we just return a dummy user ID.
    # Raise HTTPException for unauthenticated access
    # raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {"username": "user1", "id": 1} # Placeholder for a logged-in user

# --- Routers ---
auth_router = APIRouter(prefix="/auth", tags=["auth"])
todo_router = APIRouter(prefix="/todos", tags=["todos"])

@auth_router.post("/register", response_model=Token)
async def register_user(user: UserCreate):
    if user.username in fake_users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    # In a real app, hash the password and save to DB
    fake_users_db[user.username] = {"username": user.username, "hashed_password": user.password + "_hashed"}
    # Simulate token creation
    return {"access_token": "fake_jwt_token_for_" + user.username, "token_type": "bearer"}

@auth_router.post("/login", response_model=Token)
async def login_for_access_token(user: UserLogin):
    stored_user = fake_users_db.get(user.username)
    if not stored_user or stored_user["hashed_password"] != user.password + "_hashed":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Simulate token creation
    return {"access_token": "fake_jwt_token_for_" + user.username, "token_type": "bearer"}

@todo_router.post("/", response_model=TodoInDB, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, current_user: Dict = Depends(get_current_user)):
    global next_todo_id
    new_todo = TodoInDB(id=next_todo_id, owner_id=current_user["id"], **todo.model_dump())
    fake_todos_db[next_todo_id] = new_todo
    next_todo_id += 1
    return new_todo

@todo_router.get("/", response_model=List[TodoInDB])
async def read_todos(current_user: Dict = Depends(get_current_user)):
    user_todos = [todo for todo in fake_todos_db.values() if todo.owner_id == current_user["id"]]
    return user_todos

@todo_router.get("/{todo_id}", response_model=TodoInDB)
async def read_todo(todo_id: int, current_user: Dict = Depends(get_current_user)):
    todo = fake_todos_db.get(todo_id)
    if not todo or todo.owner_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return todo

@todo_router.put("/{todo_id}", response_model=TodoInDB)
async def update_todo(todo_id: int, todo_update: TodoUpdate, current_user: Dict = Depends(get_current_user)):
    todo = fake_todos_db.get(todo_id)
    if not todo or todo.owner_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    
    update_data = todo_update.model_dump(exclude_unset=True)
    updated_todo_data = todo.model_dump()
    updated_todo_data.update(update_data)
    
    updated_todo = TodoInDB(**updated_todo_data)
    fake_todos_db[todo_id] = updated_todo
    return updated_todo

@todo_router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, current_user: Dict = Depends(get_current_user)):
    todo = fake_todos_db.get(todo_id)
    if not todo or todo.owner_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    del fake_todos_db[todo_id]
    return # No content for 204


# --- Main FastAPI Application Instance ---
app = FastAPI(
    title="Todo API",
    description="A simple FastAPI application to manage todos.",
    version="1.0.0",
)

# --- Register Routers ---
app.include_router(auth_router)
app.include_router(todo_router)

# --- Global Event Handlers (Example) ---
@app.on_event("startup")
async def startup_event():
    print("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown complete.")

# --- Root Endpoint (Optional) ---
@app.get("/", tags=["root"])
async def read_root():
    return {"message": "Welcome to the Todo API! Check /docs for API documentation."}
