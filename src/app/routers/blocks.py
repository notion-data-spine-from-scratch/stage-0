# src/app/routers/blocks.py
from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import cache_get, cache_set
from app.crud import fetch_block, insert_block, update_block
from app.database import get_db
from app.schemas import BlockIn, BlockOut, BlockUpdate, OpsIn, OpsOut
from services.ot_client import OTClient

router = APIRouter(prefix="/blocks", tags=["blocks"])

CRDT_GRPC_ADDR = os.getenv("CRDT_GRPC_ADDR", "localhost:50051")
_ot_client: OTClient | None = None
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
_producer: AIOKafkaProducer | None = None


def get_ot_client() -> OTClient:
    global _ot_client
    if _ot_client is None:
        _ot_client = OTClient(CRDT_GRPC_ADDR)
    return _ot_client


async def get_producer() -> AIOKafkaProducer | None:
    global _producer
    if not KAFKA_BOOTSTRAP:
        return None
    if _producer is None:
        _producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
        try:
            await _producer.start()
        except KafkaError:
            return None
    return _producer


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


@router.post("/{block_id}/ops", response_model=OpsOut)
async def post_block_ops(
    block_id: uuid.UUID, payload: OpsIn, db: AsyncSession = Depends(get_db)
) -> OpsOut:
    """Push CRDT operations for a block."""

    client = get_ot_client()
    ops_bytes = [op.encode() for op in payload.ops]
    version, patch = client.push_ops(
        str(block_id),
        payload.client_id,
        base_version=payload.base_version,
        ops=ops_bytes,
    )

    current = await fetch_block(block_id, db)
    if current is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Block not found"
        )

    updated = await update_block(
        block_id=block_id,
        props=current["props"],
        expected_version=payload.base_version,
        session=db,
    )

    if updated is False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Version conflict"
        )
    assert isinstance(updated, dict)

    await cache_set(_cache_key(block_id), updated)

    producer = await get_producer()
    if producer is not None:
        try:
            await producer.send_and_wait(
                "block_patch",
                json.dumps(
                    {
                        "block_id": str(block_id),
                        "workspace_id": str(updated["workspace_id"]),
                        "version": version,
                        "patch": [p.decode() for p in patch],
                    }
                ).encode(),
            )
        except KafkaError:
            pass

    return OpsOut(version=version, patch=[p.decode() for p in patch])
