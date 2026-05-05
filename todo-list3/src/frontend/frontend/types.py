import logging
import time
from enum import Enum
from typing import Optional, List, Callable, Awaitable, Any

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


# Primitive type aliases
TaskId = int
Timestamp = str
OptionalString = Optional[str]
OptionalStr = Optional[str]


class string:
    """Auto-stubbed type — referenced but not defined in contract 'frontend'"""
    pass


class TaskStatus(Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class Task:
    """Complete task resource representation."""

    def __init__(
        self,
        id: TaskId,
        title: str,
        description: OptionalString,
        status: str,
        created_at: Timestamp,
        updated_at: Timestamp,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:1cf387:frontend:Task:__init__",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"Title must be 1-255 characters, got {len(title) if isinstance(title, str) else type(title)}")
        valid_statuses = {s.value for s in TaskStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        self._emit({
            "pact_key": "PACT:1cf387:frontend:Task:__init__",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskCreateRequest:
    """Request body for POST /tasks."""

    def __init__(
        self,
        title: str,
        description: OptionalString = None,
        status: str = "pending",
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:1cf387:frontend:TaskCreateRequest:__init__",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"Title must be 1-255 characters, got {len(title) if isinstance(title, str) else type(title)}")
        # Empty description -> null
        if description == "":
            description = None
        self.title = title
        self.description = description
        self.status = status
        self._emit({
            "pact_key": "PACT:1cf387:frontend:TaskCreateRequest:__init__",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
        }


class TaskUpdateRequest:
    """Request body for PUT /tasks/{id}."""

    def __init__(
        self,
        title: Optional[str] = None,
        description: OptionalString = None,
        status: Optional[str] = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:1cf387:frontend:TaskUpdateRequest:__init__",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if title is not None:
            if not isinstance(title, str) or not (1 <= len(title) <= 255):
                raise ValueError(f"Title must be 1-255 characters, got {len(title) if isinstance(title, str) else type(title)}")
        self.title = title
        self.description = description
        self.status = status
        self._emit({
            "pact_key": "PACT:1cf387:frontend:TaskUpdateRequest:__init__",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    def to_dict(self) -> dict:
        data = {}
        if self.title is not None:
            data["title"] = self.title
        if self.description is not None:
            data["description"] = self.description
        if self.status is not None:
            data["status"] = self.status
        return data


class ErrorResponse:
    """Standard error envelope."""

    def __init__(self, detail: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail


class DeleteConfirmation:
    """Response body for DELETE /tasks/{id}."""

    def __init__(self, detail: str, id: TaskId, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail
        self.id = id


class HealthResponse:
    """Response body for GET /health."""

    def __init__(self, status: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if status != "ok":
            raise ValueError(f"HealthResponse status must be 'ok', got '{status}'")
        self.status = status


class ApiError(Exception):
    """Frontend-specific error class."""

    def __init__(self, message: str, statusCode: int, detail: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        if not (100 <= statusCode <= 599):
            raise ValueError(f"statusCode must be 100-599, got {statusCode}")
        super().__init__(message)
        self.message = message
        self.statusCode = statusCode
        self.detail = detail


class TaskListProps:
    """Props interface for the TaskList component."""

    def __init__(self, tasks: list, onUpdate: str, onDelete: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.tasks = tasks
        self.onUpdate = onUpdate
        self.onDelete = onDelete


class TaskItemProps:
    """Props interface for the TaskItem component."""

    def __init__(self, task: dict, onUpdate: str, onDelete: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.task = task
        self.onUpdate = onUpdate
        self.onDelete = onDelete


class TaskFormProps:
    """Props interface for the TaskForm component."""

    def __init__(self, onCreate: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.onCreate = onCreate


class ImportMetaEnv:
    """Vite environment type augmentation."""

    def __init__(self, VITE_API_URL: str = "http://localhost:8000", event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.VITE_API_URL = VITE_API_URL


class StatusBadgeColorMap:
    """Mapping from TaskStatus to CSS badge color class names."""
    pending: str = "grey"
    in_progress: str = "blue"
    done: str = "green"

    def __init__(self, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.pending = "grey"
        self.in_progress = "blue"
        self.done = "green"
