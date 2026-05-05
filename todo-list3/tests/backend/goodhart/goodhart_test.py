"""
Goodhart adversarial hidden tests for FastAPI Backend API.

These tests detect implementations that pass visible tests through shortcuts
(hardcoded returns, missing validation, etc.) rather than truly satisfying the contract.
"""
import os
import re
import json
import time
import uuid
import pytest
from datetime import datetime

# Skip all tests if DATABASE_URL is not set
pytestmark = pytest.mark.skipif(
    not os.environ.get("DATABASE_URL"),
    reason="DATABASE_URL not set — skipping contract tests"
)

# Attempt imports — adjust based on actual project structure
try:
    from fastapi.testclient import TestClient
    from src.backend.main import app
    client = TestClient(app)
except ImportError:
    try:
        from fastapi.testclient import TestClient
        from main import app
        client = TestClient(app)
    except ImportError:
        client = None

ISO_TZ_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"


def _create_task(title="Test Task", description=None, status=None):
    """Helper to create a task and return the response."""
    body = {"title": title}
    if description is not None:
        body["description"] = description
    if status is not None:
        body["status"] = status
    return client.post("/tasks", json=body)


def _cleanup_task(task_id):
    """Best-effort cleanup of a task."""
    try:
        client.delete(f"/tasks/{task_id}")
    except Exception:
        pass


