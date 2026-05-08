"""Tool Page & Comments Section (tool_page) v1 — Python implementation.

This module implements all types, functions, and behavioral contracts
defined in the tool_page interface contract. Although the contract describes
React/TypeScript components, the test suite validates the Python data layer:
enums, type guards, utility functions, data structures, and lookup maps.
"""

import logging
import math
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union

_PACT_KEY = "PACT:e03809:tool_page"
logger = logging.getLogger(__name__)


class PactFormatter(logging.Formatter):
    """Formatter that injects the PACT log key into every record."""

    def format(self, record):
        record.pact_key = _PACT_KEY
        return super().format(record)


def _log(level: str, msg: str, **kwargs) -> None:
    """Log with PACT key embedded for production traceability."""
    getattr(logger, level)(f"[{_PACT_KEY}] {msg}", **kwargs)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ToolSlug(Enum):
    """URL-safe identifier for each tool, used as route param and Convex page key."""
    constrain = "constrain"
    ledger = "ledger"
    pact = "pact"
    advocate = "advocate"
    arbiter = "arbiter"
    baton = "baton"
    sentinel = "sentinel"
    chronicler = "chronicler"
    stigmergy = "stigmergy"
    apprentice = "apprentice"
    kindex = "kindex"


# ---------------------------------------------------------------------------
# Primitive / branded types (Python representations)
# ---------------------------------------------------------------------------

# HexColor: CSS hex color string e.g. '#00e5ff'
HexColor = str

# StepNumber: Integer 1-11
StepNumber = int

# ReactElement: Opaque type in contract context
ReactElement = Any

# OptionalVideoUrl
OptionalVideoUrl = Optional[str]


class number:
    """Auto-stubbed type — referenced but not defined in contract 'tool_page'."""
    pass


class string:
    """Auto-stubbed type — referenced but not defined in contract 'tool_page'."""
    pass


# ---------------------------------------------------------------------------
# Error classes
# ---------------------------------------------------------------------------

class render_not_found_ui(Exception):
    """Raised/used when ToolPage encounters an invalid or missing slug."""
    pass


class validation_error(Exception):
    """Raised when CommentsSection form validation fails."""
    pass


class convex_mutation_error(Exception):
    """Raised when Convex addComment mutation fails."""
    pass


class convex_query_error(Exception):
    """Raised when Convex useQuery subscription fails."""
    pass


class invalid_argument(Exception):
    """Raised for invalid arguments to formatRelativeTime."""
    pass


class invariant_violation(Exception):
    """Raised when buildToolMap detects an invariant violation."""
    pass


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""

    def __init__(self, title: str, bash: str, **kwargs: Any) -> None:
        self.title = title
        self.bash = bash

    def __repr__(self) -> str:
        return f"InstructionStep(title={self.title!r}, bash={self.bash!r})"


# InstructionStepList type alias
InstructionStepList = List[InstructionStep]


class ToolDef:
    """Complete static definition of one tool including display metadata, instructions, and video URL."""

    def __init__(
        self,
        slug: str,
        name: str,
        description: str,
        step: int,
        version: str,
        accentColor: str,
        instructions: Any,
        videoUrl: Optional[str] = None,
        event_handler: Any = None,
        log_handler: Any = None,
        **kwargs: Any,
    ) -> None:
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.slug = slug
        self.name = name
        self.description = description
        self.step = step
        self.version = version
        self.accentColor = accentColor
        self.videoUrl = videoUrl
        # instructions can be list of dicts or list of InstructionStep
        if instructions and len(instructions) > 0 and isinstance(instructions[0], dict):
            self.instructions = [InstructionStep(**inst) for inst in instructions]
        else:
            self.instructions = instructions or []

    def __repr__(self) -> str:
        return f"ToolDef(slug={self.slug!r}, name={self.name!r})"


# ToolDefList type alias
ToolDefList = List[ToolDef]


class ToolMap:
    """Record<ToolSlug, ToolDef> — O(1) lookup map derived from ToolDefList."""

    def __init__(self, entries: Dict[str, Any], event_handler: Any = None, log_handler: Any = None) -> None:
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.entries = entries

    def __contains__(self, key: str) -> bool:
        return key in self.entries

    def __getitem__(self, key: str) -> Any:
        return self.entries[key]

    def __len__(self) -> int:
        return len(self.entries)

    def keys(self):
        return self.entries.keys()

    def items(self):
        return self.entries.items()

    def values(self):
        return self.entries.values()


class Comment:
    """A user-submitted comment persisted in Convex."""

    def __init__(
        self,
        _id: str,
        page: str,
        author: str,
        body: str,
        createdAt: float,
        event_handler: Any = None,
        log_handler: Any = None,
        **kwargs: Any,
    ) -> None:
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self._id = _id
        self.page = page
        self.author = author
        self.body = body
        self.createdAt = createdAt


