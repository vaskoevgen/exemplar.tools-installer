// === Routing, Layout & Navigation (routing_and_layout) v1 ===
//  Dependencies: page_content
// Implements the routing data model and layout shell for the exemplar.tools documentation website. Includes: (1) ROUTE_SLUG_MAP constant mapping all 13 routes (home + 12 steps) with leading-slash values as a Record<StepId, RouteSlug>, (2) ROUTE_ENTRY_LIST ordered array of 13 RouteEntry objects defining sidebar order and route registration sequence, (3) ensureLeadingSlash slug guard utility using the exact ternary from operating procedures, (4) a persistent Sidebar component with NavLinks to all pages highlighting the active route (home NavLink uses `end` prop), (5) a Layout component wrapping sidebar + content area with React Router <Outlet />, (6) route registration in App.tsx using createBrowserRouter with Layout as parent route element and all 13 pages as children. All use React Router v6 browser history mode. Tests verify all 13 routes exist, no double-slash bugs, slug guard edge cases, sidebar renders all links, and all slugs are unique.

// Module invariants:
//   - ROUTE_ENTRY_LIST always contains exactly 13 entries
//   - Every value in ROUTE_SLUG_MAP starts with exactly one leading slash character ('/')
//   - No slug value in ROUTE_SLUG_MAP produces a double-slash ('//') when used as a path
//   - All RouteSlug values across ROUTE_ENTRY_LIST are unique — no two entries share the same slug
//   - ROUTE_SLUG_MAP is derivable from ROUTE_ENTRY_LIST — they are never independently maintained
//   - The first entry in ROUTE_ENTRY_LIST is always the home route with slug '/'
//   - Sidebar renders exactly one NavLink per entry in ROUTE_ENTRY_LIST, in the same order
//   - The home NavLink always uses the `end` prop to prevent matching all routes
//   - Layout always renders Sidebar on the left and Outlet in the main content area
//   - ensureLeadingSlash is a pure function with no side effects

/** All 14 valid route slugs (leading-slash paths) used for navigation and route registration across the app. */
export type RouteSlug = "/" | "/cartographer" | "/constrain" | "/ledger" | "/pact" | "/advocate" | "/arbiter" | "/baton" | "/sentinel" | "/chronicler" | "/stigmergy" | "/apprentice" | "/kindex";

/** Unique identifier for each step in the exemplar.tools pipeline, used as keys in content data and pipeline diagram nodes. */
export type StepId = "home" | "cartographer" | "constrain" | "ledger" | "pact" | "advocate" | "arbiter" | "baton" | "sentinel" | "chronicler" | "stigmergy" | "apprentice" | "kindex";

/** Human-readable display labels for each pipeline step, shown in sidebar navigation, diagram boxes, and page titles. */
export type StepLabel = "Home" | "Step 0 — Cartographer" | "Step 1a — Constrain" | "Step 1b — Ledger" | "Step 2a — Pact" | "Step 2b — Advocate" | "Step 3 — Arbiter" | "Step 4 — Baton" | "Step 5a — Sentinel" | "Step 5b — Chronicler" | "Step 5c — Stigmergy" | "Step 6 — Apprentice" | "Step 7 — Kindex";

/** A single entry in the route map linking a step to its slug and display label, consumed by sidebar nav and route registration. */
export interface RouteEntry {
  stepId: StepId;  // required, Unique pipeline step identifier.
  slug: RouteSlug;  // required, URL path slug for this route (always starts with '/').
  label: StepLabel;  // required, Human-readable label displayed in navigation and page headers.
}

/** Ordered list of all 14 RouteEntry items, defining sidebar order and route registration sequence. */
export type RouteEntryList = RouteEntry[];

/** Record<StepId, RouteSlug> providing O(1) lookup from step ID to its URL slug. Derived from ROUTE_ENTRY_LIST via Array.reduce — never independently maintained. */
export interface RouteSlugMap {
  home: RouteSlug;  // required, Slug for home page: '/'
  cartographer: RouteSlug;  // required, Slug for cartographer step: '/cartographer'
  constrain: RouteSlug;  // required, Slug for constrain step: '/constrain'
  ledger: RouteSlug;  // required, Slug for ledger step: '/ledger'
  pact: RouteSlug;  // required, Slug for pact step: '/pact'
  advocate: RouteSlug;  // required, Slug for advocate step: '/advocate'
  arbiter: RouteSlug;  // required, Slug for arbiter step: '/arbiter'
  baton: RouteSlug;  // required, Slug for baton step: '/baton'
  sentinel: RouteSlug;  // required, Slug for sentinel step: '/sentinel'
  chronicler: RouteSlug;  // required, Slug for chronicler step: '/chronicler'
  stigmergy: RouteSlug;  // required, Slug for stigmergy step: '/stigmergy'
  apprentice: RouteSlug;  // required, Slug for apprentice step: '/apprentice'
  kindex: RouteSlug;  // required, Slug for kindex step: '/kindex'
}

/** React.ReactNode — the return type of React functional components. Represents any renderable React content. */
export type ReactNode = unknown;

/** The className callback signature for React Router NavLink: ({ isActive }: { isActive: boolean }) => string. Returns Tailwind classes for active/inactive states. */
export type NavLinkClassName = unknown;

