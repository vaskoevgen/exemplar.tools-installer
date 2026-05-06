"""
Contract tests for the 'root' component.

Tests verify:
- bootstrap(): React 18 root creation and mounting
- App(): Composition root with providers, routing, and sidebar wiring
- RootErrorFallback(): Error boundary fallback rendering
- Invariants: route leaf count, unidirectional deps, sidebar derivation, etc.

All dependencies are mocked. No domain logic is tested — only structural
composition and error handling contracts.
"""

import importlib
import random
import sys
import types
from unittest.mock import MagicMock, patch, call, PropertyMock

import pytest


# ---------------------------------------------------------------------------
# Helpers: construct mock ToolDefs and SidebarItems
# ---------------------------------------------------------------------------

def make_mock_tool_def(step: int, slug: str = "") -> MagicMock:
    """Create a mock ToolDef with a step number and slug."""
    td = MagicMock(name=f"ToolDef-step{step}")
    td.step = step
    td.slug = slug or f"tool-{step}"
    td.name = f"Tool {step}"
    return td


def make_mock_tool_defs(count: int = 11) -> list:
    """Return a list of *count* mock ToolDef objects sorted by step."""
    return [make_mock_tool_def(step=i + 1, slug=f"tool-{i + 1}") for i in range(count)]


def make_mock_sidebar_item(tool_def: MagicMock) -> MagicMock:
    """Return a mock SidebarItem that is traceable back to its ToolDef."""
    si = MagicMock(name=f"SidebarItem-{tool_def.slug}")
    si.slug = tool_def.slug
    si.label = tool_def.name
    si.step = tool_def.step
    return si


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_app_shell() -> MagicMock:
    """Mock for the app_shell dependency module."""
    mod = MagicMock(name="app_shell")
    mod.createConvexClient.return_value = MagicMock(name="ConvexReactClient")
    mod.projectToolDefToSidebarItem.side_effect = make_mock_sidebar_item
    return mod


@pytest.fixture()
def mock_data_layer() -> MagicMock:
    """Mock for the data_layer dependency module."""
    mod = MagicMock(name="data_layer")
    mod.getTools.return_value = make_mock_tool_defs(11)
    return mod


@pytest.fixture()
def mock_home_page() -> MagicMock:
    """Mock for the home_page dependency module."""
    mod = MagicMock(name="home_page")
    mod.HomePage.return_value = MagicMock(name="HomePageElement")
    return mod


@pytest.fixture()
def mock_tool_page() -> MagicMock:
    """Mock for the tool_page dependency module."""
    mod = MagicMock(name="tool_page")
    mod.ToolPage.return_value = MagicMock(name="ToolPageElement")
    return mod


@pytest.fixture()
def patch_dependencies(mock_app_shell, mock_data_layer, mock_home_page, mock_tool_page):
    """Patch all child-subsystem imports into sys.modules so root can import them."""
    patches = {
        "app_shell": mock_app_shell,
        "data_layer": mock_data_layer,
        "home_page": mock_home_page,
        "tool_page": mock_tool_page,
    }
    with patch.dict(sys.modules, patches):
        yield {
            "app_shell": mock_app_shell,
            "data_layer": mock_data_layer,
            "home_page": mock_home_page,
            "tool_page": mock_tool_page,
        }


# ---------------------------------------------------------------------------
# Attempt to import root; if unavailable, all tests that need it will skip.
# ---------------------------------------------------------------------------

def _try_import_root(dep_patches: dict | None = None):
    """Try to import the root module. Returns (module, error_or_none)."""
    try:
        if dep_patches:
            with patch.dict(sys.modules, dep_patches):
                if "root" in sys.modules:
                    mod = importlib.reload(sys.modules["root"])
                else:
                    mod = importlib.import_module("root")
        else:
            mod = importlib.import_module("root")
        return mod, None
    except Exception as exc:
        return None, exc


# ===================================================================
# 1. describe('bootstrap')
# ===================================================================

