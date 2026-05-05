import logging
import enum
import time
from typing import Optional, List, Any, Dict, Callable
from dataclasses import dataclass, field

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


# ---------------------------------------------------------------------------
# Primitive type aliases
# ---------------------------------------------------------------------------

class string:
    """Auto-stubbed type — referenced but not defined in contract 'frontend'"""
    pass


# Type aliases
OptionalString = Optional[str]
OptionalStr = Optional[str]


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskStatus(enum.Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# ---------------------------------------------------------------------------
# Data classes / Models
# ---------------------------------------------------------------------------

class Task:
    """Complete task resource representation."""
    def __init__(
        self,
        id: int,
        title: str,
        description: Optional[str],
        status: str,
        created_at: str,
        updated_at: str,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"Task title must be between 1 and 255 characters, got {len(title) if isinstance(title, str) else type(title)}")

        valid_statuses = {s.value for s in TaskStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")

        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

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
        description: Optional[str] = None,
        status: str = "pending",
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"TaskCreateRequest title must be between 1 and 255 characters, got {len(title) if isinstance(title, str) else type(title)}")

        # Empty description -> null (A12)
        if description == "":
            description = None

        valid_statuses = {s.value for s in TaskStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}")

        self.title = title
        self.description = description
        self.status = status

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
        description: Optional[str] = None,
        status: Optional[str] = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if title is not None:
            if not isinstance(title, str) or not (1 <= len(title) <= 255):
                raise ValueError(f"TaskUpdateRequest title must be between 1 and 255 characters, got {len(title) if isinstance(title, str) else type(title)}")

        if status is not None:
            valid_statuses = {s.value for s in TaskStatus}
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")

        self.title = title
        self.description = description
        self.status = status

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
    """Response body for DELETE /tasks/{id} on successful hard-delete."""
    def __init__(self, detail: str, id: int, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail
        self.id = id

    def to_dict(self) -> dict:
        return {"detail": self.detail, "id": self.id}


class HealthResponse:
    """Response body for GET /health."""
    def __init__(self, status: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if status != "ok" and status != "healthy":
            raise ValueError(f"HealthResponse status must be 'ok', got '{status}'")
        self.status = status


class ApiError(Exception):
    """Frontend-specific error class extending Error."""
    def __init__(
        self,
        message: str,
        statusCode: int,
        detail: str,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)

        if not (100 <= statusCode <= 599):
            raise ValueError(f"ApiError statusCode must be between 100 and 599, got {statusCode}")

        super().__init__(message)
        self.message = message
        self.statusCode = statusCode
        self.detail = detail


# ---------------------------------------------------------------------------
# Props interfaces (Python representations)
# ---------------------------------------------------------------------------

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
    def __init__(self, task: Any, onUpdate: str, onDelete: str, event_handler=None, log_handler=None):
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
    def __init__(
        self,
        pending: str = "grey",
        in_progress: str = "blue",
        done: str = "green",
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.pending = pending
        self.in_progress = in_progress
        self.done = done

    def to_dict(self) -> dict:
        return {
            "pending": self.pending,
            "in_progress": self.in_progress,
            "done": self.done,
        }


# ---------------------------------------------------------------------------
# API helper functions
# ---------------------------------------------------------------------------

# Simulated environment variable store for Python-side testing
_env_vars: Dict[str, str] = {}


def resolveBaseUrl(env: Optional[Dict[str, str]] = None) -> str:
    """
    Pure helper that resolves the backend base URL from environment,
    falling back to 'http://localhost:8000'. Strips trailing slash if present.
    """
    _log("debug", "PACT:1cf387:frontend resolveBaseUrl invoked")
    if env is None:
        env = _env_vars
    url = env.get("VITE_API_URL", "") or "http://localhost:8000"
    # Strip trailing slashes
    url = url.rstrip("/")
    if not url:
        url = "http://localhost:8000"
    _log("debug", f"PACT:1cf387:frontend resolveBaseUrl completed: {url}")
    return url


def parseErrorResponse(response: Any) -> 'ApiError':
    """
    Internal helper that parses a non-ok Response into an ApiError.
    Attempts to parse JSON body as ErrorResponse to extract detail;
    falls back to response.statusText if JSON parsing fails.
    """
    _log("debug", "PACT:1cf387:frontend parseErrorResponse invoked")
    status_code = response.status if hasattr(response, 'status') else (response.status_code if hasattr(response, 'status_code') else 0)
    status_text = ""
    if hasattr(response, 'statusText'):
        status_text = response.statusText
    elif hasattr(response, 'status_text'):
        status_text = response.status_text

    detail = status_text
    try:
        body = response.json()
        if isinstance(body, dict) and "detail" in body:
            detail = body["detail"]
    except (ValueError, AttributeError, TypeError):
        detail = status_text

    if not detail:
        detail = status_text or f"HTTP Error {status_code}"

    # Clamp statusCode to valid range for ApiError
    if status_code < 100:
        status_code = 0  # Network error convention

    error = ApiError(
        message=detail,
        statusCode=max(status_code, 100) if status_code > 0 else 100,
        detail=detail,
    )
    _log("debug", f"PACT:1cf387:frontend parseErrorResponse completed: {status_code} {detail}")
    return error


# ---------------------------------------------------------------------------
# Async API functions
# ---------------------------------------------------------------------------

async def fetchTasks(http_client=None, base_url: Optional[str] = None) -> list:
    """
    Fetches all tasks from GET /tasks endpoint.
    Returns the full task list as an array.
    """
    _log("info", "PACT:1cf387:frontend fetchTasks invoked")
    if base_url is None:
        base_url = resolveBaseUrl()
    url = f"{base_url}/tasks"

    if http_client is None:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        )

    try:
        response = await http_client(url, method="GET")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        ) from e

    if not response.ok:
        raise parseErrorResponse(response)

    tasks = response.json()
    _log("info", f"PACT:1cf387:frontend fetchTasks completed: {len(tasks)} tasks")
    return tasks


async def createTask(data: Any, http_client=None, base_url: Optional[str] = None) -> dict:
    """
    Creates a new task via POST /tasks.
    """
    _log("info", "PACT:1cf387:frontend createTask invoked")
    if base_url is None:
        base_url = resolveBaseUrl()
    url = f"{base_url}/tasks"

    # Normalize data to dict
    if isinstance(data, dict):
        request_body = dict(data)
    elif hasattr(data, 'to_dict'):
        request_body = data.to_dict()
    else:
        request_body = data

    # Empty description -> null (A12)
    if "description" in request_body and request_body["description"] == "":
        request_body["description"] = None

    if http_client is None:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        )

    try:
        response = await http_client(url, method="POST", json=request_body)
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        ) from e

    if not response.ok:
        raise parseErrorResponse(response)

    task = response.json()
    _log("info", f"PACT:1cf387:frontend createTask completed: id={task.get('id')}")
    return task


