"""Data Constants & Convex Backend (data_layer) v1.

Provides the canonical typed registry of all 11 exemplar.tools tool definitions
and simulated Convex backend functions for comments.
"""

import logging
import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

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

class ConvexValidationError(ValueError):
    """Raised when Convex argument validation fails."""
    pass


class ValidationError(ValueError):
    """Raised when domain validation fails (e.g. empty author after trim)."""
    pass


class ConvexInternalError(RuntimeError):
    """Raised when Convex runtime encounters an internal failure."""
    pass


# ---------------------------------------------------------------------------
# Stub types referenced in contract
# ---------------------------------------------------------------------------

class number:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass


class string:
    """Auto-stubbed type — referenced but not defined in contract 'data_layer'"""
    pass


# ---------------------------------------------------------------------------
# Enum & Data Classes
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


@dataclass(frozen=True)
class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""
    title: str
    bash: str

    def __post_init__(self):
        if not isinstance(self.title, str) or not self.title:
            raise ValidationError("InstructionStep.title must be a non-empty string")
        if not isinstance(self.bash, str) or not self.bash:
            raise ValidationError("InstructionStep.bash must be a non-empty string")


@dataclass(frozen=True)
class ToolDef:
    """Complete static definition of one tool including display metadata, instructions, and video URL."""
    slug: ToolSlug
    name: str
    description: str
    step: int  # StepNumber 1–11
    version: str
    accentColor: str  # HexColor
    instructions: List[InstructionStep]
    videoUrl: Optional[str] = None  # OptionalVideoUrl


@dataclass
class Comment:
    """A user-submitted comment persisted in Convex."""
    _id: str
    page: str
    author: str
    body: str
    createdAt: float


@dataclass
class ListCommentsArgs:
    """Arguments for the Convex listComments query function."""
    page: str


@dataclass
class AddCommentArgs:
    """Arguments for the Convex addComment mutation."""
    page: str
    author: str
    body: str


# Type aliases
ToolDefArray = List[ToolDef]
CommentList = List[Comment]
OptionalVideoUrl = Optional[str]
InstructionStepList = List[InstructionStep]


# ---------------------------------------------------------------------------
# Canonical TOOLS constant
# ---------------------------------------------------------------------------

