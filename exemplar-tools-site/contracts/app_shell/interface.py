# === App Shell, Routing & Layout (app_shell) v1 ===
#  Dependencies: data_layer
# Top-level application shell comprising the Convex real-time provider, React Router v6 route tree, responsive sidebar layout with mobile hamburger toggle, and animated page transitions. Owns route definitions, tool-slug validation, sidebar rendering, and the fade-in animation/background-grid visual layers. Delegates page content to HomePage and ToolPage via Outlet. Dynamic accent colors applied via inline style props; Google Fonts loaded via link tags in index.html.

# Module invariants:
#   - Exactly one ConvexReactClient instance exists per application lifecycle, instantiated in src/lib/convexClient.ts.
#   - ROUTES object and TOOL_SLUGS array are frozen at module load; no runtime mutation is possible.
#   - TOOL_SLUGS.length === 11 — one entry per documented tool.
#   - The route tree contains exactly two leaf routes under the Layout route: index (HomePage) and :toolSlug (ToolPage).
#   - sidebarOpen state is false on initial render and resets to false on any navigation.
#   - Fade-in animation (animate-fadeIn) replays on every route change because the wrapper div is keyed on location.pathname.
#   - Active sidebar item is highlighted using the tool's accentColor applied via inline style, never via dynamic Tailwind class generation.
#   - On viewports < 768px the sidebar is hidden behind a hamburger toggle; on viewports >= 768px the sidebar is always visible and the hamburger is hidden.
#   - Background grid pattern is rendered on every page (applied to layout wrapper, not per-page).
#   - An unrecognized :toolSlug parameter renders the NotFoundFallback, not a crash.

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

HexColorString = primitive  # A CSS hex color string (e.g. '#4F46E5'). Validated by regex. Used for tool accent colors applied via inline style.

ConvexUrl = primitive  # A validated Convex deployment URL string. Must be an HTTPS URL ending with .convex.cloud or matching local dev patterns.

class SidebarItem:
    """Derived view-model for a single sidebar navigation entry, projected from ToolDef."""
    slug: ToolSlug                           # required, Route parameter for navigation link.
    name: string                             # required, Display name shown in the sidebar.
    step: StepNumber                         # required, Step number rendered as a badge in the sidebar row.
    accentColor: HexColor                    # required, Accent color used to highlight the active sidebar item.

class SidebarProps:
    """Props interface for the Sidebar component."""
    items: list                              # required, Ordered list of all 11 tool entries to render in the sidebar.
    currentSlug: ToolSlug = null             # optional, Currently active tool slug, or null if on the home page. Determines which item receives accent-color highlighting.
    onNavigate: str                          # required, Callback invoked after any sidebar navigation link is clicked. Used by Layout to close the mobile sidebar.

class RoutesObject:
    """Frozen object containing all route path constants."""
    HOME: str                                # required, custom(value === '/'), Home page path. Always '/'.
    TOOL: str                                # required, custom(value === '/:toolSlug'), Dynamic tool page route pattern. Always '/:toolSlug'.

class FadeInKeyframes:
    """Tailwind keyframe definition for the animate-fadeIn utility class. Defined in tailwind.config.ts extend.keyframes.fadeIn."""
    from_opacity: float                      # required, custom(value === 0), Starting opacity value.
    to_opacity: float                        # required, custom(value === 1), Ending opacity value.
    duration: str                            # required, custom(value === '200ms'), Animation duration string.
    easing: str                              # required, custom(value === 'ease-out'), Animation timing function.

class TailwindFontConfig:
    """Font family extension in tailwind.config.ts for the Instrument Serif typeface."""
    serif: list                              # required, Font stack for the serif family key. Must be ['Instrument Serif', 'serif'].

class GoogleFontLink:
    """Descriptor for a Google Fonts <link> tag to be placed in index.html."""
    href: str                                # required, regex(^https://fonts\.googleapis\.com/css2\?family=.+&display=swap$), Full Google Fonts CSS2 URL including family and display=swap parameters.
    preconnect_origins: list                 # required, Origins requiring preconnect hints. Must include 'https://fonts.googleapis.com' and 'https://fonts.gstatic.com'.

StepNumber = primitive  # Integer 1–11 representing the tool's position in the exemplar.tools workflow order.

HexColor = primitive  # CSS hex color string (e.g. '#00e5ff') used for per-tool accent theming.

class string:
    """Auto-stubbed type — referenced but not defined in contract 'app_shell'"""
    pass

def createConvexClient() -> any:
    """
    Reads VITE_CONVEX_URL from import.meta.env, validates it is a non-empty string, and returns a singleton ConvexReactClient instance. Throws at module load time if the env var is missing or empty, preventing silent misconfiguration.

    Preconditions:
      - import.meta.env.VITE_CONVEX_URL is defined and is a non-empty string matching ConvexUrl validation.

    Postconditions:
      - Returns a ConvexReactClient instance connected to the specified deployment URL.
      - Subsequent calls return the same instance (module-level singleton).

    Errors:
      - missing_convex_url (Error): import.meta.env.VITE_CONVEX_URL is undefined, null, or empty string.
          message: VITE_CONVEX_URL environment variable is not set. Add it to your .env.local file.

    Side effects: none
    Idempotent: yes
    """
    ...

def isValidToolSlug(
    value: str,
) -> bool:
    """
    Type guard function that narrows an arbitrary string to the ToolSlug union type. Checks membership in the frozen TOOL_SLUGS array via Array.prototype.includes.

    Postconditions:
      - Returns true if and only if value is one of the 11 ToolSlug variants.
      - When true, TypeScript narrows value to type ToolSlug in the calling scope.

    Side effects: none
    Idempotent: yes
    """
    ...

