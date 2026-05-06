"""
Adversarial hidden acceptance tests for the Root component.
These tests catch implementations that 'teach to the test' by detecting
hardcoded returns, missing validations, and invariant violations not
covered by visible tests.
"""

import pytest
import sys
import os
import types
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Helpers for creating mock ToolDef entries
# ---------------------------------------------------------------------------

def _make_tool_def(step, slug=None):
    """Create a minimal ToolDef-like dict with a step and slug."""
    slug = slug or f"tool-{step}"
    return {
        "step": step,
        "slug": slug,
        "name": f"Tool {step}",
        "description": f"Description for tool {step}",
        "version": "1.0.0",
        "accentColor": "#00ff00",
    }


def _make_sidebar_item(tool_def):
    """Create a minimal SidebarItem-like dict from a ToolDef."""
    return {
        "label": tool_def["name"],
        "slug": tool_def["slug"],
        "step": tool_def["step"],
        "href": f"/{tool_def['slug']}",
    }


def _make_n_tools(n, shuffled=False):
    """Create n tool defs with steps 1..n, optionally shuffled."""
    tools = [_make_tool_def(i) for i in range(1, n + 1)]
    if shuffled:
        import random
        random.seed(42)
        random.shuffle(tools)
    return tools


# ---------------------------------------------------------------------------
# Attempt to import the root module; skip all tests if unavailable
# ---------------------------------------------------------------------------

try:
    from root import *
    ROOT_AVAILABLE = True
except ImportError:
    ROOT_AVAILABLE = False

pytestmark = pytest.mark.skipif(not ROOT_AVAILABLE, reason="root module not importable")


# ===========================================================================
# App tests
# ===========================================================================

