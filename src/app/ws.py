from __future__ import annotations

import asyncio
import json
import os
from collections import defaultdict
from typing import DefaultDict, Set

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections per workspace."""

    def __init__(self) -> None:
        self.rooms: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, workspace_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.rooms[workspace_id].add(websocket)

    async def disconnect(self, workspace_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self.rooms[workspace_id].discard(websocket)
            if not self.rooms[workspace_id]:
                del self.rooms[workspace_id]

    async def broadcast(self, workspace_id: str, message: dict) -> None:
        async with self._lock:
            receivers = list(self.rooms.get(workspace_id, []))
        for ws in receivers:
            try:
                await ws.send_json(message)
            except Exception:
                await self.disconnect(workspace_id, ws)


manager = ConnectionManager()


async def start_kafka_consumer() -> None:
    """Background task consuming block_patch and broadcasting patches."""

    bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    if not bootstrap:
        return
    consumer = AIOKafkaConsumer(
        "block_patch",
        bootstrap_servers=bootstrap,
        value_deserializer=lambda v: json.loads(v.decode()),
    )
    try:
        await consumer.start()
    except KafkaError:
        await consumer.stop()
        return
    try:
        async for msg in consumer:
            workspace = msg.value.get("workspace_id")
            if workspace:
                await manager.broadcast(workspace, msg.value)
    finally:
        await consumer.stop()
