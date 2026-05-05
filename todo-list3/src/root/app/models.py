from pydantic import model_validator
from pydantic import field_validator
from pydantic import ConfigDict
"""Pydantic v2 models for the task management API."""
import logging
import time
import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    field_serializer,
    model_validator,
)

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


class TaskStatus(str, enum.Enum):
    """Task lifecycle states matching CROSS-TIER-11."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


class TaskCreateRequest(BaseModel):
    """Request body for POST /tasks."""
    model_config = ConfigDict(strict=False)

    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError("Title must not be blank after stripping whitespace")
        if len(stripped) > 255:
            raise ValueError("Title must not exceed 255 characters")
        return stripped

    @field_validator("description")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v.strip() == "":
            return None
        return v


class TaskUpdateRequest(BaseModel):
    """Request body for PUT /tasks/{id} with PATCH semantics."""
    model_config = ConfigDict(strict=False)

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        stripped = v.strip()
        if len(stripped) == 0:
            raise ValueError("Title must not be blank after stripping whitespace")
        if len(stripped) > 255:
            raise ValueError("Title must not exceed 255 characters")
        return stripped

    @field_validator("description")
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if v.strip() == "":
            return None
        return v


class TaskResponse(BaseModel):
    """Complete task object returned by all read/write endpoints."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, v: datetime, _info: Any) -> str:
        return v.isoformat()

    @field_serializer("updated_at")
    def serialize_updated_at(self, v: datetime, _info: Any) -> str:
        return v.isoformat()

    @field_serializer("status")
    def serialize_status(self, v: TaskStatus, _info: Any) -> str:
        return v.value


class HealthResponse(BaseModel):
    """Response body for GET /health."""
    status: str


class DeleteConfirmation(BaseModel):
    """Response body for DELETE /tasks/{id}."""
    detail: str
    id: int


class ErrorDetail(BaseModel):
    """Standard error envelope."""
    detail: str
