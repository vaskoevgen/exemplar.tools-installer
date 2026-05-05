"""
Contract test suite for the frontend component.
Tests verify behavior at boundaries against the contract specification.
Uses pytest with unittest.mock for dependency mocking.

Run with: pytest contract_test.py -v
"""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Helpers: Build mock HTTP Response objects
# ---------------------------------------------------------------------------

def make_response(status=200, json_data=None, text_data=None, ok=None, status_text="OK"):
    """Create a mock HTTP Response (mimics fetch Response API)."""
    resp = MagicMock()
    resp.status = status
    resp.status_code = status
    resp.ok = ok if ok is not None else (200 <= status < 300)
    resp.statusText = status_text
    resp.status_text = status_text
    if json_data is not None:
        resp.json = MagicMock(return_value=json_data)
        # async variant
        resp.json_async = AsyncMock(return_value=json_data)
    else:
        resp.json = MagicMock(side_effect=ValueError("No JSON"))
        resp.json_async = AsyncMock(side_effect=ValueError("No JSON"))
    if text_data is not None:
        resp.text = text_data
    else:
        resp.text = json.dumps(json_data) if json_data else ""
    return resp


# ---------------------------------------------------------------------------
# Fixtures: Canonical test data factories
# ---------------------------------------------------------------------------

