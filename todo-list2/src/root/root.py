"""Root module for personal task management web app.

Implements canonical types, REST endpoint contracts, validation functions,
in-memory storage, and async CRUD operations.
"""
import logging
import re
import time
import uuid as _uuid_mod
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, List, Optional, Union

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
# Primitive wrapper types
# ---------------------------------------------------------------------------

_UUID_V4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)


class TaskUUID:
    """A UUID v4 string in lowercase hyphenated form (8-4-4-4-12)."""
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"TaskUUID requires a string, got {type(value).__name__}")
        if not _UUID_V4_RE.match(value):
            raise ValueError(
                f"Invalid UUID v4: {value!r}. Must be lowercase hyphenated v4 UUID."
            )
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TaskUUID({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaskUUID):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class TaskTitle:
    """A non-empty, whitespace-stripped task title. Max 500 characters after stripping."""
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"TaskTitle requires a string, got {type(value).__name__}")
        if len(value) == 0:
            raise ValueError("TaskTitle must not be empty.")
        if value != value.strip():
            raise ValueError("TaskTitle must be pre-stripped (no leading/trailing whitespace).")
        if value.strip() == "":
            raise ValueError("TaskTitle must not be whitespace-only.")
        if len(value) > 500:
            raise ValueError(f"TaskTitle must not exceed 500 characters (got {len(value)}).")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TaskTitle({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TaskTitle):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class Priority:
    """An integer representing task priority (1 = default/lowest, higher = more urgent)."""
    __slots__ = ("_value",)

    def __init__(self, value: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"Priority requires an integer, got {type(value).__name__}")
        if value < 1:
            raise ValueError(f"Priority must be >= 1, got {value}")
        self._value = value

    @property
    def value(self) -> int:
        return self._value

    def __repr__(self) -> str:
        return f"Priority({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Priority):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class DateString:
    """An ISO 8601 date string in YYYY-MM-DD format (no time component)."""
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"DateString requires a string, got {type(value).__name__}")
        if not _DATE_RE.match(value):
            raise ValueError(f"DateString must match YYYY-MM-DD, got {value!r}")
        # Validate as a real calendar date
        try:
            date.fromisoformat(value)
        except ValueError:
            raise ValueError(f"DateString is not a valid calendar date: {value!r}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"DateString({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DateString):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


class TimestampTZ:
    """An ISO 8601 timestamp string with timezone."""
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"TimestampTZ requires a string, got {type(value).__name__}")
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f"TimestampTZ({self._value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TimestampTZ):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)


# Type aliases
OptionalDateString = Optional[str]
UUID = str  # A v4 UUID string uniquely identifying a task.


class boolean:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass


class string:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class HttpStatusCode(Enum):
    """The set of HTTP status codes used across the API."""
    _200 = 200
    _201 = 201
    _400 = 400
    _404 = 404

    # Allow access by integer value: HttpStatusCode(200)
    def __init__(self, val: int) -> None:
        self._value_ = val


class Sentinel(Enum):
    """Sentinel enum with a single UNSET member."""
    UNSET = "UNSET"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class Task:
    """The canonical task entity."""
    id: str
    title: str
    completed: bool
    priority: int
    due_date: Optional[str] = None
    created_at: str = ""


TaskList = List[Task]


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateTaskRequest:
    """Request body for POST /tasks."""
    title: Any = None
    priority: Any = 1
    due_date: Any = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateTaskRequest:
    """Request body for PATCH /tasks/:id — all fields optional with UNSET sentinel."""
    title: Any = Sentinel.UNSET
    completed: Any = Sentinel.UNSET
    priority: Any = Sentinel.UNSET
    due_date: Any = Sentinel.UNSET


@dataclass(frozen=True, slots=True, kw_only=True)
class ApiErrorResponse:
    """Standard error response body."""
    status: int
    error: str


@dataclass(frozen=True, slots=True, kw_only=True)
class EndpointContract:
    """Describes a single REST endpoint contract."""
    method: str
    path: str
    request_type: str
    success_status: int
    success_response_type: str
    error_branches: list


ValidationResult = Union[CreateTaskRequest, UpdateTaskRequest, str]


# ---------------------------------------------------------------------------
# Validation helpers (pure)
# ---------------------------------------------------------------------------


def _is_valid_integer_priority(val: Any) -> bool:
    """Check that val is a real integer >= 1 (not bool, not float)."""
    if isinstance(val, bool):
        return False
    if not isinstance(val, int):
        return False
    return val >= 1


def _is_valid_date_string(val: str) -> bool:
    """Check val matches YYYY-MM-DD and is a real calendar date."""
    if not isinstance(val, str):
        return False
    if not _DATE_RE.match(val):
        return False
    try:
        date.fromisoformat(val)
        return True
    except ValueError:
        return False


def validate_create_task(request: CreateTaskRequest) -> ValidationResult:
    """
    Pure validation for CreateTaskRequest.
    Returns validated CreateTaskRequest or error string.
    """
    _log("debug", "validate_create_task invoked")

    # Title validation
    title = request.title
    if title is None or not isinstance(title, str):
        return "Title is required and must not be empty."
    stripped = title.strip()
    if len(stripped) == 0:
        return "Title is required and must not be empty."
    if len(stripped) > 500:
        return "Title must not exceed 500 characters."

    # Priority validation
    priority = request.priority
    if not _is_valid_integer_priority(priority):
        return "Priority must be a positive integer >= 1."

    # Due date validation
    due_date = request.due_date
    if due_date is not None:
        if not _is_valid_date_string(due_date):
            return "Due date must be a valid date in YYYY-MM-DD format."

    return CreateTaskRequest(title=stripped, priority=priority, due_date=due_date)


def validate_update_task(request: UpdateTaskRequest) -> ValidationResult:
    """
    Pure validation for UpdateTaskRequest.
    Returns validated UpdateTaskRequest or error string.
    """
    _log("debug", "validate_update_task invoked")

    title = request.title
    completed = request.completed
    priority = request.priority
    due_date = request.due_date

    # Check at least one field is not UNSET
    all_unset = (
        title is Sentinel.UNSET
        and completed is Sentinel.UNSET
        and priority is Sentinel.UNSET
        and due_date is Sentinel.UNSET
    )
    if all_unset:
        return "At least one field must be provided for update."

    # Validate title if provided
    validated_title = Sentinel.UNSET
    if title is not Sentinel.UNSET:
        if not isinstance(title, str):
            return "Title must not be empty."
        stripped = title.strip()
        if len(stripped) == 0:
            return "Title must not be empty."
        if len(stripped) > 500:
            return "Title must not exceed 500 characters."
        validated_title = stripped

    # Validate completed if provided
    validated_completed = Sentinel.UNSET
    if completed is not Sentinel.UNSET:
        if not isinstance(completed, bool):
            return "Completed must be a boolean."
        validated_completed = completed

    # Validate priority if provided
    validated_priority = Sentinel.UNSET
    if priority is not Sentinel.UNSET:
        if not _is_valid_integer_priority(priority):
            return "Priority must be a positive integer >= 1."
        validated_priority = priority

    # Validate due_date if provided (not UNSET)
    validated_due_date = Sentinel.UNSET
    if due_date is not Sentinel.UNSET:
        if due_date is None:
            # Explicit null -> clear due date
            validated_due_date = None
        else:
            if not _is_valid_date_string(due_date):
                return "Due date must be a valid date in YYYY-MM-DD format."
            validated_due_date = due_date

    return UpdateTaskRequest(
        title=validated_title,
        completed=validated_completed,
        priority=validated_priority,
        due_date=validated_due_date,
    )


# ---------------------------------------------------------------------------
# In-memory storage
# ---------------------------------------------------------------------------


class TaskNotFoundError(Exception):
    """Raised when a task_id does not match any stored task."""
    pass


class _TaskStore:
    """Simple in-memory task store."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self._tasks[task.id] = task

    def get(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self._tasks[task_id]

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())

    def update(self, task_id: str, updated: Task) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        return self._tasks.pop(task_id)

    def clear(self) -> None:
        self._tasks.clear()


_store = _TaskStore()


# ---------------------------------------------------------------------------
# Async CRUD operations
# ---------------------------------------------------------------------------


async def create_task(
    request: CreateTaskRequest,
    event_handler=None,
    log_handler=None,
) -> Any:
    """POST /tasks — Creates a new task."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:481349:root:create_task",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    validated = validate_create_task(request)
    if isinstance(validated, str):
        result = ApiErrorResponse(status=400, error="VALIDATION_ERROR")
        _emit({
            "pact_key": "PACT:481349:root:create_task",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        return result

    task_id = str(_uuid_mod.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    task = Task(
        id=task_id,
        title=validated.title,
        completed=False,
        priority=validated.priority,
        due_date=validated.due_date,
        created_at=now,
    )
    _store.add(task)

    _emit({
        "pact_key": "PACT:481349:root:create_task",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": ["insert_task"],
        "ts": time.time_ns(),
    })
    return task


async def list_tasks(
    event_handler=None,
    log_handler=None,
) -> TaskList:
    """GET /tasks — Returns all tasks."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:481349:root:list_tasks",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = _store.list_all()
    _emit({
        "pact_key": "PACT:481349:root:list_tasks",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


async def get_task(
    task_id: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """GET /tasks/:id — Returns a single task by UUID."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:481349:root:get_task",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    try:
        result = _store.get(task_id)
    except TaskNotFoundError:
        result = ApiErrorResponse(status=404, error="NOT_FOUND")
    _emit({
        "pact_key": "PACT:481349:root:get_task",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    event_handler=None,
    log_handler=None,
) -> Any:
    """PATCH /tasks/:id — Updates a task using JSON Merge Patch semantics."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:481349:root:update_task",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })

    # Validate first
    validated = validate_update_task(request)
    if isinstance(validated, str):
        result = ApiErrorResponse(status=400, error="VALIDATION_ERROR")
        _emit({
            "pact_key": "PACT:481349:root:update_task",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        return result

    # Get existing task
    try:
        existing = _store.get(task_id)
    except TaskNotFoundError:
        result = ApiErrorResponse(status=404, error="NOT_FOUND")
        _emit({
            "pact_key": "PACT:481349:root:update_task",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        return result

    # Merge fields
    new_title = validated.title if validated.title is not Sentinel.UNSET else existing.title
    new_completed = validated.completed if validated.completed is not Sentinel.UNSET else existing.completed
    new_priority = validated.priority if validated.priority is not Sentinel.UNSET else existing.priority
    new_due_date = validated.due_date if validated.due_date is not Sentinel.UNSET else existing.due_date

    updated = Task(
        id=existing.id,
        title=new_title,
        completed=new_completed,
        priority=new_priority,
        due_date=new_due_date,
        created_at=existing.created_at,
    )
    _store.update(task_id, updated)

    _emit({
        "pact_key": "PACT:481349:root:update_task",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": ["update_task"],
        "ts": time.time_ns(),
    })
    return updated


async def delete_task(
    task_id: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """DELETE /tasks/:id — Deletes a task by UUID."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:481349:root:delete_task",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    try:
        result = _store.delete(task_id)
    except TaskNotFoundError:
        result = ApiErrorResponse(status=404, error="NOT_FOUND")
    _emit({
        "pact_key": "PACT:481349:root:delete_task",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": ["delete_task"] if isinstance(result, Task) else [],
        "ts": time.time_ns(),
    })
    return result


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------


def task_to_dict(task: Task) -> dict:
    """Serializes a Task to a JSON-compatible dict with snake_case keys."""
    return {
        "id": task.id,
        "title": task.title,
        "completed": task.completed,
        "priority": task.priority,
        "due_date": task.due_date,
        "created_at": task.created_at,
    }


def task_from_dict(data: dict) -> Task:
    """Deserializes a dict into a Task instance with validation."""
    # Check required fields
    for field_name in ("id", "title", "created_at"):
        if field_name not in data:
            raise ValueError(f"Missing required field: {field_name}")

    # Validate id
    task_id = data["id"]
    if not isinstance(task_id, str) or not _UUID_V4_RE.match(task_id):
        raise ValueError(f"Invalid value for field 'id': must be a valid lowercase v4 UUID")

    # Validate title
    title = data["title"]
    if not isinstance(title, str) or len(title.strip()) == 0:
        raise ValueError(f"Invalid value for field 'title': must be a non-empty string")
    if len(title) > 500:
        raise ValueError(f"Invalid value for field 'title': must not exceed 500 characters")

    # Validate completed
    completed = data.get("completed", False)
    if not isinstance(completed, bool):
        raise ValueError(f"Invalid value for field 'completed': must be a boolean")

    # Validate priority
    priority = data.get("priority", 1)
    if isinstance(priority, bool) or not isinstance(priority, int) or priority < 1:
        raise ValueError(f"Invalid value for field 'priority': must be >= 1")

    # Validate due_date
    due_date = data.get("due_date", None)
    if due_date is not None:
        if not _is_valid_date_string(due_date):
            raise ValueError(f"Invalid value for field 'due_date': must be YYYY-MM-DD")

    # Validate created_at
    created_at = data["created_at"]
    if not isinstance(created_at, str):
        raise ValueError(f"Invalid value for field 'created_at': must be a string")

    return Task(
        id=task_id,
        title=title,
        completed=completed,
        priority=priority,
        due_date=due_date,
        created_at=created_at,
    )


# ---------------------------------------------------------------------------
# Endpoint contracts
# ---------------------------------------------------------------------------


def get_endpoint_contracts() -> list:
    """Returns the exhaustive list of EndpointContract definitions for all 5 REST endpoints."""
    return [
        EndpointContract(
            method="POST",
            path="/tasks",
            request_type="CreateTaskRequest",
            success_status=201,
            success_response_type="Task",
            error_branches=[
                {"status": 400, "response_type": "ApiErrorResponse"},
            ],
        ),
        EndpointContract(
            method="GET",
            path="/tasks",
            request_type="None",
            success_status=200,
            success_response_type="TaskList",
            error_branches=[],
        ),
        EndpointContract(
            method="GET",
            path="/tasks/:id",
            request_type="None",
            success_status=200,
            success_response_type="Task",
            error_branches=[
                {"status": 404, "response_type": "ApiErrorResponse"},
            ],
        ),
        EndpointContract(
            method="PATCH",
            path="/tasks/:id",
            request_type="UpdateTaskRequest",
            success_status=200,
            success_response_type="Task",
            error_branches=[
                {"status": 400, "response_type": "ApiErrorResponse"},
                {"status": 404, "response_type": "ApiErrorResponse"},
            ],
        ),
        EndpointContract(
            method="DELETE",
            path="/tasks/:id",
            request_type="None",
            success_status=200,
            success_response_type="Task",
            error_branches=[
                {"status": 404, "response_type": "ApiErrorResponse"},
            ],
        ),
    ]


# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = [
    "OptionalDateString",
    "HttpStatusCode",
    "Task",
    "TaskList",
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "ApiErrorResponse",
    "EndpointContract",
    "ValidationResult",
    "Sentinel",
    "boolean",
    "string",
    "validate_create_task",
    "validate_update_task",
    "create_task",
    "list_tasks",
    "get_task",
    "update_task",
    "delete_task",
    "get_endpoint_contracts",
    "task_to_dict",
    "task_from_dict",
    "TaskUUID",
    "TaskTitle",
    "Priority",
    "DateString",
    "TimestampTZ",
    "UUID",
]