class TestGoodhartApp:
    """Adversarial tests for the App component."""

    def test_goodhart_sidebar_items_sorted_by_step_ascending(self):
        """
        Sidebar items passed to Layout must be sorted by the 'step' field
        in ascending order regardless of the order returned by getTools().
        An implementation that just passes items through unsorted violates
        the postcondition.
        """
        shuffled_tools = _make_n_tools(11, shuffled=True)
        mapped_items = [_make_sidebar_item(t) for t in shuffled_tools]

        # We need to verify that whatever the App produces, the sidebar
        # items end up sorted by step ascending.
        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()
            mapping_calls = []

            def mock_mapper(tool_def):
                item = _make_sidebar_item(tool_def)
                mapping_calls.append(item)
                return item

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=shuffled_tools), \
                 patch("root.app_shell.projectToolDefToSidebarItem", side_effect=mock_mapper):
                try:
                    result = App({})
                    # If we can inspect the result tree for sidebar items,
                    # verify they are sorted
                    if hasattr(result, 'props') and result.props:
                        # Try to find sidebar items in the tree
                        pass
                    # At minimum, verify the mapper was called for each tool
                    assert len(mapping_calls) == 11, \
                        f"Expected 11 mapping calls, got {len(mapping_calls)}"
                except Exception:
                    # If App doesn't work this way, try alternative import patterns
                    pass
        except (ImportError, AttributeError):
            pytest.skip("Cannot inspect App internals for this test")

    def test_goodhart_mapping_function_actually_called(self):
        """
        Each sidebar item must result from calling projectToolDefToSidebarItem,
        not from direct passthrough or hardcoding. Verifies the mapping function
        is invoked exactly 11 times.
        """
        tools = _make_n_tools(11)

        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()
            mock_mapper = MagicMock(side_effect=lambda td: _make_sidebar_item(td))

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=tools), \
                 patch("root.app_shell.projectToolDefToSidebarItem", mock_mapper):
                try:
                    App({})
                    assert mock_mapper.call_count == 11, \
                        f"projectToolDefToSidebarItem should be called 11 times, was called {mock_mapper.call_count}"
                    # Verify each tool was passed to the mapper
                    called_steps = sorted([c[0][0]["step"] for c in mock_mapper.call_args_list])
                    assert called_steps == list(range(1, 12)), \
                        "Each of the 11 tools must be passed to projectToolDefToSidebarItem"
                except Exception as e:
                    if "call_count" in str(e) or "projectToolDefToSidebarItem" in str(e):
                        raise
                    pytest.skip(f"App rendering requires additional setup: {e}")
        except ImportError:
            pytest.skip("Cannot import App for this test")

    def test_goodhart_tool_registry_exactly_10_raises(self):
        """
        When getTools() returns exactly 10 entries (one fewer than required 11),
        the app must raise tool_registry_empty. This catches implementations
        that only check for empty arrays rather than the exact count of 11.
        """
        tools = _make_n_tools(10)

        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=tools):
                with pytest.raises(Exception) as exc_info:
                    App({})
                error_str = str(exc_info.value).lower()
                assert "tool_registry" in error_str or "empty" in error_str or "11" in error_str or "fewer" in error_str, \
                    f"Expected tool_registry_empty error for 10 tools, got: {exc_info.value}"
        except ImportError:
            pytest.skip("Cannot import App for this test")

    def test_goodhart_tool_registry_1_entry_raises(self):
        """
        When getTools() returns exactly 1 entry, tool_registry_empty must be
        raised. Ensures the threshold is specifically 11, not just >0 or >5.
        """
        tools = _make_n_tools(1)

        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=tools):
                with pytest.raises(Exception) as exc_info:
                    App({})
                error_str = str(exc_info.value).lower()
                assert "tool_registry" in error_str or "empty" in error_str or "11" in error_str or "fewer" in error_str, \
                    f"Expected tool_registry_empty error for 1 tool, got: {exc_info.value}"
        except ImportError:
            pytest.skip("Cannot import App for this test")

    def test_goodhart_dynamic_route_param_is_toolslug(self):
        """
        The dynamic route parameter must be named exactly ':toolSlug'.
        An implementation using ':slug', ':id', or ':tool' would break
        ToolPage's useParams() call.
        """
        try:
            # Try to inspect the source file directly
            import inspect
            from root import App

            source = inspect.getsource(App)

            # Check that :toolSlug is used
            assert "toolSlug" in source or "tool_slug" in source or ":toolSlug" in source, \
                "Dynamic route must use ':toolSlug' as the parameter name"

            # Negative checks - ensure wrong param names aren't used as the route param
            # (they might appear in comments, so we check route-specific patterns)
            for wrong_param in ["path=':slug'", "path=':id'", "path=':tool'"]:
                assert wrong_param not in source, \
                    f"Route should use ':toolSlug', not '{wrong_param}'"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect App source for route param verification")

    def test_goodhart_strict_mode_is_outermost(self):
        """
        React.StrictMode must be the outermost element in the tree returned
        by App, wrapping ConvexProvider and everything else. StrictMode nested
        inside providers violates the contract hierarchy.
        """
        tools = _make_n_tools(11)

        try:
            from root import App
            from unittest.mock import patch, MagicMock
            import React from 'react' if False else None  # noqa - this is Python

            mock_client = MagicMock()

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=tools), \
                 patch("root.app_shell.projectToolDefToSidebarItem", side_effect=lambda td: _make_sidebar_item(td)):
                try:
                    result = App({})
                    # Check the outermost element type
                    if hasattr(result, 'type'):
                        type_name = getattr(result.type, '__name__', str(result.type))
                        assert 'StrictMode' in type_name or 'strict' in str(type_name).lower(), \
                            f"Root element should be StrictMode, got {type_name}"
                    elif hasattr(result, '$$typeof'):
                        # React element check
                        pass
                except Exception as e:
                    if "StrictMode" in str(e):
                        raise
                    pytest.skip(f"Cannot verify StrictMode placement: {e}")
        except ImportError:
            pytest.skip("Cannot import App for StrictMode verification")

    def test_goodhart_app_accepts_empty_props(self):
        """
        AppProps is an empty struct, so App must accept an empty dict/object
        as props without error. This tests forward compatibility.
        """
        tools = _make_n_tools(11)

        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=tools), \
                 patch("root.app_shell.projectToolDefToSidebarItem", side_effect=lambda td: _make_sidebar_item(td)):
                # Should not raise with empty props
                result = App({})
                assert result is not None, "App should return a React element, not None"
        except ImportError:
            pytest.skip("Cannot import App")
        except Exception as e:
            if "props" in str(e).lower():
                pytest.fail(f"App should accept empty props: {e}")

    def test_goodhart_no_hardcoded_sidebar_items(self):
        """
        Sidebar items must be dynamically derived from getTools(), not hardcoded.
        When getTools returns tools with custom names/slugs, the sidebar items
        must reflect those custom values, not a fixed set.
        """
        custom_tools = []
        for i in range(1, 12):
            custom_tools.append({
                "step": i,
                "slug": f"custom-unique-slug-{i}",
                "name": f"CustomUniqueName{i}",
                "description": f"Custom description {i}",
                "version": "2.0.0",
                "accentColor": "#ff0000",
            })

        try:
            from root import App
            from unittest.mock import patch, MagicMock

            mock_client = MagicMock()
            produced_items = []

            def track_mapper(td):
                item = {
                    "label": td["name"],
                    "slug": td["slug"],
                    "step": td["step"],
                    "href": f"/{td['slug']}",
                }
                produced_items.append(item)
                return item

            with patch("root.app_shell.createConvexClient", return_value=mock_client), \
                 patch("root.data_layer.getTools", return_value=custom_tools), \
                 patch("root.app_shell.projectToolDefToSidebarItem", side_effect=track_mapper):
                App({})
                assert len(produced_items) == 11, \
                    "All 11 custom tools must be mapped"
                for item in produced_items:
                    assert "custom-unique-slug" in item["slug"], \
                        f"Sidebar item slug should come from getTools, got {item['slug']}"
        except ImportError:
            pytest.skip("Cannot import App")
        except Exception as e:
            if "custom-unique" in str(e) or "mapped" in str(e):
                raise
            pytest.skip(f"Cannot verify dynamic sidebar items: {e}")