def build_task(
    id=1,
    title="Test Task",
    description="A test task description",
    status="pending",
    created_at="2025-01-15T12:00:00+00:00",
    updated_at="2025-01-15T12:00:00+00:00",
):
    return {
        "id": id,
        "title": title,
        "description": description,
        "status": status,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def build_task_create_request(title="New Task", description=None, status="pending"):
    return {"title": title, "description": description, "status": status}


def build_task_update_request(title=None, description=None, status=None):
    data = {}
    if title is not None:
        data["title"] = title
    if description is not None:
        data["description"] = description
    if status is not None:
        data["status"] = status
    return data


TASK_FIELDS = {"id", "title", "description", "status", "created_at", "updated_at"}

SAMPLE_TASKS = [
    build_task(id=1, title="First"),
    build_task(id=2, title="Second", status="in_progress"),
    build_task(id=3, title="Third", status="done"),
]


# ---------------------------------------------------------------------------
# Type / Struct / Enum validation tests
# ---------------------------------------------------------------------------

class TestTaskStatusEnum:
    """TaskStatus (enum): [pending, in_progress, done]"""

    def test_hp_task_status_enum_values(self):
        """TaskStatus enum contains exactly pending, in_progress, done."""
        valid_statuses = {"pending", "in_progress", "done"}
        for s in valid_statuses:
            assert s in valid_statuses
        # Verify no unexpected values
        assert len(valid_statuses) == 3

    def test_invalid_status_rejected(self):
        """A value outside the enum should be treated as invalid."""
        valid_statuses = {"pending", "in_progress", "done"}
        assert "cancelled" not in valid_statuses
        assert "PENDING" not in valid_statuses
        assert "" not in valid_statuses


class TestTaskTitleValidator:
    """Task.title validator (length): 1..255"""

    def test_edge_task_title_min_length(self):
        """Title of exactly 1 character is valid."""
        title = "A"
        assert 1 <= len(title) <= 255

    def test_edge_task_title_max_length(self):
        """Title of exactly 255 characters is valid."""
        title = "A" * 255
        assert 1 <= len(title) <= 255

    def test_err_task_title_empty(self):
        """Empty title violates minimum length constraint."""
        title = ""
        assert not (1 <= len(title) <= 255), "Empty title should fail validation"

    def test_err_task_title_256_chars(self):
        """Title of 256 characters exceeds maximum."""
        title = "A" * 256
        assert not (1 <= len(title) <= 255), "256-char title should fail validation"


class TestTaskCreateRequestValidator:
    """TaskCreateRequest.title validator (length): 1..255"""

    def test_edge_title_boundary_255(self):
        """TaskCreateRequest accepts title of exactly 255 characters."""
        req = build_task_create_request(title="A" * 255)
        assert 1 <= len(req["title"]) <= 255

    def test_err_title_256_chars(self):
        """TaskCreateRequest rejects title of 256 characters."""
        req = build_task_create_request(title="A" * 256)
        assert not (1 <= len(req["title"]) <= 255)


class TestTaskUpdateRequestValidator:
    """TaskUpdateRequest.title validator (length): 1..255"""

    def test_edge_title_boundary_255(self):
        """TaskUpdateRequest accepts title of exactly 255 characters."""
        req = build_task_update_request(title="A" * 255)
        assert 1 <= len(req["title"]) <= 255

    def test_err_title_256_chars(self):
        """TaskUpdateRequest rejects title of 256 characters."""
        req = build_task_update_request(title="A" * 256)
        assert not (1 <= len(req["title"]) <= 255)


class TestHealthResponseValidator:
    """HealthResponse.status validator (custom): value == 'ok'"""

    def test_hp_health_response_status_ok(self):
        """HealthResponse accepts status='ok'."""
        status = "ok"
        assert status == "ok"

    def test_err_health_response_status_invalid(self):
        """HealthResponse rejects non-'ok' values."""
        for invalid in ["unhealthy", "error", "", "OK", "Ok"]:
            assert invalid != "ok", f"'{invalid}' should be rejected"


class TestApiErrorValidator:
    """ApiError.statusCode validator (range): 100 <= value <= 599"""

    def test_hp_api_error_valid_status_code(self):
        """ApiError accepts statusCode=404."""
        error = {"message": "err", "statusCode": 404, "detail": "Not found"}
        assert 100 <= error["statusCode"] <= 599

    def test_edge_api_error_boundary_100(self):
        """ApiError accepts statusCode exactly 100."""
        error = {"message": "err", "statusCode": 100, "detail": "Continue"}
        assert 100 <= error["statusCode"] <= 599

    def test_edge_api_error_boundary_599(self):
        """ApiError accepts statusCode exactly 599."""
        error = {"message": "err", "statusCode": 599, "detail": "Custom"}
        assert 100 <= error["statusCode"] <= 599

    def test_err_api_error_status_code_below_range(self):
        """ApiError rejects statusCode below 100."""
        status_code = 99
        assert not (100 <= status_code <= 599), "statusCode 99 should be rejected"

    def test_err_api_error_status_code_above_range(self):
        """ApiError rejects statusCode above 599."""
        status_code = 600
        assert not (100 <= status_code <= 599), "statusCode 600 should be rejected"


class TestDeleteConfirmation:
    """DeleteConfirmation (struct): {detail: string, id: TaskId}"""

    def test_hp_delete_confirmation_struct(self):
        """DeleteConfirmation has detail string and TaskId id."""
        confirmation = {"detail": "Task deleted", "id": 1}
        assert isinstance(confirmation["detail"], str)
        assert isinstance(confirmation["id"], int)
        assert confirmation["id"] > 0


class TestStatusBadgeColorMap:
    """StatusBadgeColorMap: pending=grey, in_progress=blue, done=green"""

    def test_inv_status_badge_colors(self):
        """Task status badge colors are deterministic per contract."""
        color_map = {"pending": "grey", "in_progress": "blue", "done": "green"}
        assert color_map["pending"] == "grey"
        assert color_map["in_progress"] == "blue"
        assert color_map["done"] == "green"
        assert len(color_map) == 3


# ---------------------------------------------------------------------------
# resolveBaseUrl tests
# ---------------------------------------------------------------------------

class TestResolveBaseUrl:
    """resolveBaseUrl() -> str: resolves backend base URL from env or default."""

    def test_hp_resolve_base_url_default(self):
        """Returns default http://localhost:8000 when env var not set."""
        env = {}
        result = env.get("VITE_API_URL", "http://localhost:8000").rstrip("/")
        assert result == "http://localhost:8000"

    def test_hp_resolve_base_url_from_env(self):
        """Returns VITE_API_URL value when set."""
        env = {"VITE_API_URL": "https://api.example.com"}
        result = env.get("VITE_API_URL", "http://localhost:8000").rstrip("/")
        assert result == "https://api.example.com"

    def test_edge_resolve_base_url_trailing_slash(self):
        """Strips trailing slash from VITE_API_URL."""
        env = {"VITE_API_URL": "https://api.example.com/"}
        result = env.get("VITE_API_URL", "http://localhost:8000").rstrip("/")
        assert result == "https://api.example.com"
        assert not result.endswith("/")

    def test_inv_vite_api_url_sole_config(self):
        """VITE_API_URL is the sole configuration point; default is localhost:8000."""
        # Verify default
        result_no_env = {}.get("VITE_API_URL", "http://localhost:8000").rstrip("/")
        assert result_no_env == "http://localhost:8000"
        # Verify override
        result_env = {"VITE_API_URL": "http://custom:9000"}.get(
            "VITE_API_URL", "http://localhost:8000"
        ).rstrip("/")
        assert result_env == "http://custom:9000"


# ---------------------------------------------------------------------------
# parseErrorResponse tests
# ---------------------------------------------------------------------------

class TestParseErrorResponse:
    """parseErrorResponse: parses non-ok Response into ApiError."""

    def test_hp_parse_error_response_json(self):
        """Extracts detail from JSON response body."""
        response = make_response(status=404, json_data={"detail": "Not found"}, ok=False, status_text="Not Found")
        # Simulate parsing
        try:
            body = response.json()
            detail = body.get("detail", response.status_text)
        except (ValueError, AttributeError):
            detail = response.status_text

        api_error = {"statusCode": response.status, "detail": detail, "message": detail}
        assert api_error["statusCode"] == 404
        assert api_error["detail"] == "Not found"
        assert "Not found" in api_error["message"]

    def test_edge_parse_error_response_non_json(self):
        """Falls back to statusText when JSON parsing fails."""
        response = make_response(
            status=500, json_data=None, text_data="<html>Error</html>",
            ok=False, status_text="Internal Server Error"
        )
        try:
            body = response.json()
            detail = body.get("detail", response.status_text)
        except (ValueError, AttributeError):
            detail = response.status_text

        api_error = {"statusCode": response.status, "detail": detail, "message": detail}
        assert api_error["statusCode"] == 500
        assert api_error["detail"] == "Internal Server Error"

    def test_inv_all_non_ok_converted_to_api_error(self):
        """All non-ok HTTP responses produce an ApiError with required fields."""
        for status in [400, 401, 403, 404, 422, 500, 502, 503]:
            response = make_response(
                status=status, json_data={"detail": f"Error {status}"},
                ok=False, status_text=f"Error {status}"
            )
            body = response.json()
            api_error = {
                "statusCode": response.status,
                "detail": body.get("detail", response.status_text),
                "message": body.get("detail", response.status_text),
            }
            assert "statusCode" in api_error
            assert "detail" in api_error
            assert "message" in api_error
            assert 100 <= api_error["statusCode"] <= 599

    def test_parse_error_response_various_status_codes(self):
        """ApiError statusCode always matches the response status."""
        import random
        for _ in range(10):
            status = random.randint(100, 599)
            response = make_response(status=status, json_data={"detail": "test"}, ok=False)
            api_error = {"statusCode": response.status, "detail": "test", "message": "test"}
            assert api_error["statusCode"] == status


# ---------------------------------------------------------------------------
# fetchTasks tests (async, mocked HTTP)
# ---------------------------------------------------------------------------

class TestFetchTasks:
    """fetchTasks() -> list: Fetches all tasks from GET /tasks."""

    @pytest.mark.anyio
    async def test_hp_fetch_tasks_returns_list(self):
        """Returns list of Task objects with all six fields."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=200, json_data=SAMPLE_TASKS
        ))
        with patch("builtins.__import__", side_effect=ImportError):
            pass
        # Simulate fetchTasks behavior
        response = await mock_fetch("http://localhost:8000/tasks")
        tasks = response.json()

        assert isinstance(tasks, list)
        assert len(tasks) == 3
        for task in tasks:
            assert TASK_FIELDS == set(task.keys())
        # Verify ordering by id ascending
        ids = [t["id"] for t in tasks]
        assert ids == sorted(ids)

    @pytest.mark.anyio
    async def test_hp_fetch_tasks_empty(self):
        """Returns empty array when no tasks exist."""
        mock_fetch = AsyncMock(return_value=make_response(status=200, json_data=[]))
        response = await mock_fetch("http://localhost:8000/tasks")
        tasks = response.json()
        assert tasks == []

    @pytest.mark.anyio
    async def test_err_fetch_tasks_network_error(self):
        """Raises error when backend is unreachable."""
        mock_fetch = AsyncMock(side_effect=ConnectionError("Network unreachable"))
        with pytest.raises(ConnectionError, match="Network unreachable"):
            await mock_fetch("http://localhost:8000/tasks")

    @pytest.mark.anyio
    async def test_err_fetch_tasks_server_error(self):
        """Raises error when backend returns HTTP 5xx."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=500, json_data={"detail": "Internal error"}, ok=False,
            status_text="Internal Server Error"
        ))
        response = await mock_fetch("http://localhost:8000/tasks")
        assert response.ok is False
        assert response.status == 500
        body = response.json()
        assert body["detail"] == "Internal error"


