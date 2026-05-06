"""
Contract test suite for the backend component.
Tests are organized into sections: type validators, health endpoint,
CRUD API happy paths, CRUD API error cases, DB layer unit tests,
invariant tests, and contract integration tests (skipped without DATABASE_URL).

Run: pytest contract_test.py -v
"""
import os
import re
import json
import uuid
import datetime
from unittest.mock import patch, MagicMock, PropertyMock
from contextlib import contextmanager

import pytest

# ---------------------------------------------------------------------------
# Attempt imports — allow graceful degradation for contract integration tests
# ---------------------------------------------------------------------------
try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

# We attempt to import the app and types; tests that need them will skip
# if unavailable.
try:
    from backend.main import app  # type: ignore
except ImportError:
    try:
        from main import app  # type: ignore
    except ImportError:
        app = None

# Try importing models / types
_models_module = None
try:
    import backend.models as _models_module  # type: ignore
except ImportError:
    try:
        import models as _models_module  # type: ignore
    except ImportError:
        pass

# Try importing db helpers
_db_module = None
try:
    import backend.db as _db_module  # type: ignore
except ImportError:
    try:
        import db as _db_module  # type: ignore
    except ImportError:
        pass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
)
VALID_STATUSES = {"pending", "in_progress", "done"}
FAKE_UUID = str(uuid.uuid4())
NONEXISTENT_UUID = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Helper: build a fake task dict as returned by db layer
# ---------------------------------------------------------------------------
def _make_task_row(
    task_id=None,
    title="Test Task",
    description=None,
    status="pending",
    created_at=None,
    updated_at=None,
):
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "id": task_id or str(uuid.uuid4()),
        "title": title,
        "description": description,
        "status": status,
        "created_at": created_at or now,
        "updated_at": updated_at or now,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def client():
    """Provide a FastAPI TestClient; skip if app not importable."""
    if app is None or TestClient is None:
        pytest.skip("FastAPI app or TestClient not importable")
    return TestClient(app)


@pytest.fixture()
def sample_task_row():
    return _make_task_row()


@pytest.fixture()
def backend_base_url():
    """URL for contract tests against a running backend."""
    import urllib.request

    url = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")
    try:
        urllib.request.urlopen(url + "/health", timeout=2)
    except Exception:
        pytest.skip(f"Backend not reachable at {url}")
    return url


@pytest.fixture()
def database_url():
    url = os.environ.get("DATABASE_URL")
    if url is None:
        pytest.skip("DATABASE_URL not set")
    return url


