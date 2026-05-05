import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

import psycopg2
import psycopg2.extras
import psycopg2.pool

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


# Module-level pool reference
pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def init_connection_pool(
    database_url: str,
    minconn: int = 1,
    maxconn: int = 10,
) -> None:
    """Initialize the psycopg2.pool.ThreadedConnectionPool."""
    global pool
    _log("info", f"Initializing connection pool minconn={minconn} maxconn={maxconn}")
    try:
        pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=database_url,
        )
    except Exception as e:
        _log("error", f"Failed to initialize connection pool: {e}")
        pool = None
        raise RuntimeError(f"Failed to connect to PostgreSQL: {e}") from e
    _log("info", "Connection pool initialized successfully")


def close_connection_pool() -> None:
    """Close all pooled connections."""
    global pool
    _log("info", "Closing connection pool")
    if pool is not None:
        try:
            pool.closeall()
        except Exception as e:
            _log("error", f"Error closing pool: {e}")
        pool = None
    _log("info", "Connection pool closed")


@contextmanager
def get_connection() -> Generator[Any, None, None]:
    """Context manager that borrows a connection from the pool."""
    global pool
    if pool is None:
        raise RuntimeError("Connection pool not initialized")
    conn = None
    try:
        conn = pool.getconn()
    except Exception as e:
        raise RuntimeError(f"Connection pool exhausted: {e}") from e
    try:
        yield conn
        conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            pool.putconn(conn)


def db_list_tasks() -> List[Dict[str, Any]]:
    """SELECT * FROM tasks ORDER BY created_at DESC."""
    _log("debug", "db_list_tasks called")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def db_create_task(
    title: str,
    description: Optional[str],
    status: str,
) -> Dict[str, Any]:
    """INSERT INTO tasks ... RETURNING *."""
    _log("debug", f"db_create_task title={title!r} status={status!r}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING *",
                (title, description, status),
            )
            row = cur.fetchone()
    return dict(row)


def db_get_task(task_id: str) -> Optional[Dict[str, Any]]:
    """SELECT * FROM tasks WHERE id = %s."""
    _log("debug", f"db_get_task task_id={task_id!r}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)


def db_update_task(
    task_id: str,
    fields: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Dynamic UPDATE SET from fields dict. Always updates updated_at=NOW()."""
    _log("debug", f"db_update_task task_id={task_id!r} fields={fields!r}")
    if not fields:
        # Even with no user fields, still update updated_at
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "UPDATE tasks SET updated_at = NOW() WHERE id = %s RETURNING *",
                    (task_id,),
                )
                row = cur.fetchone()
        if row is None:
            return None
        return dict(row)

    set_clauses = []
    values = []
    for key, value in fields.items():
        set_clauses.append(f"{key} = %s")
        values.append(value)
    set_clauses.append("updated_at = NOW()")
    set_clause_str = ", ".join(set_clauses)
    values.append(task_id)

    query = f"UPDATE tasks SET {set_clause_str} WHERE id = %s RETURNING *"

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, tuple(values))
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)


def db_delete_task(task_id: str) -> Optional[Dict[str, Any]]:
    """DELETE FROM tasks WHERE id = %s RETURNING id."""
    _log("debug", f"db_delete_task task_id={task_id!r}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)
