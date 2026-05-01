"""
Adversarial hidden acceptance tests for the Main component.
These tests catch implementations that hardcode returns or take shortcuts
based on visible test inputs.
"""
import re
import pytest
import uuid
from datetime import datetime

from src.root import (
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
    CreateTaskRequest,
    UpdateTaskRequest,
    Task,
    TaskTitle,
    TaskUUID,
    Sentinel,
)

UUID_V4_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
)
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

UNSET = Sentinel.UNSET


# ---- Helper to build requests ----

def _make_create_req(title="Test Task", priority=None, due_date=None):
    """Build a CreateTaskRequest; fields not passed use sensible defaults or are absent."""
    kwargs = {"title": title}
    if priority is not None:
        kwargs["priority"] = priority
    if due_date is not None:
        kwargs["due_date"] = due_date
    return CreateTaskRequest(**kwargs)


def _make_update_req(title=UNSET, completed=UNSET, priority=UNSET, due_date=UNSET):
    return UpdateTaskRequest(
        title=title,
        completed=completed,
        priority=priority,
        due_date=due_date,
    )


# =====================================================================
# validate_create_task tests
# =====================================================================

class TestGoodhartValidateCreateTask:

    def test_goodhart_whitespace_only_tabs_newlines(self):
        """Title consisting of only tabs/newlines must be rejected as empty after stripping."""
        req = CreateTaskRequest(title="\t\n\r", priority=1)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_title_501_boundary(self):
        """Title of exactly 501 chars after strip must be rejected."""
        req = CreateTaskRequest(title="b" * 501, priority=1)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_title_499_boundary(self):
        """Title of exactly 499 chars must be accepted."""
        req = CreateTaskRequest(title="c" * 499, priority=1)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert len(result.title) == 499

    def test_goodhart_stripped_title_length_500_with_padding(self):
        """Title that is 500 chars after stripping but more before must be accepted."""
        title = "  " + "d" * 500 + "  "
        req = CreateTaskRequest(title=title, priority=1)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert len(result.title) == 500
        assert result.title == "d" * 500

    def test_goodhart_stripped_title_exceeds_500_with_padding(self):
        """Title that is 501 chars after stripping (with whitespace padding) must be rejected."""
        title = "  " + "e" * 501 + "  "
        req = CreateTaskRequest(title=title, priority=1)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_priority_zero(self):
        """Priority of exactly 0 must be rejected."""
        req = CreateTaskRequest(title="Valid", priority=0)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_priority_negative(self):
        """Negative priority must be rejected."""
        req = CreateTaskRequest(title="Valid", priority=-5)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_priority_large(self):
        """Very large priority values must be accepted — no upper bound."""
        req = CreateTaskRequest(title="Valid", priority=999999)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert result.priority == 999999

    def test_goodhart_priority_float(self):
        """Float priority (e.g. 2.5) must be rejected — only integers allowed."""
        req = CreateTaskRequest(title="Valid", priority=2.5)
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_leap_year_valid(self):
        """Feb 29 on a leap year must be accepted."""
        req = CreateTaskRequest(title="Leap", priority=1, due_date="2024-02-29")
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert result.due_date == "2024-02-29"

    def test_goodhart_due_date_non_leap_year_feb29(self):
        """Feb 29 on a non-leap year must be rejected."""
        req = CreateTaskRequest(title="NoLeap", priority=1, due_date="2023-02-29")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_april_31(self):
        """April 31 must be rejected as an invalid calendar date."""
        req = CreateTaskRequest(title="April", priority=1, due_date="2025-04-31")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_with_time_component(self):
        """Date string with time component must be rejected — only YYYY-MM-DD."""
        req = CreateTaskRequest(title="TimeDate", priority=1, due_date="2025-01-15T10:30:00Z")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_single_digit_month_day(self):
        """Non-zero-padded date format (e.g., 2025-1-5) must be rejected."""
        req = CreateTaskRequest(title="Pad", priority=1, due_date="2025-1-5")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_month_13(self):
        """Month 13 must be rejected."""
        req = CreateTaskRequest(title="M13", priority=1, due_date="2025-13-01")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_month_00(self):
        """Month 00 must be rejected."""
        req = CreateTaskRequest(title="M00", priority=1, due_date="2025-00-15")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_numeric_title(self):
        """Purely numeric titles must be accepted."""
        req = CreateTaskRequest(title="12345", priority=1)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert result.title == "12345"

    def test_goodhart_single_char_title(self):
        """Single-character title must be accepted — minimum valid length."""
        req = CreateTaskRequest(title="X", priority=1)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert result.title == "X"

    def test_goodhart_explicit_none_due_date(self):
        """Explicit None for due_date must be accepted."""
        req = CreateTaskRequest(title="NullDate", priority=1, due_date=None)
        result = validate_create_task(req)
        assert not isinstance(result, str)
        assert result.due_date is None

    def test_goodhart_due_date_empty_string(self):
        """Empty string as due_date must be rejected."""
        req = CreateTaskRequest(title="Valid", priority=1, due_date="")
        result = validate_create_task(req)
        assert isinstance(result, str) and len(result) > 0


