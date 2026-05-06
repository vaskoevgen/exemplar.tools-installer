# === Home Page (home_page) v1 ===
#  Dependencies: type_registry, tool_data
# Route-level page component rendered at '/'. Composes three vertical sections: (a) workflow overview prose paragraph, (b) quick-start HTML table listing all 11 tools with step number, linked tool name styled in accent color, and one-line description, (c) ClosedLoopDiagram SVG component arranging tools in a circular flow. Includes ClosedLoopDiagram as a co-located presentational component and four exported projection functions for mapping ToolDef records to view-model types. All canonical domain types are imported from the type registry; none are redefined here.

# Module invariants:
#   - HomePage and ClosedLoopDiagram never redefine canonical types (ToolDef, ToolDefList, ToolSlug, StepNumber, HexColor) — they must be imported from type_registry.
#   - All four projection functions (toQuickStartRow, toDiagramNode, toQuickStartRows, toDiagramNodes) are pure and stateless: identical inputs always produce identical outputs.
#   - ClosedLoopDiagram is purely presentational: it receives data via props and never imports from tool_data or performs data fetching.
#   - HomePage is the only component that imports ToolDefList and performs projections; ClosedLoopDiagram depends solely on its props.
#   - The quick-start table and diagram always display exactly 11 tools in step-ascending order (step 1 through step 11).
#   - Dynamic colors (accentColor) are always applied via inline style attributes, never via Tailwind utility classes, because they are runtime values.
#   - Arrow connectivity forms a closed loop: node[0] → node[1] → ... → node[10] → node[0].
#   - SVG viewBox is always '0 0 500 500'; width is always '100%' for responsive scaling.
#   - Trigonometric layout offset is -π/2 so step 1 appears at the top of the circle.
#   - All navigation links in both the table and diagram point to /tools/${slug} using the canonical ToolSlug.
#   - No class components are used; all components are React functional components.
#   - No custom CSS files are created or imported; all static styling uses Tailwind CSS v3 classes.
#   - Source files remain under 300 lines each: HomePage.tsx and ClosedLoopDiagram.tsx are separate files.

class QuickStartRow:
    """One row in the HomePage quick-start table, projected from ToolDef."""
    step: StepNumber                         # required, Step number column value.
    slug: ToolSlug                           # required, Route slug for the tool name link.
    name: string                             # required, Tool display name rendered as a router link.
    description: string                      # required, One-line description column value.

class DiagramNode:
    """Data for one node in the ClosedLoopDiagram SVG, projected from ToolDef."""
    slug: ToolSlug                           # required, Tool identifier for link target from diagram node.
    name: string                             # required, Label rendered inside the diagram node.
    step: StepNumber                         # required, Step number for ordering nodes around the circular layout.
    accentColor: HexColor                    # required, Fill/stroke color for this tool's node in the diagram.

DiagramNodeList = list[DiagramNode]
# Ordered array of DiagramNode objects passed into the ClosedLoopDiagram component.

QuickStartRowList = list[QuickStartRow]
# Ordered list of QuickStartRow view-models. Length must equal 11. Order matches step number ascending.

class ClosedLoopDiagramProps:
    """Props interface for the ClosedLoopDiagram React component. Keeps the component purely presentational with no data-fetching responsibilities."""
    nodes: DiagramNodeList                   # required, Ordered list of diagram nodes to arrange in a circular flow. Must contain exactly 11 elements.

class HomePageProps:
    """Props interface for the HomePage route-level component. Empty by design — HomePage imports ToolDefList from the data layer and performs projections internally."""
    pass

class CircularLayoutPoint:
    """Internal type representing a computed (x, y) position within the SVG viewBox for a single diagram node. Not exported."""
    x: float                                 # required, range(0.0..=500.0), Horizontal coordinate in SVG viewBox units (0–500).
    y: float                                 # required, range(0.0..=500.0), Vertical coordinate in SVG viewBox units (0–500).

