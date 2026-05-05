import logging
import time
from typing import List

from fastapi import APIRouter, HTTPException

from backend.models import (
    DeleteConfirmation,
    HealthResponse,
    TaskCreateRequest,
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


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """GET /health — Returns {'status': 'ok'}."""
    _log("info", "health_check invoked")
    return HealthResponse(status="ok")


@router.get("/tasks", response_model=List[TaskResponse])
def list_tasks() -> List[TaskResponse]:
    """GET /tasks — Returns all tasks ordered by created_at DESC."""
    _log("info", "list_tasks invoked")
    try:
        rows = db_module.db_list_tasks()
    except Exception as e:
        _log("error", f"Database error in list_tasks: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    return [TaskResponse(**row) for row in rows]


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreateRequest) -> TaskResponse:
    """POST /tasks — Creates a new task."""
    _log("info", f"create_task invoked: title={task.title}")
    try:
        row = db_module.db_create_task(
            title=task.title,
            description=task.description,
            status=task.status.value,
        )
    except Exception as e:
        _log("error", f"Database error in create_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    return TaskResponse(**row)


@router.get("/tasks/{id}", response_model=TaskResponse)
def get_task(id: int) -> TaskResponse:
    """GET /tasks/{id} — Returns a single task by id."""
    _log("info", f"get_task invoked: id={id}")
    try:
        row = db_module.db_get_task(id)
    except Exception as e:
        _log("error", f"Database error in get_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**row)


@router.put("/tasks/{id}", response_model=TaskResponse)
def update_task(id: int, task: TaskUpdateRequest) -> TaskResponse:
    """PUT /tasks/{id} — PATCH semantics."""
    _log("info", f"update_task invoked: id={id}")

    # Build fields dict from model_fields_set
    fields = {}
    for field_name in task.model_fields_set:
        fields[field_name] = getattr(task, field_name)

    if not fields:
        # No fields to update; just fetch and return current
        try:
            row = db_module.db_get_task(id)
        except Exception as e:
            _log("error", f"Database error in update_task: {e}")
            raise HTTPException(status_code=500, detail="Database connection error")
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskResponse(**row)

    try:
        row = db_module.db_update_task(id, fields)
    except Exception as e:
        _log("error", f"Database error in update_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**row)


@router.delete("/tasks/{id}", response_model=DeleteConfirmation)
def delete_task(id: int) -> DeleteConfirmation:
    """DELETE /tasks/{id} — Hard-deletes the task."""
    _log("info", f"delete_task invoked: id={id}")
    try:
        result = db_module.db_delete_task(id)
    except Exception as e:
        _log("error", f"Database error in delete_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteConfirmation(detail="Task deleted", id=result["id"])
