// === App Shell & Routing (app_routing) v1 ===
//  Dependencies: shared_components, page_components
// Main App.tsx and routing configuration using react-router-dom BrowserRouter. Defines routes for all 13 pages: / (Home), /step-0-cartographer, /step-1a-constrain, /step-1b-ledger, /step-2a-pact, /step-2b-advocate, /step-3-arbiter, /step-4-baton, /step-5a-sentinel, /step-5b-chronicler, /step-5c-stigmergy, /step-6-apprentice, /step-7-kindex. Exports the route manifest (readonly array of RouteEntry objects) as a shared data structure consumed by Sidebar and route definitions. Structured as three source files: src/routes.ts (pure data), src/App.tsx (shell component), src/main.tsx (entry point). Contract tests verify manifest completeness, path uniqueness, label validity, enum coverage, and render smoke tests for all routes.

// Module invariants:
//   - ROUTE_MANIFEST always contains exactly 13 entries — one per documentation page
//   - The set of PageComponentKey enum variants is exactly {Home, Step0Cartographer, Step1aConstrain, Step1bLedger, Step2aPact, Step2bAdvocate, Step3Arbiter, Step4Baton, Step5aSentinel, Step5bChronicler, Step5cStigmergy, Step6Apprentice, Step7Kindex}
//   - The set of route paths is exactly {'/', '/step-0-cartographer', '/step-1a-constrain', '/step-1b-ledger', '/step-2a-pact', '/step-2b-advocate', '/step-3-arbiter', '/step-4-baton', '/step-5a-sentinel', '/step-5b-chronicler', '/step-5c-stigmergy', '/step-6-apprentice', '/step-7-kindex'}
//   - All route paths are unique within the manifest
//   - All route labels are non-empty strings
//   - PAGE_COMPONENTS map has an entry for every PageComponentKey — enforced by TypeScript Record type at compile time
//   - ROUTE_MANIFEST is readonly — no runtime mutation allowed
//   - src/routes.ts has zero React component imports — it is a pure data module
//   - App component is exported as both named export and default export from App.tsx
//   - Entry point main.tsx renders App inside React.StrictMode
//   - Route manifest ordering follows navigation order: Home first, then steps 0 through 7 in ascending numeric/alpha order

/** Discriminator enum identifying each of the 13 page components. */
export type PageComponentKey = "Home" | "Cartographer" | "Constrain" | "Ledger" | "Pact" | "Advocate" | "Arbiter" | "Baton" | "Sentinel" | "Chronicler" | "Stigmergy" | "Apprentice" | "Kindex";

/** A single route definition consumed by both the router configuration and the Sidebar navigation. */
export interface RouteEntry {
  path: string;  // required, URL path segment, e.g. '/step-0-cartographer' or '/' for home.
  label: string;  // required, Human-readable navigation label shown in the Sidebar, e.g. 'Step 0 — Cartographer'.
  componentKey: PageComponentKey;  // required, Lookup key that maps this route to its lazy-loaded or statically-imported page component.
}

/** A validated URL path string. Must start with '/' and contain only lowercase alphanumeric characters, hyphens, and forward slashes. Matches the AS3 slug pattern. */
export type RoutePath = unknown;

/** A validated non-empty string used as the sidebar display label for a route. */
export type RouteLabel = unknown;

/** Ordered array of all 13 route entries; single source of truth for navigation and routing. */
export type RouteManifest = RouteEntry[];

/** Record<PageComponentKey, React.ComponentType> — exhaustive lookup map from every PageComponentKey variant to its corresponding React page component. Defined in App.tsx. TypeScript compiler enforces that every enum variant has a mapping. */
export interface PageComponentMap {
  Home: ReactComponentType;  // required, HomePage component
  Step0Cartographer: ReactComponentType;  // required, Step0CartographerPage component
  Step1aConstrain: ReactComponentType;  // required, Step1aConstrainPage component
  Step1bLedger: ReactComponentType;  // required, Step1bLedgerPage component
  Step2aPact: ReactComponentType;  // required, Step2aPactPage component
  Step2bAdvocate: ReactComponentType;  // required, Step2bAdvocatePage component
  Step3Arbiter: ReactComponentType;  // required, Step3ArbiterPage component
  Step4Baton: ReactComponentType;  // required, Step4BatonPage component
  Step5aSentinel: ReactComponentType;  // required, Step5aSentinelPage component
  Step5bChronicler: ReactComponentType;  // required, Step5bChroniclerPage component
  Step5cStigmergy: ReactComponentType;  // required, Step5cStigmergyPage component
  Step6Apprentice: ReactComponentType;  // required, Step6ApprenticePage component
  Step7Kindex: ReactComponentType;  // required, Step7KindexPage component
}

/** Opaque reference to React.ComponentType — a function or class component. Not validated at the contract level; TypeScript compiler enforces component type compatibility. */
export type ReactComponentType = unknown;

/** Props for the App component. Empty — App takes no props as it is the root component. */
export interface AppProps {
}

/** Opaque React.ReactElement returned by component render functions. */
export type ReactElement = unknown;

