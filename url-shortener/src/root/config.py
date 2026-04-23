import logging
import os
from dataclasses import dataclass
from typing import Optional

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


@dataclass
class AppConfig:
    """Application-level configuration read from environment variables."""
    database_url: str
    base_url: str
    max_code_retries: int

    def __init__(self, database_url: str, base_url: str = "http://localhost:8000",
                 max_code_retries: int = 5, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log_handler = log_handler or (lambda level, msg, ctx: None)
        self.database_url = database_url
        self.base_url = base_url
        self.max_code_retries = max_code_retries


_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """
    Returns the application configuration singleton. Reads DATABASE_URL from
    environment on first call, caches the result for subsequent calls.
    Raises RuntimeError if DATABASE_URL is not set or is empty.
    """
    global _config
    if _config is not None:
        return _config

    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        _log("error", "DATABASE_URL environment variable is required but not set.")
        raise RuntimeError("DATABASE_URL environment variable is required but not set.")

    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
    max_retries = int(os.environ.get("MAX_CODE_RETRIES", "5"))

    _config = AppConfig(
        database_url=database_url,
        base_url=base_url,
        max_code_retries=max_retries,
    )
    _log("info", f"Configuration loaded. base_url={base_url}")
    return _config
