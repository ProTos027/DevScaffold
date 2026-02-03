import sqlite3
from typing import List, Dict, Any, Generator, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# --- 1. Pydantic Models ---

class QueryRequest(BaseModel):
    """
    Request model for executing a database query.
    """
    sql: str = Field(..., example="SELECT * FROM users WHERE id = ?")
    params: Optional[List[Any]] = Field(None, example=[1, "active"])

class QueryResult(BaseModel):
    """
    Response model for the result of a database query.
    """
    columns: List[str] = Field(..., example=["id", "name", "email"])
    rows: List[Dict[str, Any]] = Field(..., example=[{"id": 1, "name": "Alice", "email": "alice@example.com"}])
    message: str = Field("Query executed successfully.", example="Query executed successfully.")

class StatusResponse(BaseModel):
    """
    Response model for the database connection status.
    """
    status: str = Field(..., example="ok")
    message: str = Field(..., example="Database connection is healthy.")

class ErrorResponse(BaseModel):
    """
    Generic error response model for HTTP exceptions.
    """
    detail: str = Field(..., example="An error occurred.")

# --- 2. Database Connector Class ---

# In a real application, DATABASE_URL would typically come from environment variables or a configuration file.
DATABASE_URL = "sqlite:///./test.db"

class DatabaseConnector:
    """
    Manages SQLite database connections and executes queries.

    Responsibilities:
    - manage_sqlite_connection (via the injected `sqlite3.Connection`)
    - execute_database_queries
    """
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initializes the DatabaseConnector with an active SQLite connection.
        """
        self.conn = db_connection
        # Set row_factory to sqlite3.Row to get dict-like rows
        self.conn.row_factory = sqlite3.Row

    def execute_query(self, sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """
        Executes a SQL query and returns results if applicable.
        Commits changes for DML operations (INSERT, UPDATE, DELETE).

        Args:
            sql: The SQL query string.
            params: Optional list of parameters for the query, used to prevent SQL injection.

        Returns:
            A dictionary containing 'columns', 'rows', and 'message'.
            'rows' will be a list of dictionaries, where each dictionary represents a row.

        Raises:
            HTTPException: If a database error occurs (e.g., syntax error, constraint violation)
                           or an unexpected internal error.
        """
        if params is None:
            params = []

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, tuple(params))
            self.conn.commit() # Commit changes for DML operations

            if cursor.description:
                # This is likely a SELECT query, fetch results
                columns = [col[0] for col in cursor.description]
                rows = [dict(row) for row in cursor.fetchall()]
                message = "Query executed successfully and results fetched."
            else:
                # This is likely a DML query (INSERT, UPDATE, DELETE)
                columns = []
                rows = []
                message = f"Query executed successfully. Rows affected: {cursor.rowcount}"
            
            return {"columns": columns, "rows": rows, "message": message}
        except sqlite3.Error as e:
            self.conn.rollback() # Rollback any changes on error
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database error: {e}"
            )
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred during query execution: {e}"
            )

# --- 3. Dependency Injection ---

def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency that provides a SQLite database connection.
    Ensures the connection is closed after the request has been processed.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_URL.split("///")[-1]) # Extract path from URL
        yield conn
    except sqlite3.Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not establish database connection: {e}"
        )
    finally:
        if conn:
            conn.close()

def get_database_connector(
    db_connection: sqlite3.Connection = Depends(get_db_connection)
) -> DatabaseConnector:
    """
    Dependency that provides a DatabaseConnector instance,
    injecting an active database connection.
    """
    return DatabaseConnector(db_connection)

# --- 4. APIRouter Setup ---

router = APIRouter(
    prefix="/database",
    tags=["Database Connector"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Internal Server Error"},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Bad Request"}
    }
)

# --- 5. Router Endpoints ---

@router.post(
    "/query",
    response_model=QueryResult,
    summary="Execute a SQL query",
    description="Executes an arbitrary SQL query against the SQLite database. "
                "Supports both SELECT and DML (INSERT, UPDATE, DELETE) operations. "
                "Parameters can be provided to prevent SQL injection. "
                "**Use with caution**: This endpoint allows execution of arbitrary SQL, "
                "which can be a security risk if not properly restricted in a production environment.",
    responses={
        status.HTTP_200_OK: {"model": QueryResult, "description": "Query executed successfully."},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Invalid SQL query or parameters."},
    }
)
async def execute_database_query(
    request: QueryRequest,
    connector: DatabaseConnector = Depends(get_database_connector)
) -> QueryResult:
    """
    Executes a SQL query provided in the request body.
    """
    result = connector.execute_query(request.sql, request.params)
    return QueryResult(**result)

@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Check database connection status",
    description="Checks if the database connection can be established and is healthy "
                "by performing a simple 'SELECT 1' query.",
    responses={
        status.HTTP_200_OK: {"model": StatusResponse, "description": "Database connection is healthy."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Failed to connect to the database or connection check failed."},
    }
)
async def get_database_status(
    connector: DatabaseConnector = Depends(get_database_connector)
) -> StatusResponse:
    """
    Checks the status of the database connection by executing a trivial query.
    """
    try:
        # A simple query to ensure the connection is truly functional
        connector.execute_query("SELECT 1")
        return StatusResponse(status="ok", message="Database connection is healthy.")
    except HTTPException as e:
        # Re-raise HTTPExceptions from execute_query if it fails
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection check failed: {e}"
        )

# --- Optional: Initial Database Setup for Testing ---
# This function is not part of the router but can be used to set up a test database
# when the application starts or for development purposes.
def _create_test_db_schema():
    """
    Creates a simple 'users' table in the test database if it doesn't exist.
    """
    db_path = DATABASE_URL.split("///")[-1]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    # Insert some dummy data if the table is empty
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com')")
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    conn.close()

# Uncomment the line below to create the test database when this module is imported
# _create_test_db_schema()