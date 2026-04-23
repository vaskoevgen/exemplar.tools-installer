import logging
import re
import secrets
import time
from typing import Optional, List, Dict, Any

import psycopg2
try:
    from psycopg2.errors import UniqueViolation
except ImportError:
    UniqueViolation = psycopg2.IntegrityError

from db import get_conn

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
# Bespoke primitive types with validation
# ---------------------------------------------------------------------------

class OriginalUrl:
    """A validated URL string representing the long URL to be shortened."""
    _PATTERN = re.compile(r'^https?://\S+$')
    _MAX_LENGTH = 2048

    def __init__(self, value: str):
        if not value:
            raise ValueError("OriginalUrl must not be empty")
        if len(value) > self._MAX_LENGTH:
            raise ValueError(f"OriginalUrl exceeds maximum length of {self._MAX_LENGTH}")
        if not self._PATTERN.match(value):
            raise ValueError(f"OriginalUrl must match pattern {self._PATTERN.pattern}")
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"OriginalUrl(value={self.value!r})"


class HitCount:
    """Non-negative integer tracking the number of times a short link has been accessed."""

    def __init__(self, value: int):
        if not isinstance(value, int):
            raise TypeError("HitCount must be an integer")
        if value < 0:
            raise ValueError("HitCount must be non-negative")
        self.value = value

    def __repr__(self) -> str:
        return f"HitCount(value={self.value})"


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def generate_code() -> str:
    """
    Generates a 6-character URL-safe short code using secrets.token_urlsafe(4)[:6].
    """
    code = secrets.token_urlsafe(4)[:6]
    return code


def shorten_url(original_url: str, base_url: str) -> dict:
    """
    Shortens a URL. If the URL already exists, returns the existing record's code.
    Otherwise generates a new short code, inserts it, and returns the result.
    Retries up to 5 times on short_code collision (UniqueViolation on short_code).
    """
    _log("debug", f"shorten_url invoked for {original_url}")
    conn = get_conn()
    try:
        for attempt in range(5):
            code = generate_code()
            with conn.cursor() as cur:
                # Check if URL already exists
                cur.execute(
                    "SELECT short_code FROM links WHERE original_url = %s",
                    (original_url,)
                )
                existing = cur.fetchone()
                if existing:
                    existing_code = existing["short_code"]
                    _log("debug", f"URL already exists with code {existing_code}")
                    return {
                        "short_url": f"{base_url}/{existing_code}",
                        "code": existing_code,
                    }
                try:
                    cur.execute(
                        "INSERT INTO links (short_code, original_url) VALUES (%s, %s)",
                        (code, original_url)
                    )
                    conn.commit()
                    _log("debug", f"shorten_url completed with code {code}")
                    return {
                        "short_url": f"{base_url}/{code}",
                        "code": code,
                    }
                except UniqueViolation:
                    conn.rollback()
                    _log("warning", f"Collision on attempt {attempt + 1} for code {code}")
                    continue
        raise RuntimeError("Could not generate a unique short code after 5 attempts")
    finally:
        conn.close()


def get_link(code: str) -> Optional[str]:
    """
    Resolves a short code to its original URL.
    Atomically increments hit_count and returns the URL, or None if not found.
    """
    _log("debug", f"get_link invoked for code {code}")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE links SET hit_count = hit_count + 1 WHERE short_code = %s RETURNING original_url",
                (code,)
            )
            row = cur.fetchone()
            conn.commit()
            if row:
                _log("debug", f"get_link completed: found {row['original_url']}")
                return row["original_url"]
            _log("debug", "get_link completed: code not found")
            return None
    finally:
        conn.close()


def list_links() -> list:
    """
    Returns all rows from the links table as a list of dicts,
    ordered by created_at descending.
    """
    _log("debug", "list_links invoked")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT short_code AS code, original_url, created_at, hit_count "
                "FROM links ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
        _log("debug", f"list_links completed: {len(rows)} rows")
        result = []
        for row in rows:
            item = dict(row)
            # Ensure created_at is serializable
            if hasattr(item.get("created_at"), "isoformat"):
                item["created_at"] = item["created_at"].isoformat()
            result.append(item)
        return result
    finally:
        conn.close()
