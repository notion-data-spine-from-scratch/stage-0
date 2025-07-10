#!/usr/bin/env python3
"""End-to-end test bench for the Stage-0 stack.

This script exercises the API, WebSocket broadcast and CRDT merge service.
It expects the full Docker Compose environment from ``compose/full.yml`` to be
running.
"""

import asyncio
import json
import os
import uuid

import httpx
import websockets
from sqlalchemy import text

# -------------------------------------------------------------------------
# Environment defaults
# -------------------------------------------------------------------------

# If run from the host, fall back to the compose-exposed Postgres port.
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://notion:notion@localhost:5433/notion"
    )

API_URL = os.getenv("API_URL", "http://localhost:8000")
WS_URL = os.getenv("WS_URL", "ws://localhost:8000/ws")

from app.database import AsyncSessionLocal  # noqa: E402  (after env tweak)


async def seed_workspace() -> uuid.UUID:
    """Insert a user and workspace directly in the database."""
    async with AsyncSessionLocal() as session:
        user_id = uuid.uuid4()
        email = f"bench+{user_id}@example.com"
        await session.execute(
            text(
                """
                INSERT INTO users (id, email, hashed_password)
                VALUES (:id, :email, 'pw')
                ON CONFLICT (email) DO NOTHING
                """
            ),
            {"id": user_id, "email": email},
        )
        workspace_id = uuid.uuid4()
        await session.execute(
            text(
                """
                INSERT INTO workspaces (id, owner_id, name)
                VALUES (:id, :owner, 'bench')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": workspace_id, "owner": user_id},
        )
        await session.commit()
        return workspace_id


async def run_bench() -> None:
    workspace_id = await seed_workspace()

    async with httpx.AsyncClient(base_url=API_URL) as client:
        # Wait up to ten seconds for the API to be reachable
        for _ in range(10):
            try:
                resp = await client.get("/health")
                resp.raise_for_status()
                break
            except (httpx.RequestError, httpx.HTTPStatusError):
                await asyncio.sleep(1)
        else:
            raise RuntimeError("API never became healthy")

        # Create a block
        block_payload = {
            "parent_id": None,
            "workspace_id": str(workspace_id),
            "type": "text",
            "props": {"bench": True},
        }
        post = await client.post("/blocks/", json=block_payload)
        post.raise_for_status()
        block_id = post.json()["id"]

        # Patch it
        patch = await client.patch(
            f"/blocks/{block_id}",
            json={"props": {"bench": 2}, "version": 1},
        )
        patch.raise_for_status()

        # WebSocket round-trip
        async with websockets.connect(f"{WS_URL}/{workspace_id}") as ws:
            ops_payload = {
                "client_id": "bench",
                "base_version": 2,
                "ops": ["foo"],
            }
            ops = await client.post(f"/blocks/{block_id}/ops", json=ops_payload)
            ops.raise_for_status()

            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            assert data["block_id"] == str(block_id)

    print("Bench completed successfully.")


def main() -> None:
    asyncio.run(run_bench())


if __name__ == "__main__":
    main()
