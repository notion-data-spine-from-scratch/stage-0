from __future__ import annotations

import json
import uuid
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# --------------------------------------------------------------------------- #
# ── helpers ---------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


async def fetch_block(
    block_id: uuid.UUID,
    session: AsyncSession,
) -> Optional[dict[str, Any]]:
    """
    Return a block row as a **dict** or **None** if it doesn’t exist.
    """
    q = text(
        """
        SELECT id, parent_id, workspace_id, type, props, version
          FROM blocks
         WHERE id = :id
        """
    )
    row = await session.execute(q, {"id": block_id})
    rec = row.mappings().first()
    return dict(rec) if rec else None


async def insert_block(
    parent_id: uuid.UUID | None,
    workspace_id: uuid.UUID,
    type_: str,  # noqa: A002 – shadowing built-in “type”
    props: dict[str, Any],
    session: AsyncSession,
) -> uuid.UUID:
    """
    Insert a new block and return its freshly-generated UUID.
    Accepts **positional** or keyword arguments – matches the tests.
    """
    block_id = uuid.uuid4()
    await session.execute(
        text(
            """
            INSERT INTO blocks (id, parent_id, workspace_id, type,  props,  version)
            VALUES             (:id, :p_id,    :ws_id,      :t,   :props, 1)
            """
        ),
        {
            "id": block_id,
            "p_id": parent_id,
            "ws_id": workspace_id,
            "t": type_,
            "props": json.dumps(props),
        },
    )
    await session.commit()
    return block_id


async def update_block(
    block_id: uuid.UUID,
    props: dict[str, Any],
    expected_version: int,
    session: AsyncSession,
) -> Optional[dict[str, Any]] | bool:
    """
    Optimistic-lock update.

    * If the current ``version`` == ``expected_version``:
        • updates the row
        • bumps ``version`` by **+1**
        • returns the full record (dict)

    * If the version is stale → **False** is returned so callers can emit **409**.
    """
    q = text(
        """
        UPDATE blocks
           SET props   = :props,
               version = version + 1
         WHERE id      = :id
           AND version = :ver
     RETURNING id, parent_id, workspace_id, type, props, version
        """
    )
    res = await session.execute(
        q, {"id": block_id, "ver": expected_version, "props": json.dumps(props)}
    )
    rec = res.mappings().first()

    if rec is None:  # stale version – nothing changed
        await session.rollback()
        return False

    await session.commit()
    return dict(rec)
