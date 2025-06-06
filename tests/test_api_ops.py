import uuid

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

import services.notion_ot_pb2 as pb2
import services.notion_ot_pb2_grpc as grpc_stubs
from app.database import AsyncSessionLocal
from app.main import create_app

pytestmark = pytest.mark.db


@pytest.fixture(autouse=True)
def fake_stub(monkeypatch):
    class FakeStub:
        def __init__(self, channel):
            self.last_req = None

        def PushOps(self, req):
            return pb2.OpsResponse(version=req.base_version + 1, patch=[b"p1", b"p2"])

    monkeypatch.setattr(grpc_stubs, "NotionOTStub", lambda channel: FakeStub(channel))
    yield


@pytest.mark.asyncio
async def test_ops_success_and_conflict():
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        email = f"user+{user_id}@example.com"
        await session.execute(
            text(
                """
                INSERT INTO users (id, email, hashed_password)
                VALUES (:id, :email, :hp)
                ON CONFLICT (email) DO NOTHING
                """
            ),
            {"id": user_id, "email": email, "hp": "pw"},
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
            {"id": workspace_id, "owner": user_id, "name": "ops-ws"},
        )
        block_id = uuid.uuid4()
        await session.execute(
            text(
                """
                INSERT INTO blocks (id, parent_id, workspace_id, type, props, version)
                VALUES (:id, NULL, :ws, 'text', '{}'::jsonb, 1)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": block_id, "ws": workspace_id},
        )
        await session.commit()

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"client_id": "c1", "base_version": 1, "ops": ["x"]}
        resp = await client.post(f"/blocks/{block_id}/ops", json=payload)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"version": 2, "patch": ["p1", "p2"]}

        payload = {"client_id": "c1", "base_version": 1, "ops": ["y"]}
        conflict = await client.post(f"/blocks/{block_id}/ops", json=payload)
        assert conflict.status_code == status.HTTP_409_CONFLICT