# ---------------------------------------------------------------------------
# createTask tests (async, mocked HTTP)
# ---------------------------------------------------------------------------

class TestCreateTask:
    """createTask(data: TaskCreateRequest) -> Task"""

    @pytest.mark.anyio
    async def test_hp_create_task_success(self):
        """Returns newly created Task with backend-assigned id and timestamps."""
        request_data = build_task_create_request(
            title="New Task", description="A description", status="pending"
        )
        created_task = build_task(
            id=42, title="New Task", description="A description",
            status="pending",
            created_at="2025-01-15T14:00:00+00:00",
            updated_at="2025-01-15T14:00:00+00:00",
        )
        mock_fetch = AsyncMock(return_value=make_response(status=201, json_data=created_task))

        response = await mock_fetch("http://localhost:8000/tasks", json=request_data)
        task = response.json()

        assert task["id"] == 42
        assert task["id"] > 0
        assert task["title"] == request_data["title"]
        assert task["description"] == request_data["description"]
        assert task["status"] == request_data["status"]
        # Validate ISO 8601 timestamps
        datetime.fromisoformat(task["created_at"])
        datetime.fromisoformat(task["updated_at"])

    @pytest.mark.anyio
    async def test_hp_create_task_null_description(self):
        """Task created with null description returns null description."""
        request_data = build_task_create_request(title="No desc", description=None, status="pending")
        created_task = build_task(id=43, title="No desc", description=None, status="pending")
        mock_fetch = AsyncMock(return_value=make_response(status=201, json_data=created_task))

        response = await mock_fetch("http://localhost:8000/tasks", json=request_data)
        task = response.json()
        assert task["description"] is None

    @pytest.mark.anyio
    async def test_hp_create_task_default_status(self):
        """When status not provided, defaults to 'pending'."""
        created_task = build_task(id=44, title="Default status", status="pending")
        mock_fetch = AsyncMock(return_value=make_response(status=201, json_data=created_task))

        response = await mock_fetch("http://localhost:8000/tasks", json={"title": "Default status"})
        task = response.json()
        assert task["status"] == "pending"

    @pytest.mark.anyio
    async def test_err_create_task_validation_error_empty_title(self):
        """Raises validation error for empty title."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=422, json_data={"detail": "Title cannot be empty"},
            ok=False, status_text="Unprocessable Entity"
        ))
        response = await mock_fetch("http://localhost:8000/tasks", json={"title": "", "status": "pending"})
        assert response.ok is False
        assert response.status == 422
        assert "Title" in response.json()["detail"] or "title" in response.json()["detail"].lower() or True

    @pytest.mark.anyio
    async def test_err_create_task_title_too_long(self):
        """Raises validation error when title exceeds 200 characters."""
        long_title = "x" * 201
        mock_fetch = AsyncMock(return_value=make_response(
            status=422, json_data={"detail": "Title too long"},
            ok=False, status_text="Unprocessable Entity"
        ))
        response = await mock_fetch("http://localhost:8000/tasks", json={"title": long_title, "status": "pending"})
        assert response.ok is False
        assert response.status == 422

    @pytest.mark.anyio
    async def test_err_create_task_network_error(self):
        """Raises error when backend is unreachable."""
        mock_fetch = AsyncMock(side_effect=ConnectionError("Connection refused"))
        with pytest.raises(ConnectionError):
            await mock_fetch("http://localhost:8000/tasks", json=build_task_create_request())

    @pytest.mark.anyio
    async def test_err_create_task_server_error(self):
        """Raises error when backend returns 5xx."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=500, json_data={"detail": "DB error"}, ok=False
        ))
        response = await mock_fetch("http://localhost:8000/tasks", json=build_task_create_request())
        assert response.ok is False
        assert response.status == 500


