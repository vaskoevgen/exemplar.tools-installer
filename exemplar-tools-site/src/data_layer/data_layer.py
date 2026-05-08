"""Data Constants & Convex Backend (data_layer) v1.

Provides the canonical typed registry of all 11 exemplar.tools tool definitions
and exposes Convex-compatible query/mutation functions for comments.

NOTE: Although the real implementation targets TypeScript, this Python module
provides the same logic so that the contract test suite can import and verify
all invariants.
"""

import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

_PACT_KEY = "PACT:16619e:data_layer"
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
# Error classes
# ---------------------------------------------------------------------------

class ConvexValidationError(Exception):
    """Raised when Convex argument validation fails."""
    pass


class ValidationError(Exception):
    """Raised when domain-level validation fails (e.g. empty author)."""
    pass


class ConvexInternalError(Exception):
    """Raised when Convex runtime encounters an internal failure."""
    pass


# ---------------------------------------------------------------------------
# Stub types referenced by the contract
# ---------------------------------------------------------------------------

class number:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass


class string:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass


# ---------------------------------------------------------------------------
# ToolSlug enum
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
# Data classes
# ---------------------------------------------------------------------------

class InstructionStep:
    """A single step-by-step instruction entry."""

    def __init__(self, title: str, bash: str):
        if not title or not isinstance(title, str):
            raise ValueError("InstructionStep.title must be a non-empty string")
        if not bash or not isinstance(bash, str):
            raise ValueError("InstructionStep.bash must be a non-empty string")
        self.title = title
        self.bash = bash

    def __repr__(self) -> str:
        return f"InstructionStep(title={self.title!r}, bash={self.bash!r})"


class ToolDef:
    """Complete static definition of one tool."""

    def __init__(
        self,
        slug: ToolSlug,
        name: str,
        description: str,
        step: int,
        version: str,
        accentColor: str,
        instructions: List[InstructionStep],
        videoUrl: Optional[str] = None,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        self.slug = slug
        self.name = name
        self.description = description
        self.step = step
        self.version = version
        self.accentColor = accentColor
        self.instructions = instructions
        self.videoUrl = videoUrl

    def __repr__(self) -> str:
        return f"ToolDef(slug={self.slug!r}, step={self.step})"


class Comment:
    """A user-submitted comment persisted in Convex."""

    def __init__(
        self,
        _id: str,
        page: str,
        author: str,
        body: str,
        createdAt: float,
        event_handler=None,
        log_handler=None,
    ):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)

        self._id = _id
        self.page = page
        self.author = author
        self.body = body
        self.createdAt = createdAt


