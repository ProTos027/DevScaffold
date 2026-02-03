# FastAPI Boilerplate API Service

This project provides a minimal, production-ready boilerplate for a FastAPI API service using SQLite, SQLAlchemy, and JWT authentication.

## Features

-   **FastAPI**: Modern, fast (high-performance) web framework for building APIs.
-   **SQLAlchemy**: Powerful and flexible ORM for database interactions.
-   **SQLite**: Simple file-based database for development and small-scale deployments.
-   **Pydantic**: Data validation and settings management.
-   **JWT Authentication**: Secure user registration, login, and token validation.
-   **Structured Project Layout**: Clear separation of concerns (models, schemas, CRUD, auth, routers).
-   **Dependency Management**: `requirements.txt`.
-   **Startup Scripts**: `start.sh` (Linux/macOS) and `start.ps1` (Windows) for easy setup and execution.

## Project Structure

```
. 
├── app/
│   ├── __init__.py
│   ├── auth.py             # JWT authentication logic
│   ├── config.py           # Application settings and environment variables
│   ├── crud.py             # Database Create, Read, Update, Delete operations
│   ├── database.py         # SQLAlchemy engine, session, and base
│   ├── dependencies.py     # Common FastAPI dependencies (e.g., get_db)
│   ├── models.py           # SQLAlchemy ORM models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── users.py        # API routes for user management and authentication
│   └── schemas.py          # Pydantic data models for request/response validation
├── .gitignore              # Files/directories to ignore in Git
├── main.py                 # Main FastAPI application entry point
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── start.ps1               # PowerShell script to set up and run the app (Windows)
└── start.sh                # Bash script to set up and run the app (Linux/macOS)
```

## Setup and Run

### Prerequisites

-   Python 3.8+

### 1. Clone the repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Run the application

Choose the appropriate script for your operating system:

#### For Linux/macOS

```bash
chmod +x start.sh
./start.sh
```

#### For Windows (using PowerShell)

```powershell
.\start.ps1
```

These scripts will:
1.  Create a Python virtual environment (`.venv`).
2.  Activate the virtual environment.
3.  Install all required dependencies from `requirements.txt`.
4.  Start the FastAPI application using Uvicorn with auto-reload.

The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

-   **Interactive API Documentation (Swagger UI)**: `http://127.0.0.1:8000/docs`
-   **Alternative API Documentation (ReDoc)**: `http://127.0.0.1:8000/redoc`

### User Authentication

-   `POST /users/`: Register a new user.
    -   Request Body: `{"email": "user@example.com", "password": "securepassword"}`
-   `POST /token`: Authenticate user and get an access token.
    -   Form Data: `username=user@example.com&password=securepassword`
    -   Response: `{"access_token": "<jwt_token>", "token_type": "bearer"}`
-   `GET /users/me/`: Get current authenticated user's details.
    -   Requires `Authorization: Bearer <jwt_token>` header.

## Configuration

Environment variables can be set to configure the application. See `app/config.py` for details.

-   `SECRET_KEY`: Used for JWT token signing. **CRITICAL: Change this in production!**
-   `ALGORITHM`: JWT algorithm (default: `HS256`).
-   `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: `30`).
-   `DATABASE_URL`: SQLAlchemy database connection string (default: `sqlite:///./sql_app.db`).

## Database

The application uses SQLite by default, storing data in `sql_app.db` in the project root. This file is ignored by Git.

On application startup, if the database file doesn't exist, SQLAlchemy will create the necessary tables based on `app/models.py`.
