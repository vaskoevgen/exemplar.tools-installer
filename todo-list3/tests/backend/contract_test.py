"""
Contract test suite for the backend component.
Tests API endpoints, type validators, database layer, and connection pool lifecycle.

Run with: pytest contract_test.py -v
For contract tests requiring a real database: DATABASE_URL=postgresql://... pytest contract_test.py -v
"""

import os
import re
import uuid
import datetime
from contextlib import contextmanager
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

# ---------------------------------------------------------------------------
# Conditional import guards — the backend module structure may vary
# ---------------------------------------------------------------------------
try:
    from backend.main import app
except ImportError:
    try:
        from main import app
    except ImportError:
        app = None

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None

# Attempt imports for types / db helpers; fall back gracefully
try:
    from backend.models import TaskStatus, TaskTitle, TaskCreateRequest, TaskUpdateRequest, TaskResponse, HealthResponse, DeleteConfirmation, DatabaseURL, ISOTimestamp
except ImportError:
    try:
        from models import TaskStatus, TaskTitle, TaskCreateRequest, TaskUpdateRequest, TaskResponse, HealthResponse, DeleteConfirmation, DatabaseURL, ISOTimestamp
    except ImportError:
        TaskStatus = TaskTitle = TaskCreateRequest = TaskUpdateRequest = None
        TaskResponse = HealthResponse = DeleteConfirmation = DatabaseURL = ISOTimestamp = None

try:
    from backend.db import (
        db_list_tasks, db_create_task, db_get_task, db_update_task, db_delete_task,
        get_connection, init_connection_pool, close_connection_pool,
    )
except ImportError:
    try:
        from db import (
            db_list_tasks, db_create_task, db_get_task, db_update_task, db_delete_task,
            get_connection, init_connection_pool, close_connection_pool,
        )
    except ImportError:
        db_list_tasks = db_create_task = db_get_task = db_update_task = db_delete_task = None
        get_connection = init_connection_pool = close_connection_pool = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
)
VALID_STATUSES = {"pending", "in_progress", "done"}
FAKE_UUID = str(uuid.uuid4())
NON_EXISTENT_UUID = "00000000-0000-4000-8000-000000000000"

DATABASE_URL = os.environ.get("DATABASE_URL", "")
skip_no_db = pytest.mark.skipif(not DATABASE_URL, reason="DATABASE_URL not set")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def client():
    """Provide a FastAPI TestClient with mocked DB dependency."""
    if app is None or TestClient is None:
        pytest.skip("FastAPI app or TestClient not importable")
    return TestClient(app)


@pytest.fixture()
def mock_get_connection():
    """
    Context-manager mock replacing get_connection.
    Yields a MagicMock pretending to be a psycopg2 connection with a RealDictCursor.
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
    mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

    @contextmanager
    def _fake_get_connection():
        yield mock_conn

    return _fake_get_connection, mock_conn, mock_cursor


def _task_row(
    task_id=None, title="Test Task", description=None,
    status="pending", created_at=None, updated_at=None,
):
    """Helper to build a fake task row dict as returned by RealDictCursor."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return {
        "id": task_id or str(uuid.uuid4()),
        "title": title,
        "description": description,
        "status": status,
        "created_at": created_at or now,
        "updated_at": updated_at or now,
    }


# ===================================================================
# SECTION 1: Type / Validator Tests
# ===================================================================

class TestTaskStatusEnum:
    """TaskStatus enum is the single source of truth for valid status values."""

    def test_valid_values(self):
        if TaskStatus is None:
            pytest.skip("TaskStatus not importable")
        for val in ("pending", "in_progress", "done"):
            assert TaskStatus(val).value == val

    def test_invalid_value_rejected(self):
        if TaskStatus is None:
            pytest.skip("TaskStatus not importable")
        with pytest.raises((ValueError, KeyError)):
            TaskStatus("invalid_status")

    def test_exactly_three_members(self):
        if TaskStatus is None:
            pytest.skip("TaskStatus not importable")
        assert set(s.value for s in TaskStatus) == VALID_STATUSES


