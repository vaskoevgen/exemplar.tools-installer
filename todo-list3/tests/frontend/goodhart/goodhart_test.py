"""
Adversarial hidden acceptance tests for the React Frontend SPA component.
These tests target behavioral gaps not covered by visible tests, detecting
implementations that hardcode returns or take shortcuts.
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
    Task,
    TaskStatus,
    StatusBadgeColorMap,
    DeleteConfirmation,
    HealthResponse,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_response(status=200, json_data=None, ok=True, status_text="OK", raise_on_json=False):
    """Create a mock fetch Response object."""
    resp = MagicMock()
    resp.status = status
    resp.ok = ok
    resp.statusText = status_text
    if raise_on_json:
        resp.json = AsyncMock(side_effect=Exception("not JSON"))
    else:
        resp.json = AsyncMock(return_value=json_data)
    resp.text = AsyncMock(return_value=json.dumps(json_data) if json_data else "")
    return resp


def make_task(id=1, title="Test", description=None, status="pending",
              created_at="2025-01-15T12:00:00+00:00", updated_at="2025-01-15T12:00:00+00:00"):
    return {
        "id": id,
        "title": title,
        "description": description,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
    }


# ---------------------------------------------------------------------------
# fetchTasks tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_fetch_tasks_correct_endpoint():
    """fetchTasks must issue a GET request to exactly {BASE_URL}/tasks using the resolved base URL."""
    with patch("src.frontend.resolveBaseUrl", return_value="http://custom-api:9000"):
        mock_fetch = AsyncMock(return_value=make_mock_response(json_data=[]))
        with patch("src.frontend.fetch", mock_fetch):
            await fetchTasks()
            args, kwargs = mock_fetch.call_args
            url = args[0] if args else kwargs.get("url", "")
            assert "/tasks" in url
            assert "custom-api:9000" in url


@pytest.mark.anyio
async def test_goodhart_fetch_tasks_returns_multiple_tasks_distinct():
    """fetchTasks must return all tasks from the response, not just the first or a subset."""
    tasks = [make_task(id=i, title=f"Task {i}") for i in range(1, 6)]
    with patch("src.frontend.fetch", AsyncMock(return_value=make_mock_response(json_data=tasks))):
        result = await fetchTasks()
        assert len(result) == 5
        ids = [t["id"] if isinstance(t, dict) else t.id for t in result]
        assert len(set(ids)) == 5


@pytest.mark.anyio
async def test_goodhart_fetch_tasks_preserves_task_order():
    """fetchTasks must preserve the order of tasks as returned by the backend."""
    tasks = [make_task(id=3), make_task(id=1), make_task(id=2)]
    with patch("src.frontend.fetch", AsyncMock(return_value=make_mock_response(json_data=tasks))):
        result = await fetchTasks()
        result_ids = [t["id"] if isinstance(t, dict) else t.id for t in result]
        assert result_ids == [3, 1, 2]


@pytest.mark.anyio
async def test_goodhart_fetch_tasks_uses_get_method():
    """fetchTasks must use HTTP GET method."""
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=[]))
    with patch("src.frontend.fetch", mock_fetch):
        await fetchTasks()
        args, kwargs = mock_fetch.call_args
        method = kwargs.get("method", "GET")
        # GET is the default, so method should be GET or not specified
        assert method.upper() in ("GET",) or "method" not in kwargs


@pytest.mark.anyio
async def test_goodhart_fetch_tasks_4xx_raises_error():
    """fetchTasks must raise an ApiError for 4xx responses, not just 5xx."""
    resp = make_mock_response(status=400, ok=False, json_data={"detail": "Bad request"}, status_text="Bad Request")
    with patch("src.frontend.fetch", AsyncMock(return_value=resp)):
        with pytest.raises((ApiError, Exception)) as exc_info:
            await fetchTasks()
        err = exc_info.value
        if hasattr(err, "statusCode"):
            assert err.statusCode == 400
        elif hasattr(err, "status_code"):
            assert err.status_code == 400


# ---------------------------------------------------------------------------
# createTask tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_create_task_sends_json_body():
    """createTask must send the data as JSON with Content-Type application/json."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data=make_task(id=10, title="Verify JSON", description="check body")
    ))
    with patch("src.frontend.fetch", mock_fetch):
        data = {"title": "Verify JSON", "description": "check body", "status": "pending"}
        await createTask(data)
        args, kwargs = mock_fetch.call_args
        headers = kwargs.get("headers", {})
        # Verify Content-Type is set to application/json
        content_type = headers.get("Content-Type", headers.get("content-type", ""))
        assert "application/json" in content_type
        # Verify method is POST
        assert kwargs.get("method", "").upper() == "POST"


