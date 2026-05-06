import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

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
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def init_connection_pool(
    database_url: str,
    minconn: int = 1,
    maxconn: int = 10,
) -> None:
    """Initialize the psycopg2 ThreadedConnectionPool."""
    global _pool
    _log("info", "Initializing connection pool")
    if not database_url or not database_url.startswith(("postgres://", "postgresql://")):
        raise RuntimeError(
            "DATABASE_URL environment variable is required and must be a valid PostgreSQL URI."
        )
    try:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn, maxconn, database_url
        )
    except psycopg2.Error as e:
        raise RuntimeError("Failed to connect to PostgreSQL.") from e

    # Ensure tasks table exists
    try:
        conn = _pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'in_progress', 'done')),
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                """)
            conn.commit()
        finally:
            _pool.putconn(conn)
    except psycopg2.Error as e:
        _log("error", f"Failed to create tasks table: {e}")

    _log("info", "Connection pool initialized")


def close_connection_pool() -> None:
    """Close the connection pool."""
    global _pool
    _log("info", "Closing connection pool")
    if _pool is not None:
        _pool.closeall()
        _pool = None
    _log("info", "Connection pool closed")


@contextmanager
def get_connection():
    """Context manager that borrows a connection from the pool."""
    global _pool
    if _pool is None:
        raise RuntimeError("Connection pool not initialized.")
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)


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
    _log("debug", f"db_create_task: title={title}, status={status}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING *",
                (title, description, status),
            )
            row = cur.fetchone()
    return dict(row)


def db_get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """SELECT * FROM tasks WHERE id = %s."""
    _log("debug", f"db_get_task: task_id={task_id}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)


def db_update_task(
    task_id: int,
    fields: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Dynamic UPDATE SET clause from fields dict. Always sets updated_at=NOW()."""
    _log("debug", f"db_update_task: task_id={task_id}, fields={fields}")
    allowed = {"title", "description", "status"}
    filtered = {k: v for k, v in fields.items() if k in allowed}

    set_clauses = []
    values = []
    for col, val in filtered.items():
        set_clauses.append(f"{col} = %s")
        if col == "status" and hasattr(val, 'value'):
            values.append(val.value)
        else:
            values.append(val)
    set_clauses.append("updated_at = NOW()")
    values.append(task_id)

    sql = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = %s RETURNING *"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, tuple(values))
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)


def db_delete_task(task_id: int) -> Optional[Dict[str, Any]]:
    """DELETE FROM tasks WHERE id = %s RETURNING id."""
    _log("debug", f"db_delete_task: task_id={task_id}")
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,)
            )
            row = cur.fetchone()
    if row is None:
        return None
    return dict(row)