class SVGViewBoxSpec:
    """Constants defining the SVG coordinate system for the diagram."""
    width: int                               # required, ViewBox width in abstract units.
    height: int                              # required, ViewBox height in abstract units.
    centerX: float                           # required, X coordinate of circle center.
    centerY: float                           # required, Y coordinate of circle center.
    radius: float                            # required, Radius of the circular layout in viewBox units.

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

StepNumber = primitive  # Integer 1–11 representing the tool's position in the exemplar.tools workflow order.

HexColor = primitive  # CSS hex color string (e.g. '#00e5ff') used for per-tool accent theming.

class ToolDef:
    """Complete static definition of one tool including display metadata, instructions, and video URL."""
    slug: ToolSlug                           # required, URL-safe identifier used as route parameter and sidebar key.
    name: string                             # required, Human-readable display name of the tool (e.g. 'Constrain').
    description: string                      # required, One-line description shown on the tool page and in the quick-start table.
    step: StepNumber                         # required, Workflow step number (1–11) displayed in the StepBadge.
    version: string                          # required, Semver version string displayed in the VersionBadge.
    accentColor: HexColor                    # required, Per-tool accent color hex for badges, headings, and diagram nodes.
    videoUrl: OptionalVideoUrl = undefined   # optional, YouTube embed URL; omitted for kindex.
    instructions: InstructionStepList        # required, Ordered step-by-step instructions rendered on the tool page.

ToolDefList = list[ToolDef]
# The canonical ordered array of all 11 ToolDef objects, indexed by workflow step order.

OptionalVideoUrl = Any | None

InstructionStepList = list[InstructionStep]
# Ordered array of InstructionStep objects for a tool's how-to section.

class InstructionStep:
    """A single step-by-step instruction entry containing a human title and a bash snippet."""
    title: string                            # required, Short human-readable title for this instruction step.
    bash: string                             # required, Bash code block content to display in a terminal-styled card.

class ReactElement:
    """Auto-stubbed type — referenced but not defined in contract 'home_page'"""
    pass

class string:
    """Auto-stubbed type — referenced but not defined in contract 'home_page'"""
    pass

def toQuickStartRow(
    tool: ToolDef,
) -> QuickStartRow:
    """
    Pure projection function. Extracts the fields required by the quick-start table from a single ToolDef record. Returns a QuickStartRow view-model. Exported from src/pages/HomePage.tsx (or a co-located utils module) for testability.

    Preconditions:
      - tool is a valid ToolDef with all required fields populated
      - tool.step is in range 1..=11
      - tool.accentColor is a valid 7-character hex color string matching /^#[0-9a-fA-F]{6}$/

    Postconditions:
      - returned QuickStartRow.step === tool.step
      - returned QuickStartRow.slug === tool.slug
      - returned QuickStartRow.name === tool.name
      - returned QuickStartRow.description === tool.description
      - returned QuickStartRow.accentColor === tool.accentColor

    Errors:
      - invalid_tool_def (TypeError): Input tool is null, undefined, or missing required fields (step, slug, name, description, accentColor).
          message: toQuickStartRow requires a valid ToolDef with step, slug, name, description, and accentColor.

    Side effects: none
    Idempotent: yes
    """
    ...

def toDiagramNode(
    tool: ToolDef,
) -> DiagramNode:
    """
    Pure projection function. Extracts the fields required by ClosedLoopDiagram from a single ToolDef record. Returns a DiagramNode view-model.

    Preconditions:
      - tool is a valid ToolDef with all required fields populated
      - tool.step is in range 1..=11
      - tool.accentColor is a valid 7-character hex color string matching /^#[0-9a-fA-F]{6}$/

    Postconditions:
      - returned DiagramNode.slug === tool.slug
      - returned DiagramNode.name === tool.name
      - returned DiagramNode.step === tool.step
      - returned DiagramNode.accentColor === tool.accentColor

    Errors:
      - invalid_tool_def (TypeError): Input tool is null, undefined, or missing required fields (slug, name, step, accentColor).
          message: toDiagramNode requires a valid ToolDef with slug, name, step, and accentColor.

    Side effects: none
    Idempotent: yes
    """
    ...

