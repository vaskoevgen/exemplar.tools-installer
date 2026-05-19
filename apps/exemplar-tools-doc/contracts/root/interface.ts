// === Root (root) v1 ===
//  Dependencies: page_content, pipeline_diagram, project_scaffold, routing_and_layout, shared_ui
// Thin orchestration layer for the exemplar.tools documentation website. Composes child modules (project_scaffold, routing_and_layout, page_content) to wire all 13 page components into a router and mount the React application into the DOM. Owns no domain types — all canonical types are defined by child modules. Consists of two files: src/root.ts (exports initApp) and src/main.tsx (side-effect entry point that calls initApp, no exports).

// Module invariants:
//   - Root owns zero domain types — all types (StepId, StepLabel, RouteSlug, StepContent, RouteEntry, etc.) are defined by and imported from child modules.
//   - Root does not re-export any child module types or constants — consumers import directly from the owning child module.
//   - The total number of registered routes is exactly 13: 1 home route + 12 step routes.
//   - src/main.tsx has zero named exports — it is a side-effect-only entry point.
//   - src/root.ts exports exactly one named runtime export: initApp.
//   - initApp calls createAppRouter exactly once and mountApp exactly once, in that order.
//   - Root has no direct runtime dependency on shared_ui or pipeline_diagram — those are consumed transitively through page_content and routing_and_layout.
//   - All slug handling is delegated to ensureLeadingSlash from routing_and_layout — root never manipulates slug strings directly.
//   - All source files use TypeScript strict mode, named exports only, and 'export type { }' for type-only exports per project standards.

/** TypeScript void return type, indicating the function returns no value. */
export type void = unknown;

/** Opaque React Router browser router instance returned by createBrowserRouter / createAppRouter. Passed to RouterProvider for mounting. */
export type RouterInstance = unknown;

/** React.ReactElement / JSX.Element returned by React functional components. */
export type ReactElement = unknown;

/**
 * Composition entry point that wires all child modules together and mounts the application. Imports createAppRouter from routing_and_layout (which internally references all 13 page components from page_content via ROUTE_ENTRY_LIST and the Layout/Sidebar shell). Calls createAppRouter() to build the complete route tree with all 13 routes (home + 12 steps). Then calls mountApp from project_scaffold, which creates a React root on the #root DOM element and renders the application with the router. This function is the single point of integration — it ensures that routing_and_layout's createAppRouter has already wired every page component to its route, so root merely invokes the composition. File: src/root.ts.
 *
 * @precondition DOM element with id='root' exists in the document (provided by index.html from project_scaffold)
 * @precondition All child module imports resolve successfully: project_scaffold.mountApp, routing_and_layout.createAppRouter
 * @precondition routing_and_layout.createAppRouter internally references all 13 page components from page_content
 * @precondition React 18 runtime and react-dom/client are available
 * @postcondition createAppRouter() from routing_and_layout has been called exactly once
 * @postcondition mountApp() from project_scaffold has been called exactly once after createAppRouter completes
 * @postcondition The React application is mounted into the #root DOM element with the complete router containing all 13 routes
 * @postcondition All 13 page components (HomePage, CartographerPage, ConstrainPage, LedgerPage, PactPage, AdvocatePage, ArbiterPage, BatonPage, SentinelPage, ChroniclerPage, StigmergyPage, ApprenticePage, KindexPage) are reachable via their registered routes
 * @throws missing_root_element (DOMException) - DOM element with id='root' does not exist when mountApp is called
 *   message: Cannot find DOM element with id='root'. Ensure index.html contains <div id="root"></div>.
 *   selector: #root
 * @throws router_creation_failure (ModuleNotFoundError) - createAppRouter throws because a required page component import is missing or ROUTE_ENTRY_LIST is malformed
 *   message: Failed to create app router. A page component or route entry could not be resolved.
 * @throws mount_failure (RuntimeError) - mountApp throws because React root creation fails (e.g., createRoot is unavailable)
 *   message: Failed to mount React application. Ensure react-dom/client is installed and createRoot is available.
 * @sideEffects Mounts React application tree into DOM #root element, Triggers React Router initialization with browser history
 * @idempotent no
 */
export function initApp(): void;

/**
 * Side-effect entry point module at src/main.tsx. Imports initApp from src/root.ts and calls it immediately. Also imports src/index.css for Tailwind style injection. This module has zero named exports — it is referenced by index.html as <script type='module' src='/src/main.tsx'> and executes on load. This is not a callable function but a module-level side effect.
 *
 * @precondition src/root.ts exports initApp as a named export
 * @precondition src/index.css exists and contains valid Tailwind @tailwind directives
 * @precondition The module is loaded by the browser via the script tag in index.html
 * @postcondition initApp() has been called exactly once
 * @postcondition Tailwind base/components/utilities styles are injected into the document via the CSS import side effect
 * @postcondition No named exports exist on this module
 * @throws init_app_import_failure (ImportError) - Named export initApp cannot be resolved from src/root.ts
 *   message: Cannot import { initApp } from './root'. Ensure root.ts exports initApp as a named export.
 *   module: ./root
 *   export: initApp
 * @throws css_import_failure (ImportError) - src/index.css cannot be resolved or is malformed
 *   message: Cannot import './index.css'. Ensure the file exists and contains valid CSS.
 *   module: ./index.css
 * @sideEffects Calls initApp() which mounts the React application, Imports CSS which injects Tailwind styles into the document
 * @idempotent no
 */
export function main(): void;

// -- REQUIRED EXPORTS -----------------------------------------------
// Your implementation module MUST export ALL of these names
// with EXACTLY these spellings. Tests import them by name.
// exports: ['initApp', 'DOMException', 'ModuleNotFoundError', 'main', 'ImportError']
