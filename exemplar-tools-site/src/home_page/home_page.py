"""Home Page component implementation.

Route-level page component rendered at '/'. Composes three vertical sections:
(a) workflow overview prose paragraph,
(b) quick-start HTML table listing all 11 tools,
(c) ClosedLoopDiagram SVG component.

Includes ClosedLoopDiagram as a co-located presentational component and four
exported projection functions for mapping ToolDef records to view-model types.
"""
import logging
import math
import time
from enum import Enum
from typing import Any, List, Optional
from dataclasses import dataclass, field

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
# Custom error classes
# ---------------------------------------------------------------------------

class RangeError(Exception):
    """Raised when a value is outside its valid range."""
    pass


class RenderError(Exception):
    """Raised when a rendering operation fails."""
    pass


# ---------------------------------------------------------------------------
# Canonical domain types (would normally be imported from type_registry)
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
string = str      # Auto-stubbed type
OptionalVideoUrl = Any
ReactElement = Any


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
    videoUrl: Any = None


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


# ---------------------------------------------------------------------------
# Helper: access attribute or dict key
# ---------------------------------------------------------------------------

def _get_field(obj: Any, key: str) -> Any:
    """Get a field from an object (dict or dataclass/object)."""
    if obj is None:
        raise AttributeError(f"Cannot access '{key}' on None")
    if isinstance(obj, dict):
        if key not in obj:
            raise KeyError(key)
        return obj[key]
    if not hasattr(obj, key):
        raise AttributeError(f"Object missing required field '{key}'")
    return getattr(obj, key)


def _has_field(obj: Any, key: str) -> bool:
    """Check if an object has a field (dict or dataclass/object)."""
    if obj is None:
        return False
    if isinstance(obj, dict):
        return key in obj
    return hasattr(obj, key)


# ---------------------------------------------------------------------------
# Pure projection functions
# ---------------------------------------------------------------------------

def toQuickStartRow(tool: Any) -> QuickStartRow:
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

    required_fields = ["step", "slug", "name", "description", "accentColor"]
    for f in required_fields:
        if not _has_field(tool, f):
            raise TypeError(
                "invalid_tool_def: toQuickStartRow requires a valid ToolDef with "
                "step, slug, name, description, and accentColor."
            )

    step = _get_field(tool, "step")
    slug = _get_field(tool, "slug")
    name = _get_field(tool, "name")
    description = _get_field(tool, "description")
    accentColor = _get_field(tool, "accentColor")

    # Resolve enum values to strings if needed
    if isinstance(slug, ToolSlug):
        slug = slug.value

    return QuickStartRow(
        step=step,
        slug=slug,
        name=name,
        description=description,
        accentColor=accentColor,
    )


def toDiagramNode(tool: Any) -> DiagramNode:
    """
    Pure projection function. Extracts the fields required by
    ClosedLoopDiagram from a single ToolDef record.
    """
    _log("debug", "toDiagramNode invoked")

    if tool is None:
        raise TypeError(
            "invalid_tool_def: toDiagramNode requires a valid ToolDef with "
            "slug, name, step, and accentColor."
        )

    required_fields = ["slug", "name", "step", "accentColor"]
    for f in required_fields:
        if not _has_field(tool, f):
            raise TypeError(
                "invalid_tool_def: toDiagramNode requires a valid ToolDef with "
                "slug, name, step, and accentColor."
            )

    slug = _get_field(tool, "slug")
    name = _get_field(tool, "name")
    step = _get_field(tool, "step")
    accentColor = _get_field(tool, "accentColor")

    # Resolve enum values to strings if needed
    if isinstance(slug, ToolSlug):
        slug = slug.value

    return DiagramNode(
        slug=slug,
        name=name,
        step=step,
        accentColor=accentColor,
    )


