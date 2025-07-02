from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws import manager

router = APIRouter()


@router.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str) -> None:
    await manager.connect(workspace_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        await manager.disconnect(workspace_id, websocket)
