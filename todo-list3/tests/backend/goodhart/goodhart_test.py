"""
Hidden adversarial acceptance tests for FastAPI Backend API.
These tests catch implementations that pass visible tests through shortcuts
rather than genuinely satisfying the contract.
"""
import os
import re
import time
import uuid
import pytest
import requests

# Base URL for the running API server
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

# Skip all tests if DATABASE_URL is absent (contract invariant)
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set; skipping contract tests"
)


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


def _create_task(title="Test Task", description=None, status=None):
    """Helper to create a task and return the response."""
    body = {"title": title}
    if description is not None:
        body["description"] = description
    if status is not None:
        body["status"] = status
    return requests.post(_url("/tasks"), json=body)


def _cleanup_task(task_id):
    """Best-effort cleanup of a task by ID."""
    try:
        requests.delete(_url(f"/tasks/{task_id}"))
    except Exception:
        pass


ISO_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"


class TestGoodhartCreateTask:
    """Adversarial tests for POST /tasks."""

    def test_goodhart_create_task_status_in_progress(self):
        """Creating a task with status 'in_progress' should persist that status in the response,
        verifying the API doesn't hardcode 'pending' or only handle 'done'."""
        resp = _create_task(title="In Progress Task", status="in_progress")
        try:
            assert resp.status_code == 201
            assert resp.json()["status"] == "in_progress"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_status_done(self):
        """Creating a task with status 'done' should persist that status,
        verifying explicit status is respected for all enum values."""
        resp = _create_task(title="Done Task", status="done")
        try:
            assert resp.status_code == 201
            assert resp.json()["status"] == "done"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_unique_ids(self):
        """Each created task must receive a distinct server-generated ID,
        verifying IDs are not hardcoded or reused."""
        resp1 = _create_task(title="Unique ID Test 1")
        resp2 = _create_task(title="Unique ID Test 2")
        try:
            assert resp1.status_code == 201
            assert resp2.status_code == 201
            assert resp1.json()["id"] != resp2.json()["id"]
        finally:
            _cleanup_task(resp1.json().get("id"))
            _cleanup_task(resp2.json().get("id"))

    def test_goodhart_create_title_with_inner_whitespace_preserved(self):
        """Title stripping should only remove leading/trailing whitespace;
        internal whitespace and structure must be preserved."""
        resp = _create_task(title="  hello   world  ")
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == "hello   world"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_description_with_content_preserved(self):
        """A non-empty, non-whitespace description must be stored and returned as-is,
        not normalized to None."""
        desc = "Some detailed description with content"
        resp = _create_task(title="Desc Test", description=desc)
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] == desc
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_description_null_explicit(self):
        """Explicitly passing null for description should result in None in response."""
        body = {"title": "Null Desc Test", "description": None}
        resp = requests.post(_url("/tasks"), json=body)
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] is None
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_missing_title_field(self):
        """Omitting the title field entirely from the request body should return 422."""
        resp = requests.post(_url("/tasks"), json={"description": "no title here"})
        assert resp.status_code == 422

    def test_goodhart_create_task_title_tab_whitespace(self):
        """A title consisting only of tab characters should be rejected as blank after stripping."""
        resp = _create_task(title="\t\t\t")
        assert resp.status_code == 422

    def test_goodhart_create_task_title_newline_whitespace(self):
        """A title consisting only of newline characters should be rejected as blank after stripping."""
        resp = _create_task(title="\n\n")
        assert resp.status_code == 422

    def test_goodhart_create_response_has_all_fields(self):
        """The create response must contain all six TaskResponse fields."""
        resp = _create_task(title="Schema Check Task")
        try:
            assert resp.status_code == 201
            body = resp.json()
            for field in ["id", "title", "description", "status", "created_at", "updated_at"]:
                assert field in body, f"Missing field: {field}"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_199_chars(self):
        """A title at 199 characters must be accepted, verifying boundary logic is not off-by-one."""
        title = "a" * 199
        resp = _create_task(title=title)
        try:
            assert resp.status_code == 201
            assert len(resp.json()["title"]) == 199
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_with_unicode(self):
        """Titles containing unicode characters must be accepted and preserved."""
        title = "任务 タスク 📝 tâche"
        resp = _create_task(title=title)
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == title
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_case_sensitive_status(self):
        """Status values must be case-sensitive; 'Pending' should be rejected."""
        resp = _create_task(title="Case Test", status="Pending")
        assert resp.status_code == 422

    def test_goodhart_create_task_case_sensitive_status_upper(self):
        """Status values must be case-sensitive; 'DONE' should be rejected."""
        resp = _create_task(title="Case Test Upper", status="DONE")
        assert resp.status_code == 422

    def test_goodhart_create_default_status_is_pending(self):
        """When status is omitted, it must default to 'pending'."""
        resp = _create_task(title="Default Status Test")
        try:
            assert resp.status_code == 201
            assert resp.json()["status"] == "pending"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_empty_body_error(self):
        """Sending an empty JSON object should return 422 since title is required."""
        resp = requests.post(_url("/tasks"), json={})
        assert resp.status_code == 422

    def test_goodhart_create_description_tab_normalized(self):
        """Description containing only tab characters should be normalized to None."""
        resp = _create_task(title="Tab Desc Test", description="\t\t")
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] is None
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_id_returned_matches_get(self):
        """The id returned by POST must be retrievable via GET, verifying the ID is genuine."""
        create_resp = _create_task(title="ID Match Test")
        try:
            assert create_resp.status_code == 201
            task_id = create_resp.json()["id"]
            get_resp = requests.get(_url(f"/tasks/{task_id}"))
            assert get_resp.status_code == 200
            assert get_resp.json()["id"] == task_id
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_create_title_max_boundary_with_leading_whitespace(self):
        """A title that is 200 chars after stripping but has surrounding whitespace should be accepted."""
        raw_title = "  " + "a" * 200 + "  "
        resp = _create_task(title=raw_title)
        try:
            assert resp.status_code == 201
            assert len(resp.json()["title"]) == 200
        finally:
            _cleanup_task(resp.json().get("id"))


