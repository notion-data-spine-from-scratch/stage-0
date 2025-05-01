from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud as crud
from app.database import get_db
from app.schemas import BlockIn, BlockOut, BlockUpdate

router = APIRouter(prefix="/blocks", tags=["blocks"])


@router.get("/{block_id}", response_model=BlockOut)
async def get_block(block_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        return await crud.fetch_block(block_id, db)
    except NoResultFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Block not found")


@router.post("/", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
async def post_block(payload: BlockIn, db: AsyncSession = Depends(get_db)):
    new_id = await crud.insert_block(
        parent_id=payload.parent_id,
        workspace_id=payload.workspace_id,
        type=payload.type,
        props=payload.props,
        db=db,
    )
    return await crud.fetch_block(new_id, db)


@router.patch("/{block_id}", response_model=BlockOut)
async def patch_block(
    block_id: UUID,
    payload: BlockUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        await crud.update_block(
            block_id=block_id,
            props=payload.props,
            version=payload.version,
            db=db,
        )
    except Exception:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Version conflict")
    return await crud.fetch_block(block_id, db)
