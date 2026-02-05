from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdateStatennasync def get_game_by_id(db: AsyncSession, game_id: int) -> Optional[Game]:
    result = await db.execute(select(Game).where(Game.id == game_id))
    return result.scalar_one_or_none()

async def get_active_games_for_user(db: AsyncSession, user_id: int) -> List[Game]:
    result = await db.execute(
        select(Game).where(
            (Game.player1_id == user_id) | (Game.player2_id == user_id),
            Game.status.in_(["waiting_for_player", "in_progress"])
        )
    )
    return result.scalars().all()

async def get_available_games(db: AsyncSession) -> List[Game]:
    result = await db.execute(
        select(Game).where(
            Game.status == "waiting_for_player",
            Game.player2_id == None # Only games waiting for a second player
        )
    )
    return result.scalars().all()

async def create_game(db: AsyncSession, game_in: GameCreate, player1_id: int) -> Game:
    db_game = Game(**game_in.model_dump(), player1_id=player1_id)
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game

async def update_game_state(db: AsyncSession, game: Game, game_update: GameUpdateState) -> Game:
    for field, value in game_update.model_dump(exclude_unset=True).items():
        setattr(game, field, value)
    await db.commit()
    await db.refresh(game)
    return game

async def delete_game(db: AsyncSession, game: Game) -> None:
    await db.delete(game)
    await db.commit()