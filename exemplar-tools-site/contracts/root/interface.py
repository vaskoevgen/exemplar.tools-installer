# === Root (root) v1 ===
#  Dependencies: app_shell, data_layer, home_page, project_scaffold, tests, tool_page
# Top-level application entry point comprising two files: src/Root.tsx (~30-50 lines) and src/main.tsx (~5 lines). Root is a zero-props React functional component that reads the VITE_CONVEX_URL environment variable, validates its presence, instantiates the ConvexReactClient singleton via app_shell's createConvexClient, and composes the outermost provider tree: StrictMode → ErrorBoundary → ConvexProvider → renderApp(). If VITE_CONVEX_URL is missing or invalid, Root renders an inline error fallback instead of crashing. All routing, layout, sidebar, page content, and data domain logic is fully delegated to app_shell and its transitive dependencies (home_page, tool_page, data_layer). src/main.tsx is the imperative Vite entry point that calls ReactDOM.createRoot on the #root DOM element and renders <Root />. Root owns zero data domains and introduces no canonical types beyond its local ErrorFallbackProps.

# Module invariants:
#   - Exactly two source files comprise this component: src/Root.tsx (~30-50 lines) and src/main.tsx (~5-10 lines).
#   - Root is a zero-props React functional component; it accepts no external configuration at render time.
#   - The provider nesting order is always: StrictMode → ErrorBoundary → ConvexProvider → renderApp(). No other nesting is valid.
#   - Exactly one ConvexReactClient singleton exists per application lifecycle, created at module load time in src/Root.tsx (delegated to app_shell's createConvexClient).
#   - Root owns zero data domains — all routing, layout, page content, and data logic is delegated to child subsystem contracts.
#   - If VITE_CONVEX_URL is missing, Root renders an inline error view; it never throws an unhandled exception to the browser console.
#   - ErrorBoundary catches all unhandled render errors from the entire child tree (app_shell layout, home_page, tool_page, data_layer hooks).
#   - No class components are used; Root and ErrorFallback are both React functional components with TypeScript type annotations.
#   - All styling uses Tailwind CSS v3 utility classes; no custom CSS is introduced by this component.
#   - src/main.tsx uses ReactDOM.createRoot (React 18 concurrent API), never ReactDOM.render (legacy API).
#   - src/main.tsx performs a non-null assertion on document.getElementById('root') — the #root div is guaranteed by project_scaffold's index.html.
#   - react-error-boundary >= 4.0 is a runtime dependency declared in package.json dependencies (not devDependencies).

ReactElement = primitive  # Opaque type representing a React JSX element (React.ReactElement / JSX.Element). Return type of all React functional components.

DOMContainer = primitive  # An HTMLElement retrieved from document.getElementById. Specifically the #root div element declared in index.html.

ConvexReactClient = primitive  # Singleton Convex client instance returned by createConvexClient from app_shell. Passed to ConvexProvider as the client prop.

class ErrorFallbackProps:
    """Props interface for the ErrorFallback component, conforming to the FallbackProps shape required by react-error-boundary's ErrorBoundary fallbackRender or FallbackComponent prop."""
    error: Error                             # required, The Error object caught by the ErrorBoundary. Displayed to the user with error.message.
    resetErrorBoundary: ResetFunction        # required, Callback to reset the ErrorBoundary state and re-attempt rendering the child tree. Wired to a retry button in the fallback UI.

Error = primitive  # Standard JavaScript Error object with a message property. Caught by ErrorBoundary and surfaced to ErrorFallback.

ResetFunction = primitive  # A zero-argument void callback function (() => void). Provided by react-error-boundary to reset the boundary state.

class ViteEnvMeta:
    """Typed subset of import.meta.env relevant to the Root component. Used to model the environment variable read at module load time."""
    VITE_CONVEX_URL: str = None              # optional, regex(^https://.+\.convex\.cloud$|^https?://localhost:\d+$), Convex deployment URL. May be undefined if not set in .env.local, in which case Root renders an error fallback.

class RootRenderTarget:
    """Configuration for the imperative mount point in src/main.tsx."""
    elementId: str                           # required, custom(value === 'root'), DOM element ID to mount the React root into. Always 'root'.

