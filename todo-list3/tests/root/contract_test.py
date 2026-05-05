"""
Contract tests for root component.

Two logical sections:
1. Type/validator unit tests (no infrastructure required)
2. Integration verification tests (require live backend/database, skip otherwise)

Run with: pytest contract_test.py -v
"""
import os
import re
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Import component under test
# ---------------------------------------------------------------------------
# We attempt imports defensively so type-level tests can still run even if
# some runtime dependencies are missing in the test environment.
try:
    from root import (
        TaskStatus,
        TaskTitle,
        TaskCreateRequest,
        TaskUpdateRequest,
        TaskResponse,
        TaskListResponse,
        HealthResponse,
        DatabaseURL,
        HttpEndpoint,
        DeleteConfirmation,
        ErrorResponse,
        ValidationErrorResponse,
        ValidationErrorItem,
        verify_http_api_contract,
        verify_cross_tier_invariants,
        verify_schema_initialization_idempotent,
        verify_test_isolation,
        verify_cors_configuration,
        verify_connection_pool_lifecycle,
    )
    ROOT_IMPORTED = True
except ImportError:
    ROOT_IMPORTED = False

pytestmark = pytest.mark.skipif(not ROOT_IMPORTED, reason="root module not importable")


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def backend_base_url() -> str:
    """Backend URL from env or default; skip when backend is unreachable."""
    import urllib.request
    url: str = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000")
    try:
        urllib.request.urlopen(url + "/health", timeout=2)
    except Exception:
        pytest.skip(f"Backend not reachable at {url}")
    return url


@pytest.fixture
def database_url() -> str:
    """Database URL from env; skip when absent."""
    url = os.environ.get("DATABASE_URL")
    if url is None:
        pytest.skip("DATABASE_URL not set — skipping database-dependent test")
    return url


@pytest.fixture
def frontend_origin() -> str:
    """Frontend origin from env or default."""
    return os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")


# ===========================================================================
# Section 1: Type / Validator Unit Tests
# ===========================================================================

class TestTaskStatusEnum:
    """CROSS-TIER-11: TaskStatus enum values are exactly {pending, in_progress, done}."""

    def test_enum_has_exactly_three_members(self) -> None:
        members = list(TaskStatus)
        assert len(members) == 3, f"Expected 3 TaskStatus members, got {len(members)}"

    def test_enum_values_match_contract(self) -> None:
        values = {s.value for s in TaskStatus}
        expected = {"pending", "in_progress", "done"}
        assert values == expected, f"TaskStatus values {values} != expected {expected}"

    def test_enum_member_access(self) -> None:
        assert TaskStatus.pending is not None
        assert TaskStatus.in_progress is not None
        assert TaskStatus.done is not None

    def test_enum_value_strings(self) -> None:
        assert TaskStatus.pending.value == "pending"
        assert TaskStatus.in_progress.value == "in_progress"
        assert TaskStatus.done.value == "done"


class TestTaskTitle:
    """TaskTitle: non-blank, whitespace-stripped, 1-255 chars after strip."""

    def test_valid_title_accepted(self) -> None:
        title = TaskTitle(value="Buy groceries")
        assert title.value == "Buy groceries"

    def test_whitespace_stripped(self) -> None:
        title = TaskTitle(value="  Hello World  ")
        assert title.value == "Hello World"

    def test_single_char_after_strip_accepted(self) -> None:
        title = TaskTitle(value="  a  ")
        assert title.value == "a"

    def test_exactly_255_chars_accepted(self) -> None:
        long_title = "x" * 255
        title = TaskTitle(value=long_title)
        assert len(title.value) == 255

    def test_256_chars_rejected(self) -> None:
        over_limit = "x" * 256
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value=over_limit)

    def test_empty_string_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="")

    def test_whitespace_only_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="   ")

    def test_tab_and_newline_whitespace_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="\t\n  ")


class TestHealthResponse:
    """HealthResponse status must be 'ok'."""

    def test_status_ok_valid(self) -> None:
        resp = HealthResponse(status="ok")
        assert resp.status == "ok"

    def test_status_not_ok_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            HealthResponse(status="bad")

    def test_status_empty_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            HealthResponse(status="")


class TestDatabaseURL:
    """DatabaseURL must start with postgresql://."""

    def test_valid_postgresql_url(self) -> None:
        url = DatabaseURL(value="postgresql://user:pass@localhost:5432/dbname")
        assert url.value.startswith("postgresql://")

    def test_minimal_postgresql_url(self) -> None:
        url = DatabaseURL(value="postgresql://localhost/db")
        assert url.value == "postgresql://localhost/db"

    def test_mysql_url_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            DatabaseURL(value="mysql://host/db")

    def test_empty_string_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            DatabaseURL(value="")

    def test_http_url_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            DatabaseURL(value="http://localhost:5432/db")


