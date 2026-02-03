# FastAPI User Authentication & Profile API

This is a minimal, production-ready FastAPI boilerplate for a web application with user authentication and profile management using SQLite.

## Features

- User Registration
- User Login (JWT based)
- User Profile Management (Get/Update)
- Password Hashing (Bcrypt)
- JWT Token Generation and Validation
- Database ORM with SQLAlchemy
- Pydantic for data validation and serialization
- Environment variable management

## Project Structure

```
.
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   └── users.py
│   │   │   └── schemas/
│   │   │       ├── msg.py
│   │   │       ├── token.py
│   │   │       └── user.py
│   ├── core/
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   └── security.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── user_service.py
│   └── main.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**
    Copy the `.env.example` file to `.env` and fill in your secret key. **Make sure to generate a strong, random secret key for production.**
    ```bash
    cp .env.example .env
    ```

    Example `.env` content:
    ```
    DATABASE_URL=sqlite:///./sql_app.db
    SECRET_KEY="your-super-secret-key-here-generate-a-long-random-one"
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

5.  **Run the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

    The API documentation will be available at `http://127.0.0.1:8000/docs` (Swagger UI) or `http://127.0.0.1:8000/redoc` (ReDoc).

## API Endpoints

-   **Authentication**
    -   `POST /api/v1/auth/register` - Register a new user.
    -   `POST /api/v1/auth/login` - Authenticate user and get JWT token.
    -   `POST /api/v1/auth/test-token` - Test current user token.

-   **User Profile**
    -   `GET /api/v1/users/me` - Get current authenticated user's profile.
    -   `PUT /api/v1/users/me` - Update current authenticated user's profile.

## Database

This project uses SQLite as the database. The database file `sql_app.db` will be created in the project root directory upon the first run if it doesn't exist. SQLAlchemy is used as the ORM.

## Contributing

Feel free to fork, modify, and use this boilerplate for your projects.
