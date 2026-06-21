from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database.connection import init_db
from src.api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize PostgreSQL schema on startup
    init_db()
    yield

app = FastAPI(
    title="Automated Code Review Assistant",
    description="A production-quality Python static analysis service",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)
