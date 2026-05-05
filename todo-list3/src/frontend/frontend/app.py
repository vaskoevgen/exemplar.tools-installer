import logging
import time
from typing import List, Optional, Any

from frontend.types import ApiError, TaskId
from frontend import api

_PACT_KEY = "PACT:1cf387:frontend"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


class App:
    """Simulates React App component state management."""

    def __init__(self, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.tasks: List[dict] = []
        self.error: Optional[ApiError] = None

    async def handleCreate(self, data: dict) -> None:
        """Creates task and prepends to local state."""
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleCreate",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        _log("info", "App.handleCreate invoked")
        try:
            created = await api.createTask(data)
            self.tasks = [created] + self.tasks
            self.error = None
        except ApiError as e:
            self.error = e
            raise
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleCreate",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    async def handleUpdate(self, id: TaskId, data: dict) -> None:
        """Updates task and replaces matching task in local state."""
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleUpdate",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        _log("info", "App.handleUpdate invoked")
        try:
            updated = await api.updateTask(id, data)
            self.tasks = [updated if t.get("id") == id else t for t in self.tasks]
            self.error = None
        except ApiError as e:
            self.error = e
            raise
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleUpdate",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    async def handleDelete(self, id: TaskId) -> None:
        """Deletes task and removes from local state immediately (AC19)."""
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleDelete",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        _log("info", "App.handleDelete invoked")
        try:
            await api.deleteTask(id)
            self.tasks = [t for t in self.tasks if t.get("id") != id]
            self.error = None
        except ApiError as e:
            self.error = e
            raise
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:handleDelete",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })

    async def useEffectFetchOnMount(self) -> None:
        """Fetches tasks on mount and populates local state."""
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:useEffectFetchOnMount",
            "event": "invoked",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
        _log("info", "App.useEffectFetchOnMount invoked")
        try:
            tasks = await api.fetchTasks()
            self.tasks = tasks
            self.error = None
        except ApiError as e:
            self.error = e
            raise
        self._emit({
            "pact_key": "PACT:1cf387:frontend:App:useEffectFetchOnMount",
            "event": "completed",
            "input_classification": [],
            "output_classification": [],
            "side_effects": [],
            "ts": time.time_ns(),
        })
