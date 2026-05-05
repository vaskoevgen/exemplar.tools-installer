"""Schema initialization and verification for the database component."""
from __future__ import annotations

import time
import logging
from typing import TYPE_CHECKING

import psycopg2
import psycopg2.errorcodes

from database.types import ConnectionConfig, InitScriptResult
from database.errors import (
    ConnectionError as DBConnectionError,
    AuthenticationError,
    DatabaseNotFoundError,
    SQLSyntaxError,
)

_PACT_KEY = "PACT:3549b0:database"
logger = logging.getLogger(__name__)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ---------------------------------------------------------------------------
# Idempotent init SQL
# ---------------------------------------------------------------------------

INIT_SQL = """
-- Create tasks table if it does not exist
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add CHECK constraint on status column (idempotent via DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.constraint_column_usage
        WHERE table_name = 'tasks'
          AND constraint_name = 'tasks_status_check'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
            CHECK (status IN ('pending', 'in_progress', 'done'));
    END IF;
END
$$;

-- Create or replace trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger if not exists (idempotent via DO block)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'set_updated_at'
          AND tgrelid = 'tasks'::regclass
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
# Error classification helper
# ---------------------------------------------------------------------------

def _classify_and_raise(exc: Exception) -> None:
    """Inspect a psycopg2 exception and re-raise as a domain error."""
    msg = str(exc).lower()

    # psycopg2 OperationalError covers connection, auth, and db-not-found
    if isinstance(exc, psycopg2.OperationalError):
        pgcode = getattr(exc, 'pgcode', None)
        if pgcode == psycopg2.errorcodes.INVALID_PASSWORD:  # 28P01
            raise AuthenticationError(str(exc)) from exc
        if pgcode == psycopg2.errorcodes.INVALID_CATALOG_NAME:  # 3D000
            raise DatabaseNotFoundError(str(exc)) from exc
        # Heuristic fallbacks when pgcode is None
        if 'authentication' in msg or 'password' in msg:
            raise AuthenticationError(str(exc)) from exc
        if 'does not exist' in msg and 'database' in msg:
            raise DatabaseNotFoundError(str(exc)) from exc
        # Default: connection refused / unreachable
        raise DBConnectionError(str(exc)) from exc

    if isinstance(exc, psycopg2.ProgrammingError):
        pgcode = getattr(exc, 'pgcode', None)
        if pgcode == psycopg2.errorcodes.INSUFFICIENT_PRIVILEGE:  # 42501
            raise PermissionError(str(exc)) from exc
        if 'permission denied' in msg:
            raise PermissionError(str(exc)) from exc
        if 'syntax' in msg:
            raise SQLSyntaxError(str(exc)) from exc
        raise PermissionError(str(exc)) from exc

    # builtins that the test mock may raise directly
    if isinstance(exc, builtins_ConnectionError):
        raise DBConnectionError(str(exc)) from exc
    if isinstance(exc, PermissionError):
        raise PermissionError(str(exc)) from exc

    raise DBConnectionError(str(exc)) from exc


import builtins as _builtins
builtins_ConnectionError = _builtins.ConnectionError


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_init_script(
    connection_config: ConnectionConfig,
    event_handler=None,
    log_handler=None,
) -> InitScriptResult:
    """
    Executes the idempotent init.sql script against the target PostgreSQL
    database.
    """
    _emit = event_handler or (lambda event: None)
    _logh = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:3549b0:database:execute_init_script",
        "event": "invoked",
        "input_classification": ["connection_config"],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "execute_init_script invoked")

    try:
        conn = psycopg2.connect(connection_config.database_url)
    except Exception as exc:
        _classify_and_raise(exc)

    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(INIT_SQL)
        result = InitScriptResult(
            table_created=True,
            trigger_created=True,
            check_constraint_present=True,
        )
    except Exception as exc:
        conn.close()
        _classify_and_raise(exc)
        # unreachable but satisfies type checker
        raise  # pragma: no cover
    finally:
        try:
            conn.close()
        except Exception:
            pass

    _emit({
        "pact_key": "PACT:3549b0:database:execute_init_script",
        "event": "completed",
        "input_classification": ["connection_config"],
        "output_classification": ["init_script_result"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "execute_init_script completed")
    return result


def verify_schema(
    connection_config: ConnectionConfig,
    event_handler=None,
    log_handler=None,
) -> InitScriptResult:
    """
    Read-only schema introspection to verify postconditions of
    execute_init_script.
    """
    _emit = event_handler or (lambda event: None)
    _logh = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:3549b0:database:verify_schema",
        "event": "invoked",
        "input_classification": ["connection_config"],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "verify_schema invoked")

    try:
        conn = psycopg2.connect(connection_config.database_url)
    except Exception as exc:
        _classify_and_raise(exc)

    try:
        conn.autocommit = True
        with conn.cursor() as cur:
            # 1. Check table exists
            cur.execute(
                "SELECT EXISTS ("
                "  SELECT 1 FROM information_schema.tables "
                "  WHERE table_schema = 'public' AND table_name = 'tasks'"
                ")"
            )
            row = cur.fetchone()
            table_exists = bool(row and row[0])

            # 2. Check CHECK constraint
            cur.execute(
                "SELECT EXISTS ("
                "  SELECT 1 FROM information_schema.table_constraints "
                "  WHERE table_name = 'tasks' "
                "    AND constraint_type = 'CHECK' "
                "    AND constraint_name = 'tasks_status_check'"
                ")"
            )
            row = cur.fetchone()
            check_exists = bool(row and row[0])

            # 3. Check trigger
            cur.execute(
                "SELECT EXISTS ("
                "  SELECT 1 FROM pg_trigger "
                "  WHERE tgname = 'set_updated_at' "
                "    AND tgrelid = 'tasks'::regclass"
                ")"
            )
            row = cur.fetchone()
            trigger_exists = bool(row and row[0])

    except Exception as exc:
        conn.close()
        _classify_and_raise(exc)
        raise  # pragma: no cover
    finally:
        try:
            conn.close()
        except Exception:
            pass

    result = InitScriptResult(
        table_created=table_exists,
        trigger_created=trigger_exists,
        check_constraint_present=check_exists,
    )

    _emit({
        "pact_key": "PACT:3549b0:database:verify_schema",
        "event": "completed",
        "input_classification": ["connection_config"],
        "output_classification": ["init_script_result"],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    _log("info", "verify_schema completed")
    return result
