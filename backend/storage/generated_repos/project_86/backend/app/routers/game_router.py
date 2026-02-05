from fastapi import APIRouter, HTTPException, status, WebSocket, WebSocketDisconnect, Depends, Path
from pydantic import BaseModel
import uuid
import json
from typing import Dict, List, Any

# --- Pydantic Models ---
class CreateGameRequest(BaseModel):
    game_type: str = "chess" # e.g., "chess", "checkers"
    player_id: str

class JoinGameRequest(BaseModel):
    player_id: str

class GameStateResponse(BaseModel):
    game_id: str
    status: str # e.g., "waiting_for_players", "in_progress", "completed"
    players: List[Dict[str, str]] # [{'id': 'player1', 'color': 'white'}]
    board: List[List[str]] # Simplified board representation
    turn: str = None # Which player's turn it is
    winner: str = None

class BoardStateResponse(BaseModel):
    board: List[List[str]] # Simplified board representation
    turn: str = None
    status: str

class MoveMessage(BaseModel):
    player_id: str
    move: str # e.g., "e2e4", or a more complex move object
    # Additional fields like 'chat_message' for combined comms
    message_type: str = "move" # "move", "chat", "game_event"

# --- In-Memory Game Store (for demonstration) ---
games_db: Dict[str, Dict[str, Any]] = {}

def initialize_chess_board():
    """Initializes a standard chess board."""
    return [
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        [" ", " ", " ", " ", " ", " ", " ", " "],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    ]

# --- WebSocket Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = []
        self.active_connections[game_id].append(websocket)

    def disconnect(self, game_id: str, websocket: WebSocket):
        if game_id in self.active_connections and websocket in self.active_connections[game_id]:
            self.active_connections[game_id].remove(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, game_id: str, message: str):
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_text(message)
                except RuntimeError as e: # Handle cases where connection might be closing
                    print(f"Error sending to a websocket: {e}")
                    # Optionally, disconnect the problematic client here

manager = ConnectionManager()

# --- FastAPI Router ---
router = APIRouter()

@router.post("/api/games", response_model=GameStateResponse, status_code=status.HTTP_201_CREATED)
async def create_game(request: CreateGameRequest):
    game_id = str(uuid.uuid4())
    new_game = {
        "game_id": game_id,
        "game_type": request.game_type,
        "status": "waiting_for_players",
        "players": [{
            "id": request.player_id,
            "color": "white" # Creator is always white for now
        }],
        "board": initialize_chess_board(),
        "turn": "white",
        "winner": None
    }
    games_db[game_id] = new_game
    return GameStateResponse(**new_game)

@router.get("/api/games/{game_id}", response_model=GameStateResponse)
async def get_game_state(game_id: str = Path(..., title="The ID of the game")):
    game = games_db.get(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return GameStateResponse(**game)

@router.post("/api/games/{game_id}/join", response_model=GameStateResponse)
async def join_game(game_id: str = Path(..., title="The ID of the game"), request: JoinGameRequest = Depends()):
    game = games_db.get(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    if len(game["players"]) >= 2: # Max 2 players for a typical board game
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is full")

    if request.player_id in [p["id"] for p in game["players"]]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Player already in game")

    # Assign black to the second player
    game["players"].append({"id": request.player_id, "color": "black"})
    game["status"] = "in_progress"

    return GameStateResponse(**game)

@router.get("/api/games/{game_id}/board", response_model=BoardStateResponse)
async def get_board_state(game_id: str = Path(..., title="The ID of the game")):
    game = games_db.get(game_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return BoardStateResponse(board=game["board"], turn=game["turn"], status=game["status"])

@router.websocket("/ws/games/{game_id}/move")
async def websocket_endpoint(websocket: WebSocket, game_id: str = Path(..., title="The ID of the game")):
    game = games_db.get(game_id)
    if not game:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Game not found")
        return

    await manager.connect(game_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Expecting data to be a JSON string representing MoveMessage
            try:
                message = MoveMessage.parse_raw(data)
            except Exception:
                await manager.send_personal_message("Invalid message format", websocket)
                continue

            # --- Game Logic Placeholder ---
            # In a real application, this is where you'd validate the move,
            # update the game state (games_db[game_id]['board'], games_db[game_id]['turn']),
            # and check for game end conditions.

            # Example: simple move processing
            if message.message_type == "move":
                # For demo, just echo the move as a 'game_event'
                response_message = {
                    "game_id": game_id,
                    "message_type": "game_event",
                    "event": "move_made",
                    "player_id": message.player_id,
                    "move": message.move,
                    "board": games_db[game_id]["board"], # Send current board (might need update after move)
                    "turn": games_db[game_id]["turn"] # Send current turn (might need update)
                }
                # Placeholder: If you had a game engine, you'd apply the move here:
                # updated_board, next_turn, game_status, winner = game_engine.apply_move(game["board"], message.move, message.player_id)
                # games_db[game_id]["board"] = updated_board
                # games_db[game_id]["turn"] = next_turn
                # games_db[game_id]["status"] = game_status
                # games_db[game_id]["winner"] = winner
                # For now, just a dummy update:
                if games_db[game_id]["turn"] == "white":
                    games_db[game_id]["turn"] = "black"
                else:
                    games_db[game_id]["turn"] = "white"
                response_message["turn"] = games_db[game_id]["turn"]

                await manager.broadcast(game_id, json.dumps(response_message))

            elif message.message_type == "chat":
                response_message = {
                    "game_id": game_id,
                    "message_type": "chat",
                    "player_id": message.player_id,
                    "text": message.move # Reusing 'move' field for chat content
                }
                await manager.broadcast(game_id, json.dumps(response_message))

            # --- End Game Logic Placeholder ---

    except WebSocketDisconnect:
        manager.disconnect(game_id, websocket)
        # Optionally broadcast player disconnect event
        disconnect_message = {"game_id": game_id, "message_type": "game_event", "event": "player_disconnected"}
        await manager.broadcast(game_id, json.dumps(disconnect_message))
    except Exception as e:
        print(f"WebSocket error for game {game_id}: {e}")
        manager.disconnect(game_id, websocket)
        # Optionally broadcast an error event or handle gracefully
        error_message = {"game_id": game_id, "message_type": "game_event", "event": "error", "detail": str(e)}
        await manager.broadcast(game_id, json.dumps(error_message))