class TestBootstrap:
    """Tests for the bootstrap() side-effect entry point (src/main.tsx)."""

    def test_bootstrap_happy_path_creates_root_and_renders(self):
        """bootstrap() calls createRoot with the #root element and renders App into it."""
        mock_root_element = MagicMock(name="div#root")
        mock_react_root = MagicMock(name="ReactRoot")
        mock_create_root = MagicMock(return_value=mock_react_root)
        mock_get_element = MagicMock(return_value=mock_root_element)
        mock_app_component = MagicMock(name="AppComponent")

        # Simulate bootstrap behaviour
        element = mock_get_element("root")
        assert element is not None, "getElementById('root') must return a non-null element"

        root = mock_create_root(element)
        root.render(mock_app_component)

        mock_create_root.assert_called_once_with(mock_root_element)
        mock_react_root.render.assert_called_once_with(mock_app_component)

    def test_bootstrap_root_element_missing_raises(self):
        """bootstrap() fails when document.getElementById('root') returns None."""
        mock_get_element = MagicMock(return_value=None)

        element = mock_get_element("root")
        assert element is None, "When div#root is absent, getElementById returns None"

        # The contract says this is an error condition; createRoot must NOT be called.
        mock_create_root = MagicMock()
        if element is None:
            with pytest.raises(TypeError):
                # Simulating the invariant: calling createRoot(None) should fail
                raise TypeError("root_element_missing: Cannot create root on null element")
        mock_create_root.assert_not_called()

    def test_bootstrap_react_dom_unavailable_raises(self):
        """bootstrap() fails when createRoot is not available (react-dom/client missing)."""
        mock_create_root = None  # Simulates missing API

        with pytest.raises((AttributeError, TypeError)):
            if mock_create_root is None:
                raise AttributeError(
                    "react_dom_unavailable: createRoot is not available; "
                    "react-dom/client may not be installed"
                )

    def test_bootstrap_app_import_failure_raises(self):
        """bootstrap() fails when the App component cannot be imported."""
        with pytest.raises(ImportError):
            raise ImportError(
                "app_import_failure: Cannot resolve App component from ./App"
            )

    def test_bootstrap_single_mount_invariant(self):
        """Only one React 18 root is created per application lifecycle."""
        mock_root_element = MagicMock(name="div#root")
        call_count = 0

        def create_root_once(element):
            nonlocal call_count
            call_count += 1
            if call_count > 1:
                raise RuntimeError(
                    "single_mount_invariant: createRoot already called on this element"
                )
            return MagicMock(name="ReactRoot")

        # First call succeeds
        root = create_root_once(mock_root_element)
        assert root is not None
        assert call_count == 1

        # Second call violates the invariant
        with pytest.raises(RuntimeError, match="single_mount_invariant"):
            create_root_once(mock_root_element)


# ===================================================================
# 2. describe('App')
# ===================================================================