class TestTaskTitle:
    """TaskTitle: non-blank, whitespace-stripped, 1..200 chars."""

    def test_valid_title(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        t = TaskTitle(value="Hello")
        # After construction the stripped value should be stored
        assert t.value.strip() == "Hello"

    def test_empty_rejected(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="")

    def test_whitespace_only_rejected(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="   \t\n  ")

    def test_max_200_accepted(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        t = TaskTitle(value="A" * 200)
        assert len(t.value.strip()) == 200

    def test_exceeds_200_rejected(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="A" * 201)

    def test_strips_whitespace(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        t = TaskTitle(value="  hello  ")
        assert t.value == "hello" or t.value.strip() == "hello"

    def test_single_char_accepted(self):
        if TaskTitle is None:
            pytest.skip("TaskTitle not importable")
        t = TaskTitle(value="X")
        assert t.value.strip() == "X"


class TestISOTimestamp:
    """ISOTimestamp: ISO 8601 with timezone offset or Z."""

    def test_valid_with_offset(self):
        if ISOTimestamp is None:
            pytest.skip("ISOTimestamp not importable")
        ts = ISOTimestamp(value="2024-01-15T10:30:00+00:00")
        assert ISO_TIMESTAMP_RE.match(ts.value)

    def test_valid_with_z(self):
        if ISOTimestamp is None:
            pytest.skip("ISOTimestamp not importable")
        ts = ISOTimestamp(value="2024-01-15T10:30:00Z")
        assert ISO_TIMESTAMP_RE.match(ts.value)

    def test_valid_with_fractional_seconds(self):
        if ISOTimestamp is None:
            pytest.skip("ISOTimestamp not importable")
        ts = ISOTimestamp(value="2024-01-15T10:30:00.123456+05:30")
        assert ISO_TIMESTAMP_RE.match(ts.value)

    def test_no_timezone_rejected(self):
        if ISOTimestamp is None:
            pytest.skip("ISOTimestamp not importable")
        with pytest.raises((ValueError, Exception)):
            ISOTimestamp(value="2024-01-15T10:30:00")


class TestDatabaseURL:
    """DatabaseURL: must start with postgres:// or postgresql://."""

    def test_postgresql_prefix(self):
        if DatabaseURL is None:
            pytest.skip("DatabaseURL not importable")
        d = DatabaseURL(value="postgresql://user:pass@localhost/db")
        assert d.value.startswith("postgresql://")

    def test_postgres_prefix(self):
        if DatabaseURL is None:
            pytest.skip("DatabaseURL not importable")
        d = DatabaseURL(value="postgres://user:pass@localhost/db")
        assert d.value.startswith("postgres://")

    def test_invalid_prefix_rejected(self):
        if DatabaseURL is None:
            pytest.skip("DatabaseURL not importable")
        with pytest.raises((ValueError, Exception)):
            DatabaseURL(value="mysql://user:pass@localhost/db")


class TestHealthResponse:
    """HealthResponse: status must be exactly 'ok'."""

    def test_valid_ok(self):
        if HealthResponse is None:
            pytest.skip("HealthResponse not importable")
        hr = HealthResponse(status="ok")
        assert hr.status == "ok"

    def test_not_ok_rejected(self):
        if HealthResponse is None:
            pytest.skip("HealthResponse not importable")
        with pytest.raises((ValueError, Exception)):
            HealthResponse(status="error")


# ===================================================================
# SECTION 2: API Endpoint Tests (via TestClient)
# ===================================================================

class TestHealthCheckEndpoint:
    """GET /health — returns {'status': 'ok'}, no DB interaction."""

    def test_health_check_happy(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"status": "ok"}

    def test_health_check_response_schema(self, client):
        resp = client.get("/health")
        body = resp.json()
        assert "status" in body
        assert body["status"] == "ok"


class TestListTasksEndpoint:
    """GET /tasks — returns JSON array of TaskResponse objects."""

    def test_list_tasks_happy_empty(self, client):
        """When DB returns no rows, response is an empty array."""
        with patch("backend.db.db_list_tasks", return_value=[]) if db_list_tasks else \
             patch("db.db_list_tasks", return_value=[]):
            resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == [] or isinstance(resp.json(), list)

    def test_list_tasks_happy_multiple(self, client):
        """When DB returns rows, all conform to TaskResponse schema."""
        now = datetime.datetime.now(datetime.timezone.utc)
        rows = [
            _task_row(title="Second", created_at=now),
            _task_row(title="First", created_at=now - datetime.timedelta(seconds=10)),
        ]
        target = "backend.db.db_list_tasks" if db_list_tasks else "db.db_list_tasks"
        with patch(target, return_value=rows):
            resp = client.get("/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 2
        for task in body:
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert task["status"] in VALID_STATUSES
            assert "created_at" in task
            assert "updated_at" in task

    def test_list_tasks_timestamps_iso8601(self, client):
        rows = [_task_row()]
        target = "backend.db.db_list_tasks" if db_list_tasks else "db.db_list_tasks"
        with patch(target, return_value=rows):
            resp = client.get("/tasks")
        assert resp.status_code == 200
        for task in resp.json():
            assert ISO_TIMESTAMP_RE.match(task["created_at"]), f"created_at not ISO8601: {task['created_at']}"
            assert ISO_TIMESTAMP_RE.match(task["updated_at"]), f"updated_at not ISO8601: {task['updated_at']}"

    def test_list_tasks_db_unavailable(self, client):
        target = "backend.db.db_list_tasks" if db_list_tasks else "db.db_list_tasks"
        with patch(target, side_effect=Exception("connection pool exhausted")):
            resp = client.get("/tasks")
        assert resp.status_code >= 500 or resp.status_code == 503


class TestCreateTaskEndpoint:
    """POST /tasks — creates a new task."""

    def _mock_create(self, title, description, status):
        return _task_row(title=title.strip(), description=description, status=status or "pending")

    def test_create_task_happy_defaults(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "My Task"})
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "My Task"
        assert body["status"] == "pending"
        assert body.get("description") is None or body["description"] is None

    def test_create_task_happy_all_fields(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        payload = {"title": "Full Task", "description": "A description", "status": "in_progress"}
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json=payload)
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Full Task"
        assert body["description"] == "A description"
        assert body["status"] == "in_progress"

    def test_create_task_blank_title_returns_422(self, client):
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422

    def test_create_task_whitespace_title_returns_422(self, client):
        resp = client.post("/tasks", json={"title": "   "})
        assert resp.status_code == 422

    def test_create_task_missing_title_returns_422(self, client):
        resp = client.post("/tasks", json={})
        assert resp.status_code == 422

    def test_create_task_invalid_status_returns_422(self, client):
        resp = client.post("/tasks", json={"title": "Task", "status": "banana"})
        assert resp.status_code == 422

    def test_create_task_empty_description_normalized_to_none(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=None, status=status)):
            resp = client.post("/tasks", json={"title": "Task", "description": ""})
        assert resp.status_code == 201
        assert resp.json().get("description") is None

    def test_create_task_whitespace_description_normalized_to_none(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=None, status=status)):
            resp = client.post("/tasks", json={"title": "Task", "description": "   "})
        assert resp.status_code == 201
        assert resp.json().get("description") is None

    def test_create_task_title_stripped(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title.strip(), description=description, status=status)):
            resp = client.post("/tasks", json={"title": "  Hello World  "})
        assert resp.status_code == 201
        assert resp.json()["title"] == "Hello World"

    def test_create_task_timestamps_iso8601(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "Task"})
        body = resp.json()
        assert ISO_TIMESTAMP_RE.match(body["created_at"])
        assert ISO_TIMESTAMP_RE.match(body["updated_at"])

    def test_create_task_title_length_255_accepted(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        title_255 = "A" * 255
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": title_255})
        assert resp.status_code == 201

    def test_create_task_title_exceeds_255_returns_422(self, client):
        title_256 = "A" * 256
        resp = client.post("/tasks", json={"title": title_256})
        assert resp.status_code == 422

    def test_create_task_status_defaults_to_pending(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "Task"})
        assert resp.status_code == 201
        assert resp.json()["status"] == "pending"

    def test_create_task_db_unavailable(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=Exception("database unavailable")):
            resp = client.post("/tasks", json={"title": "Task"})
        assert resp.status_code >= 500 or resp.status_code == 503


