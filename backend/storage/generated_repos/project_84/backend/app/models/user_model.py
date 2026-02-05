from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
