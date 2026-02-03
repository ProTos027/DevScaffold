from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, HttpUrl

# --- Data Models ---

class ShortenedURLBase(BaseModel):
    """Base model for common fields of a shortened URL."""
    original_url: HttpUrl = Field(..., description="The original URL to be shortened.")
    custom_code: Optional[str] = Field(
        None,
        min_length=3,
        max_length=20,
        regex="^[a-zA-Z0-9_-]+$",
        description="Optional custom short code. If not provided, one will be generated."
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="Optional expiration date for the short URL. After this date, the URL will be inactive."
    )

class ShortenedURLCreate(ShortenedURLBase):
    """Model for creating a new shortened URL."""
    pass

class ShortenedURLUpdate(BaseModel):
    """Model for updating an existing shortened URL."""
    original_url: Optional[HttpUrl] = Field(None, description="The new original URL.")
    expires_at: Optional[datetime] = Field(None, description="The new expiration date for the short URL.")
    is_active: Optional[bool] = Field(None, description="Whether the short URL is active.")

class ShortenedURLInDB(ShortenedURLBase):
    """Model representing a shortened URL as stored in the database."""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the shortened URL.")
    short_code: str = Field(..., min_length=3, max_length=20, description="The unique short code for the URL.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the short URL was created.")
    clicks: int = Field(0, ge=0, description="Number of times the short URL has been clicked.")
    is_active: bool = Field(True, description="Whether the short URL is currently active.")

    class Config:
        from_attributes = True # Enable ORM mode for Pydantic v2

# --- Service Layer (Placeholder) ---

class URLShortenerService:
    """
    A placeholder service class for URL shortening operations.
    In a real application, this would interact with a database
    (e.g., SQLAlchemy, MongoDB) and handle business logic.
    """
    def __init__(self):
        # Using a dictionary as a mock database for demonstration purposes.
        # Key: short_code, Value: ShortenedURLInDB object
        self.db: dict[str, ShortenedURLInDB] = {}

    def _generate_short_code(self) -> str:
        """Generates a unique random short code."""
        import string
        import random
        while True:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            if code not in self.db:
                return code

    def _check_url_status(self, url_entry: ShortenedURLInDB):
        """Checks if a URL entry is active and not expired."""
        if not url_entry.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code is inactive.")
        if url_entry.expires_at and url_entry.expires_at < datetime.utcnow():
            # Optionally deactivate expired URLs in the mock DB
            url_entry.is_active = False
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code has expired.")

    def create_new_short_url(self, url_data: ShortenedURLCreate) -> ShortenedURLInDB:
        """
        Creates a new shortened URL entry in the system.

        Args:
            url_data: The data for the new shortened URL, including original URL
                      and optional custom code or expiration.

        Returns:
            The created ShortenedURLInDB object.

        Raises:
            HTTPException: If the custom short code is already taken (400 Bad Request).
        """
        if url_data.custom_code:
            if url_data.custom_code in self.db:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Custom short code '{url_data.custom_code}' is already in use."
                )
            short_code = url_data.custom_code
        else:
            short_code = self._generate_short_code()

        new_url = ShortenedURLInDB(
            original_url=url_data.original_url,
            short_code=short_code,
            custom_code=url_data.custom_code,
            expires_at=url_data.expires_at,
            created_at=datetime.utcnow()
        )
        self.db[short_code] = new_url
        return new_url

    def retrieve_original_url_by_short_code(self, short_code: str) -> ShortenedURLInDB:
        """
        Retrieves the full details of a shortened URL by its short code.

        Args:
            short_code: The unique short code of the URL to retrieve.

        Returns:
            The ShortenedURLInDB object corresponding to the short code.

        Raises:
            HTTPException: If the short code is not found, inactive, or expired (404 Not Found).
        """
        url_entry = self.db.get(short_code)
        if not url_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")
        
        self._check_url_status(url_entry)
        
        # Increment click count for detailed view
        url_entry.clicks += 1
        return url_entry

    def list_all_shortened_urls(self, skip: int = 0, limit: int = 100) -> List[ShortenedURLInDB]:
        """
        Lists all shortened URLs in the system, with pagination support.

        Args:
            skip: The number of items to skip from the beginning of the list.
            limit: The maximum number of items to return.

        Returns:
            A list of ShortenedURLInDB objects.
        """
        return list(self.db.values())[skip : skip + limit]

    def update_existing_short_url(self, short_code: str, url_update: ShortenedURLUpdate) -> ShortenedURLInDB:
        """
        Updates an existing shortened URL's details.

        Args:
            short_code: The unique short code of the URL to update.
            url_update: The fields to update (e.g., original_url, expires_at, is_active).

        Returns:
            The updated ShortenedURLInDB object.

        Raises:
            HTTPException: If the short code is not found (404 Not Found).
        """
        url_entry = self.db.get(short_code)
        if not url_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")

        update_data = url_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(url_entry, key, value)
        
        # Ensure original_url is re-validated as HttpUrl if updated
        if 'original_url' in update_data:
            url_entry.original_url = HttpUrl(update_data['original_url'])

        self.db[short_code] = url_entry # Update in mock DB
        return url_entry

    def delete_short_url(self, short_code: str):
        """
        Deletes a shortened URL from the system.

        Args:
            short_code: The unique short code of the URL to delete.

        Raises:
            HTTPException: If the short code is not found (404 Not Found).
        """
        if short_code not in self.db:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")
        
        self.db.pop(short_code)

    def handle_short_code_redirection(self, short_code: str) -> str:
        """
        Retrieves the original URL for redirection and increments its click count.

        Args:
            short_code: The short code to resolve for redirection.

        Returns:
            The original URL as a string.

        Raises:
            HTTPException: If the short code is not found, inactive, or expired (404 Not Found).
        """
        url_entry = self.db.get(short_code)
        if not url_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found.")
        
        self._check_url_status(url_entry)
        
        url_entry.clicks += 1 # Increment click count for redirection
        return str(url_entry.original_url) # Return as string for RedirectResponse