class TestGoodhartGetTask:
    """Adversarial tests for GET /tasks/{id}."""

    def test_goodhart_get_task_returns_correct_data(self):
        """GET /tasks/{id} must return the exact data persisted during creation."""
        create_resp = _create_task(
            title="Verify Get Data",
            description="A specific description",
            status="in_progress"
        )
        try:
            assert create_resp.status_code == 201
            task_id = create_resp.json()["id"]
            get_resp = requests.get(_url(f"/tasks/{task_id}"))
            assert get_resp.status_code == 200
            body = get_resp.json()
            assert body["title"] == "Verify Get Data"
            assert body["description"] == "A specific description"
            assert body["status"] == "in_progress"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_get_task_response_has_all_fields(self):
        """The get-task response must contain all six TaskResponse schema fields."""
        create_resp = _create_task(title="Schema Fields Test")
        try:
            task_id = create_resp.json()["id"]
            get_resp = requests.get(_url(f"/tasks/{task_id}"))
            assert get_resp.status_code == 200
            body = get_resp.json()
            for field in ["id", "title", "description", "status", "created_at", "updated_at"]:
                assert field in body, f"Missing field: {field}"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_get_task_not_found_has_detail(self):
        """404 responses must include a 'detail' field in the JSON body."""
        fake_id = str(uuid.uuid4())
        resp = requests.get(_url(f"/tasks/{fake_id}"))
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_goodhart_timestamp_has_timezone_on_get(self):
        """Timestamps returned by GET must include timezone offset."""
        create_resp = _create_task(title="TZ Get Test")
        try:
            task_id = create_resp.json()["id"]
            get_resp = requests.get(_url(f"/tasks/{task_id}"))
            body = get_resp.json()
            assert re.match(ISO_REGEX, body["created_at"]), f"created_at not ISO: {body['created_at']}"
            assert re.match(ISO_REGEX, body["updated_at"]), f"updated_at not ISO: {body['updated_at']}"
        finally:
            _cleanup_task(create_resp.json().get("id"))