class ListCommentsArgs:
    """Arguments for the Convex listComments query function."""

    def __init__(self, page: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.page = page


class AddCommentArgs:
    """Arguments for the Convex addComment mutation."""

    def __init__(self, page: str, author: str, body: str, event_handler=None, log_handler=None):
        self._emit = event_handler or (lambda event: None)
        self._log = log_handler or (lambda level, msg, ctx: None)
        self.page = page
        self.author = author
        self.body = body


# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

ToolDefArray = List[ToolDef]
CommentList = List[Comment]
OptionalVideoUrl = Optional[str]
InstructionStepList = List[InstructionStep]
ConvexDocumentId = str


# ---------------------------------------------------------------------------
# TOOLS constant — canonical registry of all 11 tool definitions
# ---------------------------------------------------------------------------

def _build_tools() -> List[ToolDef]:
    """Build the canonical TOOLS array sorted by step ascending."""
    return [
        ToolDef(
            slug=ToolSlug.constrain,
            name="Constrain",
            description="Define and enforce behavioral constraints for AI agents.",
            step=1,
            version="0.1.0",
            accentColor="#00e5ff",
            videoUrl="https://www.youtube.com/embed/constrain-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/constrain"),
                InstructionStep(title="Initialize configuration", bash="bunx constrain init"),
                InstructionStep(title="Define constraints", bash="bunx constrain add --rule no-exec"),
                InstructionStep(title="Run validation", bash="bunx constrain check"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.ledger,
            name="Ledger",
            description="Immutable append-only audit log for all agent actions.",
            step=2,
            version="0.1.0",
            accentColor="#00bfa5",
            videoUrl="https://www.youtube.com/embed/ledger-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/ledger"),
                InstructionStep(title="Initialize the ledger", bash="bunx ledger init"),
                InstructionStep(title="Record an entry", bash="bunx ledger record --event action_taken"),
                InstructionStep(title="Query the log", bash="bunx ledger query --last 10"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.pact,
            name="Pact",
            description="Behavioral contracts between cooperating AI agents.",
            step=3,
            version="0.1.0",
            accentColor="#69f0ae",
            videoUrl="https://www.youtube.com/embed/pact-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/pact"),
                InstructionStep(title="Create a pact", bash="bunx pact create --parties agentA agentB"),
                InstructionStep(title="Sign the pact", bash="bunx pact sign --id pact_001"),
                InstructionStep(title="Verify compliance", bash="bunx pact verify --id pact_001"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.advocate,
            name="Advocate",
            description="Represent user interests and mediate agent negotiations.",
            step=4,
            version="0.1.0",
            accentColor="#b2ff59",
            videoUrl="https://www.youtube.com/embed/advocate-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/advocate"),
                InstructionStep(title="Register an advocate", bash="bunx advocate register --user alice"),
                InstructionStep(title="Set preferences", bash="bunx advocate prefs --privacy high"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.arbiter,
            name="Arbiter",
            description="Resolve disputes and conflicts between competing agents.",
            step=5,
            version="0.1.0",
            accentColor="#ffd740",
            videoUrl="https://www.youtube.com/embed/arbiter-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/arbiter"),
                InstructionStep(title="Initialize arbiter", bash="bunx arbiter init"),
                InstructionStep(title="Submit a dispute", bash="bunx arbiter dispute --from agentA --to agentB"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.baton,
            name="Baton",
            description="Coordinate turn-taking and handoff between agents.",
            step=6,
            version="0.1.0",
            accentColor="#ff9100",
            videoUrl="https://www.youtube.com/embed/baton-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/baton"),
                InstructionStep(title="Create a relay", bash="bunx baton relay --agents agentA agentB"),
                InstructionStep(title="Pass the baton", bash="bunx baton pass --to agentB"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.sentinel,
            name="Sentinel",
            description="Monitor agent behavior and trigger alerts on anomalies.",
            step=7,
            version="0.1.0",
            accentColor="#ff5252",
            videoUrl="https://www.youtube.com/embed/sentinel-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/sentinel"),
                InstructionStep(title="Configure watchers", bash="bunx sentinel watch --target agentA"),
                InstructionStep(title="Set alert thresholds", bash="bunx sentinel alert --threshold high"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.chronicler,
            name="Chronicler",
            description="Generate structured narratives from agent activity logs.",
            step=8,
            version="0.1.0",
            accentColor="#ff4081",
            videoUrl="https://www.youtube.com/embed/chronicler-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/chronicler"),
                InstructionStep(title="Initialize chronicler", bash="bunx chronicler init"),
                InstructionStep(title="Generate a chronicle", bash="bunx chronicler generate --from ledger"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.stigmergy,
            name="Stigmergy",
            description="Enable indirect coordination through shared environment signals.",
            step=9,
            version="0.1.0",
            accentColor="#e040fb",
            videoUrl="https://www.youtube.com/embed/stigmergy-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/stigmergy"),
                InstructionStep(title="Create a signal space", bash="bunx stigmergy create --space shared_env"),
                InstructionStep(title="Emit a signal", bash="bunx stigmergy emit --signal task_complete"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.apprentice,
            name="Apprentice",
            description="Train and evaluate junior agents under senior supervision.",
            step=10,
            version="0.1.0",
            accentColor="#7c4dff",
            videoUrl="https://www.youtube.com/embed/apprentice-video",
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/apprentice"),
                InstructionStep(title="Assign a mentor", bash="bunx apprentice assign --mentor seniorAgent"),
                InstructionStep(title="Run training session", bash="bunx apprentice train --task classify"),
            ],
        ),
        ToolDef(
            slug=ToolSlug.kindex,
            name="Kindex",
            description="Knowledge index for discovering and connecting agent capabilities.",
            step=11,
            version="0.1.0",
            accentColor="#448aff",
            videoUrl=None,  # kindex has no video
            instructions=[
                InstructionStep(title="Install the package", bash="bun add @exemplar/kindex"),
                InstructionStep(title="Build the index", bash="bunx kindex build --source registry"),
                InstructionStep(title="Search capabilities", bash="bunx kindex search --query negotiation"),
            ],
        ),
    ]


