from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from wenotify.core.logging import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pathlib import Path

from app.api.routes import api_router
from wenotify.core.config import settings
from wenotify.db.session import get_async_db
from wenotify.tasks import daily_tasks

scheduler = AsyncIOScheduler(timezone="Africa/Nairobi")


async def scheduled_task_wrapper():
    """Wrapper to create a new session for scheduled tasks"""
    async with get_async_db() as session:
        await daily_tasks(session)


@asynccontextmanager
async def lifespan(app: FastAPI):

    scheduler.add_job(func=scheduled_task_wrapper, trigger="interval", days=1)
    scheduler.start()
    logger.info("Started scheduler for daily tasks")

    yield

    scheduler.shutdown()
    logger.info("Shut down scheduler")


app = FastAPI(
    title="WenotiFy Kenya API",
    description="A simple FastAPI application with modern features and lifecycle events",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix=settings.API_V1_STR)


directory = Path(__file__).joinpath("../../").resolve()
templates = Jinja2Templates(directory)


@app.get("/docs/", response_class=HTMLResponse, include_in_schema=False)
def view_documentations(request: Request):
    return templates.TemplateResponse(
        "static/docs.html",
        {
            "request": request,
            "schema_url": "/openapi.json",
            "title": str(settings.PROJECT_NAME),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
