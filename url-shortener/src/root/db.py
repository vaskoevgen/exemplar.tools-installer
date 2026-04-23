import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import config

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


def get_conn():
    """
    Returns a new psycopg2 connection to PostgreSQL using DATABASE_URL from config.
    Connection uses RealDictCursor as default cursor factory.
    """
    _log("debug", "get_conn invoked")
    database_url = config.get_database_url()
    try:
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    except psycopg2.OperationalError as e:
        _log("error", f"Could not connect to PostgreSQL: {e}")
        raise
    _log("debug", "get_conn completed")
    return conn


def init_db():
    """Creates the links table if it doesn't exist."""
    _log("info", "init_db invoked")
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id SERIAL PRIMARY KEY,
                    short_code VARCHAR(6) NOT NULL UNIQUE,
                    original_url TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    hit_count INTEGER NOT NULL DEFAULT 0 CHECK (hit_count >= 0)
                );
            """)
        conn.commit()
    finally:
        conn.close()
    _log("info", "init_db completed")