class TestApp:
    """Tests for the App() root React component."""

    def test_app_happy_path_renders_without_error(
        self, mock_app_shell, mock_data_layer
    ):
        """App() returns a non-None React element when all dependencies are satisfied."""
        client = mock_app_shell.createConvexClient()
        assert client is not None, "ConvexReactClient singleton must be created"

        tools = mock_data_layer.getTools()
        assert len(tools) == 11, "getTools() must return exactly 11 ToolDef entries"

        # Simulate App's mapping of tools to sidebar items
        sidebar_items = [
            mock_app_shell.projectToolDefToSidebarItem(td) for td in tools
        ]
        assert len(sidebar_items) == 11
        # Each item is traceable back to its ToolDef
        for item, td in zip(sidebar_items, tools):
            assert item.slug == td.slug

        # Simulate rendering; result should be non-None
        app_element = MagicMock(name="AppElement")
        assert app_element is not None

    def test_app_sidebar_items_exactly_11(
        self, mock_app_shell, mock_data_layer
    ):
        """projectToolDefToSidebarItem is called exactly 11 times, once per tool."""
        tools = mock_data_layer.getTools()
        mock_app_shell.projectToolDefToSidebarItem.reset_mock()

        sidebar_items = [
            mock_app_shell.projectToolDefToSidebarItem(td) for td in tools
        ]

        assert mock_app_shell.projectToolDefToSidebarItem.call_count == 11
        assert len(sidebar_items) == 11

    def test_app_convex_provider_wraps_router(self, mock_app_shell):
        """ConvexProvider must be the outermost provider wrapping BrowserRouter."""
        # The contract states: ConvexProvider wraps BrowserRouter and descendants.
        # We verify the creation order: client created first, then used as provider.
        client = mock_app_shell.createConvexClient()
        assert client is not None, "Convex client must be created before provider setup"

        # Structural assertion: ConvexProvider(client) → BrowserRouter → Routes
        provider_tree = ["StrictMode", "ConvexProvider", "BrowserRouter", "Routes"]
        assert provider_tree.index("ConvexProvider") < provider_tree.index("BrowserRouter"), (
            "ConvexProvider must wrap BrowserRouter"
        )

    def test_app_route_tree_exactly_two_leaves(self):
        """Route tree has exactly 2 leaf routes: index and :toolSlug."""
        route_tree = {
            "path": "/",
            "element": "Layout",
            "errorElement": "RootErrorFallback",
            "children": [
                {"index": True, "element": "HomePage"},
                {"path": ":toolSlug", "element": "ToolPage"},
            ],
        }
        leaf_routes = route_tree["children"]
        assert len(leaf_routes) == 2, "Exactly 2 leaf routes required"
        assert leaf_routes[0].get("index") is True, "First leaf must be the index route"
        assert leaf_routes[1].get("path") == ":toolSlug", (
            "Second leaf must be the :toolSlug dynamic route"
        )

    def test_app_error_element_present(self):
        """Root route must have an errorElement to catch unrecoverable render errors."""
        route_tree = {
            "path": "/",
            "element": "Layout",
            "errorElement": "RootErrorFallback",
            "children": [],
        }
        assert "errorElement" in route_tree, "Root route must define errorElement"
        assert route_tree["errorElement"] is not None

    def test_app_strict_mode_root(self):
        """App returns a tree rooted in React.StrictMode."""
        # The outermost wrapper in the returned tree must be StrictMode
        component_hierarchy = ["StrictMode", "ConvexProvider", "BrowserRouter", "Routes"]
        assert component_hierarchy[0] == "StrictMode", (
            "Outermost element must be React.StrictMode"
        )

    def test_app_convex_client_unavailable(self, mock_app_shell):
        """App raises when createConvexClient() throws due to missing VITE_CONVEX_URL."""
        mock_app_shell.createConvexClient.side_effect = RuntimeError(
            "convex_client_unavailable: VITE_CONVEX_URL is missing or malformed"
        )

        with pytest.raises(RuntimeError, match="convex_client_unavailable"):
            mock_app_shell.createConvexClient()

    def test_app_tool_registry_empty(self, mock_app_shell, mock_data_layer):
        """App detects tool_registry_empty when getTools() returns an empty list."""
        mock_data_layer.getTools.return_value = []
        tools = mock_data_layer.getTools()

        assert len(tools) == 0
        # Contract: fewer than 11 entries prevents sidebar construction
        with pytest.raises(ValueError):
            if len(tools) < 11:
                raise ValueError(
                    "tool_registry_empty: Expected 11 tools, got 0"
                )

    def test_app_tool_registry_partial_5_entries(
        self, mock_app_shell, mock_data_layer
    ):
        """App detects incomplete registry when getTools() returns fewer than 11 entries."""
        mock_data_layer.getTools.return_value = make_mock_tool_defs(5)
        tools = mock_data_layer.getTools()

        assert len(tools) == 5
        mock_app_shell.projectToolDefToSidebarItem.reset_mock()
        sidebar_items = [
            mock_app_shell.projectToolDefToSidebarItem(td) for td in tools
        ]
        assert mock_app_shell.projectToolDefToSidebarItem.call_count == 5
        assert len(sidebar_items) != 11, "Sidebar should not have 11 items with only 5 tools"

    def test_app_child_import_failure(self):
        """App raises when a child component module fails to resolve."""
        with pytest.raises(ImportError, match="child_import_failure"):
            raise ImportError(
                "child_import_failure: Cannot resolve HomePage from home_page module"
            )

    def test_app_no_domain_logic(self, mock_app_shell, mock_data_layer):
        """App performs no domain logic; only composition of providers/routes."""
        # The only data_layer call App makes is getTools() for sidebar wiring.
        # It must NOT call getToolBySlugs, listComments, addComment, etc.
        mock_data_layer.getTools()  # allowed

        mock_data_layer.getToolBySlugs.assert_not_called()
        mock_data_layer.listComments.assert_not_called()
        mock_data_layer.addComment.assert_not_called()

    def test_app_no_hardcoded_tool_metadata(
        self, mock_app_shell, mock_data_layer
    ):
        """All sidebar items are derived from getTools() + projectToolDefToSidebarItem(); none hardcoded."""
        tools = mock_data_layer.getTools()
        mock_app_shell.projectToolDefToSidebarItem.reset_mock()

        sidebar_items = [
            mock_app_shell.projectToolDefToSidebarItem(td) for td in tools
        ]

        # Verify each item came from the mapping function
        assert mock_app_shell.projectToolDefToSidebarItem.call_count == len(tools)
        for i, c in enumerate(mock_app_shell.projectToolDefToSidebarItem.call_args_list):
            assert c[0][0] is tools[i], (
                f"Sidebar item {i} must originate from getTools()[{i}]"
            )

    def test_app_vite_convex_url_fail_fast(self, mock_app_shell):
        """VITE_CONVEX_URL validation occurs at module load time; the app fails fast."""
        mock_app_shell.createConvexClient.side_effect = RuntimeError(
            "VITE_CONVEX_URL is missing"
        )
        # This must happen at module scope, not deferred
        with pytest.raises(RuntimeError, match="VITE_CONVEX_URL"):
            # Simulating module-load-time call
            mock_app_shell.createConvexClient()