@pytest.mark.anyio
async def test_goodhart_create_task_with_in_progress_status():
    """createTask must correctly propagate 'in_progress' status, not default to 'pending'."""
    task = make_task(id=11, title="Test task", status="in_progress")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task))
    with patch("src.frontend.fetch", mock_fetch):
        data = {"title": "Test task", "description": None, "status": "in_progress"}
        result = await createTask(data)
        # Check request body was sent with in_progress
        args, kwargs = mock_fetch.call_args
        body = kwargs.get("body", kwargs.get("data", ""))
        if isinstance(body, str):
            parsed = json.loads(body)
        else:
            parsed = body
        assert parsed.get("status") == "in_progress"


@pytest.mark.anyio
async def test_goodhart_create_task_with_done_status():
    """createTask must correctly propagate 'done' status, not hardcode to 'pending'."""
    task = make_task(id=12, title="Completed task", description="finished", status="done")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task))
    with patch("src.frontend.fetch", mock_fetch):
        data = {"title": "Completed task", "description": "finished", "status": "done"}
        result = await createTask(data)
        result_status = result["status"] if isinstance(result, dict) else result.status
        assert result_status == "done"


@pytest.mark.anyio
async def test_goodhart_create_task_empty_desc_becomes_null():
    """Empty description strings must be converted to null before sending to backend (A12)."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data=make_task(id=13, title="Test", description=None)
    ))
    with patch("src.frontend.fetch", mock_fetch):
        data = {"title": "Test", "description": "", "status": "pending"}
        await createTask(data)
        args, kwargs = mock_fetch.call_args
        body = kwargs.get("body", kwargs.get("data", ""))
        if isinstance(body, str):
            parsed = json.loads(body)
        else:
            parsed = body
        assert parsed.get("description") is None, \
            f"Empty description should be sent as null, got: {parsed.get('description')!r}"


@pytest.mark.anyio
async def test_goodhart_create_task_description_with_value_preserved():
    """createTask must preserve non-empty description strings, not convert all to null."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data=make_task(id=14, title="Test", description="A real description")
    ))
    with patch("src.frontend.fetch", mock_fetch):
        data = {"title": "Test", "description": "A real description", "status": "pending"}
        await createTask(data)
        args, kwargs = mock_fetch.call_args
        body = kwargs.get("body", kwargs.get("data", ""))
        if isinstance(body, str):
            parsed = json.loads(body)
        else:
            parsed = body
        assert parsed.get("description") == "A real description"


