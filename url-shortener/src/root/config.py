import logging
import os

_PACT_KEY = "PACT:481349:root"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


def get_database_url() -> str:
    """
    Reads DATABASE_URL from os.environ and returns it.
    Raises KeyError if the variable is not set.
    """
    _log("debug", "get_database_url invoked")
    try:
        url = os.environ["DATABASE_URL"]
    except KeyError:
        _log("error", "DATABASE_URL environment variable is not set")
        raise KeyError("DATABASE_URL environment variable is not set")
    if not url:
        raise KeyError("DATABASE_URL environment variable is not set")
    _log("debug", "get_database_url completed")
    return url
