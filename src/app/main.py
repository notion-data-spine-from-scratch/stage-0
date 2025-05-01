from fastapi import FastAPI

from app.routers.blocks import router as blocks_router


def create_app() -> FastAPI:
    app = FastAPI(title="Notion-Proto · Stage 0")
    app.include_router(blocks_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
