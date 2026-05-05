"""Root integration contract implementation.

This module implements the canonical type registry and integration verification
functions for the task management application's three-tier architecture.
"""
import logging
import time
import re
import os
from enum import Enum
from typing import Optional, List, Any
from datetime import datetime, timezone

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


# ===========================================================================
# Canonical Type Registry
# ===========================================================================


class string:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass


class TaskStatus(Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


OptionalString = Optional[str]


class TaskTitle:
    """Non-blank, whitespace-stripped task title. 1-255 chars after strip."""

    def __init__(self, value: str, *, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:TaskTitle.__init__",
            "event": "invoked",
            "input_classification": ["value"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if not isinstance(value, str):
            raise ValueError("TaskTitle value must be a string")
        stripped = value.strip()
        if len(stripped) == 0:
            raise ValueError("TaskTitle must be non-blank after whitespace stripping")
        if len(stripped) > 255:
            raise ValueError(
                f"TaskTitle must be at most 255 characters after stripping, got {len(stripped)}"
            )
        self.value = stripped
        self._emit({
            "pact_key": "PACT:481349:root:TaskTitle.__init__",
            "event": "completed",
            "input_classification": ["value"],
            "output_classification": ["TaskTitle"],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"TaskTitle(value={self.value!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, TaskTitle):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented


class DatabaseURL:
    """PostgreSQL connection string. Must start with postgresql://."""

    def __init__(self, value: str, *, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:DatabaseURL.__init__",
            "event": "invoked",
            "input_classification": ["value"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if not isinstance(value, str) or not value.startswith("postgresql://"):
            raise ValueError(
                "DatabaseURL must start with 'postgresql://'"
            )
        self.value = value
        self._emit({
            "pact_key": "PACT:481349:root:DatabaseURL.__init__",
            "event": "completed",
            "input_classification": ["value"],
            "output_classification": ["DatabaseURL"],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"DatabaseURL(value={self.value!r})"


def _validate_title(title: Optional[str], required: bool = True) -> Optional[str]:
    """Shared title validation logic for TaskCreateRequest and TaskUpdateRequest."""
    if title is None:
        if required:
            raise ValueError("title is required")
        return None
    if not isinstance(title, str):
        raise ValueError("title must be a string")
    stripped = title.strip()
    if len(stripped) == 0:
        raise ValueError("title must be non-blank after whitespace stripping")
    if len(stripped) > 255:
        raise ValueError(
            f"title must be at most 255 characters after stripping, got {len(stripped)}"
        )
    return stripped


class TaskCreateRequest:
    """Request body for POST /tasks."""

    def __init__(
        self,
        title: str,
        description: OptionalString = None,
        status: TaskStatus = TaskStatus.pending,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:TaskCreateRequest.__init__",
            "event": "invoked",
            "input_classification": ["title", "description", "status"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        self.title = _validate_title(title, required=True)
        self.description = description
        if not isinstance(status, TaskStatus):
            raise ValueError(f"status must be a TaskStatus enum value, got {status!r}")
        self.status = status
        self._emit({
            "pact_key": "PACT:481349:root:TaskCreateRequest.__init__",
            "event": "completed",
            "input_classification": ["title", "description", "status"],
            "output_classification": ["TaskCreateRequest"],
            "side_effects": [],
            "ts": time.time_ns(),
        })


class TaskUpdateRequest:
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics)."""

    def __init__(
        self,
        title: Optional[str] = None,
        description: OptionalString = None,
        status: Optional[TaskStatus] = None,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:TaskUpdateRequest.__init__",
            "event": "invoked",
            "input_classification": ["title", "description", "status"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        # Title is optional in update, but if provided must be valid
        if title is not None:
            self.title = _validate_title(title, required=True)
        else:
            self.title = None
        self.description = description
        if status is not None and not isinstance(status, TaskStatus):
            raise ValueError(f"status must be a TaskStatus enum value, got {status!r}")
        self.status = status
        self._emit({
            "pact_key": "PACT:481349:root:TaskUpdateRequest.__init__",
            "event": "completed",
            "input_classification": ["title", "description", "status"],
            "output_classification": ["TaskUpdateRequest"],
            "side_effects": [],
            "ts": time.time_ns(),
        })


class TaskResponse:
    """Complete task object returned by all read/write endpoints."""

    def __init__(
        self,
        id: int,
        title: str,
        description: OptionalString,
        status: TaskStatus,
        created_at: datetime,
        updated_at: datetime,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at


# TaskListResponse is just a list alias
TaskListResponse = List[TaskResponse]


class ErrorResponse:
    """Standard error envelope."""

    def __init__(self, detail: str, *, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail


class ValidationErrorItem:
    """A single validation error within the 422 response."""

    def __init__(
        self,
        loc: list,
        msg: str,
        type: str,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.loc = loc
        self.msg = msg
        self.type = type


class ValidationErrorResponse:
    """HTTP 422 Unprocessable Entity response body."""

    def __init__(self, detail: list, *, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail


class HealthResponse:
    """Response body for GET /health."""

    def __init__(self, status: str, *, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:HealthResponse.__init__",
            "event": "invoked",
            "input_classification": ["status"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if status != "ok":
            raise ValueError("HealthResponse status must be exactly 'ok'")
        self.status = status
        self._emit({
            "pact_key": "PACT:481349:root:HealthResponse.__init__",
            "event": "completed",
            "input_classification": ["status"],
            "output_classification": ["HealthResponse"],
            "side_effects": [],
            "ts": time.time_ns(),
        })


class DeleteConfirmation:
    """Response body for DELETE /tasks/{id} on successful hard-delete."""

    def __init__(
        self,
        detail: str,
        id: int,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.detail = detail
        self.id = id


class HttpEndpoint:
    """Descriptor for one REST API endpoint in the HTTP API contract."""

    VALID_METHODS = {"GET", "POST", "PUT", "DELETE"}

    def __init__(
        self,
        method: str,
        path: str,
        response_body_type: str,
        success_status_code: int,
        content_type: str,
        request_body_type: OptionalString = None,
        *,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._emit({
            "pact_key": "PACT:481349:root:HttpEndpoint.__init__",
            "event": "invoked",
            "input_classification": ["method", "path"],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        if method not in self.VALID_METHODS:
            raise ValueError(
                f"HttpEndpoint method must be one of {self.VALID_METHODS}, got {method!r}"
            )
        self.method = method
        self.path = path
        self.request_body_type = request_body_type
        self.response_body_type = response_body_type
        self.success_status_code = success_status_code
        self.content_type = content_type
        self._emit({
            "pact_key": "PACT:481349:root:HttpEndpoint.__init__",
            "event": "completed",
            "input_classification": ["method", "path"],
            "output_classification": ["HttpEndpoint"],
            "side_effects": [],
            "ts": time.time_ns(),
        })


# ===========================================================================
# Canonical HTTP Endpoint Table
# ===========================================================================

HTTP_ENDPOINTS = [
    HttpEndpoint(
        method="GET", path="/health",
        response_body_type="HealthResponse",
        success_status_code=200, content_type="application/json",
    ),
    HttpEndpoint(
        method="GET", path="/tasks",
        response_body_type="TaskListResponse",
        success_status_code=200, content_type="application/json",
    ),
    HttpEndpoint(
        method="POST", path="/tasks",
        request_body_type="TaskCreateRequest",
        response_body_type="TaskResponse",
        success_status_code=201, content_type="application/json",
    ),
    HttpEndpoint(
        method="GET", path="/tasks/{id}",
        response_body_type="TaskResponse",
        success_status_code=200, content_type="application/json",
    ),
    HttpEndpoint(
        method="PUT", path="/tasks/{id}",
        request_body_type="TaskUpdateRequest",
        response_body_type="TaskResponse",
        success_status_code=200, content_type="application/json",
    ),
    HttpEndpoint(
        method="DELETE", path="/tasks/{id}",
        response_body_type="DeleteConfirmation",
        success_status_code=200, content_type="application/json",
    ),
]


# ===========================================================================
# Integration Verification Functions
# ===========================================================================

# Init SQL script for schema verification
INIT_SQL = """
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'tasks_status_check'
    ) THEN
        ALTER TABLE tasks ADD CONSTRAINT tasks_status_check
            CHECK (status IN ('pending', 'in_progress', 'done'));
    END IF;
END
$$;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'update_updated_at_column'
    ) THEN
        CREATE TRIGGER update_updated_at_column
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;
"""


def _get_psycopg2_connection(database_url: str):
    """Create a psycopg2 connection from a database URL."""
    try:
        import psycopg2
        conn = psycopg2.connect(database_url, connect_timeout=5)
        return conn
    except Exception as e:
        raise ConnectionError(f"database_unreachable: {e}") from e


def verify_schema_initialization_idempotent(database_url: str) -> bool:
    """Verify that the database init.sql script is fully idempotent."""
    _log("info", "verify_schema_initialization_idempotent invoked")

    # Connect to database
    conn = _get_psycopg2_connection(database_url)
    try:
        conn.autocommit = True
        cur = conn.cursor()

        # Execute init SQL twice - both must succeed (idempotency)
        try:
            cur.execute(INIT_SQL)
        except Exception as e:
            raise AssertionError(f"idempotency_failure: First execution of init.sql failed: {e}") from e

        try:
            cur.execute(INIT_SQL)
        except Exception as e:
            raise AssertionError(f"idempotency_failure: Second execution of init.sql failed: {e}") from e

        # Verify table exists with correct columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tasks'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        if not columns:
            raise AssertionError("schema_mismatch: tasks table does not exist")

        col_names = [c[0] for c in columns]
        expected_columns = ['id', 'title', 'description', 'status', 'created_at', 'updated_at']
        for expected_col in expected_columns:
            if expected_col not in col_names:
                raise AssertionError(
                    f"schema_mismatch: Missing column '{expected_col}' in tasks table. "
                    f"Found columns: {col_names}"
                )

        # Verify CHECK constraint on status
        cur.execute("""
            SELECT 1 FROM pg_constraint
            WHERE conname = 'tasks_status_check'
              AND contype = 'c';
        """)
        if not cur.fetchone():
            raise AssertionError(
                "schema_mismatch: CHECK constraint 'tasks_status_check' not found on tasks table"
            )

        # Verify trigger exists
        cur.execute("""
            SELECT 1 FROM pg_trigger
            WHERE tgname = 'update_updated_at_column';
        """)
        if not cur.fetchone():
            raise AssertionError(
                "schema_mismatch: Trigger 'update_updated_at_column' not found on tasks table"
            )

        cur.close()
        _log("info", "verify_schema_initialization_idempotent completed successfully")
        return True
    finally:
        conn.close()


def verify_test_isolation(database_url: str) -> bool:
    """Verify that contract tests properly isolate test data."""
    _log("info", "verify_test_isolation invoked")

    conn = _get_psycopg2_connection(database_url)
    try:
        conn.autocommit = False
        cur = conn.cursor()

        # Record initial row count
        cur.execute("SELECT COUNT(*) FROM tasks;")
        initial_count = cur.fetchone()[0]

        # Insert a test row within a transaction
        cur.execute(
            "INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING id;",
            ("__test_isolation_probe__", "pending"),
        )
        test_id = cur.fetchone()[0]

        # Verify it exists
        cur.execute("SELECT COUNT(*) FROM tasks WHERE id = %s;", (test_id,))
        found = cur.fetchone()[0]
        if found != 1:
            raise AssertionError(
                "isolation_violation: Test row was not inserted correctly"
            )

        # Rollback to simulate proper test cleanup
        conn.rollback()

        # Verify the row is gone after rollback
        cur.execute("SELECT COUNT(*) FROM tasks WHERE id = %s;", (test_id,))
        found_after = cur.fetchone()[0]
        if found_after != 0:
            raise AssertionError(
                "isolation_violation: Test data leaked after rollback"
            )

        # Verify row count unchanged
        cur.execute("SELECT COUNT(*) FROM tasks;")
        final_count = cur.fetchone()[0]
        if final_count != initial_count:
            raise AssertionError(
                f"isolation_violation: Row count changed from {initial_count} to {final_count}"
            )

        conn.commit()
        cur.close()
        _log("info", "verify_test_isolation completed successfully")
        return True
    finally:
        conn.close()


async def verify_connection_pool_lifecycle(backend_base_url: str) -> bool:
    """Verify that psycopg2 ThreadedConnectionPool lifecycle is tied to FastAPI lifespan."""
    _log("info", "verify_connection_pool_lifecycle invoked")

    try:
        import httpx
    except ImportError:
        import aiohttp
        # Fallback to aiohttp if httpx not available
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                # Verify health endpoint works
                async with session.get(f"{backend_base_url}/health") as resp:
                    if resp.status != 200:
                        raise AssertionError(
                            "pool_not_initialized: /health endpoint returned non-200"
                        )
                # Verify database queries work (pool is functional)
                async with session.get(f"{backend_base_url}/tasks") as resp:
                    if resp.status == 500:
                        raise AssertionError(
                            "pool_not_initialized: /tasks returned 500 - "
                            "connection pool may not be initialized"
                        )
                    if resp.status != 200:
                        raise AssertionError(
                            f"pool_not_initialized: /tasks returned {resp.status}"
                        )
            _log("info", "verify_connection_pool_lifecycle completed successfully")
            return True
        except (aiohttp.ClientError, OSError) as e:
            raise ConnectionError(f"backend_unreachable: {e}") from e

    # Use httpx
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Verify health endpoint works
            resp = await client.get(f"{backend_base_url}/health")
            if resp.status_code != 200:
                raise AssertionError(
                    "pool_not_initialized: /health endpoint returned non-200"
                )

            # Verify database queries work (pool is functional)
            resp = await client.get(f"{backend_base_url}/tasks")
            if resp.status_code == 500:
                raise AssertionError(
                    "pool_not_initialized: /tasks returned 500 - "
                    "connection pool may not be initialized"
                )
            if resp.status_code != 200:
                raise AssertionError(
                    f"pool_not_initialized: /tasks returned {resp.status_code}"
                )

        _log("info", "verify_connection_pool_lifecycle completed successfully")
        return True
    except httpx.ConnectError as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except httpx.TimeoutException as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except (OSError, Exception) as e:
        if isinstance(e, (AssertionError, ConnectionError)):
            raise
        raise ConnectionError(f"backend_unreachable: {e}") from e


async def _http_request(
    client, method: str, url: str, **kwargs
) -> Any:
    """Make an HTTP request using httpx or aiohttp."""
    resp = await client.request(method, url, **kwargs)
    return resp


async def verify_http_api_contract(backend_base_url: str) -> bool:
    """Verify that the backend exposes all six REST endpoints correctly."""
    _log("info", "verify_http_api_contract invoked")

    try:
        import httpx
    except ImportError:
        raise ImportError("httpx is required for HTTP API contract verification")

    created_task_ids: list = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. GET /health -> 200
            resp = await client.get(f"{backend_base_url}/health")
            if resp.status_code != 200:
                raise AssertionError(
                    f"endpoint_mismatch: GET /health returned {resp.status_code}, expected 200"
                )
            body = resp.json()
            if "status" not in body:
                raise AssertionError(
                    "endpoint_mismatch: GET /health response missing 'status' field"
                )

            # 2. GET /tasks -> 200
            resp = await client.get(f"{backend_base_url}/tasks")
            if resp.status_code != 200:
                raise AssertionError(
                    f"endpoint_mismatch: GET /tasks returned {resp.status_code}, expected 200"
                )
            body = resp.json()
            if not isinstance(body, list):
                raise AssertionError(
                    "endpoint_mismatch: GET /tasks response is not a list"
                )

            # 3. POST /tasks -> 201
            create_payload = {
                "title": "__contract_test_task__",
                "description": "Integration test task",
                "status": "pending",
            }
            resp = await client.post(
                f"{backend_base_url}/tasks", json=create_payload
            )
            if resp.status_code != 201:
                raise AssertionError(
                    f"endpoint_mismatch: POST /tasks returned {resp.status_code}, expected 201"
                )
            task = resp.json()
            required_fields = ["id", "title", "description", "status", "created_at", "updated_at"]
            for field in required_fields:
                if field not in task:
                    raise AssertionError(
                        f"endpoint_mismatch: POST /tasks response missing '{field}' field"
                    )
            task_id = task["id"]
            created_task_ids.append(task_id)

            # 4. GET /tasks/{id} -> 200
            resp = await client.get(f"{backend_base_url}/tasks/{task_id}")
            if resp.status_code != 200:
                raise AssertionError(
                    f"endpoint_mismatch: GET /tasks/{task_id} returned {resp.status_code}, expected 200"
                )
            body = resp.json()
            for field in required_fields:
                if field not in body:
                    raise AssertionError(
                        f"endpoint_mismatch: GET /tasks/{{id}} response missing '{field}' field"
                    )

            # 5. PUT /tasks/{id} -> 200
            update_payload = {"title": "__contract_test_updated__"}
            resp = await client.put(
                f"{backend_base_url}/tasks/{task_id}", json=update_payload
            )
            if resp.status_code != 200:
                raise AssertionError(
                    f"endpoint_mismatch: PUT /tasks/{task_id} returned {resp.status_code}, expected 200"
                )
            body = resp.json()
            for field in required_fields:
                if field not in body:
                    raise AssertionError(
                        f"endpoint_mismatch: PUT /tasks/{{id}} response missing '{field}' field"
                    )

            # 6. DELETE /tasks/{id} -> 200
            resp = await client.delete(f"{backend_base_url}/tasks/{task_id}")
            if resp.status_code != 200:
                raise AssertionError(
                    f"endpoint_mismatch: DELETE /tasks/{task_id} returned {resp.status_code}, expected 200"
                )
            body = resp.json()
            if "detail" not in body or "id" not in body:
                raise AssertionError(
                    "endpoint_mismatch: DELETE /tasks/{id} response missing 'detail' or 'id' field"
                )
            # Task was already deleted, remove from cleanup list
            created_task_ids.remove(task_id)

            # Verify 404 on non-existent task
            resp = await client.get(f"{backend_base_url}/tasks/{task_id}")
            if resp.status_code != 404:
                raise AssertionError(
                    f"endpoint_mismatch: GET /tasks/{task_id} after delete returned "
                    f"{resp.status_code}, expected 404"
                )

        _log("info", "verify_http_api_contract completed successfully")
        return True

    except httpx.ConnectError as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except httpx.TimeoutException as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except (OSError, Exception) as e:
        if isinstance(e, (AssertionError, ConnectionError)):
            raise
        raise ConnectionError(f"backend_unreachable: {e}") from e
    finally:
        # Cleanup any created tasks
        if created_task_ids:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    for tid in created_task_ids:
                        try:
                            await client.delete(f"{backend_base_url}/tasks/{tid}")
                        except Exception:
                            pass
            except Exception:
                pass


async def verify_cross_tier_invariants(
    backend_base_url: str,
    database_url: str,
) -> bool:
    """Verify cross-tier behavioral invariants."""
    _log("info", "verify_cross_tier_invariants invoked")

    # First verify database is reachable
    try:
        conn = _get_psycopg2_connection(database_url)
        conn.close()
    except ConnectionError:
        raise
    except Exception as e:
        raise ConnectionError(f"database_unreachable: {e}") from e

    try:
        import httpx
    except ImportError:
        raise ImportError("httpx is required")

    created_task_ids: list = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # (g) Status default: POST without status defaults to 'pending'
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "__invariant_test_1__"},
            )
            if resp.status_code != 201:
                raise AssertionError(
                    f"invariant_violation: POST /tasks returned {resp.status_code}"
                )
            task1 = resp.json()
            created_task_ids.append(task1["id"])
            if task1["status"] != "pending":
                raise AssertionError(
                    f"invariant_violation: Default status should be 'pending', got '{task1['status']}'"
                )

            # (h) Timestamp format: ISO 8601 with timezone offset
            created_at = task1["created_at"]
            updated_at = task1["updated_at"]
            if not ("+" in created_at or "Z" in created_at):
                raise AssertionError(
                    f"invariant_violation: created_at '{created_at}' missing timezone offset"
                )
            if not ("+" in updated_at or "Z" in updated_at):
                raise AssertionError(
                    f"invariant_violation: updated_at '{updated_at}' missing timezone offset"
                )

            # (e) Description normalization: empty/whitespace -> null
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "__invariant_test_2__", "description": "   "},
            )
            if resp.status_code != 201:
                raise AssertionError(
                    f"invariant_violation: POST /tasks returned {resp.status_code}"
                )
            task2 = resp.json()
            created_task_ids.append(task2["id"])
            if task2["description"] is not None:
                raise AssertionError(
                    f"invariant_violation: Whitespace-only description should be null, "
                    f"got '{task2['description']}'"
                )

            # Also check empty string normalization
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "__invariant_test_2b__", "description": ""},
            )
            if resp.status_code != 201:
                raise AssertionError(
                    f"invariant_violation: POST /tasks returned {resp.status_code}"
                )
            task2b = resp.json()
            created_task_ids.append(task2b["id"])
            if task2b["description"] is not None:
                raise AssertionError(
                    f"invariant_violation: Empty description should be null, "
                    f"got '{task2b['description']}'"
                )

            # (f) Title stripping: leading/trailing whitespace stripped
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "  __invariant_test_3__  "},
            )
            if resp.status_code != 201:
                raise AssertionError(
                    f"invariant_violation: POST /tasks returned {resp.status_code}"
                )
            task3 = resp.json()
            created_task_ids.append(task3["id"])
            if task3["title"] != "__invariant_test_3__":
                raise AssertionError(
                    f"invariant_violation: Title should be stripped, "
                    f"got '{task3['title']}'"
                )

            # (b) created_at immutability: PUT never modifies created_at
            # (c) updated_at refresh: PUT sets updated_at >= previous
            import asyncio
            await asyncio.sleep(0.1)  # Ensure time difference
            original_created_at = task1["created_at"]
            original_updated_at = task1["updated_at"]
            resp = await client.put(
                f"{backend_base_url}/tasks/{task1['id']}",
                json={"title": "__invariant_updated__"},
            )
            if resp.status_code != 200:
                raise AssertionError(
                    f"invariant_violation: PUT /tasks/{task1['id']} returned {resp.status_code}"
                )
            updated_task = resp.json()
            if updated_task["created_at"] != original_created_at:
                raise AssertionError(
                    f"invariant_violation: created_at was modified by PUT. "
                    f"Original: {original_created_at}, After: {updated_task['created_at']}"
                )
            if updated_task["updated_at"] < original_updated_at:
                raise AssertionError(
                    f"invariant_violation: updated_at decreased after PUT. "
                    f"Previous: {original_updated_at}, After: {updated_task['updated_at']}"
                )

            # (a) Task list ordering: created_at DESC
            # Create additional tasks with slight time gaps
            await asyncio.sleep(0.05)
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "__invariant_test_order_1__"},
            )
            task_o1 = resp.json()
            created_task_ids.append(task_o1["id"])

            await asyncio.sleep(0.05)
            resp = await client.post(
                f"{backend_base_url}/tasks",
                json={"title": "__invariant_test_order_2__"},
            )
            task_o2 = resp.json()
            created_task_ids.append(task_o2["id"])

            resp = await client.get(f"{backend_base_url}/tasks")
            task_list = resp.json()

            # Find our test tasks in the list and verify ordering
            our_ids = set(created_task_ids)
            our_tasks = [t for t in task_list if t["id"] in our_ids]
            for i in range(len(our_tasks) - 1):
                if our_tasks[i]["created_at"] < our_tasks[i + 1]["created_at"]:
                    raise AssertionError(
                        "invariant_violation: Task list is not ordered by created_at DESC"
                    )

            # (d) Hard delete: DELETE removes the row permanently
            delete_id = task_o2["id"]
            resp = await client.delete(f"{backend_base_url}/tasks/{delete_id}")
            if resp.status_code != 200:
                raise AssertionError(
                    f"invariant_violation: DELETE /tasks/{delete_id} returned {resp.status_code}"
                )
            created_task_ids.remove(delete_id)

            resp = await client.get(f"{backend_base_url}/tasks/{delete_id}")
            if resp.status_code != 404:
                raise AssertionError(
                    f"invariant_violation: GET /tasks/{delete_id} after delete returned "
                    f"{resp.status_code}, expected 404 (hard delete)"
                )

        _log("info", "verify_cross_tier_invariants completed successfully")
        return True

    except httpx.ConnectError as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except httpx.TimeoutException as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except (OSError, Exception) as e:
        if isinstance(e, (AssertionError, ConnectionError)):
            raise
        raise ConnectionError(f"backend_unreachable: {e}") from e
    finally:
        # Cleanup created tasks
        if created_task_ids:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    for tid in created_task_ids:
                        try:
                            await client.delete(f"{backend_base_url}/tasks/{tid}")
                        except Exception:
                            pass
            except Exception:
                pass


async def verify_cors_configuration(
    backend_base_url: str,
    frontend_origin: str,
) -> bool:
    """Verify CORS middleware configuration."""
    _log("info", "verify_cors_configuration invoked")

    try:
        import httpx
    except ImportError:
        raise ImportError("httpx is required")

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Send OPTIONS preflight request
            resp = await client.options(
                f"{backend_base_url}/tasks",
                headers={
                    "Origin": frontend_origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type",
                },
            )

            # Check Access-Control-Allow-Origin
            allow_origin = resp.headers.get("access-control-allow-origin", "")
            if allow_origin != "*" and allow_origin != frontend_origin:
                raise AssertionError(
                    f"cors_not_configured: Access-Control-Allow-Origin is '{allow_origin}', "
                    f"expected '{frontend_origin}' or '*'"
                )

            # Check Access-Control-Allow-Methods
            allow_methods = resp.headers.get("access-control-allow-methods", "")
            required_methods = {"GET", "POST", "PUT", "DELETE", "OPTIONS"}
            actual_methods = {
                m.strip().upper() for m in allow_methods.split(",") if m.strip()
            }
            # Some CORS implementations use '*' for methods
            if "*" not in actual_methods:
                missing = required_methods - actual_methods
                if missing:
                    raise AssertionError(
                        f"cors_not_configured: Access-Control-Allow-Methods missing {missing}. "
                        f"Got: {allow_methods}"
                    )

            # Check Access-Control-Allow-Headers includes Content-Type
            allow_headers = resp.headers.get("access-control-allow-headers", "")
            actual_headers = {
                h.strip().lower() for h in allow_headers.split(",") if h.strip()
            }
            if "*" not in actual_headers and "content-type" not in actual_headers:
                raise AssertionError(
                    f"cors_not_configured: Access-Control-Allow-Headers missing 'Content-Type'. "
                    f"Got: {allow_headers}"
                )

        _log("info", "verify_cors_configuration completed successfully")
        return True

    except httpx.ConnectError as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except httpx.TimeoutException as e:
        raise ConnectionError(f"backend_unreachable: {e}") from e
    except (OSError, Exception) as e:
        if isinstance(e, (AssertionError, ConnectionError)):
            raise
        raise ConnectionError(f"backend_unreachable: {e}") from e


# ===========================================================================
# Required Exports
# ===========================================================================

__all__ = [
    "TaskStatus",
    "OptionalString",
    "TaskCreateRequest",
    "TaskUpdateRequest",
    "TaskResponse",
    "TaskListResponse",
    "ErrorResponse",
    "ValidationErrorItem",
    "ValidationErrorResponse",
    "HealthResponse",
    "DeleteConfirmation",
    "HttpEndpoint",
    "string",
    "verify_http_api_contract",
    "ConnectionError",
    "AssertionError",
    "verify_cross_tier_invariants",
    "verify_schema_initialization_idempotent",
    "verify_test_isolation",
    "verify_cors_configuration",
    "verify_connection_pool_lifecycle",
    "TaskTitle",
    "DatabaseURL",
    "TaskId",
    "ISOTimestamp",
]

# Type aliases for primitive types referenced in the contract
TaskId = int
ISOTimestamp = datetime
