import logging

_PACT_KEY = "PACT:1cf387:frontend"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


from frontend.types import (
    TaskStatus,
    Task,
    OptionalStr,
    TaskCreateRequest,
    TaskUpdateRequest,
    ErrorResponse,
    DeleteConfirmation,
    HealthResponse,
    ApiError,
    TaskListProps,
    TaskItemProps,
    TaskFormProps,
    ImportMetaEnv,
    StatusBadgeColorMap,
    OptionalString,
    string,
)
from frontend.api import (
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    healthCheck,
    resolveBaseUrl,
    parseErrorResponse,
)
from frontend.app import App

__all__ = [
    'TaskStatus',
    'Task',
    'OptionalStr',
    'TaskCreateRequest',
    'TaskUpdateRequest',
    'ErrorResponse',
    'DeleteConfirmation',
    'HealthResponse',
    'ApiError',
    'TaskListProps',
    'TaskItemProps',
    'TaskFormProps',
    'ImportMetaEnv',
    'StatusBadgeColorMap',
    'OptionalString',
    'string',
    'fetchTasks',
    'createTask',
    'updateTask',
    'deleteTask',
    'healthCheck',
    'resolveBaseUrl',
    'parseErrorResponse',
    'App',
]
