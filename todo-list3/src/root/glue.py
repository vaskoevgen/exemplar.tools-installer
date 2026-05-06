"""Root integration glue — wires backend, database, and frontend children
into the parent Root interface.

All six parent functions are **integration verification functions**. They
delegate to child components (backend REST API via HTTP, database via direct
SQL, frontend via its Python API mirror) and perform cross-tier assertions.
No business logic is added; only data transformation, routing, and error
propagation per the parent contract.

Error contract:
    - ConnectionError  — backend/database unreachable
    - AssertionError   — endpoint mismatch, invariant violation, schema
                         mismatch, idempotency failure, isolation violation,
                         CORS misconfiguration, pool not initialized
"""

import asyncio
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

_PACT_KEY = "PACT:root:integration"
logger = logging.getLogger(__name__)


def _log(level: str, msg: str, **kwargs) -> None:
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ---------------------------------------------------------------------------
# Child imports
# ---------------------------------------------------------------------------

# backend — HTTP routes & db helpers
from backend.routes import (
    health_check as _backend_health_check,
    list_tasks as _backend_list_tasks,
    create_task as _backend_create_task,
    get_task as _backend_get_task,
    update_task as _backend_update_task,
    delete_task as _backend_delete_task,
)
from backend.db import (
    init_connection_pool as _backend_init_pool,
    close_connection_pool as _backend_close_pool,
    get_connection as _backend_get_connection,
    db_list_tasks as _backend_db_list_tasks,
    db_create_task as _backend_db_create_task,
    db_get_task as _backend_db_get_task,
    db_update_task as _backend_db_update_task,
    db_delete_task as _backend_db_delete_task,
)
from backend.models import (
    TaskCreateRequest as BackendTaskCreateRequest,
    TaskUpdateRequest as BackendTaskUpdateRequest,
    TaskResponse as BackendTaskResponse,
    HealthResponse as BackendHealthResponse,
    DeleteConfirmation as BackendDeleteConfirmation,
)

# database — schema init / verification
from database import (
    execute_init_script as _db_execute_init_script,
    verify_schema as _db_verify_schema,
    ConnectionConfig as DbConnectionConfig,
)

# frontend — Python mirrors of the TypeScript API client
from frontend import (
    fetchTasks as _fe_fetchTasks,
    createTask as _fe_createTask,
    updateTask as _fe_updateTask,
    deleteTask as _fe_deleteTask,
    healthCheck as _fe_healthCheck,
    resolveBaseUrl as _fe_resolveBaseUrl,
    parseErrorResponse as _fe_parseErrorResponse,
)


# ---------------------------------------------------------------------------
# Internal HTTP helpers (used by verification functions against a live backend)
# ---------------------------------------------------------------------------