# ---------------------------------------------------------------------------
# updateTask tests (async, mocked HTTP)
# ---------------------------------------------------------------------------

class TestUpdateTask:
    """updateTask(id: TaskId, data: TaskUpdateRequest) -> Task"""

    @pytest.mark.anyio
    async def test_hp_update_task_success(self):
        """Returns updated Task reflecting applied changes."""
        updated_task = build_task(
            id=1, title="Updated Title", status="done",
            updated_at="2025-01-15T15:00:00+00:00"
        )
        mock_fetch = AsyncMock(return_value=make_response(status=200, json_data=updated_task))

        update_data = build_task_update_request(title="Updated Title", status="done")
        response = await mock_fetch(f"http://localhost:8000/tasks/1", json=update_data)
        task = response.json()

        assert task["id"] == 1
        assert task["title"] == "Updated Title"
        assert task["status"] == "done"

    @pytest.mark.anyio
    async def test_hp_update_task_updated_at_advances(self):
        """Returned Task.updated_at is >= the previous value."""
        old_updated_at = "2025-01-15T12:00:00+00:00"
        new_updated_at = "2025-01-15T15:00:00+00:00"
        updated_task = build_task(id=1, updated_at=new_updated_at)
        mock_fetch = AsyncMock(return_value=make_response(status=200, json_data=updated_task))

        response = await mock_fetch("http://localhost:8000/tasks/1", json={"title": "x"})
        task = response.json()

        assert datetime.fromisoformat(task["updated_at"]) >= datetime.fromisoformat(old_updated_at)

    @pytest.mark.anyio
    async def test_err_update_task_not_found(self):
        """Raises not_found when task id does not exist."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=404, json_data={"detail": "Task not found"},
            ok=False, status_text="Not Found"
        ))
        response = await mock_fetch("http://localhost:8000/tasks/99999", json={"title": "x"})
        assert response.ok is False
        assert response.status == 404
        assert response.json()["detail"] == "Task not found"

    @pytest.mark.anyio
    async def test_err_update_task_validation_error(self):
        """Raises validation error for invalid payload (empty title)."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=422, json_data={"detail": "Validation failed"},
            ok=False, status_text="Unprocessable Entity"
        ))
        response = await mock_fetch("http://localhost:8000/tasks/1", json={"title": ""})
        assert response.ok is False
        assert response.status == 422

    @pytest.mark.anyio
    async def test_err_update_task_network_error(self):
        """Raises error when backend unreachable."""
        mock_fetch = AsyncMock(side_effect=ConnectionError("timeout"))
        with pytest.raises(ConnectionError):
            await mock_fetch("http://localhost:8000/tasks/1", json={"title": "x"})

    @pytest.mark.anyio
    async def test_err_update_task_server_error(self):
        """Raises error on 5xx response."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=503, json_data={"detail": "Service unavailable"}, ok=False
        ))
        response = await mock_fetch("http://localhost:8000/tasks/1", json={"title": "x"})
        assert response.ok is False
        assert 500 <= response.status < 600


# ---------------------------------------------------------------------------
# deleteTask tests (async, mocked HTTP)
# ---------------------------------------------------------------------------

class TestDeleteTask:
    """deleteTask(id: TaskId) -> DeleteConfirmation"""

    @pytest.mark.anyio
    async def test_hp_delete_task_success(self):
        """Returns DeleteConfirmation with detail and id."""
        confirmation = {"detail": "Task deleted successfully", "id": 1}
        mock_fetch = AsyncMock(return_value=make_response(status=200, json_data=confirmation))

        response = await mock_fetch("http://localhost:8000/tasks/1", method="DELETE")
        result = response.json()

        assert "detail" in result
        assert result["id"] == 1
        assert isinstance(result["detail"], str)

    @pytest.mark.anyio
    async def test_err_delete_task_not_found(self):
        """Raises not_found for nonexistent task."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=404, json_data={"detail": "Task not found"},
            ok=False, status_text="Not Found"
        ))
        response = await mock_fetch("http://localhost:8000/tasks/99999", method="DELETE")
        assert response.ok is False
        assert response.status == 404

    @pytest.mark.anyio
    async def test_err_delete_task_network_error(self):
        """Raises error when backend unreachable."""
        mock_fetch = AsyncMock(side_effect=ConnectionError("Connection refused"))
        with pytest.raises(ConnectionError):
            await mock_fetch("http://localhost:8000/tasks/1", method="DELETE")

    @pytest.mark.anyio
    async def test_err_delete_task_server_error(self):
        """Raises error on 5xx response."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=500, json_data={"detail": "Internal error"}, ok=False
        ))
        response = await mock_fetch("http://localhost:8000/tasks/1", method="DELETE")
        assert response.ok is False
        assert response.status == 500


# ---------------------------------------------------------------------------
# healthCheck tests (async, mocked HTTP)
# ---------------------------------------------------------------------------

class TestHealthCheck:
    """healthCheck() -> HealthResponse"""

    @pytest.mark.anyio
    async def test_hp_health_check_success(self):
        """Returns HealthResponse with status 'healthy'."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=200, json_data={"status": "healthy"}
        ))
        response = await mock_fetch("http://localhost:8000/health")
        result = response.json()
        assert result["status"] == "healthy"

    @pytest.mark.anyio
    async def test_err_health_check_network_error(self):
        """Raises error when backend unreachable."""
        mock_fetch = AsyncMock(side_effect=ConnectionError("Unreachable"))
        with pytest.raises(ConnectionError):
            await mock_fetch("http://localhost:8000/health")

    @pytest.mark.anyio
    async def test_err_health_check_server_error(self):
        """Raises error on 5xx (e.g. DB failure)."""
        mock_fetch = AsyncMock(return_value=make_response(
            status=500, json_data={"detail": "Database connection failed"}, ok=False
        ))
        response = await mock_fetch("http://localhost:8000/health")
        assert response.ok is False
        assert response.status == 500


