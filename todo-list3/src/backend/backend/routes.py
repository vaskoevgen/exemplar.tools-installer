import logging
import time
import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from backend.models import (
    DeleteConfirmation,
    HealthResponse,
    TaskCreateRequest,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from backend import db as db_module

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


router = APIRouter()


def _validate_uuid(id_str: str) -> str:
    """Validate that the string is a valid UUID. Raise 422 if not."""
    try:
        val = uuid.UUID(id_str)
        return str(val)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail="Invalid UUID format")


@router.get("/health", response_model=HealthResponse, status_code=200)
def health_check() -> HealthResponse:
    """GET /health — Returns {'status': 'ok'}."""
    _log("info", "PACT:10e08a:backend:health_check invoked")
    return HealthResponse(status="ok")


@router.get("/tasks", response_model=TaskListResponse, status_code=200)
def list_tasks() -> TaskListResponse:
    """GET /tasks — Returns all tasks ordered by created_at DESC."""
    _log("info", "PACT:10e08a:backend:list_tasks invoked")
    try:
        rows = db_module.db_list_tasks()
    except Exception as e:
        _log("error", f"Database error in list_tasks: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    result = [TaskResponse(**_row_to_response(row)) for row in rows]
    return result


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreateRequest) -> TaskResponse:
    """POST /tasks — Creates a new task."""
    _log("info", "PACT:10e08a:backend:create_task invoked")
    try:
        row = db_module.db_create_task(
            title=task.title,
            description=task.description,
            status=task.status if isinstance(task.status, str) else task.status,
        )
    except Exception as e:
        _log("error", f"Database error in create_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    return TaskResponse(**_row_to_response(row))


@router.get("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def get_task(task_id: str) -> TaskResponse:
    """GET /tasks/{id} — Returns a single task by UUID."""
    _log("info", f"PACT:10e08a:backend:get_task invoked task_id={task_id}")
    _validate_uuid(task_id)
    try:
        row = db_module.db_get_task(task_id)
    except Exception as e:
        _log("error", f"Database error in get_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**_row_to_response(row))


@router.put("/tasks/{task_id}", response_model=TaskResponse, status_code=200)
def update_task(task_id: str, task: TaskUpdateRequest) -> TaskResponse:
    """PUT /tasks/{id} — PATCH semantics partial update."""
    _log("info", f"PACT:10e08a:backend:update_task invoked task_id={task_id}")
    _validate_uuid(task_id)

    # Build fields dict from only provided fields
    fields = {}
    for field_name in task.model_fields_set:
        value = getattr(task, field_name)
        fields[field_name] = value

    try:
        row = db_module.db_update_task(task_id, fields)
    except Exception as e:
        _log("error", f"Database error in update_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**_row_to_response(row))


@router.delete("/tasks/{task_id}", response_model=DeleteConfirmation, status_code=200)
def delete_task(task_id: str) -> DeleteConfirmation:
    """DELETE /tasks/{id} — Hard-deletes the task."""
    _log("info", f"PACT:10e08a:backend:delete_task invoked task_id={task_id}")
    _validate_uuid(task_id)
    try:
        row = db_module.db_delete_task(task_id)
    except Exception as e:
        _log("error", f"Database error in delete_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteConfirmation(
        detail="Task deleted",
        id=str(row["id"]),
    )


def _row_to_response(row: dict) -> dict:
    """Convert a database row dict to TaskResponse-compatible dict."""
    return {
        "id": str(row["id"]),
        "title": row["title"],
        "description": row.get("description"),
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