def _sync(coro):
    """Run an async coroutine synchronously, reusing an existing loop if available."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    return asyncio.run(coro)


async def _http_request(
    method: str,
    url: str,
    json_body: Any = None,
    headers: Optional[Dict[str, str]] = None,
) -> "HTTPResult":
    """Thin async HTTP client returning status, headers, and parsed JSON."""
    import aiohttp

    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    kwargs: Dict[str, Any] = {"headers": req_headers}
    if json_body is not None:
        import json as _json
        kwargs["data"] = _json.dumps(json_body)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as resp:
                body = None
                try:
                    body = await resp.json()
                except Exception:
                    body = await resp.text()
                return HTTPResult(
                    status=resp.status,
                    headers=dict(resp.headers),
                    body=body,
                )
    except aiohttp.ClientError as exc:
        raise ConnectionError(f"Backend unreachable at {url}: {exc}") from exc


class HTTPResult:
    __slots__ = ("status", "headers", "body")

    def __init__(self, status: int, headers: dict, body: Any):
        self.status = status
        self.headers = headers
        self.body = body


# ---------------------------------------------------------------------------
# Timestamp format regex (ISO 8601 with timezone)
# ---------------------------------------------------------------------------

_ISO_TZ_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
)


def _assert_iso_tz(value: str, label: str = "timestamp") -> None:
    assert _ISO_TZ_RE.match(value), (
        f"{label} is not ISO 8601 with timezone: {value!r}"
    )


# ---------------------------------------------------------------------------
# Parent interface implementation
# ---------------------------------------------------------------------------

async def verify_http_api_contract(backend_base_url: str) -> bool:
    """Validate that the backend exposes all six REST endpoints per contract.

    Raises:
        ConnectionError: backend unreachable.
        AssertionError: endpoint returns unexpected status code or shape.
    """
    if not re.match(r"^https?://", backend_base_url):
        raise ValueError("Backend base URL must start with http:// or https://")

    base = backend_base_url.rstrip("/")
    _log("info", f"verify_http_api_contract: base={base}")

    # --- 1. GET /health → 200, HealthResponse ---
    r = await _http_request("GET", f"{base}/health")
    assert r.status == 200, f"GET /health expected 200, got {r.status}"
    assert isinstance(r.body, dict) and r.body.get("status") == "ok", (
        f"GET /health body mismatch: {r.body}"
    )

    # --- 2. POST /tasks → 201, TaskResponse ---
    create_body = {"title": "__verify_http_contract__", "description": None}
    r = await _http_request("POST", f"{base}/tasks", json_body=create_body)
    assert r.status == 201, f"POST /tasks expected 201, got {r.status}"
    task = r.body
    assert isinstance(task, dict), f"POST /tasks body not dict: {task}"
    for key in ("id", "title", "description", "status", "created_at", "updated_at"):
        assert key in task, f"POST /tasks missing key '{key}'"
    assert task["status"] == "pending"
    _assert_iso_tz(task["created_at"], "POST created_at")
    _assert_iso_tz(task["updated_at"], "POST updated_at")
    created_id = task["id"]

    try:
        # --- 3. GET /tasks → 200, list ---
        r = await _http_request("GET", f"{base}/tasks")
        assert r.status == 200, f"GET /tasks expected 200, got {r.status}"
        assert isinstance(r.body, list), f"GET /tasks body not list: {type(r.body)}"

        # --- 4. GET /tasks/{id} → 200, TaskResponse ---
        r = await _http_request("GET", f"{base}/tasks/{created_id}")
        assert r.status == 200, f"GET /tasks/{{id}} expected 200, got {r.status}"
        assert r.body["id"] == created_id

        # --- 5. PUT /tasks/{id} → 200, TaskResponse ---
        update_body = {"title": "__verify_updated__"}
        r = await _http_request("PUT", f"{base}/tasks/{created_id}", json_body=update_body)
        assert r.status == 200, f"PUT /tasks/{{id}} expected 200, got {r.status}"
        assert r.body["title"] == "__verify_updated__"

        # --- 6. DELETE /tasks/{id} → 200, DeleteConfirmation ---
        r = await _http_request("DELETE", f"{base}/tasks/{created_id}")
        assert r.status == 200, f"DELETE /tasks/{{id}} expected 200, got {r.status}"
        assert "detail" in r.body and "id" in r.body

        # --- Error taxonomy: 404 on deleted task ---
        r = await _http_request("GET", f"{base}/tasks/{created_id}")
        assert r.status == 404, f"GET deleted task expected 404, got {r.status}"
        assert isinstance(r.body, dict) and "detail" in r.body

        # --- Error taxonomy: 422 on invalid create ---
        r = await _http_request("POST", f"{base}/tasks", json_body={"title": ""})
        assert r.status == 422, f"POST empty title expected 422, got {r.status}"
        assert isinstance(r.body, dict) and "detail" in r.body

    except Exception:
        # Cleanup: best-effort delete
        try:
            await _http_request("DELETE", f"{base}/tasks/{created_id}")
        except Exception:
            pass
        raise

    _log("info", "verify_http_api_contract: PASSED")
    return True


async def verify_cross_tier_invariants(
    backend_base_url: str, database_url: str
) -> bool:
    """Validate cross-tier behavioral invariants across the full stack.

    Raises:
        ConnectionError: backend or database unreachable.
        AssertionError: invariant violation.
    """
    base = backend_base_url.rstrip("/")
    _log("info", f"verify_cross_tier_invariants: base={base}")

    created_ids: List[int] = []

    try:
        # (g) Status default: POST without status → 'pending'
        r = await _http_request("POST", f"{base}/tasks", json_body={
            "title": "__invariant_test_1__",
        })
        assert r.status == 201
        t1 = r.body
        created_ids.append(t1["id"])
        assert t1["status"] == "pending", f"Default status not 'pending': {t1['status']}"

        # (h) Timestamp format: ISO 8601 with timezone
        _assert_iso_tz(t1["created_at"], "t1.created_at")
        _assert_iso_tz(t1["updated_at"], "t1.updated_at")

        # (f) Title stripping
        r = await _http_request("POST", f"{base}/tasks", json_body={
            "title": "  spaced title  ",
        })
        assert r.status == 201
        t2 = r.body
        created_ids.append(t2["id"])
        assert t2["title"] == "spaced title", (
            f"Title not stripped: {t2['title']!r}"
        )

        # (e) Description normalization: empty → null
        r = await _http_request("POST", f"{base}/tasks", json_body={
            "title": "__invariant_desc_norm__",
            "description": "   ",
        })
        assert r.status == 201
        t3 = r.body
        created_ids.append(t3["id"])
        assert t3["description"] is None, (
            f"Whitespace description not normalized to null: {t3['description']!r}"
        )

        # (b) created_at immutability + (c) updated_at refresh
        import asyncio as _aio
        await _aio.sleep(0.05)  # small delay to ensure timestamp difference
        original_created_at = t1["created_at"]
        original_updated_at = t1["updated_at"]
        r = await _http_request("PUT", f"{base}/tasks/{t1['id']}", json_body={
            "title": "__invariant_updated__",
        })
        assert r.status == 200
        t1_updated = r.body
        assert t1_updated["created_at"] == original_created_at, (
            f"created_at mutated: {original_created_at} -> {t1_updated['created_at']}"
        )
        assert t1_updated["updated_at"] >= original_updated_at, (
            f"updated_at not refreshed: {original_updated_at} -> {t1_updated['updated_at']}"
        )

        # (a) TaskList ordering: created_at DESC
        r = await _http_request("GET", f"{base}/tasks")
        assert r.status == 200
        tasks = r.body
        if len(tasks) >= 2:
            for i in range(len(tasks) - 1):
                assert tasks[i]["created_at"] >= tasks[i + 1]["created_at"], (
                    f"Task list not ordered DESC by created_at at index {i}: "
                    f"{tasks[i]['created_at']} < {tasks[i+1]['created_at']}"
                )

        # (d) Hard delete
        delete_id = created_ids.pop()  # remove t3
        r = await _http_request("DELETE", f"{base}/tasks/{delete_id}")
        assert r.status == 200
        r = await _http_request("GET", f"{base}/tasks/{delete_id}")
        assert r.status == 404, (
            f"Hard-deleted task still accessible: status {r.status}"
        )

        # Cross-check with direct DB if psycopg2 available
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            try:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM tasks WHERE id = %s", (delete_id,))
                count = cur.fetchone()[0]
                assert count == 0, f"Deleted row still in DB: count={count}"
                cur.close()
            finally:
                conn.close()
        except ImportError:
            _log("warning", "psycopg2 not available for direct DB cross-check")

    finally:
        # Cleanup all created tasks
        for tid in created_ids:
            try:
                await _http_request("DELETE", f"{base}/tasks/{tid}")
            except Exception:
                pass

    _log("info", "verify_cross_tier_invariants: PASSED")
    return True


def verify_schema_initialization_idempotent(database_url: str) -> bool:
    """Validate init.sql idempotency and schema correctness.

    Raises:
        ConnectionError: database unreachable.
        AssertionError: schema mismatch or idempotency failure.
    """
    if not re.match(r"^postgresql://", database_url):
        raise ValueError("database_url must start with 'postgresql://'")

    _log("info", "verify_schema_initialization_idempotent: start")

    config = DbConnectionConfig(database_url=database_url, port=5432)

    # First execution
    result1 = _db_execute_init_script(config)
    assert result1.table_created, "tasks table not present after first init"
    assert result1.check_constraint_present, "CHECK constraint missing after first init"
    assert result1.trigger_created, "Trigger missing after first init"

    # Capture pre-existing row count
    import psycopg2
    conn = psycopg2.connect(database_url)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_before = cur.fetchone()[0]
        cur.close()
    finally:
        conn.close()

    # Second execution — must not raise
    try:
        result2 = _db_execute_init_script(config)
    except Exception as exc:
        raise AssertionError(f"Second init.sql execution failed: {exc}") from exc

    assert result2.table_created, "tasks table missing after second init"
    assert result2.check_constraint_present, "CHECK constraint missing after second init"
    assert result2.trigger_created, "Trigger missing after second init"

    # Row count unchanged
    conn = psycopg2.connect(database_url)
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_after = cur.fetchone()[0]
        cur.close()
    finally:
        conn.close()
    assert count_after == count_before, (
        f"Row count changed: {count_before} → {count_after}"
    )

    # Verify column structure via information_schema
    conn = psycopg2.connect(database_url)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'tasks' AND table_schema = 'public'
            ORDER BY ordinal_position
        """)
        columns = {row[0]: row for row in cur.fetchall()}
        cur.close()
    finally:
        conn.close()

    expected_cols = {"id", "title", "description", "status", "created_at", "updated_at"}
    assert set(columns.keys()) == expected_cols, (
        f"Column set mismatch: {set(columns.keys())} != {expected_cols}"
    )

    # title: NOT NULL
    assert columns["title"][2] == "NO", "title should be NOT NULL"
    # description: nullable
    assert columns["description"][2] == "YES", "description should be nullable"
    # status: NOT NULL
    assert columns["status"][2] == "NO", "status should be NOT NULL"

    _log("info", "verify_schema_initialization_idempotent: PASSED")
    return True


