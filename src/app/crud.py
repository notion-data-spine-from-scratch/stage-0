from typing import Optional
from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import metadata

blocks = metadata.tables["blocks"]


async def insert_block(
    parent_id: Optional[UUID],
    workspace_id: UUID,
    type: str,
    props: dict,
    db: AsyncSession,
) -> UUID:
    stmt = (
        insert(blocks)
        .values(parent_id=parent_id, workspace_id=workspace_id, type=type, props=props)
        .returning(blocks.c.id)
    )
    result = await db.execute(stmt)
    new_id = result.scalar_one()
    await db.commit()
    return new_id


async def fetch_block(block_id: UUID, db: AsyncSession) -> dict:
    stmt = select(blocks).where(blocks.c.id == block_id)
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise NoResultFound(f"Block {block_id} not found")
    # row._mapping is a RowMapping; convert to plain dict
    return dict(row._mapping)


async def update_block(
    block_id: UUID,
    props: dict,
    version: int,
    db: AsyncSession,
) -> None:
    stmt = (
        update(blocks)
        .where(blocks.c.id == block_id, blocks.c.version == version)
        .values(props=props, version=version + 1)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        # no rows updated → optimistic lock failure
        raise Exception("Version conflict")
    await db.commit()
