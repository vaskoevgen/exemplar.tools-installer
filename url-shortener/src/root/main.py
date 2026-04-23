import logging
import os
import time
from enum import Enum
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from pydantic import BaseModel, field_validator

import db
import shortener
from config import AppConfig, get_config
from shortener import (
    CodeCollisionError,
    LinkListItem,
    ShortenResponse as _InternalShortenResponse,
)

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ---------------------------------------------------------------------------
# Pydantic models for request/response serialization
# ---------------------------------------------------------------------------


class ShortenRequest(BaseModel):
    """Request body for POST /shorten containing the long URL to shorten."""
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v or not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("url must be a valid HTTP or HTTPS URL")
        return v


class ShortenResponseModel(BaseModel):
    """Response body for POST /shorten."""
    short_url: str
    code: str


class LinkListItemModel(BaseModel):
    """Public-facing link summary for GET /links."""
    code: str
    original_url: str
    created_at: Any
    hit_count: int


class ErrorResponse(BaseModel):
    """Standard JSON error body returned for 4xx/5xx responses."""
    detail: str


class HttpMethod(str, Enum):
    """HTTP methods used by the API routes."""
    GET = "GET"
    POST = "POST"


# Re-export contract names at module level
ShortenResponse = _InternalShortenResponse

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI()


# ---------------------------------------------------------------------------
# Exception handler for CodeCollisionError -> 503
# ---------------------------------------------------------------------------

@app.exception_handler(CodeCollisionError)
async def code_collision_handler(request: Request, exc: CodeCollisionError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Failed to generate a unique short code. Try again later."},
    )


# ---------------------------------------------------------------------------
# Lifecycle events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup_event() -> None:
    """Verify DB connectivity on startup."""
    _log("info", "Application startup: verifying database connection.")
    conn = db.get_conn()
    _log("info", "Database connection verified. Application ready.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Close DB connection on shutdown."""
    _log("info", "Application shutdown: closing database connection.")
    db.close_conn()


# ---------------------------------------------------------------------------
# Routes — order matters! Static/literal routes before path parameter routes.
# ---------------------------------------------------------------------------

@app.get("/")
async def get_index() -> Any:
    """Serves static/index.html as a FileResponse with content-type text/html."""
    _log("info", "GET / called")
    index_path = os.path.join("static", "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Index file not found.")
    return FileResponse(index_path, media_type="text/html")


@app.get("/links")
async def get_links() -> Any:
    """Returns a JSON array of all link records."""
    _log("info", "GET /links called")
    try:
        items = shortener.list_links()
        return [item.model_dump() if hasattr(item, 'model_dump') else item for item in items]
    except Exception:
        _log("error", "Database error during link listing.")
        raise HTTPException(status_code=500, detail="Internal server error.")


@app.get("/{code}")
async def get_redirect(code: str) -> Any:
    """Resolves a short code and returns 307 redirect."""
    _log("info", f"GET /{code} called")
    original_url = shortener.resolve_and_track(code)
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short link not found.")
    return RedirectResponse(url=original_url, status_code=307)


@app.post("/shorten")
async def post_shorten(body: ShortenRequest) -> Any:
    """Accepts a JSON body with a URL, delegates to shortener.shorten_url()."""
    _log("info", "POST /shorten called")
    result = shortener.shorten_url(body.url)
    return result.model_dump()


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "AppConfig",
    "ShortenRequest",
    "ShortenResponse",
    "LinkListItem",
    "ErrorResponse",
    "CodeCollisionError",
    "HttpMethod",
]