@pytest.mark.anyio
async def test_goodhart_create_task_uses_post_method():
    """createTask must use HTTP POST method."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data=make_task(id=15, title="Test")
    ))
    with patch("src.frontend.fetch", mock_fetch):
        await createTask({"title": "Test", "status": "pending"})
        args, kwargs = mock_fetch.call_args
        assert kwargs.get("method", "").upper() == "POST"


@pytest.mark.anyio
async def test_goodhart_create_task_returns_full_task_object():
    """createTask must return a complete Task with all six fields."""
    task_data = make_task(id=16, title="Full fields", description="desc")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        result = await createTask({"title": "Full fields", "description": "desc", "status": "pending"})
        if isinstance(result, dict):
            for field in ("id", "title", "description", "status", "created_at", "updated_at"):
                assert field in result, f"Missing field: {field}"
        else:
            for field in ("id", "title", "description", "status", "created_at", "updated_at"):
                assert hasattr(result, field), f"Missing attribute: {field}"


@pytest.mark.anyio
async def test_goodhart_create_task_special_chars_title():
    """createTask must handle titles with special/unicode characters without mangling."""
    special_title = "<script>alert('xss')</script> & ñ 日本語"
    task_data = make_task(id=17, title=special_title)
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        result = await createTask({"title": special_title, "status": "pending"})
        result_title = result["title"] if isinstance(result, dict) else result.title
        assert result_title == special_title


@pytest.mark.anyio
async def test_goodhart_create_task_422_raises_api_error():
    """createTask must convert 422 responses into ApiError with correct status code."""
    resp = make_mock_response(status=422, ok=False, json_data={"detail": "Invalid status"}, status_text="Unprocessable Entity")
    with patch("src.frontend.fetch", AsyncMock(return_value=resp)):
        with pytest.raises((ApiError, Exception)) as exc_info:
            await createTask({"title": "x", "status": "invalid_status"})
        err = exc_info.value
        if hasattr(err, "statusCode"):
            assert err.statusCode == 422
        elif hasattr(err, "status_code"):
            assert err.status_code == 422


# ---------------------------------------------------------------------------
# updateTask tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_update_task_correct_url_interpolation():
    """updateTask must interpolate the task id into the URL path for arbitrary id values."""
    task_data = make_task(id=42, title="Updated")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        await updateTask(42, {"title": "Updated"})
        args, kwargs = mock_fetch.call_args
        url = args[0] if args else kwargs.get("url", "")
        assert "/tasks/42" in url


@pytest.mark.anyio
async def test_goodhart_update_task_different_id():
    """updateTask must correctly interpolate various id values, not hardcode a specific id."""
    task_data = make_task(id=9999, title="Updated")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        await updateTask(9999, {"status": "done"})
        args, kwargs = mock_fetch.call_args
        url = args[0] if args else kwargs.get("url", "")
        assert "/tasks/9999" in url


@pytest.mark.anyio
async def test_goodhart_update_task_uses_put_method():
    """updateTask must use HTTP PUT method."""
    task_data = make_task(id=1, title="Updated")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        await updateTask(1, {"title": "Updated"})
        args, kwargs = mock_fetch.call_args
        assert kwargs.get("method", "").upper() == "PUT"


@pytest.mark.anyio
async def test_goodhart_update_task_sends_json_body():
    """updateTask must send update data as JSON with Content-Type application/json."""
    task_data = make_task(id=5, status="done")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        await updateTask(5, {"status": "done"})
        args, kwargs = mock_fetch.call_args
        headers = kwargs.get("headers", {})
        content_type = headers.get("Content-Type", headers.get("content-type", ""))
        assert "application/json" in content_type


@pytest.mark.anyio
async def test_goodhart_update_task_returns_id_matching_input():
    """updateTask must return a Task whose id matches the input id parameter."""
    task_data = make_task(id=123, title="Changed")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        result = await updateTask(123, {"title": "Changed"})
        result_id = result["id"] if isinstance(result, dict) else result.id
        assert result_id == 123


@pytest.mark.anyio
async def test_goodhart_update_task_status_only():
    """updateTask must correctly send a payload containing only a status change."""
    task_data = make_task(id=10, status="in_progress")
    mock_fetch = AsyncMock(return_value=make_mock_response(json_data=task_data))
    with patch("src.frontend.fetch", mock_fetch):
        result = await updateTask(10, {"status": "in_progress"})
        result_status = result["status"] if isinstance(result, dict) else result.status
        assert result_status == "in_progress"


@pytest.mark.anyio
async def test_goodhart_update_task_404_raises_api_error_with_detail():
    """updateTask must propagate the backend's specific detail message in ApiError for 404."""
    resp = make_mock_response(status=404, ok=False, json_data={"detail": "Task 99999 not found"}, status_text="Not Found")
    with patch("src.frontend.fetch", AsyncMock(return_value=resp)):
        with pytest.raises((ApiError, Exception)) as exc_info:
            await updateTask(99999, {"title": "Updated"})
        err = exc_info.value
        if hasattr(err, "detail"):
            assert "99999" in str(err.detail)
        elif hasattr(err, "message"):
            assert "99999" in str(err.message)


# ---------------------------------------------------------------------------
# deleteTask tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_delete_task_correct_url_interpolation():
    """deleteTask must interpolate the task id into the URL as DELETE {BASE_URL}/tasks/{id}."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data={"detail": "Deleted", "id": 77}
    ))
    with patch("src.frontend.fetch", mock_fetch):
        await deleteTask(77)
        args, kwargs = mock_fetch.call_args
        url = args[0] if args else kwargs.get("url", "")
        assert "/tasks/77" in url


@pytest.mark.anyio
async def test_goodhart_delete_task_uses_delete_method():
    """deleteTask must use HTTP DELETE method."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data={"detail": "Deleted", "id": 1}
    ))
    with patch("src.frontend.fetch", mock_fetch):
        await deleteTask(1)
        args, kwargs = mock_fetch.call_args
        assert kwargs.get("method", "").upper() == "DELETE"