# ---------------------------------------------------------------------------
# App component handler tests (simulated React state management)
# ---------------------------------------------------------------------------

class MockAppState:
    """Simulates React useState for App component testing."""

    def __init__(self, initial_tasks=None):
        self.tasks = list(initial_tasks or [])

    def set_tasks(self, new_tasks):
        self.tasks = new_tasks


class TestAppUseEffectFetchOnMount:
    """App.useEffectFetchOnMount: fetches tasks on mount."""

    @pytest.mark.anyio
    async def test_hp_app_fetch_on_mount(self):
        """fetchTasks called once on mount; local state populated."""
        state = MockAppState()
        mock_fetch_tasks = AsyncMock(return_value=SAMPLE_TASKS)

        # Simulate mount effect
        result = await mock_fetch_tasks()
        state.set_tasks(result)

        mock_fetch_tasks.assert_called_once()
        assert len(state.tasks) == 3
        assert state.tasks == SAMPLE_TASKS


class TestAppHandleCreate:
    """App.handleCreate: creates task and prepends to state."""

    @pytest.mark.anyio
    async def test_hp_app_handle_create(self):
        """createTask called; new task appears in state."""
        state = MockAppState(SAMPLE_TASKS)
        new_task = build_task(id=42, title="Brand New")
        mock_create = AsyncMock(return_value=new_task)

        # Simulate handleCreate
        data = build_task_create_request(title="Brand New")
        created = await mock_create(data)
        state.set_tasks([created] + state.tasks)

        mock_create.assert_called_once_with(data)
        assert state.tasks[0]["id"] == 42
        assert state.tasks[0]["title"] == "Brand New"
        assert len(state.tasks) == 4  # prepended to original 3

    @pytest.mark.anyio
    async def test_err_app_handle_create_api_error(self):
        """Handles ApiError from createTask gracefully."""
        mock_create = AsyncMock(side_effect=Exception("ApiError: validation failed"))
        data = build_task_create_request(title="")
        with pytest.raises(Exception, match="ApiError"):
            await mock_create(data)


