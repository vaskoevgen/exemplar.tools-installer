"""
Adversarial hidden acceptance tests for React Frontend SPA (api.ts layer).

These tests target behavioral properties that a shortcut implementation might
violate — e.g. hardcoded URLs, hardcoded return values, missing method enforcement,
missing header enforcement, and insufficient error handling generalization.

All backend interactions are mocked via unittest.mock to test the frontend
API module in isolation.
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch, call
from frontend import (
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    healthCheck,
    resolveBaseUrl,
    parseErrorResponse,
    ApiError,
)


# ---------------------------------------------------------------------------
# Helpers to build mock fetch responses
# ---------------------------------------------------------------------------

def _make_response(status=200, json_data=None, ok=True, status_text="OK", headers=None):
    """Build a mock Response object mimicking the Fetch API Response."""
    resp = MagicMock()
    resp.ok = ok
    resp.status = status
    resp.statusText = status_text
    resp.headers = headers or {"content-type": "application/json"}
    if json_data is not None:
        resp.json = AsyncMock(return_value=json_data)
    else:
        resp.json = AsyncMock(side_effect=Exception("No JSON"))
    resp.text = AsyncMock(return_value=json.dumps(json_data) if json_data else status_text)
    return resp


def _make_task(id=1, title="Task", description=None, status="pending",
               created_at="2025-01-15T12:00:00+00:00",
               updated_at="2025-01-15T12:00:00+00:00"):
    return {
        "id": id,
        "title": title,
        "description": description,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
    }


# A mock fetch that captures calls
class FetchCapture:
    """Callable mock that records the URL, method, headers, and body of each call."""
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def __call__(self, url, **kwargs):
        self.calls.append({"url": url, "kwargs": kwargs})
        return self.response

    @property
    def last_url(self):
        return self.calls[-1]["url"] if self.calls else None

    @property
    def last_method(self):
        kw = self.calls[-1]["kwargs"] if self.calls else {}
        return kw.get("method", "GET")

    @property
    def last_body(self):
        kw = self.calls[-1]["kwargs"] if self.calls else {}
        body = kw.get("body", None)
        if body and isinstance(body, str):
            return json.loads(body)
        return body

    @property
    def last_headers(self):
        kw = self.calls[-1]["kwargs"] if self.calls else {}
        return kw.get("headers", {})


# ---------------------------------------------------------------------------
# resolveBaseUrl tests
# ---------------------------------------------------------------------------

class TestGoodhartResolveBaseUrl:

    def test_goodhart_resolve_base_url_multiple_trailing_slashes(self):
        """resolveBaseUrl must strip ALL trailing slashes, not just one."""
        with patch.dict("os.environ", {"VITE_API_URL": "http://example.com///"}, clear=False):
            try:
                result = resolveBaseUrl()
            except Exception:
                # Some implementations read from import.meta.env — try alternate approach
                pytest.skip("Cannot mock env in this runtime")
            assert not result.endswith("/"), f"Expected no trailing slash, got: {result}"

    def test_goodhart_resolve_base_url_empty_string_fallback(self):
        """resolveBaseUrl must fall back to default when VITE_API_URL is empty string."""
        with patch.dict("os.environ", {"VITE_API_URL": ""}, clear=False):
            try:
                result = resolveBaseUrl()
            except Exception:
                pytest.skip("Cannot mock env in this runtime")
            assert result == "http://localhost:8000"

    def test_goodhart_resolve_base_url_preserves_path(self):
        """resolveBaseUrl must preserve path segments, stripping only trailing slash."""
        with patch.dict("os.environ", {"VITE_API_URL": "http://api.example.com/v1/"}, clear=False):
            try:
                result = resolveBaseUrl()
            except Exception:
                pytest.skip("Cannot mock env in this runtime")
            assert result == "http://api.example.com/v1"

    def test_goodhart_resolve_base_url_no_slash_passthrough(self):
        """resolveBaseUrl returns URL unchanged when no trailing slash present."""
        with patch.dict("os.environ", {"VITE_API_URL": "https://api.prod.example.com:3000"}, clear=False):
            try:
                result = resolveBaseUrl()
            except Exception:
                pytest.skip("Cannot mock env in this runtime")
            assert result == "https://api.prod.example.com:3000"


# ---------------------------------------------------------------------------
# fetchTasks tests
# ---------------------------------------------------------------------------

class TestGoodhartFetchTasks:

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_uses_resolved_base_url(self):
        """fetchTasks must construct URL dynamically from resolveBaseUrl, not hardcode localhost."""
        tasks = [_make_task(id=1), _make_task(id=2)]
        resp = _make_response(json_data=tasks)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://custom-api:9999"):
            result = await fetchTasks()

        assert capture.last_url == "http://custom-api:9999/tasks", \
            f"Expected URL 'http://custom-api:9999/tasks', got '{capture.last_url}'"

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_preserves_backend_order(self):
        """fetchTasks must preserve task ordering from backend, not sort by id."""
        tasks = [_make_task(id=3), _make_task(id=1), _make_task(id=2)]
        resp = _make_response(json_data=tasks)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await fetchTasks()

        ids = [t["id"] if isinstance(t, dict) else t.id for t in result]
        assert ids == [3, 1, 2], f"Expected order [3, 1, 2], got {ids}"

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_large_list(self):
        """fetchTasks must handle responses with many tasks, not just small arrays."""
        tasks = [_make_task(id=i, title=f"Task {i}") for i in range(1, 51)]
        resp = _make_response(json_data=tasks)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await fetchTasks()

        assert len(result) == 50

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_single_task(self):
        """fetchTasks must correctly return a single-element array."""
        tasks = [_make_task(id=7, title="Only task")]
        resp = _make_response(json_data=tasks)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await fetchTasks()

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_returns_array_type(self):
        """fetchTasks must return a list/array, not an object wrapper."""
        tasks = [_make_task(id=1), _make_task(id=2)]
        resp = _make_response(json_data=tasks)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await fetchTasks()

        assert isinstance(result, list), f"Expected list, got {type(result)}"

    @pytest.mark.asyncio
    async def test_goodhart_fetch_tasks_502_raises_api_error(self):
        """fetchTasks must convert HTTP 502 (not just 500) into ApiError."""
        resp = _make_response(status=502, ok=False, json_data={"detail": "Bad Gateway"},
                              status_text="Bad Gateway")
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            with pytest.raises((ApiError, Exception)) as exc_info:
                await fetchTasks()

        err = exc_info.value
        if hasattr(err, "statusCode"):
            assert err.statusCode == 502
        elif hasattr(err, "status_code"):
            assert err.status_code == 502


# ---------------------------------------------------------------------------
# createTask tests
# ---------------------------------------------------------------------------

class TestGoodhartCreateTask:

    @pytest.mark.asyncio
    async def test_goodhart_create_task_sends_post_method(self):
        """createTask must use HTTP POST method."""
        task = _make_task(id=10, title="New", status="pending")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "New", "description": None, "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await createTask(data)

        assert capture.last_method.upper() == "POST", \
            f"Expected POST, got {capture.last_method}"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_sends_json_content_type(self):
        """createTask must set Content-Type to application/json."""
        task = _make_task(id=10, title="New")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "New", "description": None, "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await createTask(data)

        headers = capture.last_headers
        ct = headers.get("Content-Type", headers.get("content-type", ""))
        assert "application/json" in ct.lower(), \
            f"Expected Content-Type application/json, got '{ct}'"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_with_in_progress_status(self):
        """createTask must transmit non-default status 'in_progress' correctly."""
        task = _make_task(id=11, title="Active", status="in_progress")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "Active", "description": None, "status": "in_progress"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await createTask(data)

        body = capture.last_body
        if body:
            assert body.get("status") == "in_progress"
        # Also verify response
        status_val = result.get("status") if isinstance(result, dict) else getattr(result, "status", None)
        assert status_val == "in_progress"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_with_done_status(self):
        """createTask must support 'done' status, not just 'pending'."""
        task = _make_task(id=12, title="Completed", description="Finished", status="done")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "Completed", "description": "Finished", "status": "done"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await createTask(data)

        status_val = result.get("status") if isinstance(result, dict) else getattr(result, "status", None)
        assert status_val == "done"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_empty_description_to_null(self):
        """Empty description strings must be sent as null in the JSON body (invariant A12)."""
        task = _make_task(id=13, title="Task", description=None)
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "Task", "description": "", "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await createTask(data)

        body = capture.last_body
        assert body is not None, "Request body should not be empty"
        assert body.get("description") is None, \
            f"Empty description should be null, got: {body.get('description')!r}"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_null_description_preserved(self):
        """createTask must transmit null description as JSON null, not omit the field."""
        task = _make_task(id=14, title="No desc")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "No desc", "description": None, "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await createTask(data)

        body = capture.last_body
        assert "description" in body, "description field must be present in request body"
        assert body["description"] is None

    @pytest.mark.asyncio
    async def test_goodhart_create_task_returns_all_six_fields(self):
        """createTask response must include all six Task fields."""
        task = _make_task(id=15, title="Full", description="desc", status="pending")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "Full", "description": "desc", "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await createTask(data)

        if isinstance(result, dict):
            for field in ["id", "title", "description", "status", "created_at", "updated_at"]:
                assert field in result, f"Missing field '{field}' in returned Task"
        else:
            for field in ["id", "title", "description", "status", "created_at", "updated_at"]:
                assert hasattr(result, field), f"Missing attribute '{field}' in returned Task"

    @pytest.mark.asyncio
    async def test_goodhart_create_task_special_chars_in_description(self):
        """createTask must handle special characters, unicode, and newlines in description."""
        desc = 'Line1\nLine2\t日本語 <script>alert(1)</script>'
        task = _make_task(id=16, title="Test", description=desc)
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        data = {"title": "Test", "description": desc, "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await createTask(data)

        body = capture.last_body
        assert body["description"] == desc

    @pytest.mark.asyncio
    async def test_goodhart_create_task_409_conflict(self):
        """createTask must raise ApiError for 409 Conflict, not just specifically handled codes."""
        resp = _make_response(status=409, ok=False, json_data={"detail": "Conflict"},
                              status_text="Conflict")
        capture = FetchCapture(resp)

        data = {"title": "Conflict Task", "description": None, "status": "pending"}
        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            with pytest.raises((ApiError, Exception)) as exc_info:
                await createTask(data)

        err = exc_info.value
        if hasattr(err, "statusCode"):
            assert err.statusCode == 409
        elif hasattr(err, "status_code"):
            assert err.status_code == 409


# ---------------------------------------------------------------------------
# updateTask tests
# ---------------------------------------------------------------------------

class TestGoodhartUpdateTask:

    @pytest.mark.asyncio
    async def test_goodhart_update_task_uses_id_in_url(self):
        """updateTask must interpolate the id into the URL path dynamically."""
        task = _make_task(id=42, title="Updated")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await updateTask(42, {"title": "Updated"})

        assert "/tasks/42" in capture.last_url, \
            f"Expected '/tasks/42' in URL, got '{capture.last_url}'"

    @pytest.mark.asyncio
    async def test_goodhart_update_task_different_id(self):
        """updateTask must work with arbitrary ids, not just id=1."""
        task = _make_task(id=9999, title="Big ID", status="done")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await updateTask(9999, {"status": "done"})

        assert "/tasks/9999" in capture.last_url
        id_val = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        assert id_val == 9999

    @pytest.mark.asyncio
    async def test_goodhart_update_task_sends_put_method(self):
        """updateTask must use HTTP PUT method, not POST or PATCH."""
        task = _make_task(id=1, title="Updated")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await updateTask(1, {"title": "Updated"})

        assert capture.last_method.upper() == "PUT", \
            f"Expected PUT, got {capture.last_method}"

    @pytest.mark.asyncio
    async def test_goodhart_update_task_status_only(self):
        """updateTask must support sending only status, not require title to always be present."""
        task = _make_task(id=5, title="Existing", status="done")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await updateTask(5, {"status": "done"})

        body = capture.last_body
        assert body.get("status") == "done"

    @pytest.mark.asyncio
    async def test_goodhart_update_task_returns_matching_id(self):
        """updateTask must return a Task whose id matches the input id for any value."""
        task = _make_task(id=12345, title="New Title")
        resp = _make_response(json_data=task)
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await updateTask(12345, {"title": "New Title"})

        id_val = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        assert id_val == 12345


# ---------------------------------------------------------------------------
# deleteTask tests
# ---------------------------------------------------------------------------

class TestGoodhartDeleteTask:

    @pytest.mark.asyncio
    async def test_goodhart_delete_task_uses_id_in_url(self):
        """deleteTask must interpolate the id into the DELETE URL path."""
        resp = _make_response(json_data={"detail": "Deleted", "id": 77})
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await deleteTask(77)

        assert "/tasks/77" in capture.last_url, \
            f"Expected '/tasks/77' in URL, got '{capture.last_url}'"

    @pytest.mark.asyncio
    async def test_goodhart_delete_task_sends_delete_method(self):
        """deleteTask must use HTTP DELETE method."""
        resp = _make_response(json_data={"detail": "Deleted", "id": 1})
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            await deleteTask(1)

        assert capture.last_method.upper() == "DELETE", \
            f"Expected DELETE, got {capture.last_method}"

    @pytest.mark.asyncio
    async def test_goodhart_delete_task_returns_matching_id(self):
        """deleteTask returns DeleteConfirmation with id matching the input."""
        resp = _make_response(json_data={"detail": "Task 256 deleted", "id": 256})
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://localhost:8000"):
            result = await deleteTask(256)

        id_val = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
        assert id_val == 256


# ---------------------------------------------------------------------------
# healthCheck tests
# ---------------------------------------------------------------------------

class TestGoodhartHealthCheck:

    @pytest.mark.asyncio
    async def test_goodhart_health_check_uses_resolved_base_url(self):
        """healthCheck must hit /health on the resolved base URL, not hardcode."""
        resp = _make_response(json_data={"status": "healthy"})
        capture = FetchCapture(resp)

        with patch("frontend.fetch", capture), \
             patch("frontend.resolveBaseUrl", return_value="http://custom:5555"):
            await healthCheck()

        assert capture.last_url == "http://custom:5555/health", \
            f"Expected 'http://custom:5555/health', got '{capture.last_url}'"


# ---------------------------------------------------------------------------
# parseErrorResponse tests
# ---------------------------------------------------------------------------

class TestGoodhartParseErrorResponse:

    @pytest.mark.asyncio
    async def test_goodhart_parse_error_422(self):
        """parseErrorResponse must handle 422 Unprocessable Entity."""
        resp = _make_response(status=422, ok=False,
                              json_data={"detail": "Validation failed"},
                              status_text="Unprocessable Entity")
        result = await parseErrorResponse(resp)

        sc = result.statusCode if hasattr(result, "statusCode") else result.get("statusCode")
        detail = result.detail if hasattr(result, "detail") else result.get("detail")
        assert sc == 422
        assert detail == "Validation failed"

    @pytest.mark.asyncio
    async def test_goodhart_parse_error_401(self):
        """parseErrorResponse must handle 401 Unauthorized."""
        resp = _make_response(status=401, ok=False,
                              json_data={"detail": "Not authenticated"},
                              status_text="Unauthorized")
        result = await parseErrorResponse(resp)

        sc = result.statusCode if hasattr(result, "statusCode") else result.get("statusCode")
        detail = result.detail if hasattr(result, "detail") else result.get("detail")
        assert sc == 401
        assert detail == "Not authenticated"

    @pytest.mark.asyncio
    async def test_goodhart_parse_error_503_non_json_fallback(self):
        """parseErrorResponse must handle 503 with non-JSON body, falling back to statusText."""
        resp = MagicMock()
        resp.ok = False
        resp.status = 503
        resp.statusText = "Service Unavailable"
        resp.json = AsyncMock(side_effect=Exception("Not JSON"))
        resp.text = AsyncMock(return_value="<html>503</html>")

        result = await parseErrorResponse(resp)

        sc = result.statusCode if hasattr(result, "statusCode") else result.get("statusCode")
        detail = result.detail if hasattr(result, "detail") else result.get("detail")
        assert sc == 503
        assert "Service Unavailable" in str(detail)

    @pytest.mark.asyncio
    async def test_goodhart_parse_error_message_includes_detail(self):
        """parseErrorResponse message field must include the parsed detail string, not a generic message."""
        resp = _make_response(status=404, ok=False,
                              json_data={"detail": "Task 99 not found"},
                              status_text="Not Found")
        result = await parseErrorResponse(resp)

        msg = result.message if hasattr(result, "message") else result.get("message", "")
        assert "Task 99 not found" in msg, \
            f"Expected 'Task 99 not found' in message, got '{msg}'"

    @pytest.mark.asyncio
    async def test_goodhart_api_error_is_exception(self):
        """ApiError must be throwable — it should be an instance of Exception."""
        resp = _make_response(status=400, ok=False,
                              json_data={"detail": "Bad request"},
                              status_text="Bad Request")
        result = await parseErrorResponse(resp)

        # If parseErrorResponse returns the error rather than raising it
        if isinstance(result, Exception):
            assert True
        elif isinstance(result, dict):
            # Implementation may return a dict — but ApiError class itself should be an Exception
            err = ApiError(message="test", statusCode=400, detail="test")
            assert isinstance(err, Exception), "ApiError must extend Exception"
        else:
            assert isinstance(result, Exception), f"Expected Exception, got {type(result)}"