def toQuickStartRows(
    tools: ToolDefList,
) -> QuickStartRowList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered QuickStartRowList, preserving step-number ascending order. Delegates to toQuickStartRow for each element.

    Preconditions:
      - tools is a non-empty array of exactly 11 valid ToolDef records
      - tools is sorted by step ascending (tools[i].step === i + 1 for all i in 0..10)

    Postconditions:
      - returned list has length 11
      - returned list is sorted by step ascending
      - returned[i].step === tools[i].step for all i in 0..10
      - each element satisfies toQuickStartRow postconditions

    Errors:
      - invalid_tool_list (TypeError): Input tools is null, undefined, not an array, or length !== 11.
          message: toQuickStartRows requires a ToolDefList of exactly 11 elements.
      - unsorted_input (RangeError): Input tools array is not sorted by step ascending.
          message: toQuickStartRows requires tools sorted by step ascending.

    Side effects: none
    Idempotent: yes
    """
    ...

def toDiagramNodes(
    tools: ToolDefList,
) -> DiagramNodeList:
    """
    Pure projection function. Maps an entire ToolDefList to an ordered DiagramNodeList, preserving step-number ascending order. Delegates to toDiagramNode for each element.

    Preconditions:
      - tools is a non-empty array of exactly 11 valid ToolDef records
      - tools is sorted by step ascending (tools[i].step === i + 1 for all i in 0..10)

    Postconditions:
      - returned list has length 11
      - returned list is sorted by step ascending
      - returned[i].step === tools[i].step for all i in 0..10
      - each element satisfies toDiagramNode postconditions

    Errors:
      - invalid_tool_list (TypeError): Input tools is null, undefined, not an array, or length !== 11.
          message: toDiagramNodes requires a ToolDefList of exactly 11 elements.
      - unsorted_input (RangeError): Input tools array is not sorted by step ascending.
          message: toDiagramNodes requires tools sorted by step ascending.

    Side effects: none
    Idempotent: yes
    """
    ...

def computeNodePosition(
    step: StepNumber,
    totalNodes: int,           # range(1..=100)
    centerX: float,
    centerY: float,
    radius: float,
) -> CircularLayoutPoint:
    """
    Internal pure function. Computes the (x, y) SVG coordinates for a diagram node given its step number and total node count, using trigonometric circular layout. angle = ((step - 1) / totalNodes) * 2π - π/2. x = centerX + radius * cos(angle). y = centerY + radius * sin(angle). Not exported.

    Preconditions:
      - step >= 1 && step <= totalNodes
      - totalNodes >= 1
      - radius > 0

    Postconditions:
      - returned point x is within [centerX - radius, centerX + radius]
      - returned point y is within [centerY - radius, centerY + radius]
      - for step=1 and standard defaults: x ≈ 250.0, y ≈ 50.0 (top of circle, -π/2 offset)

    Errors:
      - step_out_of_range (RangeError): step < 1 or step > totalNodes.
          message: step must be in range [1, totalNodes].
      - invalid_radius (RangeError): radius <= 0.
          message: radius must be a positive number.

    Side effects: none
    Idempotent: yes
    """
    ...

def ClosedLoopDiagram(
    nodes: DiagramNodeList,
) -> ReactElement:
    """
    React functional component (src/components/ClosedLoopDiagram.tsx). Renders an SVG with viewBox='0 0 500 500' and width='100%' (responsive). Positions N=11 tool nodes in a circular layout via computeNodePosition. For each node: renders a circle with fill=accentColor at (x,y), a text label, and wraps in an SVG <a> element with href='/tools/${slug}'. Adds an onClick handler calling useNavigate() for SPA navigation without full page reload. Each node has aria-label='Navigate to ${name} tool page'. Connecting arrows form a sequential closed loop: arrow from node[i] to node[(i+1) % N], colored with node[i].accentColor. Arrow markers are defined in <defs> with one <marker id='arrow-${slug}'> per tool, colored to match. Background is transparent (inherits dark theme from parent). Text color is white (#FFFFFF). No custom CSS; all non-dynamic styling via Tailwind classes on the wrapper div.

    Preconditions:
      - nodes is a non-empty array of exactly 11 DiagramNode elements
      - nodes is sorted by step ascending
      - all accentColor values are valid 7-character hex color strings
      - all slug values are non-empty and URL-safe

    Postconditions:
      - renders exactly one <svg> element with viewBox='0 0 500 500'
      - SVG contains exactly 11 node groups, each wrapped in an <a> with href='/tools/${slug}'
      - SVG <defs> contains exactly 11 <marker> elements, one per tool
      - SVG contains exactly 11 <line> or <path> arrow elements forming a closed loop
      - each node circle has fill set to its accentColor via inline style
      - each arrow stroke is set to the source node's accentColor via inline style
      - all text elements use fill='#FFFFFF'
      - wrapper div uses Tailwind classes only (no custom CSS)

    Errors:
      - empty_nodes (RenderError): nodes is an empty array.
          message: ClosedLoopDiagram requires a non-empty DiagramNodeList.
      - incorrect_node_count (RenderError): nodes.length !== 11.
          message: ClosedLoopDiagram expects exactly 11 nodes.
      - invalid_accent_color (RenderError): Any node's accentColor does not match /^#[0-9a-fA-F]{6}$/.
          message: All DiagramNode accentColor values must be valid hex colors.

    Side effects: none
    Idempotent: yes
    """
    ...

def HomePage() -> ReactElement:
    """
    Route-level React functional component (src/pages/HomePage.tsx) rendered at path '/'. Accepts no props (HomePageProps is empty). On render: (1) imports ToolDefList from the tool_data module, (2) calls toQuickStartRows(tools) and toDiagramNodes(tools) to produce view-models, (3) renders three vertical sections: (a) a workflow overview paragraph wrapped in Tailwind prose classes (dark theme: text-gray-300, prose-invert), (b) a semantic <table> with <thead> columns ['Step', 'Tool', 'Description'] and <tbody> rows from QuickStartRowList — tool name cell is a React Router <Link to='/tools/${slug}'> with inline style color set to accentColor, (c) a <ClosedLoopDiagram nodes={diagramNodes} /> instance. Page wrapper uses Tailwind classes for padding, max-width, and responsive layout. No custom CSS.

    Preconditions:
      - ToolDefList is importable from tool_data and contains exactly 11 entries sorted by step
      - React Router context is available (component is rendered within a <Routes> tree)
      - Tailwind CSS is loaded and configured

    Postconditions:
      - renders a single root <div> or <main> element with Tailwind layout classes
      - first section contains a <p> or <div> with workflow overview text
      - second section contains a <table> with 11 <tr> body rows
      - each table row tool name is a React Router <Link> with correct to='/tools/${slug}'
      - each <Link> has inline style={{ color: row.accentColor }}
      - third section contains exactly one ClosedLoopDiagram component
      - no custom CSS stylesheets are loaded or injected

    Errors:
      - tool_data_import_failure (RenderError): ToolDefList import from tool_data fails or returns undefined.
          message: HomePage failed to load tool definitions from data layer.
      - projection_failure (TypeError): toQuickStartRows or toDiagramNodes throws due to malformed ToolDefList.
          message: HomePage projection failed: ToolDefList is malformed.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['QuickStartRow', 'DiagramNode', 'DiagramNodeList', 'QuickStartRowList', 'ClosedLoopDiagramProps', 'HomePageProps', 'CircularLayoutPoint', 'SVGViewBoxSpec', 'ToolSlug', 'ToolDef', 'ToolDefList', 'OptionalVideoUrl', 'InstructionStepList', 'InstructionStep', 'ReactElement', 'string', 'toQuickStartRow', 'toDiagramNode', 'toQuickStartRows', 'RangeError', 'toDiagramNodes', 'computeNodePosition', 'ClosedLoopDiagram', 'RenderError', 'HomePage']