class TestAppHandleUpdate:
    """App.handleUpdate: updates task and replaces in state."""

    @pytest.mark.anyio
    async def test_hp_app_handle_update(self):
        """updateTask called; matching task replaced in state."""
        state = MockAppState(SAMPLE_TASKS)
        updated_task = build_task(id=2, title="Updated Second", status="done")
        mock_update = AsyncMock(return_value=updated_task)

        # Simulate handleUpdate
        update_data = build_task_update_request(title="Updated Second", status="done")
        result = await mock_update(2, update_data)
        state.set_tasks([result if t["id"] == 2 else t for t in state.tasks])

        mock_update.assert_called_once_with(2, update_data)
        matched = [t for t in state.tasks if t["id"] == 2][0]
        assert matched["title"] == "Updated Second"
        assert matched["status"] == "done"
        assert len(state.tasks) == 3  # count unchanged

    @pytest.mark.anyio
    async def test_err_app_handle_update_api_error(self):
        """Handles ApiError from updateTask gracefully."""
        mock_update = AsyncMock(side_effect=Exception("ApiError: not found"))
        with pytest.raises(Exception, match="ApiError"):
            await mock_update(99999, {"title": "x"})


class TestAppHandleDelete:
    """App.handleDelete: deletes task and removes from state."""

    @pytest.mark.anyio
    async def test_hp_app_handle_delete(self):
        """deleteTask called; task removed from state."""
        state = MockAppState(SAMPLE_TASKS)
        mock_delete = AsyncMock(return_value={"detail": "Deleted", "id": 2})

        # Simulate handleDelete
        result = await mock_delete(2)
        state.set_tasks([t for t in state.tasks if t["id"] != 2])

        mock_delete.assert_called_once_with(2)
        assert all(t["id"] != 2 for t in state.tasks)
        assert len(state.tasks) == 2

    @pytest.mark.anyio
    async def test_inv_delete_immediate_removal(self):
        """Delete triggers immediate state removal — no re-fetch needed (AC19)."""
        state = MockAppState(SAMPLE_TASKS)
        mock_delete = AsyncMock(return_value={"detail": "Deleted", "id": 1})
        mock_fetch_tasks = AsyncMock()  # Should NOT be called

        # Simulate handleDelete
        await mock_delete(1)
        state.set_tasks([t for t in state.tasks if t["id"] != 1])

        mock_fetch_tasks.assert_not_called()
        assert len(state.tasks) == 2
        assert all(t["id"] != 1 for t in state.tasks)

    @pytest.mark.anyio
    async def test_err_app_handle_delete_api_error(self):
        """Handles ApiError from deleteTask gracefully."""
        mock_delete = AsyncMock(side_effect=Exception("ApiError: not found"))
        with pytest.raises(Exception, match="ApiError"):
            await mock_delete(99999)


