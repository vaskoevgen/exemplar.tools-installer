import logging
import time
import enum
from typing import Optional, List, Dict, Any, Callable
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


# ===========================================================================
# Type: string (auto-stubbed)
# ===========================================================================

class string:
    """Auto-stubbed type — referenced but not defined in contract 'frontend'"""
    pass


# ===========================================================================
# Type aliases
# ===========================================================================

# TaskId is an integer surrogate key
TaskId = int

# Timestamp is an ISO 8601 datetime string
Timestamp = str

# OptionalString is str | None
OptionalString = Optional[str]
OptionalStr = Optional[str]


# ===========================================================================
# TaskStatus enum
# ===========================================================================

class TaskStatus(enum.Enum):
    """Closed set of allowed task lifecycle states; enforced by backend validation
    and database CHECK-equivalent logic."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# ===========================================================================
# StatusBadgeColorMap
# ===========================================================================

class StatusBadgeColorMap:
    """Mapping from TaskStatus to CSS badge color class names used in TaskItem rendering."""
    pending: str = "grey"
    in_progress: str = "blue"
    done: str = "green"

    def __init__(self, pending: str = "grey", in_progress: str = "blue", done: str = "green",
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.pending = pending
        self.in_progress = in_progress
        self.done = done


# ===========================================================================
# Task
# ===========================================================================

class Task:
    """Complete task resource representation returned by all GET/POST/PUT endpoints;
    mirrors the database row with timestamps serialized as ISO strings."""

    def __init__(self, id: TaskId, title: str, description: OptionalString,
                 status: str, created_at: Timestamp, updated_at: Timestamp,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if not isinstance(id, int) or id <= 0:
            raise ValueError(f"Task id must be a positive integer, got {id}")
        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"Task title must be 1-255 characters, got length {len(title) if isinstance(title, str) else 'non-string'}")
        valid_statuses = {s.value for s in TaskStatus}
        status_val = status.value if isinstance(status, TaskStatus) else status
        if status_val not in valid_statuses:
            raise ValueError(f"Task status must be one of {valid_statuses}, got '{status_val}'")

        self.id = id
        self.title = title
        self.description = description
        self.status = status_val
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ===========================================================================
# TaskCreateRequest
# ===========================================================================

class TaskCreateRequest:
    """Request body for POST /tasks — creates a new task."""

    def __init__(self, title: str, description: OptionalString = None,
                 status: str = "pending", event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if not isinstance(title, str) or not (1 <= len(title) <= 255):
            raise ValueError(f"Title must be 1-255 characters")

        # Invariant A12: empty description strings are sent as null
        if description is not None and isinstance(description, str):
            if not description.strip():
                description = None

        valid_statuses = {s.value for s in TaskStatus}
        status_val = status.value if isinstance(status, TaskStatus) else status
        if status_val not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}, got '{status_val}'")

        self.title = title
        self.description = description
        self.status = status_val

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status,
        }


# ===========================================================================
# TaskUpdateRequest
# ===========================================================================

class TaskUpdateRequest:
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics).
    Only provided fields are modified; created_at is never affected."""

    def __init__(self, title: Optional[str] = None, description: OptionalString = None,
                 status: Optional[str] = None, event_handler=None, log_handler=None,
                 _description_provided: bool = False):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        if title is not None:
            if not isinstance(title, str) or not (1 <= len(title) <= 255):
                raise ValueError(f"Title must be 1-255 characters")

        if status is not None:
            valid_statuses = {s.value for s in TaskStatus}
            status_val = status.value if isinstance(status, TaskStatus) else status
            if status_val not in valid_statuses:
                raise ValueError(f"Status must be one of {valid_statuses}, got '{status_val}'")
            status = status_val

        self.title = title
        self.description = description
        self.status = status
        self._description_provided = _description_provided

    def to_dict(self) -> Dict[str, Any]:
        """Returns dict with only the fields that were explicitly set."""
        result: Dict[str, Any] = {}
        if self.title is not None:
            result["title"] = self.title
        if self._description_provided or self.description is not None:
            result["description"] = self.description
        if self.status is not None:
            result["status"] = self.status
        return result


# ===========================================================================
# ErrorResponse
# ===========================================================================

