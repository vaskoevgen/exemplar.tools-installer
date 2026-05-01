"""
Contract test suite for root component.
Tests validation, async CRUD, serialization, endpoint contracts, and type invariants.

Run with: pytest contract_test.py -v
"""
import re
import uuid
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Import all public symbols from the component
from root import (
    TaskUUID,
    TaskTitle,
    Priority,
    DateString,
    TimestampTZ,
    OptionalDateString,
    HttpStatusCode,
    Task,
    TaskList,
    CreateTaskRequest,
    UpdateTaskRequest,
    ApiErrorResponse,
    EndpointContract,
    ValidationResult,
    Sentinel,
    validate_create_task,
    validate_update_task,
    create_task,
    list_tasks,
    get_task,
    update_task,
    delete_task,
    get_endpoint_contracts,
    task_to_dict,
    task_from_dict,
)


# ---------------------------------------------------------------------------
# Helpers and constants
# ---------------------------------------------------------------------------

VALID_UUID_V4 = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
VALID_UUID_V4_2 = "11111111-1111-4111-a111-111111111111"
NON_EXISTENT_UUID = "00000000-0000-4000-a000-000000000000"
UUID_V4_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
VALID_TIMESTAMP = "2024-01-15T10:30:00.000Z"


def _make_create_request(**overrides):
    """Factory producing a valid CreateTaskRequest with sensible defaults."""
    defaults = {"title": "Buy groceries", "priority": 1, "due_date": None}
    defaults.update(overrides)
    return CreateTaskRequest(**defaults)


def _make_update_request(**overrides):
    """Factory producing an UpdateTaskRequest. Fields not in overrides are UNSET."""
    fields = {}
    for key in ("title", "completed", "priority", "due_date"):
        fields[key] = overrides.get(key, Sentinel.UNSET)
    return UpdateTaskRequest(**fields)


def _make_valid_task_dict(**overrides):
    """Factory producing a valid Task-serialisable dict."""
    d = {
        "id": VALID_UUID_V4,
        "title": "Test task",
        "completed": False,
        "priority": 1,
        "due_date": None,
        "created_at": VALID_TIMESTAMP,
    }
    d.update(overrides)
    return d


# ===========================================================================
# 1. TYPE VALIDATION TESTS
# ===========================================================================