class TestGoodhartCreateTask:

    def test_goodhart_create_task_unique_ids(self):
        """Each created task must receive a distinct server-generated id; ids cannot be hardcoded or reused."""
        resp1 = _create_task(title="Unique ID Test 1")
        resp2 = _create_task(title="Unique ID Test 2")
        try:
            assert resp1.status_code == 201
            assert resp2.status_code == 201
            id1 = resp1.json()["id"]
            id2 = resp2.json()["id"]
            assert id1 != id2, "Two created tasks must have different ids"
            # Both must be valid UUIDs
            uuid.UUID(str(id1))
            uuid.UUID(str(id2))
        finally:
            _cleanup_task(resp1.json().get("id"))
            _cleanup_task(resp2.json().get("id"))

    def test_goodhart_create_task_in_progress_status(self):
        """Creating a task with status 'in_progress' must persist that exact status, not default to 'pending'."""
        resp = _create_task(title="Progress task", status="in_progress")
        try:
            assert resp.status_code == 201
            assert resp.json()["status"] == "in_progress"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_done_status(self):
        """Creating a task with status 'done' must persist that exact status."""
        resp = _create_task(title="Done task", status="done")
        try:
            assert resp.status_code == 201
            assert resp.json()["status"] == "done"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_description_preserved(self):
        """A non-empty, non-whitespace description must be stored and returned verbatim, not normalized to None."""
        desc = "This is a meaningful description with details"
        resp = _create_task(title="Desc test", description=desc)
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] == desc
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_description_with_inner_whitespace(self):
        """Description with leading/trailing whitespace but non-empty content should not be normalized to None."""
        resp = _create_task(title="Inner ws", description="  has content  ")
        try:
            assert resp.status_code == 201
            data = resp.json()
            assert data["description"] is not None
            assert "has content" in data["description"]
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_tab_only_description_normalized(self):
        """Description consisting only of tab characters must be normalized to None."""
        resp = _create_task(title="Tab desc", description="\t\t\t")
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] is None
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_newline_only_description_normalized(self):
        """Description consisting only of newline characters must be normalized to None."""
        resp = _create_task(title="Newline desc", description="\n\n\n")
        try:
            assert resp.status_code == 201
            assert resp.json()["description"] is None
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_single_char(self):
        """A single non-whitespace character title should be accepted as valid minimum-length title."""
        resp = _create_task(title="X")
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == "X"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_199_chars(self):
        """A title of 199 characters (adjacent to 200-char TaskTitle boundary) must be accepted."""
        title = "a" * 199
        resp = _create_task(title=title)
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == title
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_254_chars(self):
        """A title of 254 characters (one below API max of 255) must be accepted."""
        title = "b" * 254
        resp = _create_task(title=title)
        try:
            assert resp.status_code == 201
            assert len(resp.json()["title"]) == 254
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_title_256_chars_rejected(self):
        """A title of 256 characters (one above API max of 255) must be rejected with 422."""
        title = "c" * 256
        resp = _create_task(title=title)
        assert resp.status_code == 422

    def test_goodhart_create_task_missing_title_rejected(self):
        """Omitting the title field entirely must be rejected — title is required."""
        resp = client.post("/tasks", json={"description": "no title provided"})
        assert resp.status_code == 422

    def test_goodhart_create_task_empty_body_rejected(self):
        """An empty JSON body {} must be rejected since title is required."""
        resp = client.post("/tasks", json={})
        assert resp.status_code == 422

    def test_goodhart_create_task_status_case_sensitive_pending(self):
        """Status 'Pending' (capitalized) must be rejected — values are case-sensitive."""
        resp = _create_task(title="Case test", status="Pending")
        assert resp.status_code == 422

    def test_goodhart_create_task_status_case_sensitive_upper(self):
        """Status 'DONE' (all caps) must be rejected — values are case-sensitive."""
        resp = _create_task(title="Case test 2", status="DONE")
        assert resp.status_code == 422

    def test_goodhart_create_task_status_case_sensitive_in_progress(self):
        """Status 'In_Progress' (mixed case) must be rejected — values are case-sensitive."""
        resp = _create_task(title="Case test 3", status="In_Progress")
        assert resp.status_code == 422

    def test_goodhart_create_task_response_has_all_fields(self):
        """Create response must include all six TaskResponse fields and no extras."""
        resp = _create_task(title="Field completeness check")
        try:
            assert resp.status_code == 201
            data = resp.json()
            required_keys = {"id", "title", "description", "status", "created_at", "updated_at"}
            assert required_keys.issubset(set(data.keys())), f"Missing keys: {required_keys - set(data.keys())}"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_no_extra_fields(self):
        """Create response must not contain unexpected extra fields beyond the TaskResponse schema."""
        resp = _create_task(title="Extra fields check")
        try:
            assert resp.status_code == 201
            data = resp.json()
            allowed_keys = {"id", "title", "description", "status", "created_at", "updated_at"}
            extra = set(data.keys()) - allowed_keys
            assert not extra, f"Unexpected fields in response: {extra}"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_created_at_equals_updated_at(self):
        """On creation, created_at and updated_at should be equal or within 1 second of each other."""
        resp = _create_task(title="Timestamp equality check")
        try:
            assert resp.status_code == 201
            data = resp.json()
            # Parse both timestamps - they should be very close
            created = data["created_at"]
            updated = data["updated_at"]
            # At minimum they should both exist and be valid
            assert re.match(ISO_TZ_REGEX, created)
            assert re.match(ISO_TZ_REGEX, updated)
            # They should be equal (set by same NOW() call)
            assert created == updated, f"created_at ({created}) != updated_at ({updated}) on creation"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_id_is_valid_uuid(self):
        """The id returned from task creation must be a parseable UUID, not an integer or arbitrary string."""
        resp = _create_task(title="UUID format check")
        try:
            assert resp.status_code == 201
            task_id = resp.json()["id"]
            # Must not raise
            parsed = uuid.UUID(str(task_id))
            assert str(parsed) == str(task_id).lower().strip()
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_mixed_whitespace_title_stripped(self):
        """Title with tabs, newlines, and spaces at edges should be stripped to clean content."""
        resp = _create_task(title="\t\n  Real Title \n\t ")
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == "Real Title"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_unicode_title(self):
        """Titles with unicode characters (CJK, emoji, accents) should be accepted and stored correctly."""
        title = "任务标题 🎉 café"
        resp = _create_task(title=title)
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == title
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_create_task_whitespace_padded_title_over_255_raw(self):
        """A title within 255 chars after stripping but exceeding 255 raw chars due to whitespace should be accepted."""
        inner = "a" * 200
        padded = " " * 30 + inner + " " * 30  # 260 raw chars
        resp = _create_task(title=padded)
        try:
            assert resp.status_code == 201
            assert resp.json()["title"] == inner
        finally:
            _cleanup_task(resp.json().get("id"))


class TestGoodhartGetTask:

    def test_goodhart_get_task_returns_correct_task(self):
        """GET /tasks/{id} must return the specific task matching the requested id, not any arbitrary task."""
        resp1 = _create_task(title="Unique Title Alpha 12345")
        resp2 = _create_task(title="Unique Title Beta 67890")
        try:
            id1 = resp1.json()["id"]
            id2 = resp2.json()["id"]

            get1 = client.get(f"/tasks/{id1}")
            get2 = client.get(f"/tasks/{id2}")

            assert get1.status_code == 200
            assert get2.status_code == 200
            assert get1.json()["id"] == str(id1) or get1.json()["id"] == id1
            assert get1.json()["title"] == "Unique Title Alpha 12345"
            assert get2.json()["id"] == str(id2) or get2.json()["id"] == id2
            assert get2.json()["title"] == "Unique Title Beta 67890"
        finally:
            _cleanup_task(resp1.json().get("id"))
            _cleanup_task(resp2.json().get("id"))

    def test_goodhart_get_task_timestamps_iso8601(self):
        """GET /tasks/{id} response timestamps must be ISO 8601 with timezone offset."""
        resp = _create_task(title="Timestamp format on read")
        try:
            task_id = resp.json()["id"]
            get_resp = client.get(f"/tasks/{task_id}")
            assert get_resp.status_code == 200
            data = get_resp.json()
            assert re.match(ISO_TZ_REGEX, data["created_at"]), f"created_at not ISO 8601+tz: {data['created_at']}"
            assert re.match(ISO_TZ_REGEX, data["updated_at"]), f"updated_at not ISO 8601+tz: {data['updated_at']}"
        finally:
            _cleanup_task(resp.json().get("id"))

    def test_goodhart_get_task_404_has_detail(self):
        """404 response for non-existent task must include a 'detail' field with a meaningful message."""
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/tasks/{fake_id}")
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0


