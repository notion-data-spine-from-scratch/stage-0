# src/app/routers/blocks.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import fetch_block, insert_block, update_block
from app.database import get_db
from app.schemas import BlockIn, BlockOut, BlockUpdate

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.get("/{block_id}", response_model=BlockOut)
async def get_block(
    block_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    block = await fetch_block(block_id, db)
    if block is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Block not found",
        )
    return block


@router.post("/", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
async def post_block(
    payload: BlockIn,
    db: AsyncSession = Depends(get_db),
):
    # positional call: parent_id, workspace_id, type, props, db
    new_id = await insert_block(
        payload.parent_id,
        payload.workspace_id,
        payload.type,  # no trailing underscore here
        payload.props,
        db,
    )
    new_block = await fetch_block(new_id, db)
    return new_block


@router.patch("/{block_id}", response_model=BlockOut)
async def patch_block(
    block_id: UUID,
    payload: BlockUpdate,
    db: AsyncSession = Depends(get_db),
):
    success = await update_block(
        block_id,  # positional
        payload.props,  # positional
        payload.version,  # positional (expected_version)
        db,  # positional
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Version conflict; please refetch",
        )
    updated = await fetch_block(block_id, db)
    return updated
