# Chess Variant Engine (FastAPI)

This is a FastAPI-based backend for a chess variant engine. It provides APIs for user authentication, creating and managing game instances, and handling custom piece movements for various chess variants.

## Features

- User Authentication (Registration, Login, JWT Tokens)
- Custom Piece Movement Rules
- Game Management (Create, Join, Make Moves, Game State)
- SQLite Database Integration

## Project Structure

```
.github/                  # GitHub Actions (e.g., CI/CD)
├── workflows/
│   └── main.yml
app/
├── __init__.py
├── auth/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy User model
│   ├── router.py         # Auth API endpoints
│   ├── schemas.py        # Pydantic models for auth
│   └── security.py       # Password hashing, JWT logic
├── core/
│   ├── __init__.py
│   ├── config.py         # Application settings
│   ├── database.py       # SQLAlchemy engine and session setup
│   ├── dependencies.py   # Common FastAPI dependencies (DB, current user)
│   └── exceptions.py     # Custom HTTP exceptions
├── games/
│   ├── __init__.py
│   ├── models.py         # SQLAlchemy Game, Board, Piece models
│   ├── router.py         # Game API endpoints
│   ├── schemas.py        # Pydantic models for games
│   └── services.py       # Game logic (piece movement, board, game management)
├── main.py               # Main FastAPI application entry point
.env                      # Environment variables
.gitignore                # Git ignore file
requirements.txt          # Python dependencies
start.ps1                 # Windows startup script
start.sh                  # Linux/macOS startup script
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/chess-variant-engine.git
cd chess-variant-engine
```

### 2. Set up environment variables

Create a `.env` file in the project root based on `.env.example` (if provided, otherwise create as below):

```ini
DATABASE_URL="sqlite:///./sql_app.db"
SECRET_KEY="your_super_secret_jwt_key_here"
ALGORITHM="HS256"
```

**Note**: Replace `your_super_secret_jwt_key_here` with a strong, random secret key.

### 3. Run the application

#### On Linux/macOS

```bash
./start.sh
```

#### On Windows (PowerShell)

```powershell
.\start.ps1
```

These scripts will:
1. Create a Python virtual environment if it doesn't exist.
2. Activate the virtual environment.
3. Install all required Python packages.
4. Start the FastAPI application using Uvicorn with auto-reload.

## API Documentation

Once the server is running, you can access the interactive API documentation (Swagger UI) at:

`http://localhost:8000/docs`

Or the ReDoc documentation at:

`http://localhost:8000/redoc`

## Database

The project uses SQLite as the database, with SQLAlchemy as the ORM. The database file `sql_app.db` will be created in the project root when the application starts for the first time.

## Extending Custom Piece Movement

The `app/games/services.py` file contains the `PieceMovementService`. To add new chess variants or custom piece movements, you will extend the logic within this service to define specific rules based on piece types and game states.

## Contributing

Feel free to fork the repository, make changes, and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details (not included in this boilerplate).