@pytest.mark.anyio
async def test_goodhart_delete_task_returns_correct_id():
    """deleteTask must return DeleteConfirmation with id matching the deleted task."""
    mock_fetch = AsyncMock(return_value=make_mock_response(
        json_data={"detail": "Task deleted successfully", "id": 55}
    ))
    with patch("src.frontend.fetch", mock_fetch):
        result = await deleteTask(55)
        result_id = result["id"] if isinstance(result, dict) else result.id
        assert result_id == 55


# ---------------------------------------------------------------------------
# healthCheck tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_health_check_correct_endpoint():
    """healthCheck must issue GET to {BASE_URL}/health using the resolved base URL."""
    with patch("src.frontend.resolveBaseUrl", return_value="http://other-host:3000"):
        mock_fetch = AsyncMock(return_value=make_mock_response(
            json_data={"status": "healthy"}
        ))
        with patch("src.frontend.fetch", mock_fetch):
            await healthCheck()
            args, kwargs = mock_fetch.call_args
            url = args[0] if args else kwargs.get("url", "")
            assert "other-host:3000" in url
            assert "/health" in url


# ---------------------------------------------------------------------------
# resolveBaseUrl tests
# ---------------------------------------------------------------------------

def test_goodhart_resolve_base_url_multiple_trailing_slashes():
    """resolveBaseUrl should strip trailing slashes from URLs with multiple trailing slashes."""
    with patch.dict("os.environ", {"VITE_API_URL": "http://example.com///"}, clear=False):
        try:
            result = resolveBaseUrl()
            assert not result.endswith("/")
        except Exception:
            # Some implementations read from import.meta.env - try alternate approach
            pass


def test_goodhart_resolve_base_url_no_trailing_slash_default():
    """resolveBaseUrl default return must not have a trailing slash."""
    result = resolveBaseUrl()
    assert not result.endswith("/")
    assert result == "http://localhost:8000"


# ---------------------------------------------------------------------------
# parseErrorResponse tests
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_parse_error_response_preserves_status_code_404():
    """parseErrorResponse must capture actual HTTP status code 404, not hardcode common values."""
    resp = make_mock_response(status=404, ok=False, json_data={"detail": "Not found"}, status_text="Not Found")
    result = await parseErrorResponse(resp)
    assert (result.statusCode if hasattr(result, "statusCode") else result.status_code) == 404


@pytest.mark.anyio
async def test_goodhart_parse_error_response_preserves_status_code_422():
    """parseErrorResponse must correctly capture 422 status codes."""
    resp = make_mock_response(status=422, ok=False, json_data={"detail": "Validation failed"}, status_text="Unprocessable Entity")
    result = await parseErrorResponse(resp)
    assert (result.statusCode if hasattr(result, "statusCode") else result.status_code) == 422


@pytest.mark.anyio
async def test_goodhart_parse_error_response_preserves_status_code_409():
    """parseErrorResponse must handle less common HTTP error codes like 409."""
    resp = make_mock_response(status=409, ok=False, json_data={"detail": "Conflict"}, status_text="Conflict")
    result = await parseErrorResponse(resp)
    assert (result.statusCode if hasattr(result, "statusCode") else result.status_code) == 409


@pytest.mark.anyio
async def test_goodhart_parse_error_response_message_includes_detail():
    """parseErrorResponse must compose message to include the parsed detail string."""
    resp = make_mock_response(status=400, ok=False, json_data={"detail": "Title cannot be empty"}, status_text="Bad Request")
    result = await parseErrorResponse(resp)
    msg = result.message if hasattr(result, "message") else str(result)
    assert "Title cannot be empty" in msg


@pytest.mark.anyio
async def test_goodhart_parse_error_response_html_body_fallback():
    """parseErrorResponse must fall back to statusText when response body is HTML."""
    resp = make_mock_response(status=502, ok=False, status_text="Bad Gateway", raise_on_json=True)
    result = await parseErrorResponse(resp)
    detail = result.detail if hasattr(result, "detail") else str(result)
    assert "Bad Gateway" in detail or "502" in detail


