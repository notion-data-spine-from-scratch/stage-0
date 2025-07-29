# src/app/main.py

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.routers.billing import router as billing_router
from app.routers.blocks import router as blocks_router
from app.routers.search import router as search_router
from app.routers.ws import router as ws_router
from app.ws import start_kafka_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    asyncio.create_task(start_kafka_consumer())
    yield
    # ---- shutdown ----


app = FastAPI(
    title="Notion-Proto · Stage 0",
    lifespan=lifespan,
)

# register API routers
app.include_router(blocks_router, tags=["blocks"])
app.include_router(ws_router, tags=["ws"])
app.include_router(search_router, tags=["search"])
app.include_router(billing_router, tags=["billing"])

Instrumentator().instrument(app).expose(app)


@app.get("/health")
async def health():
    return {"status": "ok"}


def create_app() -> FastAPI:
    """
    Factory function for Uvicorn.
    Returns the FastAPI application instance.
    """
    return app