# CommentList type alias
CommentList = List[Comment]


class ToolPageProps:
    """ToolPage receives no explicit props."""
    pass


class CommentsSectionProps:
    """Props interface for CommentsSection component."""

    def __init__(self, page: str, accentColor: str, **kwargs: Any) -> None:
        self.page = page
        self.accentColor = accentColor


class StepBadgeProps:
    """Props interface for StepBadge presentational component."""

    def __init__(self, step: int, accentColor: str, **kwargs: Any) -> None:
        self.step = step
        self.accentColor = accentColor


class VersionBadgeProps:
    """Props interface for VersionBadge presentational component."""

    def __init__(self, version: str, accentColor: str, **kwargs: Any) -> None:
        self.version = version
        self.accentColor = accentColor


class CodeBlockProps:
    """Props interface for CodeBlock presentational component."""

    def __init__(self, title: str, bash: str, **kwargs: Any) -> None:
        self.title = title
        self.bash = bash


class VideoEmbedProps:
    """Props interface for VideoEmbed presentational component."""

    def __init__(self, url: str, title: str = "Video tutorial", **kwargs: Any) -> None:
        self.url = url
        self.title = title


class CommentFormState:
    """Internal useState shape for the comment submission form."""

    def __init__(self, author: str = "", body: str = "", **kwargs: Any) -> None:
        self.author = author
        self.body = body


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

_TOOL_SLUG_VALUES = {slug.value for slug in ToolSlug}


def isToolSlug(value: str) -> bool:
    """Type guard: checks if an arbitrary string is a valid ToolSlug.

    Postconditions:
      - Returns True iff value is one of the known ToolSlug enum variant values.
    """
    _log("debug", f"isToolSlug called with value={value!r}")
    return value in _TOOL_SLUG_VALUES


def formatRelativeTime(createdAt: float) -> str:
    """Converts a millisecond epoch timestamp to a human-readable relative time string.

    Preconditions:
      - createdAt is a non-negative finite number (milliseconds since epoch).

    Postconditions:
      - Returns 'just now' for < 60s ago or future timestamps.
      - Returns '{n} minute(s) ago' for 1-59 minutes ago.
      - Returns '{n} hour(s) ago' for 1-23 hours ago.
      - Returns '{n} day(s) ago' for 1-30 days ago.
      - Returns formatted absolute date for > 30 days ago.
      - Returned string is always non-empty.

    Errors:
      - Raises invalid_argument for NaN input.
      - Raises invalid_argument for negative input.
    """
    _log("debug", f"formatRelativeTime called with createdAt={createdAt}")

    # Guard against NaN
    if isinstance(createdAt, float) and math.isnan(createdAt):
        raise invalid_argument("createdAt must not be NaN")

    # Guard against negative
    if createdAt < 0:
        raise invalid_argument("createdAt must be non-negative")

    now_ms = time.time() * 1000
    diff_ms = now_ms - createdAt

    # Future timestamps -> 'just now'
    if diff_ms < 0:
        return "just now"

    diff_seconds = diff_ms / 1000

    # < 60 seconds -> 'just now'
    if diff_seconds < 60:
        return "just now"

    diff_minutes = diff_seconds / 60
    # 1-59 minutes
    if diff_minutes < 60:
        n = int(diff_minutes)
        if n == 1:
            return "1 minute ago"
        return f"{n} minutes ago"

    diff_hours = diff_seconds / 3600
    # 1-23 hours
    if diff_hours < 24:
        n = int(diff_hours)
        if n == 1:
            return "1 hour ago"
        return f"{n} hours ago"

    diff_days = diff_seconds / 86400
    # 1-30 days (inclusive: use < 31 so that exactly 30 days returns "30 days ago")
    if diff_days < 31:
        n = int(diff_days)
        if n == 1:
            return "1 day ago"
        return f"{n} days ago"

    # > 30 days -> absolute date
    import datetime
    dt = datetime.datetime.fromtimestamp(createdAt / 1000, tz=datetime.timezone.utc)
    # Format as "Jan 15, 2024"
    month_abbr = dt.strftime("%b")
    day = dt.day
    year = dt.year
    return f"{month_abbr} {day}, {year}"