/** Auto-stubbed type — referenced but not defined in contract 'app_routing' */
export interface string {
}

/**
 * Returns the ROUTE_MANIFEST constant — the canonical readonly array of all 13 RouteEntry objects. This is a module-level constant export from src/routes.ts, modeled here as a pure accessor for contract verification. The manifest is the single source of truth for all route paths, labels, and component keys consumed by App.tsx and shared_components (Sidebar).
 *
 * @postcondition returned array has exactly 13 entries
 * @postcondition every PageComponentKey variant appears exactly once across all entries
 * @postcondition all path values are unique (no duplicates)
 * @postcondition all label values are non-empty strings
 * @postcondition paths match the canonical set: '/', '/step-0-cartographer', '/step-1a-constrain', '/step-1b-ledger', '/step-2a-pact', '/step-2b-advocate', '/step-3-arbiter', '/step-4-baton', '/step-5a-sentinel', '/step-5b-chronicler', '/step-5c-stigmergy', '/step-6-apprentice', '/step-7-kindex'
 * @postcondition array order matches navigation order: Home first, then steps 0 through 7 in ascending order
 * @sideEffects none
 * @idempotent yes
 */
export function getRouteManifest(): RouteManifest;

/**
 * Root React component exported from src/App.tsx as both named and default export. Renders <BrowserRouter> wrapping <PageLayout routes={ROUTE_MANIFEST}> which in turn wraps <Routes> containing one <Route> element per ROUTE_MANIFEST entry. Each Route's element is resolved by looking up the entry's componentKey in the PAGE_COMPONENTS map (Record<PageComponentKey, React.ComponentType>). The component map is compile-time exhaustive — every PageComponentKey variant must have a corresponding component import.
 *
 * @precondition react-router-dom BrowserRouter (or MemoryRouter in tests) is available in the render tree or provided by this component
 * @precondition all 13 page components are importable from page_components dependency
 * @precondition PageLayout component is importable from shared_components dependency
 * @postcondition renders a BrowserRouter at the root
 * @postcondition renders PageLayout with the full ROUTE_MANIFEST passed as the routes prop
 * @postcondition renders exactly 13 Route elements inside a Routes container
 * @postcondition each Route path matches the corresponding ROUTE_MANIFEST entry path
 * @postcondition each Route element renders the component resolved from PAGE_COMPONENTS[entry.componentKey]
 * @postcondition navigating to any manifest path renders without throwing
 * @throws missing_page_component (TypeScriptCompileError) - A PageComponentKey variant exists in the manifest but has no entry in PAGE_COMPONENTS (compile-time TypeScript error, not a runtime error)
 *   message: Property 'X' is missing in type — Record<PageComponentKey, React.ComponentType> requires all enum variants
 * @throws unmatched_route (NoMatchingRoute) - User navigates to a URL path not present in ROUTE_MANIFEST
 *   behavior: react-router-dom renders no matching Route; no explicit fallback 404 is defined in this contract version
 * @sideEffects none
 * @idempotent yes
 */
export function App(): ReactElement;

/**
 * Minimal entry point function in src/main.tsx. Calls ReactDOM.createRoot on document.getElementById('root') and renders <React.StrictMode><App /></React.StrictMode>. This is the bootstrap function invoked by the Vite dev server and production build.
 *
 * @precondition document contains an element with id='root'
 * @precondition ReactDOM is available (react-dom/client)
 * @postcondition React root is created and mounted on #root element
 * @postcondition App component is rendered inside React.StrictMode
 * @throws missing_root_element (TypeError) - document.getElementById('root') returns null
 *   message: Cannot call createRoot on null — #root element not found in document
 * @sideEffects none
 * @idempotent no
 */
export function renderEntryPoint(): null;

/**
 * Constructs the PAGE_COMPONENTS constant: Record<PageComponentKey, React.ComponentType>. Defined as a module-level constant in App.tsx mapping every PageComponentKey enum variant to its imported page component. TypeScript's Record type enforces compile-time exhaustiveness — omitting any variant is a type error. Modeled as a function for contract verification purposes.
 *
 * @precondition all 13 page components are imported from page_components dependency
 * @postcondition returned map contains exactly 13 entries
 * @postcondition every PageComponentKey variant is a key in the map
 * @postcondition every value is a valid React.ComponentType (function or class component)
 * @postcondition map keys correspond 1:1 with ROUTE_MANIFEST componentKey values
 * @throws missing_import (ModuleNotFoundError) - A page component module fails to resolve at build time
 *   message: Cannot find module 'page_components/XxxPage' — ensure page_components dependency exports the component
 * @sideEffects none
 * @idempotent yes
 */
export function buildPageComponentMap(): PageComponentMap;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['PageComponentKey', 'RouteEntry', 'RouteManifest', 'PageComponentMap', 'AppProps', 'getRouteManifest', 'App', 'TypeScriptCompileError', 'NoMatchingRoute', 'renderEntryPoint', 'buildPageComponentMap', 'ModuleNotFoundError']
