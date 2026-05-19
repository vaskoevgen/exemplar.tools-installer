// === Pipeline Diagram Component (pipeline_diagram) v1 ===
//  Dependencies: step_content, route_config
// Custom React/SVG component for the Home page showing the exemplar.tools pipeline flow. Renders step boxes (Step 0 through Step 7) connected by arrows/lines in the correct order, with branching for parallel steps (1a/1b, 2a/2b, 5a/5b/5c). Each box is clickable and navigates to the corresponding step page via React Router. Responsive sizing. Named export PipelineDiagram. Tests verify all step nodes render and click navigation.

// Module invariants:
//   - PIPELINE_NODES always contains exactly 12 nodes, one for each step: step-0, step-1a, step-1b, step-2a, step-2b, step-3, step-4, step-5a, step-5b, step-5c, step-6, step-7.
//   - PIPELINE_EDGES always contains exactly 14 directed edges modeling the DAG: 0→1a, 0→1b, 1a→2a, 1b→2b, 2a→3, 2b→3, 3→4, 4→5a, 4→5b, 4→5c, 5a→6, 5b→6, 5c→6, 6→7.
//   - Every edge in PIPELINE_EDGES references stepIds that exist in PIPELINE_NODES.
//   - The slug guard (slug.startsWith('/') ? slug : '/' + slug) is always applied before any navigation call, preventing double-slash prefixes.
//   - All exports are named exports only — no default exports.
//   - The SVG viewBox is always '0 0 1200 800' and the SVG root is always responsive (width='100%', preserveAspectRatio='xMidYMid meet').
//   - Every rendered node group has role='link', tabIndex=0, and aria-label='Navigate to {label}' for accessibility.
//   - Keyboard interaction (Enter and Space) on a node triggers the same navigation as a mouse click.
//   - The component never prepends an extra '/' to a slug that already starts with '/'.
//   - Module exports exactly: PipelineDiagram, PIPELINE_NODES, PIPELINE_EDGES, guardSlug as runtime values; PipelineDiagramProps, PipelineEdge, PipelineEdgeList, DiagramNode, DiagramNodeList as type-only exports.

/** Unique identifier for each step in the exemplar.tools pipeline, used as keys in content data and pipeline diagram nodes. */
export type StepId = "home" | "cartographer" | "constrain" | "ledger" | "pact" | "advocate" | "arbiter" | "baton" | "sentinel" | "chronicler" | "stigmergy" | "apprentice" | "kindex";

/** Human-readable display labels for each pipeline step, shown in sidebar navigation, diagram boxes, and page titles. */
export type StepLabel = "Home" | "Step 0 — Cartographer" | "Step 1a — Constrain" | "Step 1b — Ledger" | "Step 2a — Pact" | "Step 2b — Advocate" | "Step 3 — Arbiter" | "Step 4 — Baton" | "Step 5a — Sentinel" | "Step 5b — Chronicler" | "Step 5c — Stigmergy" | "Step 6 — Apprentice" | "Step 7 — Kindex";

/** All 14 valid route slugs (leading-slash paths) used for navigation and route registration across the app. */
export type RouteSlug = "/" | "/cartographer" | "/constrain" | "/ledger" | "/pact" | "/advocate" | "/arbiter" | "/baton" | "/sentinel" | "/chronicler" | "/stigmergy" | "/apprentice" | "/kindex";

/** A single node in the pipeline diagram representing one step, linking to its route for click navigation. */
export interface PipelineNode {
  stepId: StepId;  // required, Step identifier used to look up the route slug for navigation.
  label: StepLabel;  // required, Text rendered inside the SVG box.
  slug: RouteSlug;  // required, Route slug for click-through navigation.
  x: number;  // required, Horizontal position of the node in the SVG coordinate system.
  y: number;  // required, Vertical position of the node in the SVG coordinate system.
}

/** All nodes to render in the pipeline diagram SVG. */
export type PipelineNodeList = PipelineNode[];

/** A PipelineNode augmented with SVG viewBox layout coordinates for rendering. Owned by this component. */
export interface DiagramNode {
  stepId: StepId;  // required, Unique identifier for this pipeline step.
  label: StepLabel;  // required, Display label rendered inside the step box.
  slug: RouteSlug;  // required, Navigation target slug for the step page.
  x: number;  // required, range(min=0,max=1200), X coordinate of the node center within the SVG viewBox.
  y: number;  // required, range(min=0,max=800), Y coordinate of the node center within the SVG viewBox.
}

/** Array of DiagramNode objects with layout coordinates. This is the internal representation used by PIPELINE_NODES constant. */
export type DiagramNodeList = DiagramNode[];

/** A directed edge connecting two pipeline steps in the DAG. Owned by this component. */
export interface PipelineEdge {
  from: StepId;  // required, Source step of the directed edge.
  to: StepId;  // required, Target step of the directed edge.
}

/** Array of all directed edges forming the pipeline DAG topology. */
export type PipelineEdgeList = PipelineEdge[];

/** Props for the PipelineDiagram React component. All fields are optional; defaults to internal PIPELINE_NODES/PIPELINE_EDGES constants and useNavigate-based click handler. */
export interface PipelineDiagramProps {
  className?: string;  // optional, default: '', Optional CSS class name applied to the root SVG element for styling overrides.
  nodes?: DiagramNodeList;  // optional, default: PIPELINE_NODES, Optional override of the pipeline nodes to render. Defaults to the built-in PIPELINE_NODES constant (12 nodes).
  edges?: PipelineEdgeList;  // optional, default: PIPELINE_EDGES, Optional override of the pipeline edges to render. Defaults to the built-in PIPELINE_EDGES constant (14 edges).
  onNodeClick?: NodeClickHandler;  // optional, default: undefined, Optional click handler override. Receives the guarded RouteSlug. If not provided, component uses React Router useNavigate internally.
}

