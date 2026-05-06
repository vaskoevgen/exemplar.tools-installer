"""Home Page component module.

Route-level page component rendered at '/'. Composes three vertical sections:
(a) workflow overview prose paragraph,
(b) quick-start HTML table listing all 11 tools,
(c) ClosedLoopDiagram SVG component arranging tools in a circular flow.

Includes ClosedLoopDiagram as a co-located presentational component and four
exported projection functions for mapping ToolDef records to view-model types.
"""
import logging
import math
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, List, Optional

_PACT_KEY = "PACT:1c0533:home_page"
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

class RangeError(Exception):
    """Raised when a value is outside its valid range."""
    pass


class RenderError(Exception):
    """Raised when a component cannot render due to invalid props."""
    pass


# ---------------------------------------------------------------------------
# Canonical domain types (would be imported from type_registry in production)
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


# Primitive type aliases
StepNumber = int  # Integer 1-11
HexColor = str    # CSS hex color string e.g. '#00e5ff'
OptionalVideoUrl = Optional[str]
string = str


@dataclass
class InstructionStep:
    """A single step-by-step instruction entry."""
    title: str
    bash: str


InstructionStepList = List[InstructionStep]


@dataclass
class ToolDef:
    """Complete static definition of one tool."""
    slug: str
    name: str
    description: str
    step: int
    version: str
    accentColor: str
    instructions: Any = field(default_factory=list)
    videoUrl: Optional[str] = None


ToolDefList = List[ToolDef]


# ---------------------------------------------------------------------------
# View-model types
# ---------------------------------------------------------------------------

@dataclass
class QuickStartRow:
    """One row in the HomePage quick-start table, projected from ToolDef."""
    step: int
    slug: str
    name: str
    description: str
    accentColor: str


@dataclass
class DiagramNode:
    """Data for one node in the ClosedLoopDiagram SVG, projected from ToolDef."""
    slug: str
    name: str
    step: int
    accentColor: str


DiagramNodeList = List[DiagramNode]
QuickStartRowList = List[QuickStartRow]


@dataclass
class ClosedLoopDiagramProps:
    """Props interface for the ClosedLoopDiagram React component."""
    nodes: DiagramNodeList


@dataclass
class HomePageProps:
    """Props interface for the HomePage route-level component. Empty by design."""
    pass


@dataclass
class CircularLayoutPoint:
    """Computed (x, y) position within the SVG viewBox for a single diagram node."""
    x: float
    y: float


@dataclass
class SVGViewBoxSpec:
    """Constants defining the SVG coordinate system for the diagram."""
    width: int
    height: int
    centerX: float
    centerY: float
    radius: float


class ReactElement:
    """Auto-stubbed type — referenced but not defined in contract 'home_page'."""
    pass


# ---------------------------------------------------------------------------
# Helper: attribute-or-dict access
# ---------------------------------------------------------------------------

def _getattr_or_item(obj: Any, key: str) -> Any:
    """Retrieve a field from either a dict or an object with attributes."""
    if obj is None:
        raise AttributeError(f"Cannot get '{key}' from None")
    if isinstance(obj, dict):
        if key not in obj:
            raise KeyError(key)
        return obj[key]
    if not hasattr(obj, key):
        raise AttributeError(f"Object has no attribute '{key}'")
    return getattr(obj, key)


def _has_field(obj: Any, key: str) -> bool:
    """Check if a field exists on a dict or object."""
    if obj is None:
        return False
    if isinstance(obj, dict):
        return key in obj
    return hasattr(obj, key)


# ---------------------------------------------------------------------------
# Projection functions
# ---------------------------------------------------------------------------

def toQuickStartRow(
    tool: Any,
) -> QuickStartRow:
    """
    Pure projection function. Extracts the fields required by the quick-start
    table from a single ToolDef record. Returns a QuickStartRow view-model.
    """
    _log("debug", "toQuickStartRow invoked")

    if tool is None:
        raise TypeError(
            "invalid_tool_def: toQuickStartRow requires a valid ToolDef with "
            "step, slug, name, description, and accentColor."
        )

    required_fields = ("step", "slug", "name", "description", "accentColor")
    for f in required_fields:
        if not _has_field(tool, f):
            raise TypeError(
                "invalid_tool_def: toQuickStartRow requires a valid ToolDef with "
                "step, slug, name, description, and accentColor."
            )

    step = _getattr_or_item(tool, "step")
    slug = _getattr_or_item(tool, "slug")
    name = _getattr_or_item(tool, "name")
    description = _getattr_or_item(tool, "description")
    accentColor = _getattr_or_item(tool, "accentColor")

    # Normalize ToolSlug enum to string value
    if isinstance(slug, ToolSlug):
        slug = slug.value

    return QuickStartRow(
        step=step,
        slug=slug,
        name=name,
        description=description,
        accentColor=accentColor,
    )


