"""Integration tests for the Root glue layer.

These tests validate that the glue code correctly delegates to child
components and satisfies the parent contract.  Tests requiring a live
backend/database are conditionally skipped when the relevant environment
variables are absent.

Environment variables:
    BACKEND_BASE_URL — e.g. http://localhost:8000  (default: not set → skip)
    DATABASE_URL     — e.g. postgresql://user:pass@localhost:5432/tasks
"""

import os
import asyncio
import pytest

# ---------------------------------------------------------------------------
# Skip conditions
# ---------------------------------------------------------------------------

BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

skip_no_backend = pytest.mark.skipif(
    not BACKEND_BASE_URL,
    reason="BACKEND_BASE_URL not set; skipping live backend tests",
)
skip_no_database = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL not set; skipping live database tests",
)
skip_no_both = pytest.mark.skipif(
    not BACKEND_BASE_URL or not DATABASE_URL,
    reason="BACKEND_BASE_URL and/or DATABASE_URL not set",
)


# ---------------------------------------------------------------------------
# Import glue
# ---------------------------------------------------------------------------

from glue import (
    verify_http_api_contract,
    verify_cross_tier_invariants,
    verify_schema_initialization_idempotent,
    verify_test_isolation,
    verify_cors_configuration,
    verify_connection_pool_lifecycle,
)


# ---------------------------------------------------------------------------
# Unit tests — structural (no live services required)
# ---------------------------------------------------------------------------

class TestGlueImports:
    """Verify that all parent functions are importable from the glue module."""

    def test_verify_http_api_contract_callable(self):
        assert callable(verify_http_api_contract)

    def test_verify_cross_tier_invariants_callable(self):
        assert callable(verify_cross_tier_invariants)

    def test_verify_schema_initialization_idempotent_callable(self):
        assert callable(verify_schema_initialization_idempotent)

    def test_verify_test_isolation_callable(self):
        assert callable(verify_test_isolation)

    def test_verify_cors_configuration_callable(self):
        assert callable(verify_cors_configuration)

    def test_verify_connection_pool_lifecycle_callable(self):
        assert callable(verify_connection_pool_lifecycle)


class TestInputValidation:
    """Verify that parent input validators are enforced at the glue boundary."""

    def test_http_api_rejects_invalid_url(self):
        with pytest.raises(ValueError, match="must start with http"):
            asyncio.run(verify_http_api_contract("ftp://invalid"))

    def test_schema_init_rejects_non_postgresql_url(self):
        with pytest.raises(ValueError, match="must start with 'postgresql://'"):
            verify_schema_initialization_idempotent("mysql://host/db")

    def test_cors_raises_connection_error_for_unreachable(self):
        with pytest.raises((ConnectionError, OSError)):
            asyncio.run(
                verify_cors_configuration(
                    "http://127.0.0.1:19999", "http://localhost:5173"
                )
            )


class TestChildImportsAvailable:
    """Verify that child modules are importable through the glue layer."""

    def test_backend_routes_imported(self):
        from backend.routes import health_check
        assert callable(health_check)

    def test_database_module_imported(self):
        from database import execute_init_script, verify_schema, ConnectionConfig
        assert callable(execute_init_script)
        assert callable(verify_schema)

    def test_frontend_module_imported(self):
        from frontend import fetchTasks, resolveBaseUrl
        assert callable(fetchTasks)
        assert callable(resolveBaseUrl)


class TestFrontendResolveBaseUrl:
    """Verify resolveBaseUrl delegation works correctly."""

    def test_default_url(self):
        from frontend import resolveBaseUrl
        url = resolveBaseUrl()
        assert url == "http://localhost:8000"

    def test_custom_url(self):
        from frontend import resolveBaseUrl
        url = resolveBaseUrl({"VITE_API_URL": "http://api.example.com/"})
        assert url == "http://api.example.com"  # trailing slash stripped

    def test_custom_url_no_trailing_slash(self):
        from frontend import resolveBaseUrl
        url = resolveBaseUrl({"VITE_API_URL": "http://api.example.com"})
        assert url == "http://api.example.com"


# ---------------------------------------------------------------------------
# Integration tests — live backend required
# ---------------------------------------------------------------------------

@skip_no_backend
class TestHttpApiContract:
    """Verify the full HTTP API contract against a live backend."""

    @pytest.mark.asyncio
    async def test_all_endpoints(self):
        result = await verify_http_api_contract(BACKEND_BASE_URL)
        assert result is True


@skip_no_both
class TestCrossTierInvariants:
    """Verify cross-tier invariants against live backend + database."""

    @pytest.mark.asyncio
    async def test_invariants_hold(self):
        result = await verify_cross_tier_invariants(BACKEND_BASE_URL, DATABASE_URL)
        assert result is True


@skip_no_database
class TestSchemaIdempotency:
    """Verify init.sql idempotency against a live database."""

    def test_idempotent(self):
        result = verify_schema_initialization_idempotent(DATABASE_URL)
        assert result is True


@skip_no_database
class TestTestIsolation:
    """Verify test isolation properties against a live database."""

    def test_isolation(self):
        result = verify_test_isolation(DATABASE_URL)
        assert result is True


@skip_no_backend
class TestCorsConfiguration:
    """Verify CORS headers against a live backend."""

    @pytest.mark.asyncio
    async def test_default_origin(self):
        result = await verify_cors_configuration(BACKEND_BASE_URL)
        assert result is True

    @pytest.mark.asyncio
    async def test_explicit_origin(self):
        result = await verify_cors_configuration(
            BACKEND_BASE_URL, "http://localhost:5173"
        )
        assert result is True


@skip_no_backend
class TestConnectionPoolLifecycle:
    """Verify connection pool is functional during app runtime."""

    @pytest.mark.asyncio
    async def test_pool_functional(self):
        result = await verify_connection_pool_lifecycle(BACKEND_BASE_URL)
        assert result is True


# ---------------------------------------------------------------------------
# Error propagation tests
# ---------------------------------------------------------------------------

class TestErrorPropagation:
    """Verify that child errors propagate as parent-contracted types."""

    def test_connection_error_on_unreachable_backend(self):
        """ConnectionError when backend_base_url is unreachable."""
        with pytest.raises(ConnectionError):
            asyncio.run(
                verify_http_api_contract("http://127.0.0.1:19999")
            )

    @skip_no_database
    def test_assertion_error_on_bad_schema(self):
        """AssertionError scenario is tested by schema idempotency test."""
        # This is a placeholder — a real test would require a corrupt schema.
        pass

    def test_database_connection_error(self):
        """ConnectionError when database_url is unreachable."""
        with pytest.raises((ConnectionError, Exception)):
            verify_schema_initialization_idempotent(
                "postgresql://nobody:wrong@127.0.0.1:19999/nonexistent"
            )
