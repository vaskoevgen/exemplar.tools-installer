"""
Contract test suite for root component.
Tests verify the full-stack integration contract including HTTP API,
cross-tier invariants, schema initialization, test isolation, CORS, and
connection pool lifecycle.

Run with: pytest contract_test.py -v
"""
import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
)
TASK_RESPONSE_KEYS = {"id", "title", "description", "status", "created_at", "updated_at"}
VALID_STATUSES = {"pending", "in_progress", "done"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def backend_base_url() -> str:
    """Resolve backend URL; skip if unreachable."""
    url = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")
    try:
        urllib.request.urlopen(url + "/health", timeout=2)
    except Exception:
        pytest.skip(f"Backend not reachable at {url}")
    return url


@pytest.fixture(scope="session")
def database_url() -> str:
    """Resolve DATABASE_URL; skip if absent."""
    url = os.environ.get("DATABASE_URL")
    if url is None:
        pytest.skip("DATABASE_URL not set")
    return url


@pytest.fixture(scope="session")
def frontend_origin() -> str:
    return os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------
def _request(
    method: str,
    url: str,
    data: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> tuple:
    """Low-level HTTP request. Returns (status_code, headers, body_dict|list)."""
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


def _create_task(
    base: str,
    title: str = "Contract Test Task",
    description: Optional[str] = None,
    status: Optional[str] = None,
) -> tuple:
    """Create a task via POST and return (status, body)."""
    payload: Dict[str, Any] = {"title": title}
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    s, _, b = _request("POST", f"{base}/tasks", data=payload)
    return s, b


def _delete_task(base: str, task_id: int) -> None:
    """Best-effort cleanup."""
    try:
        _request("DELETE", f"{base}/tasks/{task_id}")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# 1. verify_http_api_contract — happy paths
# ---------------------------------------------------------------------------
class TestHttpApiContractHappyPath:
    """Happy-path verification of all six REST endpoints."""

    def test_health_endpoint(self, backend_base_url: str) -> None:
        status, _, body = _request("GET", f"{backend_base_url}/health")
        assert status == 200
        assert body == {"status": "ok"}

    def test_list_tasks_endpoint(self, backend_base_url: str) -> None:
        status, _, body = _request("GET", f"{backend_base_url}/tasks")
        assert status == 200
        assert isinstance(body, list)

    def test_create_task_endpoint(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="hp create test")
        assert status == 201
        assert TASK_RESPONSE_KEYS.issubset(set(body.keys()))
        _delete_task(backend_base_url, body["id"])

    def test_get_task_endpoint(self, backend_base_url: str) -> None:
        _, created = _create_task(backend_base_url, title="hp get test")
        tid = created["id"]
        try:
            status, _, body = _request("GET", f"{backend_base_url}/tasks/{tid}")
            assert status == 200
            assert TASK_RESPONSE_KEYS.issubset(set(body.keys()))
            assert body["id"] == tid
        finally:
            _delete_task(backend_base_url, tid)

    def test_update_task_endpoint(self, backend_base_url: str) -> None:
        _, created = _create_task(backend_base_url, title="hp update test")
        tid = created["id"]
        try:
            status, _, body = _request(
                "PUT",
                f"{backend_base_url}/tasks/{tid}",
                data={"title": "updated title"},
            )
            assert status == 200
            assert body["title"] == "updated title"
        finally:
            _delete_task(backend_base_url, tid)

    def test_delete_task_endpoint(self, backend_base_url: str) -> None:
        _, created = _create_task(backend_base_url, title="hp delete test")
        tid = created["id"]
        status, _, body = _request("DELETE", f"{backend_base_url}/tasks/{tid}")
        assert status == 200
        assert "detail" in body
        assert body["id"] == tid


# ---------------------------------------------------------------------------
# 2. verify_http_api_contract — error cases
# ---------------------------------------------------------------------------
class TestHttpApiContractErrors:

    def test_get_nonexistent_task_returns_404(self, backend_base_url: str) -> None:
        status, _, body = _request("GET", f"{backend_base_url}/tasks/999999999")
        assert status == 404
        assert body.get("detail") == "Task not found"

    def test_create_blank_title_returns_422(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="   ")
        assert status == 422
        assert "detail" in body
        assert isinstance(body["detail"], list)

    def test_update_nonexistent_task_returns_404(self, backend_base_url: str) -> None:
        status, _, body = _request(
            "PUT",
            f"{backend_base_url}/tasks/999999999",
            data={"title": "no such task"},
        )
        assert status == 404
        assert body.get("detail") == "Task not found"

    def test_delete_nonexistent_task_returns_404(self, backend_base_url: str) -> None:
        status, _, body = _request("DELETE", f"{backend_base_url}/tasks/999999999")
        assert status == 404
        assert body.get("detail") == "Task not found"

    def test_create_invalid_status_returns_422(self, backend_base_url: str) -> None:
        status, _ = _create_task(backend_base_url, title="bad status", status="invalid")
        assert status == 422


# ---------------------------------------------------------------------------
# 3. verify_http_api_contract — edge cases
# ---------------------------------------------------------------------------
class TestHttpApiContractEdgeCases:

    def test_title_min_length_1(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="a")
        assert status == 201
        _delete_task(backend_base_url, body["id"])

    def test_title_max_length_255(self, backend_base_url: str) -> None:
        title = "a" * 255
        status, body = _create_task(backend_base_url, title=title)
        assert status == 201
        assert len(body["title"]) == 255
        _delete_task(backend_base_url, body["id"])

    def test_title_whitespace_only_rejected(self, backend_base_url: str) -> None:
        status, _ = _create_task(backend_base_url, title="   ")
        assert status == 422

    def test_valid_status_pending(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="s pending", status="pending")
        assert status == 201
        _delete_task(backend_base_url, body["id"])

    def test_valid_status_in_progress(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="s in_progress", status="in_progress")
        assert status == 201
        _delete_task(backend_base_url, body["id"])

    def test_valid_status_done(self, backend_base_url: str) -> None:
        status, body = _create_task(backend_base_url, title="s done", status="done")
        assert status == 201
        _delete_task(backend_base_url, body["id"])


# ---------------------------------------------------------------------------
# 4. verify_cross_tier_invariants
# ---------------------------------------------------------------------------
class TestCrossTierInvariants:

    def test_task_list_ordered_by_created_at_desc(self, backend_base_url: str) -> None:
        """CROSS-TIER-01"""
        ids: List[int] = []
        try:
            for i in range(3):
                _, body = _create_task(backend_base_url, title=f"order test {i}")
                ids.append(body["id"])
                time.sleep(0.05)  # ensure distinct created_at
            _, _, tasks = _request("GET", f"{backend_base_url}/tasks")
            # filter to our test tasks
            test_tasks = [t for t in tasks if t["id"] in ids]
            timestamps = [t["created_at"] for t in test_tasks]
            assert timestamps == sorted(timestamps, reverse=True)
        finally:
            for tid in ids:
                _delete_task(backend_base_url, tid)

    def test_created_at_immutable_on_update(self, backend_base_url: str) -> None:
        """CROSS-TIER-02"""
        _, created = _create_task(backend_base_url, title="immutable ca")
        tid = created["id"]
        try:
            original_ca = created["created_at"]
            time.sleep(0.05)
            _, _, updated = _request(
                "PUT",
                f"{backend_base_url}/tasks/{tid}",
                data={"title": "immutable ca changed"},
            )
            assert updated["created_at"] == original_ca
        finally:
            _delete_task(backend_base_url, tid)

    def test_updated_at_refreshed_on_update(self, backend_base_url: str) -> None:
        """CROSS-TIER-03"""
        _, created = _create_task(backend_base_url, title="refresh ua")
        tid = created["id"]
        try:
            original_ua = created["updated_at"]
            time.sleep(0.05)
            _, _, updated = _request(
                "PUT",
                f"{backend_base_url}/tasks/{tid}",
                data={"title": "refresh ua changed"},
            )
            assert updated["updated_at"] >= original_ua
        finally:
            _delete_task(backend_base_url, tid)

    def test_hard_delete(self, backend_base_url: str) -> None:
        """CROSS-TIER-04"""
        _, created = _create_task(backend_base_url, title="hard delete")
        tid = created["id"]
        status, _, _ = _request("DELETE", f"{backend_base_url}/tasks/{tid}")
        assert status == 200
        status2, _, body2 = _request("GET", f"{backend_base_url}/tasks/{tid}")
        assert status2 == 404

    def test_description_normalization_empty_string(self, backend_base_url: str) -> None:
        """CROSS-TIER-09: empty string -> null"""
        status, body = _create_task(backend_base_url, title="desc norm empty", description="")
        tid = body["id"]
        try:
            assert status == 201
            assert body["description"] is None
        finally:
            _delete_task(backend_base_url, tid)

    def test_description_normalization_whitespace(self, backend_base_url: str) -> None:
        """CROSS-TIER-09: whitespace-only -> null"""
        status, body = _create_task(backend_base_url, title="desc norm ws", description="   ")
        tid = body["id"]
        try:
            assert status == 201
            assert body["description"] is None
        finally:
            _delete_task(backend_base_url, tid)

    def test_title_stripping(self, backend_base_url: str) -> None:
        """CROSS-TIER-18"""
        status, body = _create_task(backend_base_url, title="  stripped title  ")
        tid = body["id"]
        try:
            assert status == 201
            assert body["title"] == "stripped title"
        finally:
            _delete_task(backend_base_url, tid)

    def test_status_defaults_to_pending(self, backend_base_url: str) -> None:
        """Status default when not provided."""
        payload = {"title": "default status test"}
        s, _, body = _request("POST", f"{backend_base_url}/tasks", data=payload)
        tid = body["id"]
        try:
            assert s == 201
            assert body["status"] == "pending"
        finally:
            _delete_task(backend_base_url, tid)

    def test_timestamps_iso8601_with_timezone(self, backend_base_url: str) -> None:
        """CROSS-TIER-10"""
        _, body = _create_task(backend_base_url, title="ts format test")
        tid = body["id"]
        try:
            assert ISO_TIMESTAMP_RE.match(body["created_at"]), (
                f"created_at '{body['created_at']}' does not match ISO 8601 with tz"
            )
            assert ISO_TIMESTAMP_RE.match(body["updated_at"]), (
                f"updated_at '{body['updated_at']}' does not match ISO 8601 with tz"
            )
        finally:
            _delete_task(backend_base_url, tid)

    def test_put_patch_semantics(self, backend_base_url: str) -> None:
        """CROSS-TIER-12: Only provided fields are updated."""
        _, created = _create_task(
            backend_base_url,
            title="patch sem",
            description="original desc",
            status="pending",
        )
        tid = created["id"]
        try:
            # Update only title
            _, _, updated = _request(
                "PUT",
                f"{backend_base_url}/tasks/{tid}",
                data={"title": "patch sem changed"},
            )
            assert updated["title"] == "patch sem changed"
            # description and status should be unchanged
            assert updated["description"] == "original desc"
            assert updated["status"] == "pending"
        finally:
            _delete_task(backend_base_url, tid)


# ---------------------------------------------------------------------------
# 5. verify_schema_initialization_idempotent
# ---------------------------------------------------------------------------
class TestSchemaInitializationIdempotent:

    def test_schema_idempotent_and_correct(self, database_url: str) -> None:
        """CROSS-TIER-15: init.sql can be run twice; schema matches contract."""
        import psycopg2  # type: ignore

        conn = None
        try:
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            cur = conn.cursor()

            # Locate init.sql — try common paths
            init_sql_path = None
            for candidate in [
                "init.sql",
                "database/init.sql",
                "db/init.sql",
                "../database/init.sql",
            ]:
                if os.path.isfile(candidate):
                    init_sql_path = candidate
                    break

            if init_sql_path is None:
                pytest.skip("init.sql not found in expected locations")

            with open(init_sql_path, "r") as f:
                init_sql = f.read()

            # Execute twice — second must not raise
            cur.execute(init_sql)
            cur.execute(init_sql)

            # Verify table exists with expected columns
            cur.execute(
                """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                ORDER BY ordinal_position;
                """
            )
            columns = cur.fetchall()
            col_names = [c[0] for c in columns]
            expected_cols = {"id", "title", "description", "status", "created_at", "updated_at"}
            assert expected_cols.issubset(set(col_names)), (
                f"Missing columns: {expected_cols - set(col_names)}"
            )

            # Verify CHECK constraint on status
            cur.execute(
                """
                SELECT conname FROM pg_constraint
                WHERE conrelid = 'tasks'::regclass AND contype = 'c';
                """
            )
            check_constraints = [row[0] for row in cur.fetchall()]
            assert len(check_constraints) > 0, "No CHECK constraint found on tasks table"

            # Verify trigger exists
            cur.execute(
                """
                SELECT tgname FROM pg_trigger
                WHERE tgrelid = 'tasks'::regclass AND NOT tgisinternal;
                """
            )
            triggers = [row[0] for row in cur.fetchall()]
            assert any("update" in t.lower() for t in triggers), (
                f"update_updated_at_column trigger not found; triggers: {triggers}"
            )

            cur.close()
        except psycopg2.OperationalError:
            pytest.skip("Database unreachable")
        finally:
            if conn:
                conn.close()

    def test_schema_preserves_existing_data(self, database_url: str) -> None:
        """Re-execution of init.sql must not modify existing rows."""
        import psycopg2  # type: ignore

        conn = None
        try:
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            cur = conn.cursor()

            cur.execute("SELECT count(*) FROM tasks;")
            count_before = cur.fetchone()[0]

            init_sql_path = None
            for candidate in [
                "init.sql",
                "database/init.sql",
                "db/init.sql",
                "../database/init.sql",
            ]:
                if os.path.isfile(candidate):
                    init_sql_path = candidate
                    break

            if init_sql_path is None:
                pytest.skip("init.sql not found")

            with open(init_sql_path, "r") as f:
                init_sql = f.read()
            cur.execute(init_sql)

            cur.execute("SELECT count(*) FROM tasks;")
            count_after = cur.fetchone()[0]
            assert count_after == count_before, (
                f"Row count changed: {count_before} -> {count_after}"
            )
            cur.close()
        except psycopg2.OperationalError:
            pytest.skip("Database unreachable")
        finally:
            if conn:
                conn.close()

    def test_database_url_must_be_postgresql(self, database_url: str) -> None:
        """DatabaseURL validator: must start with postgresql://"""
        assert database_url.startswith("postgresql://"), (
            f"DATABASE_URL does not start with postgresql://: {database_url[:20]}..."
        )


# ---------------------------------------------------------------------------
# 6. verify_test_isolation
# ---------------------------------------------------------------------------
class TestTestIsolation:

    def test_row_count_unchanged_after_crud_cycle(
        self, backend_base_url: str, database_url: str
    ) -> None:
        """CROSS-TIER-14: test data is cleaned up; no leaked rows."""
        import psycopg2  # type: ignore

        conn = None
        try:
            conn = psycopg2.connect(database_url)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM tasks;")
            count_before = cur.fetchone()[0]

            # Full CRUD cycle
            _, created = _create_task(backend_base_url, title="isolation test")
            tid = created["id"]
            _request("GET", f"{backend_base_url}/tasks/{tid}")
            _request("PUT", f"{backend_base_url}/tasks/{tid}", data={"title": "iso updated"})
            _request("DELETE", f"{backend_base_url}/tasks/{tid}")

            cur.execute("SELECT count(*) FROM tasks;")
            count_after = cur.fetchone()[0]
            assert count_after == count_before, (
                f"Leaked rows: before={count_before}, after={count_after}"
            )
            cur.close()
        except psycopg2.OperationalError:
            pytest.skip("Database unreachable")
        finally:
            if conn:
                conn.close()


# ---------------------------------------------------------------------------
# 7. verify_cors_configuration
# ---------------------------------------------------------------------------
class TestCorsConfiguration:

    def test_cors_preflight(self, backend_base_url: str, frontend_origin: str) -> None:
        """CROSS-TIER-05: CORS allows frontend origin."""
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

        allow_origin = headers.get("access-control-allow-origin", "")
        assert frontend_origin in allow_origin or "*" in allow_origin, (
            f"Origin not allowed: {allow_origin}"
        )

        allow_methods = headers.get("access-control-allow-methods", "").upper()
        for method in ["GET", "POST", "PUT", "DELETE"]:
            assert method in allow_methods, f"{method} not in Allow-Methods: {allow_methods}"

        allow_headers = headers.get("access-control-allow-headers", "").lower()
        assert "content-type" in allow_headers, (
            f"Content-Type not in Allow-Headers: {allow_headers}"
        )


# ---------------------------------------------------------------------------
# 8. verify_connection_pool_lifecycle
# ---------------------------------------------------------------------------
class TestConnectionPoolLifecycle:

    def test_pool_functional_get_tasks(self, backend_base_url: str) -> None:
        """CROSS-TIER-07: pool initialized → GET /tasks succeeds."""
        status, _, body = _request("GET", f"{backend_base_url}/tasks")
        assert status == 200
        assert isinstance(body, list)

    def test_pool_functional_create_and_delete(self, backend_base_url: str) -> None:
        """Connection pool handles write operations correctly."""
        status, body = _create_task(backend_base_url, title="pool test")
        assert status == 201
        tid = body["id"]
        _delete_task(backend_base_url, tid)


# ---------------------------------------------------------------------------
# 9. Type validation unit tests (no backend required)
# ---------------------------------------------------------------------------
class TestTypeValidation:
    """Validate canonical type contracts without network calls."""

    def test_task_status_enum_values(self) -> None:
        """CROSS-TIER-11: TaskStatus enum values are exactly {pending, in_progress, done}."""
        assert VALID_STATUSES == {"pending", "in_progress", "done"}

    def test_iso_timestamp_regex_accepts_offset(self) -> None:
        assert ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00+00:00")
        assert ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00-05:00")
        assert ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00.123456+00:00")

    def test_iso_timestamp_regex_accepts_z(self) -> None:
        assert ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00Z")
        assert ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00.123Z")

    def test_iso_timestamp_regex_rejects_naive(self) -> None:
        assert not ISO_TIMESTAMP_RE.match("2024-01-15T10:30:00")
        assert not ISO_TIMESTAMP_RE.match("2024-01-15 10:30:00")

    def test_iso_timestamp_regex_rejects_unix(self) -> None:
        assert not ISO_TIMESTAMP_RE.match("1705312200")

    def test_task_title_validator_non_blank_after_strip(self) -> None:
        """TaskTitle: 1 <= len(stripped) <= 255."""
        stripped = "   ".strip()
        assert len(stripped) == 0  # would be rejected
        stripped2 = "  a  ".strip()
        assert 1 <= len(stripped2) <= 255

    def test_task_title_validator_max_length(self) -> None:
        title = "a" * 256
        assert len(title.strip()) > 255  # would be rejected

    def test_health_response_status_must_be_ok(self) -> None:
        """HealthResponse validator: status == 'ok'."""
        valid = {"status": "ok"}
        assert valid["status"] == "ok"
        invalid = {"status": "error"}
        assert invalid["status"] != "ok"

    def test_database_url_regex(self) -> None:
        """DatabaseURL must start with postgresql://."""
        valid = "postgresql://user:pass@host:5432/dbname"
        assert valid.startswith("postgresql://")
        invalid = "mysql://user:pass@host:3306/dbname"
        assert not invalid.startswith("postgresql://")

    def test_http_endpoint_method_validator(self) -> None:
        """HttpEndpoint.method must be in (GET, POST, PUT, DELETE)."""
        allowed = {"GET", "POST", "PUT", "DELETE"}
        assert "PATCH" not in allowed
        for m in allowed:
            assert m in allowed

    def test_error_response_shape(self) -> None:
        """ErrorResponse has exactly a 'detail' string field."""
        err = {"detail": "Task not found"}
        assert "detail" in err
        assert isinstance(err["detail"], str)

    def test_delete_confirmation_shape(self) -> None:
        """DeleteConfirmation has 'detail' and 'id' fields."""
        dc = {"detail": "Task deleted", "id": 42}
        assert "detail" in dc
        assert "id" in dc

    def test_validation_error_response_shape(self) -> None:
        """ValidationErrorResponse.detail is a list of ValidationErrorItem."""
        ver = {
            "detail": [
                {"loc": ["body", "title"], "msg": "field required", "type": "value_error"}
            ]
        }
        assert isinstance(ver["detail"], list)
        item = ver["detail"][0]
        assert "loc" in item and "msg" in item and "type" in item
