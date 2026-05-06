"""Database connection pool and query helpers using psycopg2."""
import logging
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

import psycopg2
import psycopg2.pool
import psycopg2.extras

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# Module-level pool reference (set during lifespan, not at import time)
_pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None


def init_pool(database_url: str, minconn: int = 2, maxconn: int = 10) -> None:
    """Initialize the ThreadedConnectionPool. Called during FastAPI lifespan startup."""
    global _pool
    _log("info", f"Initializing connection pool (min={minconn}, max={maxconn})")
    _pool = psycopg2.pool.ThreadedConnectionPool(
        minconn, maxconn, database_url
    )


def close_pool() -> None:
    """Close the ThreadedConnectionPool. Called during FastAPI lifespan shutdown."""
    global _pool
    if _pool is not None:
        _log("info", "Closing connection pool")
        _pool.closeall()
        _pool = None


def get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    """Return the current pool. Raises if not initialized."""
    if _pool is None:
        raise RuntimeError("Connection pool not initialized")
    return _pool


@contextmanager
def get_connection():
    """Context manager: get connection from pool, return on exit."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def db_list_tasks() -> List[Dict[str, Any]]:
    """SELECT all tasks ordered by created_at DESC."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, description, status, created_at, updated_at "
                "FROM tasks ORDER BY created_at DESC;"
            )
            rows = cur.fetchall()
    return [dict(r) for r in rows]


def db_create_task(title: str, description: Optional[str],
                   status: str) -> Dict[str, Any]:
    """INSERT a new task and return the created row."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "INSERT INTO tasks (title, description, status) "
                "VALUES (%s, %s, %s) "
                "RETURNING id, title, description, status, created_at, updated_at;",
                (title, description, status),
            )
            row = cur.fetchone()
            conn.commit()
    return dict(row)


def db_get_task(task_id: int) -> Optional[Dict[str, Any]]:
    """SELECT a single task by id. Returns None if not found."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, title, description, status, created_at, updated_at "
                "FROM tasks WHERE id = %s;",
                (task_id,),
            )
            row = cur.fetchone()
    return dict(row) if row else None


def db_update_task(task_id: int, fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """UPDATE only provided fields (PATCH semantics). Returns updated row or None."""
    if not fields:
        return db_get_task(task_id)

    set_clauses = []
    values = []
    for key, val in fields.items():
        if key == "created_at":
            continue  # Never update created_at
        set_clauses.append(f"{key} = %s")
        values.append(val)

    # Always refresh updated_at as defense-in-depth
    set_clauses.append("updated_at = NOW()")

    if not set_clauses:
        return db_get_task(task_id)

    sql = (
        f"UPDATE tasks SET {', '.join(set_clauses)} "
        f"WHERE id = %s "
        f"RETURNING id, title, description, status, created_at, updated_at;"
    )
    values.append(task_id)

    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, tuple(values))
            row = cur.fetchone()
            conn.commit()
    return dict(row) if row else None


def db_delete_task(task_id: int) -> Optional[Dict[str, Any]]:
    """DELETE a task by id. Returns the deleted row or None."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s "
                "RETURNING id, title, description, status, created_at, updated_at;",
                (task_id,),
            )
            row = cur.fetchone()
            conn.commit()
    return dict(row) if row else None
