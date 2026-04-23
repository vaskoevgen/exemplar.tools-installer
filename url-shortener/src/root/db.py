import logging
from typing import Any, List, Dict, Optional, Tuple

import psycopg2
import psycopg2.extras

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


_conn: Optional[Any] = None


def get_conn() -> Any:
    """
    Returns a psycopg2 connection to PostgreSQL. Lazily initialises the
    connection on first call. Returns the existing connection on subsequent
    calls. Connection has autocommit=True.
    """
    global _conn
    if _conn is not None and not getattr(_conn, 'closed', 1):
        return _conn

    cfg = get_config()
    try:
        _conn = psycopg2.connect(cfg.database_url)
        _conn.autocommit = True
        _log("info", "PostgreSQL connection established.")
    except psycopg2.OperationalError:
        _log("error", "Could not connect to PostgreSQL at the configured DATABASE_URL.")
        raise
    return _conn


def execute(query: str, params: Any = ()) -> List[Dict[str, Any]]:
    """
    Executes a parameterised SQL query and returns all result rows as a list
    of dicts (via RealDictCursor). Returns an empty list for statements with
    no result set.
    """
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(query, params)
        try:
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        except psycopg2.ProgrammingError:
            # No result set (e.g. INSERT without RETURNING)
            return []


def execute_one(query: str, params: Any = ()) -> Optional[Dict[str, Any]]:
    """
    Executes a parameterised SQL query and returns the first row as a dict,
    or None if no rows are returned.
    """
    rows = execute(query, params)
    if rows:
        return rows[0]
    return None


def close_conn() -> None:
    """
    Closes the cached PostgreSQL connection if one is open. Safe to call
    multiple times.
    """
    global _conn
    if _conn is not None:
        try:
            _conn.close()
            _log("info", "PostgreSQL connection closed.")
        except Exception:
            pass
        _conn = None
