from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
# No specific models from app.models are used as per the requirement "Data Models Used: None".
# Pydantic models for responses are defined locally for clarity and OpenAPI documentation.
from pydantic import BaseModel

# Define Pydantic models for responses
class ServiceStatusResponse(BaseModel):
    """
    Response model for the root endpoint, providing overall service status.
    """
    message: str
    service_status: str
    backend_integration_status: str

class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.
    """
    status: str

# Create router = APIRouter() at module level
# Tag the router appropriately
router = APIRouter(
    prefix="",  # These endpoints are typically at the root level
    tags=["Core Service"]
)

@router.get(
    "/",
    response_model=ServiceStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get API Service Status",
    description="""
    Retrieves the overall operational status of the API service.

    This endpoint indicates if the service is ready to route incoming HTTP requests
    and provides a status check for its critical backend integrations.
    It simulates a check for backend service connectivity.
    """
)
def get_api_service_status(db: Session = Depends(get_db)):
    """
    Retrieves the overall status of the API service.

    This endpoint provides a high-level overview of the service's operational status,
    indicating if it's ready to route incoming HTTP requests and if its backend
    integrations are functioning. It simulates a check for backend service connectivity.
    """
    try:
        # Simulate a check for backend service integration.
        # In a real application, this would involve making an actual call
        # to a backend service (e.g., another microservice, a message queue, etc.)
        # or checking a connection pool status.
        backend_service_ok = True # Assume backend is OK for this example

        # Example of a more realistic check:
        # try:
        #     # Attempt to query a backend service or check a connection
        #     # For instance, if integrating with a user service:
        #     # user_service_client.get_status()
        #     # If it fails, set backend_service_ok = False
        #     pass
        # except Exception:
        #     backend_service_ok = False

        if not backend_service_ok:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend service integration is currently unavailable."
            )

        return ServiceStatusResponse(
            message="API Service is operational and ready to route requests.",
            service_status="Online",
            backend_integration_status="Operational"
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions directly
        raise e
    except Exception as e:
        # Catch any unexpected errors during the status check
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while checking service status: {e}"
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform Health Check",
    description="""
    Performs a simple health check of the API service.

    This endpoint is primarily used by load balancers and monitoring systems
    to determine if the service is alive and responding to requests.
    It includes a basic database connectivity check.
    """
)
def get_health_status(db: Session = Depends(get_db)):
    """
    Performs a simple health check of the API service.

    This endpoint is used by monitoring systems to determine if the service is alive
    and responding to requests. It includes a basic database connectivity check
    to ensure the application can connect to its data store.
    """
    try:
        # Perform a very basic database connectivity check.
        # This will raise an error if the database connection is completely broken.
        db.execute("SELECT 1")
        db.commit() # Commit to ensure any implicit transaction is closed/released
    except Exception as e:
        # If the database check fails, the service is considered unhealthy.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )

    return HealthResponse(status="OK")