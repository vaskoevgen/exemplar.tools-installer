"""Conftest to reset the in-memory store between async test classes."""
import pytest

@pytest.fixture(autouse=True)
def _reset_store():
    """Clear the in-memory task store before each test."""
    from root import _store
    _store.clear()
    yield
    _store.clear()
