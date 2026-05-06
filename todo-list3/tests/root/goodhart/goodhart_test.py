"""
Hidden adversarial acceptance tests for the Root component.

These tests are designed to catch implementations that pass visible tests
through shortcuts (hardcoded returns, incomplete validation, etc.) rather
than truly satisfying the contract.
"""

import pytest
import asyncio
import re
import json
import time
import httpx
import os

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

ISO_TZ_REGEX = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$"
)


def _sync(coro):
    """Run an async coroutine in a new event loop (pytest-friendly)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as c:
        yield c


@pytest.fixture()
def create_and_cleanup(client):
    """Creates a task, yields its data, then deletes it for cleanup."""
    created_ids = []

    def _create(payload=None):
        if payload is None:
            payload = {"title": f"goodhart-fixture-{time.time()}"}
        resp = client.post("/tasks", json=payload)
        assert resp.status_code == 201, f"Setup failed: {resp.status_code} {resp.text}"
        data = resp.json()
        created_ids.append(data["id"])
        return data

    yield _create

    for tid in created_ids:
        client.delete(f"/tasks/{tid}")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGoodhartHttpApiContract:
    """Tests targeting verify_http_api_contract gaps."""

    def test_goodhart_create_returns_matching_title(self, client, create_and_cleanup):
        """POST /tasks must return a TaskResponse whose title field matches
        the title sent in the request body, not a hardcoded value."""
        unique_title = f"Unique-{time.time_ns()}"
        data = create_and_cleanup({"title": unique_title})
        assert data["title"] == unique_title

    def test_goodhart_create_returns_unique_ids(self, client, create_and_cleanup):
        """Each POST /tasks call must return a distinct auto-generated id."""
        t1 = create_and_cleanup({"title": "id-test-1"})
        t2 = create_and_cleanup({"title": "id-test-2"})
        assert t1["id"] != t2["id"]

    def test_goodhart_404_detail_message_exact(self, client):
        """GET /tasks/{id} for a non-existent task must return detail exactly
        'Task not found'."""
        resp = client.get("/tasks/999999999")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body
        assert body["detail"] == "Task not found"

    def test_goodhart_delete_confirmation_includes_correct_id(
        self, client, create_and_cleanup
    ):
        """DELETE response 'id' field must match the deleted task's id."""
        task = create_and_cleanup({"title": "del-id-check"})
        tid = task["id"]
        resp = client.delete(f"/tasks/{tid}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == tid

    def test_goodhart_title_length_256_rejected(self, client):
        """A title of exactly 256 characters must be rejected with 422."""
        resp = client.post("/tasks", json={"title": "a" * 256})
        assert resp.status_code == 422

    def test_goodhart_create_with_explicit_status_in_progress(
        self, client, create_and_cleanup
    ):
        """POST with status 'in_progress' must honor that value."""
        data = create_and_cleanup(
            {"title": "status-test", "status": "in_progress"}
        )
        assert data["status"] == "in_progress"

    def test_goodhart_create_with_explicit_status_done(
        self, client, create_and_cleanup
    ):
        """POST with status 'done' must store it, not force 'pending'."""
        data = create_and_cleanup({"title": "done-test", "status": "done"})
        assert data["status"] == "done"

    def test_goodhart_get_task_returns_correct_task_by_id(
        self, client, create_and_cleanup
    ):
        """GET /tasks/{id} must return the specific task matching the id."""
        t1 = create_and_cleanup({"title": "first-task"})
        t2 = create_and_cleanup({"title": "second-task"})

        resp1 = client.get(f"/tasks/{t1['id']}")
        assert resp1.status_code == 200
        assert resp1.json()["title"] == "first-task"

        resp2 = client.get(f"/tasks/{t2['id']}")
        assert resp2.status_code == 200
        assert resp2.json()["title"] == "second-task"

    def test_goodhart_update_blank_title_rejected(self, client, create_and_cleanup):
        """PUT with blank-after-strip title must be rejected with 422."""
        task = create_and_cleanup({"title": "valid-title"})
        resp = client.put(f"/tasks/{task['id']}", json={"title": "   "})
        assert resp.status_code == 422

    def test_goodhart_update_invalid_status_rejected(self, client, create_and_cleanup):
        """PUT with an invalid status must be rejected with 422."""
        task = create_and_cleanup({"title": "status-val"})
        resp = client.put(f"/tasks/{task['id']}", json={"status": "archived"})
        assert resp.status_code == 422

    def test_goodhart_status_invalid_value_rejected(self, client):
        """POST with a non-enum status value must be rejected with 422."""
        resp = client.post(
            "/tasks", json={"title": "test", "status": "cancelled"}
        )
        assert resp.status_code == 422

    def test_goodhart_created_at_and_updated_at_present_on_create(
        self, client, create_and_cleanup
    ):
        """POST response must include both timestamp fields as valid ISO 8601."""
        data = create_and_cleanup({"title": "ts-check"})
        assert "created_at" in data
        assert "updated_at" in data
        assert ISO_TZ_REGEX.match(data["created_at"]), f"Bad created_at: {data['created_at']}"
        assert ISO_TZ_REGEX.match(data["updated_at"]), f"Bad updated_at: {data['updated_at']}"

    def test_goodhart_task_list_empty_when_no_tasks(self, client):
        """GET /tasks must return [] when no tasks exist, not null or error."""
        # First, collect and delete all existing tasks
        resp = client.get("/tasks")
        assert resp.status_code == 200
        existing = resp.json()
        assert isinstance(existing, list)
        for t in existing:
            client.delete(f"/tasks/{t['id']}")

        resp = client.get("/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert body == []

    def test_goodhart_create_response_has_all_six_fields(
        self, client, create_and_cleanup
    ):
        """POST response must contain all six TaskResponse fields."""
        data = create_and_cleanup({"title": "field-check"})
        for key in ("id", "title", "description", "status", "created_at", "updated_at"):
            assert key in data, f"Missing key '{key}' in response"

    def test_goodhart_get_task_response_has_all_six_fields(
        self, client, create_and_cleanup
    ):
        """GET /tasks/{id} response must contain all six TaskResponse fields."""
        task = create_and_cleanup({"title": "get-fields"})
        resp = client.get(f"/tasks/{task['id']}")
        data = resp.json()
        for key in ("id", "title", "description", "status", "created_at", "updated_at"):
            assert key in data, f"Missing key '{key}' in GET response"

    def test_goodhart_delete_confirmation_has_detail_and_id(
        self, client, create_and_cleanup
    ):
        """DELETE response must contain both 'detail' and 'id' fields."""
        task = create_and_cleanup({"title": "del-shape"})
        resp = client.delete(f"/tasks/{task['id']}")
        assert resp.status_code == 200
        body = resp.json()
        assert "detail" in body
        assert "id" in body

    def test_goodhart_create_post_status_code_is_201_not_200(self, client, create_and_cleanup):
        """POST /tasks must return 201, not 200."""
        resp_raw = client.post("/tasks", json={"title": "status-code-test"})
        # Cleanup
        if resp_raw.status_code in (200, 201):
            tid = resp_raw.json().get("id")
            if tid:
                client.delete(f"/tasks/{tid}")
        assert resp_raw.status_code == 201

    def test_goodhart_list_tasks_returns_array_not_object(self, client):
        """GET /tasks must return a JSON array at the top level."""
        resp = client.get("/tasks")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list), f"Expected list, got {type(body)}"

    def test_goodhart_task_id_is_integer(self, client, create_and_cleanup):
        """Task id must be an integer, not a string or UUID."""
        data = create_and_cleanup({"title": "int-id-check"})
        assert isinstance(data["id"], int), f"Expected int id, got {type(data['id'])}"

    def test_goodhart_404_for_id_zero(self, client):
        """GET /tasks/0 should return 404 since SERIAL ids start at 1."""
        resp = client.get("/tasks/0")
        assert resp.status_code == 404

    def test_goodhart_404_for_negative_id(self, client):
        """GET /tasks/-1 should return 404 or 422."""
        resp = client.get("/tasks/-1")
        assert resp.status_code in (404, 422)

    def test_goodhart_update_with_all_three_fields(self, client, create_and_cleanup):
        """PUT with all three fields must update all of them."""
        task = create_and_cleanup(
            {"title": "orig", "description": "orig-desc", "status": "pending"}
        )
        resp = client.put(
            f"/tasks/{task['id']}",
            json={
                "title": "new-title",
                "description": "new-desc",
                "status": "done",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "new-title"
        assert body["description"] == "new-desc"
        assert body["status"] == "done"

    def test_goodhart_missing_title_field_rejected(self, client):
        """POST with no title field at all must return 422."""
        resp = client.post("/tasks", json={"description": "no title here"})
        assert resp.status_code == 422

    def test_goodhart_create_task_with_special_chars_in_title(
        self, client, create_and_cleanup
    ):
        """Unicode/special characters in title must be preserved."""
        special = "Tâche à faire — «test» 🎯"
        data = create_and_cleanup({"title": special})
        assert data["title"] == special

    def test_goodhart_health_response_content_type_json(self, client):
        """GET /health must return Content-Type: application/json."""
        resp = client.get("/health")
        assert resp.status_code == 200
        ct = resp.headers.get("content-type", "")
        assert "application/json" in ct


class TestGoodhartCrossTierInvariants:
    """Tests targeting verify_cross_tier_invariants gaps."""

    def test_goodhart_title_with_interior_whitespace_preserved(
        self, client, create_and_cleanup
    ):
        """Stripping only removes leading/trailing; interior whitespace kept."""
        data = create_and_cleanup({"title": "  hello   world  "})
        assert data["title"] == "hello   world"

    def test_goodhart_description_whitespace_tabs_normalized(
        self, client, create_and_cleanup
    ):
        """Description of tabs/newlines/spaces only must normalize to null."""
        data = create_and_cleanup(
            {"title": "ws-desc", "description": "  \t\n  "}
        )
        assert data["description"] is None

    def test_goodhart_description_nonempty_preserved(
        self, client, create_and_cleanup
    ):
        """Non-whitespace description must be returned as-is, not nullified."""
        data = create_and_cleanup(
            {"title": "desc-keep", "description": "This is a real description"}
        )
        assert data["description"] == "This is a real description"

    def test_goodhart_description_explicit_null_stored_as_null(
        self, client, create_and_cleanup
    ):
        """Explicit null description must remain null."""
        data = create_and_cleanup({"title": "null-desc", "description": None})
        assert data["description"] is None

    def test_goodhart_description_empty_string_normalized_to_null(
        self, client, create_and_cleanup
    ):
        """Empty string description must normalize to null per CROSS-TIER-09."""
        data = create_and_cleanup({"title": "empty-desc", "description": ""})
        assert data["description"] is None

    def test_goodhart_put_only_title_preserves_description_and_status(
        self, client, create_and_cleanup
    ):
        """PUT with only title must not alter description or status."""
        task = create_and_cleanup(
            {
                "title": "Original",
                "description": "Keep this",
                "status": "in_progress",
            }
        )
        resp = client.put(
            f"/tasks/{task['id']}", json={"title": "Updated"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "Updated"
        assert body["description"] == "Keep this"
        assert body["status"] == "in_progress"

    def test_goodhart_put_only_status_preserves_title_and_description(
        self, client, create_and_cleanup
    ):
        """PUT with only status must not alter title or description."""
        task = create_and_cleanup(
            {
                "title": "Keep",
                "description": "Also Keep",
                "status": "pending",
            }
        )
        resp = client.put(
            f"/tasks/{task['id']}", json={"status": "done"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "Keep"
        assert body["description"] == "Also Keep"
        assert body["status"] == "done"

    def test_goodhart_put_only_description_preserves_title_and_status(
        self, client, create_and_cleanup
    ):
        """PUT with only description must not alter title or status."""
        task = create_and_cleanup(
            {"title": "T", "status": "in_progress"}
        )
        resp = client.put(
            f"/tasks/{task['id']}", json={"description": "New desc"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "T"
        assert body["description"] == "New desc"
        assert body["status"] == "in_progress"

    def test_goodhart_update_title_stripping(self, client, create_and_cleanup):
        """PUT must also strip leading/trailing whitespace from title."""
        task = create_and_cleanup({"title": "original"})
        resp = client.put(
            f"/tasks/{task['id']}", json={"title": "  Updated Title  "}
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated Title"

    def test_goodhart_update_description_normalization(
        self, client, create_and_cleanup
    ):
        """PUT with whitespace-only description must normalize to null."""
        task = create_and_cleanup(
            {"title": "desc-norm", "description": "Something"}
        )
        resp = client.put(
            f"/tasks/{task['id']}", json={"description": "   "}
        )
        assert resp.status_code == 200
        assert resp.json()["description"] is None

    def test_goodhart_multiple_updates_each_refresh_updated_at(
        self, client, create_and_cleanup
    ):
        """Multiple sequential PUTs must each produce non-decreasing updated_at."""
        task = create_and_cleanup({"title": "multi-update"})
        timestamps = []
        for i in range(3):
            resp = client.put(
                f"/tasks/{task['id']}",
                json={"title": f"multi-update-{i}"},
            )
            assert resp.status_code == 200
            timestamps.append(resp.json()["updated_at"])
            time.sleep(0.05)  # small delay to allow timestamp progression

        for j in range(len(timestamps) - 1):
            assert timestamps[j] <= timestamps[j + 1], (
                f"updated_at did not increase: {timestamps[j]} -> {timestamps[j+1]}"
            )

    def test_goodhart_ordering_with_three_plus_tasks(
        self, client, create_and_cleanup
    ):
        """GET /tasks ordering by created_at DESC for 3+ tasks."""
        tasks = []
        for i in range(3):
            t = create_and_cleanup({"title": f"order-{i}"})
            tasks.append(t)
            time.sleep(0.05)

        resp = client.get("/tasks")
        assert resp.status_code == 200
        listed = resp.json()

        # Extract our created task ids
        our_ids = [t["id"] for t in tasks]
        our_listed = [t for t in listed if t["id"] in our_ids]

        # They should appear in reverse creation order (newest first)
        listed_ids = [t["id"] for t in our_listed]
        expected_ids = list(reversed(our_ids))
        assert listed_ids == expected_ids, (
            f"Ordering wrong: got {listed_ids}, expected {expected_ids}"
        )

    def test_goodhart_timestamps_have_timezone_not_naive(
        self, client, create_and_cleanup
    ):
        """Timestamps must include timezone offset, not be naive."""
        data = create_and_cleanup({"title": "tz-check"})
        for field in ("created_at", "updated_at"):
            val = data[field]
            assert "+" in val or "Z" in val, (
                f"{field} lacks timezone: {val}"
            )

    def test_goodhart_double_delete_returns_404(self, client, create_and_cleanup):
        """Deleting same task twice: second attempt must return 404."""
        # Create manually to avoid cleanup fixture trying to delete again
        resp = client.post("/tasks", json={"title": "double-del"})
        assert resp.status_code == 201
        tid = resp.json()["id"]

        r1 = client.delete(f"/tasks/{tid}")
        assert r1.status_code == 200

        r2 = client.delete(f"/tasks/{tid}")
        assert r2.status_code == 404

    def test_goodhart_delete_then_list_excludes_deleted(
        self, client, create_and_cleanup
    ):
        """After deletion, GET /tasks must not include the deleted task."""
        resp = client.post("/tasks", json={"title": "list-excl"})
        assert resp.status_code == 201
        tid = resp.json()["id"]

        client.delete(f"/tasks/{tid}")

        resp = client.get("/tasks")
        assert resp.status_code == 200
        ids_in_list = [t["id"] for t in resp.json()]
        assert tid not in ids_in_list

    def test_goodhart_title_tab_and_newline_stripping(
        self, client, create_and_cleanup
    ):
        """Title strip() handles tabs and newlines, not just spaces."""
        data = create_and_cleanup({"title": "\t\nActual Title\n\t"})
        assert data["title"] == "Actual Title"


class TestGoodhartCors:
    """Tests targeting verify_cors_configuration gaps."""

    def test_goodhart_cors_allows_put_method(self, client):
        """CORS must explicitly allow PUT method."""
        resp = client.options(
            "/tasks",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "PUT",
            },
        )
        methods = resp.headers.get("access-control-allow-methods", "")
        assert "PUT" in methods.upper(), f"PUT not in allowed methods: {methods}"

    def test_goodhart_cors_allows_delete_method(self, client):
        """CORS must explicitly allow DELETE method."""
        resp = client.options(
            "/tasks",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "DELETE",
            },
        )
        methods = resp.headers.get("access-control-allow-methods", "")
        assert "DELETE" in methods.upper(), f"DELETE not in allowed methods: {methods}"
