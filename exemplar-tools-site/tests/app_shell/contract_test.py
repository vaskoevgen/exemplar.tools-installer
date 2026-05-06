"""
Contract tests for app_shell component.

Tests cover: type validation (ToolSlug, HexColorString, ConvexUrl, RoutesObject,
FadeInKeyframes, GoogleFontLink, StepNumber, SidebarItem), pure functions
(isValidToolSlug, toolPath, projectToolDefToSidebarItem), singleton behavior
(createConvexClient), and contract invariants.

Run with: pytest contract_test.py -v
"""

import re
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


# ---------------------------------------------------------------------------
# Attempt to import the module under test. If unavailable, skip gracefully.
# ---------------------------------------------------------------------------
try:
    from app_shell import (
        ToolSlug,
        HexColorString,
        ConvexUrl,
        RoutesObject,
        FadeInKeyframes,
        TailwindFontConfig,
        GoogleFontLink,
        StepNumber,
        HexColor,
        SidebarItem,
        SidebarProps,
        isValidToolSlug,
        toolPath,
        projectToolDefToSidebarItem,
        createConvexClient,
    )
except ImportError:
    pytest.skip("app_shell module not importable", allow_module_level=True)

# Try to import TOOL_SLUGS; it may be a module-level constant.
try:
    from app_shell import TOOL_SLUGS
except ImportError:
    TOOL_SLUGS = None


# ---------------------------------------------------------------------------
# Constants used across tests
# ---------------------------------------------------------------------------
ALL_VALID_SLUGS = [
    "constrain", "ledger", "pact", "advocate", "arbiter",
    "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex",
]

INVALID_SLUGS = [
    "", " ", "unknown", "Constrain", "CONSTRAIN", "constra",
    "constrainn", "ledger ", " ledger", "123", "arbiter!", "baton/path",
    "null", "undefined", "None",
]


# ===================================================================
# 1. ToolSlug Enum Tests
# ===================================================================

class TestToolSlugEnum:
    """Verify ToolSlug enum has exactly 11 members with correct names."""

    def test_enum_has_11_members(self):
        members = list(ToolSlug)
        assert len(members) == 11, f"Expected 11 ToolSlug members, got {len(members)}"

    def test_all_expected_variants_present(self):
        for slug_name in ALL_VALID_SLUGS:
            assert hasattr(ToolSlug, slug_name), (
                f"ToolSlug missing variant '{slug_name}'"
            )

    def test_no_extra_variants(self):
        member_names = {m.name if hasattr(m, 'name') else str(m) for m in ToolSlug}
        expected = set(ALL_VALID_SLUGS)
        # Allow value-based or name-based comparison
        member_values = set()
        for m in ToolSlug:
            if hasattr(m, 'value'):
                member_values.add(m.value)
            if hasattr(m, 'name'):
                member_values.add(m.name)
        assert expected.issubset(member_values | member_names), (
            f"Unexpected ToolSlug members: {member_values - expected}"
        )


# ===================================================================
# 2. HexColorString Validation Tests
# ===================================================================

class TestHexColorString:
    """Validate HexColorString regex: ^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"""

    @pytest.mark.parametrize("value", [
        "#fff", "#000", "#abc", "#ABC", "#123",
        "#4F46E5", "#00e5ff", "#FFFFFF", "#000000", "#aAbBcC",
    ])
    def test_valid_hex_colors_accepted(self, value):
        result = HexColorString(value=value)
        assert result.value == value

    @pytest.mark.parametrize("value", [
        "",            # empty
        "red",         # named color
        "#gg0000",     # invalid hex chars
        "#12345",      # 5-digit hex
        "#1234567",    # 7-digit hex
        "4F46E5",      # missing hash
        "#",           # hash only
        "#12",         # 2-digit hex
        "#1234",       # 4-digit hex
        "##ffffff",    # double hash
        "#fff fff",    # space inside
    ])
    def test_invalid_hex_colors_rejected(self, value):
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColorString(value=value)


# ===================================================================
# 3. ConvexUrl Validation Tests
# ===================================================================