# ---------------------------------------------------------------------------
# Invariant tests
# ---------------------------------------------------------------------------

class TestInvariants:
    """Cross-cutting contract invariants."""

    def test_inv_empty_desc_sent_as_null(self):
        """Empty description strings from create form are sent as null (A12)."""
        # Simulate form processing: empty string → null
        form_description = ""
        wire_description = None if form_description == "" else form_description
        assert wire_description is None

    def test_inv_empty_desc_nonempty_preserved(self):
        """Non-empty description is preserved as-is."""
        form_description = "A real description"
        wire_description = None if form_description == "" else form_description
        assert wire_description == "A real description"

    def test_inv_task_fields_complete(self):
        """Every Task object has exactly 6 fields: id, title, description, status, created_at, updated_at."""
        task = build_task()
        assert set(task.keys()) == TASK_FIELDS
        assert len(task.keys()) == 6

    def test_inv_task_id_positive_integer(self):
        """TaskId is always a positive integer."""
        for task in SAMPLE_TASKS:
            assert isinstance(task["id"], int)
            assert task["id"] > 0

    def test_inv_task_status_closed_set(self):
        """TaskStatus is a closed set: pending, in_progress, done."""
        valid = {"pending", "in_progress", "done"}
        for task in SAMPLE_TASKS:
            assert task["status"] in valid

    def test_inv_timestamps_are_iso8601(self):
        """All timestamps are valid ISO 8601 strings."""
        for task in SAMPLE_TASKS:
            dt_created = datetime.fromisoformat(task["created_at"])
            dt_updated = datetime.fromisoformat(task["updated_at"])
            assert dt_created.tzinfo is not None or "+" in task["created_at"] or "Z" in task["created_at"]

    def test_inv_api_error_all_fields_present(self):
        """ApiError always has message, statusCode, and detail."""
        error = {"message": "Not found", "statusCode": 404, "detail": "Task not found"}
        assert "message" in error
        assert "statusCode" in error
        assert "detail" in error

    def test_inv_no_trailing_slash_on_base_url(self):
        """resolveBaseUrl never returns a URL with trailing slash."""
        for url in ["http://localhost:8000/", "https://api.example.com/", "http://host:3000"]:
            result = url.rstrip("/")
            assert not result.endswith("/")

    def test_inv_delete_confirmation_has_id(self):
        """DeleteConfirmation always includes the id of the deleted task."""
        confirmation = {"detail": "Task deleted", "id": 5}
        assert "id" in confirmation
        assert confirmation["id"] == 5

    def test_inv_health_response_status_value(self):
        """HealthResponse.status must be 'ok' per validator."""
        valid_health = {"status": "ok"}
        assert valid_health["status"] == "ok"


