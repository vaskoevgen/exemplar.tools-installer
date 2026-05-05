import logging
import time

_PACT_KEY = "PACT:3549b0:database"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


from database.types import (
    TaskStatus,
    TaskId,
    TaskTitle,
    TaskDescription,
    Timestamptz,
    TaskRow,
    ConnectionConfig,
    InitScriptResult,
)
from database.errors import (
    ConnectionError,
    AuthenticationError,
    DatabaseNotFoundError,
    SQLSyntaxError,
)
from database.schema import (
    execute_init_script,
    verify_schema,
)

__all__ = [
    'TaskStatus',
    'TaskId',
    'TaskTitle',
    'TaskDescription',
    'TaskRow',
    'ConnectionConfig',
    'InitScriptResult',
    'execute_init_script',
    'verify_schema',
    'ConnectionError',
    'AuthenticationError',
    'DatabaseNotFoundError',
    'SQLSyntaxError',
]
