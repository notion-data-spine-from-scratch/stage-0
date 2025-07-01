from fastapi import FastAPI

from app.routers.blocks import router as blocks_router
from app.routers.ws import router as ws_router
from app.ws import start_kafka_consumer


def create_app() -> FastAPI:
    app = FastAPI(title="Notion-Proto · Stage 0")

    @app.on_event("startup")
    async def _startup() -> None:
        import asyncio

        asyncio.create_task(start_kafka_consumer())

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(blocks_router)
    app.include_router(ws_router)
    return app
