import logging
import os
import time
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator, ConfigDict

import shortener
import db

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
# Path configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = str(BASE_DIR / "static")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ShortenRequest(BaseModel):
    """Request body for POST /shorten containing the original long URL to shorten."""
    model_config = ConfigDict(strict=False)
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_nonempty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("url must not be empty")
        return v


class ShortenResponse(BaseModel):
    """Response body for POST /shorten."""
    short_url: str
    code: str


class LinkListItem(BaseModel):
    """Public projection of a link record returned in GET /links JSON array."""
    code: str
    original_url: str
    created_at: str
    hit_count: int


# Type alias
LinkList = List[LinkListItem]


class LinkRecord(BaseModel):
    """A single shortened-link record as stored in the database."""
    id: int
    short_code: str
    original_url: str
    created_at: str
    hit_count: int

    @field_validator("short_code")
    @classmethod
    def short_code_length(cls, v: str) -> str:
        if len(v) != 6:
            raise ValueError("short_code must be exactly 6 characters")
        return v

    @field_validator("hit_count")
    @classmethod
    def hit_count_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("hit_count must be non-negative")
        return v


class ErrorDetail(BaseModel):
    """Standard error response body."""
    detail: str


from enum import Enum


class MaxRetriesExhaustedCode(Enum):
    """Enum for short-code generation failure modes."""
    COLLISION_LIMIT_REACHED = "COLLISION_LIMIT_REACHED"


class AppConfig(BaseModel):
    """Application configuration read from environment variables."""
    database_url: str
    base_url: str = "http://localhost:8000"

    @field_validator("database_url")
    @classmethod
    def database_url_must_start_with_postgresql(cls, v: str) -> str:
        if not v.startswith("postgresql://"):
            raise ValueError("database_url must start with postgresql://")
        return v


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI()


# ---------------------------------------------------------------------------
# Routes — order matters: /links and / before /{code}
# ---------------------------------------------------------------------------


@app.get("/")
def route_index():
    """GET / — serves static/index.html via FileResponse."""
    _log("debug", "route_index invoked")
    index_path = Path(BASE_DIR) / "static" / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="Index file not found.")
    return FileResponse(str(index_path), media_type="text/html")


@app.get("/links")
def route_list_links():
    """GET /links — returns JSON array of all links."""
    _log("debug", "route_list_links invoked")
    try:
        links = shortener.list_links()
    except Exception as e:
        _log("error", f"Database error during link listing: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    _log("debug", "route_list_links completed")
    return links


@app.post("/shorten")
def route_shorten(body: ShortenRequest):
    """POST /shorten — accepts ShortenRequest JSON body, returns ShortenResponse."""
    _log("debug", f"route_shorten invoked for url={body.url}")
    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    try:
        result = shortener.shorten_url(body.url, base_url)
    except RuntimeError as e:
        _log("error", f"Max retries exhausted: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not generate a unique short code after 5 attempts."
        )
    except Exception as e:
        _log("error", f"Database error during shorten: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    _log("debug", "route_shorten completed")
    return result


@app.get("/{code}")
def route_redirect(code: str):
    """GET /{code} — resolves short code, returns 307 redirect or 404."""
    _log("debug", f"route_redirect invoked for code={code}")
    try:
        original_url = shortener.get_link(code)
    except Exception as e:
        _log("error", f"Database error during redirect: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    if original_url is None:
        raise HTTPException(status_code=404, detail="Short link not found.")
    _log("debug", f"route_redirect completed: redirecting to {original_url}")
    return RedirectResponse(url=original_url, status_code=307)


# Mount static files after routes so routes take priority
try:
    if Path(STATIC_DIR).exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    pass


# Re-export all required names at module level for test imports
# (They are already defined above, this comment documents the exports)
# ShortenRequest, ShortenResponse, LinkRecord, LinkListItem, LinkList,
# ErrorDetail, MaxRetriesExhaustedCode, AppConfig, HTTPException,
# route_index, route_shorten, route_redirect, route_list_links
# The functions get_database_url, get_conn, generate_code, shorten_url,
# get_link, list_links are in their respective modules.