class TestGoodhartUpdateTask:

    def test_goodhart_update_task_status_only(self):
        """Updating only the status field must preserve the original title and description."""
        create_resp = _create_task(title="Original Title", description="Original Desc", status="pending")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"status": "done"})
            assert update_resp.status_code == 200
            data = update_resp.json()
            assert data["status"] == "done"
            assert data["title"] == "Original Title"
            assert data["description"] == "Original Desc"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_description_only(self):
        """Updating only the description must preserve original title and status."""
        create_resp = _create_task(title="Keep Title", status="in_progress")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"description": "New description"})
            assert update_resp.status_code == 200
            data = update_resp.json()
            assert data["title"] == "Keep Title"
            assert data["status"] == "in_progress"
            assert data["description"] == "New description"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_description_to_empty_normalized(self):
        """Setting description to empty string via update must normalize it to None."""
        create_resp = _create_task(title="Desc to empty", description="Has content")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"description": ""})
            assert update_resp.status_code == 200
            assert update_resp.json()["description"] is None
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_description_whitespace_normalized(self):
        """Setting description to whitespace-only via update must normalize it to None."""
        create_resp = _create_task(title="Desc to ws", description="Has content")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"description": "   \t\n  "})
            assert update_resp.status_code == 200
            assert update_resp.json()["description"] is None
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_title_stripped(self):
        """Title provided in update with leading/trailing whitespace must be stripped in response."""
        create_resp = _create_task(title="Original")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"title": "  Updated Title  "})
            assert update_resp.status_code == 200
            assert update_resp.json()["title"] == "Updated Title"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_all_fields_simultaneously(self):
        """Updating title, description, and status simultaneously must change all three fields."""
        create_resp = _create_task(title="Old Title", description="Old Desc", status="pending")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={
                "title": "New Title",
                "description": "New Description",
                "status": "done"
            })
            assert update_resp.status_code == 200
            data = update_resp.json()
            assert data["title"] == "New Title"
            assert data["description"] == "New Description"
            assert data["status"] == "done"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_whitespace_only_title_rejected(self):
        """Updating with whitespace-only title (tabs+newlines) must be rejected with 422."""
        create_resp = _create_task(title="Valid Title")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"title": "\t\n  "})
            assert update_resp.status_code == 422
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_timestamps_iso8601(self):
        """PUT /tasks/{id} response timestamps must be ISO 8601 with timezone offset."""
        create_resp = _create_task(title="TS format update")
        try:
            task_id = create_resp.json()["id"]
            update_resp = client.put(f"/tasks/{task_id}", json={"title": "Updated TS"})
            assert update_resp.status_code == 200
            data = update_resp.json()
            assert re.match(ISO_TZ_REGEX, data["created_at"]), f"created_at not ISO 8601+tz: {data['created_at']}"
            assert re.match(ISO_TZ_REGEX, data["updated_at"]), f"updated_at not ISO 8601+tz: {data['updated_at']}"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_multiple_times_updated_at_advances(self):
        """Updating a task multiple times must keep advancing updated_at while created_at remains unchanged."""
        create_resp = _create_task(title="Multi update")
        try:
            task_id = create_resp.json()["id"]
            original_created = create_resp.json()["created_at"]

            time.sleep(0.1)
            update1 = client.put(f"/tasks/{task_id}", json={"title": "Update 1"})
            assert update1.status_code == 200
            updated_at_1 = update1.json()["updated_at"]
            assert update1.json()["created_at"] == original_created

            time.sleep(0.1)
            update2 = client.put(f"/tasks/{task_id}", json={"title": "Update 2"})
            assert update2.status_code == 200
            updated_at_2 = update2.json()["updated_at"]
            assert update2.json()["created_at"] == original_created

            assert updated_at_2 >= updated_at_1, "updated_at should advance on subsequent updates"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_update_task_404_has_detail(self):
        """404 response for updating a non-existent task must include a 'detail' field."""
        fake_id = str(uuid.uuid4())
        resp = client.put(f"/tasks/{fake_id}", json={"title": "Ghost"})
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0


