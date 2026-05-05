import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, field_serializer, field_validator, model_validator

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


# ----------- Enums -----------

class TaskStatus(str, Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# ----------- Bespoke primitive types -----------

class TaskTitle:
    """Non-blank, whitespace-stripped task title. 1..200 chars after strip."""
    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("TaskTitle value must be a string")
        stripped = value.strip()
        if len(stripped) == 0:
            raise ValueError("TaskTitle must be non-blank after stripping whitespace")
        if len(stripped) > 200:
            raise ValueError(f"TaskTitle must be at most 200 characters, got {len(stripped)}")
        self.value = stripped

    def __str__(self) -> str:
        return self.value


OptionalString = Optional[str]


class ISOTimestamp:
    """A datetime with timezone info, serialized to ISO 8601 string with timezone."""
    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("ISOTimestamp value must be a string")
        # Parse to verify it's valid ISO 8601 with timezone
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid ISO 8601 timestamp: {value}") from e
        if dt.tzinfo is None:
            raise ValueError(f"ISOTimestamp requires timezone info: {value}")
        self.value = value
        self.datetime = dt

    def __str__(self) -> str:
        return self.value


class DatabaseURL:
    """PostgreSQL connection string."""
    def __init__(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("DatabaseURL value must be a string")
        if not (value.startswith("postgresql://") or value.startswith("postgres://")):
            raise ValueError(f"DatabaseURL must start with postgresql:// or postgres://, got: {value}")
        self.value = value

    def __str__(self) -> str:
        return self.value


class string:
    """Auto-stubbed type — referenced but not defined in contract 'backend'"""
    pass


# ----------- Pydantic models -----------

class TaskCreateRequest(BaseModel):
    """Request body for POST /tasks."""
    model_config = ConfigDict(use_enum_values=True)

    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Title must be a string")
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError("Title must be non-blank after stripping whitespace")
        if len(stripped) > 255:
            raise ValueError(f"Title must be at most 255 characters, got {len(stripped)}")
        return stripped

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            stripped = v.strip()
            if len(stripped) == 0:
                return None
            return stripped
        return v


class TaskUpdateRequest(BaseModel):
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics)."""
    model_config = ConfigDict(use_enum_values=True)

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Title must be a string")
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError("Title must be non-blank after stripping whitespace")
        if len(stripped) > 255:
            raise ValueError(f"Title must be at most 255 characters, got {len(stripped)}")
        return stripped

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, str):
            stripped = v.strip()
            if len(stripped) == 0:
                return None
            return stripped
        return v


class TaskResponse(BaseModel):
    """Complete task object returned by all read/write endpoints."""
    model_config = ConfigDict(use_enum_values=True)

    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime, _info: Any) -> str:
        return dt.isoformat()


TaskListResponse = List[TaskResponse]


class HealthResponse(BaseModel):
    """Response body for GET /health."""
    status: str

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: Any) -> str:
        if v != "ok":
            raise ValueError("HealthResponse status must be 'ok'")
        return v


class DeleteConfirmation(BaseModel):
    """Response body for DELETE /tasks/{id}."""
    detail: str
    id: str


class ErrorDetail(BaseModel):
    """Standard error response body."""
    detail: str


class ValidationErrorResponse(BaseModel):
    """422 Unprocessable Entity response body."""
    detail: list
