# FastAPI Framework Reference

## Project Structure
- `main.py` — App creation, router includes
- `app/routers/` — Route modules with `APIRouter`
- `app/models/` — SQLAlchemy/Pydantic models
- `app/schemas/` — Pydantic request/response schemas
- `app/dependencies.py` — Dependency injection

## Version Compatibility
- FastAPI 0.100+: Pydantic v2 native (use `model_dump()` not `dict()`)
- FastAPI 0.109+: Requires Python 3.8+
- FastAPI < 0.100: Pydantic v1 (use `dict()`, `schema()`)

## Pydantic v2 (FastAPI 0.100+)
- `BaseModel` with `model_dump()`, `model_validate()`
- `Field()` for validation, `ConfigDict` replaces `class Config`
- `from_attributes=True` replaces `orm_mode = True`
- Validators: `@field_validator` replaces `@validator`

## Pydantic v1 (FastAPI < 0.100)
- `BaseModel` with `dict()`, `parse_obj()`
- `class Config: orm_mode = True`
- Validators: `@validator`

## Routing
- `@app.get("/")`, `@app.post("/")` for main app
- `APIRouter()` for modular routing
- `app.include_router(router, prefix="/api")`
- Path params: `@app.get("/items/{item_id}")`
- Query params: automatic from function args

## Database
- SQLAlchemy: `create_engine()`, `SessionLocal`, `Base.metadata`
- Dependency: `def get_db(): yield db`
- Alembic for migrations

## Authentication
- OAuth2 with `OAuth2PasswordBearer`
- JWT: `python-jose` for encoding/decoding
- Dependency injection for current user

## Startup
- `uvicorn main:app --reload` for development
- `uvicorn main:app --host 0.0.0.0 --port 8000` for production
