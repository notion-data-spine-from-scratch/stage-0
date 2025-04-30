from fastapi import FastAPI

from app.routers.blocks import router as blocks_router  # import your router here


def create_app() -> FastAPI:
    app = FastAPI(title="Notion-Proto · Stage 0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Mount the blocks router under the /blocks prefix
    app.include_router(blocks_router)

    return app
