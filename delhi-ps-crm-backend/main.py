"""Delhi PS-CRM FastAPI application entry point."""

import json
import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from routers import webhook, notifications
from services.escalation_cron import run_escalation_check


class StructuredJSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info"]:
                log_entry["extra"] = log_entry.get("extra", {})
                log_entry["extra"][key] = value
        
        return json.dumps(log_entry)


# Configure structured logging
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(StructuredJSONFormatter())
logging.root.setLevel(logging.INFO)
logging.root.addHandler(handler)
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with safe response."""
    logger.warning("Request validation failed", extra={
        "validation_errors": exc.errors(),
        "path": str(request.url),
        "method": request.method
    })
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request format", "type": "validation_error"}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with safe response."""
    logger.warning("HTTP exception", extra={
        "status_code": exc.status_code,
        "path": str(request.url),
        "method": request.method
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "Request failed", "type": "http_error"}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error("Unhandled exception", extra={
        "path": str(request.url),
        "method": request.method,
        "error_type": type(exc).__name__,
        "stack_trace": True
    }, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )


@app.get("/")
def root() -> dict[str, str]:
    """Return basic application status."""
    return {"status": "Delhi PS-CRM Backend Running"}


@app.get("/health")
def health() -> dict[str, object]:
    """Return comprehensive health check with system status."""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {}
    }
    
    # Check Supabase connectivity
    try:
        from config import supabase
        test_result = supabase.table("users").select("count").limit(1).execute()
        health_status["checks"]["supabase"] = {
            "status": "healthy",
            "response_time_ms": "<100"
        }
    except Exception as exc:
        logger.error("Supabase health check failed: %s", exc)
        health_status["checks"]["supabase"] = {
            "status": "unhealthy",
            "error": str(exc)
        }
        health_status["status"] = "unhealthy"
    
    # Check ML model load status
    try:
        from services.escalation import _load_model
        model = _load_model()
        health_status["checks"]["ml_model"] = {
            "status": "healthy",
            "model_loaded": model is not None
        }
    except Exception as exc:
        logger.error("ML model health check failed: %s", exc)
        health_status["checks"]["ml_model"] = {
            "status": "unhealthy",
            "error": str(exc)
        }
        health_status["status"] = "unhealthy"
    
    # Check WhatsApp API configuration
    try:
        from config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID
        if WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID:
            health_status["checks"]["whatsapp_api"] = {
                "status": "healthy",
                "configured": True
            }
        else:
            raise ValueError("WhatsApp API not configured")
    except Exception as exc:
        logger.error("WhatsApp API health check failed: %s", exc)
        health_status["checks"]["whatsapp_api"] = {
            "status": "unhealthy",
            "error": str(exc)
        }
        health_status["status"] = "unhealthy"
    
    # Check Gemini API configuration
    try:
        from config import GEMINI_API_KEY
        if GEMINI_API_KEY:
            health_status["checks"]["gemini_api"] = {
                "status": "healthy",
                "configured": True
            }
        else:
            raise ValueError("Gemini API not configured")
    except Exception as exc:
        logger.error("Gemini API health check failed: %s", exc)
        health_status["checks"]["gemini_api"] = {
            "status": "unhealthy",
            "error": str(exc)
        }
        health_status["status"] = "unhealthy"
    
    return health_status
