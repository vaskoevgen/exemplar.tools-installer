import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db import close_connection_pool, init_connection_pool
from backend.routes import router

_PACT_KEY = "PACT:10e08a:backend"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Lifespan context manager: init pool on startup, close on shutdown."""
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url:
        try:
            init_connection_pool(database_url)
            _log("info", "Connection pool initialized during startup")
        except Exception as e:
            _log("error", f"Failed to init pool: {e}")
    else:
        _log("warning", "DATABASE_URL not set; skipping pool initialization")
    yield
    close_connection_pool()
    _log("info", "Connection pool closed during shutdown")


app = FastAPI(title="Task Management API", lifespan=lifespan)

# CORS middleware
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(router)