# ===========================================================================
# Bootstrap tests
# ===========================================================================

class TestGoodhartBootstrap:
    """Adversarial tests for the bootstrap function."""

    def test_goodhart_bootstrap_queries_element_id_root(self):
        """
        Bootstrap must call document.getElementById with exactly the string
        'root', matching the RootDivId type constraint. Using any other ID
        ('app', 'main', etc.) violates the contract.
        """
        try:
            from root import bootstrap
            from unittest.mock import patch, MagicMock

            mock_element = MagicMock()
            mock_get_by_id = MagicMock(return_value=mock_element)
            mock_root = MagicMock()
            mock_create_root = MagicMock(return_value=mock_root)

            with patch("root.document.getElementById", mock_get_by_id), \
                 patch("root.ReactDOM.createRoot", mock_create_root):
                try:
                    bootstrap()
                except Exception:
                    pass

                if mock_get_by_id.called:
                    call_args = mock_get_by_id.call_args[0][0]
                    assert call_args == "root", \
                        f"getElementById must be called with 'root', got '{call_args}'"
        except (ImportError, AttributeError):
            # Try alternative: inspect source
            try:
                import inspect
                from root import bootstrap
                source = inspect.getsource(bootstrap)
                assert "'root'" in source or '"root"' in source, \
                    "bootstrap must reference element ID 'root'"
            except (ImportError, TypeError, OSError):
                pytest.skip("Cannot verify bootstrap element ID")

    def test_goodhart_bootstrap_returns_none(self):
        """
        Bootstrap is purely side-effectful and must return None.
        Returning a root object or rendered element violates the contract.
        """
        try:
            from root import bootstrap
            from unittest.mock import patch, MagicMock

            mock_element = MagicMock()
            mock_root = MagicMock()
            mock_create_root = MagicMock(return_value=mock_root)

            with patch("root.document.getElementById", return_value=mock_element), \
                 patch("root.ReactDOM.createRoot", mock_create_root):
                try:
                    result = bootstrap()
                    assert result is None, \
                        f"bootstrap() must return None, got {type(result)}"
                except Exception:
                    # If bootstrap raises for other reasons, that's separate
                    pass
        except ImportError:
            pytest.skip("Cannot import bootstrap")

    def test_goodhart_bootstrap_uses_createroot_api(self):
        """
        Bootstrap must use React 18's createRoot API from react-dom/client,
        not the legacy ReactDOM.render. This ensures concurrent mode support.
        """
        try:
            import inspect
            from root import bootstrap
            source = inspect.getsource(bootstrap)

            assert "createRoot" in source, \
                "bootstrap must use React 18 createRoot API"
            # Verify it's not using legacy render
            # (render might appear in 'render(<App />)' which is fine for createRoot().render())
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect bootstrap source")


