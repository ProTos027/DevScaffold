from pydantic import BaseModel, Field
from typing import Optional, Any

# Enum for WebSocket message types
class WebSocketMessageType:
    GAME_STATE_UPDATE = "game_state_update"
    PLAYER_MOVE = "player_move"
    CHAT_MESSAGE = "chat_message"
    ERROR = "error"
    GAME_OVER = "game_over"

# Base WebSocket Message Schemanclass WebSocketMessage(BaseModel):
    type: str = Field(..., description="Type of the WebSocket message")
    payload: Any = Field(..., description="Payload data depending on the message type")

# Specific Payloads for Game Actions
class WsPlayerMovePayload(BaseModel):
    game_id: int
    player_id: int
    from_position: str = Field(..., pattern=r"^[a-h][1-8]$", description="e.g., 'e2'")
    to_position: str = Field(..., pattern=r"^[a-h][1-8]$", description="e.g., 'e4'")
    promotion_piece: Optional[str] = None # e.g., 'Q', 'R', 'B', 'N'
    move_id: Optional[str] = None # Client-generated ID to track response

class WsChatMessagePayload(BaseModel):
    game_id: int
    sender_id: int
    message: str
    timestamp: Optional[str] = None # ISO format

# Specific Payloads for Game State Updates
class WsGameStateUpdatePayload(BaseModel):
    game_id: int
    current_fen: str
    last_move: Optional[str] = None # e.g., 'e2e4'
    turn: int # 1 for player1, 2 for player2
    status: str # 'in_progress', 'check', 'checkmate', 'stalemate', etc.
    pieces: list # Simplified representation of pieces: [{'type': 'P', 'color': 'w', 'pos': 'a2'}, ...]
    captured_pieces: list # e.g., [{'type': 'R', 'color': 'b'}, ...]
    message: Optional[str] = None # e.g., "Check!"

class WsErrorPayload(BaseModel):
    game_id: Optional[int] = None
    error_message: str
    code: Optional[int] = None

class WsGameOverPayload(BaseModel):
    game_id: int
    winner_id: Optional[int] = None
    reason: str # 'checkmate', 'stalemate', 'resignation', 'timeout', etc.