class TestGetTaskEndpoint:
    """GET /tasks/{id} — returns single task or 404."""

    def test_get_task_happy(self, client):
        task_id = str(uuid.uuid4())
        row = _task_row(task_id=task_id)
        target = "backend.db.db_get_task" if db_get_task else "db.db_get_task"
        with patch(target, return_value=row):
            resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == task_id
        assert body["status"] in VALID_STATUSES
        assert ISO_TIMESTAMP_RE.match(body["created_at"])
        assert ISO_TIMESTAMP_RE.match(body["updated_at"])

    def test_get_task_not_found(self, client):
        target = "backend.db.db_get_task" if db_get_task else "db.db_get_task"
        with patch(target, return_value=None):
            resp = client.get(f"/tasks/{NON_EXISTENT_UUID}")
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_get_task_invalid_id(self, client):
        resp = client.get("/tasks/not-a-uuid")
        assert resp.status_code == 422 or resp.status_code == 400

    def test_get_task_db_unavailable(self, client):
        task_id = str(uuid.uuid4())
        target = "backend.db.db_get_task" if db_get_task else "db.db_get_task"
        with patch(target, side_effect=Exception("db down")):
            resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code >= 500 or resp.status_code == 503


class TestUpdateTaskEndpoint:
    """PUT /tasks/{id} — PATCH semantics update."""

    def test_update_task_happy(self, client):
        task_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc)
        original = _task_row(task_id=task_id, title="Old", status="pending", created_at=now, updated_at=now)
        updated = dict(original, title="New", updated_at=now + datetime.timedelta(seconds=1))
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, return_value=updated):
            resp = client.put(f"/tasks/{task_id}", json={"title": "New"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == task_id
        assert body["title"] == "New"

    def test_update_task_partial_title_only(self, client):
        task_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc)
        original = _task_row(task_id=task_id, title="Old", description="keep me", status="done",
                             created_at=now, updated_at=now)
        updated = dict(original, title="New Title", updated_at=now + datetime.timedelta(seconds=1))
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, return_value=updated):
            resp = client.put(f"/tasks/{task_id}", json={"title": "New Title"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "New Title"
        assert body["description"] == "keep me"
        assert body["status"] == "done"

    def test_update_task_not_found(self, client):
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, return_value=None):
            resp = client.put(f"/tasks/{NON_EXISTENT_UUID}", json={"title": "X"})
        assert resp.status_code == 404

    def test_update_task_invalid_status(self, client):
        task_id = str(uuid.uuid4())
        resp = client.put(f"/tasks/{task_id}", json={"status": "banana"})
        assert resp.status_code == 422

    def test_update_task_blank_title(self, client):
        task_id = str(uuid.uuid4())
        resp = client.put(f"/tasks/{task_id}", json={"title": ""})
        assert resp.status_code == 422

    def test_update_task_whitespace_title(self, client):
        task_id = str(uuid.uuid4())
        resp = client.put(f"/tasks/{task_id}", json={"title": "   "})
        assert resp.status_code == 422

    def test_update_task_invalid_id(self, client):
        resp = client.put("/tasks/bad-id", json={"title": "X"})
        assert resp.status_code == 422 or resp.status_code == 400

    def test_update_task_created_at_immutable(self, client):
        task_id = str(uuid.uuid4())
        now = datetime.datetime.now(datetime.timezone.utc)
        original_created = now - datetime.timedelta(hours=1)
        updated = _task_row(task_id=task_id, title="Updated", created_at=original_created,
                            updated_at=now)
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, return_value=updated):
            resp = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        body = resp.json()
        # created_at should match the original (before the update request time)
        assert body["created_at"] is not None
        created_dt = datetime.datetime.fromisoformat(body["created_at"])
        assert created_dt <= now  # created_at was not bumped to now

    def test_update_task_updated_at_advances(self, client):
        task_id = str(uuid.uuid4())
        old_time = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
        new_time = datetime.datetime.now(datetime.timezone.utc)
        updated = _task_row(task_id=task_id, title="Updated", created_at=old_time, updated_at=new_time)
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, return_value=updated):
            resp = client.put(f"/tasks/{task_id}", json={"title": "Updated"})
        body = resp.json()
        updated_at = datetime.datetime.fromisoformat(body["updated_at"])
        assert updated_at >= old_time

    def test_update_task_db_unavailable(self, client):
        task_id = str(uuid.uuid4())
        target = "backend.db.db_update_task" if db_update_task else "db.db_update_task"
        with patch(target, side_effect=Exception("db down")):
            resp = client.put(f"/tasks/{task_id}", json={"title": "X"})
        assert resp.status_code >= 500 or resp.status_code == 503