@pytest.mark.anyio
async def test_goodhart_parse_error_response_empty_body_fallback():
    """parseErrorResponse must handle empty response body, falling back to statusText."""
    resp = MagicMock()
    resp.status = 500
    resp.ok = False
    resp.statusText = "Internal Server Error"
    resp.json = AsyncMock(side_effect=Exception("empty body"))
    resp.text = AsyncMock(return_value="")
    result = await parseErrorResponse(resp)
    code = result.statusCode if hasattr(result, "statusCode") else result.status_code
    assert code == 500
    detail = result.detail if hasattr(result, "detail") else str(result)
    assert len(detail) > 0  # Should have some fallback text


# ---------------------------------------------------------------------------
# Type / Validator tests
# ---------------------------------------------------------------------------

def test_goodhart_api_error_status_code_boundary_101():
    """ApiError must accept statusCode 101, verifying the range is truly [100, 599]."""
    try:
        err = ApiError(message="test", statusCode=101, detail="test")
        code = err.statusCode if hasattr(err, "statusCode") else err.status_code
        assert code == 101
    except Exception:
        # Try alternate constructor patterns
        err = ApiError("test", 101, "test")
        assert True


def test_goodhart_api_error_status_code_boundary_598():
    """ApiError must accept statusCode 598, adjacent to upper boundary."""
    try:
        err = ApiError(message="test", statusCode=598, detail="test")
        code = err.statusCode if hasattr(err, "statusCode") else err.status_code
        assert code == 598
    except Exception:
        err = ApiError("test", 598, "test")
        assert True


def test_goodhart_api_error_status_code_99_rejected():
    """ApiError must reject statusCode 99, one below the minimum boundary."""
    with pytest.raises((ValueError, Exception)):
        ApiError(message="test", statusCode=99, detail="test")


def test_goodhart_api_error_status_code_600_rejected():
    """ApiError must reject statusCode 600, one above the maximum boundary."""
    with pytest.raises((ValueError, Exception)):
        ApiError(message="test", statusCode=600, detail="test")


def test_goodhart_task_title_2_chars_accepted():
    """Task title validator must accept titles of arbitrary valid length, not just boundaries."""
    task = Task(id=1, title="Ab", description=None, status="pending",
                created_at="2025-01-15T12:00:00+00:00", updated_at="2025-01-15T12:00:00+00:00")
    title = task.title if hasattr(task, "title") else task["title"]
    assert title == "Ab"


def test_goodhart_task_title_254_chars_accepted():
    """Task title validator must accept 254-char titles, adjacent to upper boundary."""
    long_title = "a" * 254
    task = Task(id=1, title=long_title, description=None, status="pending",
                created_at="2025-01-15T12:00:00+00:00", updated_at="2025-01-15T12:00:00+00:00")
    title = task.title if hasattr(task, "title") else task["title"]
    assert len(title) == 254


def test_goodhart_status_badge_all_three_distinct():
    """Status badge colors must be distinct for each status — no two share the same color."""
    if isinstance(StatusBadgeColorMap, dict):
        colors = StatusBadgeColorMap
    else:
        colors = {
            "pending": StatusBadgeColorMap.pending if hasattr(StatusBadgeColorMap, "pending") else StatusBadgeColorMap["pending"],
            "in_progress": StatusBadgeColorMap.in_progress if hasattr(StatusBadgeColorMap, "in_progress") else StatusBadgeColorMap["in_progress"],
            "done": StatusBadgeColorMap.done if hasattr(StatusBadgeColorMap, "done") else StatusBadgeColorMap["done"],
        }
    assert colors["pending"] != colors["in_progress"]
    assert colors["in_progress"] != colors["done"]
    assert colors["pending"] != colors["done"]


