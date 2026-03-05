# FastAPI Framework Reference

## Directory Layout (REQUIRED — Do not deviate)
```
project_root/
├── main.py                   ← App creation, CORS, startup events, include all routers
├── app/
│   ├── routers/              ← ONE file per resource (e.g. users.py, items.py)
│   │   └── {resource}.py     ← APIRouter() instance, injected via Depends()
│   ├── services/             ← Business logic classes (one class per domain)
│   │   └── {domain}_service.py
│   ├── models/               ← SQLAlchemy ORM models ONLY (no Pydantic here)
│   │   └── {entity}.py
│   ├── schemas/              ← Pydantic request/response schemas ONLY
│   │   └── {entity}.py
│   ├── dependencies.py       ← get_db(), get_current_user() and other Depends functions
│   ├── database.py           ← engine, SessionLocal, Base
│   └── __init__.py
├── requirements.txt
└── .env
```

### Interface Contract Rules
- Routers MUST inject service classes via `Depends()`, not instantiate them directly.
- Service class method signatures: `def method(self, db: Session, ...) -> Schema`.
- Schemas define the public API surface — routers accept/return schemas, NOT models.
- Every router file MUST `import` the matching service from `app/services/`.

## Project Structure
- `main.py` — App creation, router includes, **CORS Configuration**
- `app/routers/` — Route modules with `APIRouter`
- `app/models/` — SQLAlchemy ORM models ONLY
- `app/schemas/` — Pydantic request/response schemas ONLY
- `app/dependencies.py` — get_db, auth dependencies

## Version Compatibility
- FastAPI 0.100+: Pydantic v2 native (use `model_dump()` not `dict()`)
- FastAPI 0.109+: Requires Python 3.8+
- FastAPI < 0.100: Pydantic v1 (use `dict()`, `schema()`)

## Pydantic v2 (FastAPI 0.100+)
- `BaseModel` with `model_dump()`, `model_validate()`
- `Field()` for validation, `ConfigDict` replaces `class Config`
- `from_attributes=True` replaces `orm_mode = True`
- Validators: `@field_validator` replaces `@validator`

## Pydantic v2 — MIGRATION CRITICAL RULES
- **NEVER use `.dict()`** → use `.model_dump()`
- **NEVER use `.from_orm(obj)`** → use `Model.model_validate(obj)`
- **NEVER use `class Config: orm_mode = True`** → use `model_config = ConfigDict(from_attributes=True)`
- **NEVER use `@validator`** → use `@field_validator`
- **NEVER use `datetime.utcnow()`** → use `datetime.now(timezone.utc)` (Python 3.12+ requirement)
- Use `pydantic-settings` (`BaseSettings`) for config, NOT `python-decouple` alone
- Correct schema pattern:
  ```python
  from pydantic import BaseModel, ConfigDict
  class UserRead(BaseModel):
      model_config = ConfigDict(from_attributes=True)
      id: int
      email: str
  # Usage: UserRead.model_validate(db_user)  ← NOT UserRead.from_orm(db_user)
  ```

## Routing — CRITICAL: Order Matters
- **Specific routes MUST come before parameterized routes** in the same router:
  ```python
  # CORRECT
  @router.get("/games/")          # list — register FIRST
  @router.get("/games/{game_id}") # detail — register SECOND

  # WRONG — FastAPI matches "games/" as game_id
  @router.get("/games/{game_id}")
  @router.get("/games/")
  ```
- `@app.get("/")`, `@app.post("/")` for main app
- `APIRouter()` for modular routing
- `app.include_router(router, prefix="/api/v1")`
- Path params: `@app.get("/items/{item_id}")`
- Always return `HTTPException(status_code=404)` — NEVER return `None` from a route

## main.py — CORS Configuration
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be loaded from env/settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## app/dependencies.py — Canonical Wiring
```python
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .database import get_db
from .models.user import User

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user
```

## Database — Singleton Pattern (CRITICAL)
- **ALWAYS create ONE global database/session instance** shared across all services:
  ```python
  # database.py — ONE global instance
  engine = create_engine(DATABASE_URL)
  SessionLocal = sessionmaker(bind=engine)
  Base = declarative_base()

  def get_db():
      db = SessionLocal()
      try:
          yield db
      finally:
          db.close()
  ```
- **Router/Service receives db via Depends(get_db) — NEVER create Session() directly**
- **In-memory DBs**: define ONE module-level instance and import it everywhere:
  ```python
  # database.py
  class InMemoryDB: ...
  db = InMemoryDB()  # ← single global

  # service.py
  from .database import db  # ← import shared, NEVER InMemoryDB()
  ```
- SQLAlchemy: `create_engine()`, `SessionLocal`, `Base.metadata`
- Alembic for migrations

## Authentication — JWT CRITICAL RULES
- JWT payload MUST contain `sub` (subject/email) AND `id` (integer PK):
  ```python
  def create_access_token(data: dict) -> str:
      # data = {"sub": user.email, "id": user.id}
      to_encode = data.copy()
      to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
      return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  ```
- OAuth2 with `OAuth2PasswordBearer`
- Password hashing: `passlib[bcrypt]` — NEVER store plaintext

## SQLAlchemy — Field Name Exactness
- ORM model field names (Column names) must exactly match what's set in constructors:
  ```python
  class Game(Base):
      game_status = Column(String)  # ← exact name
      board_state = Column(JSON)

  # CORRECT
  game = Game(game_status="active", board_state={})
  # WRONG
  game = Game(status="active")  # ← "status" doesn't exist
  ```
- Access via exact column names: `game.game_status`, NOT `game.status`

## Startup
- `uvicorn main:app --reload` for development
- `uvicorn main:app --host 0.0.0.0 --port 8000` for production