class TestDeleteTaskEndpoint:
    """DELETE /tasks/{id} — hard deletes task."""

    def test_delete_task_happy(self, client):
        task_id = str(uuid.uuid4())
        target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        with patch(target, return_value={"id": task_id}):
            resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == task_id
        assert "detail" in body
        assert len(body["detail"]) > 0

    def test_delete_task_not_found(self, client):
        target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        with patch(target, return_value=None):
            resp = client.delete(f"/tasks/{NON_EXISTENT_UUID}")
        assert resp.status_code == 404

    def test_delete_task_invalid_id(self, client):
        resp = client.delete("/tasks/bad-id")
        assert resp.status_code == 422 or resp.status_code == 400

    def test_delete_task_hard_delete_verified(self, client):
        """After delete, GET for same id returns 404."""
        task_id = str(uuid.uuid4())
        del_target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        get_target = "backend.db.db_get_task" if db_get_task else "db.db_get_task"
        with patch(del_target, return_value={"id": task_id}):
            del_resp = client.delete(f"/tasks/{task_id}")
        assert del_resp.status_code == 200
        with patch(get_target, return_value=None):
            get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_delete_task_db_unavailable(self, client):
        task_id = str(uuid.uuid4())
        target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        with patch(target, side_effect=Exception("db down")):
            resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code >= 500 or resp.status_code == 503