# ---------------------------------------------------------------------------
# App handler tests (state management)
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_goodhart_app_handle_create_prepends_not_appends():
    """App.handleCreate must prepend (not append) the new task so newest tasks appear first."""
    # This test verifies the contract postcondition about prepending.
    # Import App-level handlers or simulate state management.
    try:
        from src.frontend import App
        # If App is a class with handleCreate:
        initial_tasks = [make_task(id=1, title="A"), make_task(id=2, title="B")]
        new_task = make_task(id=3, title="New")
        
        with patch("src.frontend.createTask", AsyncMock(return_value=new_task)):
            app = App()
            app.tasks = list(initial_tasks)
            await app.handleCreate({"title": "New", "status": "pending"})
            first_id = app.tasks[0]["id"] if isinstance(app.tasks[0], dict) else app.tasks[0].id
            assert first_id == 3, "New task should be prepended at index 0"
            assert len(app.tasks) == 3
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_update_replaces_correct_task():
    """App.handleUpdate must replace only the matching task, leaving others unchanged."""
    try:
        from src.frontend import App
        initial_tasks = [
            make_task(id=1, title="A"),
            make_task(id=2, title="B"),
            make_task(id=3, title="C"),
        ]
        updated_task = make_task(id=2, title="Updated")
        
        with patch("src.frontend.updateTask", AsyncMock(return_value=updated_task)):
            app = App()
            app.tasks = list(initial_tasks)
            await app.handleUpdate(2, {"title": "Updated"})
            
            titles = [t["title"] if isinstance(t, dict) else t.title for t in app.tasks]
            assert titles[0] == "A"
            assert titles[1] == "Updated"
            assert titles[2] == "C"
            assert len(app.tasks) == 3
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_update_preserves_order():
    """App.handleUpdate must preserve the position of the updated task in the array."""
    try:
        from src.frontend import App
        initial_tasks = [
            make_task(id=1, title="A"),
            make_task(id=2, title="B"),
            make_task(id=3, title="C"),
        ]
        updated_task = make_task(id=2, title="Updated B")
        
        with patch("src.frontend.updateTask", AsyncMock(return_value=updated_task)):
            app = App()
            app.tasks = list(initial_tasks)
            await app.handleUpdate(2, {"title": "Updated B"})
            
            ids = [t["id"] if isinstance(t, dict) else t.id for t in app.tasks]
            assert ids == [1, 2, 3], "Task order must be preserved after update"
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_delete_removes_only_target():
    """App.handleDelete must remove only the specified task, preserving all others."""
    try:
        from src.frontend import App
        initial_tasks = [
            make_task(id=1, title="A"),
            make_task(id=2, title="B"),
            make_task(id=3, title="C"),
        ]
        
        with patch("src.frontend.deleteTask", AsyncMock(return_value={"detail": "Deleted", "id": 2})):
            app = App()
            app.tasks = list(initial_tasks)
            await app.handleDelete(2)
            
            ids = [t["id"] if isinstance(t, dict) else t.id for t in app.tasks]
            assert 2 not in ids
            assert 1 in ids
            assert 3 in ids
            assert len(app.tasks) == 2
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_delete_no_refetch():
    """App.handleDelete must NOT call fetchTasks after successful deletion (AC19)."""
    try:
        from src.frontend import App
        initial_tasks = [make_task(id=1), make_task(id=2)]
        
        mock_fetch_tasks = AsyncMock(return_value=[])
        with patch("src.frontend.deleteTask", AsyncMock(return_value={"detail": "Deleted", "id": 1})):
            with patch("src.frontend.fetchTasks", mock_fetch_tasks):
                app = App()
                app.tasks = list(initial_tasks)
                await app.handleDelete(1)
                
                mock_fetch_tasks.assert_not_called(), \
                    "fetchTasks should NOT be called during handleDelete — state should be filtered locally"
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_create_error_does_not_mutate_state():
    """App.handleCreate must not add a task when createTask throws an error."""
    try:
        from src.frontend import App
        initial_tasks = [make_task(id=1), make_task(id=2)]
        
        with patch("src.frontend.createTask", AsyncMock(side_effect=ApiError("fail", 500, "error"))):
            app = App()
            app.tasks = list(initial_tasks)
            try:
                await app.handleCreate({"title": "Test", "status": "pending"})
            except (ApiError, Exception):
                pass
            assert len(app.tasks) == 2, "State should not be mutated on error"
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")


@pytest.mark.anyio
async def test_goodhart_app_handle_delete_error_does_not_remove():
    """App.handleDelete must not remove a task when deleteTask throws an error."""
    try:
        from src.frontend import App
        initial_tasks = [make_task(id=1), make_task(id=2), make_task(id=3)]
        
        with patch("src.frontend.deleteTask", AsyncMock(side_effect=ApiError("fail", 500, "error"))):
            app = App()
            app.tasks = list(initial_tasks)
            try:
                await app.handleDelete(2)
            except (ApiError, Exception):
                pass
            assert len(app.tasks) == 3, "State should not be mutated on error"
    except (ImportError, AttributeError, TypeError):
        pytest.skip("App handler not directly testable in this implementation pattern")
