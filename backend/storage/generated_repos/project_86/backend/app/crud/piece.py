from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.piece import Piece
from app.schemas.game import PieceCreateSch, PieceUpdateSchnnasync def get_piece_by_id(db: AsyncSession, piece_id: int) -> Optional[Piece]:
    result = await db.execute(select(Piece).where(Piece.id == piece_id))
    return result.scalar_one_or_none()

async def get_pieces_for_game(db: AsyncSession, game_id: int) -> List[Piece]:
    result = await db.execute(select(Piece).where(Piece.game_id == game_id))
    return result.scalars().all()

async def create_piece(db: AsyncSession, piece_in: PieceCreateSch) -> Piece:
    db_piece = Piece(**piece_in.model_dump())
    db.add(db_piece)
    await db.commit()
    await db.refresh(db_piece)
    return db_piece

async def update_piece(db: AsyncSession, piece: Piece, piece_update: PieceUpdateSch) -> Piece:
    for field, value in piece_update.model_dump(exclude_unset=True).items():
        setattr(piece, field, value)
    await db.commit()
    await db.refresh(piece)
    return piece

async def delete_piece(db: AsyncSession, piece: Piece) -> None:
    await db.delete(piece)
    await db.commit()