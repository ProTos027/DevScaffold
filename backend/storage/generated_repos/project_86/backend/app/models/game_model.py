import datetime
import uuid
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel

class GameStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"
    DRAW = "draw"

class Game(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    player1_id: uuid.UUID = Field(index=True)
    player2_id: uuid.UUID = Field(index=True)

    status: GameStatus = Field(default=GameStatus.PENDING)
    current_turn: uuid.UUID
    winner_id: Optional[uuid.UUID] = Field(default=None, index=True)

    start_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    end_time: Optional[datetime.datetime] = Field(default=None)