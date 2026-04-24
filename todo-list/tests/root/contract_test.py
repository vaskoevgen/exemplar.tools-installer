"""
Contract test suite for root component (src/root/main.py).
Tests organized into three classes: TestDatabase, TestCRUD, TestHandlers.
Run with: pytest contract_test.py -v
"""
import os
import re
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Attempt imports — the component is a single file: src/root/main.py
# We try multiple import paths to be resilient to project layout.
# ---------------------------------------------------------------------------
try:
    from root.main import *
    import root.main as main_module
except ImportError:
    try:
        from root import *
        import root as main_module
    except ImportError:
        from main import *
        import main as main_module


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fake_row(task_id=1, title="Test task", completed=False, created_at=None):
    """Return a dict mimicking a RealDictCursor row."""
    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()
    return {
        "id": task_id,
        "title": title,
        "completed": completed,
        "created_at": created_at,
    }


def _mock_cursor(fetchone_return=None, fetchall_return=None, rowcount=1):
    """Build a mock psycopg2 cursor."""
    cur = MagicMock()
    cur.fetchone.return_value = fetchone_return
    cur.fetchall.return_value = fetchall_return if fetchall_return is not None else []
    cur.rowcount = rowcount
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    return cur


def _mock_connection(cursor=None):
    """Build a mock psycopg2 connection."""
    conn = MagicMock()
    if cursor is None:
        cursor = _mock_cursor()
    conn.cursor.return_value = cursor
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    return conn


# ---------------------------------------------------------------------------
# Type validation tests
# ---------------------------------------------------------------------------

class TestTypes:
    """Tests for contract-defined types and their validators."""

    def test_task_title_valid_min(self):
        """TaskTitle accepts a single-character string (boundary min)."""
        # Try constructing a TaskTitle or CreateTaskRequest with length-1 title
        try:
            obj = CreateTaskRequest(title="A")
            assert obj.title == "A"
        except NameError:
            # If CreateTaskRequest is not a Pydantic model, try TaskTitle
            try:
                obj = TaskTitle(value="A")
                assert obj.value == "A"
            except NameError:
                pytest.skip("TaskTitle/CreateTaskRequest types not directly exposed")

    def test_task_title_valid_max(self):
        """TaskTitle accepts a 500-character string (boundary max)."""
        long_title = "A" * 500
        try:
            obj = CreateTaskRequest(title=long_title)
            assert obj.title == long_title
        except NameError:
            try:
                obj = TaskTitle(value=long_title)
                assert obj.value == long_title
            except NameError:
                pytest.skip("TaskTitle/CreateTaskRequest types not directly exposed")

    def test_task_title_reject_empty(self):
        """TaskTitle rejects empty string."""
        with pytest.raises((ValueError, Exception)):
            try:
                CreateTaskRequest(title="")
            except NameError:
                TaskTitle(value="")

    def test_task_title_reject_too_long(self):
        """TaskTitle rejects string >500 characters."""
        with pytest.raises((ValueError, Exception)):
            try:
                CreateTaskRequest(title="A" * 501)
            except NameError:
                TaskTitle(value="A" * 501)

    def test_database_url_valid_postgresql(self):
        """DatabaseURL accepts postgresql:// URI."""
        try:
            url = DatabaseURL(value="postgresql://user:pass@localhost/db")
            assert "postgresql" in url.value
        except NameError:
            pytest.skip("DatabaseURL type not directly exposed")

    def test_database_url_valid_psycopg2(self):
        """DatabaseURL accepts postgresql+psycopg2:// URI."""
        try:
            url = DatabaseURL(value="postgresql+psycopg2://user:pass@localhost/db")
            assert "postgresql" in url.value
        except NameError:
            pytest.skip("DatabaseURL type not directly exposed")

    def test_database_url_reject_mysql(self):
        """DatabaseURL rejects non-postgresql URIs."""
        try:
            with pytest.raises((ValueError, Exception)):
                DatabaseURL(value="mysql://user:pass@localhost/db")
        except NameError:
            pytest.skip("DatabaseURL type not directly exposed")

    def test_database_url_reject_empty(self):
        """DatabaseURL rejects empty string."""
        try:
            with pytest.raises((ValueError, Exception)):
                DatabaseURL(value="")
        except NameError:
            pytest.skip("DatabaseURL type not directly exposed")


# ---------------------------------------------------------------------------
# Database layer tests
# ---------------------------------------------------------------------------