_TOOLS: ToolDefArray = [
    ToolDef(
        slug=ToolSlug.constrain,
        name="Constrain",
        description="Define and enforce behavioral constraints for AI agents.",
        step=1,
        version="0.1.0",
        accentColor="#00e5ff",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Constrain", bash="bun add @exemplar/constrain"),
            InstructionStep(title="Initialize configuration", bash="bunx constrain init"),
            InstructionStep(title="Define constraints", bash="bunx constrain add --rule 'no-hallucination'"),
            InstructionStep(title="Run validation", bash="bunx constrain validate"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.ledger,
        name="Ledger",
        description="Immutable append-only log for agent actions and decisions.",
        step=2,
        version="0.1.0",
        accentColor="#00bfa5",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Ledger", bash="bun add @exemplar/ledger"),
            InstructionStep(title="Initialize ledger store", bash="bunx ledger init"),
            InstructionStep(title="Record an entry", bash="bunx ledger record --action 'tool_call'"),
            InstructionStep(title="Query entries", bash="bunx ledger query --last 10"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.pact,
        name="Pact",
        description="Typed contracts between components with runtime verification.",
        step=3,
        version="0.1.0",
        accentColor="#69f0ae",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Pact", bash="bun add @exemplar/pact"),
            InstructionStep(title="Generate contract stubs", bash="bunx pact generate --component auth"),
            InstructionStep(title="Implement contract", bash="bunx pact implement --component auth"),
            InstructionStep(title="Verify contracts", bash="bunx pact verify"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.advocate,
        name="Advocate",
        description="Adversarial review agent that challenges proposed plans.",
        step=4,
        version="0.1.0",
        accentColor="#b2ff59",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Advocate", bash="bun add @exemplar/advocate"),
            InstructionStep(title="Configure review rules", bash="bunx advocate config --strict"),
            InstructionStep(title="Submit plan for review", bash="bunx advocate review --plan plan.yaml"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.arbiter,
        name="Arbiter",
        description="Conflict resolution engine for multi-agent disagreements.",
        step=5,
        version="0.1.0",
        accentColor="#ffd740",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Arbiter", bash="bun add @exemplar/arbiter"),
            InstructionStep(title="Register agents", bash="bunx arbiter register --agents a1,a2"),
            InstructionStep(title="Submit dispute", bash="bunx arbiter dispute --topic allocation"),
            InstructionStep(title="Resolve conflict", bash="bunx arbiter resolve"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.baton,
        name="Baton",
        description="Task handoff protocol for sequential agent workflows.",
        step=6,
        version="0.1.0",
        accentColor="#ff9100",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Baton", bash="bun add @exemplar/baton"),
            InstructionStep(title="Define workflow", bash="bunx baton workflow --steps 3"),
            InstructionStep(title="Pass baton", bash="bunx baton pass --to agent-b"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.sentinel,
        name="Sentinel",
        description="Real-time monitoring and alerting for agent health.",
        step=7,
        version="0.1.0",
        accentColor="#ff5252",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Sentinel", bash="bun add @exemplar/sentinel"),
            InstructionStep(title="Configure alerts", bash="bunx sentinel alerts --threshold 0.95"),
            InstructionStep(title="Start monitoring", bash="bunx sentinel watch"),
            InstructionStep(title="View dashboard", bash="bunx sentinel dashboard --port 3001"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.chronicler,
        name="Chronicler",
        description="Structured narrative generation from agent activity logs.",
        step=8,
        version="0.1.0",
        accentColor="#ff4081",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Chronicler", bash="bun add @exemplar/chronicler"),
            InstructionStep(title="Ingest logs", bash="bunx chronicler ingest --source ledger"),
            InstructionStep(title="Generate narrative", bash="bunx chronicler narrate --format markdown"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.stigmergy,
        name="Stigmergy",
        description="Indirect coordination through shared environment signals.",
        step=9,
        version="0.1.0",
        accentColor="#e040fb",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Stigmergy", bash="bun add @exemplar/stigmergy"),
            InstructionStep(title="Create signal space", bash="bunx stigmergy space --name shared-env"),
            InstructionStep(title="Emit signal", bash="bunx stigmergy emit --type pheromone --value 0.8"),
            InstructionStep(title="Read signals", bash="bunx stigmergy read --space shared-env"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.apprentice,
        name="Apprentice",
        description="Learning agent that improves through observation and feedback.",
        step=10,
        version="0.1.0",
        accentColor="#7c4dff",
        videoUrl="https://www.youtube.com/embed/dQw4w9WgXcQ",
        instructions=[
            InstructionStep(title="Install Apprentice", bash="bun add @exemplar/apprentice"),
            InstructionStep(title="Configure mentor", bash="bunx apprentice mentor --agent expert-1"),
            InstructionStep(title="Start learning session", bash="bunx apprentice learn --episodes 100"),
        ],
    ),
    ToolDef(
        slug=ToolSlug.kindex,
        name="Kindex",
        description="Knowledge index for cross-agent semantic search and retrieval.",
        step=11,
        version="0.1.0",
        accentColor="#448aff",
        videoUrl=None,  # kindex has no video
        instructions=[
            InstructionStep(title="Install Kindex", bash="bun add @exemplar/kindex"),
            InstructionStep(title="Build index", bash="bunx kindex build --source ./docs"),
            InstructionStep(title="Query index", bash="bunx kindex search --query 'agent coordination'"),
        ],
    ),
]

# Pre-build slug lookup map
_TOOLS_BY_SLUG: Dict[str, ToolDef] = {t.slug.value: t for t in _TOOLS}

# ---------------------------------------------------------------------------
# In-memory comment store (simulates Convex backend)
# ---------------------------------------------------------------------------

_comments_store: List[Dict[str, Any]] = []


# ---------------------------------------------------------------------------
# PACT event emission helper
# ---------------------------------------------------------------------------

def _make_event(method: str, event_type: str, **extra) -> dict:
    return {
        "pact_key": f"PACT:16619e:data_layer:{method}",
        "event": event_type,
        "input_classification": extra.get("input_classification", []),
        "output_classification": extra.get("output_classification", []),
        "side_effects": extra.get("side_effects", []),
        "ts": time.time_ns(),
    }


# ---------------------------------------------------------------------------
# Public API functions
# ---------------------------------------------------------------------------

def getTools(
    event_handler=None,
    log_handler=None,
) -> ToolDefArray:
    """
    Returns the static TOOLS constant: a readonly array of all 11 ToolDef objects
    ordered by step number (1–11). Pure synchronous access.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit(_make_event("getTools", "invoked"))
    _log("debug", "getTools invoked")

    result = list(_TOOLS)

    _emit(_make_event("getTools", "completed",
                      output_classification=["ToolDefArray"]))
    return result


def getToolBySlugs(
    slug: str,
    event_handler=None,
    log_handler=None,
) -> Optional[ToolDef]:
    """
    Utility lookup: finds a ToolDef by its slug from the TOOLS array.
    Returns None if the slug does not match any of the 11 known tools.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit(_make_event("getToolBySlugs", "invoked",
                      input_classification=["slug"]))
    _log("debug", f"getToolBySlugs invoked with slug={slug}")

    result = _TOOLS_BY_SLUG.get(slug, None)

    _emit(_make_event("getToolBySlugs", "completed",
                      output_classification=["ToolDef|None"]))
    return result


async def listComments(
    page: str,
    event_handler=None,
    log_handler=None,
) -> List[Dict[str, Any]]:
    """
    Convex query function (convex/comments.ts). Retrieves all comments for a
    given page slug, sorted by createdAt ascending.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit(_make_event("listComments", "invoked",
                      input_classification=["page"]))
    _log("debug", f"listComments invoked with page={page}")

    if not isinstance(page, str) or not page:
        raise ConvexValidationError(
            "Argument 'page' is required and must be a string."
        )

    filtered = [
        c for c in _comments_store if c["page"] == page
    ]
    filtered.sort(key=lambda c: c["createdAt"])

    _emit(_make_event("listComments", "completed",
                      output_classification=["CommentList"]))
    return filtered


async def addComment(
    page: str = None,
    author: str = None,
    body: str = None,
    event_handler=None,
    log_handler=None,
) -> str:
    """
    Convex mutation function (convex/comments.ts). Inserts a new comment
    document and returns the generated document ID.
    """
    _emit = event_handler or (lambda event: None)
    _log_h = log_handler or (lambda level, msg, ctx: None)

    _emit(_make_event("addComment", "invoked",
                      input_classification=["page", "author", "body"]))
    _log("debug", f"addComment invoked with page={page}, author={author}")

    # Validate page
    if page is None or not isinstance(page, str):
        raise ConvexValidationError(
            "Argument 'page' is required and must be a string."
        )

    # Validate author
    if author is None or not isinstance(author, str):
        raise ConvexValidationError(
            "Argument 'author' is required and must be a string."
        )

    # Validate body
    if body is None or not isinstance(body, str):
        raise ConvexValidationError(
            "Argument 'body' is required and must be a string."
        )

    # Domain validation: non-empty after trim
    trimmed_author = author.strip()
    if not trimmed_author:
        raise ValidationError("Author name must not be empty.")

    trimmed_body = body.strip()
    if not trimmed_body:
        raise ValidationError("Comment body must not be empty.")

    # Length validation
    if len(trimmed_author) > 100:
        raise ValidationError("Author name must not exceed 100 characters.")

    if len(trimmed_body) > 5000:
        raise ValidationError("Comment body must not exceed 5000 characters.")

    # Insert
    doc_id = str(uuid.uuid4())
    created_at = time.time() * 1000  # epoch millis, server-side

    comment_doc = {
        "_id": doc_id,
        "page": page,
        "author": trimmed_author,
        "body": trimmed_body,
        "createdAt": created_at,
    }
    _comments_store.append(comment_doc)

    _emit(_make_event("addComment", "completed",
                      output_classification=["ConvexDocumentId"],
                      side_effects=["insert:comments"]))
    _log("info", f"addComment completed, id={doc_id}")
    return doc_id


# ConvexDocumentId is just a str alias for the Python side
ConvexDocumentId = str


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------
__all__ = [
    'ToolSlug',
    'InstructionStep',
    'ToolDef',
    'ToolDefArray',
    'Comment',
    'ListCommentsArgs',
    'AddCommentArgs',
    'CommentList',
    'OptionalVideoUrl',
    'InstructionStepList',
    'number',
    'string',
    'getTools',
    'getToolBySlugs',
    'listComments',
    'ConvexValidationError',
    'addComment',
    'ValidationError',
    'ConvexInternalError',
]