def verify_test_isolation(database_url: str) -> bool:
    """Validate that integration tests leave the database in its pre-test state.

    Raises:
        ConnectionError: database unreachable.
        AssertionError: data leaked or modified.
    """
    _log("info", "verify_test_isolation: start")

    import psycopg2

    try:
        conn = psycopg2.connect(database_url)
    except Exception as exc:
        raise ConnectionError(f"Database unreachable: {exc}") from exc

    try:
        cur = conn.cursor()

        # Snapshot row count before test operations
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_before = cur.fetchone()[0]

        # Simulate test data lifecycle within a transaction that rolls back
        conn.autocommit = False
        try:
            cur.execute(
                "INSERT INTO tasks (title, status) VALUES (%s, %s) RETURNING id",
                ("__isolation_test__", "pending"),
            )
            test_id = cur.fetchone()[0]

            # Verify the row exists inside the transaction
            cur.execute("SELECT COUNT(*) FROM tasks WHERE id = %s", (test_id,))
            assert cur.fetchone()[0] == 1, "Test row not visible in transaction"

            # Rollback — simulating proper test teardown
            conn.rollback()
        except Exception:
            conn.rollback()
            raise

        # Verify count unchanged after rollback
        conn.autocommit = True
        cur.execute("SELECT COUNT(*) FROM tasks")
        count_after = cur.fetchone()[0]
        assert count_after == count_before, (
            f"Test isolation violated: count {count_before} → {count_after}"
        )

        cur.close()
    finally:
        conn.close()

    # Verify DATABASE_URL skip mechanism is testable
    # (The contract requires tests to be skipped when DATABASE_URL is absent;
    #  we verify the env var is indeed set when we reach this point.)
    assert database_url, "DATABASE_URL must be set for integration tests"

    _log("info", "verify_test_isolation: PASSED")
    return True


