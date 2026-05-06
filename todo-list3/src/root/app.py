"""FastAPI application factory for the Task Management backend."""
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    TaskCreateModel,
    TaskUpdateModel,
    TaskResponseModel,
    HealthResponseModel,
    DeleteConfirmationModel,
)
from db import init_pool, close_pool, get_pool

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize connection pool on startup, close on shutdown."""
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        _log("error", "DATABASE_URL not set")
        raise RuntimeError("DATABASE_URL environment variable is required")
    _log("info", "Initializing connection pool")
    init_pool(database_url)
    yield
    _log("info", "Closing connection pool")
    close_pool()


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(title="Task Management API", lifespan=lifespan)

    frontend_origin = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Import and include routes
    from routes import router
    app.include_router(router)

    return app


app = create_app()