def buildToolMap(tools: List[Any], event_handler: Any = None, log_handler: Any = None) -> ToolMap:
    """Converts ToolDefList array into TOOL_MAP: Record<ToolSlug, ToolDef> for O(1) access.

    Preconditions:
      - tools array is non-empty.
      - All ToolDef.slug values in tools are unique.

    Postconditions:
      - Returned ToolMap contains exactly one entry per element in the input array.
      - Each key is a ToolSlug string, each value is the corresponding ToolDef.

    Errors:
      - Raises invariant_violation for empty tools array.
      - Raises invariant_violation for duplicate slugs.
    """
    _log("debug", f"buildToolMap called with {len(tools)} tools")

    if not tools:
        raise invariant_violation("Input tools array must not be empty")

    entries: Dict[str, Any] = {}
    for tool in tools:
        # Extract slug from tool (may be ToolDef, SimpleNamespace, or dict)
        slug: str
        if isinstance(tool, dict):
            slug = tool["slug"]
        else:
            slug = getattr(tool, "slug", None)
            if slug is None:
                raise invariant_violation(f"Tool missing 'slug' attribute: {tool}")

        if slug in entries:
            raise invariant_violation(f"Duplicate slug detected: {slug!r}")

        entries[slug] = tool

    return ToolMap(entries=entries, event_handler=event_handler, log_handler=log_handler)


# ---------------------------------------------------------------------------
# React component stubs (Python-side representations for contract compliance)
# These are callable stubs that return a representation of the rendered output.
# In the real TypeScript project, these are React functional components.
# ---------------------------------------------------------------------------

def ToolPage(event_handler: Any = None, log_handler: Any = None) -> Any:
    """Page-level React functional component stub.

    In TypeScript, extracts toolSlug from useParams, validates via isToolSlug,
    performs O(1) lookup from TOOL_MAP, and renders sub-components.
    """
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:ToolPage",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {"component": "ToolPage", "type": "react_element"}
    _emit({
        "pact_key": "PACT:e03809:tool_page:ToolPage",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def CommentsSection(
    page: str,
    accentColor: str,
    event_handler: Any = None,
    log_handler: Any = None,
) -> Any:
    """Stateful React functional component stub for comments."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:CommentsSection",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {"component": "CommentsSection", "page": page, "accentColor": accentColor}
    _emit({
        "pact_key": "PACT:e03809:tool_page:CommentsSection",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def StepBadge(
    step: int,
    accentColor: str,
    event_handler: Any = None,
    log_handler: Any = None,
) -> Any:
    """Pure presentational React functional component stub for StepBadge."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:StepBadge",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {"component": "StepBadge", "step": step, "accentColor": accentColor}
    _emit({
        "pact_key": "PACT:e03809:tool_page:StepBadge",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def VersionBadge(
    version: str,
    accentColor: str,
    event_handler: Any = None,
    log_handler: Any = None,
) -> Any:
    """Pure presentational React functional component stub for VersionBadge."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:VersionBadge",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    display_version = f"v{version}" if not version.startswith("v") else version
    result = {
        "component": "VersionBadge",
        "version": display_version,
        "accentColor": accentColor,
    }
    _emit({
        "pact_key": "PACT:e03809:tool_page:VersionBadge",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def CodeBlock(
    title: str,
    bash: str,
    event_handler: Any = None,
    log_handler: Any = None,
) -> Any:
    """Pure presentational React functional component stub for CodeBlock."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:CodeBlock",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {
        "component": "CodeBlock",
        "title": title,
        "bash": bash,
        "fontFamily": "'JetBrains Mono', monospace",
    }
    _emit({
        "pact_key": "PACT:e03809:tool_page:CodeBlock",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


def VideoEmbed(
    url: str,
    title: str = "Video tutorial",
    event_handler: Any = None,
    log_handler: Any = None,
) -> Any:
    """Pure presentational React functional component stub for VideoEmbed."""
    _emit = event_handler or (lambda event: None)
    _emit({
        "pact_key": "PACT:e03809:tool_page:VideoEmbed",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    result = {
        "component": "VideoEmbed",
        "url": url,
        "title": title,
    }
    _emit({
        "pact_key": "PACT:e03809:tool_page:VideoEmbed",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns(),
    })
    return result


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "ToolSlug",
    "InstructionStep",
    "InstructionStepList",
    "ToolDef",
    "ToolDefList",
    "ToolMap",
    "Comment",
    "CommentList",
    "ToolPageProps",
    "CommentsSectionProps",
    "StepBadgeProps",
    "VersionBadgeProps",
    "CodeBlockProps",
    "VideoEmbedProps",
    "CommentFormState",
    "OptionalVideoUrl",
    "number",
    "string",
    "ToolPage",
    "render_not_found_ui",
    "CommentsSection",
    "validation_error",
    "convex_mutation_error",
    "convex_query_error",
    "StepBadge",
    "VersionBadge",
    "CodeBlock",
    "VideoEmbed",
    "formatRelativeTime",
    "invalid_argument",
    "isToolSlug",
    "buildToolMap",
    "invariant_violation",
]
