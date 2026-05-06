"""PostgreSQL Database Schema component.

Provides idempotent SQL init script execution, schema verification,
and validated domain types for the tasks table.
"""

import logging
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

_PACT_KEY = "PACT:3549b0:database"
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
# Custom Error Classes
# ---------------------------------------------------------------------------

class ConnectionError(Exception):
    """PostgreSQL server is not running or not reachable."""
    pass


class AuthenticationError(Exception):
    """Credentials in DATABASE_URL are invalid."""
    pass


class DatabaseNotFoundError(Exception):
    """The database name in DATABASE_URL does not exist on the server."""
    pass


class SQLSyntaxError(Exception):
    """The init.sql script contains a syntax error."""
    pass


# ---------------------------------------------------------------------------
# Domain Types
# ---------------------------------------------------------------------------

class TaskStatus(Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


@dataclass(frozen=True)
class TaskTitle:
    """The title column of the tasks table. VARCHAR(255) NOT NULL. Length 1..255."""
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError(f"TaskTitle value must be a str, got {type(self.value).__name__}")
        if len(self.value) < 1:
            raise ValueError("TaskTitle must be at least 1 character long")
        if len(self.value) > 255:
            raise ValueError(f"TaskTitle must be at most 255 characters, got {len(self.value)}")


# TaskDescription is just a type alias
TaskDescription = Optional[str]

# TaskId is an int surrogate key
TaskId = int


# Timestamptz regex: ISO 8601 with mandatory T separator and timezone
_TIMESTAMPTZ_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class Timestamptz:
    """TIMESTAMPTZ column type. Accepts ISO 8601 with timezone."""
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise ValueError(f"Timestamptz value must be str, got {type(self.value).__name__}")
        if not _TIMESTAMPTZ_RE.match(self.value):
            raise ValueError(
                f"Timestamptz value must be ISO 8601 with timezone (e.g. 2024-01-01T00:00:00Z), got: {self.value!r}"
            )


@dataclass
class TaskRow:
    """Represents a single row in the tasks table."""
    id: TaskId
    title: str
    description: TaskDescription = None
    status: TaskStatus = TaskStatus.pending
    created_at: object = None  # datetime.datetime at runtime
    updated_at: object = None  # datetime.datetime at runtime


@dataclass(frozen=True)
class ConnectionConfig:
    """PostgreSQL connection parameters."""
    database_url: str
    port: int

    def __post_init__(self) -> None:
        if not isinstance(self.database_url, str):
            raise ValueError("database_url must be a string")
        if not self.database_url.startswith("postgresql://"):
            raise ValueError(
                f"database_url must start with 'postgresql://', got: {self.database_url!r}"
            )
        if self.port != 5432:
            raise ValueError(f"port must be exactly 5432, got {self.port}")


@dataclass
class InitScriptResult:
    """Result of executing the init.sql script."""
    table_created: bool
    trigger_created: bool
    check_constraint_present: bool


# ---------------------------------------------------------------------------
# SQL Init Script (inline, idempotent)
# ---------------------------------------------------------------------------

_INIT_SQL = """
-- Idempotent init script for 'tasks' table
-- Safe to re-execute: uses IF NOT EXISTS, OR REPLACE, DO blocks

-- 1. Create the tasks table if it does not exist
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Add CHECK constraint on status if not already present
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        WHERE t.relname = 'tasks'
          AND c.contype = 'c'
          AND pg_get_constraintdef(c.oid) LIKE '%status%'
    ) THEN
        ALTER TABLE tasks
            ADD CONSTRAINT tasks_status_check
            CHECK (status IN ('pending', 'in_progress', 'done'));
    END IF;
END
$$;

-- 3. Create or replace the trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Create trigger if not exists (using DO block for idempotency)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
        WHERE pg_class.relname = 'tasks'
          AND pg_trigger.tgname = 'set_updated_at'
    ) THEN
        CREATE TRIGGER set_updated_at
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;
"""


# ---------------------------------------------------------------------------
# Helper: connect with classified error handling
# ---------------------------------------------------------------------------

def _connect(database_url: str):
    """Open a psycopg2 connection, translating errors to domain exceptions."""
    import psycopg2
    import psycopg2.errors

    try:
        conn = psycopg2.connect(database_url, connect_timeout=5)
        return conn
    except psycopg2.OperationalError as e:
        err_msg = str(e).lower()
        if "password authentication failed" in err_msg or "authentication failed" in err_msg:
            raise AuthenticationError(str(e)) from e
        if "does not exist" in err_msg and "database" in err_msg:
            raise DatabaseNotFoundError(str(e)) from e
        # Default: connection refused / unreachable
        raise ConnectionError(str(e)) from e
    except Exception as e:
        raise ConnectionError(str(e)) from e


# ---------------------------------------------------------------------------
# Public Functions
# ---------------------------------------------------------------------------

def execute_init_script(
    connection_config: ConnectionConfig,
    event_handler=None,
    log_handler=None,
) -> InitScriptResult:
    """Execute the idempotent init.sql script against the target PostgreSQL database."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:3549b0:database:execute_init_script",
        "event": "invoked",
        "input_classification": ["connection_config"],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "Executing init script")

    conn = _connect(connection_config.database_url)
    try:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(_INIT_SQL)
        cur.close()
    except Exception as e:
        conn.close()
        err_msg = str(e).lower()
        if "syntax" in err_msg:
            raise SQLSyntaxError(str(e)) from e
        if "permission" in err_msg or "privilege" in err_msg:
            raise PermissionError(str(e)) from e
        raise
    finally:
        if not conn.closed:
            conn.close()

    # Verify the result
    result = verify_schema(connection_config)

    _emit({
        "pact_key": "PACT:3549b0:database:execute_init_script",
        "event": "completed",
        "input_classification": ["connection_config"],
        "output_classification": ["init_script_result"],
        "side_effects": ["schema_modified"],
        "ts": time.time_ns(),
    })

    _log("info", f"Init script completed: table={result.table_created}, trigger={result.trigger_created}, check={result.check_constraint_present}")

    return result


def verify_schema(
    connection_config: ConnectionConfig,
    event_handler=None,
    log_handler=None,
) -> InitScriptResult:
    """Verify the schema by introspecting information_schema and pg_catalog."""
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:3549b0:database:verify_schema",
        "event": "invoked",
        "input_classification": ["connection_config"],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "Verifying schema")

    conn = _connect(connection_config.database_url)
    try:
        conn.autocommit = True
        cur = conn.cursor()

        # 1. Check table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'tasks'
                  AND table_schema = 'public'
            )
        """)
        table_exists = cur.fetchone()[0]

        # 2. Check trigger exists
        trigger_exists = False
        if table_exists:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_trigger
                    JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
                    WHERE pg_class.relname = 'tasks'
                      AND pg_trigger.tgname = 'set_updated_at'
                      AND NOT pg_trigger.tgisinternal
                )
            """)
            trigger_exists = cur.fetchone()[0]

        # Also check the trigger function exists
        if trigger_exists:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_proc
                    WHERE proname = 'update_updated_at_column'
                )
            """)
            trigger_func_exists = cur.fetchone()[0]
            trigger_exists = trigger_exists and trigger_func_exists

        # 3. Check CHECK constraint
        check_present = False
        if table_exists:
            cur.execute("""
                SELECT pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_class t ON c.conrelid = t.oid
                WHERE t.relname = 'tasks' AND c.contype = 'c'
            """)
            rows = cur.fetchall()
            for row in rows:
                defn = row[0]
                if 'pending' in defn and 'in_progress' in defn and 'done' in defn:
                    check_present = True
                    break

        cur.close()
    finally:
        if not conn.closed:
            conn.close()

    result = InitScriptResult(
        table_created=table_exists,
        trigger_created=trigger_exists,
        check_constraint_present=check_present,
    )

    _emit({
        "pact_key": "PACT:3549b0:database:verify_schema",
        "event": "completed",
        "input_classification": ["connection_config"],
        "output_classification": ["init_script_result"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", f"Schema verification: table={result.table_created}, trigger={result.trigger_created}, check={result.check_constraint_present}")

    return result


# ---------------------------------------------------------------------------
# Required exports
# ---------------------------------------------------------------------------

__all__ = [
    'TaskStatus',
    'TaskDescription',
    'TaskRow',
    'ConnectionConfig',
    'InitScriptResult',
    'execute_init_script',
    'ConnectionError',
    'AuthenticationError',
    'DatabaseNotFoundError',
    'SQLSyntaxError',
    'verify_schema',
]