# =====================================================================
# validate_update_task tests
# =====================================================================

class TestGoodhartValidateUpdateTask:

    def test_goodhart_priority_zero(self):
        """Priority of 0 must be rejected in update validation."""
        req = _make_update_req(priority=0)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_completed_false(self):
        """completed=False must be accepted as a valid boolean value."""
        req = _make_update_req(completed=False)
        result = validate_update_task(req)
        assert not isinstance(result, str)
        assert result.completed is False

    def test_goodhart_completed_int_1(self):
        """Integer 1 must be rejected as completed — only bool allowed."""
        req = _make_update_req(completed=1)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_completed_string_true(self):
        """String 'true' must be rejected as completed — only bool allowed."""
        req = _make_update_req(completed="true")
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_multiple_fields(self):
        """All non-UNSET fields must be validated and returned together."""
        req = _make_update_req(
            title="  New Title  ",
            priority=5,
            completed=True,
            due_date="2025-06-15",
        )
        result = validate_update_task(req)
        assert not isinstance(result, str)
        assert result.title == "New Title"
        assert result.priority == 5
        assert result.completed is True
        assert result.due_date == "2025-06-15"

    def test_goodhart_title_whitespace_only(self):
        """Title that is only whitespace (tabs/newlines) must be rejected after stripping."""
        req = _make_update_req(title="\t  \n")
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0

    def test_goodhart_due_date_only(self):
        """Due date as the only non-UNSET field must be accepted."""
        req = _make_update_req(due_date="2025-12-31")
        result = validate_update_task(req)
        assert not isinstance(result, str)
        assert result.due_date == "2025-12-31"

    def test_goodhart_strips_title_whitespace(self):
        """update validation must strip whitespace from title."""
        req = _make_update_req(title="  Stripped  ")
        result = validate_update_task(req)
        assert not isinstance(result, str)
        assert result.title == "Stripped"

    def test_goodhart_priority_float(self):
        """Float priority must be rejected in update validation."""
        req = _make_update_req(priority=1.5)
        result = validate_update_task(req)
        assert isinstance(result, str) and len(result) > 0


# =====================================================================
# create_task tests
# =====================================================================

class TestGoodhartCreateTask:

    @pytest.mark.asyncio
    async def test_goodhart_unique_ids(self):
        """Each create_task call must generate a unique UUID — no hardcoding."""
        req1 = CreateTaskRequest(title="Same Title", priority=1)
        req2 = CreateTaskRequest(title="Same Title", priority=1)
        task1 = await create_task(req1)
        task2 = await create_task(req2)
        assert task1.id != task2.id
        assert UUID_V4_RE.match(task1.id)
        assert UUID_V4_RE.match(task2.id)

    @pytest.mark.asyncio
    async def test_goodhart_completed_always_false(self):
        """Newly created task must always have completed=False."""
        req = CreateTaskRequest(title="CompCheck", priority=3)
        task = await create_task(req)
        assert task.completed is False
        assert type(task.completed) is bool

    @pytest.mark.asyncio
    async def test_goodhart_default_priority(self):
        """When priority is not provided, it must default to 1."""
        req = CreateTaskRequest(title="Default Priority")
        task = await create_task(req)
        assert task.priority == 1

    @pytest.mark.asyncio
    async def test_goodhart_default_due_date_null(self):
        """When due_date is not provided, it must default to None."""
        req = CreateTaskRequest(title="No Due Date")
        task = await create_task(req)
        assert task.due_date is None

    @pytest.mark.asyncio
    async def test_goodhart_strips_title(self):
        """create_task must strip whitespace from the title."""
        req = CreateTaskRequest(title="  Whitespace Task  ", priority=1)
        task = await create_task(req)
        assert task.title == "Whitespace Task"

    @pytest.mark.asyncio
    async def test_goodhart_created_at_format(self):
        """created_at must be a valid ISO 8601 UTC timestamp ending in Z."""
        req = CreateTaskRequest(title="Timestamp Check", priority=1)
        task = await create_task(req)
        assert task.created_at.endswith("Z")
        # Should be parseable
        ts = task.created_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        assert dt is not None

    @pytest.mark.asyncio
    async def test_goodhart_with_high_priority_and_due_date(self):
        """create_task must correctly persist non-default priority and due_date."""
        req = CreateTaskRequest(title="Important", priority=10, due_date="2025-12-25")
        task = await create_task(req)
        assert task.priority == 10
        assert task.due_date == "2025-12-25"
        assert task.title == "Important"
        assert task.completed is False


