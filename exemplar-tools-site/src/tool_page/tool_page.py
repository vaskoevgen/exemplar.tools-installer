import logging
import math
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

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
# Enum: ToolSlug
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
# Primitive types
# ---------------------------------------------------------------------------

# HexColor: CSS hex color string (e.g. '#00e5ff')
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
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""
    title: str
    bash: str


InstructionStepList = List[InstructionStep]


@dataclass
class ToolDef:
    """Complete static definition of one tool including display metadata, instructions, and video URL."""
    slug: str
    name: str
    description: str
    step: int
    version: str
    accentColor: str
    instructions: Any  # list of InstructionStep or dicts
    videoUrl: Optional[str] = None


ToolDefList = List[ToolDef]


@dataclass
class ToolMap:
    """Record<ToolSlug, ToolDef> — O(1) lookup map derived from ToolDefList at module load time."""
    entries: Dict[str, ToolDef]

    def __getitem__(self, key):
        return self.entries[key]

    def __contains__(self, key):
        return key in self.entries

    def __len__(self):
        return len(self.entries)

    def keys(self):
        return self.entries.keys()

    def values(self):
        return self.entries.values()

    def items(self):
        return self.entries.items()


@dataclass
class Comment:
    """A user-submitted comment persisted in Convex."""
    _id: str
    page: str  # ToolSlug string
    author: str
    body: str
    createdAt: float

    def __post_init__(self):
        if not (1 <= len(self.author) <= 100):
            raise ValueError(f"Comment author length must be 1-100, got {len(self.author)}")
        if not (1 <= len(self.body) <= 2000):
            raise ValueError(f"Comment body length must be 1-2000, got {len(self.body)}")


CommentList = List[Comment]


@dataclass
class ToolPageProps:
    """ToolPage receives no explicit props; it extracts toolSlug from React Router useParams internally."""
    pass


@dataclass
class CommentsSectionProps:
    """Props interface for CommentsSection component."""
    page: str  # ToolSlug
    accentColor: str  # HexColor


@dataclass
class StepBadgeProps:
    """Props interface for StepBadge presentational component."""
    step: int  # StepNumber
    accentColor: str  # HexColor


@dataclass
class VersionBadgeProps:
    """Props interface for VersionBadge presentational component."""
    version: str
    accentColor: str  # HexColor


@dataclass
class CodeBlockProps:
    """Props interface for CodeBlock presentational component."""
    title: str
    bash: str


@dataclass
class VideoEmbedProps:
    """Props interface for VideoEmbed presentational component."""
    url: str
    title: str = "Video tutorial"


@dataclass
class CommentFormState:
    """Internal useState shape for the comment submission form in CommentsSection."""
    author: str
    body: str


# ---------------------------------------------------------------------------
# Error sentinel classes
# ---------------------------------------------------------------------------

class render_not_found_ui(Exception):
    """Raised/used when ToolPage encounters an invalid or missing tool slug."""
    pass


class validation_error(Exception):
    """Raised when CommentsSection form validation fails (empty author or body)."""
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
    """Raised when buildToolMap detects a contract invariant violation."""
    pass


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

_VALID_TOOL_SLUGS = frozenset(member.value for member in ToolSlug)


def isToolSlug(value: str) -> bool:
    """
    Type guard utility function. Checks if an arbitrary string is a valid ToolSlug
    by testing membership in the set of known slug values.

    Postconditions:
      - Returns true if and only if value is one of the known ToolSlug enum variants.
    """
    _log("debug", f"isToolSlug called with value={value!r}")
    return isinstance(value, str) and value in _VALID_TOOL_SLUGS


def buildToolMap(tools: List[Any]) -> ToolMap:
    """
    Derived lookup map factory. Converts ToolDefList array into TOOL_MAP: Record<ToolSlug, ToolDef>
    for O(1) access.

    Preconditions:
      - tools array is non-empty
      - All ToolDef.slug values in tools are unique

    Postconditions:
      - Returned map contains exactly one entry per element in the input array.
    """
    _log("debug", f"buildToolMap called with {len(tools)} tools")

    if not tools:
        raise invariant_violation("Input tools array is empty")

    entries: Dict[str, Any] = {}
    for tool in tools:
        slug = getattr(tool, "slug", None)
        if slug is None and isinstance(tool, dict):
            slug = tool.get("slug")
        if slug is None:
            raise invariant_violation("ToolDef missing slug field")

        if slug in entries:
            raise invariant_violation(f"Duplicate slug: {slug}")

        entries[slug] = tool

    result = ToolMap(entries=entries)
    _log("debug", f"buildToolMap completed with {len(entries)} entries")
    return result