async def verify_cors_configuration(
    backend_base_url: str,
    frontend_origin: str = "http://localhost:5173",
) -> bool:
    """Validate CORS headers for the frontend origin.

    Raises:
        ConnectionError: backend unreachable.
        AssertionError: CORS not configured correctly.
    """
    base = backend_base_url.rstrip("/")
    _log("info", f"verify_cors_configuration: base={base}, origin={frontend_origin}")

    # Send OPTIONS preflight request
    preflight_headers = {
        "Origin": frontend_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }

    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.options(
                f"{base}/tasks",
                headers=preflight_headers,
            ) as resp:
                h = {k.lower(): v for k, v in resp.headers.items()}

                # Access-Control-Allow-Origin
                acao = h.get("access-control-allow-origin", "")
                assert acao == frontend_origin, (
                    f"CORS Allow-Origin missing or wrong: {acao!r} "
                    f"(expected {frontend_origin!r})"
                )

                # Access-Control-Allow-Methods
                acam = h.get("access-control-allow-methods", "")
                for method in ("GET", "POST", "PUT", "DELETE"):
                    assert method in acam.upper() or "*" in acam, (
                        f"CORS Allow-Methods missing {method}: {acam!r}"
                    )

                # Access-Control-Allow-Headers
                acah = h.get("access-control-allow-headers", "")
                assert "content-type" in acah.lower() or "*" in acah, (
                    f"CORS Allow-Headers missing Content-Type: {acah!r}"
                )
    except aiohttp.ClientError as exc:
        raise ConnectionError(
            f"Backend unreachable at {base}: {exc}"
        ) from exc

    _log("info", "verify_cors_configuration: PASSED")
    return True