def Root() -> ReactElement:
    """
    Zero-props top-level React functional component exported as default from src/Root.tsx. Composes the outermost provider tree: React.StrictMode wrapping an ErrorBoundary (from react-error-boundary) wrapping ConvexProvider (with the singleton ConvexReactClient) wrapping the result of app_shell's renderApp(). If createConvexClient threw at module load time (VITE_CONVEX_URL missing), Root catches the module-level error and renders an inline configuration error message instead of the provider tree. The ErrorBoundary catches any runtime errors from the child tree (routing, layout, pages) and delegates to the ErrorFallback component. Root contains no routing logic, no layout logic, no data fetching, and no domain knowledge — it is purely a composition root.

    Preconditions:
      - React 18 runtime is available (react and react-dom packages installed).
      - react-error-boundary >= 4.0 is installed as a runtime dependency.
      - convex/react package is installed and exports ConvexProvider.
      - app_shell module is importable and exports createConvexClient and renderApp.
      - index.html contains <div id='root'></div> for the React mount point.
      - Tailwind CSS v3 stylesheet is loaded (via src/index.css processed by PostCSS).
      - Google Fonts (Instrument Serif, JetBrains Mono, Inter) are loaded via <link> tags in index.html.

    Postconditions:
      - When VITE_CONVEX_URL is defined and valid: renders StrictMode > ErrorBoundary > ConvexProvider > renderApp() tree.
      - When VITE_CONVEX_URL is missing or invalid: renders a full-page configuration error message with instructions to set VITE_CONVEX_URL in .env.local. No ConvexProvider or router tree is mounted.
      - ErrorBoundary wraps the entire ConvexProvider + app tree so that any unhandled render error is caught and displays ErrorFallback.
      - Exactly one ConvexReactClient instance exists per application lifecycle (module-level singleton from createConvexClient).
      - No props are required to mount this component.
      - Component renders without runtime errors when all preconditions are met.

    Errors:
      - missing_convex_url (render_fallback): import.meta.env.VITE_CONVEX_URL is undefined, null, or empty string at module load time, causing createConvexClient to throw.
          behavior: Root catches the module-level initialization error and renders an inline error view with the message 'VITE_CONVEX_URL environment variable is not set. Add it to your .env.local file.' and a dark-themed full-page container. No ConvexProvider, router, or page content is mounted.
          recovery: User must set VITE_CONVEX_URL in .env.local and restart the dev server.
      - invalid_convex_url (render_fallback): VITE_CONVEX_URL is set but does not match the expected URL pattern (not a valid Convex deployment URL).
          behavior: createConvexClient may throw or ConvexProvider may fail to connect. ErrorBoundary catches the resulting render error and displays ErrorFallback.
          recovery: User must correct the VITE_CONVEX_URL value in .env.local.
      - child_tree_render_error (ErrorBoundary): Any component in the app_shell, home_page, or tool_page tree throws an unhandled error during rendering.
          behavior: ErrorBoundary catches the error and renders ErrorFallback with the error message and a retry button that calls resetErrorBoundary.
          component: ErrorFallback
      - root_dom_element_missing (TypeError): document.getElementById('root') returns null in src/main.tsx because index.html is missing the #root div.
          message: Cannot call createRoot on null. Ensure index.html contains <div id="root"></div>.
          file: src/main.tsx

    Side effects: none
    Idempotent: yes
    """
    ...

def ErrorFallback(
    error: Error,
    resetErrorBoundary: ResetFunction,
) -> ReactElement:
    """
    Presentational React functional component rendered by the ErrorBoundary when an unhandled error is caught from the child tree. Displays the error message in a dark-themed full-page container with a 'Try Again' button that calls resetErrorBoundary to re-attempt rendering. Styled with Tailwind CSS utility classes. Exported as a named export from src/Root.tsx for testability.

    Preconditions:
      - error is a valid Error object with a non-null message property.
      - resetErrorBoundary is a callable function provided by react-error-boundary.

    Postconditions:
      - Renders a full-viewport container (min-h-screen) with dark background matching the project's bg-background (#0a0a0a) color.
      - Displays a heading indicating an error occurred (e.g. 'Something went wrong').
      - Displays error.message in a code-styled block for debugging context.
      - Renders a 'Try Again' button that calls resetErrorBoundary exactly once on click.
      - All styling uses Tailwind CSS utility classes; no custom CSS.
      - Component is accessible: button is focusable, error text is readable.

    Errors:
      - null_error (render_fallback): error parameter is null or undefined (should not occur with react-error-boundary >= 4.0 but defensively handled).
          behavior: Renders a generic 'An unknown error occurred' message without the error details block.

    Side effects: none
    Idempotent: yes
    """
    ...

def mountRoot() -> None:
    """
    Imperative entry point function in src/main.tsx. Retrieves the #root DOM element via document.getElementById('root'), asserts it is non-null, calls ReactDOM.createRoot to create a React 18 concurrent root, and renders <Root /> into it. This is the singular bootstrap call for the entire application. The file is referenced by index.html via <script type='module' src='/src/main.tsx'>.

    Preconditions:
      - index.html has been loaded by the browser and contains <div id='root'></div>.
      - src/main.tsx is loaded as an ES module via <script type='module'>.
      - react-dom/client exports createRoot (React 18+).
      - Root component is importable from src/Root.tsx.

    Postconditions:
      - ReactDOM.createRoot is called with document.getElementById('root') as the container.
      - root.render(<Root />) is called exactly once.
      - The Root component tree begins rendering into the #root DOM element.
      - No other components are rendered outside the Root tree.

    Errors:
      - root_element_not_found (TypeError): document.getElementById('root') returns null.
          message: Target container is not a DOM element. Ensure index.html contains <div id='root'></div>.
      - react_dom_import_failed (ModuleNotFoundError): react-dom/client module cannot be resolved (package not installed).
          module: react-dom/client
          message: Cannot resolve react-dom/client. Run bun install to install dependencies.

    Side effects: Mutates the DOM by mounting the React tree into the #root element.
    Idempotent: no
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ErrorFallbackProps', 'ViteEnvMeta', 'RootRenderTarget', 'Root', 'render_fallback', 'ErrorBoundary', 'ErrorFallback', 'mountRoot', 'ModuleNotFoundError']
