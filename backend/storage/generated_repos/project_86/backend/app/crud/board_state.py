from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.board_state import BoardState
from app.schemas.game import BoardStateCreateSch, BoardStateUpdateSchnnasync def get_board_state_by_id(db: AsyncSession, board_state_id: int) -> Optional[BoardState]:
    result = await db.execute(select(BoardState).where(BoardState.id == board_state_id))
    return result.scalar_one_or_none()

async def get_board_states_for_game(db: AsyncSession, game_id: int) -> List[BoardState]:
    result = await db.execute(
        select(BoardState)
        .where(BoardState.game_id == game_id)
        .order_by(BoardState.move_number)
    )
    return result.scalars().all()

async def get_latest_board_state_for_game(db: AsyncSession, game_id: int) -> Optional[BoardState]:
    result = await db.execute(
        select(BoardState)
        .where(BoardState.game_id == game_id)
        .order_by(BoardState.move_number.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def create_board_state(db: AsyncSession, board_state_in: BoardStateCreateSch) -> BoardState:
    db_board_state = BoardState(**board_state_in.model_dump())
    db.add(db_board_state)
    await db.commit()
    await db.refresh(db_board_state)
    return db_board_state

async def update_board_state(db: AsyncSession, board_state: BoardState, board_state_update: BoardStateUpdateSch) -> BoardState:
    for field, value in board_state_update.model_dump(exclude_unset=True).items():
        setattr(board_state, field, value)
    await db.commit()
    await db.refresh(board_state)
    return board_state

async def delete_board_state(db: AsyncSession, board_state: BoardState) -> None:
    await db.delete(board_state)
    await db.commit()