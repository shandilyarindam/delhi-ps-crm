"""Delhi PS-CRM FastAPI application entry point."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from routers import webhook, notifications
from services.escalation_cron import run_escalation_check

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    logger.info("Starting escalation scheduler (every 30 min)")
    scheduler.add_job(
        run_escalation_check,
        IntervalTrigger(minutes=30, start_date=datetime.now(timezone.utc)),
        id="escalation_check",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shut down")


app = FastAPI(
    title="Delhi PS-CRM",
    description="WhatsApp-based civic complaint management system for Delhi. "
    "Uses Gemini AI for classification, Supabase for storage, "
    "and ML-based auto-escalation.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(webhook.router)
app.include_router(notifications.router)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic application status."""
    return {"status": "Delhi PS-CRM Backend Running"}


@app.get("/health")
def health() -> dict[str, str]:
    """Return application health check and version."""
    return {"status": "healthy", "version": "1.0.0"}
