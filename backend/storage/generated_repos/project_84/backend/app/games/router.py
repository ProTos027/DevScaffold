from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.dependencies import GetDB, CurrentActiveUser
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.games import schemas, services
from app.games.models import Game, GameStatus, PieceColor


router = APIRouter()


@router.post("/create", response_model=schemas.GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(game_create: schemas.GameCreate, current_user: CurrentActiveUser, db: GetDB):
    """Create a new game instance. The creating user becomes player white."""
    game = services.GameService.create_game(
        db=db,
        title=game_create.title,
        variant_name=game_create.variant_name,
        player_white_id=current_user.id
    )
    return game


@router.post("/{game_id}/join", response_model=schemas.GameResponse)
def join_game(game_id: int, current_user: CurrentActiveUser, db: GetDB):
    """Allows a user to join an existing game as player black."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise NotFoundException("Game not found")

    if game.player_white_id == current_user.id:
        raise BadRequestException("You are already player white in this game.")

    if game.player_black_id is not None and game.player_black_id != current_user.id:
        raise BadRequestException("Game already has two players.")

    if game.player_black_id == current_user.id:
        return game # Already joined as black

    game.player_black_id = current_user.id
    game.status = GameStatus.IN_PROGRESS
    game.current_player_id = game.player_white_id # White always starts
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@router.get("/{game_id}", response_model=schemas.GameResponse)
def get_game(game_id: int, db: GetDB):
    """Retrieve details of a specific game."""
    game = services.GameService.get_game_by_id(db, game_id)
    if not game:
        raise NotFoundException("Game not found")
    return game


@router.get("/", response_model=List[schemas.GameResponse])
def get_all_games(db: GetDB, skip: int = 0, limit: int = 100):
    """Retrieve a list of all active or public games."""
    games = db.query(Game).offset(skip).limit(limit).all()
    return games


@router.post("/{game_id}/move", response_model=schemas.GameResponse)
def make_move(game_id: int, move_request: schemas.MoveRequest, current_user: CurrentActiveUser, db: GetDB):
    """Submit a move for a game."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise NotFoundException("Game not found")

    if game.status not in [GameStatus.IN_PROGRESS, GameStatus.CHECK]:
        raise BadRequestException(f"Game is not in a playable state. Current status: {game.status}")

    # Determine which player is making the move based on current_turn
    expected_player_id = None
    if game.current_turn == PieceColor.WHITE:
        expected_player_id = game.player_white_id
    elif game.current_turn == PieceColor.BLACK:
        expected_player_id = game.player_black_id

    if current_user.id != expected_player_id:
        raise ForbiddenException("It's not your turn or you are not a player in this game.")

    updated_game = services.GameService.apply_move(
        db=db,
        game=game,
        player_id=current_user.id,
        from_coords=(move_request.from_x, move_request.from_y),
        to_coords=(move_request.to_x, move_request.to_y),
        promotion_choice=move_request.promotion_choice
    )
    return updated_game


@router.post("/{game_id}/resign", response_model=schemas.GameResponse)
def resign_game(game_id: int, current_user: CurrentActiveUser, db: GetDB):
    """Allow a player to resign from a game."""
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise NotFoundException("Game not found")

    if current_user.id not in [game.player_white_id, game.player_black_id]:
        raise ForbiddenException("You are not a player in this game.")

    if game.status not in [GameStatus.IN_PROGRESS, GameStatus.CHECK]:
        raise BadRequestException("Game is not in a state where it can be resigned.")

    game.status = GameStatus.RESIGNED
    # Optionally, set winner based on who resigned
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