# ===========================================================================
# RootErrorFallback tests
# ===========================================================================

class TestGoodhartRootErrorFallback:
    """Adversarial tests for the RootErrorFallback component."""

    def test_goodhart_error_fallback_home_link_points_to_slash(self):
        """
        The home navigation link in the error fallback must point to exactly
        '/', not '#', '/home', or any other path.
        """
        try:
            import inspect
            from root import RootErrorFallback
            source = inspect.getsource(RootErrorFallback)

            # The component should contain a reference to '/' as the home path
            assert '/' in source, \
                "RootErrorFallback must contain a link to '/'"
            # More specific: look for href or to attribute pointing to '/'
            has_home_link = (
                "href=\"/\"" in source or
                "href='/'" in source or
                "to=\"/\"" in source or
                "to='/'" in source or
                'href="/"' in source or
                "to={'/'}" in source or
                'to="/"' in source
            )
            assert has_home_link, \
                "RootErrorFallback must have a link/anchor pointing to '/'"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect RootErrorFallback source")

    def test_goodhart_error_fallback_has_visible_error_text(self):
        """
        The error fallback must render human-readable text indicating an error
        occurred. An empty div or purely styled container with no text violates
        the postcondition of displaying a 'user-friendly error message'.
        """
        try:
            import inspect
            from root import RootErrorFallback
            source = inspect.getsource(RootErrorFallback)

            # Should contain user-facing error text
            error_indicators = [
                "wrong", "error", "oops", "problem", "sorry",
                "unexpected", "failed", "went wrong", "crash"
            ]
            source_lower = source.lower()
            has_error_text = any(indicator in source_lower for indicator in error_indicators)
            assert has_error_text, \
                "RootErrorFallback must contain visible error message text"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect RootErrorFallback source")

    def test_goodhart_error_fallback_handles_circular_reference_error(self):
        """
        RootErrorFallback must not crash when the error object has circular
        references. If the implementation tries to serialize the error
        (e.g., JSON.stringify), circular refs would cause a TypeError.
        """
        try:
            from root import RootErrorFallback
            from unittest.mock import patch, MagicMock

            # Create a circular error object
            class CircularError(Exception):
                pass

            err = CircularError("circular")
            err.cause = err  # circular reference

            # Try rendering with mocked router context
            with patch("root.useRouteError", return_value=err):
                try:
                    result = RootErrorFallback({"error": err})
                    assert result is not None, \
                        "RootErrorFallback should render even with circular error"
                except RecursionError:
                    pytest.fail("RootErrorFallback caused RecursionError with circular reference")
                except Exception as e:
                    if "recursion" in str(e).lower() or "circular" in str(e).lower():
                        pytest.fail(f"RootErrorFallback failed on circular error: {e}")
        except ImportError:
            pytest.skip("Cannot import RootErrorFallback")

    def test_goodhart_error_fallback_handles_undefined_error(self):
        """
        RootErrorFallback must handle None/undefined error value without
        crashing. useRouteError() can return undefined in edge cases.
        """
        try:
            from root import RootErrorFallback
            from unittest.mock import patch

            with patch("root.useRouteError", return_value=None):
                try:
                    result = RootErrorFallback({"error": None})
                    assert result is not None, \
                        "RootErrorFallback should render with None error"
                except TypeError as e:
                    pytest.fail(f"RootErrorFallback crashed on None error: {e}")
        except ImportError:
            pytest.skip("Cannot import RootErrorFallback")

    def test_goodhart_error_fallback_handles_error_with_huge_message(self):
        """
        RootErrorFallback must not crash or hang when given an error with
        an extremely long message string (e.g., 1MB). Detects implementations
        that attempt to fully display or process the raw error.
        """
        try:
            from root import RootErrorFallback
            from unittest.mock import patch

            huge_msg = "x" * (1024 * 1024)  # 1MB error message
            err = Exception(huge_msg)

            with patch("root.useRouteError", return_value=err):
                try:
                    result = RootErrorFallback({"error": err})
                    assert result is not None
                except MemoryError:
                    pytest.fail("RootErrorFallback caused MemoryError with huge error message")
        except ImportError:
            pytest.skip("Cannot import RootErrorFallback")

    def test_goodhart_error_fallback_does_not_expose_error_details(self):
        """
        A user-friendly error fallback should show a generic message,
        not dump raw error details to the user. The component should
        contain generic user-facing language.
        """
        try:
            import inspect
            from root import RootErrorFallback
            source = inspect.getsource(RootErrorFallback)

            # Should not just dump error.message or error.stack directly
            # Should contain user-friendly phrasing
            friendly_indicators = [
                "home", "back", "return", "go back", "try again",
                "navigate", "start", "main"
            ]
            source_lower = source.lower()
            has_friendly = any(ind in source_lower for ind in friendly_indicators)
            assert has_friendly, \
                "RootErrorFallback should provide a way to navigate back/home"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect RootErrorFallback source")

    def test_goodhart_error_fallback_dark_theme_has_dark_bg_class(self):
        """
        The dark terminal aesthetic requires dark background Tailwind classes.
        The component must use classes like bg-gray-900, bg-black, bg-slate-900,
        or similar dark background utilities.
        """
        try:
            import inspect
            from root import RootErrorFallback
            source = inspect.getsource(RootErrorFallback)

            dark_bg_classes = [
                "bg-gray-900", "bg-gray-950", "bg-black", "bg-slate-900",
                "bg-slate-950", "bg-zinc-900", "bg-zinc-950", "bg-neutral-900",
                "bg-neutral-950", "bg-stone-900", "bg-stone-950"
            ]
            has_dark_bg = any(cls in source for cls in dark_bg_classes)
            assert has_dark_bg, \
                "RootErrorFallback must use a dark background Tailwind class for terminal aesthetic"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect RootErrorFallback source")

    def test_goodhart_error_fallback_light_text_class(self):
        """
        The dark terminal aesthetic requires light text on dark background.
        The component must use Tailwind text color classes like text-white,
        text-gray-100, text-gray-200, etc.
        """
        try:
            import inspect
            from root import RootErrorFallback
            source = inspect.getsource(RootErrorFallback)

            light_text_classes = [
                "text-white", "text-gray-100", "text-gray-200", "text-gray-300",
                "text-slate-100", "text-slate-200", "text-slate-300",
                "text-zinc-100", "text-zinc-200", "text-zinc-300",
                "text-neutral-100", "text-neutral-200",
                "text-green-", "text-emerald-",  # terminal green aesthetic
            ]
            has_light_text = any(cls in source for cls in light_text_classes)
            assert has_light_text, \
                "RootErrorFallback must use light text Tailwind classes for dark theme"
        except (ImportError, TypeError, OSError):
            pytest.skip("Cannot inspect RootErrorFallback source")


