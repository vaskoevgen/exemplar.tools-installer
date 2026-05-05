"""Database helper functions using parameterized queries (CROSS-TIER-08)."""
import logging
from typing import Any, Dict, List, Optional

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


def db_list_tasks(conn: Any) -> List[dict]:
    """Fetch all tasks ordered by created_at DESC (CROSS-TIER-01)."""
    _log("debug", "db_list_tasks")
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, title, description, status, created_at, updated_at "
            "FROM tasks ORDER BY created_at DESC"
        )
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        cur.close()


def db_create_task(conn: Any, title: str, description: Optional[str],
                   status: str) -> dict:
    """Insert a new task and return it."""
    _log("debug", f"db_create_task title={title}")
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO tasks (title, description, status) "
            "VALUES (%s, %s, %s) "
            "RETURNING id, title, description, status, created_at, updated_at",
            (title, description, status),
        )
        columns = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        conn.commit()
        return dict(zip(columns, row))
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def db_get_task(conn: Any, task_id: int) -> Optional[dict]:
    """Fetch a single task by id."""
    _log("debug", f"db_get_task id={task_id}")
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, title, description, status, created_at, updated_at "
            "FROM tasks WHERE id = %s",
            (task_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    finally:
        cur.close()


def db_update_task(conn: Any, task_id: int, fields: Dict[str, Any]) -> Optional[dict]:
    """Update specified fields only (CROSS-TIER-12 PATCH semantics).
    
    Never modifies created_at (CROSS-TIER-02).
    Always sets updated_at = NOW() as defense-in-depth (CROSS-TIER-03).
    """
    _log("debug", f"db_update_task id={task_id} fields={list(fields.keys())}")
    if not fields:
        # No fields to update, just return the current task
        return db_get_task(conn, task_id)

    # Build SET clause — only provided fields + updated_at
    set_parts = []
    params = []
    for key, value in fields.items():
        if key in ("created_at", "id"):
            continue
        set_parts.append(f"{key} = %s")
        params.append(value)

    # Defense-in-depth: always set updated_at
    set_parts.append("updated_at = NOW()")

    if not set_parts:
        return db_get_task(conn, task_id)

    params.append(task_id)
    query = (
        f"UPDATE tasks SET {', '.join(set_parts)} "
        f"WHERE id = %s "
        f"RETURNING id, title, description, status, created_at, updated_at"
    )

    cur = conn.cursor()
    try:
        cur.execute(query, tuple(params))
        row = cur.fetchone()
        conn.commit()
        if row is None:
            return None
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def db_delete_task(conn: Any, task_id: int) -> Optional[dict]:
    """Hard delete a task (CROSS-TIER-04)."""
    _log("debug", f"db_delete_task id={task_id}")
    cur = conn.cursor()
    try:
        cur.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id",
            (task_id,),
        )
        row = cur.fetchone()
        conn.commit()
        if row is None:
            return None
        return {"id": row[0]}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