/** Callback function type: (slug: RouteSlug) => void. Invoked when a pipeline node is clicked. */
export type NodeClickHandler = unknown;

/** A React element (JSX.Element / React.ReactElement). Returned by React functional components. */
export type ReactElement = unknown;

/** A slug string that has been normalized to always start with '/'. Result of applying the slug guard: slug.startsWith('/') ? slug : '/' + slug. */
export type GuardedSlug = unknown;

/** TypeScript number primitive. */
export type number = unknown;

/**
 * React functional component that renders the pipeline DAG as an interactive SVG diagram. Renders 12 step nodes (Step 0 through Step 7 including parallel branches 1a/1b, 2a/2b, 5a/5b/5c) connected by 14 directed edges. Each node is an accessible, clickable SVG group (<g>) containing a rect and text. Clicking a node navigates to the corresponding step page. The SVG uses a fixed viewBox with width='100%' and preserveAspectRatio='xMidYMid meet' for responsive sizing. Keyboard accessible via tabIndex and Enter/Space key handlers.
 *
 * @precondition Component must be rendered within a React Router context (e.g. BrowserRouter or MemoryRouter) if onNodeClick is not provided, because useNavigate requires router context.
 * @precondition If nodes are provided, each node.slug must be a valid RouteSlug.
 * @precondition If edges are provided, each edge.from and edge.to must reference a stepId present in the nodes array.
 * @postcondition Returned SVG element contains exactly nodes.length clickable node groups, each with role='link', tabIndex=0, and an aria-label of the form 'Navigate to {label}'.
 * @postcondition Returned SVG element contains exactly edges.length line or path elements connecting the corresponding node pairs.
 * @postcondition SVG root element has viewBox='0 0 1200 800', width='100%', and preserveAspectRatio='xMidYMid meet'.
 * @postcondition Each node group's onClick handler applies the slug guard before navigating: slug.startsWith('/') ? slug : '/' + slug.
 * @postcondition Each node group responds to Enter and Space keydown events identically to click.
 * @postcondition If className prop is provided, it is applied to the root SVG element's class attribute.
 * @throws missing_router_context (RuntimeError) - Component is rendered outside a React Router context and onNodeClick prop is not provided.
 *   message: useNavigate() may be used only in the context of a <Router> component.
 * @throws invalid_edge_reference (RenderWarning) - An edge references a stepId not present in the nodes array.
 *   message: Edge references unknown stepId; the edge will not be rendered.
 * @sideEffects none
 * @idempotent yes
 */
export function PipelineDiagram(
  props?: PipelineDiagramProps,
): ReactElement;

/**
 * Normalizes a slug string to guarantee it starts with a leading '/'. Implements the project-standard slug guard: slug.startsWith('/') ? slug : '/' + slug. This is a pure utility function used internally by PipelineDiagram before any navigation call.
 *
 * @precondition slug must be a non-empty string.
 * @postcondition Returned string always starts with exactly one '/'.
 * @postcondition If input already starts with '/', the output is identical to the input.
 * @postcondition If input does not start with '/', the output is '/' prepended to the input.
 * @postcondition No double-slash '//' prefix is introduced when input already starts with '/'.
 * @throws empty_slug (ValueError) - slug is an empty string.
 *   message: Slug must not be empty.
 * @sideEffects none
 * @idempotent yes
 */
export function guardSlug(
  slug: string,  // length(min=1,max=64)
): GuardedSlug;

/**
 * Module-level constant: an array of 12 DiagramNode objects representing all pipeline steps excluding 'home'. Each node has a stepId, label, slug, and x/y viewBox coordinates for layout. Steps: step-0, step-1a, step-1b, step-2a, step-2b, step-3, step-4, step-5a, step-5b, step-5c, step-6, step-7. Exported as a named constant.
 *
 * @postcondition Array contains exactly 12 DiagramNode elements.
 * @postcondition No node has stepId 'home'.
 * @postcondition All stepIds are unique within the array.
 * @postcondition All slugs start with '/' (pre-guarded from ROUTE_SLUG_MAP).
 * @postcondition All x values are within [0, 1200] and all y values are within [0, 800].
 * @sideEffects none
 * @idempotent yes
 */
export function PIPELINE_NODES(): DiagramNodeList;

/**
 * Module-level constant: an array of 14 PipelineEdge objects defining the complete DAG topology. Edges: step-0→step-1a, step-0→step-1b, step-1a→step-2a, step-1b→step-2b, step-2a→step-3, step-2b→step-3, step-3→step-4, step-4→step-5a, step-4→step-5b, step-4→step-5c, step-5a→step-6, step-5b→step-6, step-5c→step-6, step-6→step-7. Exported as a named constant.
 *
 * @postcondition Array contains exactly 14 PipelineEdge elements.
 * @postcondition All 'from' and 'to' stepIds reference steps present in PIPELINE_NODES.
 * @postcondition The edge set forms a valid directed acyclic graph (DAG) with no cycles.
 * @postcondition step-0 is the sole root node (no incoming edges).
 * @postcondition step-7 is the sole terminal node (no outgoing edges).
 * @sideEffects none
 * @idempotent yes
 */
export function PIPELINE_EDGES(): PipelineEdgeList;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['StepId', 'StepLabel', 'RouteSlug', 'PipelineNode', 'PipelineNodeList', 'DiagramNode', 'DiagramNodeList', 'PipelineEdge', 'PipelineEdgeList', 'PipelineDiagramProps', 'PipelineDiagram', 'RenderWarning', 'guardSlug', 'PIPELINE_NODES', 'PIPELINE_EDGES']