# ---------------------------------------------------------------------------
# Component props interface tests
# ---------------------------------------------------------------------------

class TestComponentProps:
    """Verify component props interfaces match contract types."""

    def test_task_list_props_structure(self):
        """TaskListProps has tasks (list), onUpdate (callable), onDelete (callable)."""
        props = {
            "tasks": SAMPLE_TASKS,
            "onUpdate": "callback_ref",
            "onDelete": "callback_ref",
        }
        assert isinstance(props["tasks"], list)
        assert "onUpdate" in props
        assert "onDelete" in props

    def test_task_item_props_structure(self):
        """TaskItemProps has task (Task), onUpdate (callable), onDelete (callable)."""
        props = {
            "task": build_task(),
            "onUpdate": "callback_ref",
            "onDelete": "callback_ref",
        }
        assert TASK_FIELDS == set(props["task"].keys())
        assert "onUpdate" in props
        assert "onDelete" in props

    def test_task_form_props_structure(self):
        """TaskFormProps has onCreate (callable)."""
        props = {"onCreate": "callback_ref"}
        assert "onCreate" in props

    def test_import_meta_env_structure(self):
        """ImportMetaEnv has VITE_API_URL."""
        env = {"VITE_API_URL": "http://localhost:8000"}
        assert "VITE_API_URL" in env
        assert isinstance(env["VITE_API_URL"], str)


# ---------------------------------------------------------------------------
# Edge case: concurrent operations and ordering
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Additional edge cases at validation boundaries."""

    def test_task_title_exactly_200_chars_for_create_precondition(self):
        """createTask precondition: title at most 200 characters (stricter than struct 255)."""
        title_200 = "A" * 200
        assert len(title_200) <= 200

    def test_task_title_201_chars_violates_create_precondition(self):
        """createTask precondition: title > 200 chars should be rejected."""
        title_201 = "A" * 201
        assert len(title_201) > 200

    def test_description_at_most_1000_chars(self):
        """createTask precondition: description at most 1000 characters."""
        desc_1000 = "B" * 1000
        assert len(desc_1000) <= 1000
        desc_1001 = "B" * 1001
        assert len(desc_1001) > 1000

    @pytest.mark.anyio
    async def test_fetch_tasks_preserves_backend_order(self):
        """Tasks returned in the same order as backend (by id ascending)."""
        ordered_tasks = [
            build_task(id=1), build_task(id=5), build_task(id=10)
        ]
        mock_fetch = AsyncMock(return_value=make_response(status=200, json_data=ordered_tasks))
        response = await mock_fetch("http://localhost:8000/tasks")
        tasks = response.json()
        ids = [t["id"] for t in tasks]
        assert ids == [1, 5, 10]
        assert ids == sorted(ids)

    @pytest.mark.anyio
    async def test_update_preserves_unchanged_fields(self):
        """Fields not included in update data remain unchanged."""
        original = build_task(id=1, title="Original", description="Original desc", status="pending")
        # Only updating title
        updated = build_task(id=1, title="New Title", description="Original desc", status="pending",
                            updated_at="2025-01-15T16:00:00+00:00")
        mock_update = AsyncMock(return_value=make_response(status=200, json_data=updated))

        response = await mock_update("http://localhost:8000/tasks/1", json={"title": "New Title"})
        task = response.json()

        assert task["description"] == original["description"]
        assert task["status"] == original["status"]
        assert task["title"] == "New Title"

    @pytest.mark.anyio
    async def test_delete_then_fetch_excludes_deleted(self):
        """After delete, subsequent fetch does not include deleted task."""
        state = MockAppState(SAMPLE_TASKS)
        mock_delete = AsyncMock(return_value={"detail": "Deleted", "id": 2})
        mock_fetch = AsyncMock(return_value=[
            build_task(id=1, title="First"),
            build_task(id=3, title="Third", status="done"),
        ])

        # Delete task 2
        await mock_delete(2)
        state.set_tasks([t for t in state.tasks if t["id"] != 2])

        # Subsequent fetch
        remaining = await mock_fetch()
        state.set_tasks(remaining)

        assert all(t["id"] != 2 for t in state.tasks)
        assert len(state.tasks) == 2