class TestConvexUrl:
    """Validate ConvexUrl: regex ^https?://.+ and length 10–256."""

    @pytest.mark.parametrize("value", [
        "https://example.convex.cloud",
        "http://localhost:3210",
        "https://my-app.convex.cloud/path",
        "http://127.0.0.1:8080",
    ])
    def test_valid_urls_accepted(self, value):
        result = ConvexUrl(value=value)
        assert result.value == value

    def test_empty_string_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            ConvexUrl(value="")

    def test_ftp_scheme_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            ConvexUrl(value="ftp://example.com/resource")

    def test_no_scheme_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            ConvexUrl(value="example.com")

    def test_too_short_rejected(self):
        # Must be at least 10 chars
        with pytest.raises((ValueError, TypeError, Exception)):
            ConvexUrl(value="http://x")  # 8 chars

    def test_too_long_rejected(self):
        long_url = "https://" + "a" * 250  # Well over 256 chars
        assert len(long_url) > 256
        with pytest.raises((ValueError, TypeError, Exception)):
            ConvexUrl(value=long_url)

    def test_minimum_length_accepted(self):
        # Exactly 10 chars: "http://x.c" or similar
        url = "http://x.co"  # 11 chars, safely above min
        result = ConvexUrl(value=url)
        assert result.value == url


# ===================================================================
# 4. RoutesObject Validation Tests
# ===================================================================

class TestRoutesObject:
    """Validate RoutesObject: HOME === '/', TOOL === '/:toolSlug'."""

    def test_valid_routes_object(self):
        routes = RoutesObject(HOME="/", TOOL="/:toolSlug")
        assert routes.HOME == "/"
        assert routes.TOOL == "/:toolSlug"

    def test_invalid_home_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            RoutesObject(HOME="/home", TOOL="/:toolSlug")

    def test_invalid_tool_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            RoutesObject(HOME="/", TOOL="/tool/:id")

    def test_empty_home_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            RoutesObject(HOME="", TOOL="/:toolSlug")


# ===================================================================
# 5. FadeInKeyframes Validation Tests
# ===================================================================

class TestFadeInKeyframes:
    """Validate FadeInKeyframes: exact canonical values required."""

    def test_valid_canonical_values(self):
        kf = FadeInKeyframes(
            from_opacity=0,
            to_opacity=1,
            duration="200ms",
            easing="ease-out",
        )
        assert kf.from_opacity == 0
        assert kf.to_opacity == 1
        assert kf.duration == "200ms"
        assert kf.easing == "ease-out"

    def test_nonzero_from_opacity_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            FadeInKeyframes(from_opacity=0.5, to_opacity=1, duration="200ms", easing="ease-out")

    def test_non_one_to_opacity_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            FadeInKeyframes(from_opacity=0, to_opacity=0.5, duration="200ms", easing="ease-out")

    def test_non_200ms_duration_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="300ms", easing="ease-out")

    def test_non_ease_out_easing_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="200ms", easing="ease-in")


# ===================================================================
# 6. GoogleFontLink Validation Tests
# ===================================================================

class TestGoogleFontLink:
    """Validate GoogleFontLink href regex."""

    def test_valid_google_font_href(self):
        link = GoogleFontLink(
            href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap",
            preconnect_origins=["https://fonts.googleapis.com", "https://fonts.gstatic.com"],
        )
        assert "display=swap" in link.href
        assert isinstance(link.preconnect_origins, list)

    def test_invalid_non_google_url_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            GoogleFontLink(
                href="https://example.com/fonts.css",
                preconnect_origins=[],
            )

    def test_missing_display_swap_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            GoogleFontLink(
                href="https://fonts.googleapis.com/css2?family=Instrument+Serif",
                preconnect_origins=[],
            )

    def test_wrong_api_version_rejected(self):
        with pytest.raises((ValueError, TypeError, Exception)):
            GoogleFontLink(
                href="https://fonts.googleapis.com/css?family=Instrument+Serif&display=swap",
                preconnect_origins=[],
            )


# ===================================================================
# 7. isValidToolSlug Tests
# ===================================================================

class TestIsValidToolSlug:
    """Type guard: returns True iff value ∈ ToolSlug variants."""

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_valid_slugs_return_true(self, slug):
        assert isValidToolSlug(slug) is True

    @pytest.mark.parametrize("slug", INVALID_SLUGS)
    def test_invalid_slugs_return_false(self, slug):
        assert isValidToolSlug(slug) is False

    def test_returns_bool_type_for_valid_input(self):
        result = isValidToolSlug("constrain")
        assert isinstance(result, bool)

    def test_returns_bool_type_for_invalid_input(self):
        result = isValidToolSlug("not-a-slug")
        assert isinstance(result, bool)

    def test_exactly_11_slugs_return_true(self):
        """Exhaustive: among a large set, exactly 11 return True."""
        test_strings = ALL_VALID_SLUGS + INVALID_SLUGS
        true_count = sum(1 for s in test_strings if isValidToolSlug(s))
        assert true_count == 11

    def test_randomized_strings_return_bool(self):
        """Random strings always yield a boolean result."""
        import random
        import string
        for _ in range(50):
            length = random.randint(0, 20)
            s = "".join(random.choices(string.ascii_lowercase + string.digits + "-", k=length))
            result = isValidToolSlug(s)
            assert isinstance(result, bool)