# --- Dependency Injection ---

def get_url_shortener_service() -> URLShortenerService:
    """
    Dependency injector that provides a URLShortenerService instance.
    In a real application, this would typically manage a singleton
    or a database session per request.
    """
    # For this example, we'll create a new instance each time.
    # For a production application, consider using a global instance
    # or a dependency that manages database connections.
    return URLShortenerService()

# --- FastAPI Routers ---

# Router for managing shortened URLs (CRUD operations)
router = APIRouter(
    prefix="/urls",
    tags=["URL Shortener Management"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Resource not found"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad request or validation error"}
    },
)

# Router for handling direct short code redirections
redirect_router = APIRouter(
    tags=["URL Redirection"],
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Short code not found or inactive/expired"}
    },
)

@router.post("/", response_model=ShortenedURLInDB, status_code=status.HTTP_201_CREATED)
async def create_new_short_url_endpoint(
    url_data: ShortenedURLCreate,
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Create a new shortened URL.**

    Allows users to submit a long URL and optionally a custom short code
    or an expiration date. If no custom code is provided, a random one
    will be generated.

    - **original_url**: The full URL to be shortened.
    - **custom_code (optional)**: A preferred short code (e.g., "my-cool-link").
      Must be unique if provided.
    - **expires_at (optional)**: A specific date and time when the short URL
      should become inactive.

    Returns the newly created `ShortenedURLInDB` object.
    """
    return service.create_new_short_url(url_data)

@router.get("/", response_model=List[ShortenedURLInDB])
async def list_all_shortened_urls_endpoint(
    skip: int = Field(0, ge=0, description="Number of items to skip for pagination."),
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of items to return."),
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Retrieve a list of all shortened URLs.**

    Supports pagination to fetch a subset of URLs.

    - **skip**: The number of items to skip (for pagination).
    - **limit**: The maximum number of items to return.

    Returns a list of `ShortenedURLInDB` objects.
    """
    return service.list_all_shortened_urls(skip=skip, limit=limit)

@router.get("/{short_code}", response_model=ShortenedURLInDB)
async def retrieve_short_url_details_endpoint(
    short_code: str = Field(..., min_length=3, max_length=20, description="The unique short code of the URL."),
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Retrieve details of a specific shortened URL.**

    Fetches all available information about a short URL, including its
    original URL, creation date, click count, and expiration status.

    - **short_code**: The unique short code of the URL to retrieve.

    Returns a `ShortenedURLInDB` object.
    Raises `HTTPException` with status 404 if the short code is not found,
    inactive, or expired.
    """
    return service.retrieve_original_url_by_short_code(short_code)

@router.put("/{short_code}", response_model=ShortenedURLInDB)
async def update_existing_short_url_endpoint(
    short_code: str = Field(..., min_length=3, max_length=20, description="The unique short code of the URL to update."),
    url_update: ShortenedURLUpdate,
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Update an existing shortened URL.**

    Allows modification of the original URL, expiration date, or active status
    of an existing short URL.

    - **short_code**: The unique short code of the URL to update.
    - **url_update**: The fields to update (original_url, expires_at, is_active).
      Only provided fields will be changed.

    Returns the updated `ShortenedURLInDB` object.
    Raises `HTTPException` with status 404 if the short code is not found.
    """
    return service.update_existing_short_url(short_code, url_update)

@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url_endpoint(
    short_code: str = Field(..., min_length=3, max_length=20, description="The unique short code of the URL to delete."),
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Delete a shortened URL.**

    Permanently removes a short URL entry from the system.

    - **short_code**: The unique short code of the URL to delete.

    Returns an empty response on successful deletion.
    Raises `HTTPException` with status 404 if the short code is not found.
    """
    service.delete_short_url(short_code)
    return # FastAPI automatically handles 204 for no return

@redirect_router.get("/{short_code}", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def handle_short_code_redirection_endpoint(
    short_code: str = Field(..., min_length=3, max_length=20, description="The short code to resolve and redirect."),
    service: URLShortenerService = Depends(get_url_shortener_service)
):
    """
    **Redirect to the original URL.**

    When a user accesses the short code directly (e.g., `yourdomain.com/xyz`),
    this endpoint redirects them to the original, long URL.
    It also increments the click count for the short URL.

    - **short_code**: The short code to resolve and redirect.

    Returns a `RedirectResponse` to the original URL.
    Raises `HTTPException` with status 404 if the short code is not found,
    inactive, or expired.
    """
    original_url = service.handle_short_code_redirection(short_code)
    return RedirectResponse(url=original_url)