def formatRelativeTime(createdAt: float) -> str:
    """
    Pure utility function. Converts a timestamp (milliseconds since epoch) to a
    human-readable relative time string.

    Preconditions:
      - createdAt is a non-negative finite number representing milliseconds since Unix epoch.

    Postconditions:
      - Returns 'just now' for timestamps less than 60 seconds ago.
      - Returns '{n} minute(s) ago' for timestamps 1-59 minutes ago.
      - Returns '{n} hour(s) ago' for timestamps 1-23 hours ago.
      - Returns '{n} day(s) ago' for timestamps 1-30 days ago.
      - Returns formatted absolute date for timestamps older than 30 days.
      - Returned string is always non-empty.
    """
    _log("debug", f"formatRelativeTime called with createdAt={createdAt}")

    # Guard against NaN
    if isinstance(createdAt, float) and math.isnan(createdAt):
        raise invalid_argument("createdAt is NaN")

    # Guard against negative
    if createdAt < 0:
        raise invalid_argument(f"createdAt is negative: {createdAt}")

    now_ms = time.time() * 1000
    diff_ms = now_ms - createdAt

    # Future timestamps -> 'just now'
    if diff_ms < 0:
        return "just now"

    diff_seconds = diff_ms / 1000
    diff_minutes = diff_seconds / 60
    diff_hours = diff_minutes / 60
    diff_days = diff_hours / 24

    if diff_seconds < 60:
        return "just now"
    elif diff_minutes < 60:
        n = int(diff_minutes)
        if n == 1:
            return "1 minute ago"
        return f"{n} minutes ago"
    elif diff_hours < 24:
        n = int(diff_hours)
        if n == 1:
            return "1 hour ago"
        return f"{n} hours ago"
    elif diff_days < 31:
        n = round(diff_days)
        if n < 1:
            n = 1
        if n == 1:
            return "1 day ago"
        return f"{n} days ago"
    else:
        # Absolute date format: e.g. 'Jan 15, 2024'
        import datetime
        dt = datetime.datetime.fromtimestamp(createdAt / 1000, tz=datetime.timezone.utc)
        # Format as 'Mon DD, YYYY' e.g. 'Jan 15, 2024'
        month_abbr = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        formatted = f"{month_abbr[dt.month - 1]} {dt.day}, {dt.year}"
        return formatted


# ---------------------------------------------------------------------------
# React component stubs (Python-side representations)
# These are callable functions that return a dict representing the
# rendered output, since we're in a Python test context.
# ---------------------------------------------------------------------------

def ToolPage(event_handler=None, log_handler=None) -> Any:
    """
    Page-level React functional component. Extracts toolSlug from useParams,
    validates via isToolSlug type guard, performs O(1) lookup from TOOL_MAP.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:ToolPage",
        "event": "invoked",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    result = {"type": "ToolPage", "rendered": True}

    _emit({
        "pact_key": "PACT:e03809:tool_page:ToolPage",
        "event": "completed",
        "input_classification": [],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


def CommentsSection(
    page: str,
    accentColor: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Stateful React functional component. Accepts page (ToolSlug) and accentColor props.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:CommentsSection",
        "event": "invoked",
        "input_classification": [page, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    result = {"type": "CommentsSection", "page": page, "accentColor": accentColor}

    _emit({
        "pact_key": "PACT:e03809:tool_page:CommentsSection",
        "event": "completed",
        "input_classification": [page, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


def StepBadge(
    step: int,
    accentColor: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Pure presentational React functional component. Renders a styled pill
    displaying the step number with background color derived from accentColor.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:StepBadge",
        "event": "invoked",
        "input_classification": [step, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    result = {
        "type": "StepBadge",
        "step": step,
        "accentColor": accentColor,
        "text": str(step),
    }

    _emit({
        "pact_key": "PACT:e03809:tool_page:StepBadge",
        "event": "completed",
        "input_classification": [step, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


def VersionBadge(
    version: str,
    accentColor: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Pure presentational React functional component. Renders a version string
    in a pill badge with border and text color derived from accentColor.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:VersionBadge",
        "event": "invoked",
        "input_classification": [version, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    display_version = version if version.startswith("v") else f"v{version}"

    result = {
        "type": "VersionBadge",
        "version": display_version,
        "accentColor": accentColor,
    }

    _emit({
        "pact_key": "PACT:e03809:tool_page:VersionBadge",
        "event": "completed",
        "input_classification": [version, accentColor],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


def CodeBlock(
    title: str,
    bash: str,
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Pure presentational React functional component. Renders a dark terminal card
    with a title bar and a pre > code block with bash content styled in JetBrains Mono.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:CodeBlock",
        "event": "invoked",
        "input_classification": [title, bash],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    result = {
        "type": "CodeBlock",
        "title": title,
        "bash": bash,
        "fontFamily": "'JetBrains Mono', monospace",
    }

    _emit({
        "pact_key": "PACT:e03809:tool_page:CodeBlock",
        "event": "completed",
        "input_classification": [title, bash],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


def VideoEmbed(
    url: str,
    title: str = "Video tutorial",
    event_handler=None,
    log_handler=None,
) -> Any:
    """
    Pure presentational React functional component. Renders a responsive 16:9
    YouTube iframe embed.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit({
        "pact_key": "PACT:e03809:tool_page:VideoEmbed",
        "event": "invoked",
        "input_classification": [url, title],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    result = {
        "type": "VideoEmbed",
        "url": url,
        "title": title,
    }

    _emit({
        "pact_key": "PACT:e03809:tool_page:VideoEmbed",
        "event": "completed",
        "input_classification": [url, title],
        "output_classification": [],
        "side_effects": [],
        "ts": time.time_ns()
    })

    return result


# ---------------------------------------------------------------------------
# Module exports
# ---------------------------------------------------------------------------

__all__ = [
    'ToolSlug',
    'InstructionStep',
    'InstructionStepList',
    'ToolDef',
    'ToolDefList',
    'ToolMap',
    'Comment',
    'CommentList',
    'ToolPageProps',
    'CommentsSectionProps',
    'StepBadgeProps',
    'VersionBadgeProps',
    'CodeBlockProps',
    'VideoEmbedProps',
    'CommentFormState',
    'OptionalVideoUrl',
    'number',
    'string',
    'ToolPage',
    'render_not_found_ui',
    'CommentsSection',
    'validation_error',
    'convex_mutation_error',
    'convex_query_error',
    'StepBadge',
    'VersionBadge',
    'CodeBlock',
    'VideoEmbed',
    'formatRelativeTime',
    'invalid_argument',
    'isToolSlug',
    'buildToolMap',
    'invariant_violation',
]