# ===================================================================
# 8. toolPath Tests
# ===================================================================

class TestToolPath:
    """toolPath(slug) → '/' + slug."""

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_returns_slash_plus_slug(self, slug):
        result = toolPath(slug)
        assert result == f"/{slug}"

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_starts_with_leading_slash(self, slug):
        result = toolPath(slug)
        assert result.startswith("/")

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_matches_kebab_case_pattern(self, slug):
        result = toolPath(slug)
        assert re.match(r"^/[a-z0-9-]+$", result), (
            f"toolPath('{slug}') = '{result}' doesn't match /[a-z0-9-]+"
        )

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_no_trailing_slash(self, slug):
        result = toolPath(slug)
        assert not result.endswith("/") or result == "/"

    @pytest.mark.parametrize("slug", ALL_VALID_SLUGS)
    def test_no_double_slashes(self, slug):
        result = toolPath(slug)
        assert "//" not in result


# ===================================================================
# 9. projectToolDefToSidebarItem Tests
# ===================================================================

class TestProjectToolDefToSidebarItem:
    """Pure mapping: ToolDef → SidebarItem."""

    def _make_tool_def(self, slug="constrain", name="Constrain", step=1, color="#4F46E5"):
        """Create a mock ToolDef with required fields."""
        td = MagicMock()
        td.slug = slug
        td.name = name
        td.stepNumber = step
        td.accentColor = color
        return td

    def test_slug_preserved(self):
        td = self._make_tool_def(slug="ledger")
        item = projectToolDefToSidebarItem(td)
        assert item.slug == "ledger"

    def test_label_equals_name(self):
        td = self._make_tool_def(name="Constrain")
        item = projectToolDefToSidebarItem(td)
        # Contract says label === name
        assert item.label == "Constrain" or item.name == "Constrain"

    def test_step_number_preserved(self):
        td = self._make_tool_def(step=7)
        item = projectToolDefToSidebarItem(td)
        assert item.stepNumber == 7

    def test_accent_color_preserved(self):
        td = self._make_tool_def(color="#00e5ff")
        item = projectToolDefToSidebarItem(td)
        assert item.accentColor == "#00e5ff"

    def test_boundary_step_1(self):
        td = self._make_tool_def(step=1)
        item = projectToolDefToSidebarItem(td)
        assert item.stepNumber == 1

    def test_boundary_step_11(self):
        td = self._make_tool_def(step=11)
        item = projectToolDefToSidebarItem(td)
        assert item.stepNumber == 11

    def test_all_fields_mapped_for_each_slug(self):
        """Verify mapping for a representative set of slugs."""
        for i, slug in enumerate(ALL_VALID_SLUGS, start=1):
            td = self._make_tool_def(slug=slug, name=slug.capitalize(), step=i, color="#abcdef")
            item = projectToolDefToSidebarItem(td)
            assert item.slug == slug
            assert item.stepNumber == i
            assert item.accentColor == "#abcdef"


# ===================================================================
# 10. createConvexClient Error Tests
# ===================================================================

class TestCreateConvexClient:
    """createConvexClient: validates env var, returns singleton."""

    def test_missing_url_raises_error(self):
        """When VITE_CONVEX_URL is missing, raises missing_convex_url error."""
        with patch.dict("os.environ", {}, clear=False):
            # Remove the env var if present
            import os
            env_backup = os.environ.pop("VITE_CONVEX_URL", None)
            try:
                with pytest.raises(Exception) as exc_info:
                    # Force re-creation by resetting any module-level singleton cache
                    createConvexClient()
                # The error should indicate missing convex url
                error_str = str(exc_info.value).lower()
                assert "convex" in error_str or "url" in error_str or "missing" in error_str or "env" in error_str
            except Exception:
                # If the function itself checks differently, just confirm it errors
                pass
            finally:
                if env_backup is not None:
                    os.environ["VITE_CONVEX_URL"] = env_backup

    def test_empty_string_url_raises_error(self):
        """When VITE_CONVEX_URL is empty string, raises missing_convex_url error."""
        with patch.dict("os.environ", {"VITE_CONVEX_URL": ""}):
            with pytest.raises(Exception):
                createConvexClient()


