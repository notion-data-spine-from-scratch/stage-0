#!/usr/bin/env python3
"""Minimal smoke test covering the main API surface."""

import asyncio
import os
import uuid

import httpx

API_URL = os.getenv("API_URL", "http://localhost:8000")


async def main() -> None:
    async with httpx.AsyncClient(base_url=API_URL) as client:
        # Wait (max 10 s) for the API container to report healthy
        for _ in range(10):
            try:
                resp = await client.get("/health")
                resp.raise_for_status()
                break
            except (httpx.RequestError, httpx.HTTPStatusError):
                await asyncio.sleep(1)
        else:
            raise RuntimeError("API never became healthy")

        # Basic CRUD round-trip
        ws = uuid.uuid4()
        block = await client.post(
            "/blocks/",
            json={
                "parent_id": None,
                "workspace_id": str(ws),
                "type": "text",
                "props": {"smoke": True},
            },
        )
        block.raise_for_status()

    print("Smoke test passed")


if __name__ == "__main__":
    asyncio.run(main())