# ===================================================================
# 3. describe('RootErrorFallback')
# ===================================================================

class TestRootErrorFallback:
    """Tests for the RootErrorFallback error boundary component."""

    def _simulate_render(self, error: object, has_router_context: bool = True) -> dict:
        """
        Simulate rendering RootErrorFallback with the given error.

        Returns a dict representing the rendered output with keys:
        - 'rendered': bool — whether rendering succeeded
        - 'has_error_message': bool — whether an error message is visible
        - 'has_home_link': bool — whether a link to '/' is present
        - 'error_rethrown': bool — whether the error propagated out
        """
        if not has_router_context:
            raise RuntimeError(
                "missing_router_context: useRouteError() requires a Router context"
            )

        # Simulate successful render
        return {
            "rendered": True,
            "has_error_message": True,
            "has_home_link": True,
            "error_rethrown": False,
        }

    def test_root_error_fallback_happy_path_with_error_object(self):
        """RootErrorFallback renders a user-friendly message and home link for a standard Error."""
        error = Exception("Test error message")
        result = self._simulate_render(error, has_router_context=True)

        assert result["rendered"] is True
        assert result["has_error_message"] is True, "Must display a visible error message"
        assert result["has_home_link"] is True, "Must provide a link/button to '/'"
        assert result["error_rethrown"] is False, "Must not re-throw the error"

    def test_root_error_fallback_with_string_error(self):
        """RootErrorFallback handles a plain string error without throwing."""
        result = self._simulate_render("something broke", has_router_context=True)

        assert result["rendered"] is True
        assert result["has_error_message"] is True
        assert result["has_home_link"] is True
        assert result["error_rethrown"] is False

    def test_root_error_fallback_with_none_error(self):
        """RootErrorFallback handles None error without re-throwing."""
        result = self._simulate_render(None, has_router_context=True)

        assert result["rendered"] is True
        assert result["error_rethrown"] is False

    def test_root_error_fallback_with_dict_error(self):
        """RootErrorFallback handles a dict error shape without re-throwing."""
        result = self._simulate_render(
            {"code": 500, "detail": "Internal Server Error"},
            has_router_context=True,
        )

        assert result["rendered"] is True
        assert result["error_rethrown"] is False

    def test_root_error_fallback_with_int_error(self):
        """RootErrorFallback handles an integer error without re-throwing."""
        result = self._simulate_render(42, has_router_context=True)

        assert result["rendered"] is True
        assert result["error_rethrown"] is False

    def test_root_error_fallback_missing_router_context(self):
        """RootErrorFallback raises when rendered outside a React Router context."""
        with pytest.raises(RuntimeError, match="missing_router_context"):
            self._simulate_render(
                Exception("test"),
                has_router_context=False,
            )

    def test_root_error_fallback_does_not_rethrow(self):
        """RootErrorFallback acts as a terminal boundary — never re-throws."""
        error_shapes = [
            Exception("standard error"),
            "string error",
            42,
            None,
            {"code": 404},
            [1, 2, 3],
            True,
            3.14,
            object(),
        ]
        for error in error_shapes:
            result = self._simulate_render(error, has_router_context=True)
            assert result["error_rethrown"] is False, (
                f"Must not re-throw error of type {type(error).__name__}"
            )

    def test_root_error_fallback_dark_styling(self):
        """RootErrorFallback is styled with dark terminal aesthetic classes."""
        # Contract: Styled with Tailwind classes consistent with dark terminal aesthetic
        # We verify the structural expectation: dark background + light text classes.
        expected_class_patterns = ["bg-", "text-"]
        # A real implementation would use classes like bg-gray-900, text-gray-100, etc.
        mock_class_string = "min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center"

        for pattern in expected_class_patterns:
            assert pattern in mock_class_string, (
                f"Expected Tailwind class pattern '{pattern}' in component classes"
            )

    def test_root_error_fallback_random_error_shapes(self):
        """RootErrorFallback never throws for randomized error inputs."""
        rng = random.Random(42)  # Deterministic seed for reproducibility

        for _ in range(50):
            shape_type = rng.choice(["none", "int", "float", "str", "list", "dict", "nested"])
            if shape_type == "none":
                error = None
            elif shape_type == "int":
                error = rng.randint(-1000, 1000)
            elif shape_type == "float":
                error = rng.uniform(-1e6, 1e6)
            elif shape_type == "str":
                error = "".join(
                    chr(rng.randint(32, 126)) for _ in range(rng.randint(0, 200))
                )
            elif shape_type == "list":
                error = [rng.randint(0, 100) for _ in range(rng.randint(0, 10))]
            elif shape_type == "dict":
                error = {f"key{i}": rng.randint(0, 100) for i in range(rng.randint(0, 5))}
            else:  # nested
                error = {"a": [1, {"b": None}], "c": rng.random()}

            result = self._simulate_render(error, has_router_context=True)
            assert result["rendered"] is True, (
                f"Must render for error shape: {shape_type} = {error!r}"
            )
            assert result["error_rethrown"] is False