async def updateTask(id: int, data: Any, http_client=None, base_url: Optional[str] = None) -> dict:
    """
    Updates an existing task via PUT /tasks/{id}.
    """
    _log("info", f"PACT:1cf387:frontend updateTask invoked: id={id}")
    if base_url is None:
        base_url = resolveBaseUrl()
    url = f"{base_url}/tasks/{id}"

    # Normalize data to dict
    if isinstance(data, dict):
        request_body = dict(data)
    elif hasattr(data, 'to_dict'):
        request_body = data.to_dict()
    else:
        request_body = data

    if http_client is None:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        )

    try:
        response = await http_client(url, method="PUT", json=request_body)
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        ) from e

    if not response.ok:
        raise parseErrorResponse(response)

    task = response.json()
    _log("info", f"PACT:1cf387:frontend updateTask completed: id={task.get('id')}")
    return task


async def deleteTask(id: int, http_client=None, base_url: Optional[str] = None) -> dict:
    """
    Deletes a task via DELETE /tasks/{id}.
    """
    _log("info", f"PACT:1cf387:frontend deleteTask invoked: id={id}")
    if base_url is None:
        base_url = resolveBaseUrl()
    url = f"{base_url}/tasks/{id}"

    if http_client is None:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        )

    try:
        response = await http_client(url, method="DELETE")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        ) from e

    if not response.ok:
        raise parseErrorResponse(response)

    result = response.json()
    _log("info", f"PACT:1cf387:frontend deleteTask completed: id={result.get('id')}")
    return result


async def healthCheck(http_client=None, base_url: Optional[str] = None) -> dict:
    """
    Checks backend availability via GET /health.
    """
    _log("info", "PACT:1cf387:frontend healthCheck invoked")
    if base_url is None:
        base_url = resolveBaseUrl()
    url = f"{base_url}/health"

    if http_client is None:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        )

    try:
        response = await http_client(url, method="GET")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=100,
            detail="Network error or backend unreachable",
        ) from e

    if not response.ok:
        raise parseErrorResponse(response)

    result = response.json()
    _log("info", f"PACT:1cf387:frontend healthCheck completed: status={result.get('status')}")
    return result


# ---------------------------------------------------------------------------
# Exports list
# ---------------------------------------------------------------------------

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
]