def toolPath(
    slug: ToolSlug,
) -> str:
    """
    Constructs a resolved route path string for a given tool slug. Replaces the :toolSlug parameter in ROUTES.TOOL with the provided slug value. Used for programmatic navigation and NavLink href generation.

    Preconditions:
      - slug is a valid ToolSlug (one of the 11 variants).

    Postconditions:
      - Returned string matches the pattern '/[a-z0-9-]+' (leading slash, then the kebab-case slug).
      - Returned string equals '/' + slug.

    Side effects: none
    Idempotent: yes
    """
    ...

def renderApp() -> any:
    """
    Top-level App component render function (src/App.tsx default export). Returns the JSX tree: ConvexProvider(client) > BrowserRouter > Routes > Route(path='/', element=Layout) with children Route(index, element=HomePage) and Route(path=':toolSlug', element=ToolPage). No props.

    Preconditions:
      - ConvexReactClient singleton has been successfully created (VITE_CONVEX_URL was valid).
      - HomePage and ToolPage components are importable from their respective modules.

    Postconditions:
      - Renders a single ConvexProvider wrapping the entire route tree.
      - All routes are reachable: '/' renders HomePage inside Layout, '/:toolSlug' renders ToolPage inside Layout.
      - No props are required to mount this component.

    Errors:
      - convex_client_unavailable (Error): createConvexClient threw because VITE_CONVEX_URL was missing.
          message: App cannot render: Convex client failed to initialize.

    Side effects: none
    Idempotent: yes
    """
    ...

def renderLayout() -> any:
    """
    Layout component render function (src/components/Layout.tsx default export). Manages mobile sidebar toggle state. Reads current location via useLocation and current toolSlug via useParams. Imports ToolDefList from data_layer and projects it to SidebarItem[]. Renders: background grid layer (fixed, z-0), Sidebar (fixed, z-20), hamburger toggle button (md:hidden, z-30), main content area with <div key={location.pathname} className='animate-fadeIn'><Outlet /></div>.

    Preconditions:
      - Component is rendered as a Route element within BrowserRouter (useLocation and useParams are available).
      - ToolDefList is importable from data_layer and contains exactly 11 entries.

    Postconditions:
      - sidebarOpen is false on initial mount.
      - sidebarOpen resets to false whenever location.pathname changes.
      - Outlet wrapper div has key={location.pathname}, causing remount and fade-in replay on route change.
      - Background grid pattern div is rendered behind all content.
      - Sidebar receives correctly projected SidebarItem[] with stepNumber, label, slug, and accentColor.
      - On screens < 768px, sidebar is conditionally visible based on sidebarOpen state.
      - On screens >= 768px, sidebar is always visible and hamburger button is hidden.

    Errors:
      - tool_def_list_empty (Error): ToolDefList import resolves to an empty array (data_layer misconfiguration).
          message: ToolDefList is empty. Sidebar cannot render without tool definitions.

    Side effects: none
    Idempotent: yes
    """
    ...

def renderSidebar(
    items: list,
    currentSlug: ToolSlug = null,
    onNavigate: str,
) -> any:
    """
    Sidebar presentational component (src/components/Sidebar.tsx default export). Renders the 'exemplar.tools' text logo as a NavLink to '/', followed by an ordered list of SidebarItem entries. Each entry shows a step-number badge and the tool label. The active entry (matching currentSlug) is highlighted using inline style with the item's accentColor. Calls onNavigate after any link click to allow the parent to close the mobile sidebar.

    Preconditions:
      - items array is non-empty and contains exactly 11 SidebarItem entries.
      - If currentSlug is not null, it matches one of the items' slug fields.

    Postconditions:
      - Logo link navigates to '/' and triggers onNavigate.
      - Each tool entry is rendered in items array order with stepNumber badge and label.
      - Exactly one entry (or zero, if currentSlug is null) has accent-color inline styling.
      - Active item's background/border/text color uses accentColor from the matching SidebarItem, applied via inline style attribute.
      - onNavigate is called exactly once per link click.

    Side effects: none
    Idempotent: yes
    """
    ...

def projectToolDefToSidebarItem(
    toolDef: any,
) -> SidebarItem:
    """
    Pure mapping function that transforms a ToolDef (from data_layer) into a SidebarItem view-model. Extracts slug, name (as label), stepNumber, and accentColor. May be inlined in Layout or extracted as a helper.

    Preconditions:
      - toolDef has non-null slug, name, stepNumber, and accentColor fields.
      - toolDef.slug is a valid ToolSlug.
      - toolDef.stepNumber is between 1 and 11 inclusive.

    Postconditions:
      - Returned SidebarItem.slug === toolDef.slug.
      - Returned SidebarItem.label === toolDef.name.
      - Returned SidebarItem.stepNumber === toolDef.stepNumber.
      - Returned SidebarItem.accentColor === toolDef.accentColor.

    Side effects: none
    Idempotent: yes
    """
    ...

# ── REQUIRED EXPORTS ──────────────────────────────────
# Your implementation module MUST export ALL of these names
# with EXACTLY these spellings. Tests import them by name.
# __all__ = ['ToolSlug', 'SidebarItem', 'SidebarProps', 'RoutesObject', 'FadeInKeyframes', 'TailwindFontConfig', 'GoogleFontLink', 'string', 'createConvexClient', 'Error', 'isValidToolSlug', 'toolPath', 'renderApp', 'renderLayout', 'renderSidebar', 'projectToolDefToSidebarItem']