# =====================================================================
# update_task tests
# =====================================================================

class TestGoodhartUpdateTask:

    @pytest.mark.asyncio
    async def test_goodhart_preserves_created_at(self):
        """update_task must never modify created_at."""
        created = await create_task(CreateTaskRequest(title="Original", priority=1))
        updated = await update_task(
            created.id,
            _make_update_req(title="Changed", priority=5),
        )
        assert updated.created_at == created.created_at

    @pytest.mark.asyncio
    async def test_goodhart_preserves_unset_fields(self):
        """Fields that are UNSET in the update request must retain their previous values."""
        created = await create_task(
            CreateTaskRequest(title="Original", priority=5, due_date="2025-01-01")
        )
        updated = await update_task(
            created.id,
            _make_update_req(completed=True),
        )
        assert updated.title == "Original"
        assert updated.priority == 5
        assert updated.due_date == "2025-01-01"
        assert updated.completed is True

    @pytest.mark.asyncio
    async def test_goodhart_priority_change(self):
        """update_task must correctly update priority when it is the only changed field."""
        created = await create_task(CreateTaskRequest(title="PriTest", priority=1))
        updated = await update_task(
            created.id,
            _make_update_req(priority=10),
        )
        assert updated.priority == 10
        assert updated.title == "PriTest"

    @pytest.mark.asyncio
    async def test_goodhart_title_change_only(self):
        """update_task must correctly change title when only title is provided."""
        created = await create_task(CreateTaskRequest(title="Before", priority=2))
        updated = await update_task(
            created.id,
            _make_update_req(title="After"),
        )
        assert updated.title == "After"
        assert updated.id == created.id
        assert updated.priority == 2


# =====================================================================
# delete_task tests
# =====================================================================

class TestGoodhartDeleteTask:

    @pytest.mark.asyncio
    async def test_goodhart_returns_full_snapshot(self):
        """delete_task must return the full task data, not a partial or empty object."""
        created = await create_task(
            CreateTaskRequest(title="DeleteMe", priority=3, due_date="2025-06-01")
        )
        deleted = await delete_task(created.id)
        assert deleted.id == created.id
        assert deleted.title == created.title
        assert deleted.priority == created.priority
        assert deleted.due_date == created.due_date
        assert deleted.completed == created.completed
        assert deleted.created_at == created.created_at

    @pytest.mark.asyncio
    async def test_goodhart_actually_removes_from_store(self):
        """After deletion, get_task with the same ID must return 404."""
        created = await create_task(CreateTaskRequest(title="Gone", priority=1))
        await delete_task(created.id)
        result = await get_task(created.id)
        # result should be an error response with NOT_FOUND
        assert hasattr(result, 'error') or hasattr(result, 'status')
        if hasattr(result, 'error'):
            assert result.error == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_goodhart_not_in_list_after_delete(self):
        """Deleted task must not appear in list_tasks results."""
        t1 = await create_task(CreateTaskRequest(title="Keep", priority=1))
        t2 = await create_task(CreateTaskRequest(title="Remove", priority=1))
        await delete_task(t2.id)
        tasks = await list_tasks()
        task_ids = [t.id for t in tasks]
        assert t2.id not in task_ids
        assert t1.id in task_ids

    @pytest.mark.asyncio
    async def test_goodhart_double_delete_404(self):
        """Deleting an already-deleted task must return 404."""
        created = await create_task(CreateTaskRequest(title="DoubleDel", priority=1))
        await delete_task(created.id)
        result = await delete_task(created.id)
        assert hasattr(result, 'error')
        assert result.error == "NOT_FOUND"