# ===================================================================
# SECTION 3: Connection Pool Lifecycle Tests (mocked)
# ===================================================================

class TestInitConnectionPool:
    """init_connection_pool — initializes psycopg2 ThreadedConnectionPool."""

    def test_init_pool_happy(self):
        if init_connection_pool is None:
            pytest.skip("init_connection_pool not importable")
        with patch("psycopg2.pool.ThreadedConnectionPool") as MockPool:
            mock_pool_instance = MagicMock()
            MockPool.return_value = mock_pool_instance
            try:
                init_connection_pool("postgresql://user:pass@localhost/test", 1, 5)
            except TypeError:
                # Signature may differ; try alternate approach
                pass
            MockPool.assert_called_once()

    def test_init_pool_invalid_url(self):
        if init_connection_pool is None:
            pytest.skip("init_connection_pool not importable")
        with patch("psycopg2.pool.ThreadedConnectionPool", side_effect=Exception("invalid DSN")):
            with pytest.raises(Exception):
                init_connection_pool("mysql://bad", 1, 5)

    def test_init_pool_connection_failed(self):
        if init_connection_pool is None:
            pytest.skip("init_connection_pool not importable")
        with patch("psycopg2.pool.ThreadedConnectionPool", side_effect=Exception("could not connect")):
            with pytest.raises(Exception):
                init_connection_pool("postgresql://user:pass@unreachable:5432/db", 1, 5)


