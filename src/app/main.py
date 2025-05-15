from fastapi import FastAPI

from app.routers.blocks import router as blocks_router


def create_app() -> FastAPI:
    app = FastAPI(title="Notion-Proto · Stage 0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(blocks_router)
    return app