# =====================================================================
# get_task tests
# =====================================================================

class TestGoodhartGetTask:

    @pytest.mark.asyncio
    async def test_goodhart_reflects_updates(self):
        """get_task must return the current state after updates, not the original."""
        created = await create_task(CreateTaskRequest(title="V1", priority=1))
        await update_task(created.id, _make_update_req(title="V2"))
        fetched = await get_task(created.id)
        assert fetched.title == "V2"

    @pytest.mark.asyncio
    async def test_goodhart_404_error_field_value(self):
        """get_task 404 must have error exactly equal to 'NOT_FOUND'."""
        fake_id = "00000000-0000-4000-a000-000000000000"
        result = await get_task(fake_id)
        assert hasattr(result, 'error')
        assert result.error == "NOT_FOUND"


# =====================================================================
# list_tasks tests
# =====================================================================

class TestGoodhartListTasks:

    @pytest.mark.asyncio
    async def test_goodhart_returns_all_three(self):
        """list_tasks must return ALL created tasks, not just one or two."""
        t1 = await create_task(CreateTaskRequest(title="List1", priority=1))
        t2 = await create_task(CreateTaskRequest(title="List2", priority=2))
        t3 = await create_task(CreateTaskRequest(title="List3", priority=3))
        tasks = await list_tasks()
        task_ids = {t.id for t in tasks}
        assert t1.id in task_ids
        assert t2.id in task_ids
        assert t3.id in task_ids


# =====================================================================
# task_to_dict tests
# =====================================================================

class TestGoodhartTaskToDict:

    def test_goodhart_exactly_six_keys(self):
        """task_to_dict must return exactly 6 keys, no more, no less."""
        task = Task(
            id="a1b2c3d4-e5f6-4789-ab01-234567890abc",
            title="DictTest",
            completed=False,
            priority=2,
            due_date="2025-03-15",
            created_at="2025-01-15T10:30:00.000Z",
        )
        d = task_to_dict(task)
        assert len(d) == 6
        assert set(d.keys()) == {"id", "title", "completed", "priority", "due_date", "created_at"}

    def test_goodhart_completed_is_bool_type(self):
        """dict['completed'] must be of type bool, not int."""
        task = Task(
            id="a1b2c3d4-e5f6-4789-ab01-234567890abc",
            title="BoolCheck",
            completed=False,
            priority=1,
            due_date=None,
            created_at="2025-01-15T10:30:00.000Z",
        )
        d = task_to_dict(task)
        assert type(d["completed"]) is bool

    def test_goodhart_priority_is_int_type(self):
        """dict['priority'] must be of type int, not float."""
        task = Task(
            id="a1b2c3d4-e5f6-4789-ab01-234567890abc",
            title="IntCheck",
            completed=False,
            priority=3,
            due_date=None,
            created_at="2025-01-15T10:30:00.000Z",
        )
        d = task_to_dict(task)
        assert type(d["priority"]) is int
        assert d["priority"] == 3

    def test_goodhart_id_lowercase(self):
        """dict['id'] must be lowercase and match UUID v4 format."""
        task = Task(
            id="a1b2c3d4-e5f6-4789-ab01-234567890abc",
            title="LowerID",
            completed=False,
            priority=1,
            due_date=None,
            created_at="2025-01-15T10:30:00.000Z",
        )
        d = task_to_dict(task)
        assert d["id"] == d["id"].lower()
        assert UUID_V4_RE.match(d["id"])

    def test_goodhart_with_due_date(self):
        """Non-null due_date must be serialized as a YYYY-MM-DD string."""
        task = Task(
            id="a1b2c3d4-e5f6-4789-ab01-234567890abc",
            title="DueDate",
            completed=False,
            priority=1,
            due_date="2025-06-15",
            created_at="2025-01-15T10:30:00.000Z",
        )
        d = task_to_dict(task)
        assert d["due_date"] == "2025-06-15"
        assert type(d["due_date"]) is str


# =====================================================================
# task_from_dict tests
# =====================================================================