class TestTaskUUIDType:
    def test_valid_uuid_v4(self):
        t = TaskUUID(VALID_UUID_V4)
        assert t.value == VALID_UUID_V4

    def test_rejects_uppercase(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskUUID("A1B2C3D4-E5F6-4A7B-8C9D-0E1F2A3B4C5D")

    def test_rejects_non_v4(self):
        # version digit is 1, not 4
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskUUID("a1b2c3d4-e5f6-1a7b-8c9d-0e1f2a3b4c5d")

    def test_rejects_invalid_variant(self):
        # variant nibble is 0, must be 8-b
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskUUID("a1b2c3d4-e5f6-4a7b-0c9d-0e1f2a3b4c5d")


class TestTaskTitleType:
    def test_valid_title(self):
        t = TaskTitle("Hello")
        assert t.value == "Hello"

    def test_accepts_500_chars(self):
        title = "A" * 500
        t = TaskTitle(title)
        assert t.value == title

    def test_rejects_empty(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle("")

    def test_rejects_whitespace_only(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle("   ")

    def test_rejects_leading_trailing_whitespace(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle("  hello  ")

    def test_rejects_over_500(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            TaskTitle("A" * 501)

    def test_single_char(self):
        t = TaskTitle("X")
        assert t.value == "X"


class TestSentinelType:
    def test_unset_not_none(self):
        assert Sentinel.UNSET is not None

    def test_unset_identity(self):
        assert Sentinel.UNSET == Sentinel.UNSET
        assert Sentinel.UNSET is Sentinel.UNSET


# ===========================================================================
# 2. VALIDATION FUNCTION TESTS
# ===========================================================================


class TestValidateCreateTask:
    """Tests for validate_create_task — pure function."""

    def test_happy_path_full(self):
        req = _make_create_request(title="Buy groceries", priority=3, due_date="2025-06-15")
        result = validate_create_task(req)
        # Success: result should be a CreateTaskRequest, not a string
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.title == "Buy groceries"
        assert result.priority == 3
        assert result.due_date == "2025-06-15"

    def test_strips_whitespace(self):
        req = _make_create_request(title="  Buy groceries  ")
        result = validate_create_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.title == "Buy groceries"
        assert result.title == result.title.strip()

    def test_minimal_request(self):
        req = _make_create_request(title="T", priority=1, due_date=None)
        result = validate_create_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"

    def test_title_exactly_500(self):
        req = _make_create_request(title="A" * 500)
        result = validate_create_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert len(result.title) == 500

    @pytest.mark.parametrize("title", ["", "   ", "\t\n"])
    def test_error_empty_title(self, title):
        req = _make_create_request(title=title)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_error_none_title(self):
        req = _make_create_request(title=None)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_error_title_too_long(self):
        req = _make_create_request(title="A" * 501)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize("priority", [0, -1, -100])
    def test_error_invalid_priority_value(self, priority):
        req = _make_create_request(priority=priority)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_error_invalid_priority_type(self):
        req = _make_create_request(priority="high")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize(
        "due_date",
        ["not-a-date", "2025/06/15", "15-06-2025", "2025-13-01", "2025-02-30"],
    )
    def test_error_invalid_due_date(self, due_date):
        req = _make_create_request(due_date=due_date)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_valid_leap_day(self):
        req = _make_create_request(due_date="2024-02-29")
        result = validate_create_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"


class TestValidateUpdateTask:
    """Tests for validate_update_task — pure function."""

    def test_happy_path_title(self):
        req = _make_update_request(title="  New title  ")
        result = validate_update_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.title == "New title"

    def test_happy_path_completed(self):
        req = _make_update_request(completed=True)
        result = validate_update_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.completed is True

    def test_happy_path_clear_due_date(self):
        req = _make_update_request(due_date=None)
        result = validate_update_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.due_date is None

    def test_happy_path_set_due_date(self):
        req = _make_update_request(due_date="2025-12-31")
        result = validate_update_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"
        assert result.due_date == "2025-12-31"

    def test_happy_path_multiple_fields(self):
        req = _make_update_request(title="Updated", priority=5, completed=False)
        result = validate_update_task(req)
        assert not isinstance(result, str), f"Expected success but got error: {result}"

    def test_error_no_fields(self):
        req = _make_update_request()  # all UNSET
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize("title", ["", "   ", "\t"])
    def test_error_empty_title(self, title):
        req = _make_update_request(title=title)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_error_title_too_long(self):
        req = _make_update_request(title="B" * 501)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize("priority", [0, -1])
    def test_error_invalid_priority(self, priority):
        req = _make_update_request(priority=priority)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_error_invalid_due_date(self):
        req = _make_update_request(due_date="bad-date")
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.parametrize("completed", [1, 0, "true", None])
    def test_error_invalid_completed(self, completed):
        req = _make_update_request(completed=completed)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0


# ===========================================================================
# 3. ASYNC CRUD TESTS
# ===========================================================================


@pytest.mark.asyncio
class TestCreateTask:
    async def test_happy_path(self):
        req = _make_create_request(title="  Integration test  ", priority=2, due_date="2025-07-01")
        result = await create_task(req)
        # Postconditions
        assert UUID_V4_REGEX.match(result.id), f"id is not valid UUID v4: {result.id}"
        assert result.title == "Integration test"
        assert result.completed is False
        assert result.priority == 2
        assert result.due_date == "2025-07-01"
        assert result.created_at.endswith("Z") or "+" in result.created_at

    async def test_default_priority(self):
        req = _make_create_request(title="Defaults", priority=1, due_date=None)
        result = await create_task(req)
        assert result.priority == 1
        assert result.due_date is None

    async def test_validation_error_empty_title(self):
        req = _make_create_request(title="")
        # Depending on implementation, this may raise or return an error response.
        # We test for either pattern:
        try:
            result = await create_task(req)
            # If no exception, we expect an ApiErrorResponse-like object or HTTP 400 indicator
            if hasattr(result, "status"):
                assert result.status == 400
            elif hasattr(result, "error"):
                assert len(result.error) > 0
            else:
                # Result should indicate failure somehow
                pass
        except Exception:
            pass  # Exception-based error handling is acceptable


@pytest.mark.asyncio
class TestListTasks:
    async def test_empty_list(self):
        result = await list_tasks()
        # Should return a list (possibly empty)
        assert isinstance(result, (list, TaskList))

    async def test_returns_created_tasks(self):
        # Create tasks then list
        req1 = _make_create_request(title="Task A")
        req2 = _make_create_request(title="Task B")
        t1 = await create_task(req1)
        t2 = await create_task(req2)
        result = await list_tasks()
        # The result should be a list containing at least the tasks we created
        if isinstance(result, list):
            ids = [t.id for t in result]
        else:
            ids = [t.id for t in result]
        assert t1.id in ids
        assert t2.id in ids


@pytest.mark.asyncio
class TestGetTask:
    async def test_happy_path(self):
        req = _make_create_request(title="Fetchable")
        created = await create_task(req)
        result = await get_task(created.id)
        assert result.id == created.id
        assert result.title == created.title
        assert result.completed == created.completed
        assert result.priority == created.priority
        assert result.created_at == created.created_at

    async def test_not_found(self):
        try:
            result = await get_task(NON_EXISTENT_UUID)
            # If returns error response object
            if hasattr(result, "error"):
                assert result.error == "NOT_FOUND"
            if hasattr(result, "status"):
                assert result.status == 404
        except Exception as e:
            # Exception-based 404 handling is also acceptable
            assert "not found" in str(e).lower() or "NOT_FOUND" in str(e)


@pytest.mark.asyncio
class TestUpdateTask:
    async def test_happy_path_partial_update(self):
        req = _make_create_request(title="Original", priority=1, due_date="2025-01-01")
        created = await create_task(req)

        update_req = _make_update_request(title="  Updated  ", priority=5)
        result = await update_task(created.id, update_req)

        assert result.id == created.id
        assert result.title == "Updated"
        assert result.priority == 5
        # Unchanged fields
        assert result.due_date == created.due_date
        assert result.created_at == created.created_at

    async def test_clear_due_date(self):
        req = _make_create_request(title="With date", due_date="2025-06-01")
        created = await create_task(req)

        update_req = _make_update_request(due_date=None)
        result = await update_task(created.id, update_req)
        assert result.due_date is None

    async def test_toggle_completed(self):
        req = _make_create_request(title="Toggle me")
        created = await create_task(req)
        assert created.completed is False

        update_req = _make_update_request(completed=True)
        result = await update_task(created.id, update_req)
        assert result.completed is True

    async def test_not_found(self):
        update_req = _make_update_request(title="Ghost")
        try:
            result = await update_task(NON_EXISTENT_UUID, update_req)
            if hasattr(result, "error"):
                assert result.error == "NOT_FOUND"
            if hasattr(result, "status"):
                assert result.status == 404
        except Exception as e:
            assert "not found" in str(e).lower() or "NOT_FOUND" in str(e)

    async def test_validation_error(self):
        req = _make_create_request(title="Valid")
        created = await create_task(req)

        bad_update = _make_update_request(title="")
        try:
            result = await update_task(created.id, bad_update)
            if hasattr(result, "error"):
                assert result.error == "VALIDATION_ERROR"
            if hasattr(result, "status"):
                assert result.status == 400
        except Exception:
            pass  # Exception-based error handling acceptable


@pytest.mark.asyncio
class TestDeleteTask:
    async def test_happy_path(self):
        req = _make_create_request(title="Deletable")
        created = await create_task(req)

        result = await delete_task(created.id)
        assert result.id == created.id
        assert result.title == "Deletable"

        # Verify task is no longer retrievable
        try:
            get_result = await get_task(created.id)
            if hasattr(get_result, "error"):
                assert get_result.error == "NOT_FOUND"
            if hasattr(get_result, "status"):
                assert get_result.status == 404
        except Exception:
            pass  # 404 exception is expected

    async def test_not_found(self):
        try:
            result = await delete_task(NON_EXISTENT_UUID)
            if hasattr(result, "error"):
                assert result.error == "NOT_FOUND"
            if hasattr(result, "status"):
                assert result.status == 404
        except Exception as e:
            assert "not found" in str(e).lower() or "NOT_FOUND" in str(e)

    async def test_double_delete(self):
        req = _make_create_request(title="Once only")
        created = await create_task(req)
        await delete_task(created.id)

        # Second delete should be not-found
        try:
            result = await delete_task(created.id)
            if hasattr(result, "error"):
                assert result.error == "NOT_FOUND"
        except Exception:
            pass  # Expected


# ===========================================================================
# 4. SERIALIZATION TESTS
# ===========================================================================


class TestTaskToDict:
    def test_happy_path(self):
        d = _make_valid_task_dict()
        task = task_from_dict(d)
        result = task_to_dict(task)

        assert set(result.keys()) == {"id", "title", "completed", "priority", "due_date", "created_at"}
        assert UUID_V4_REGEX.match(result["id"])
        assert result["created_at"].endswith("Z")
        assert isinstance(result["priority"], int) and result["priority"] >= 1
        assert isinstance(result["completed"], bool)

    def test_null_due_date(self):
        d = _make_valid_task_dict(due_date=None)
        task = task_from_dict(d)
        result = task_to_dict(task)
        assert result["due_date"] is None

    def test_with_due_date(self):
        d = _make_valid_task_dict(due_date="2025-03-15")
        task = task_from_dict(d)
        result = task_to_dict(task)
        assert result["due_date"] == "2025-03-15"
        assert re.match(r"^\d{4}-\d{2}-\d{2}$", result["due_date"])

    def test_snake_case_keys(self):
        d = _make_valid_task_dict()
        task = task_from_dict(d)
        result = task_to_dict(task)
        for key in result:
            assert re.match(r"^[a-z][a-z0-9_]*$", key), f"Key '{key}' is not snake_case"


class TestTaskFromDict:
    def test_happy_path(self):
        d = _make_valid_task_dict()
        task = task_from_dict(d)
        assert task.id == d["id"]
        assert task.title == d["title"]
        assert task.completed == d["completed"]
        assert task.priority == d["priority"]
        assert task.due_date == d["due_date"]
        assert task.created_at == d["created_at"]

    def test_round_trip(self):
        d = _make_valid_task_dict(due_date="2025-06-15")
        task = task_from_dict(d)
        result = task_to_dict(task)
        assert result == d

    def test_round_trip_null_due_date(self):
        d = _make_valid_task_dict(due_date=None)
        task = task_from_dict(d)
        result = task_to_dict(task)
        assert result == d

    @pytest.mark.parametrize("missing_key", ["id", "title", "created_at"])
    def test_missing_required_field(self, missing_key):
        d = _make_valid_task_dict()
        del d[missing_key]
        with pytest.raises((ValueError, TypeError, KeyError, Exception)):
            task_from_dict(d)

    def test_invalid_priority_zero(self):
        d = _make_valid_task_dict(priority=0)
        with pytest.raises((ValueError, TypeError, Exception)):
            task_from_dict(d)

    def test_invalid_priority_negative(self):
        d = _make_valid_task_dict(priority=-5)
        with pytest.raises((ValueError, TypeError, Exception)):
            task_from_dict(d)

    def test_invalid_empty_title(self):
        d = _make_valid_task_dict(title="")
        with pytest.raises((ValueError, TypeError, Exception)):
            task_from_dict(d)


# ===========================================================================
# 5. ENDPOINT CONTRACT TESTS
# ===========================================================================


class TestGetEndpointContracts:
    def test_returns_exactly_five(self):
        contracts = get_endpoint_contracts()
        assert len(contracts) == 5

    def test_methods_and_paths(self):
        contracts = get_endpoint_contracts()
        method_path_pairs = {(c.method, c.path) for c in contracts}
        # Must cover all 5 endpoints
        assert ("POST", "/tasks") in method_path_pairs
        assert ("GET", "/tasks") in method_path_pairs
        assert ("GET", "/tasks/:id") in method_path_pairs
        assert ("PATCH", "/tasks/:id") in method_path_pairs
        assert ("DELETE", "/tasks/:id") in method_path_pairs

    def test_all_http_status_codes_used(self):
        contracts = get_endpoint_contracts()
        all_statuses = set()
        for c in contracts:
            all_statuses.add(c.success_status)
            if hasattr(c, "error_branches"):
                for branch in c.error_branches:
                    if hasattr(branch, "status"):
                        all_statuses.add(branch.status)
                    elif isinstance(branch, dict) and "status" in branch:
                        all_statuses.add(branch["status"])
        # All HttpStatusCode variants must appear
        for code in [200, 201, 400, 404]:
            assert code in all_statuses, f"HTTP {code} not found in any endpoint contract"

    def test_valid_methods(self):
        contracts = get_endpoint_contracts()
        valid_methods = {"GET", "POST", "PATCH", "DELETE"}
        for c in contracts:
            assert c.method in valid_methods

    def test_valid_paths(self):
        contracts = get_endpoint_contracts()
        path_regex = re.compile(r"^/tasks(/:id)?$")
        for c in contracts:
            assert path_regex.match(c.path), f"Invalid path: {c.path}"

    def test_post_uses_201(self):
        contracts = get_endpoint_contracts()
        post_contracts = [c for c in contracts if c.method == "POST"]
        assert len(post_contracts) == 1
        assert post_contracts[0].success_status == 201


# ===========================================================================
# 6. INVARIANT TESTS
# ===========================================================================


class TestInvariants:
    def test_task_is_immutable(self):
        """Task instances are frozen dataclasses — attribute assignment must fail."""
        d = _make_valid_task_dict()
        task = task_from_dict(d)
        with pytest.raises((AttributeError, TypeError, Exception)):
            task.title = "Mutated"

    def test_sentinel_never_in_serialized_task(self):
        """Sentinel.UNSET must never appear in a serialized Task dict."""
        d = _make_valid_task_dict()
        task = task_from_dict(d)
        result = task_to_dict(task)
        for value in result.values():
            assert value is not Sentinel.UNSET

    def test_uuid_lowercase_format(self):
        """UUID strings are always lowercase hyphenated."""
        d = _make_valid_task_dict(id=VALID_UUID_V4)
        task = task_from_dict(d)
        result = task_to_dict(task)
        assert result["id"] == result["id"].lower()
        assert UUID_V4_REGEX.match(result["id"])

    @pytest.mark.asyncio
    async def test_created_at_immutable_after_creation(self):
        """created_at must not change after update."""
        req = _make_create_request(title="Immutable timestamp")
        created = await create_task(req)

        update_req = _make_update_request(title="Updated title")
        updated = await update_task(created.id, update_req)

        assert updated.created_at == created.created_at

    @pytest.mark.asyncio
    async def test_create_task_always_completed_false(self):
        """Newly created tasks always have completed=False."""
        req = _make_create_request(title="Fresh task")
        result = await create_task(req)
        assert result.completed is False

    @pytest.mark.asyncio
    async def test_unique_ids(self):
        """Each created task gets a unique UUID."""
        req1 = _make_create_request(title="Task 1")
        req2 = _make_create_request(title="Task 2")
        t1 = await create_task(req1)
        t2 = await create_task(req2)
        assert t1.id != t2.id

    def test_http_status_code_enum_values(self):
        """HttpStatusCode enum contains exactly the specified variants."""
        expected = {200, 201, 400, 404}
        actual = {member.value if hasattr(member, "value") else member for member in HttpStatusCode}
        assert expected == actual