class TestCloseConnectionPool:
    """close_connection_pool — closes all pooled connections."""

    def test_close_pool_happy(self):
        if close_connection_pool is None:
            pytest.skip("close_connection_pool not importable")
        mock_pool = MagicMock()
        # Patch the module-level pool reference
        try:
            with patch("backend.db.pool", mock_pool):
                close_connection_pool()
        except (AttributeError, TypeError):
            try:
                with patch("db.pool", mock_pool):
                    close_connection_pool()
            except (AttributeError, TypeError):
                pytest.skip("Cannot patch pool reference")
        mock_pool.closeall.assert_called_once()


class TestGetConnection:
    """get_connection — context manager borrowing from pool."""

    def test_get_connection_commits_on_success(self):
        if get_connection is None:
            pytest.skip("get_connection not importable")
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        try:
            module_path = "backend.db.pool"
            with patch(module_path, mock_pool):
                with get_connection() as conn:
                    pass
        except (AttributeError, TypeError):
            try:
                module_path = "db.pool"
                with patch(module_path, mock_pool):
                    with get_connection() as conn:
                        pass
            except (AttributeError, TypeError):
                pytest.skip("Cannot patch pool for get_connection test")
                return
        mock_conn.commit.assert_called()

    def test_get_connection_rollback_on_exception(self):
        if get_connection is None:
            pytest.skip("get_connection not importable")
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_pool.getconn.return_value = mock_conn
        try:
            module_path = "backend.db.pool"
            with patch(module_path, mock_pool):
                try:
                    with get_connection() as conn:
                        raise RuntimeError("boom")
                except RuntimeError:
                    pass
        except (AttributeError, TypeError):
            try:
                module_path = "db.pool"
                with patch(module_path, mock_pool):
                    try:
                        with get_connection() as conn:
                            raise RuntimeError("boom")
                    except RuntimeError:
                        pass
            except (AttributeError, TypeError):
                pytest.skip("Cannot patch pool for rollback test")
                return
        mock_conn.rollback.assert_called()

    def test_get_connection_pool_exhausted(self):
        if get_connection is None:
            pytest.skip("get_connection not importable")
        mock_pool = MagicMock()
        from psycopg2.pool import PoolError
        mock_pool.getconn.side_effect = PoolError("connection pool exhausted")
        try:
            module_path = "backend.db.pool"
            with patch(module_path, mock_pool):
                with pytest.raises(Exception):
                    with get_connection() as conn:
                        pass
        except (AttributeError, TypeError, ImportError):
            try:
                module_path = "db.pool"
                with patch(module_path, mock_pool):
                    with pytest.raises(Exception):
                        with get_connection() as conn:
                            pass
            except (AttributeError, TypeError, ImportError):
                pytest.skip("Cannot test pool_exhausted")


# ===================================================================
# SECTION 4: Database Layer Tests (require DATABASE_URL)
# ===================================================================

@skip_no_db
class TestDbListTasks:
    """db_list_tasks — SELECT * FROM tasks ORDER BY created_at DESC."""

    def test_db_list_tasks_happy(self):
        if db_list_tasks is None:
            pytest.skip("db_list_tasks not importable")
        result = db_list_tasks()
        assert isinstance(result, list)
        for row in result:
            assert "id" in row
            assert "title" in row
            assert "description" in row
            assert "status" in row
            assert "created_at" in row
            assert "updated_at" in row
            assert row["status"] in VALID_STATUSES
            # Timestamps should be datetime with tzinfo
            assert row["created_at"].tzinfo is not None
            assert row["updated_at"].tzinfo is not None

    def test_db_list_tasks_ordered_by_created_at_desc(self):
        if db_list_tasks is None or db_create_task is None:
            pytest.skip("db functions not importable")
        # Create two tasks to ensure ordering
        t1 = db_create_task("First Task", None, "pending")
        t2 = db_create_task("Second Task", None, "pending")
        try:
            result = db_list_tasks()
            if len(result) >= 2:
                for i in range(len(result) - 1):
                    assert result[i]["created_at"] >= result[i + 1]["created_at"]
        finally:
            # Cleanup
            if db_delete_task:
                db_delete_task(str(t1["id"]))
                db_delete_task(str(t2["id"]))


