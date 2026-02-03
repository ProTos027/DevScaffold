# FastAPI User Management API

A minimal FastAPI project boilerplate for user authentication and profile management with SQLite.

## Features

*   User Registration
*   User Login (JWT Authentication)
*   User Profile Management (CRUD for authenticated user)
*   SQLite Database
*   Pydantic for data validation and serialization
*   SQLAlchemy for ORM

## Setup Instructions

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Run the application

You can use the provided startup scripts for convenience.

#### On Linux/macOS:

```bash
./start.sh
```

#### On Windows (PowerShell):

```powershell
.\start.ps1
```

These scripts will:
1.  Create a Python virtual environment (`.venv`).
2.  Activate the virtual environment.
3.  Install all required dependencies from `requirements.txt`.
4.  Start the FastAPI application using `uvicorn` with auto-reload.

The application will be accessible at `http://127.0.0.1:8000`.

### Manual Setup (Alternative)

If you prefer to set up manually:

1.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate    # On Windows CMD
    # .venv\Scripts\Activate.ps1 # On Windows PowerShell
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

## API Endpoints

The API documentation (Swagger UI) will be available at `http://127.0.0.1:8000/docs`.

### Authentication

*   `POST /api/v1/auth/register`: Register a new user.
*   `POST /api/v1/auth/login`: Authenticate user and get JWT token.

### User Profile

*   `GET /api/v1/users/me`: Get current authenticated user's profile. (Requires JWT)
*   `PUT /api/v1/users/me`: Update current authenticated user's profile. (Requires JWT)
*   `DELETE /api/v1/users/me`: Delete current authenticated user's account. (Requires JWT)

## Project Structure

```
.
├── .gitignore
├── README.md
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── start.sh                # Startup script for Linux/macOS
├── start.ps1               # Startup script for Windows
└── app/
    ├── config.py           # Application settings
    ├── database.py         # SQLAlchemy database setup
    ├── core/               # Core utilities (e.g., security)
    │   └── security.py     # Password hashing, JWT encoding/decoding
    ├── models/             # SQLAlchemy ORM models
    │   └── user.py         # User model
    ├── schemas/            # Pydantic schemas for request/response validation
    │   └── user.py         # User schemas
    ├── crud/               # CRUD operations
    │   └── user.py         # User CRUD functions
    ├── services/           # Business logic services
    │   └── auth.py         # Authentication service
    └── api/
        ├── deps.py         # FastAPI dependency injection functions
        └── v1/             # Version 1 of the API
            ├── api.py      # Main router for v1 endpoints
            └── endpoints/
                ├── auth.py # Authentication endpoints
                └── users.py # User profile endpoints
```