class TestGoodhartDeleteTask:

    def test_goodhart_delete_task_idempotent_404(self):
        """Deleting an already-deleted task must return 404 on the second attempt."""
        create_resp = _create_task(title="Delete twice")
        task_id = create_resp.json()["id"]

        first_delete = client.delete(f"/tasks/{task_id}")
        assert first_delete.status_code == 200

        second_delete = client.delete(f"/tasks/{task_id}")
        assert second_delete.status_code == 404

    def test_goodhart_delete_task_removes_from_list(self):
        """After deleting a task, it must no longer appear in GET /tasks listing."""
        create_resp = _create_task(title="Delete from list test")
        task_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/tasks/{task_id}")
        assert delete_resp.status_code == 200

        list_resp = client.get("/tasks")
        assert list_resp.status_code == 200
        task_ids = [t["id"] for t in list_resp.json()]
        assert task_id not in task_ids and str(task_id) not in [str(tid) for tid in task_ids]

    def test_goodhart_delete_task_response_id_matches(self):
        """The id in DeleteConfirmation must match the requested deletion id."""
        create_resp = _create_task(title="Delete id match")
        task_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/tasks/{task_id}")
        assert delete_resp.status_code == 200
        data = delete_resp.json()
        assert str(data["id"]) == str(task_id)

    def test_goodhart_delete_task_response_detail_nonempty(self):
        """The detail field in DeleteConfirmation must be a non-empty string."""
        create_resp = _create_task(title="Delete detail check")
        task_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/tasks/{task_id}")
        assert delete_resp.status_code == 200
        data = delete_resp.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0

    def test_goodhart_delete_task_404_has_detail(self):
        """404 response for deleting a non-existent task must include a 'detail' field."""
        fake_id = str(uuid.uuid4())
        resp = client.delete(f"/tasks/{fake_id}")
        assert resp.status_code == 404
        data = resp.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        assert len(data["detail"]) > 0


class TestGoodhartListTasks:

    def test_goodhart_list_tasks_contains_created_task(self):
        """A task created via POST must appear in the subsequent GET /tasks listing with matching fields."""
        unique_title = f"Findable Task {uuid.uuid4().hex[:8]}"
        create_resp = _create_task(title=unique_title, status="in_progress")
        try:
            assert create_resp.status_code == 201
            task_id = create_resp.json()["id"]

            list_resp = client.get("/tasks")
            assert list_resp.status_code == 200
            tasks = list_resp.json()
            found = [t for t in tasks if str(t["id"]) == str(task_id)]
            assert len(found) == 1, f"Created task {task_id} not found in listing"
            assert found[0]["title"] == unique_title
            assert found[0]["status"] == "in_progress"
        finally:
            _cleanup_task(create_resp.json().get("id"))

    def test_goodhart_list_tasks_order_with_three_tasks(self):
        """Listing three sequentially created tasks should return them in created_at DESC order."""
        created_ids = []
        try:
            for i in range(3):
                resp = _create_task(title=f"Order test {i} {uuid.uuid4().hex[:8]}")
                assert resp.status_code == 201
                created_ids.append(resp.json()["id"])
                time.sleep(0.05)  # ensure distinct timestamps

            list_resp = client.get("/tasks")
            assert list_resp.status_code == 200
            tasks = list_resp.json()

            # Verify DESC ordering of all tasks in the list
            for i in range(len(tasks) - 1):
                assert tasks[i]["created_at"] >= tasks[i + 1]["created_at"], \
                    f"Tasks not in created_at DESC order: {tasks[i]['created_at']} < {tasks[i+1]['created_at']}"
        finally:
            for tid in created_ids:
                _cleanup_task(tid)

    def test_goodhart_list_tasks_after_delete_excludes_deleted(self):
        """After creating 3 tasks and deleting one, list should not include the deleted task."""
        created_ids = []
        try:
            for i in range(3):
                resp = _create_task(title=f"Del list test {i} {uuid.uuid4().hex[:8]}")
                assert resp.status_code == 201
                created_ids.append(resp.json()["id"])

            # Delete the middle one
            delete_id = created_ids[1]
            del_resp = client.delete(f"/tasks/{delete_id}")
            assert del_resp.status_code == 200

            list_resp = client.get("/tasks")
            assert list_resp.status_code == 200
            listed_ids = [str(t["id"]) for t in list_resp.json()]
            assert str(delete_id) not in listed_ids
        finally:
            for tid in created_ids:
                _cleanup_task(tid)


class TestGoodhartHealthCheck:

    def test_goodhart_health_check_response_exact(self):
        """Health check must return exactly {'status': 'ok'} with no additional fields."""
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data == {"status": "ok"}, f"Expected exactly {{'status': 'ok'}}, got {data}"
        # Ensure no extra keys
        assert set(data.keys()) == {"status"}