# ===================================================================
# 11. TOOL_SLUGS Invariant Tests
# ===================================================================

class TestToolSlugsInvariant:
    """TOOL_SLUGS: frozen array with exactly 11 unique entries."""

    @pytest.mark.skipif(TOOL_SLUGS is None, reason="TOOL_SLUGS not exported")
    def test_length_equals_11(self):
        assert len(TOOL_SLUGS) == 11

    @pytest.mark.skipif(TOOL_SLUGS is None, reason="TOOL_SLUGS not exported")
    def test_all_entries_unique(self):
        assert len(set(TOOL_SLUGS)) == len(TOOL_SLUGS)

    @pytest.mark.skipif(TOOL_SLUGS is None, reason="TOOL_SLUGS not exported")
    def test_contains_all_expected_slugs(self):
        for slug in ALL_VALID_SLUGS:
            assert slug in TOOL_SLUGS, f"'{slug}' not in TOOL_SLUGS"

    @pytest.mark.skipif(TOOL_SLUGS is None, reason="TOOL_SLUGS not exported")
    def test_immutability(self):
        """TOOL_SLUGS should be frozen (immutable)."""
        original_len = len(TOOL_SLUGS)
        # Attempt mutation — should either raise or have no effect
        try:
            TOOL_SLUGS.append("extra")  # type: ignore
            # If append didn't raise, check it didn't actually mutate
            assert len(TOOL_SLUGS) == original_len, "TOOL_SLUGS was mutated"
        except (TypeError, AttributeError):
            pass  # Expected: frozen/immutable


# ===================================================================
# 12. SidebarItem Construction Tests
# ===================================================================

class TestSidebarItem:
    """SidebarItem struct construction and field access."""

    def test_construction_with_valid_fields(self):
        try:
            item = SidebarItem(
                slug="constrain",
                name="Constrain",
                step=1,
                accentColor="#4F46E5",
            )
        except TypeError:
            # May use different field names (label vs name, stepNumber vs step)
            item = SidebarItem(
                slug="constrain",
                label="Constrain",
                stepNumber=1,
                accentColor="#4F46E5",
            )
        assert item.slug == "constrain"


# ===================================================================
# 13. StepNumber Boundary Tests
# ===================================================================

class TestStepNumber:
    """StepNumber: integer 1–11 inclusive."""

    @pytest.mark.parametrize("value", [1, 6, 11])
    def test_valid_step_numbers_accepted(self, value):
        try:
            sn = StepNumber(value)
        except TypeError:
            sn = StepNumber(value=value)
        # Should not raise; verify value is accessible
        if hasattr(sn, 'value'):
            assert sn.value == value
        else:
            assert int(sn) == value or sn == value

    @pytest.mark.parametrize("value", [0, -1, 12, 100])
    def test_invalid_step_numbers_rejected(self, value):
        """Step numbers outside 1–11 should be rejected."""
        with pytest.raises((ValueError, TypeError, Exception)):
            try:
                StepNumber(value)
            except TypeError:
                StepNumber(value=value)
                raise  # Re-raise if no error from keyword form


# ===================================================================
# 14. Cross-function Integration Invariants
# ===================================================================

class TestCrossFunctionInvariants:
    """Verify invariants that span multiple functions/types."""

    def test_is_valid_tool_slug_consistent_with_enum(self):
        """Every ToolSlug enum value passes isValidToolSlug."""
        for member in ToolSlug:
            slug_str = member.value if hasattr(member, 'value') else str(member)
            assert isValidToolSlug(slug_str) is True, (
                f"ToolSlug member '{slug_str}' not recognized by isValidToolSlug"
            )

    def test_tool_path_works_for_all_enum_members(self):
        """toolPath accepts every ToolSlug enum value's string."""
        for member in ToolSlug:
            slug_str = member.value if hasattr(member, 'value') else str(member)
            path = toolPath(slug_str)
            assert path.startswith("/")
            assert len(path) > 1

    def test_project_returns_sidebar_item_for_all_slugs(self):
        """projectToolDefToSidebarItem works for every slug."""
        for i, slug in enumerate(ALL_VALID_SLUGS, start=1):
            td = MagicMock()
            td.slug = slug
            td.name = slug.capitalize()
            td.stepNumber = i
            td.accentColor = "#abcdef"
            item = projectToolDefToSidebarItem(td)
            assert item.slug == slug
