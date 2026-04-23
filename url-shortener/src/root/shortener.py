import logging
import secrets
import time
from typing import Any, List, Optional

import psycopg2

import db
from config import get_config

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


class CodeCollisionError(Exception):
    """Raised when generate_code() fails to produce a unique short code after
    max_retries attempts. Mapped to HTTP 503 by the exception handler in main.py."""

    def __init__(self, attempts: int, message: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        if not isinstance(attempts, int) or attempts < 1 or attempts > 5:
            raise ValueError(f"attempts must be in range 1..5, got {attempts}")
        self.attempts = attempts
        self.message = message
        super().__init__(message)


class ShortenResponse:
    """Response body for POST /shorten."""

    def __init__(self, short_url: str, code: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        self.short_url = short_url
        self.code = code

    def model_dump(self):
        return {"short_url": self.short_url, "code": self.code}


class LinkListItem:
    """Public-facing link summary returned in the GET /links JSON array."""

    def __init__(self, code: str, original_url: str, created_at: Any, hit_count: int,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        self.code = code
        self.original_url = original_url
        self.created_at = created_at
        self.hit_count = hit_count

    def model_dump(self):
        created_at_val = self.created_at
        if hasattr(created_at_val, 'isoformat'):
            created_at_val = created_at_val.isoformat()
        return {
            "code": self.code,
            "original_url": self.original_url,
            "created_at": created_at_val,
            "hit_count": self.hit_count,
        }


def generate_code() -> str:
    """
    Generates a 6-character URL-safe short code using secrets.token_urlsafe(4)[:6].
    """
    return secrets.token_urlsafe(4)[:6]


def shorten_url(original_url: str) -> ShortenResponse:
    """
    Shortens a URL. If the original_url already exists in the links table,
    returns the existing code (idempotent). Otherwise generates a new short
    code, inserts the row, and returns the ShortenResponse. Retries up to
    5 times on short_code collision.
    """
    _log("info", f"shorten_url called")
    cfg = get_config()

    # Check if URL already exists
    existing = db.execute_one(
        "SELECT short_code FROM links WHERE original_url = %s",
        (original_url,)
    )
    if existing:
        code = existing["short_code"]
        short_url = f"{cfg.base_url}/{code}"
        return ShortenResponse(short_url=short_url, code=code)

    max_retries = cfg.max_code_retries
    for attempt in range(1, max_retries + 1):
        code = generate_code()
        try:
            row = db.execute_one(
                "INSERT INTO links (short_code, original_url) VALUES (%s, %s) "
                "RETURNING short_code, original_url",
                (code, original_url)
            )
            if row:
                short_url = f"{cfg.base_url}/{row['short_code']}"
                return ShortenResponse(short_url=short_url, code=row["short_code"])
        except psycopg2.errors.UniqueViolation:
            _log("warning", f"Code collision on attempt {attempt}: {code}")
            # Check if it was a collision on original_url (concurrent insert)
            existing = db.execute_one(
                "SELECT short_code FROM links WHERE original_url = %s",
                (original_url,)
            )
            if existing:
                code = existing["short_code"]
                short_url = f"{cfg.base_url}/{code}"
                return ShortenResponse(short_url=short_url, code=code)
            if attempt == max_retries:
                raise CodeCollisionError(
                    attempts=max_retries,
                    message=f"Failed to generate a unique short code after {max_retries} attempts."
                )
            continue

    raise CodeCollisionError(
        attempts=max_retries,
        message=f"Failed to generate a unique short code after {max_retries} attempts."
    )


def resolve_and_track(code: str) -> Optional[str]:
    """
    Resolves a short code to its original URL and atomically increments hit_count.
    """
    _log("info", f"resolve_and_track called for code={code}")
    row = db.execute_one(
        "UPDATE links SET hit_count = hit_count + 1 WHERE short_code = %s RETURNING original_url",
        (code,)
    )
    if row:
        return row["original_url"]
    return None


def list_links() -> List[LinkListItem]:
    """
    Returns all link records ordered by created_at descending.
    """
    _log("info", "list_links called")
    rows = db.execute(
        "SELECT short_code, original_url, created_at, hit_count "
        "FROM links ORDER BY created_at DESC"
    )
    return [
        LinkListItem(
            code=row["short_code"],
            original_url=row["original_url"],
            created_at=row["created_at"],
            hit_count=row["hit_count"],
        )
        for row in rows
    ]