TOOLS: List[ToolDef] = _build_tools()

# Runtime array of slug strings
TOOL_SLUGS: List[str] = [t.slug.value for t in TOOLS]


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def getTools() -> List[ToolDef]:
    """
    Returns the static TOOLS constant: a readonly array of all 11 ToolDef objects
    ordered by step number (1–11). Pure synchronous access to the in-memory tool registry.
    """
    _log("debug", "getTools invoked")
    return list(TOOLS)


def getToolBySlugs(slug: str) -> Optional[ToolDef]:
    """
    Utility lookup: finds a ToolDef by its slug from the TOOLS array.
    Returns None if the slug does not match any of the 11 known tools.
    """
    _log("debug", f"getToolBySlugs invoked with slug={slug!r}")
    if not slug or not isinstance(slug, str):
        return None
    for tool in TOOLS:
        if tool.slug.value == slug:
            return tool
    return None


# ---------------------------------------------------------------------------
# In-memory comment store (simulates Convex backend for Python tests)
# ---------------------------------------------------------------------------

_comments_store: List[Dict[str, Any]] = []


async def listComments(page: str = None, **kwargs) -> List[Dict[str, Any]]:
    """
    Convex query function (convex/comments.ts). Retrieves all comments for a
    given page slug from the 'comments' table.
    """
    _log("debug", f"listComments invoked with page={page!r}")

    if page is None or not isinstance(page, str):
        raise ConvexValidationError("Argument 'page' is required and must be a string.")

    result = [
        c for c in _comments_store
        if c["page"] == page
    ]
    result.sort(key=lambda c: c["createdAt"])
    return result


async def addComment(
    page: str = None,
    author: str = None,
    body: str = None,
    **kwargs,
) -> str:
    """
    Convex mutation function (convex/comments.ts). Inserts a new comment document.
    """
    _log("debug", f"addComment invoked with page={page!r}, author={author!r}")

    if page is None or not isinstance(page, str):
        raise ConvexValidationError("Argument 'page' is required and must be a string.")
    if author is None or not isinstance(author, str):
        raise ConvexValidationError("Argument 'author' is required and must be a string.")
    if body is None or not isinstance(body, str):
        raise ConvexValidationError("Argument 'body' is required and must be a string.")

    if not author.strip():
        raise ValidationError("Author name must not be empty.")
    if not body.strip():
        raise ValidationError("Comment body must not be empty.")

    doc_id = f"conv_{uuid.uuid4().hex[:16]}"
    now = time.time() * 1000  # epoch ms

    comment = {
        "_id": doc_id,
        "page": page,
        "author": author,
        "body": body,
        "createdAt": now,
    }
    _comments_store.append(comment)

    _log("debug", f"addComment completed, doc_id={doc_id}")
    return doc_id


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------

__all__ = [
    "ToolSlug",
    "InstructionStep",
    "ToolDef",
    "ToolDefArray",
    "Comment",
    "ListCommentsArgs",
    "AddCommentArgs",
    "CommentList",
    "OptionalVideoUrl",
    "InstructionStepList",
    "number",
    "string",
    "getTools",
    "getToolBySlugs",
    "listComments",
    "ConvexValidationError",
    "addComment",
    "ValidationError",
    "ConvexInternalError",
]
