from fastapi import FastAPI
from app.api import api_router
from app.db.init_db import init_db

def create_app():

    async def lifespan(app: FastAPI):
        print("Running database initialization...")
        init_db()
        yield

    app = FastAPI(
        title="RAG Backend API",
        description="Second Brain RAG System",
        version="1.0.0",
        lifespan=lifespan
    )

    app.include_router(api_router)
    return app

app = create_app()