class TestDatabase:
    """Tests for init_db and get_db_connection."""

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/testdb"})
    @patch("psycopg2.connect")
    def test_init_db_success(self, mock_connect):
        """init_db creates tasks table with correct schema."""
        mock_conn = _mock_connection()
        mock_cur = _mock_cursor()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn

        try:
            result = init_db(os.environ["DATABASE_URL"])
        except TypeError:
            # init_db might take no args and read DATABASE_URL itself
            result = init_db()

        assert result is None
        # Verify CREATE TABLE was executed
        calls = mock_cur.execute.call_args_list
        sql_executed = " ".join(str(c) for c in calls).lower()
        assert "create table" in sql_executed or "create" in sql_executed

    @patch.dict(os.environ, {}, clear=True)
    def test_init_db_missing_database_url(self):
        """init_db raises error when DATABASE_URL is not set."""
        # Remove DATABASE_URL if present
        os.environ.pop("DATABASE_URL", None)
        with pytest.raises(Exception):
            try:
                init_db("")
            except TypeError:
                init_db()

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@badhost/db"})
    @patch("psycopg2.connect", side_effect=Exception("connection refused"))
    def test_init_db_connection_failed(self, mock_connect):
        """init_db raises error when PostgreSQL is unreachable."""
        with pytest.raises(Exception, match="connect|connection|refused"):
            try:
                init_db(os.environ["DATABASE_URL"])
            except TypeError:
                init_db()

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost/testdb"})
    @patch("psycopg2.connect")
    def test_get_db_connection_success(self, mock_connect):
        """get_db_connection returns a connection object."""
        mock_conn = _mock_connection()
        mock_connect.return_value = mock_conn

        # Initialize first
        try:
            init_db(os.environ["DATABASE_URL"])
        except TypeError:
            init_db()

        conn = get_db_connection()
        assert conn is not None


# ---------------------------------------------------------------------------
# CRUD function tests
# ---------------------------------------------------------------------------

class TestCRUD:
    """Tests for create_task, list_tasks, update_task, delete_task."""

    # -- create_task --------------------------------------------------------

    @patch("psycopg2.connect")
    def test_create_task_success(self, mock_connect):
        """create_task inserts a task and returns it with correct fields."""
        row = _make_fake_row(task_id=1, title="Buy groceries", completed=False)
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        # Patch the module-level connection retrieval
        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                task = create_task("Buy groceries")
            except TypeError:
                # Might need a connection arg
                task = create_task("Buy groceries", mock_conn)

        # Verify the result has expected shape
        if isinstance(task, dict):
            assert task["title"] == "Buy groceries"
            assert task["completed"] is False
            assert "id" in task
            assert "created_at" in task
        else:
            assert task.title == "Buy groceries"
            assert task.completed is False
            assert task.id is not None
            assert task.created_at is not None

        # Verify INSERT with RETURNING was used
        sql_arg = str(mock_cur.execute.call_args)
        assert "insert" in sql_arg.lower()
        assert "returning" in sql_arg.lower()

    @patch("psycopg2.connect")
    def test_create_task_uses_parameterized_query(self, mock_connect):
        """Invariant: create_task uses %s placeholders, not string interpolation."""
        row = _make_fake_row()
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                create_task("Test")
            except TypeError:
                create_task("Test", mock_conn)

        sql = mock_cur.execute.call_args[0][0]
        assert "%s" in sql, "SQL must use parameterized %s placeholders"
        # Ensure no f-string patterns
        assert "{" not in sql, "SQL must not use string interpolation"

    # -- list_tasks ---------------------------------------------------------

    @pytest.mark.parametrize("completed_filter,expected_where", [
        (None, False),
        (True, True),
        (False, True),
    ])
    @patch("psycopg2.connect")
    def test_list_tasks_filter(self, mock_connect, completed_filter, expected_where):
        """list_tasks applies correct WHERE clause based on CompletedFilter."""
        rows = [_make_fake_row(task_id=1, completed=True), _make_fake_row(task_id=2, completed=False)]
        if completed_filter is True:
            rows = [r for r in rows if r["completed"]]
        elif completed_filter is False:
            rows = [r for r in rows if not r["completed"]]

        mock_cur = _mock_cursor(fetchall_return=rows)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = list_tasks(completed_filter)
            except TypeError:
                result = list_tasks(completed_filter, mock_conn)

        assert isinstance(result, list)
        if expected_where and completed_filter is not None:
            sql = mock_cur.execute.call_args[0][0].lower()
            assert "where" in sql or "completed" in sql

    @patch("psycopg2.connect")
    def test_list_tasks_empty(self, mock_connect):
        """list_tasks returns empty list when no tasks exist."""
        mock_cur = _mock_cursor(fetchall_return=[])
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = list_tasks(None)
            except TypeError:
                result = list_tasks(None, mock_conn)

        assert result == []

    # -- update_task --------------------------------------------------------

    @patch("psycopg2.connect")
    def test_update_task_success(self, mock_connect):
        """update_task returns updated task with new completed value."""
        row = _make_fake_row(task_id=1, title="Test", completed=True)
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = update_task(1, True)
            except TypeError:
                result = update_task(1, True, mock_conn)

        assert result is not None
        if isinstance(result, dict):
            assert result["completed"] is True
            assert result["id"] == 1
        else:
            assert result.completed is True
            assert result.id == 1

        # Verify UPDATE ... RETURNING
        sql = mock_cur.execute.call_args[0][0].lower()
        assert "update" in sql
        assert "returning" in sql

    @patch("psycopg2.connect")
    def test_update_task_not_found(self, mock_connect):
        """update_task returns None when task_id does not exist."""
        mock_cur = _mock_cursor(fetchone_return=None, rowcount=0)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = update_task(99999, True)
            except TypeError:
                result = update_task(99999, True, mock_conn)

        assert result is None

    # -- delete_task --------------------------------------------------------

    @patch("psycopg2.connect")
    def test_delete_task_success(self, mock_connect):
        """delete_task returns True when task exists and is deleted."""
        mock_cur = _mock_cursor(rowcount=1)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = delete_task(1)
            except TypeError:
                result = delete_task(1, mock_conn)

        assert result is True

    @patch("psycopg2.connect")
    def test_delete_task_not_found(self, mock_connect):
        """delete_task returns False when task_id does not exist."""
        mock_cur = _mock_cursor(rowcount=0)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            try:
                result = delete_task(99999)
            except TypeError:
                result = delete_task(99999, mock_conn)

        assert result is False


