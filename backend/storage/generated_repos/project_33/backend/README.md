# FastAPI REST API Project

This is a boilerplate for a FastAPI REST API project with PostgreSQL, JWT authentication, and a user management system.

## Setup

1.  **Clone the repository:**
    `git clone <repository-url>`
    `cd <project-folder>`

2.  **Create and activate a virtual environment:**
    *(Linux/macOS)*
    `python3 -m venv .venv`
    `source .venv/bin/activate`
    *(Windows)*
    `python -m venv .venv`
    `.venv\Scripts\activate`

3.  **Install dependencies:**
    `pip install -r requirements.txt`

4.  **Environment Variables:**
    Create a `.env` file in the root directory based on `.env.example` (if provided) and fill in the required values.
    Example `.env`:
    ```
    DATABASE_URL="postgresql://user:password@host:port/database"
    SECRET_KEY="your-super-secret-jwt-key"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Run Migrations (if using Alembic/similar):**
    *(Not included in this boilerplate, but good to mention for future expansion)*

## Running the Application

*   **Using `start.sh` (Linux/macOS):**
    `chmod +x start.sh`
    `./start.sh`

*   **Using `start.ps1` (Windows PowerShell):**
    `./start.ps1`

*   **Manually:**
    `uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## API Documentation

Once the application is running, you can access the interactive API documentation (Swagger UI) at:
`http://127.0.0.1:8000/docs`

And ReDoc at:
`http://127.0.0.1:8000/redoc`

## Project Structure

```
.
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── start.ps1
├── start.sh
├── main.py
└── app/
    ├── api/
    │   └── v1/
    │       ├── endpoints/
    │       │   └── users.py
    │       └── router.py
    ├── core/
    │   ├── config.py
    │   ├── exceptions.py
    │   └── security.py
    ├── database.py
    ├── dependencies/
    │   └── auth.py
    ├── models/
    │   └── user.py
    ├── schemas/
    │   ├── token.py
    │   └── user.py
    ├── services/
    │   ├── auth_service.py
    │   └── user_service.py
```

## Dependencies

See `requirements.txt` for a list of dependencies.