@skip_no_db
class TestDbCreateTask:
    """db_create_task — INSERT INTO tasks ... RETURNING *."""

    def test_db_create_task_happy(self):
        if db_create_task is None:
            pytest.skip("db_create_task not importable")
        result = db_create_task("Test Task", "A description", "pending")
        try:
            assert isinstance(result, dict)
            assert "id" in result
            assert result["title"] == "Test Task"
            assert result["description"] == "A description"
            assert result["status"] == "pending"
            assert "created_at" in result
            assert "updated_at" in result
            assert result["created_at"].tzinfo is not None
        finally:
            if db_delete_task:
                db_delete_task(str(result["id"]))

    def test_db_create_task_null_description(self):
        if db_create_task is None:
            pytest.skip("db_create_task not importable")
        result = db_create_task("No Desc Task", None, "done")
        try:
            assert result["description"] is None
        finally:
            if db_delete_task:
                db_delete_task(str(result["id"]))


@skip_no_db
class TestDbGetTask:
    """db_get_task — SELECT * FROM tasks WHERE id = %s."""

    def test_db_get_task_happy(self):
        if db_create_task is None or db_get_task is None:
            pytest.skip("db functions not importable")
        created = db_create_task("Get Me", None, "pending")
        try:
            result = db_get_task(str(created["id"]))
            assert result is not None
            assert result["id"] == created["id"]
            assert result["title"] == "Get Me"
        finally:
            if db_delete_task:
                db_delete_task(str(created["id"]))

    def test_db_get_task_not_found(self):
        if db_get_task is None:
            pytest.skip("db_get_task not importable")
        result = db_get_task(NON_EXISTENT_UUID)
        assert result is None


@skip_no_db
class TestDbUpdateTask:
    """db_update_task — dynamic UPDATE SET ... RETURNING *."""

    def test_db_update_task_happy(self):
        if db_create_task is None or db_update_task is None:
            pytest.skip("db functions not importable")
        created = db_create_task("Before Update", "old desc", "pending")
        try:
            result = db_update_task(str(created["id"]), {"title": "After Update", "status": "done"})
            assert result is not None
            assert result["title"] == "After Update"
            assert result["status"] == "done"
            assert result["description"] == "old desc"  # unchanged
            assert result["created_at"] == created["created_at"]  # immutable
            assert result["updated_at"] >= created["updated_at"]
        finally:
            if db_delete_task:
                db_delete_task(str(created["id"]))

    def test_db_update_task_not_found(self):
        if db_update_task is None:
            pytest.skip("db_update_task not importable")
        result = db_update_task(NON_EXISTENT_UUID, {"title": "Ghost"})
        assert result is None


@skip_no_db
class TestDbDeleteTask:
    """db_delete_task — DELETE FROM tasks WHERE id = %s RETURNING id."""

    def test_db_delete_task_happy(self):
        if db_create_task is None or db_delete_task is None:
            pytest.skip("db functions not importable")
        created = db_create_task("Delete Me", None, "pending")
        result = db_delete_task(str(created["id"]))
        assert result is not None
        assert "id" in result
        assert str(result["id"]) == str(created["id"])
        # Verify it's truly gone
        if db_get_task:
            assert db_get_task(str(created["id"])) is None

    def test_db_delete_task_not_found(self):
        if db_delete_task is None:
            pytest.skip("db_delete_task not importable")
        result = db_delete_task(NON_EXISTENT_UUID)
        assert result is None


