# src/app/routers/blocks.py
from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_get, cache_set
from app.crud import fetch_block, insert_block, update_block
from app.database import get_db
from app.schemas import BlockIn, BlockOut, BlockUpdate

router = APIRouter(prefix="/blocks", tags=["blocks"])


def _cache_key(block_id: uuid.UUID) -> str:
    """Consistent Redis key format."""
    return f"block:{block_id}"


@router.get("/{block_id}", response_model=BlockOut)
async def get_block(
    block_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> BlockOut:
    if (cached := await cache_get(_cache_key(block_id))) is not None:
        return cached  # type: ignore[return-value]

    record: Dict[str, Any] | None = await fetch_block(block_id, db)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Block not found"
        )
    await cache_set(_cache_key(block_id), record)
    return record  # type: ignore[return-value]


@router.post("/", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
async def post_block(payload: BlockIn, db: AsyncSession = Depends(get_db)) -> BlockOut:
    new_id = await insert_block(
        parent_id=payload.parent_id,
        workspace_id=payload.workspace_id,
        type_=payload.type_,
        props=payload.props,
        session=db,
    )
    # Invalidate (just in case) and fetch fresh row
    await cache_set(_cache_key(new_id), None, ttl=0)
    record = await fetch_block(new_id, db)
    # `insert_block` guarantees the row exists; mypy-safe cast
    return record  # type: ignore[return-value]


@router.patch("/{block_id}", response_model=BlockOut)
async def patch_block(
    block_id: uuid.UUID, payload: BlockUpdate, db: AsyncSession = Depends(get_db)
) -> BlockOut:
    updated = await update_block(
        block_id=block_id,
        props=payload.props,
        expected_version=payload.version,
        session=db,
    )
    if updated is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Version conflict"
        )
    # Refresh cache
    await cache_set(_cache_key(block_id), updated)
    return updated  # type: ignore[return-value]
