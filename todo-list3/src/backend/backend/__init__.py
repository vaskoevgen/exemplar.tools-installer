import logging

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


from backend.models import (
    TaskStatus,
    TaskTitle,
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
    TaskListResponse,
    HealthResponse,
    DeleteConfirmation,
    ErrorDetail,
    ValidationErrorResponse,
    OptionalString,
    ISOTimestamp,
    DatabaseURL,
    string,
)

from backend.db import (
    init_connection_pool,
    close_connection_pool,
    get_connection,
    db_list_tasks,
    db_create_task,
    db_get_task,
    db_update_task,
    db_delete_task,
)

from backend.routes import (
    health_check,
    list_tasks,
    create_task,
    get_task,
    update_task,
    delete_task,
)

from backend.main import app

from fastapi import HTTPException

__all__ = [
    "TaskStatus",
    "OptionalString",
    "TaskCreateRequest",
    "TaskUpdateRequest",
    "TaskResponse",
    "TaskListResponse",
    "HealthResponse",
    "DeleteConfirmation",
    "ErrorDetail",
    "ValidationErrorResponse",
    "string",
    "health_check",
    "list_tasks",
    "HTTPException",
    "create_task",
    "get_task",
    "update_task",
    "delete_task",
    "init_connection_pool",
    "close_connection_pool",
    "get_connection",
    "db_list_tasks",
    "db_create_task",
    "db_get_task",
    "db_update_task",
    "db_delete_task",
    "TaskTitle",
    "ISOTimestamp",
    "DatabaseURL",
    "app",
]
