from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy Base for declarative models
Base = declarative_base()


class ShortenedURL(Base):
    """
    SQLAlchemy ORM model for storing shortened URL data.

    Responsibilities:
    - store_shortened_url_data: Represents the structure for saving new URL data.
    - fetch_shortened_url_by_id: Provides the structure to retrieve by ID.
    - fetch_shortened_url_by_short_code: Provides the structure to retrieve by short code.
    - fetch_all_shortened_urls: Represents individual items in a list of all URLs.
    - update_shortened_url_data: Structure for updating existing URL data.
    - delete_shortened_url_data: Identifies the record to be deleted.
    - increment_url_click_count: Stores and allows modification of the click count.
    """
    __tablename__ = "shortened_urls"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    original_url = Column(String, nullable=False, index=True)
    short_code = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    clicks = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return (
            f"<ShortenedURL(id={self.id}, original_url='{self.original_url}', "
            f"short_code='{self.short_code}', clicks={self.clicks})>"
        )


class ShortenedURLSchema(BaseModel):
    """
    Pydantic schema for API responses of ShortenedURL data.

    This schema is used to serialize ShortenedURL ORM objects into a
    JSON-compatible format for API clients, ensuring proper data types
    and validation.

    Responsibilities:
    - store_shortened_url_data: Used to return the newly created URL data.
    - fetch_shortened_url_by_id: Returns the full data for a specific URL by ID.
    - fetch_shortened_url_by_short_code: Returns the full data for a specific URL by short code.
    - fetch_all_shortened_urls: Represents individual items in a list of all URLs returned.
    - update_shortened_url_data: Returns the updated URL data after a modification.
    - delete_shortened_url_data: Can be used to confirm the deletion by returning the deleted item's data.
    - increment_url_click_count: Returns the URL data with the updated click count.
    """
    id: int
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    clicks: int

    class Config:
        orm_mode = True
        from_attributes = True # For Pydantic v2 compatibility