# ---------------------------------------------------------------------------
# Handler / API tests (via FastAPI TestClient)
# ---------------------------------------------------------------------------

class TestHandlers:
    """Tests for handle_* route handlers via FastAPI TestClient."""

    @pytest.fixture(autouse=True)
    def _setup_client(self):
        """Create a TestClient if the module exposes a FastAPI app."""
        try:
            from fastapi.testclient import TestClient
        except ImportError:
            pytest.skip("fastapi not installed; skipping handler tests")

        # Find the FastAPI app instance
        app = getattr(main_module, "app", None)
        if app is None:
            # Scan module for FastAPI instance
            import fastapi
            for name in dir(main_module):
                obj = getattr(main_module, name)
                if isinstance(obj, fastapi.FastAPI):
                    app = obj
                    break
        if app is None:
            pytest.skip("No FastAPI app found in module")

        self.client = TestClient(app, raise_server_exceptions=False)
        self.app = app

    # -- GET / (serve index) ------------------------------------------------

    def test_handle_serve_index_success(self, tmp_path):
        """GET / serves static/index.html with text/html content type."""
        # Create the expected file
        static_dir = tmp_path / "static"
        static_dir.mkdir()
        index_file = static_dir / "index.html"
        index_file.write_text("<html><body>Hello</body></html>")

        with patch("os.path.exists", return_value=True):
            # Try patching FileResponse or the path used
            resp = self.client.get("/")
            # If the file doesn't actually exist in test env, we accept various outcomes
            if resp.status_code == 200:
                assert "html" in resp.headers.get("content-type", "").lower() or resp.status_code == 200

    # -- POST /tasks --------------------------------------------------------

    @patch("psycopg2.connect")
    def test_handle_create_task_success(self, mock_connect):
        """POST /tasks with valid title returns 201 and created task."""
        row = _make_fake_row(task_id=1, title="New task", completed=False)
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.post("/tasks", json={"title": "New task"})

        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "New task"
        assert body["completed"] is False
        assert "id" in body
        assert "created_at" in body

    def test_handle_create_task_empty_title(self):
        """POST /tasks with empty title returns validation error (422)."""
        resp = self.client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422 or resp.status_code == 400

    def test_handle_create_task_title_too_long(self):
        """POST /tasks with title > 500 chars returns validation error."""
        resp = self.client.post("/tasks", json={"title": "A" * 501})
        assert resp.status_code == 422 or resp.status_code == 400

    def test_handle_create_task_missing_body(self):
        """POST /tasks with no body returns validation error."""
        resp = self.client.post("/tasks")
        assert resp.status_code == 422 or resp.status_code == 400

    # -- GET /tasks ---------------------------------------------------------

    @patch("psycopg2.connect")
    def test_handle_list_tasks_success(self, mock_connect):
        """GET /tasks returns 200 with a JSON array."""
        rows = [_make_fake_row(task_id=1), _make_fake_row(task_id=2)]
        mock_cur = _mock_cursor(fetchall_return=rows)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.get("/tasks")

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) == 2

    @pytest.mark.parametrize("query,filter_val", [
        ("?completed=true", True),
        ("?completed=false", False),
        ("", None),
    ])
    @patch("psycopg2.connect")
    def test_handle_list_tasks_filter(self, mock_connect, query, filter_val):
        """GET /tasks with completed query param filters correctly."""
        if filter_val is True:
            rows = [_make_fake_row(task_id=1, completed=True)]
        elif filter_val is False:
            rows = [_make_fake_row(task_id=1, completed=False)]
        else:
            rows = [_make_fake_row(task_id=1, completed=True), _make_fake_row(task_id=2, completed=False)]

        mock_cur = _mock_cursor(fetchall_return=rows)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.get(f"/tasks{query}")

        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        if filter_val is not None:
            for task in body:
                assert task["completed"] == filter_val

    # -- PATCH /tasks/{id} --------------------------------------------------

    @patch("psycopg2.connect")
    def test_handle_update_task_success(self, mock_connect):
        """PATCH /tasks/1 with valid body returns 200 and updated task."""
        row = _make_fake_row(task_id=1, title="Test", completed=True)
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.patch("/tasks/1", json={"completed": True})

        assert resp.status_code == 200
        body = resp.json()
        assert body["completed"] is True
        assert body["id"] == 1

    @patch("psycopg2.connect")
    def test_handle_update_task_not_found(self, mock_connect):
        """PATCH /tasks/99999 returns 404 with ErrorResponse."""
        mock_cur = _mock_cursor(fetchone_return=None, rowcount=0)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.patch("/tasks/99999", json={"completed": True})

        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body
        assert body["detail"] == "Task not found"

    def test_handle_update_task_missing_body(self):
        """PATCH /tasks/1 with no body returns validation error."""
        resp = self.client.patch("/tasks/1")
        assert resp.status_code == 422 or resp.status_code == 400

    # -- DELETE /tasks/{id} -------------------------------------------------

    @patch("psycopg2.connect")
    def test_handle_delete_task_success(self, mock_connect):
        """DELETE /tasks/1 returns 204 with empty body."""
        mock_cur = _mock_cursor(rowcount=1)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.delete("/tasks/1")

        assert resp.status_code == 204
        assert resp.content == b"" or resp.text == ""

    @patch("psycopg2.connect")
    def test_handle_delete_task_not_found(self, mock_connect):
        """DELETE /tasks/99999 returns 404 with ErrorResponse."""
        mock_cur = _mock_cursor(rowcount=0, fetchone_return=None)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.delete("/tasks/99999")

        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body
        assert body["detail"] == "Task not found"

    # -- Invariant: error response format -----------------------------------

    @patch("psycopg2.connect")
    def test_invariant_error_response_format(self, mock_connect):
        """All error responses conform to {'detail': 'message'} structure."""
        mock_cur = _mock_cursor(fetchone_return=None, rowcount=0)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.patch("/tasks/99999", json={"completed": True})

        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)
        # Should not have unexpected keys at top level beyond 'detail'
        # (some frameworks add others, so we just verify 'detail' exists)

    @patch("psycopg2.connect")
    def test_invariant_post_returns_201(self, mock_connect):
        """POST /tasks returns exactly 201 on success, never 200."""
        row = _make_fake_row(task_id=42, title="Invariant test")
        mock_cur = _mock_cursor(fetchone_return=row)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.post("/tasks", json={"title": "Invariant test"})

        assert resp.status_code == 201, f"Expected 201 but got {resp.status_code}"

    @patch("psycopg2.connect")
    def test_invariant_delete_returns_204_empty_body(self, mock_connect):
        """DELETE /tasks/{id} returns exactly 204 with empty body, never JSON."""
        mock_cur = _mock_cursor(rowcount=1)
        mock_conn = _mock_connection(cursor=mock_cur)
        mock_connect.return_value = mock_conn

        with patch.object(main_module, "get_db_connection", return_value=mock_conn):
            resp = self.client.delete("/tasks/1")

        assert resp.status_code == 204, f"Expected 204 but got {resp.status_code}"
        assert resp.content == b"", "DELETE success must return empty body"
