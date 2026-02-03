from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from pydantic import BaseModel
from typing import List, Dict, Any

# No specific models from app.models are needed as per prompt "Data Models Used: None"

router = APIRouter(prefix="/database", tags=["Database Management"])

# Pydantic models for request/response
class DatabaseHealthResponse(BaseModel):
    """
    Response model for database health check.
    """
    status: str
    message: str = None

class ExecuteQueryRequest(BaseModel):
    """
    Request model for executing a SQL query.
    """
    query: str

class ExecuteQueryResponse(BaseModel):
    """
    Response model for the results of a SQL query execution.
    """
    results: List[Dict[str, Any]]
    message: str = None

@router.get(
    "/health",
    response_model=DatabaseHealthResponse,
    summary="Check database connection health",
    description="""
    Tests the connection to the database by executing a simple query.
    Returns 'connected' if successful, otherwise 'disconnected' with an error message.
    This endpoint is useful for monitoring the database service's availability.
    """
)
def get_database_health(db: Session = Depends(get_db)):
    """
    Checks the health and connectivity of the database.

    Attempts to execute a trivial query to verify the database session is active.
    """
    try:
        # Attempt a simple query to check connection
        db.execute("SELECT 1")
        return DatabaseHealthResponse(status="connected", message="Database connection is active.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {e}"
        )

@router.post(
    "/query",
    response_model=ExecuteQueryResponse,
    summary="Execute a read-only SQL query",
    description="""
    Executes a provided SQL query against the database and returns the results.
    
    **WARNING**: This endpoint is designed primarily for read-only operations (SELECT statements).
    Executing DDL (CREATE, ALTER, DROP) or DML (INSERT, UPDATE, DELETE) statements
    through this endpoint is highly discouraged due to severe security risks and potential data corruption.
    For safety, only `SELECT` queries are explicitly allowed by default.
    Use with extreme caution and ensure proper authorization mechanisms are in place
    if this functionality is exposed to external users.
    """
)
def execute_database_query(request: ExecuteQueryRequest, db: Session = Depends(get_db)):
    """
    Executes a SQL query and returns the results as a list of dictionaries.

    Args:
        request (ExecuteQueryRequest): The request body containing the SQL query string.
        db (Session): The database session dependency.

    Returns:
        ExecuteQueryResponse: A response containing the query results and a success message.

    Raises:
        HTTPException:
            - 400 Bad Request if the query is not a 'SELECT' statement or if there's a SQL error.
            - 500 Internal Server Error for unexpected database issues.
    """
    query = request.query.strip()

    # Basic security check: only allow SELECT statements
    # This is a rudimentary check. For production, consider more robust solutions
    # like pre-defined query templates, role-based access control, or a dedicated
    # query builder that prevents malicious input.
    if not query.lower().startswith("select"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only 'SELECT' queries are allowed through this endpoint for security reasons."
        )

    try:
        # Execute the query
        result = db.execute(query)

        # Fetch all rows and convert to a list of dictionaries
        # This approach works well for SELECT queries returning tabular data.
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]

        return ExecuteQueryResponse(results=rows, message="Query executed successfully.")
    except Exception as e:
        # Rollback the session in case of an error to ensure a clean state
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, # Use 400 for client-side query errors
            detail=f"Error executing query: {e}"
        )