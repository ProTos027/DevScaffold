from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.game_service import game_service, connection_manager
from app.schemas.game import GameCreate, GameResponse, GameFullStateResponse
from app.schemas.websocket import WebSocketMessage, WsErrorPayload, WebSocketMessageType
import json

router = APIRouter(prefix="/games", tags=["Games"])

@router.post("/", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(game_in: GameCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    game = await game_service.create_new_game(db, game_in, current_user.id)
    return GameResponse.model_validate(game)

@router.post("/{game_id}/join", response_model=GameResponse)
async def join_game(game_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    game = await game_service.join_game(db, game_id, current_user.id)
    return GameResponse.model_validate(game)

@router.get("/available", response_model=List[GameResponse])
async def get_available_games_api(db: AsyncSession = Depends(get_db)):
    games = await game_service.get_available_games(db)
    return [GameResponse.model_validate(game) for game in games]

@router.get("/my-active", response_model=List[GameResponse])
async def get_my_active_games_api(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    games = await game_service.get_active_games_for_user(db, current_user.id)
    return [GameResponse.model_validate(game) for game in games]

@router.get("/{game_id}", response_model=GameFullStateResponse)
async def get_game_state(game_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    game = await game_service.get_game_full_state(db, game_id)
    # Basic authorization: ensure user is a player in the game
    if current_user.id not in [game.player1_id, game.player2_id]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this game.")
    return game

@router.websocket("/{game_id}/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: int, player_id: int, db: AsyncSession = Depends(get_db)):
    # In a real application, you'd verify player_id and game_id with authentication
    # For this boilerplate, we assume player_id is valid and authorized to join this game.
    # You could pass JWT token via WebSocket header or query param and verify it here.
    # For now, let's just do a basic check that the player is indeed part of the game.
    game = await game_service.get_game_by_id(db, game_id)
    if not game or (game.player1_id != player_id and game.player2_id != player_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Player not part of this game or game not found")
        return
    
    # Attach db session to websocket state for use in game_service
    websocket.state.db = db

    await connection_manager.connect(websocket, game_id)
    try:
        # On connection, send the initial game state
        initial_state = await game_service.get_game_full_state(db, game_id)
        initial_state_msg = WebSocketMessage(
            type=WebSocketMessageType.GAME_STATE_UPDATE,
            payload=initial_state.model_dump()
        )
        await connection_manager.send_personal_message(initial_state_msg.model_dump_json(), websocket)

        while True:
            data = await websocket.receive_text()
            await game_service.handle_websocket_message(websocket, game_id, player_id, data)

    except WebSocketDisconnect:
        await connection_manager.disconnect(websocket, game_id)
        print(f"Client disconnected from game {game_id}, player {player_id}")
    except Exception as e:
        print(f"Error in WebSocket for game {game_id}, player {player_id}: {e}")
        # Send an error message to the client before closing
        error_message = WebSocketMessage(
            type=WebSocketMessageType.ERROR,
            payload=WsErrorPayload(game_id=game_id, error_message=f"An unexpected error occurred: {e}")
        )
        await connection_manager.send_personal_message(error_message.model_dump_json(), websocket)
        await connection_manager.disconnect(websocket, game_id)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Internal server error")