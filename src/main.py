import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.core.database import SessionLocal
from src.api import displays, health, news, ws, templates
from src.logging_config import setup_logging
from src.services.news_watcher import news_watcher_service

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    news_watcher_task = asyncio.create_task(
        news_watcher_service.run_polling(
            session_factory=SessionLocal,
            interval_seconds=settings.NEWS_POLL_INTERVAL_SECONDS,
        )
    )
    app.state.news_watcher_task = news_watcher_task

    try:
        yield
    finally:
        news_watcher_task.cancel()
        try:
            await news_watcher_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="Display API", version="1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(displays.router)
app.include_router(news.router)
app.include_router(templates.router)
app.include_router(ws.router)
