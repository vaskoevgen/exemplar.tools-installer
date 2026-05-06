"""FastAPI route handlers for the Task Management API."""
import logging
import time
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from models import (
    TaskCreateModel,
    TaskUpdateModel,
    TaskResponseModel,
    HealthResponseModel,
    DeleteConfirmationModel,
    TaskStatus,
)
from db import db_list_tasks, db_create_task, db_get_task, db_update_task, db_delete_task

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


router = APIRouter()


@router.get("/health", response_model=HealthResponseModel)
def health_check():
    """GET /health — liveness probe."""
    _log("info", "health_check invoked")
    return HealthResponseModel(status="ok")


@router.get("/tasks", response_model=List[TaskResponseModel])
def list_tasks():
    """GET /tasks — list all tasks ordered by created_at DESC."""
    _log("info", "list_tasks invoked")
    try:
        rows = db_list_tasks()
    except Exception as e:
        _log("error", f"Database error in list_tasks: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    return [TaskResponseModel(**row) for row in rows]


@router.post("/tasks", response_model=TaskResponseModel, status_code=201)
def create_task(task: TaskCreateModel):
    """POST /tasks — create a new task."""
    _log("info", f"create_task invoked: title={task.title!r}")
    try:
        row = db_create_task(
            title=task.title,
            description=task.description,
            status=task.status.value,
        )
    except Exception as e:
        _log("error", f"Database error in create_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    return TaskResponseModel(**row)


@router.get("/tasks/{task_id}", response_model=TaskResponseModel)
def get_task(task_id: int):
    """GET /tasks/{id} — retrieve a single task."""
    _log("info", f"get_task invoked: id={task_id}")
    try:
        row = db_get_task(task_id)
    except Exception as e:
        _log("error", f"Database error in get_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponseModel(**row)


@router.put("/tasks/{task_id}", response_model=TaskResponseModel)
def update_task(task_id: int, task: TaskUpdateModel):
    """PUT /tasks/{id} — partial update (PATCH semantics)."""
    _log("info", f"update_task invoked: id={task_id}")

    # Check task exists first
    try:
        existing = db_get_task(task_id)
    except Exception as e:
        _log("error", f"Database error in update_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")

    # Build fields dict from model_fields_set (PATCH semantics)
    fields = {}
    provided = task.model_fields_set
    if "title" in provided:
        fields["title"] = task.title
    if "description" in provided:
        fields["description"] = task.description
    if "status" in provided:
        fields["status"] = task.status.value if task.status else None

    if not fields:
        return TaskResponseModel(**existing)

    try:
        row = db_update_task(task_id, fields)
    except Exception as e:
        _log("error", f"Database error in update_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponseModel(**row)


@router.delete("/tasks/{task_id}", response_model=DeleteConfirmationModel)
def delete_task(task_id: int):
    """DELETE /tasks/{id} — hard delete."""
    _log("info", f"delete_task invoked: id={task_id}")
    try:
        row = db_delete_task(task_id)
    except Exception as e:
        _log("error", f"Database error in delete_task: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return DeleteConfirmationModel(detail="Task deleted", id=row["id"])