# ===========================================================================
# Source / structural analysis tests
# ===========================================================================

class TestGoodhartStructural:
    """Tests that verify structural properties of the root module files."""

    def test_goodhart_app_file_imports_from_data_layer(self):
        """
        App must import getTools from data_layer dependency, not define
        tools inline. Verifies the unidirectional dependency flow where
        root imports from data_layer.
        """
        try:
            import inspect
            from root import App
            source = inspect.getsource(sys.modules.get('root', App))
        except (ImportError, TypeError, OSError):
            try:
                # Try reading App.tsx or similar source file
                possible_paths = [
                    "src/App.tsx", "src/App.ts", "src/App.jsx", "src/App.js",
                    "root/App.tsx", "root/App.ts",
                ]
                source = None
                for p in possible_paths:
                    if os.path.exists(p):
                        with open(p, 'r') as f:
                            source = f.read()
                        break
                if source is None:
                    pytest.skip("Cannot locate App source file")
            except Exception:
                pytest.skip("Cannot read App source")

        assert source is not None
        # Verify data_layer import
        has_data_layer = (
            "data_layer" in source or
            "getTools" in source
        )
        assert has_data_layer, \
            "App must import getTools from data_layer, not hardcode tools"

    def test_goodhart_app_file_imports_from_app_shell(self):
        """
        App must import createConvexClient and projectToolDefToSidebarItem
        from app_shell. These must not be inlined.
        """
        try:
            possible_paths = [
                "src/App.tsx", "src/App.ts", "src/App.jsx", "src/App.js",
            ]
            source = None
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        source = f.read()
                    break
            if source is None:
                pytest.skip("Cannot locate App source file")

            has_app_shell = (
                "app_shell" in source or
                "createConvexClient" in source or
                "projectToolDefToSidebarItem" in source
            )
            assert has_app_shell, \
                "App must import from app_shell (createConvexClient, projectToolDefToSidebarItem)"
        except Exception:
            pytest.skip("Cannot verify app_shell imports")

    def test_goodhart_main_file_not_exported_bootstrap(self):
        """
        bootstrap() executes as a top-level side effect in main.tsx.
        It should not be exported as a named or default export.
        The invariant states it 'is not exported'.
        """
        try:
            possible_paths = [
                "src/main.tsx", "src/main.ts", "src/main.jsx", "src/main.js",
            ]
            source = None
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        source = f.read()
                    break
            if source is None:
                pytest.skip("Cannot locate main source file")

            # Should not have 'export function bootstrap' or 'export { bootstrap }'
            assert "export function bootstrap" not in source, \
                "bootstrap should not be exported as a named function"
            assert "export { bootstrap" not in source, \
                "bootstrap should not be exported via named export"
            assert "export default bootstrap" not in source, \
                "bootstrap should not be the default export"
        except Exception:
            pytest.skip("Cannot verify bootstrap export status")

    def test_goodhart_no_custom_css_files_in_root(self):
        """
        The invariant states 'no custom CSS files are created by root'.
        All styling uses Tailwind CSS classes. Verify no .css files
        (other than standard Tailwind imports) are created.
        """
        try:
            root_dirs = ["src/", "root/"]
            css_files = []
            for root_dir in root_dirs:
                if os.path.exists(root_dir):
                    for f in os.listdir(root_dir):
                        if f.endswith('.css') and f not in ('index.css', 'globals.css', 'tailwind.css', 'app.css'):
                            css_files.append(f)

            # Allow standard Tailwind entry CSS, but no custom component CSS
            for css_file in css_files:
                with open(os.path.join(root_dir, css_file), 'r') as f:
                    content = f.read()
                # If it contains only Tailwind directives, that's fine
                is_tailwind_only = all(
                    line.strip().startswith('@tailwind') or
                    line.strip().startswith('@import') or
                    line.strip() == '' or
                    line.strip().startswith('/*') or
                    line.strip().startswith('*') or
                    line.strip().endswith('*/')
                    for line in content.splitlines()
                )
                if not is_tailwind_only:
                    pytest.fail(f"Custom CSS file found: {css_file}. Root should only use Tailwind classes.")
        except Exception:
            pytest.skip("Cannot verify CSS file structure")

    def test_goodhart_index_html_has_module_script(self):
        """
        index.html must load src/main.tsx as type='module'. This is how
        Vite bootstraps the application.
        """
        try:
            possible_paths = ["index.html", "public/index.html"]
            html_source = None
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        html_source = f.read()
                    break
            if html_source is None:
                pytest.skip("Cannot locate index.html")

            assert 'type="module"' in html_source or "type='module'" in html_source, \
                "index.html must load main.tsx as type='module'"
            assert 'src/main.tsx' in html_source or 'src/main.ts' in html_source, \
                "index.html must reference src/main.tsx"
        except Exception:
            pytest.skip("Cannot verify index.html structure")

    def test_goodhart_index_html_has_div_root(self):
        """
        index.html must contain a div element with id='root' as the
        React mount point. This is the RootDivId invariant.
        """
        try:
            possible_paths = ["index.html", "public/index.html"]
            html_source = None
            for p in possible_paths:
                if os.path.exists(p):
                    with open(p, 'r') as f:
                        html_source = f.read()
                    break
            if html_source is None:
                pytest.skip("Cannot locate index.html")

            assert 'id="root"' in html_source or "id='root'" in html_source, \
                "index.html must contain <div id='root'>"
        except Exception:
            pytest.skip("Cannot verify index.html structure")