class TestGoodhartUpdateTask:
    """Adversarial tests for PUT /tasks/{id}."""

    def test_goodhart_update_description_only(self):
        """Updating only description should leave title and status unchanged (PATCH semantics)."""
        create_resp = _create_task(title="Orig Title", description="Orig Desc", status="pending")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"description": "New Description"}
            )
            assert update_resp.status_code == 200
            body = update_resp.json()
            assert body["title"] == "Orig Title"
            assert body["status"] == "pending"
            assert body["description"] == "New Description"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_description_whitespace_normalized(self):
        """Updating description to whitespace-only should normalize it to None."""
        create_resp = _create_task(title="Desc Norm Test", description="Has description")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"description": "   "}
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["description"] is None
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_multiple_fields(self):
        """Updating both title and status in a single request should apply both changes."""
        create_resp = _create_task(title="Multi Update", status="pending")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "New Multi Title", "status": "done"}
            )
            assert update_resp.status_code == 200
            body = update_resp.json()
            assert body["title"] == "New Multi Title"
            assert body["status"] == "done"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_title_stripping(self):
        """Title stripping must also apply during updates."""
        create_resp = _create_task(title="Before Strip")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "  updated title  "}
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["title"] == "updated title"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_status_pending_to_in_progress(self):
        """Status transition from pending to in_progress should be allowed."""
        create_resp = _create_task(title="Status Trans", status="pending")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"status": "in_progress"}
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["status"] == "in_progress"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_status_done_to_pending(self):
        """Backward status transition (done -> pending) should be permitted."""
        create_resp = _create_task(title="Backward Trans", status="done")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"status": "pending"}
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["status"] == "pending"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_case_sensitive_status(self):
        """Status validation on update must be case-sensitive; 'DONE' should be rejected."""
        create_resp = _create_task(title="Case Status Update")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"status": "DONE"}
            )
            assert update_resp.status_code == 422
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_whitespace_only_title_tab_newline(self):
        """Updating a task with tabs/newlines only as title should be rejected."""
        create_resp = _create_task(title="WS Title Update")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "\t\n  "}
            )
            assert update_resp.status_code == 422
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_preserves_description_when_not_sent(self):
        """When updating only title, existing description must be preserved (PATCH semantics)."""
        create_resp = _create_task(title="Preserve Desc", description="Keep this")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "New Title Only"}
            )
            assert update_resp.status_code == 200
            assert update_resp.json()["description"] == "Keep this"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_timestamp_has_timezone_on_update(self):
        """Timestamps returned by PUT must include timezone offset."""
        create_resp = _create_task(title="TZ Update Test")
        try:
            task_id = create_resp.json()["id"]
            update_resp = requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "TZ Updated"}
            )
            body = update_resp.json()
            assert re.match(ISO_REGEX, body["created_at"]), f"created_at not ISO: {body['created_at']}"
            assert re.match(ISO_REGEX, body["updated_at"]), f"updated_at not ISO: {body['updated_at']}"
        finally:
            _cleanup_task(create_resp.json().get("id"))


class TestGoodhartDeleteTask:
    """Adversarial tests for DELETE /tasks/{id}."""

    def test_goodhart_delete_confirmation_has_correct_id(self):
        """Delete confirmation response must contain the exact ID of the deleted task."""
        create_resp = _create_task(title="Delete ID Check")
        assert create_resp.status_code == 201
        task_id = create_resp.json()["id"]
        del_resp = requests.delete(_url(f"/tasks/{task_id}"))
        assert del_resp.status_code == 200
        body = del_resp.json()
        assert str(body["id"]) == str(task_id)
        assert len(body["detail"]) > 0

    def test_goodhart_delete_double_delete_404(self):
        """Deleting the same task twice should return 404 on the second attempt."""
        create_resp = _create_task(title="Double Delete")
        task_id = create_resp.json()["id"]
        first = requests.delete(_url(f"/tasks/{task_id}"))
        assert first.status_code == 200
        second = requests.delete(_url(f"/tasks/{task_id}"))
        assert second.status_code == 404

    def test_goodhart_delete_removes_from_list(self):
        """After deleting a task, it must no longer appear in the list endpoint response."""
        create_resp = _create_task(title="Delete List Check")
        task_id = create_resp.json()["id"]
        requests.delete(_url(f"/tasks/{task_id}"))
        list_resp = requests.get(_url("/tasks"))
        assert list_resp.status_code == 200
        ids_in_list = [t["id"] for t in list_resp.json()]
        assert task_id not in ids_in_list


