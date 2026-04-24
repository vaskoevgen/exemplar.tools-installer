import logging
import os
import time
from dataclasses import dataclass, field
from typing import Optional, Any

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
# Types
# ---------------------------------------------------------------------------

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel, field_validator, ConfigDict

# Re-export HTTPException so tests can import it from this module
HTTPException = HTTPException

TaskId = int
TaskTitle = str


class DatabaseURL:
    """PostgreSQL connection string with validation."""
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("DATABASE_URL must not be empty")
        if not value.startswith("postgresql"):
            raise ValueError("DATABASE_URL must be a postgresql:// URI")
        self.value = value


CompletedFilter = Optional[bool]
Bool = bool
String = str
DateTime = str


class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    completed: bool
    created_at: Any  # datetime or string


class CreateTaskRequest(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError("Title must not be empty")
        if len(v) > 500:
            raise ValueError("Title must be at most 500 characters")
        return v


class UpdateTaskRequest(BaseModel):
    completed: bool


class ErrorResponse(BaseModel):
    detail: str


TaskList = list[Task]

# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------

_database_url: Optional[str] = None


def init_db(database_url: Optional[str] = None) -> None:
    """Connect to PostgreSQL and create the tasks table if it doesn't exist."""
    global _database_url

    if database_url is not None and database_url != "":
        url = database_url
    else:
        url = os.environ.get("DATABASE_URL", "")

    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    _database_url = url

    conn = psycopg2.connect(_database_url, cursor_factory=RealDictCursor)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.commit()
        cur.close()
    finally:
        conn.close()

    _log("info", "Database initialized successfully")


def get_db_connection() -> Any:
    """Return a new psycopg2 connection using the stored DATABASE_URL."""
    global _database_url
    url = _database_url or os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("Database connection unavailable.")
    conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
    return conn


# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------

def create_task(title: str) -> Task:
    """Insert a new task and return it."""
    if not title or len(title.strip()) == 0:
        raise ValueError("Title must not be empty")
    if len(title) > 500:
        raise ValueError("Title must be at most 500 characters")

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed, created_at",
            (title,)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        return Task(
            id=row["id"],
            title=row["title"],
            completed=row["completed"],
            created_at=row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
        )
    except psycopg2.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def list_tasks(completed: CompletedFilter = None) -> TaskList:
    """Return all tasks, optionally filtered by completed status."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if completed is None:
            cur.execute("SELECT id, title, completed, created_at FROM tasks ORDER BY id")
        else:
            cur.execute(
                "SELECT id, title, completed, created_at FROM tasks WHERE completed = %s ORDER BY id",
                (completed,)
            )
        rows = cur.fetchall()
        cur.close()
        result = []
        for r in rows:
            result.append(Task(
                id=r["id"],
                title=r["title"],
                completed=r["completed"],
                created_at=r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
            ))
        return result
    except psycopg2.Error:
        raise
    finally:
        conn.close()


def update_task(task_id: int, completed: bool) -> Optional[Task]:
    """Update the completed field of a task. Returns None if not found."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET completed = %s WHERE id = %s RETURNING id, title, completed, created_at",
            (completed, task_id)
        )
        row = cur.fetchone()
        conn.commit()
        cur.close()
        if row is None:
            return None
        return Task(
            id=row["id"],
            title=row["title"],
            completed=row["completed"],
            created_at=row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
        )
    except psycopg2.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_task(task_id: int) -> bool:
    """Delete a task by id. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        cur.close()
        return deleted
    except psycopg2.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# FastAPI app and handlers
# ---------------------------------------------------------------------------

app = FastAPI(title="Todo List")


@app.on_event("startup")
def startup_event() -> None:
    url = os.environ.get("DATABASE_URL", "")
    if url:
        try:
            init_db(url)
        except Exception as e:
            _log("error", f"Failed to initialize database: {e}")


def handle_serve_index() -> Any:
    """Serve static/index.html."""
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Frontend file not found.")
    return FileResponse(file_path, media_type="text/html")


def handle_create_task(body: CreateTaskRequest) -> Task:
    """POST /tasks handler."""
    return create_task(body.title)


def handle_list_tasks(completed: CompletedFilter = None) -> TaskList:
    """GET /tasks handler."""
    return list_tasks(completed)


def handle_update_task(task_id: int, body: UpdateTaskRequest) -> Task:
    """PATCH /tasks/{id} handler."""
    result = update_task(task_id, body.completed)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


def handle_delete_task(task_id: int) -> None:
    """DELETE /tasks/{id} handler."""
    deleted = delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


# Register routes
@app.get("/")
def route_index():
    return handle_serve_index()


@app.post("/tasks", status_code=201)
def route_create_task(body: CreateTaskRequest):
    return handle_create_task(body)


@app.get("/tasks")
def route_list_tasks(completed: Optional[bool] = Query(default=None)):
    return handle_list_tasks(completed)


@app.patch("/tasks/{task_id}")
def route_update_task(task_id: int, body: UpdateTaskRequest):
    return handle_update_task(task_id, body)


@app.delete("/tasks/{task_id}", status_code=204)
def route_delete_task(task_id: int):
    handle_delete_task(task_id)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    "Task",
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "ErrorResponse",
    "TaskList",
    "CompletedFilter",
    "init_db",
    "get_db_connection",
    "create_task",
    "list_tasks",
    "update_task",
    "delete_task",
    "handle_serve_index",
    "HTTPException",
    "handle_create_task",
    "handle_list_tasks",
    "handle_update_task",
    "handle_delete_task",
    "DatabaseURL",
    "TaskId",
    "TaskTitle",
    "app",
]