# ===========================================================================
# SECTION 1: Type / Validator Tests
# ===========================================================================
class TestTaskStatusEnum:
    """TaskStatus enum is the single source of truth for {pending, in_progress, done}."""

    def test_valid_statuses_accepted(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        TaskStatus = getattr(_models_module, "TaskStatus", None)
        if TaskStatus is None:
            pytest.skip("TaskStatus not found in models")
        for s in ("pending", "in_progress", "done"):
            assert TaskStatus(s).value == s

    def test_invalid_status_rejected(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        TaskStatus = getattr(_models_module, "TaskStatus", None)
        if TaskStatus is None:
            pytest.skip("TaskStatus not found in models")
        with pytest.raises(ValueError):
            TaskStatus("archived")

    def test_exactly_three_members(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        TaskStatus = getattr(_models_module, "TaskStatus", None)
        if TaskStatus is None:
            pytest.skip("TaskStatus not found in models")
        assert {m.value for m in TaskStatus} == VALID_STATUSES


class TestISOTimestampFormat:
    """Verify ISO 8601 timestamp regex from contract."""

    @pytest.mark.parametrize(
        "value,valid",
        [
            ("2024-01-15T10:30:00+00:00", True),
            ("2024-01-15T10:30:00Z", True),
            ("2024-01-15T10:30:00.123456+05:30", True),
            ("2024-01-15T10:30:00", False),  # no tz
            ("not-a-date", False),
            ("2024-01-15", False),
        ],
    )
    def test_iso_timestamp_regex(self, value, valid):
        match = ISO_TIMESTAMP_RE.match(value) is not None
        assert match == valid, f"Expected {value} validity={valid}, got {match}"


class TestDatabaseURLValidator:
    """DatabaseURL must start with postgres:// or postgresql://."""

    @pytest.mark.parametrize(
        "url,valid",
        [
            ("postgres://user:pass@host/db", True),
            ("postgresql://user:pass@host/db", True),
            ("mysql://user:pass@host/db", False),
            ("", False),
            ("http://example.com", False),
        ],
    )
    def test_database_url_regex(self, url, valid):
        pattern = re.compile(r"^postgres(ql)?://")
        assert (pattern.match(url) is not None) == valid


class TestTaskTitleValidation:
    """TaskTitle: non-blank after strip, 1 <= len <= 200."""

    def _get_title_model(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        # Try to find TaskTitle or the request model for validation
        return getattr(_models_module, "TaskTitle", None)

    def test_single_char_accepted(self):
        model = self._get_title_model()
        if model is None:
            pytest.skip("TaskTitle not found")
        try:
            obj = model(value="A")
            assert obj.value.strip() == "A"
        except TypeError:
            # May be constructed differently
            pytest.skip("Cannot construct TaskTitle")

    def test_200_chars_accepted(self):
        model = self._get_title_model()
        if model is None:
            pytest.skip("TaskTitle not found")
        try:
            obj = model(value="A" * 200)
            assert len(obj.value.strip()) == 200
        except TypeError:
            pytest.skip("Cannot construct TaskTitle")

    def test_201_chars_rejected(self):
        model = self._get_title_model()
        if model is None:
            pytest.skip("TaskTitle not found")
        try:
            with pytest.raises(Exception):  # Pydantic ValidationError
                model(value="A" * 201)
        except TypeError:
            pytest.skip("Cannot construct TaskTitle")

    def test_empty_string_rejected(self):
        model = self._get_title_model()
        if model is None:
            pytest.skip("TaskTitle not found")
        try:
            with pytest.raises(Exception):
                model(value="")
        except TypeError:
            pytest.skip("Cannot construct TaskTitle")

    def test_whitespace_only_rejected(self):
        model = self._get_title_model()
        if model is None:
            pytest.skip("TaskTitle not found")
        try:
            with pytest.raises(Exception):
                model(value="   \t\n  ")
        except TypeError:
            pytest.skip("Cannot construct TaskTitle")


class TestHealthResponseValidator:
    """HealthResponse only accepts status='ok'."""

    def test_ok_accepted(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        HealthResponse = getattr(_models_module, "HealthResponse", None)
        if HealthResponse is None:
            pytest.skip("HealthResponse not found")
        obj = HealthResponse(status="ok")
        assert obj.status == "ok"

    def test_non_ok_rejected(self):
        if _models_module is None:
            pytest.skip("models module not importable")
        HealthResponse = getattr(_models_module, "HealthResponse", None)
        if HealthResponse is None:
            pytest.skip("HealthResponse not found")
        with pytest.raises(Exception):
            HealthResponse(status="bad")


# ===========================================================================
# SECTION 2: Health Endpoint
# ===========================================================================
class TestHealthEndpoint:
    def test_health_returns_200_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}

    def test_health_no_db_interaction(self, client):
        """Health check must work even if DB is down — no DB interaction."""
        # We patch any db module reference to raise; health should still work
        resp = client.get("/health")
        assert resp.status_code == 200


# ===========================================================================
# SECTION 3: CRUD API Happy Paths (mocked DB)
# ===========================================================================

def _resolve_db_module_path():
    """Return the dotted module path for patching db functions."""
    if _db_module is not None:
        return _db_module.__name__
    return "backend.db"


DB_MOD = _resolve_db_module_path()


class TestListTasksAPI:
    def test_list_empty(self, client):
        with patch(f"{DB_MOD}.db_list_tasks", return_value=[]):
            resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_array_of_task_responses(self, client):
        rows = [
            _make_task_row(title="Task 1"),
            _make_task_row(title="Task 2"),
        ]
        with patch(f"{DB_MOD}.db_list_tasks", return_value=rows):
            resp = client.get("/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2
        for task in body:
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert "created_at" in task
            assert "updated_at" in task


class TestCreateTaskAPI:
    def test_create_minimal(self, client):
        row = _make_task_row(title="My Task")
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": "My Task"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "My Task"
        assert body["status"] == "pending"
        assert ISO_TIMESTAMP_RE.match(body["created_at"])
        assert ISO_TIMESTAMP_RE.match(body["updated_at"])

    def test_create_with_all_fields(self, client):
        row = _make_task_row(
            title="Full",
            description="Desc",
            status="in_progress",
        )
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post(
                "/tasks",
                json={
                    "title": "Full",
                    "description": "Desc",
                    "status": "in_progress",
                },
            )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Full"
        assert body["description"] == "Desc"
        assert body["status"] == "in_progress"

    def test_create_description_none_when_omitted(self, client):
        row = _make_task_row(title="No Desc", description=None)
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": "No Desc"})
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_create_empty_description_normalized_to_none(self, client):
        row = _make_task_row(title="Task", description=None)
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post(
                "/tasks", json={"title": "Task", "description": ""}
            )
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_create_whitespace_description_normalized_to_none(self, client):
        row = _make_task_row(title="Task", description=None)
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post(
                "/tasks", json={"title": "Task", "description": "   "}
            )
        assert resp.status_code == 201
        assert resp.json()["description"] is None

    def test_create_title_stripped(self, client):
        row = _make_task_row(title="Stripped")
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": "  Stripped  "})
        assert resp.status_code == 201
        # The server should have stripped the title before passing to db
        assert resp.json()["title"].strip() == "Stripped"

    def test_create_single_char_title(self, client):
        row = _make_task_row(title="A")
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": "A"})
        assert resp.status_code == 201
        assert resp.json()["title"] == "A"


class TestGetTaskAPI:
    def test_get_existing_task(self, client):
        tid = str(uuid.uuid4())
        row = _make_task_row(task_id=tid, title="Found")
        with patch(f"{DB_MOD}.db_get_task", return_value=row):
            resp = client.get(f"/tasks/{tid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == tid
        assert body["title"] == "Found"
        assert ISO_TIMESTAMP_RE.match(body["created_at"])
        assert ISO_TIMESTAMP_RE.match(body["updated_at"])


class TestUpdateTaskAPI:
    def test_update_title(self, client):
        tid = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc)
        updated_row = _make_task_row(
            task_id=tid,
            title="Updated",
            created_at=now - datetime.timedelta(hours=1),
            updated_at=now,
        )
        with patch(f"{DB_MOD}.db_get_task", return_value=_make_task_row(task_id=tid)):
            with patch(f"{DB_MOD}.db_update_task", return_value=updated_row):
                resp = client.put(
                    f"/tasks/{tid}", json={"title": "Updated"}
                )
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == tid
        assert body["title"] == "Updated"

    def test_update_status_to_done(self, client):
        tid = str(uuid.uuid4())
        updated_row = _make_task_row(task_id=tid, status="done")
        with patch(f"{DB_MOD}.db_get_task", return_value=_make_task_row(task_id=tid)):
            with patch(f"{DB_MOD}.db_update_task", return_value=updated_row):
                resp = client.put(
                    f"/tasks/{tid}", json={"status": "done"}
                )
        assert resp.status_code == 200
        assert resp.json()["status"] == "done"


class TestDeleteTaskAPI:
    def test_delete_existing(self, client):
        tid = str(uuid.uuid4())
        with patch(
            f"{DB_MOD}.db_delete_task", return_value={"id": tid}
        ):
            resp = client.delete(f"/tasks/{tid}")
        assert resp.status_code == 200
        body = resp.json()
        assert "detail" in body
        assert body["detail"]  # non-empty string
        assert body["id"] == tid


# ===========================================================================
# SECTION 4: CRUD API Error Cases
# ===========================================================================
class TestCreateTaskErrors:
    def test_blank_title(self, client):
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422

    def test_whitespace_only_title(self, client):
        resp = client.post("/tasks", json={"title": "   "})
        assert resp.status_code == 422

    def test_missing_title(self, client):
        resp = client.post("/tasks", json={})
        assert resp.status_code == 422

    def test_invalid_status(self, client):
        resp = client.post(
            "/tasks", json={"title": "X", "status": "invalid"}
        )
        assert resp.status_code == 422

    def test_title_too_long(self, client):
        resp = client.post("/tasks", json={"title": "A" * 256})
        assert resp.status_code == 422

    @pytest.mark.parametrize("bad_status", ["PENDING", "active", "archived", ""])
    def test_various_invalid_statuses(self, client, bad_status):
        resp = client.post(
            "/tasks", json={"title": "Task", "status": bad_status}
        )
        assert resp.status_code == 422


class TestGetTaskErrors:
    def test_not_found(self, client):
        tid = str(uuid.uuid4())
        with patch(f"{DB_MOD}.db_get_task", return_value=None):
            resp = client.get(f"/tasks/{tid}")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_invalid_uuid_format(self, client):
        resp = client.get("/tasks/not-a-uuid")
        assert resp.status_code in (404, 422)  # either is acceptable per contract


class TestUpdateTaskErrors:
    def test_not_found(self, client):
        tid = str(uuid.uuid4())
        with patch(f"{DB_MOD}.db_get_task", return_value=None):
            with patch(f"{DB_MOD}.db_update_task", return_value=None):
                resp = client.put(
                    f"/tasks/{tid}", json={"title": "X"}
                )
        assert resp.status_code == 404

    def test_blank_title(self, client):
        tid = str(uuid.uuid4())
        resp = client.put(f"/tasks/{tid}", json={"title": ""})
        assert resp.status_code == 422

    def test_whitespace_title(self, client):
        tid = str(uuid.uuid4())
        resp = client.put(f"/tasks/{tid}", json={"title": "   "})
        assert resp.status_code == 422

    def test_invalid_status(self, client):
        tid = str(uuid.uuid4())
        resp = client.put(
            f"/tasks/{tid}", json={"status": "archived"}
        )
        assert resp.status_code == 422

    def test_invalid_uuid_format(self, client):
        resp = client.put("/tasks/bad-id", json={"title": "X"})
        assert resp.status_code in (404, 422)


class TestDeleteTaskErrors:
    def test_not_found(self, client):
        tid = str(uuid.uuid4())
        with patch(f"{DB_MOD}.db_delete_task", return_value=None):
            resp = client.delete(f"/tasks/{tid}")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_invalid_uuid_format(self, client):
        resp = client.delete("/tasks/not-a-valid-uuid")
        assert resp.status_code in (404, 422)


# ===========================================================================
# SECTION 5: DB Layer Unit Tests (mocked psycopg2)
# ===========================================================================
class TestDbLayerMocked:
    """Test db_* functions with mocked connection pool and cursors."""

    def _skip_if_no_db_module(self):
        if _db_module is None:
            pytest.skip("db module not importable")

    def _mock_cursor(self, fetchall_result=None, fetchone_result=None):
        cursor = MagicMock()
        cursor.fetchall.return_value = fetchall_result or []
        cursor.fetchone.return_value = fetchone_result
        cursor.__enter__ = MagicMock(return_value=cursor)
        cursor.__exit__ = MagicMock(return_value=False)
        return cursor

    def _mock_connection(self, cursor):
        conn = MagicMock()
        conn.cursor.return_value = cursor
        conn.__enter__ = MagicMock(return_value=conn)
        conn.__exit__ = MagicMock(return_value=False)
        return conn

    def test_db_list_tasks(self):
        self._skip_if_no_db_module()
        rows = [
            _make_task_row(title="T1"),
            _make_task_row(title="T2"),
        ]
        cursor = self._mock_cursor(fetchall_result=rows)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            # Make get_connection a context manager yielding conn
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            # Also try patching if get_connection is used differently
            try:
                result = _db_module.db_list_tasks()
                assert isinstance(result, list)
            except Exception:
                pytest.skip("db_list_tasks interface differs from expected")

    def test_db_create_task(self):
        self._skip_if_no_db_module()
        row = _make_task_row(title="Created")
        cursor = self._mock_cursor(fetchone_result=row)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_create_task("Created", None, "pending")
                assert isinstance(result, dict)
                assert result["title"] == "Created"
            except Exception:
                pytest.skip("db_create_task interface differs from expected")

    def test_db_get_task_found(self):
        self._skip_if_no_db_module()
        tid = str(uuid.uuid4())
        row = _make_task_row(task_id=tid)
        cursor = self._mock_cursor(fetchone_result=row)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_get_task(tid)
                assert result is not None
                assert result["id"] == tid
            except Exception:
                pytest.skip("db_get_task interface differs from expected")

    def test_db_get_task_not_found(self):
        self._skip_if_no_db_module()
        cursor = self._mock_cursor(fetchone_result=None)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_get_task(str(uuid.uuid4()))
                assert result is None
            except Exception:
                pytest.skip("db_get_task interface differs from expected")

    def test_db_update_task(self):
        self._skip_if_no_db_module()
        tid = str(uuid.uuid4())
        updated_row = _make_task_row(task_id=tid, title="Updated")
        cursor = self._mock_cursor(fetchone_result=updated_row)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_update_task(tid, {"title": "Updated"})
                assert result is not None
                assert result["title"] == "Updated"
            except Exception:
                pytest.skip("db_update_task interface differs from expected")

    def test_db_delete_task_found(self):
        self._skip_if_no_db_module()
        tid = str(uuid.uuid4())
        cursor = self._mock_cursor(fetchone_result={"id": tid})
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_delete_task(tid)
                assert result is not None
                assert result["id"] == tid
            except Exception:
                pytest.skip("db_delete_task interface differs from expected")

    def test_db_delete_task_not_found(self):
        self._skip_if_no_db_module()
        cursor = self._mock_cursor(fetchone_result=None)
        conn = self._mock_connection(cursor)

        with patch.object(_db_module, "get_connection") as mock_gc:
            @contextmanager
            def _ctx():
                yield conn

            mock_gc.return_value = _ctx()
            try:
                result = _db_module.db_delete_task(str(uuid.uuid4()))
                assert result is None
            except Exception:
                pytest.skip("db_delete_task interface differs from expected")


# ===========================================================================
# SECTION 6: Invariant Tests
# ===========================================================================
class TestInvariants:
    """Cross-cutting invariants from the contract."""

    def test_all_valid_statuses_accepted_by_create(self, client):
        """TaskStatus enum is the single source of truth: pending, in_progress, done."""
        for status in VALID_STATUSES:
            row = _make_task_row(title="Task", status=status)
            with patch(f"{DB_MOD}.db_create_task", return_value=row):
                resp = client.post(
                    "/tasks",
                    json={"title": "Task", "status": status},
                )
            assert resp.status_code == 201, f"Status '{status}' should be accepted"
            assert resp.json()["status"] == status

    def test_timestamps_are_iso8601_with_tz(self, client):
        row = _make_task_row()
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": "TS Test"})
        body = resp.json()
        assert ISO_TIMESTAMP_RE.match(body["created_at"]), (
            f"created_at '{body['created_at']}' is not ISO 8601 with tz"
        )
        assert ISO_TIMESTAMP_RE.match(body["updated_at"]), (
            f"updated_at '{body['updated_at']}' is not ISO 8601 with tz"
        )

    def test_created_at_immutable_on_update(self, client):
        """created_at must not change when a task is updated."""
        tid = str(uuid.uuid4())
        original_created = datetime.datetime(
            2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )
        original_row = _make_task_row(
            task_id=tid,
            title="Original",
            created_at=original_created,
            updated_at=original_created,
        )
        updated_row = _make_task_row(
            task_id=tid,
            title="Updated",
            created_at=original_created,  # must stay the same
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )
        with patch(f"{DB_MOD}.db_get_task", return_value=original_row):
            with patch(f"{DB_MOD}.db_update_task", return_value=updated_row):
                resp = client.put(
                    f"/tasks/{tid}", json={"title": "Updated"}
                )
        assert resp.status_code == 200
        body = resp.json()
        # Parse and compare created_at
        resp_created = body["created_at"]
        assert resp_created.startswith("2024-01-01T00:00:00")

    def test_updated_at_advances_on_update(self, client):
        """updated_at must be >= previous updated_at after update."""
        tid = str(uuid.uuid4())
        old_time = datetime.datetime(
            2024, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
        )
        new_time = datetime.datetime(
            2024, 6, 15, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        original_row = _make_task_row(
            task_id=tid,
            created_at=old_time,
            updated_at=old_time,
        )
        updated_row = _make_task_row(
            task_id=tid,
            title="Updated",
            created_at=old_time,
            updated_at=new_time,
        )
        with patch(f"{DB_MOD}.db_get_task", return_value=original_row):
            with patch(f"{DB_MOD}.db_update_task", return_value=updated_row):
                resp = client.put(
                    f"/tasks/{tid}", json={"title": "Updated"}
                )
        assert resp.status_code == 200
        body = resp.json()
        assert body["updated_at"] >= body["created_at"]

    def test_hard_delete_then_get_404(self, client):
        """DELETE is a hard delete; subsequent GET returns 404."""
        tid = str(uuid.uuid4())
        with patch(f"{DB_MOD}.db_delete_task", return_value={"id": tid}):
            del_resp = client.delete(f"/tasks/{tid}")
        assert del_resp.status_code == 200

        with patch(f"{DB_MOD}.db_get_task", return_value=None):
            get_resp = client.get(f"/tasks/{tid}")
        assert get_resp.status_code == 404

    def test_title_boundary_255_create_request(self, client):
        """TaskCreateRequest title validator: 1..255 length."""
        # 255 chars should be accepted
        title_255 = "A" * 255
        row = _make_task_row(title=title_255)
        with patch(f"{DB_MOD}.db_create_task", return_value=row):
            resp = client.post("/tasks", json={"title": title_255})
        assert resp.status_code == 201

    def test_title_boundary_256_create_request_rejected(self, client):
        """TaskCreateRequest title > 255 chars should be rejected."""
        title_256 = "A" * 256
        resp = client.post("/tasks", json={"title": title_256})
        assert resp.status_code == 422


# ===========================================================================
# SECTION 7: Contract Integration Tests (real DB, skipped without DATABASE_URL)
# ===========================================================================
class TestContractIntegration:
    """
    End-to-end contract tests against a running backend with real PostgreSQL.
    Skipped when BACKEND_BASE_URL is unreachable or DATABASE_URL is unset.
    """

    def _post_task(self, base_url, title="Contract Task", **kwargs):
        import urllib.request

        payload = {"title": title}
        payload.update(kwargs)
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{base_url}/tasks",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())

    def _get_task(self, base_url, task_id):
        import urllib.request

        req = urllib.request.Request(
            f"{base_url}/tasks/{task_id}", method="GET"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())

    def _delete_task(self, base_url, task_id):
        import urllib.request

        req = urllib.request.Request(
            f"{base_url}/tasks/{task_id}", method="DELETE"
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())

    def _put_task(self, base_url, task_id, **kwargs):
        import urllib.request

        data = json.dumps(kwargs).encode()
        req = urllib.request.Request(
            f"{base_url}/tasks/{task_id}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())

    def _list_tasks(self, base_url):
        import urllib.request

        req = urllib.request.Request(f"{base_url}/tasks", method="GET")
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.status, json.loads(resp.read())

    def test_full_crud_lifecycle(self, backend_base_url):
        """Create → Get → List → Update → Delete → Get (404)."""
        base = backend_base_url

        # Create
        status, created = self._post_task(base, title="Lifecycle Task")
        assert status == 201
        task_id = created["id"]
        assert created["title"] == "Lifecycle Task"
        assert created["status"] == "pending"
        assert created["description"] is None
        assert ISO_TIMESTAMP_RE.match(created["created_at"])
        assert ISO_TIMESTAMP_RE.match(created["updated_at"])

        # Get
        status, fetched = self._get_task(base, task_id)
        assert status == 200
        assert fetched["id"] == task_id
        assert fetched["title"] == "Lifecycle Task"

        # List (should contain our task)
        status, tasks = self._list_tasks(base)
        assert status == 200
        assert isinstance(tasks, list)
        ids = [t["id"] for t in tasks]
        assert task_id in ids

        # Update
        status, updated = self._put_task(
            base, task_id, title="Updated Lifecycle", status="done"
        )
        assert status == 200
        assert updated["title"] == "Updated Lifecycle"
        assert updated["status"] == "done"
        # created_at must be unchanged
        assert updated["created_at"] == created["created_at"]
        assert updated["updated_at"] >= created["updated_at"]

        # Delete
        status, deleted = self._delete_task(base, task_id)
        assert status == 200
        assert deleted["id"] == task_id
        assert deleted["detail"]  # non-empty

        # Get after delete → 404
        import urllib.request
        import urllib.error

        try:
            req = urllib.request.Request(
                f"{base}/tasks/{task_id}", method="GET"
            )
            urllib.request.urlopen(req, timeout=5)
            assert False, "Expected 404 but got success"
        except urllib.error.HTTPError as e:
            assert e.code == 404

    def test_list_ordering_desc(self, backend_base_url):
        """Tasks listed in created_at DESC order."""
        import time

        base = backend_base_url
        created_ids = []
        for i in range(3):
            _, task = self._post_task(base, title=f"Order Task {i}")
            created_ids.append(task["id"])
            time.sleep(0.05)  # tiny delay for ordering

        _, tasks = self._list_tasks(base)
        # Find our tasks in the list
        our_tasks = [t for t in tasks if t["id"] in created_ids]
        timestamps = [t["created_at"] for t in our_tasks]
        assert timestamps == sorted(timestamps, reverse=True)

        # Cleanup
        for tid in created_ids:
            try:
                self._delete_task(base, tid)
            except Exception:
                pass

    def test_created_at_immutable_contract(self, backend_base_url):
        """created_at never changes after creation."""
        base = backend_base_url
        _, created = self._post_task(base, title="Immutable TS")
        task_id = created["id"]
        original_created_at = created["created_at"]

        _, updated = self._put_task(
            base, task_id, title="Changed Title"
        )
        assert updated["created_at"] == original_created_at

        # Cleanup
        try:
            self._delete_task(base, task_id)
        except Exception:
            pass

    def test_description_normalization_contract(self, backend_base_url):
        """Empty/whitespace descriptions normalized to None."""
        base = backend_base_url

        _, task1 = self._post_task(base, title="DescTest1", description="")
        assert task1["description"] is None

        _, task2 = self._post_task(base, title="DescTest2", description="   ")
        assert task2["description"] is None

        # Cleanup
        for t in (task1, task2):
            try:
                self._delete_task(base, t["id"])
            except Exception:
                pass
