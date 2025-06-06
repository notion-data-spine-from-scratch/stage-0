# tests/test_crud.py

import uuid

import pytest
from sqlalchemy import text

from app.crud import fetch_block, insert_block, update_block
from app.database import AsyncSessionLocal

pytestmark = pytest.mark.db


@pytest.mark.asyncio
async def test_crud_flow():
    # 1. Create a fresh session
    async with AsyncSessionLocal() as session:
        # 2. Pick any existing workspace_id from the DB
        ws_row = await session.execute(text("SELECT id FROM workspaces LIMIT 1"))
        workspace_id = ws_row.scalar_one()

        # 3. Insert a new block
        parent = None
        props = {"foo": "bar"}
        block_id = await insert_block(parent, workspace_id, "text", props, session)
        assert isinstance(block_id, uuid.UUID)

        # 4. Fetch it back
        block = await fetch_block(block_id, session)
        assert block is not None
        assert block["id"] == block_id
        assert block["props"] == props
        assert block["version"] == 1

        # 5. Successful optimistic update
        new_props = {"foo": "baz"}
        ok = await update_block(
            block_id, new_props, expected_version=1, session=session
        )
        assert ok

        # 6. Fetch again & check version bump
        updated = await fetch_block(block_id, session)
        assert updated["props"] == new_props
        assert updated["version"] == 2

        # 7. Stale update should fail
        stale = await update_block(
            block_id, {"x": 1}, expected_version=1, session=session
        )
        assert stale is False