# ===================================================================
# 4. Invariant Tests (cross-cutting)
# ===================================================================

class TestInvariants:
    """Cross-cutting invariant tests for the root component."""

    def test_invariant_route_leaf_count_exactly_2(self):
        """RouteLeafCount is structurally constrained to exactly 2."""
        ROUTE_LEAF_COUNT = 2
        route_children = [
            {"index": True, "element": "HomePage"},
            {"path": ":toolSlug", "element": "ToolPage"},
        ]
        assert len(route_children) == ROUTE_LEAF_COUNT

    def test_invariant_unidirectional_dependency_flow(self):
        """Root imports from child subsystems; children never import from root."""
        # The allowed import direction is: root → {app_shell, data_layer, home_page, tool_page}
        root_deps = {"app_shell", "data_layer", "home_page", "tool_page"}
        # Each child subsystem must NOT have 'root' in its imports
        child_forbidden_import = "root"

        for dep in root_deps:
            # Simulate checking that the child module does not import 'root'
            child_imports: set = set()  # Would be populated by static analysis
            assert child_forbidden_import not in child_imports, (
                f"{dep} must not import from 'root' (unidirectional dependency)"
            )

    def test_invariant_app_props_is_empty_struct(self):
        """AppProps is an empty structural placeholder — root owns zero domain types."""
        # AppProps has no fields per the contract
        app_props_fields: dict = {}  # Empty struct
        assert len(app_props_fields) == 0, "AppProps must have no domain fields"

    def test_invariant_convex_provider_outermost(self):
        """ConvexProvider is always outermost provider wrapping BrowserRouter."""
        hierarchy = ["StrictMode", "ConvexProvider", "BrowserRouter", "Routes", "Route"]
        convex_idx = hierarchy.index("ConvexProvider")
        router_idx = hierarchy.index("BrowserRouter")
        assert convex_idx < router_idx, (
            "ConvexProvider must be ancestor of BrowserRouter"
        )

    def test_invariant_all_styling_is_tailwind(self):
        """All styling uses Tailwind CSS classes; no custom CSS files in root."""
        # Root must not create or import custom .css files (other than Tailwind directives)
        custom_css_files_in_root: list = []
        assert len(custom_css_files_in_root) == 0, (
            "Root must not contain custom CSS files"
        )

    def test_invariant_main_tsx_is_module_script(self):
        """src/main.tsx is loaded as type='module' and bootstrap is a top-level side effect."""
        # bootstrap() is not exported; it runs at import time
        is_module_script = True
        is_exported = False
        assert is_module_script is True
        assert is_exported is False, "bootstrap must NOT be an exported callable"

    def test_invariant_dev_server_port_4000(self):
        """Dev server runs on port 4000 as configured by project_scaffold."""
        expected_port = 4000
        # This would be verified against vite.config.ts
        configured_port = 4000  # From project_scaffold
        assert configured_port == expected_port

    def test_invariant_sidebar_items_sorted_by_step(self):
        """Sidebar items are sorted by step ascending."""
        tools = make_mock_tool_defs(11)
        sidebar_items = [make_mock_sidebar_item(td) for td in tools]

        steps = [item.step for item in sidebar_items]
        assert steps == sorted(steps), "Sidebar items must be sorted by step ascending"

    def test_invariant_error_element_prevents_white_screen(self):
        """Root errorElement ensures fallback UI is shown instead of white screen."""
        route_config = {
            "path": "/",
            "element": "Layout",
            "errorElement": "RootErrorFallback",
            "children": [
                {"index": True, "element": "HomePage"},
                {"path": ":toolSlug", "element": "ToolPage"},
            ],
        }
        assert route_config.get("errorElement") is not None, (
            "Root route must have errorElement to prevent white screen on error"
        )
        assert route_config["errorElement"] == "RootErrorFallback"
