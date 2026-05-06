import logging
import time
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

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


# --- string stub type ---
class string:
    """Auto-stubbed type — referenced but not defined in contract 'backend'"""
    pass


# --- TaskStatus enum ---
class TaskStatus(str, Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# --- TaskTitle as a Pydantic model for standalone validation ---
class TaskTitle(BaseModel):
    """Non-blank, whitespace-stripped task title. 1..200 chars after strip."""
    model_config = ConfigDict(strict=False)
    value: str

    @field_validator('value')
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError('Title must not be blank after stripping whitespace')
        if len(stripped) > 200:
            raise ValueError('Title must be at most 200 characters after stripping')
        return stripped


OptionalString = Optional[str]
ISOTimestamp = datetime
TaskId = int
TaskListResponse = List["TaskResponse"]
DatabaseURL = str


def _normalize_description(v: Optional[str]) -> Optional[str]:
    """Normalize empty/whitespace-only descriptions to None."""
    if v is None:
        return None
    stripped = v.strip()
    if not stripped:
        return None
    return v


def _validate_title(v: str) -> str:
    """Strip and validate title: non-blank, 1..255 chars."""
    if v is None:
        raise ValueError('Title is required')
    stripped = v.strip()
    if len(stripped) == 0:
        raise ValueError('Title must not be blank after stripping whitespace')
    if len(stripped) > 255:
        raise ValueError('Title must be at most 255 characters')
    return stripped


class TaskCreateRequest(BaseModel):
    """Request body for POST /tasks."""
    model_config = ConfigDict(strict=False)
    title: str
    description: OptionalString = None
    status: TaskStatus = TaskStatus.pending

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        return _validate_title(v)

    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_description(v)


class TaskUpdateRequest(BaseModel):
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics)."""
    model_config = ConfigDict(strict=False)
    title: Optional[str] = None
    description: OptionalString = None
    status: Optional[TaskStatus] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_title(v)

    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_description(v)


class TaskResponse(BaseModel):
    """Complete task object returned by all read/write endpoints."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: OptionalString = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, v: datetime, _info: Any) -> str:
        return v.isoformat()


class HealthResponse(BaseModel):
    """Response body for GET /health."""
    status: str

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v != 'ok':
            raise ValueError("status must be 'ok'")
        return v


class DeleteConfirmation(BaseModel):
    """Response body for DELETE /tasks/{id}."""
    detail: str
    id: int


class ErrorDetail(BaseModel):
    """Standard error response body."""
    detail: str


class ValidationErrorResponse(BaseModel):
    """422 Unprocessable Entity response body."""
    detail: list
