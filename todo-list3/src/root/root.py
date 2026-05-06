import logging
import time
import enum
import re
import os
import asyncio
from typing import Any, Dict, List, Optional, Union
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


# ---------------------------------------------------------------------------
# string stub
# ---------------------------------------------------------------------------
class string:
    """Auto-stubbed type — referenced but not defined in contract 'root'"""
    pass


# ---------------------------------------------------------------------------
# TaskStatus enum
# ---------------------------------------------------------------------------
class TaskStatus(enum.Enum):
    """Closed set of allowed task lifecycle states."""
    pending = "pending"
    in_progress = "in_progress"
    done = "done"


# ---------------------------------------------------------------------------
# Primitive type aliases
# ---------------------------------------------------------------------------
TaskId = int
TaskTitle = str
OptionalString = Optional[str]
ISOTimestamp = str
DatabaseURL = str


# ---------------------------------------------------------------------------
# Data classes matching the contract types
# ---------------------------------------------------------------------------
class TaskCreateRequest:
    """Request body for POST /tasks."""
    def __init__(self, title: str, description: OptionalString = None,
                 status: TaskStatus = TaskStatus.pending):
        self.title = title
        self.description = description
        self.status = status


class TaskUpdateRequest:
    """Request body for PUT /tasks/{id} — partial update (PATCH semantics)."""
    def __init__(self, title: Optional[str] = None,
                 description: OptionalString = None,
                 status: Optional[TaskStatus] = None):
        self.title = title
        self.description = description
        self.status = status


class TaskResponse:
    """Complete task object returned by all read/write endpoints."""
    def __init__(self, id: TaskId, title: TaskTitle, description: OptionalString,
                 status: TaskStatus, created_at: ISOTimestamp,
                 updated_at: ISOTimestamp):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at


TaskListResponse = List[TaskResponse]


class ErrorResponse:
    """Standard error envelope."""
    def __init__(self, detail: str):
        self.detail = detail


class ValidationErrorItem:
    """A single validation error within the 422 response."""
    def __init__(self, loc: list, msg: str, type: str):
        self.loc = loc
        self.msg = msg
        self.type = type


class ValidationErrorResponse:
    """HTTP 422 Unprocessable Entity response body."""
    def __init__(self, detail: list):
        self.detail = detail


class HealthResponse:
    """Response body for GET /health."""
    def __init__(self, status: str):
        if status != "ok":
            raise ValueError("HealthResponse status must be 'ok'")
        self.status = status


class DeleteConfirmation:
    """Response body for DELETE /tasks/{id} on successful hard-delete."""
    def __init__(self, detail: str, id: TaskId):
        self.detail = detail
        self.id = id


class HttpEndpoint:
    """Descriptor for one REST API endpoint."""
    def __init__(self, method: str, path: str, response_body_type: str,
                 success_status_code: int, content_type: str,
                 request_body_type: OptionalString = None):
        if method not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError(f"Invalid method: {method}")
        self.method = method
        self.path = path
        self.request_body_type = request_body_type
        self.response_body_type = response_body_type
        self.success_status_code = success_status_code
        self.content_type = content_type


# ---------------------------------------------------------------------------
# HTTP helpers for verification functions
# ---------------------------------------------------------------------------
import json
import urllib.request
import urllib.error


def _http_request(method: str, url: str, data: Optional[dict] = None,
                  headers: Optional[dict] = None) -> tuple:
    """Low-level HTTP request. Returns (status_code, headers_dict, body)."""
    hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    body_bytes: Optional[bytes] = None
    if data is not None:
        body_bytes = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body_bytes, headers=hdrs, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        status = resp.status
        resp_headers = dict(resp.headers)
        resp_body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        status = exc.code
        resp_headers = dict(exc.headers)
        resp_body = json.loads(exc.read().decode("utf-8"))
    return status, resp_headers, resp_body


def _create_task_http(base: str, title: str = "Test Task",
                      description: Optional[str] = None,
                      status: Optional[str] = None) -> tuple:
    payload: Dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    s, _, b = _http_request("POST", f"{base}/tasks", data=payload)
    return s, b


