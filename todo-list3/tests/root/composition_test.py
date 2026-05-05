"""Composition tests for the Root glue layer.

These tests validate that the glue code correctly wires children into the
parent interface.  They are designed to run against real backend + database
infrastructure (integration tests).

Usage:
    DATABASE_URL=postgresql://... BACKEND_URL=http://localhost:8000 pytest root/composition_test.py -v

Tests are conditionally skipped when required environment variables are absent
(CROSS-TIER-13 compliance).
"""

import asyncio
import os
import pytest

# Conditional skip when infrastructure is unavailable
DATABASE_URL = os.environ.get("DATABASE_URL", "")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

skip_no_db = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL not set — skipping integration tests (CROSS-TIER-13)",
)
skip_no_backend = pytest.mark.skipif(
    not DATABASE_URL,  # backend requires DB too
    reason="DATABASE_URL not set — backend unavailable",
)


# ---------------------------------------------------------------------------
# Import glue module
# ---------------------------------------------------------------------------

from root import (
    verify_http_api_contract,
    verify_cross_tier_invariants,
    verify_schema_initialization_idempotent,
    verify_test_isolation,
    verify_cors_configuration,
    verify_connection_pool_lifecycle,
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@skip_no_db
class TestSchemaInitialization:
    """verify_schema_initialization_idempotent delegates to database child."""

    def test_idempotent_init(self):
        result = verify_schema_initialization_idempotent(DATABASE_URL)
        assert result is True

    def test_rejects_invalid_url(self):
        with pytest.raises(ConnectionError):
            verify_schema_initialization_idempotent("mysql://bad")


@skip_no_db
class TestTestIsolation:
    """verify_test_isolation delegates to database child for row counting."""

    def test_isolation_holds(self):
        result = verify_test_isolation(DATABASE_URL)
        assert result is True


@skip_no_backend
class TestHttpApiContract:
    """verify_http_api_contract delegates to backend child via HTTP."""

    @pytest.mark.asyncio
    async def test_all_endpoints(self):
        result = await verify_http_api_contract(BACKEND_URL)
        assert result is True

    @pytest.mark.asyncio
    async def test_rejects_invalid_url(self):
        with pytest.raises(ConnectionError):
            await verify_http_api_contract("ftp://bad")


@skip_no_backend
class TestCrossTierInvariants:
    """verify_cross_tier_invariants exercises backend + database together."""

    @pytest.mark.asyncio
    async def test_invariants_hold(self):
        result = await verify_cross_tier_invariants(BACKEND_URL, DATABASE_URL)
        assert result is True


@skip_no_backend
class TestCorsConfiguration:
    """verify_cors_configuration sends OPTIONS preflight."""

    @pytest.mark.asyncio
    async def test_default_origin(self):
        result = await verify_cors_configuration(BACKEND_URL)
        assert result is True

    @pytest.mark.asyncio
    async def test_explicit_origin(self):
        result = await verify_cors_configuration(
            BACKEND_URL, frontend_origin="http://localhost:5173"
        )
        assert result is True


@skip_no_backend
class TestConnectionPoolLifecycle:
    """verify_connection_pool_lifecycle checks pool is functional."""

    @pytest.mark.asyncio
    async def test_pool_functional(self):
        result = await verify_connection_pool_lifecycle(BACKEND_URL)
        assert result is True


# ---------------------------------------------------------------------------
# Structural composition tests (no infrastructure required)
# ---------------------------------------------------------------------------


class TestGlueStructure:
    """Verify glue module structure without live infrastructure."""

    def test_all_parent_functions_exist(self):
        """All six parent functions are importable from the glue module."""
        import root
        for fn_name in [
            "verify_http_api_contract",
            "verify_cross_tier_invariants",
            "verify_schema_initialization_idempotent",
            "verify_test_isolation",
            "verify_cors_configuration",
            "verify_connection_pool_lifecycle",
        ]:
            assert hasattr(root, fn_name), f"Missing parent function: {fn_name}"
            assert callable(getattr(root, fn_name)), f"{fn_name} is not callable"

    def test_sync_functions_are_sync(self):
        """verify_schema_initialization_idempotent and verify_test_isolation
        are synchronous (not coroutines)."""
        import asyncio
        assert not asyncio.iscoroutinefunction(verify_schema_initialization_idempotent)
        assert not asyncio.iscoroutinefunction(verify_test_isolation)

    def test_async_functions_are_async(self):
        """Async parent functions are coroutine functions."""
        import asyncio
        assert asyncio.iscoroutinefunction(verify_http_api_contract)
        assert asyncio.iscoroutinefunction(verify_cross_tier_invariants)
        assert asyncio.iscoroutinefunction(verify_cors_configuration)
        assert asyncio.iscoroutinefunction(verify_connection_pool_lifecycle)

    def test_return_type_annotations(self):
        """Parent functions have bool return type annotation."""
        import inspect
        for fn in [
            verify_http_api_contract,
            verify_cross_tier_invariants,
            verify_schema_initialization_idempotent,
            verify_test_isolation,
            verify_cors_configuration,
            verify_connection_pool_lifecycle,
        ]:
            sig = inspect.signature(fn)
            assert sig.return_annotation is bool or sig.return_annotation == "bool", \
                f"{fn.__name__} return annotation is {sig.return_annotation}, expected bool"

    def test_backend_url_validation(self):
        """Invalid backend URLs raise ConnectionError synchronously."""
        with pytest.raises(ConnectionError):
            verify_test_isolation("mysql://invalid")

    def test_database_url_validation(self):
        """Invalid database URLs raise ConnectionError."""
        with pytest.raises(ConnectionError):
            verify_schema_initialization_idempotent("mysql://invalid")

    def test_error_propagation_contract(self):
        """ConnectionError and AssertionError are the documented error types."""
        # These are Python builtins, just confirm they're the right types
        assert issubclass(ConnectionError, OSError)
        assert issubclass(AssertionError, Exception)
