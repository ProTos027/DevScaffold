# FastAPI Todo Application

This is a simple Todo application built with FastAPI, using SQLite as its database, and includes basic user authentication.

## Features

*   User registration and authentication (JWT)
*   Create, Read, Update, Delete (CRUD) Todo items
*   Protected routes requiring authentication

## Project Structure

```
.gitignore
README.md
requirements.txt
scripts/
├── start.ps1
└── start.sh
app/
├── __init__.py
├── main.py             # Main FastAPI application entry point
├── config.py           # Application settings and environment variables
├── database.py         # SQLAlchemy database setup
├── core/
│   ├── __init__.py
│   ├── exceptions.py   # Custom HTTP exceptions
│   └── security.py     # Password hashing and JWT utilities
├── models/
│   ├── __init__.py
│   ├── user.py         # SQLAlchemy User model
│   └── todo.py         # SQLAlchemy Todo model
├── schemas/
│   ├── __init__.py
│   ├── user.py         # Pydantic models for User (request/response)
│   └── todo.py         # Pydantic models for Todo (request/response)
├── crud/
│   ├── __init__.py
│   ├── user.py         # CRUD operations for Users
│   └── todo.py         # CRUD operations for Todos
├── services/
│   ├── __init__.py
│   └── auth.py         # Authentication business logic
├── dependencies/
│   ├── __init__.py
│   └── auth.py         # FastAPI dependency for authentication
└── api/
    └── v1/
        ├── __init__.py
        └── endpoints/
            ├── __init__.py
            ├── auth.py   # API routes for authentication
            └── todos.py  # API routes for Todo items
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd fastapi-todo-app
    ```

2.  **Run the setup script:**
    *   **On Linux/macOS:**
        ```bash
        ./scripts/start.sh
        ```
    *   **On Windows (PowerShell):**
        ```powershell
        .\scripts\start.ps1
        ```
    These scripts will:
    *   Create a Python virtual environment (`.venv`).
    *   Activate the virtual environment.
    *   Install all required Python dependencies.
    *   Start the FastAPI application using Uvicorn.

3.  **Access the API Documentation:**
    Once the server is running, open your browser and navigate to:
    *   **Swagger UI:** `http://127.0.0.1:8000/docs`
    *   **ReDoc:** `http://127.0.0.1:8000/redoc`

## Environment Variables

Configure your environment variables in `.env` file (create one in the root directory if it doesn't exist) or directly in your environment. Refer to `app/config.py` for available settings.

*   `DATABASE_URL`: SQLAlchemy database URL (e.g., `sqlite:///./sql_app.db`)
*   `SECRET_KEY`: A strong, random string used for JWT encoding.
*   `ALGORITHM`: JWT algorithm (e.g., `HS256`)
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: Expiration time for access tokens in minutes.

## Usage

1.  **Register a User:**
    Send a POST request to `/api/v1/users/` with `username` and `password`.

2.  **Login and Get Token:**
    Send a POST request to `/api/v1/token` with `username` and `password` (form-data).
    You will receive an `access_token`.

3.  **Access Protected Routes:**
    Include the `access_token` in the `Authorization` header as a Bearer token for protected routes (e.g., Todo CRUD operations).
    Example: `Authorization: Bearer <your_access_token>`

## Development

To run the application manually after initial setup:

1.  **Activate virtual environment:**
    *   Linux/macOS: `source .venv/bin/activate`
    *   Windows: `.venv\Scripts\activate`

2.  **Run Uvicorn:**
    ```bash
    uvicorn app.main:app --reload
    ```

This will start the server with auto-reloading enabled for development.