def _validate_tool_list(tools: Any, func_name: str) -> None:
    """Validate that tools is a list of exactly 11 elements sorted by step ascending."""
    if tools is None or not isinstance(tools, list):
        raise TypeError(
            f"invalid_tool_list: {func_name} requires a ToolDefList of exactly 11 elements."
        )
    if len(tools) != 11:
        raise TypeError(
            f"invalid_tool_list: {func_name} requires a ToolDefList of exactly 11 elements."
        )
    # Check sorted by step ascending
    for i in range(len(tools) - 1):
        step_i = _get_field(tools[i], "step")
        step_next = _get_field(tools[i + 1], "step")
        if step_i >= step_next:
            raise RangeError(
                f"unsorted_input: {func_name} requires tools sorted by step ascending."
            )


def toQuickStartRows(tools: Any) -> QuickStartRowList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered
    QuickStartRowList, preserving step-number ascending order.
    """
    _log("debug", "toQuickStartRows invoked")
    _validate_tool_list(tools, "toQuickStartRows")
    return [toQuickStartRow(tool) for tool in tools]


def toDiagramNodes(tools: Any) -> DiagramNodeList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered
    DiagramNodeList, preserving step-number ascending order.
    """
    _log("debug", "toDiagramNodes invoked")
    _validate_tool_list(tools, "toDiagramNodes")
    return [toDiagramNode(tool) for tool in tools]


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
    _log("debug", f"computeNodePosition invoked for step={step}")

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

def ClosedLoopDiagram(nodes: DiagramNodeList) -> Any:
    """
    React functional component stub. In production this would be a .tsx file.
    Renders an SVG with viewBox='0 0 500 500' and width='100%'.
    """
    _log("debug", "ClosedLoopDiagram invoked")

    if nodes is None or not isinstance(nodes, list) or len(nodes) == 0:
        raise RenderError(
            "ClosedLoopDiagram requires a non-empty DiagramNodeList."
        )

    if len(nodes) != 11:
        raise RenderError(
            "ClosedLoopDiagram expects exactly 11 nodes."
        )

    import re
    hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')
    for node in nodes:
        color = _get_field(node, "accentColor")
        if not hex_pattern.match(color):
            raise RenderError(
                "All DiagramNode accentColor values must be valid hex colors."
            )

    # Compute positions and return a representation
    spec = SVGViewBoxSpec(width=500, height=500, centerX=250.0, centerY=250.0, radius=200.0)
    positions = []
    for node in nodes:
        step = _get_field(node, "step")
        pos = computeNodePosition(step, len(nodes), spec.centerX, spec.centerY, spec.radius)
        positions.append(pos)

    # Return a representation of the rendered SVG element
    return {
        "type": "svg",
        "viewBox": "0 0 500 500",
        "width": "100%",
        "nodes": nodes,
        "positions": positions,
    }


def HomePage() -> Any:
    """
    Route-level React functional component rendered at path '/'.
    """
    _log("debug", "HomePage invoked")

    # In production this would import from tool_data module
    # For now, return a representation
    return {
        "type": "div",
        "className": "max-w-4xl mx-auto px-4 py-8",
        "children": [
            {"type": "section", "id": "overview"},
            {"type": "section", "id": "quick-start-table"},
            {"type": "section", "id": "closed-loop-diagram"},
        ],
    }


# ---------------------------------------------------------------------------
# Required exports
# ---------------------------------------------------------------------------

__all__ = [
    'QuickStartRow',
    'DiagramNode',
    'DiagramNodeList',
    'QuickStartRowList',
    'ClosedLoopDiagramProps',
    'HomePageProps',
    'CircularLayoutPoint',
    'SVGViewBoxSpec',
    'ToolSlug',
    'ToolDef',
    'ToolDefList',
    'OptionalVideoUrl',
    'InstructionStepList',
    'InstructionStep',
    'ReactElement',
    'string',
    'toQuickStartRow',
    'toDiagramNode',
    'toQuickStartRows',
    'RangeError',
    'toDiagramNodes',
    'computeNodePosition',
    'ClosedLoopDiagram',
    'RenderError',
    'HomePage',
]
