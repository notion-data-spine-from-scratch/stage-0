# tests/test_api_blocks.py

import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.database import AsyncSessionLocal
from app.main import create_app


@pytest.mark.asyncio
async def test_blocks_endpoints():
    """
    End-to-end integration test for the /blocks router:
     1. Seed a unique user and workspace
     2. Health check
     3. POST a new block
     4. GET it back
     5. PATCH with optimistic locking
     6. Verify version conflict
    """
    # 1. Seed a unique user + workspace
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        unique_email = f"user+{user_id}@example.com"
        # Use INSERT ... ON CONFLICT DO NOTHING to avoid any future collisions
        await session.execute(
            text(
                """
                INSERT INTO users (id, email, hashed_password)
                VALUES (:id, :email, :hp)
                ON CONFLICT (email) DO NOTHING
                """
            ),
            {"id": user_id, "email": unique_email, "hp": "pw"},
        )

        workspace_id = uuid.uuid4()
        await session.execute(
            text(
                """
                INSERT INTO workspaces (id, owner_id, name)
                VALUES (:id, :owner, :name)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": workspace_id, "owner": user_id, "name": "api-test-ws"},
        )

        await session.commit()

    # 2. Spin up FastAPI app in-process
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Health check
        resp = await client.get("/health")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"status": "ok"}

        # 3. POST a new block
        new_payload = {
            "parent_id": None,
            "workspace_id": str(workspace_id),
            "type": "text",
            "props": {"hello": "world"},
        }
        post_resp = await client.post("/blocks/", json=new_payload)
        assert post_resp.status_code == status.HTTP_201_CREATED
        post_data = post_resp.json()
        block_id = post_data["id"]
        assert post_data["props"] == new_payload["props"]
        assert post_data["version"] == 1

        # 4. GET it back
        get_resp = await client.get(f"/blocks/{block_id}")
        assert get_resp.status_code == status.HTTP_200_OK
        assert get_resp.json() == post_data

        # 5. PATCH with optimistic lock
        patch_payload = {"props": {"hello": "universe"}, "version": 1}
        patch_resp = await client.patch(f"/blocks/{block_id}", json=patch_payload)
        assert patch_resp.status_code == status.HTTP_200_OK
        updated_data = patch_resp.json()
        assert updated_data["version"] == 2
        assert updated_data["props"] == {"hello": "universe"}

        # 6. PATCH stale → conflict
        stale_resp = await client.patch(f"/blocks/{block_id}", json=patch_payload)
        assert stale_resp.status_code == status.HTTP_409_CONFLICT
