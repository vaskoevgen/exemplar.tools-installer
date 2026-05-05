import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan: initialize connection pool on startup, close on shutdown."""
    from backend.db import init_connection_pool, close_connection_pool
    database_url = os.environ.get("DATABASE_URL", "")
    if database_url:
        _log("info", "Starting connection pool")
        try:
            init_connection_pool(database_url)
        except Exception as e:
            _log("error", f"Failed to initialize pool: {e}")
    else:
        _log("warning", "DATABASE_URL not set, skipping pool initialization")
    yield
    _log("info", "Shutting down connection pool")
    close_connection_pool()


app = FastAPI(title="Task Management API", lifespan=lifespan)

# CORS middleware
frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
from backend.routes import router
app.include_router(router)