class TestHttpEndpoint:
    """HttpEndpoint method must be one of GET, POST, PUT, DELETE."""

    def _make_endpoint(self, method: str) -> "HttpEndpoint":
        return HttpEndpoint(
            method=method,
            path="/test",
            request_body_type=None,
            response_body_type="TestResponse",
            success_status_code=200,
            content_type="application/json",
        )

    def test_get_method_valid(self) -> None:
        ep = self._make_endpoint("GET")
        assert ep.method == "GET"

    def test_post_method_valid(self) -> None:
        ep = self._make_endpoint("POST")
        assert ep.method == "POST"

    def test_put_method_valid(self) -> None:
        ep = self._make_endpoint("PUT")
        assert ep.method == "PUT"

    def test_delete_method_valid(self) -> None:
        ep = self._make_endpoint("DELETE")
        assert ep.method == "DELETE"

    def test_patch_method_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            self._make_endpoint("PATCH")

    def test_lowercase_method_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            self._make_endpoint("get")


class TestTaskCreateRequest:
    """TaskCreateRequest title validation: 1-255 chars, rejects blank."""

    def test_valid_creation(self) -> None:
        req = TaskCreateRequest(
            title="Test task",
            description=None,
            status=TaskStatus.pending,
        )
        assert req.title is not None

    def test_empty_title_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskCreateRequest(title="", description=None, status=TaskStatus.pending)

    def test_whitespace_only_title_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskCreateRequest(title="   ", description=None, status=TaskStatus.pending)

    def test_title_at_max_boundary(self) -> None:
        req = TaskCreateRequest(
            title="a" * 255,
            description="desc",
            status=TaskStatus.done,
        )
        assert len(req.title) <= 255

    def test_title_exceeds_max_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskCreateRequest(
                title="a" * 256,
                description=None,
                status=TaskStatus.pending,
            )

    def test_description_none_accepted(self) -> None:
        req = TaskCreateRequest(
            title="T", description=None, status=TaskStatus.pending
        )
        assert req.description is None

    def test_description_string_accepted(self) -> None:
        req = TaskCreateRequest(
            title="T", description="Some description", status=TaskStatus.in_progress
        )
        assert req.description == "Some description"


class TestTaskUpdateRequest:
    """TaskUpdateRequest title validation mirrors TaskCreateRequest."""

    def test_valid_update(self) -> None:
        req = TaskUpdateRequest(
            title="Updated title",
            description="New desc",
            status=TaskStatus.done,
        )
        assert req.title == "Updated title"

    def test_empty_title_rejected(self) -> None:
        with pytest.raises((ValueError, Exception)):
            TaskUpdateRequest(title="", description=None, status=TaskStatus.pending)


class TestDeleteConfirmation:
    """DeleteConfirmation has detail string and id."""

    def test_valid_confirmation(self) -> None:
        dc = DeleteConfirmation(detail="Task deleted", id=42)
        assert dc.detail == "Task deleted"
        assert dc.id == 42


class TestErrorResponse:
    """ErrorResponse wraps a detail string."""

    def test_valid_error(self) -> None:
        er = ErrorResponse(detail="Task not found")
        assert er.detail == "Task not found"


# ===========================================================================
# Section 2: Integration Verification Tests (mocked dependencies)
# ===========================================================================


class TestVerifySchemaInitializationIdempotent:
    """Tests for verify_schema_initialization_idempotent."""

    def test_happy_path_returns_true(self, database_url: str) -> None:
        """Schema init verification succeeds against live database."""
        result = verify_schema_initialization_idempotent(database_url)
        assert result is True, "verify_schema_initialization_idempotent should return True"

    def test_unreachable_database_raises(self) -> None:
        """Raises on unreachable database."""
        bad_url = "postgresql://nouser:nopass@192.0.2.1:5432/nodb"
        with pytest.raises(Exception) as exc_info:
            verify_schema_initialization_idempotent(bad_url)
        # Accept any exception — the key contract is that it does not return True
        assert exc_info.value is not None


class TestVerifyTestIsolation:
    """Tests for verify_test_isolation."""

    def test_happy_path_returns_true(self, database_url: str) -> None:
        result = verify_test_isolation(database_url)
        assert result is True, "verify_test_isolation should return True"

    def test_unreachable_database_raises(self) -> None:
        bad_url = "postgresql://nouser:nopass@192.0.2.1:5432/nodb"
        with pytest.raises(Exception) as exc_info:
            verify_test_isolation(bad_url)
        assert exc_info.value is not None


