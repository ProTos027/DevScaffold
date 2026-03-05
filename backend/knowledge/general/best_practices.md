# General Best Practices

## Cross-Layer Connectivity (The Bridge)
Rules for where Frontend and Backend must align perfectly.

### 1. CORS Configuration (Canonical)
**FastAPI (main.py):**
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config("FRONTEND_URL")], # derived from frontend_port contract
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Express (app.js):**
```javascript
const cors = require('cors');
app.use(cors({
  origin: process.env.FRONTEND_URL, // derived from frontend_port contract
  credentials: true
}));
```

### 2. JWT Payload Contract
**ALWAYS** include both `sub` and `id` in the payload.
- `sub`: User identifier (usually email/username).
- `id`: Internal Database Primary Key (Integer).
- **Reason**: Routers need the `id` for fast DB lookups; `sub` alone is for identity.

### 3. Error Response Shapes (Neutral)
**NEVER** assume a specific error key. Always follow the framework convention:
- **FastAPI/Django**: `{"detail": "..."}`
- **Express**: `{"error": "..."}`

## Python/SQLAlchemy Time Management
**NEVER** use `datetime.utcnow()` (deprecated in Python 3.12).
- **Python**: `datetime.now(timezone.utc)`
- **SQLAlchemy**: `Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))`

## Environment Integrity
- **MANDATORY**: Always generate a `.env.example` file documenting every key.
- **NEVER** hardcode secrets in source code or `ProjectManifest`.
- **ALWAYS** use `python-decouple` (Python) or `dotenv` (Node) for config.

## .gitignore
Ensure these are always present to prevent credential leaks:
- `.env`
- `node_modules/` / `venv/`
- `__pycache__/`
- `*.sqlite3` / `*.db`