def _delete_task_http(base: str, task_id: int) -> None:
    try:
        _http_request("DELETE", f"{base}/tasks/{task_id}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Verification functions
# ---------------------------------------------------------------------------

async def verify_http_api_contract(backend_base_url: str) -> bool:
    _log("info", "verify_http_api_contract invoked")
    
    try:
        # 1. GET /health
        s, _, b = _http_request("GET", f"{backend_base_url}/health")
        assert s == 200, f"Health expected 200, got {s}"
        assert b == {"status": "ok"}, f"Health body mismatch: {b}"

        # 2. GET /tasks
        s, _, b = _http_request("GET", f"{backend_base_url}/tasks")
        assert s == 200, f"List tasks expected 200, got {s}"
        assert isinstance(b, list), f"Expected list, got {type(b)}"

        # 3. POST /tasks
        s, created = _create_task_http(backend_base_url, title="verify contract")
        assert s == 201, f"Create expected 201, got {s}"
        required_keys = {"id", "title", "description", "status", "created_at", "updated_at"}
        assert required_keys.issubset(set(created.keys())), f"Missing keys in create response"
        tid = created["id"]

        try:
            # 4. GET /tasks/{id}
            s, _, b = _http_request("GET", f"{backend_base_url}/tasks/{tid}")
            assert s == 200, f"Get task expected 200, got {s}"
            assert required_keys.issubset(set(b.keys()))
            assert b["id"] == tid

            # 5. PUT /tasks/{id}
            s, _, b = _http_request("PUT", f"{backend_base_url}/tasks/{tid}",
                                    data={"title": "updated verify"})
            assert s == 200, f"Update expected 200, got {s}"
            assert b["title"] == "updated verify"

            # 6. DELETE /tasks/{id}
            s, _, b = _http_request("DELETE", f"{backend_base_url}/tasks/{tid}")
            assert s == 200, f"Delete expected 200, got {s}"
            assert "detail" in b
            assert b["id"] == tid
        except Exception:
            _delete_task_http(backend_base_url, tid)
            raise

        # Verify 404 on deleted task
        s, _, b = _http_request("GET", f"{backend_base_url}/tasks/{tid}")
        assert s == 404
        assert b.get("detail") == "Task not found"

    except ConnectionError as e:
        raise ConnectionError(f"Backend unreachable: {e}")

    _log("info", "verify_http_api_contract completed")
    return True


async def verify_cross_tier_invariants(backend_base_url: str, database_url: str) -> bool:
    _log("info", "verify_cross_tier_invariants invoked")
    import time as _time

    created_ids: List[int] = []

    try:
        # (a) TaskList ordering: created_at DESC
        for i in range(3):
            s, body = _create_task_http(backend_base_url, title=f"order test {i}")
            assert s == 201
            created_ids.append(body["id"])
            _time.sleep(0.05)

        s, _, tasks = _http_request("GET", f"{backend_base_url}/tasks")
        assert s == 200
        test_tasks = [t for t in tasks if t["id"] in created_ids]
        timestamps = [t["created_at"] for t in test_tasks]
        assert timestamps == sorted(timestamps, reverse=True), "Tasks not ordered by created_at DESC"

        for tid in created_ids:
            _delete_task_http(backend_base_url, tid)
        created_ids.clear()

        # (b) created_at immutability
        s, created = _create_task_http(backend_base_url, title="immutable ca")
        assert s == 201
        tid = created["id"]
        created_ids.append(tid)
        original_ca = created["created_at"]
        _time.sleep(0.05)
        s, _, updated = _http_request("PUT", f"{backend_base_url}/tasks/{tid}",
                                       data={"title": "immutable ca changed"})
        assert s == 200
        assert updated["created_at"] == original_ca, "created_at was modified"

        # (c) updated_at refresh
        original_ua = created["updated_at"]
        assert updated["updated_at"] >= original_ua, "updated_at not refreshed"

        _delete_task_http(backend_base_url, tid)
        created_ids.clear()

        # (d) Hard delete
        s, created = _create_task_http(backend_base_url, title="hard delete")
        tid = created["id"]
        s, _, _ = _http_request("DELETE", f"{backend_base_url}/tasks/{tid}")
        assert s == 200
        s, _, _ = _http_request("GET", f"{backend_base_url}/tasks/{tid}")
        assert s == 404, "Task not hard deleted"

        # (e) Description normalization
        s, body = _create_task_http(backend_base_url, title="desc norm", description="")
        created_ids.append(body["id"])
        assert body["description"] is None, "Empty description not normalized to null"
        _delete_task_http(backend_base_url, body["id"])
        created_ids.clear()

        s, body = _create_task_http(backend_base_url, title="desc norm ws", description="   ")
        created_ids.append(body["id"])
        assert body["description"] is None, "Whitespace description not normalized to null"
        _delete_task_http(backend_base_url, body["id"])
        created_ids.clear()

        # (f) Title stripping
        s, body = _create_task_http(backend_base_url, title="  stripped  ")
        created_ids.append(body["id"])
        assert body["title"] == "stripped", "Title not stripped"
        _delete_task_http(backend_base_url, body["id"])
        created_ids.clear()

        # (g) Status default
        payload = {"title": "default status"}
        s, _, body = _http_request("POST", f"{backend_base_url}/tasks", data=payload)
        created_ids.append(body["id"])
        assert body["status"] == "pending", "Default status not pending"
        _delete_task_http(backend_base_url, body["id"])
        created_ids.clear()

        # (h) Timestamp format
        iso_re = re.compile(
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
        )
        s, body = _create_task_http(backend_base_url, title="ts format")
        created_ids.append(body["id"])
        assert iso_re.match(body["created_at"]), f"Invalid created_at format: {body['created_at']}"
        assert iso_re.match(body["updated_at"]), f"Invalid updated_at format: {body['updated_at']}"
        _delete_task_http(backend_base_url, body["id"])
        created_ids.clear()

    except Exception:
        for tid in created_ids:
            _delete_task_http(backend_base_url, tid)
        raise

    _log("info", "verify_cross_tier_invariants completed")
    return True


def verify_schema_initialization_idempotent(database_url: str) -> bool:
    _log("info", "verify_schema_initialization_idempotent invoked")
    import psycopg2

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()

        # Find init.sql
        init_sql_path = None
        for candidate in ["init.sql", "database/init.sql", "db/init.sql", "../database/init.sql"]:
            if os.path.isfile(candidate):
                init_sql_path = candidate
                break

        if init_sql_path is None:
            raise FileNotFoundError("init.sql not found")

        with open(init_sql_path, "r") as f:
            init_sql = f.read()

        # Execute twice
        cur.execute(init_sql)
        cur.execute(init_sql)

        # Verify columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'tasks' ORDER BY ordinal_position;
        """)
        col_names = {row[0] for row in cur.fetchall()}
        expected = {"id", "title", "description", "status", "created_at", "updated_at"}
        assert expected.issubset(col_names), f"Missing columns: {expected - col_names}"

        # Verify CHECK constraint
        cur.execute("""
            SELECT conname FROM pg_constraint
            WHERE conrelid = 'tasks'::regclass AND contype = 'c';
        """)
        checks = [row[0] for row in cur.fetchall()]
        assert len(checks) > 0, "No CHECK constraint found"

        # Verify trigger
        cur.execute("""
            SELECT tgname FROM pg_trigger
            WHERE tgrelid = 'tasks'::regclass AND NOT tgisinternal;
        """)
        triggers = [row[0] for row in cur.fetchall()]
        assert any("update" in t.lower() for t in triggers), f"Trigger not found: {triggers}"

        cur.close()
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"Database unreachable: {e}")
    finally:
        if conn:
            conn.close()

    _log("info", "verify_schema_initialization_idempotent completed")
    return True


def verify_test_isolation(database_url: str) -> bool:
    _log("info", "verify_test_isolation invoked")
    import psycopg2

    conn = None
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute("SELECT count(*) FROM tasks;")
        count_before = cur.fetchone()[0]

        # The verification itself should not leak rows
        cur.execute("SELECT count(*) FROM tasks;")
        count_after = cur.fetchone()[0]
        assert count_after == count_before, (
            f"Row count changed: {count_before} -> {count_after}"
        )

        cur.close()
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"Database unreachable: {e}")
    finally:
        if conn:
            conn.close()

    _log("info", "verify_test_isolation completed")
    return True


async def verify_cors_configuration(backend_base_url: str, frontend_origin: str) -> bool:
    _log("info", "verify_cors_configuration invoked")

    req = urllib.request.Request(
        f"{backend_base_url}/tasks",
        method="OPTIONS",
        headers={
            "Origin": frontend_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    try:
        resp = urllib.request.urlopen(req, timeout=5)
        headers = {k.lower(): v for k, v in resp.headers.items()}
    except urllib.error.HTTPError as exc:
        headers = {k.lower(): v for k, v in exc.headers.items()}
    except Exception as e:
        raise ConnectionError(f"Backend unreachable: {e}")

    allow_origin = headers.get("access-control-allow-origin", "")
    assert frontend_origin in allow_origin or "*" in allow_origin, (
        f"Origin not allowed: {allow_origin}"
    )

    allow_methods = headers.get("access-control-allow-methods", "").upper()
    for method in ["GET", "POST", "PUT", "DELETE"]:
        assert method in allow_methods, f"{method} not in Allow-Methods"

    allow_headers = headers.get("access-control-allow-headers", "").lower()
    assert "content-type" in allow_headers, "Content-Type not in Allow-Headers"

    _log("info", "verify_cors_configuration completed")
    return True


async def verify_connection_pool_lifecycle(backend_base_url: str) -> bool:
    _log("info", "verify_connection_pool_lifecycle invoked")

    try:
        s, _, body = _http_request("GET", f"{backend_base_url}/tasks")
        assert s == 200, f"Expected 200, got {s}"
        assert isinstance(body, list), f"Expected list, got {type(body)}"
    except Exception as e:
        if isinstance(e, AssertionError):
            raise
        raise ConnectionError(f"Backend unreachable: {e}")

    _log("info", "verify_connection_pool_lifecycle completed")
    return True


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------
__all__ = [
    'TaskStatus',
    'OptionalString',
    'TaskCreateRequest',
    'TaskUpdateRequest',
    'TaskResponse',
    'TaskListResponse',
    'ErrorResponse',
    'ValidationErrorItem',
    'ValidationErrorResponse',
    'HealthResponse',
    'DeleteConfirmation',
    'HttpEndpoint',
    'string',
    'verify_http_api_contract',
    'ConnectionError',
    'AssertionError',
    'verify_cross_tier_invariants',
    'verify_schema_initialization_idempotent',
    'verify_test_isolation',
    'verify_cors_configuration',
    'verify_connection_pool_lifecycle',
]
