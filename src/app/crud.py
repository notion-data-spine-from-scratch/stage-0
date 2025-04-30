# src/app/crud.py

import uuid
from typing import Any, Dict, Optional

from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import metadata

# Grab the reflected table
blocks_table = metadata.tables["blocks"]


async def fetch_block(
    block_id: uuid.UUID, session: AsyncSession
) -> Optional[Dict[str, Any]]:
    """
    Fetch a single block by ID. Returns a dict of columns or None if not found.
    """
    stmt = select(blocks_table).where(blocks_table.c.id == block_id)
    result = await session.execute(stmt)
    row = result.first()
    if not row:
        return None
    return dict(row._mapping)


async def insert_block(
    parent_id: Optional[uuid.UUID],
    workspace_id: uuid.UUID,
    type: str,
    props: Dict[str, Any],
    session: AsyncSession,
) -> uuid.UUID:
    """
    Insert a new block, generating a UUID on the Python side.
    Returns the new block's ID.
    """
    new_id = uuid.uuid4()
    stmt = insert(blocks_table).values(
        id=new_id,
        parent_id=parent_id,
        workspace_id=workspace_id,
        type=type,
        props=props,
        version=1,
    )
    await session.execute(stmt)
    await session.commit()
    return new_id


async def update_block(
    block_id: uuid.UUID,
    new_props: Dict[str, Any],
    expected_version: int,
    session: AsyncSession,
) -> bool:
    """
    Optimistically update a block's props if version matches,
    incrementing version by 1. Returns True on success, False if
    the version check failed.
    """
    stmt = (
        update(blocks_table)
        .where(
            (blocks_table.c.id == block_id)
            & (blocks_table.c.version == expected_version)
        )
        .values(
            props=new_props,
            version=blocks_table.c.version + 1,
        )
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount == 1