class ErrorResponse:
    """Standard error envelope returned on 404 (and other error codes)
    with a human-readable detail message."""

    def __init__(self, detail: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail


# ===========================================================================
# DeleteConfirmation
# ===========================================================================

class DeleteConfirmation:
    """Response body for DELETE /tasks/{id} on successful hard-delete (HTTP 200)."""

    def __init__(self, detail: str, id: TaskId, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail
        self.id = id


# ===========================================================================
# HealthResponse
# ===========================================================================

class HealthResponse:
    """Response body for GET /health indicating service liveness."""

    def __init__(self, status: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        if status != "ok" and status != "healthy":
            raise ValueError(f"HealthResponse status must be 'ok', got '{status}'")
        self.status = status


# ===========================================================================
# ApiError
# ===========================================================================

class ApiError(Exception):
    """Frontend-specific error class extending Error. Thrown by api.ts functions
    when the backend returns a non-ok HTTP response. Captures HTTP status code
    and parsed detail message."""

    def __init__(self, message: str, statusCode: int, detail: str,
                 event_handler=None, log_handler=None):
        self._emit_handler = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)

        # Validate statusCode range: 0 is allowed for network errors, otherwise 100-599
        if statusCode != 0 and not (100 <= statusCode <= 599):
            raise ValueError(f"ApiError statusCode must be 0 or 100-599, got {statusCode}")

        super().__init__(message)
        self.message = message
        self.statusCode = statusCode
        self.detail = detail


# ===========================================================================
# Props interfaces (Python representations)
# ===========================================================================

class TaskListProps:
    """Props interface for the TaskList component."""

    def __init__(self, tasks: list, onUpdate: str, onDelete: str,
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.tasks = tasks
        self.onUpdate = onUpdate
        self.onDelete = onDelete


class TaskItemProps:
    """Props interface for the TaskItem component."""

    def __init__(self, task: Task, onUpdate: str, onDelete: str,
                 event_handler=None, log_handler=None):
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


# ===========================================================================
# ImportMetaEnv
# ===========================================================================

class ImportMetaEnv:
    """Vite environment type augmentation."""

    def __init__(self, VITE_API_URL: str = "http://localhost:8000",
                 event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.VITE_API_URL = VITE_API_URL


# ===========================================================================
# Environment simulation for resolveBaseUrl
# ===========================================================================

# This simulates import.meta.env in a Python context
_env: Dict[str, str] = {}


def _set_env(key: str, value: Optional[str]) -> None:
    """Test helper to set environment variables."""
    if value is None:
        _env.pop(key, None)
    else:
        _env[key] = value


def _get_env(key: str) -> Optional[str]:
    """Test helper to get environment variables."""
    return _env.get(key)


# ===========================================================================
# resolveBaseUrl
# ===========================================================================

def resolveBaseUrl() -> str:
    """Pure helper that resolves the backend base URL from VITE_API_URL,
    falling back to 'http://localhost:8000'. Strips trailing slash if present."""
    _log("debug", "resolveBaseUrl invoked")
    import os
    url = os.environ.get("VITE_API_URL", "").strip()
    if not url:
        url = _env.get("VITE_API_URL", "").strip()
    if not url:
        url = "http://localhost:8000"
    # Strip trailing slashes
    url = url.rstrip("/")
    _log("debug", f"resolveBaseUrl resolved to: {url}")
    return url


# ===========================================================================
# parseErrorResponse
# ===========================================================================

async def parseErrorResponse(response: Any) -> 'ApiError':
    """Internal helper that parses a non-ok Response into an ApiError.
    Attempts to parse JSON body as ErrorResponse to extract detail;
    falls back to response.statusText if JSON parsing fails."""
    _log("debug", f"parseErrorResponse invoked for status {getattr(response, 'status', 'unknown')}")

    status_code = getattr(response, 'status', getattr(response, 'status_code', 0))
    status_text = getattr(response, 'statusText', getattr(response, 'status_text', 'Unknown Error'))

    detail = status_text
    try:
        # Try to parse JSON body
        json_body = response.json()
        if isinstance(json_body, dict) and "detail" in json_body:
            detail = json_body["detail"]
    except (ValueError, AttributeError, TypeError):
        # Fall back to statusText
        detail = status_text

    message = detail
    error = ApiError(message=message, statusCode=status_code, detail=detail)
    _log("debug", f"parseErrorResponse created ApiError: {status_code} - {detail}")
    return error


# ===========================================================================
# HTTP client simulation helpers
# ===========================================================================

# In a real frontend, these would use native fetch().
# For Python testing, we use a pluggable HTTP client.

_http_client: Optional[Any] = None


def _set_http_client(client: Any) -> None:
    """Set the HTTP client for testing."""
    global _http_client
    _http_client = client


async def _fetch(url: str, method: str = "GET", body: Optional[Dict] = None,
                 headers: Optional[Dict] = None) -> Any:
    """Internal fetch wrapper."""
    import json as json_module

    if _http_client is not None:
        return await _http_client(url, method=method, body=body, headers=headers)

    # Default: use aiohttp or httpx if available, otherwise raise
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            kwargs: Dict[str, Any] = {"method": method, "url": url}
            if headers:
                kwargs["headers"] = headers
            if body is not None:
                kwargs["content"] = json_module.dumps(body)
                if headers is None:
                    kwargs["headers"] = {"Content-Type": "application/json"}
            resp = await client.request(**kwargs)
            return resp
    except ImportError:
        raise ConnectionError(f"No HTTP client available to fetch {url}")


# ===========================================================================
# API Functions
# ===========================================================================

async def fetchTasks() -> List[Dict[str, Any]]:
    """Fetches all tasks from GET /tasks endpoint. Returns the full task list as an array."""
    _log("info", "fetchTasks invoked")
    base_url = resolveBaseUrl()
    url = f"{base_url}/tasks"

    try:
        response = await _fetch(url, method="GET")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable"
        ) from e

    if not getattr(response, 'ok', False) and not (200 <= getattr(response, 'status', 0) < 300):
        error = await parseErrorResponse(response)
        raise error

    try:
        data = response.json()
    except (ValueError, AttributeError):
        data = []

    _log("info", f"fetchTasks completed, returned {len(data)} tasks")
    return data


async def createTask(data: Any) -> Dict[str, Any]:
    """Creates a new task via POST /tasks. Sends TaskCreateRequest as JSON body.
    Returns the newly created Task with backend-assigned id, created_at, and updated_at."""
    _log("info", "createTask invoked")
    base_url = resolveBaseUrl()
    url = f"{base_url}/tasks"

    # Build request body
    if isinstance(data, dict):
        body = dict(data)
    elif hasattr(data, 'to_dict'):
        body = data.to_dict()
    else:
        body = {
            "title": getattr(data, 'title', ''),
            "description": getattr(data, 'description', None),
            "status": getattr(data, 'status', 'pending'),
        }

    # Invariant A12: empty description strings are sent as null
    if "description" in body and isinstance(body["description"], str):
        if not body["description"].strip():
            body["description"] = None

    # Ensure status defaults to pending if not provided
    if "status" not in body or body["status"] is None:
        body["status"] = "pending"

    headers = {"Content-Type": "application/json"}

    try:
        response = await _fetch(url, method="POST", body=body, headers=headers)
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable"
        ) from e

    if not getattr(response, 'ok', False) and not (200 <= getattr(response, 'status', 0) < 300):
        error = await parseErrorResponse(response)
        raise error

    try:
        result = response.json()
    except (ValueError, AttributeError):
        raise ApiError(
            message="Invalid response from server",
            statusCode=500,
            detail="Invalid response from server"
        )

    _log("info", f"createTask completed, created task id={result.get('id')}")
    return result


async def updateTask(id: TaskId, data: Any) -> Dict[str, Any]:
    """Updates an existing task via PUT /tasks/{id}. Sends TaskUpdateRequest as JSON body
    containing only changed fields. Returns the fully updated Task."""
    _log("info", f"updateTask invoked for id={id}")
    base_url = resolveBaseUrl()
    url = f"{base_url}/tasks/{id}"

    # Build request body
    if isinstance(data, dict):
        body = dict(data)
    elif hasattr(data, 'to_dict'):
        body = data.to_dict()
    else:
        body = {}
        if getattr(data, 'title', None) is not None:
            body["title"] = data.title
        if getattr(data, 'description', None) is not None or getattr(data, '_description_provided', False):
            body["description"] = data.description
        if getattr(data, 'status', None) is not None:
            body["status"] = data.status

    headers = {"Content-Type": "application/json"}

    try:
        response = await _fetch(url, method="PUT", body=body, headers=headers)
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable"
        ) from e

    if not getattr(response, 'ok', False) and not (200 <= getattr(response, 'status', 0) < 300):
        error = await parseErrorResponse(response)
        raise error

    try:
        result = response.json()
    except (ValueError, AttributeError):
        raise ApiError(
            message="Invalid response from server",
            statusCode=500,
            detail="Invalid response from server"
        )

    _log("info", f"updateTask completed for id={id}")
    return result


async def deleteTask(id: TaskId) -> Dict[str, Any]:
    """Deletes a task via DELETE /tasks/{id}. Returns DeleteConfirmation on success."""
    _log("info", f"deleteTask invoked for id={id}")
    base_url = resolveBaseUrl()
    url = f"{base_url}/tasks/{id}"

    try:
        response = await _fetch(url, method="DELETE")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable"
        ) from e

    if not getattr(response, 'ok', False) and not (200 <= getattr(response, 'status', 0) < 300):
        error = await parseErrorResponse(response)
        raise error

    try:
        result = response.json()
    except (ValueError, AttributeError):
        raise ApiError(
            message="Invalid response from server",
            statusCode=500,
            detail="Invalid response from server"
        )

    _log("info", f"deleteTask completed for id={id}")
    return result


async def healthCheck() -> Dict[str, Any]:
    """Checks backend availability via GET /health. Returns HealthResponse with status field."""
    _log("info", "healthCheck invoked")
    base_url = resolveBaseUrl()
    url = f"{base_url}/health"

    try:
        response = await _fetch(url, method="GET")
    except (ConnectionError, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable"
        ) from e

    if not getattr(response, 'ok', False) and not (200 <= getattr(response, 'status', 0) < 300):
        error = await parseErrorResponse(response)
        raise error

    try:
        result = response.json()
    except (ValueError, AttributeError):
        raise ApiError(
            message="Invalid response from server",
            statusCode=500,
            detail="Invalid response from server"
        )

    _log("info", f"healthCheck completed, status={result.get('status')}")
    return result


# ===========================================================================
# REQUIRED EXPORTS
# ===========================================================================

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