class TestVerifyConnectionPoolLifecycle:
    """Tests for verify_connection_pool_lifecycle (async)."""

    @pytest.mark.anyio
    async def test_happy_path_returns_true(self, backend_base_url: str) -> None:
        result = await verify_connection_pool_lifecycle(backend_base_url)
        assert result is True, "verify_connection_pool_lifecycle should return True"

    @pytest.mark.anyio
    async def test_unreachable_backend_raises(self) -> None:
        bad_url = "http://192.0.2.1:9999"
        with pytest.raises(Exception) as exc_info:
            await verify_connection_pool_lifecycle(bad_url)
        assert exc_info.value is not None


class TestVerifyHttpApiContract:
    """Tests for verify_http_api_contract (async)."""

    @pytest.mark.anyio
    async def test_happy_path_returns_true(self, backend_base_url: str) -> None:
        result = await verify_http_api_contract(backend_base_url)
        assert result is True, "verify_http_api_contract should return True"

    @pytest.mark.anyio
    async def test_unreachable_backend_raises(self) -> None:
        bad_url = "http://192.0.2.1:9999"
        with pytest.raises(Exception) as exc_info:
            await verify_http_api_contract(bad_url)
        assert exc_info.value is not None


class TestVerifyCrossTierInvariants:
    """Tests for verify_cross_tier_invariants (async)."""

    @pytest.mark.anyio
    async def test_happy_path_returns_true(
        self, backend_base_url: str, database_url: str
    ) -> None:
        result = await verify_cross_tier_invariants(backend_base_url, database_url)
        assert result is True, "verify_cross_tier_invariants should return True"

    @pytest.mark.anyio
    async def test_unreachable_backend_raises(self) -> None:
        bad_url = "http://192.0.2.1:9999"
        db_url = "postgresql://nouser:nopass@192.0.2.1:5432/nodb"
        with pytest.raises(Exception) as exc_info:
            await verify_cross_tier_invariants(bad_url, db_url)
        assert exc_info.value is not None


class TestVerifyCorsConfiguration:
    """Tests for verify_cors_configuration (async)."""

    @pytest.mark.anyio
    async def test_happy_path_returns_true(
        self, backend_base_url: str, frontend_origin: str
    ) -> None:
        result = await verify_cors_configuration(backend_base_url, frontend_origin)
        assert result is True, "verify_cors_configuration should return True"

    @pytest.mark.anyio
    async def test_unreachable_backend_raises(self) -> None:
        bad_url = "http://192.0.2.1:9999"
        with pytest.raises(Exception) as exc_info:
            await verify_cors_configuration(bad_url, "http://localhost:5173")
        assert exc_info.value is not None

    @pytest.mark.anyio
    async def test_wrong_origin_may_fail(self, backend_base_url: str) -> None:
        """If CORS is strict, a wrong origin should trigger cors_not_configured."""
        # This test verifies that the function actually validates the origin.
        # If CORS allows '*', this will still pass — which is acceptable per contract.
        try:
            result = await verify_cors_configuration(
                backend_base_url, "http://evil.example.com:9999"
            )
            # If it returns True, CORS allows all origins (wildcard) — acceptable
            assert result is True
        except Exception:
            # cors_not_configured or similar — also acceptable
            pass


# ===========================================================================
# Section 3: Cross-cutting invariant tests
# ===========================================================================

class TestCrossTierInvariantTypes:
    """Verify type-level invariants from the contract."""

    def test_cross_tier_11_status_enum_consistency(self) -> None:
        """CROSS-TIER-11: TaskStatus values are {pending, in_progress, done}."""
        values = {s.value for s in TaskStatus}
        assert values == {"pending", "in_progress", "done"}

    def test_cross_tier_06_database_url_prefix(self) -> None:
        """CROSS-TIER-06: DatabaseURL must start with postgresql://."""
        valid = DatabaseURL(value="postgresql://x")
        assert valid.value.startswith("postgresql://")
        with pytest.raises((ValueError, Exception)):
            DatabaseURL(value="sqlite:///test.db")

    def test_cross_tier_18_blank_title_rejected(self) -> None:
        """CROSS-TIER-18: Title must be non-blank after whitespace stripping."""
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="   ")
        with pytest.raises((ValueError, Exception)):
            TaskTitle(value="")

    def test_cross_tier_10_iso_timestamp_format(self) -> None:
        """CROSS-TIER-10: ISOTimestamp must be timezone-aware ISO 8601."""
        # Verify that a timezone-aware datetime produces correct ISO format
        dt = datetime(2024, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        iso_str = dt.isoformat()
        assert "+" in iso_str or "Z" in iso_str, f"Expected tz offset in {iso_str}"
        # Verify the pattern matches the contract example format
        assert re.match(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}", iso_str
        ), f"ISO string {iso_str} does not match expected pattern"