/** Configuration object returned by createBrowserRouter. Represents the complete route tree with Layout as the parent route and all 13 page routes as children. */
export interface RouterConfig {
  path: string;  // required, Root path, always '/'
  element: ReactNode;  // required, The Layout component instance wrapping Sidebar + Outlet
  children: unknown[];  // required, Array of child route objects, one per ROUTE_ENTRY_LIST entry, each with path and element props
}

/**
 * Pure utility function that guarantees a string has exactly one leading slash. Uses the exact ternary from operating procedures: `slug.startsWith('/') ? slug : '/' + slug`. Does NOT strip double slashes — that is a separate concern validated by invariants on ROUTE_SLUG_MAP values.
 *
 * @precondition slug is a string (may be empty)
 * @postcondition Return value always starts with '/'
 * @postcondition If input already starts with '/', return value equals input unchanged
 * @postcondition If input does not start with '/', return value equals '/' + input
 * @postcondition Empty string input returns '/'
 * @sideEffects none
 * @idempotent yes
 */
export function ensureLeadingSlash(
  slug: string,
): string;

/**
 * React functional component that renders a vertical navigation sidebar. Iterates over ROUTE_ENTRY_LIST and renders one React Router NavLink per entry, using entry.slug as the `to` prop and entry.label as the link text. Uses NavLink's className callback `({ isActive }) => string` to apply Tailwind active/inactive styles. The home NavLink (slug='/') uses the `end` prop to prevent it from matching all routes. Styled with Tailwind for fixed-width left sidebar positioning.
 *
 * @precondition Component must be rendered within a React Router context (BrowserRouter, MemoryRouter, or RouterProvider)
 * @precondition ROUTE_ENTRY_LIST must be available as an import from the routing module
 * @postcondition Renders exactly 13 NavLink elements, one per entry in ROUTE_ENTRY_LIST
 * @postcondition NavLinks appear in the same order as ROUTE_ENTRY_LIST
 * @postcondition The home NavLink (slug='/') has the `end` prop set to true
 * @postcondition Each NavLink's `to` prop matches the corresponding entry's slug value
 * @postcondition Each NavLink displays the corresponding entry's label as text content
 * @postcondition Active NavLink receives distinct Tailwind classes for visual highlighting
 * @throws no_router_context (React Router invariant error) - Sidebar is rendered outside of a React Router context
 *   message: useLocation() may be used only in the context of a <Router> component
 * @sideEffects none
 * @idempotent yes
 */
export function Sidebar(): ReactNode;

/**
 * React functional component that renders the top-level page layout shell. Uses a Tailwind flex container with Sidebar on the left and a main content area on the right containing React Router's <Outlet /> component. The Outlet renders the matched child route's component. Layout is used as the `element` of the root route in createBrowserRouter configuration.
 *
 * @precondition Component must be rendered within a React Router context
 * @precondition Sidebar component must be available as an import
 * @precondition React Router Outlet must be available
 * @postcondition Renders a flex container with exactly two children: Sidebar and a main content wrapper
 * @postcondition The main content wrapper contains exactly one <Outlet /> component
 * @postcondition Sidebar is positioned on the left side of the flex container
 * @postcondition The main content area fills the remaining horizontal space
 * @throws no_router_context (React Router invariant error) - Layout is rendered outside of a React Router context
 *   message: useOutlet() may be used only in the context of a <Router> component
 * @sideEffects none
 * @idempotent yes
 */
export function Layout(): ReactNode;

/**
 * Factory function that creates and returns a React Router v6 browser router instance using createBrowserRouter. Constructs the route tree with Layout as the parent route element (path='/') and all 13 page routes as children. Child route paths are derived from ROUTE_ENTRY_LIST entries: home uses `index: true`, all others use `path: entry.slug.slice(1)` (removing the leading slash since they are relative to the parent). Each child route's element is the corresponding page component, lazy-loaded or directly imported.
 *
 * @precondition ROUTE_ENTRY_LIST must contain exactly 13 entries
 * @precondition All page components referenced by route entries must be importable
 * @precondition React Router createBrowserRouter must be available
 * @postcondition Returns a valid router instance with exactly 1 parent route and 13 child routes
 * @postcondition Parent route has path '/' and element <Layout />
 * @postcondition Home child route uses `index: true` instead of `path: ''`
 * @postcondition All non-home child routes have paths matching their slug without the leading slash
 * @postcondition Router uses browser history mode (not hash or memory)
 * @throws missing_page_component (ModuleNotFoundError) - A page component referenced in ROUTE_ENTRY_LIST cannot be resolved at import time
 *   message: Cannot find module for route entry stepId
 * @sideEffects none
 * @idempotent yes
 */
export function createAppRouter(): RouterConfig;

/**
 * Pure helper function that returns the className callback for NavLink components. Given an isActive boolean from React Router's NavLink render prop, returns the appropriate Tailwind CSS class string for active or inactive navigation link styling.
 *
 * @postcondition When isActive is true, returns a class string containing active state Tailwind classes (e.g., font-bold, specific background/text color)
 * @postcondition When isActive is false, returns a class string containing inactive state Tailwind classes
 * @postcondition Return value is always a non-empty string
 * @sideEffects none
 * @idempotent yes
 */
export function getNavLinkClassName(
  isActive: boolean,
): string;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['RouteSlug', 'StepId', 'StepLabel', 'RouteEntry', 'RouteEntryList', 'RouteSlugMap', 'RouterConfig', 'ensureLeadingSlash', 'Sidebar', 'Layout', 'createAppRouter', 'ModuleNotFoundError', 'getNavLinkClassName']