class TestGoodhartListTasks:
    """Adversarial tests for GET /tasks."""

    def test_goodhart_list_tasks_includes_newly_created(self):
        """A task created via POST must appear in the subsequent GET /tasks listing."""
        create_resp = _create_task(title="List Include Check")
        try:
            task_id = create_resp.json()["id"]
            list_resp = requests.get(_url("/tasks"))
            assert list_resp.status_code == 200
            ids_in_list = [t["id"] for t in list_resp.json()]
            assert task_id in ids_in_list
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_list_tasks_reflects_updates(self):
        """After updating a task's title, the list endpoint must return the updated value."""
        create_resp = _create_task(title="Original List Title")
        try:
            task_id = create_resp.json()["id"]
            requests.put(
                _url(f"/tasks/{task_id}"),
                json={"title": "Updated List Title"}
            )
            list_resp = requests.get(_url("/tasks"))
            tasks = list_resp.json()
            matching = [t for t in tasks if t["id"] == task_id]
            assert len(matching) == 1
            assert matching[0]["title"] == "Updated List Title"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_list_ordering_three_tasks(self):
        """List ordering must be strictly created_at DESC across three tasks."""
        ids = []
        try:
            for i in range(3):
                resp = _create_task(title=f"Order Test {i}")
                assert resp.status_code == 201
                ids.append(resp.json()["id"])
                time.sleep(0.05)  # small delay to ensure distinct timestamps

            list_resp = requests.get(_url("/tasks"))
            assert list_resp.status_code == 200
            all_tasks = list_resp.json()
            # Filter to just our tasks
            our_tasks = [t for t in all_tasks if t["id"] in ids]
            assert len(our_tasks) == 3
            # Most recently created should appear first in the list
            our_task_ids = [t["id"] for t in our_tasks]
            assert our_task_ids[0] == ids[2], "Most recent task should be first"
            assert our_task_ids[2] == ids[0], "Oldest task should be last"
        finally:
            for tid in ids:
                _cleanup_task(tid)

    def test_goodhart_timestamp_has_timezone_on_list(self):
        """Timestamps in list endpoint responses must include timezone offset."""
        create_resp = _create_task(title="TZ List Test")
        try:
            list_resp = requests.get(_url("/tasks"))
            tasks = list_resp.json()
            assert len(tasks) > 0
            task = tasks[0]
            assert re.match(ISO_REGEX, task["created_at"]), f"created_at not ISO: {task['created_at']}"
            assert re.match(ISO_REGEX, task["updated_at"]), f"updated_at not ISO: {task['updated_at']}"
        finally:
            _cleanup_task(create_resp.json().get("id"))


class TestGoodhartNotFoundDetail:
    """Tests that 404 error responses conform to ErrorDetail schema."""

    def test_goodhart_update_not_found_has_detail(self):
        """404 from PUT must include 'detail' field."""
        fake_id = str(uuid.uuid4())
        resp = requests.put(_url(f"/tasks/{fake_id}"), json={"title": "Nope"})
        assert resp.status_code == 404
        assert "detail" in resp.json()

    def test_goodhart_delete_not_found_has_detail(self):
        """404 from DELETE must include 'detail' field."""
        fake_id = str(uuid.uuid4())
        resp = requests.delete(_url(f"/tasks/{fake_id}"))
        assert resp.status_code == 404
        assert "detail" in resp.json()