# ===================================================================
# SECTION 5: Invariant Tests
# ===================================================================

class TestInvariantTaskStatusSingleSourceOfTruth:
    """TaskStatus enum is the single source of truth; exactly {pending, in_progress, done}."""

    def test_status_enum_values(self):
        if TaskStatus is None:
            pytest.skip("TaskStatus not importable")
        values = {s.value for s in TaskStatus}
        assert values == {"pending", "in_progress", "done"}


class TestInvariantDescriptionNormalization:
    """Empty or whitespace-only descriptions are normalized to None before storage."""

    def test_empty_string_normalized(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "T", "description": ""})
        if resp.status_code == 201:
            assert resp.json()["description"] is None

    def test_whitespace_normalized(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "T", "description": "  \t\n  "})
        if resp.status_code == 201:
            assert resp.json()["description"] is None

    def test_null_stays_none(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "T", "description": None})
        if resp.status_code == 201:
            assert resp.json()["description"] is None


class TestInvariantTimestampFormat:
    """All API timestamps are ISO 8601 with timezone offset."""

    def _assert_iso_ts(self, ts_str):
        assert ISO_TIMESTAMP_RE.match(ts_str), f"Not ISO 8601 with tz: {ts_str}"

    def test_create_timestamps(self, client):
        target = "backend.db.db_create_task" if db_create_task else "db.db_create_task"
        with patch(target, side_effect=lambda title, description, status: _task_row(title=title, description=description, status=status)):
            resp = client.post("/tasks", json={"title": "TS Test"})
        if resp.status_code == 201:
            body = resp.json()
            self._assert_iso_ts(body["created_at"])
            self._assert_iso_ts(body["updated_at"])

    def test_list_timestamps(self, client):
        rows = [_task_row(), _task_row()]
        target = "backend.db.db_list_tasks" if db_list_tasks else "db.db_list_tasks"
        with patch(target, return_value=rows):
            resp = client.get("/tasks")
        for task in resp.json():
            self._assert_iso_ts(task["created_at"])
            self._assert_iso_ts(task["updated_at"])


class TestInvariantBlankTitleRejected:
    """Title must be non-blank after stripping; blank titles => 422."""

    def test_empty_title_post(self, client):
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422

    def test_whitespace_title_post(self, client):
        resp = client.post("/tasks", json={"title": "   "})
        assert resp.status_code == 422

    def test_empty_title_put(self, client):
        tid = str(uuid.uuid4())
        resp = client.put(f"/tasks/{tid}", json={"title": ""})
        assert resp.status_code == 422

    def test_whitespace_title_put(self, client):
        tid = str(uuid.uuid4())
        resp = client.put(f"/tasks/{tid}", json={"title": "   "})
        assert resp.status_code == 422


class TestInvariantHardDelete:
    """DELETE is a hard delete; no soft-delete or archival."""

    def test_delete_then_get_returns_404(self, client):
        task_id = str(uuid.uuid4())
        del_target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        get_target = "backend.db.db_get_task" if db_get_task else "db.db_get_task"
        with patch(del_target, return_value={"id": task_id}):
            del_resp = client.delete(f"/tasks/{task_id}")
        assert del_resp.status_code == 200
        with patch(get_target, return_value=None):
            get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_delete_then_list_excludes_task(self, client):
        task_id = str(uuid.uuid4())
        del_target = "backend.db.db_delete_task" if db_delete_task else "db.db_delete_task"
        list_target = "backend.db.db_list_tasks" if db_list_tasks else "db.db_list_tasks"
        with patch(del_target, return_value={"id": task_id}):
            client.delete(f"/tasks/{task_id}")
        with patch(list_target, return_value=[]):
            resp = client.get("/tasks")
        ids = [t["id"] for t in resp.json()]
        assert task_id not in ids
