# FastAPI Todo App

A simple Todo application built with FastAPI, using SQLite for the database, SQLAlchemy ORM, and JWT for authentication.

## Features

*   User Registration & Login
*   JWT-based Authentication
*   CRUD operations for Todo items
*   Secure password hashing
*   Database migrations (manual for now, could integrate Alembic)

## Setup

### Prerequisites

*   Python 3.9+

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd todo-app
    ```

2.  **Create and activate a virtual environment:**

    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

You can use the provided startup scripts:

*   **macOS/Linux:**
    ```bash
    ./scripts/start.sh
    ```
*   **Windows (PowerShell):**
    ```powershell
    .\scripts\start.ps1
    ```

Alternatively, you can run it manually:

1.  **Activate your virtual environment** (if not already active).
2.  **Run Uvicorn:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```

The API documentation will be available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## API Endpoints

### Authentication

*   `POST /api/v1/auth/register`: Register a new user.
*   `POST /api/v1/auth/token`: Login and get an access token.
*   `GET /api/v1/auth/me`: Get current user details (requires authentication).

### Todo Items

*   `POST /api/v1/todos/`: Create a new Todo item (requires authentication).
*   `GET /api/v1/todos/`: Get all Todo items for the current user (requires authentication).
*   `GET /api/v1/todos/{todo_id}`: Get a specific Todo item (requires authentication).
*   `PUT /api/v1/todos/{todo_id}`: Update a Todo item (requires authentication).
*   `DELETE /api/v1/todos/{todo_id}`: Delete a Todo item (requires authentication).

## Database

The application uses SQLite as its database. The database file will be created at the root of the project as `./sql_app.db`.