def toDiagramNode(
    tool: Any,
) -> DiagramNode:
    """
    Pure projection function. Extracts the fields required by ClosedLoopDiagram
    from a single ToolDef record. Returns a DiagramNode view-model.
    """
    _log("debug", "toDiagramNode invoked")

    if tool is None:
        raise TypeError(
            "invalid_tool_def: toDiagramNode requires a valid ToolDef with "
            "slug, name, step, and accentColor."
        )

    required_fields = ("slug", "name", "step", "accentColor")
    for f in required_fields:
        if not _has_field(tool, f):
            raise TypeError(
                "invalid_tool_def: toDiagramNode requires a valid ToolDef with "
                "slug, name, step, and accentColor."
            )

    slug = _getattr_or_item(tool, "slug")
    name = _getattr_or_item(tool, "name")
    step = _getattr_or_item(tool, "step")
    accentColor = _getattr_or_item(tool, "accentColor")

    if isinstance(slug, ToolSlug):
        slug = slug.value

    return DiagramNode(
        slug=slug,
        name=name,
        step=step,
        accentColor=accentColor,
    )


def _validate_tool_list(tools: Any, func_name: str) -> None:
    """Shared validation for list projection functions."""
    if tools is None or not isinstance(tools, (list, tuple)):
        raise TypeError(
            f"invalid_tool_list: {func_name} requires a ToolDefList of exactly 11 elements."
        )
    if len(tools) != 11:
        raise TypeError(
            f"invalid_tool_list: {func_name} requires a ToolDefList of exactly 11 elements."
        )
    # Check ascending step order
    for i in range(len(tools)):
        step_i = _getattr_or_item(tools[i], "step")
        if i > 0:
            step_prev = _getattr_or_item(tools[i - 1], "step")
            if step_i <= step_prev:
                raise RangeError(
                    f"unsorted_input: {func_name} requires tools sorted by step ascending."
                )


def toQuickStartRows(
    tools: Any,
) -> QuickStartRowList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered
    QuickStartRowList, preserving step-number ascending order.
    """
    _log("debug", "toQuickStartRows invoked")
    _validate_tool_list(tools, "toQuickStartRows")
    return [toQuickStartRow(t) for t in tools]


def toDiagramNodes(
    tools: Any,
) -> DiagramNodeList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered
    DiagramNodeList, preserving step-number ascending order.
    """
    _log("debug", "toDiagramNodes invoked")
    _validate_tool_list(tools, "toDiagramNodes")
    return [toDiagramNode(t) for t in tools]


# ---------------------------------------------------------------------------
# Circular layout computation
# ---------------------------------------------------------------------------

def computeNodePosition(
    step: int,
    totalNodes: int,
    centerX: float,
    centerY: float,
    radius: float,
) -> CircularLayoutPoint:
    """
    Internal pure function. Computes the (x, y) SVG coordinates for a diagram
    node given its step number and total node count, using trigonometric
    circular layout.

    angle = ((step - 1) / totalNodes) * 2\u03c0 - \u03c0/2
    x = centerX + radius * cos(angle)
    y = centerY + radius * sin(angle)
    """
    _log("debug", f"computeNodePosition invoked step={step}")

    if radius <= 0:
        raise RangeError("invalid_radius: radius must be a positive number.")

    if step < 1 or step > totalNodes:
        raise RangeError("step_out_of_range: step must be in range [1, totalNodes].")

    angle = ((step - 1) / totalNodes) * 2 * math.pi - math.pi / 2
    x = centerX + radius * math.cos(angle)
    y = centerY + radius * math.sin(angle)

    return CircularLayoutPoint(x=x, y=y)


# ---------------------------------------------------------------------------
# React component stubs (Python-side representations)
# ---------------------------------------------------------------------------

def ClosedLoopDiagram(
    nodes: DiagramNodeList,
) -> ReactElement:
    """
    React functional component. Renders an SVG with viewBox='0 0 500 500'
    and width='100%'. Positions 11 tool nodes in a circular layout.
    """
    _log("debug", "ClosedLoopDiagram invoked")

    if not nodes or len(nodes) == 0:
        raise RenderError(
            "empty_nodes: ClosedLoopDiagram requires a non-empty DiagramNodeList."
        )
    if len(nodes) != 11:
        raise RenderError(
            "incorrect_node_count: ClosedLoopDiagram expects exactly 11 nodes."
        )

    import re
    hex_pattern = re.compile(r"^#[0-9a-fA-F]{6}$")
    for node in nodes:
        color = _getattr_or_item(node, "accentColor")
        if not hex_pattern.match(color):
            raise RenderError(
                "invalid_accent_color: All DiagramNode accentColor values must be valid hex colors."
            )

    # In a real React app this would return JSX. Here we return a ReactElement stub.
    return ReactElement()


def HomePage() -> ReactElement:
    """
    Route-level React functional component rendered at path '/'.
    """
    _log("debug", "HomePage invoked")
    # In a real React app this would import from tool_data and render JSX.
    return ReactElement()


# ---------------------------------------------------------------------------
# REQUIRED EXPORTS
# ---------------------------------------------------------------------------
__all__ = [
    "QuickStartRow",
    "DiagramNode",
    "DiagramNodeList",
    "QuickStartRowList",
    "ClosedLoopDiagramProps",
    "HomePageProps",
    "CircularLayoutPoint",
    "SVGViewBoxSpec",
    "ToolSlug",
    "ToolDef",
    "ToolDefList",
    "OptionalVideoUrl",
    "InstructionStepList",
    "InstructionStep",
    "ReactElement",
    "string",
    "toQuickStartRow",
    "toDiagramNode",
    "toQuickStartRows",
    "RangeError",
    "toDiagramNodes",
    "computeNodePosition",
    "ClosedLoopDiagram",
    "RenderError",
    "HomePage",
]