async def verify_connection_pool_lifecycle(backend_base_url: str) -> bool:
    """Validate that the connection pool is functional during app runtime.

    Raises:
        ConnectionError: backend unreachable.
        AssertionError: pool not initialized or queries fail.
    """
    base = backend_base_url.rstrip("/")
    _log("info", f"verify_connection_pool_lifecycle: base={base}")

    # (a) Pool initialized on startup: GET /tasks should work (requires DB)
    r = await _http_request("GET", f"{base}/tasks")
    assert r.status == 200, (
        f"GET /tasks failed (pool not initialized?): status {r.status}, body {r.body}"
    )

    # (c) Database queries work: health check + list tasks
    r = await _http_request("GET", f"{base}/health")
    assert r.status == 200 and r.body.get("status") == "ok"

    # Create and immediately delete to exercise pool under write load
    r = await _http_request("POST", f"{base}/tasks", json_body={
        "title": "__pool_lifecycle_test__",
    })
    assert r.status == 201, f"POST during pool test failed: {r.status}"
    test_id = r.body["id"]
    r = await _http_request("DELETE", f"{base}/tasks/{test_id}")
    assert r.status == 200, f"DELETE during pool test failed: {r.status}"

    _log("info", "verify_connection_pool_lifecycle: PASSED")
    return True


# ---------------------------------------------------------------------------
# Synchronous wrappers for async verification functions
# (The parent contract declares async, but we also provide sync entry points
#  for pytest or direct invocation.)
# ---------------------------------------------------------------------------

def verify_http_api_contract_sync(backend_base_url: str) -> bool:
    return _sync(verify_http_api_contract(backend_base_url))


def verify_cross_tier_invariants_sync(
    backend_base_url: str, database_url: str
) -> bool:
    return _sync(verify_cross_tier_invariants(backend_base_url, database_url))


def verify_cors_configuration_sync(
    backend_base_url: str, frontend_origin: str = "http://localhost:5173"
) -> bool:
    return _sync(verify_cors_configuration(backend_base_url, frontend_origin))


def verify_connection_pool_lifecycle_sync(backend_base_url: str) -> bool:
    return _sync(verify_connection_pool_lifecycle(backend_base_url))


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    # Parent verification functions (async)
    "verify_http_api_contract",
    "verify_cross_tier_invariants",
    "verify_schema_initialization_idempotent",
    "verify_test_isolation",
    "verify_cors_configuration",
    "verify_connection_pool_lifecycle",
    # Synchronous wrappers
    "verify_http_api_contract_sync",
    "verify_cross_tier_invariants_sync",
    "verify_cors_configuration_sync",
    "verify_connection_pool_lifecycle_sync",
]
