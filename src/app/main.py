from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="Notion-Proto · Stage 0")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