class TestGoodhartTaskFromDict:

    def test_goodhart_missing_created_at(self):
        """task_from_dict must raise an error when 'created_at' is missing."""
        data = {
            "id": "a1b2c3d4-e5f6-4789-ab01-234567890abc",
            "title": "NoCreatedAt",
            "completed": False,
            "priority": 1,
            "due_date": None,
        }
        with pytest.raises(Exception):
            task_from_dict(data)

    def test_goodhart_invalid_uuid_in_id(self):
        """task_from_dict must reject an invalid UUID in the id field."""
        data = {
            "id": "not-a-uuid",
            "title": "BadUUID",
            "completed": False,
            "priority": 1,
            "due_date": None,
            "created_at": "2025-01-15T10:30:00.000Z",
        }
        with pytest.raises(Exception):
            task_from_dict(data)

    def test_goodhart_roundtrip_with_due_date(self):
        """Round-trip through task_to_dict(task_from_dict(data)) must be identity for well-formed data with due_date."""
        data = {
            "id": "b2c3d4e5-f6a7-4890-ab12-345678901bcd",
            "title": "RoundTrip",
            "completed": True,
            "priority": 7,
            "due_date": "2025-03-15",
            "created_at": "2025-02-01T08:00:00.000Z",
        }
        assert task_to_dict(task_from_dict(data)) == data

    def test_goodhart_roundtrip_null_due_date(self):
        """Round-trip must preserve None due_date."""
        data = {
            "id": "c3d4e5f6-a7b8-4901-8c23-456789012cde",
            "title": "NullDueRT",
            "completed": False,
            "priority": 1,
            "due_date": None,
            "created_at": "2025-01-01T00:00:00.000Z",
        }
        assert task_to_dict(task_from_dict(data)) == data


# =====================================================================
# get_endpoint_contracts tests
# =====================================================================

class TestGoodhartEndpointContracts:

    def test_goodhart_paths_covered(self):
        """Contracts must include both /tasks and /tasks/:id path patterns."""
        contracts = get_endpoint_contracts()
        paths = {c.path for c in contracts}
        assert "/tasks" in paths
        assert "/tasks/:id" in paths

    def test_goodhart_error_branches_map_to_api_error(self):
        """Every error branch in every contract must map to ApiErrorResponse."""
        contracts = get_endpoint_contracts()
        for c in contracts:
            for branch in c.error_branches:
                # Branch should reference ApiErrorResponse somehow
                if hasattr(branch, 'response_type'):
                    assert "ApiErrorResponse" in str(branch.response_type)
                elif isinstance(branch, dict) and 'response_type' in branch:
                    assert "ApiErrorResponse" in str(branch['response_type'])

    def test_goodhart_post_uses_201(self):
        """POST /tasks contract must have success_status=201."""
        contracts = get_endpoint_contracts()
        post_contracts = [c for c in contracts if c.method == "POST"]
        assert len(post_contracts) == 1
        assert post_contracts[0].success_status == 201

    def test_goodhart_non_post_use_200(self):
        """All non-POST endpoint contracts must have success_status=200."""
        contracts = get_endpoint_contracts()
        non_post = [c for c in contracts if c.method != "POST"]
        assert len(non_post) == 4
        for c in non_post:
            assert c.success_status == 200, f"{c.method} {c.path} has success_status={c.success_status}"


# =====================================================================
# TaskUUID type tests
# =====================================================================

class TestGoodhartTaskUUID:

    def test_goodhart_rejects_v1_uuid(self):
        """TaskUUID must reject a version 1 UUID."""
        with pytest.raises(Exception):
            TaskUUID("a1b2c3d4-e5f6-1789-ab01-234567890abc")

    def test_goodhart_rejects_variant_c(self):
        """TaskUUID must reject a UUID with variant digit 'c' (not in [89ab])."""
        with pytest.raises(Exception):
            TaskUUID("a1b2c3d4-e5f6-4789-c012-234567890abc")


# =====================================================================
# TaskTitle type tests
# =====================================================================

class TestGoodhartTaskTitle:

    def test_goodhart_accepts_different_500_chars(self):
        """TaskTitle must accept a 500-character string using different characters than visible tests."""
        title = "Z" * 500
        tt = TaskTitle(title)
        assert len(tt.value) == 500
