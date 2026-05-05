import logging
import os
import time
from typing import List, Optional, Any

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from frontend.types import (
    Task,
    TaskCreateRequest,
    TaskUpdateRequest,
    DeleteConfirmation,
    HealthResponse,
    ApiError,
    ErrorResponse,
    TaskId,
)

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


def resolveBaseUrl() -> str:
    """Resolves backend base URL from env or default."""
    url = os.environ.get("VITE_API_URL", "http://localhost:8000")
    return url.rstrip("/")


async def parseErrorResponse(response: Any) -> "ApiError":
    """Parses a non-ok Response into an ApiError."""
    status_code = getattr(response, "status", None) or getattr(response, "status_code", 0)
    status_text = getattr(response, "statusText", None) or getattr(response, "status_text", "Unknown Error")

    detail = status_text
    try:
        # Try sync json() first (mock objects)
        json_fn = getattr(response, "json", None)
        if json_fn is not None:
            body = json_fn()
            if isinstance(body, dict):
                detail = body.get("detail", status_text)
    except (ValueError, TypeError, AttributeError):
        detail = status_text

    return ApiError(
        message=str(detail),
        statusCode=status_code,
        detail=str(detail),
    )


async def fetchTasks() -> list:
    """Fetches all tasks from GET /tasks endpoint."""
    _log("info", "fetchTasks invoked")
    base_url = resolveBaseUrl()
    if not HAS_HTTPX:
        raise ApiError(
            message="httpx not available",
            statusCode=500,
            detail="httpx not available",
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/tasks")
    except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable",
        ) from e

    if response.status_code < 200 or response.status_code >= 300:
        try:
            body = response.json()
            detail = body.get("detail", response.reason_phrase)
        except Exception:
            detail = response.reason_phrase
        raise ApiError(
            message=str(detail),
            statusCode=response.status_code,
            detail=str(detail),
        )

    _log("info", "fetchTasks completed")
    return response.json()


async def createTask(data: dict) -> dict:
    """Creates a new task via POST /tasks."""
    _log("info", "createTask invoked")
    base_url = resolveBaseUrl()
    if not HAS_HTTPX:
        raise ApiError(
            message="httpx not available",
            statusCode=500,
            detail="httpx not available",
        )

    # Normalize: empty description -> null
    if isinstance(data, dict):
        payload = dict(data)
        if payload.get("description") == "":
            payload["description"] = None
    else:
        payload = data

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/tasks", json=payload)
    except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable",
        ) from e

    if response.status_code < 200 or response.status_code >= 300:
        try:
            body = response.json()
            detail = body.get("detail", response.reason_phrase)
        except Exception:
            detail = response.reason_phrase
        raise ApiError(
            message=str(detail),
            statusCode=response.status_code,
            detail=str(detail),
        )

    _log("info", "createTask completed")
    return response.json()


async def updateTask(id: int, data: dict) -> dict:
    """Updates an existing task via PUT /tasks/{id}."""
    _log("info", "updateTask invoked")
    base_url = resolveBaseUrl()
    if not HAS_HTTPX:
        raise ApiError(
            message="httpx not available",
            statusCode=500,
            detail="httpx not available",
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{base_url}/tasks/{id}", json=data)
    except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable",
        ) from e

    if response.status_code < 200 or response.status_code >= 300:
        try:
            body = response.json()
            detail = body.get("detail", response.reason_phrase)
        except Exception:
            detail = response.reason_phrase
        raise ApiError(
            message=str(detail),
            statusCode=response.status_code,
            detail=str(detail),
        )

    _log("info", "updateTask completed")
    return response.json()


async def deleteTask(id: int) -> dict:
    """Deletes a task via DELETE /tasks/{id}."""
    _log("info", "deleteTask invoked")
    base_url = resolveBaseUrl()
    if not HAS_HTTPX:
        raise ApiError(
            message="httpx not available",
            statusCode=500,
            detail="httpx not available",
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{base_url}/tasks/{id}")
    except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable",
        ) from e

    if response.status_code < 200 or response.status_code >= 300:
        try:
            body = response.json()
            detail = body.get("detail", response.reason_phrase)
        except Exception:
            detail = response.reason_phrase
        raise ApiError(
            message=str(detail),
            statusCode=response.status_code,
            detail=str(detail),
        )

    _log("info", "deleteTask completed")
    return response.json()


async def healthCheck() -> dict:
    """Checks backend availability via GET /health."""
    _log("info", "healthCheck invoked")
    base_url = resolveBaseUrl()
    if not HAS_HTTPX:
        raise ApiError(
            message="httpx not available",
            statusCode=500,
            detail="httpx not available",
        )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
    except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
        raise ApiError(
            message="Network error or backend unreachable",
            statusCode=0,
            detail="Network error or backend unreachable",
        ) from e

    if response.status_code < 200 or response.status_code >= 300:
        try:
            body = response.json()
            detail = body.get("detail", response.reason_phrase)
        except Exception:
            detail = response.reason_phrase
        raise ApiError(
            message=str(detail),
            statusCode=response.status_code,
            detail=str(detail),
        )

    _log("info", "healthCheck completed")
    return response.json()
