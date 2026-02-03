# FastAPI User Management API

This is a minimal FastAPI project boilerplate for managing users with authentication (JWT) and basic CRUD operations, using SQLite as the database.

## Features

-   **User Authentication**: Register, Login, JWT token generation and validation.
-   **User Profiles**: Create, Retrieve, Update, Delete user data.
-   **Database**: SQLite with SQLAlchemy ORM.
-   **Dependency Injection**: FastAPI's `Depends` for database sessions and current user.
-   **Password Hashing**: Secure password storage using `passlib`.
-   **Configuration**: Environment variables support via `pydantic-settings`.

## Project Structure

```
.gitignore
README.md
main.py
requirements.txt
start.sh
start.ps1
app/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── auth.py
│   └── users.py
├── config.py
├── core/
│   ├── __init__.py
│   ├── dependencies.py
│   └── security.py
├── crud/
│   ├── __init__.py
│   └── user.py
├── database.py
├── models/
│   ├── __init__.py
│   └── user.py
└── schemas/
    ├── __init__.py
    └── user.py
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create and Activate a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

**On Linux/macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**

```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables (Optional)

Create a `.env` file in the project root for sensitive configurations. Example:

```env
SECRET_KEY="your-super-secret-jwt-key"
DATABASE_URL="sqlite:///./sql_app.db"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

If `SECRET_KEY` is not set, a default will be used (not recommended for production).

### 5. Run the Application

Use the provided startup scripts for convenience.

**On Linux/macOS:**

```bash
bash start.sh
```

**On Windows (PowerShell):**

```powershell
.\start.ps1
```

The application will run on `http://127.0.0.1:8000`.

Access the API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.
Access the alternative API documentation (ReDoc) at `http://127.0.0.1:8000/redoc`.

## API Endpoints

### Authentication

-   `POST /auth/register`: Register a new user.
-   `POST /auth/token`: Login and get an access token.

### Users (Requires Authentication)

-   `GET /users/me`: Get the current authenticated user's profile.
-   `GET /users/`: Get a list of all users (requires authentication).
-   `GET /users/{user_id}`: Get a specific user by ID (requires authentication).
-   `PUT /users/{user_id}`: Update a user's profile (requires authentication).
-   `DELETE /users/{user_id}`: Delete a user (requires authentication).

## Development

-   **Database Migrations**: For more complex database schema changes in production, consider using a tool like Alembic with SQLAlchemy.
-   **Testing**: Add unit and integration tests for your API endpoints and services.
-   **Error Handling**: Implement more granular error handling and custom exceptions.
-   **Logging**: Set up proper logging for your application.
