"""
Hidden adversarial acceptance tests for the App Shell, Routing & Layout component.
These tests target gaps in visible test coverage and detect implementations
that hardcode returns or take shortcuts matching only visible test inputs.
"""
import pytest
import re
from app_shell import (
    isValidToolSlug,
    toolPath,
    projectToolDefToSidebarItem,
    HexColorString,
    ConvexUrl,
    RoutesObject,
    FadeInKeyframes,
    GoogleFontLink,
    StepNumber,
    TOOL_SLUGS,
    ROUTES,
)


# ─── ToolSlug enum membership: case sensitivity ───

class TestGoodhartIsValidToolSlug:

    def test_goodhart_case_sensitivity_uppercase(self):
        """isValidToolSlug must be case-sensitive: uppercase variants of valid slugs must be rejected"""
        assert isValidToolSlug("Constrain") is False
        assert isValidToolSlug("LEDGER") is False
        assert isValidToolSlug("Pact") is False
        assert isValidToolSlug("ARBITER") is False
        assert isValidToolSlug("Sentinel") is False
        assert isValidToolSlug("KINDEX") is False
        assert isValidToolSlug("ADVOCATE") is False
        assert isValidToolSlug("BATON") is False

    def test_goodhart_near_miss_substrings(self):
        """isValidToolSlug must reject substrings, superstrings, and misspellings of valid slugs"""
        assert isValidToolSlug("constrai") is False
        assert isValidToolSlug("constrainn") is False
        assert isValidToolSlug("pacts") is False
        assert isValidToolSlug("advocat") is False
        assert isValidToolSlug("batons") is False
        assert isValidToolSlug("sentinels") is False
        assert isValidToolSlug("chroniclers") is False
        assert isValidToolSlug("apprentic") is False
        assert isValidToolSlug("kinde") is False

    def test_goodhart_whitespace_variants(self):
        """isValidToolSlug must reject whitespace-padded or whitespace-only inputs"""
        assert isValidToolSlug("") is False
        assert isValidToolSlug(" ") is False
        assert isValidToolSlug("  ") is False
        assert isValidToolSlug("ledger ") is False
        assert isValidToolSlug(" ledger") is False
        assert isValidToolSlug(" constrain ") is False

    def test_goodhart_non_string_types(self):
        """isValidToolSlug must return False (not raise) for non-string inputs"""
        # The function should gracefully handle non-strings
        for val in [None, 0, 42, True, False, [], {}]:
            result = isValidToolSlug(val)
            assert result is False or result == False, f"isValidToolSlug({val!r}) should be False"

    def test_goodhart_slug_like_but_invalid(self):
        """isValidToolSlug must reject plausible-looking but non-canonical slug strings"""
        assert isValidToolSlug("constraint") is False
        assert isValidToolSlug("ledgers") is False
        assert isValidToolSlug("contract") is False
        assert isValidToolSlug("tool") is False
        assert isValidToolSlug("index") is False
        assert isValidToolSlug("kindle") is False


# ─── toolPath: format and content ───

class TestGoodhartToolPath:

    def test_goodhart_no_trailing_slash(self):
        """toolPath must produce paths with no trailing slash for any slug"""
        for slug in TOOL_SLUGS:
            result = toolPath(slug)
            assert not result.endswith("/") or result == "/", f"toolPath('{slug}') should not end with '/'"

    def test_goodhart_exactly_one_slash(self):
        """toolPath must produce a path with exactly one slash (the leading one)"""
        for slug in TOOL_SLUGS:
            result = toolPath(slug)
            assert result.count("/") == 1, f"toolPath('{slug}') has {result.count('/')} slashes, expected 1"

    def test_goodhart_no_template_placeholder(self):
        """toolPath must replace the route parameter, never returning literal ':toolSlug'"""
        for slug in TOOL_SLUGS:
            result = toolPath(slug)
            assert ":" not in result, f"toolPath('{slug}') contains ':' template syntax"
            assert "toolSlug" not in result, f"toolPath('{slug}') contains literal 'toolSlug'"

    def test_goodhart_slug_preserved_exactly(self):
        """toolPath must preserve the slug string exactly after the leading slash"""
        for slug in TOOL_SLUGS:
            result = toolPath(slug)
            assert result[1:] == slug, f"toolPath('{slug}')[1:] == {result[1:]!r}, expected {slug!r}"

    def test_goodhart_path_matches_pattern(self):
        """toolPath output must match the regex pattern '/[a-z0-9-]+'"""
        pattern = re.compile(r"^/[a-z0-9-]+$")
        for slug in TOOL_SLUGS:
            result = toolPath(slug)
            assert pattern.match(result), f"toolPath('{slug}') = {result!r} doesn't match pattern"


# ─── projectToolDefToSidebarItem: field mapping fidelity ───

class TestGoodhartProjectToolDef:

    def _make_tooldef(self, slug="constrain", name="Test Tool", step=1, color="#ff0000"):
        """Helper to create a mock ToolDef-like object."""
        class ToolDef:
            pass
        td = ToolDef()
        td.slug = slug
        td.name = name
        td.stepNumber = step
        td.accentColor = color
        return td

    def test_goodhart_various_accent_colors(self):
        """projectToolDefToSidebarItem must faithfully pass through any valid accentColor, not hardcode a specific color"""
        colors = ["#ff0000", "#00e5ff", "#abc", "#4F46E5", "#000000", "#FFFFFF"]
        for color in colors:
            td = self._make_tooldef(color=color)
            result = projectToolDefToSidebarItem(td)
            assert result.accentColor == color, f"Expected accentColor={color!r}, got {result.accentColor!r}"

    def test_goodhart_arbitrary_name_mapping(self):
        """projectToolDefToSidebarItem must map name to label for arbitrary name strings, not just known tool names"""
        td = self._make_tooldef(name="My Custom Tool", slug="constrain", step=5)
        result = projectToolDefToSidebarItem(td)
        assert result.label == "My Custom Tool"
        assert result.slug == "constrain"
        assert result.stepNumber == 5

    def test_goodhart_mid_range_step_numbers(self):
        """projectToolDefToSidebarItem must handle all step numbers 1-11, not just boundaries 1 and 11"""
        for step in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
            td = self._make_tooldef(step=step)
            result = projectToolDefToSidebarItem(td)
            assert result.stepNumber == step, f"Expected stepNumber={step}, got {result.stepNumber}"

    def test_goodhart_no_field_swapping(self):
        """projectToolDefToSidebarItem must not swap or confuse fields during mapping"""
        td = self._make_tooldef(slug="stigmergy", name="Unique Name XYZ", step=7, color="#abcdef")
        result = projectToolDefToSidebarItem(td)
        assert result.slug == "stigmergy"
        assert result.label == "Unique Name XYZ"
        assert result.stepNumber == 7
        assert result.accentColor == "#abcdef"
        # Ensure no cross-contamination
        assert result.slug != result.label
        assert result.slug != result.accentColor

    def test_goodhart_all_slugs_mappable(self):
        """projectToolDefToSidebarItem must work correctly for every valid ToolSlug, not just a subset"""
        for i, slug in enumerate(TOOL_SLUGS):
            td = self._make_tooldef(slug=slug, name=f"Tool {slug}", step=(i % 11) + 1, color="#aabbcc")
            result = projectToolDefToSidebarItem(td)
            assert result.slug == slug


# ─── HexColorString: boundary and format ───

class TestGoodhartHexColorString:

    def test_goodhart_3digit_various_cases(self):
        """HexColorString must accept all case combinations of 3-digit hex colors"""
        valid_3digit = ["#abc", "#ABC", "#1a2", "#FFF", "#000", "#fFf", "#A0c"]
        for color in valid_3digit:
            result = HexColorString(color)
            assert result is not None, f"HexColorString should accept {color!r}"

    def test_goodhart_wrong_digit_counts(self):
        """HexColorString must reject hex strings with digit counts other than 3 or 6"""
        invalid_counts = ["#a", "#ab", "#abcd", "#abcde", "#abcdef0", "#abcdef01"]
        for color in invalid_counts:
            with pytest.raises(Exception):
                HexColorString(color)

    def test_goodhart_no_hash_prefix(self):
        """HexColorString must require the leading '#' character"""
        for color in ["abc", "AABBCC", "123456", "fff"]:
            with pytest.raises(Exception):
                HexColorString(color)

    def test_goodhart_non_hex_chars(self):
        """HexColorString must reject strings containing non-hexadecimal characters after #"""
        for color in ["#gggggg", "#xyz", "#12345g", "#zzzzzz"]:
            with pytest.raises(Exception):
                HexColorString(color)

    def test_goodhart_double_hash(self):
        """HexColorString must reject strings with double hash or other prefix anomalies"""
        for color in ["##aabbcc", "# aabbcc", "#aabb cc"]:
            with pytest.raises(Exception):
                HexColorString(color)


# ─── ConvexUrl: length boundaries and scheme ───

class TestGoodhartConvexUrl:

    def test_goodhart_exact_min_length(self):
        """ConvexUrl must accept URLs of exactly 10 characters and reject those of 9"""
        url_10 = "http://a.b"  # exactly 10 chars
        assert len(url_10) == 10
        result = ConvexUrl(url_10)
        assert result is not None

        url_9 = "http://a."  # 9 chars
        assert len(url_9) == 9
        with pytest.raises(Exception):
            ConvexUrl(url_9)

    def test_goodhart_exact_max_length(self):
        """ConvexUrl must accept URLs of exactly 256 characters and reject those of 257"""
        base = "https://example.com/"
        url_256 = base + "a" * (256 - len(base))
        assert len(url_256) == 256
        result = ConvexUrl(url_256)
        assert result is not None

        url_257 = base + "a" * (257 - len(base))
        assert len(url_257) == 257
        with pytest.raises(Exception):
            ConvexUrl(url_257)

    def test_goodhart_rejects_non_http_schemes(self):
        """ConvexUrl must reject URLs with schemes other than http/https"""
        for url in ["ftp://example.com/path", "ws://example.com/ws", "file:///etc/passwd"]:
            with pytest.raises(Exception):
                ConvexUrl(url)

    def test_goodhart_empty_and_whitespace(self):
        """ConvexUrl must reject empty strings and whitespace"""
        for url in ["", " ", "   "]:
            with pytest.raises(Exception):
                ConvexUrl(url)


# ─── RoutesObject: TOOL value and immutability ───

class TestGoodhartRoutesObject:

    def test_goodhart_tool_value_exact(self):
        """RoutesObject TOOL field must be exactly '/:toolSlug'"""
        routes = RoutesObject(HOME="/", TOOL="/:toolSlug")
        assert routes.TOOL == "/:toolSlug"

    def test_goodhart_invalid_tool_values(self):
        """RoutesObject must reject TOOL values that differ from '/:toolSlug'"""
        for bad_tool in ["/:tool", "/tool/:slug", "/tools/:toolSlug", "/", "/:toolSlug/", ""]:
            with pytest.raises(Exception):
                RoutesObject(HOME="/", TOOL=bad_tool)

    def test_goodhart_frozen_routes(self):
        """ROUTES object must be frozen/immutable — mutation attempts should fail or have no effect"""
        # If ROUTES is a module-level constant, verify it cannot be mutated
        original_home = ROUTES.HOME
        original_tool = ROUTES.TOOL
        try:
            ROUTES.HOME = "/changed"
        except (AttributeError, TypeError, Exception):
            pass  # Expected for frozen objects
        assert ROUTES.HOME == original_home, "ROUTES.HOME should not be mutable"
        assert ROUTES.TOOL == original_tool, "ROUTES.TOOL should not be mutable"


# ─── FadeInKeyframes: per-field validation ───

class TestGoodhartFadeInKeyframes:

    def test_goodhart_single_field_deviation(self):
        """FadeInKeyframes must validate each field independently — changing one field from canonical must cause rejection"""
        # Canonical: from_opacity=0, to_opacity=1, duration='200ms', easing='ease-out'
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0.1, to_opacity=1, duration="200ms", easing="ease-out")
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0, to_opacity=0.9, duration="200ms", easing="ease-out")
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="300ms", easing="ease-out")
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="200ms", easing="ease-in")

    def test_goodhart_wrong_duration_units(self):
        """FadeInKeyframes must reject duration values with wrong units or format"""
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="0.2s", easing="ease-out")
        with pytest.raises(Exception):
            FadeInKeyframes(from_opacity=0, to_opacity=1, duration="200", easing="ease-out")

    def test_goodhart_wrong_easing_variants(self):
        """FadeInKeyframes must reject easing values that are CSS-valid but not 'ease-out'"""
        for easing in ["ease", "ease-in", "ease-in-out", "linear", "cubic-bezier(0,0,1,1)"]:
            with pytest.raises(Exception):
                FadeInKeyframes(from_opacity=0, to_opacity=1, duration="200ms", easing=easing)


# ─── TOOL_SLUGS: content and immutability ───

class TestGoodhartToolSlugs:

    def test_goodhart_exact_membership(self):
        """TOOL_SLUGS must contain exactly the 11 specified slugs and no others"""
        expected = {"constrain", "ledger", "pact", "advocate", "arbiter", "baton",
                    "sentinel", "chronicler", "stigmergy", "apprentice", "kindex"}
        actual = set(TOOL_SLUGS)
        assert actual == expected, f"TOOL_SLUGS mismatch: extra={actual - expected}, missing={expected - actual}"

    def test_goodhart_no_duplicates(self):
        """TOOL_SLUGS must contain no duplicate entries"""
        assert len(TOOL_SLUGS) == len(set(TOOL_SLUGS)), "TOOL_SLUGS contains duplicates"

    def test_goodhart_frozen(self):
        """TOOL_SLUGS must be immutable — append/extend/mutation should fail or have no effect"""
        original_len = len(TOOL_SLUGS)
        try:
            TOOL_SLUGS.append("extra")
        except (AttributeError, TypeError, Exception):
            pass  # Expected for frozen collections
        assert len(TOOL_SLUGS) == original_len, "TOOL_SLUGS should not be mutable"

    def test_goodhart_all_lowercase(self):
        """Every entry in TOOL_SLUGS must be lowercase"""
        for slug in TOOL_SLUGS:
            assert slug == slug.lower(), f"TOOL_SLUGS entry {slug!r} is not lowercase"

    def test_goodhart_all_kebab_case(self):
        """Every entry in TOOL_SLUGS must be URL-safe kebab-case (lowercase alphanumeric and hyphens)"""
        pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
        for slug in TOOL_SLUGS:
            assert pattern.match(slug), f"TOOL_SLUGS entry {slug!r} is not valid kebab-case"


# ─── StepNumber: complete range and rejection ───

class TestGoodhartStepNumber:

    def test_goodhart_all_valid_range(self):
        """StepNumber must accept every integer from 1 through 11 inclusive"""
        for n in range(1, 12):
            result = StepNumber(n)
            assert result is not None, f"StepNumber({n}) should be valid"

    def test_goodhart_out_of_range_rejection(self):
        """StepNumber must reject integers outside 1-11 range"""
        for n in [0, -1, 12, 13, 100, -100]:
            with pytest.raises(Exception):
                StepNumber(n)

    def test_goodhart_non_integer_rejection(self):
        """StepNumber must reject non-integer types"""
        for val in [1.5, "1", None, True]:
            with pytest.raises(Exception):
                StepNumber(val)


# ─── GoogleFontLink: content validation ───

class TestGoodhartGoogleFontLink:

    def test_goodhart_preconnect_origins_present(self):
        """GoogleFontLink must include non-empty preconnect_origins for proper font loading"""
        link = GoogleFontLink(
            href="https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap",
            preconnect_origins=["https://fonts.googleapis.com", "https://fonts.gstatic.com"]
        )
        assert len(link.preconnect_origins) > 0

    def test_goodhart_href_must_have_family_param(self):
        """GoogleFontLink href must contain a family parameter between 'css2?family=' and '&display=swap'"""
        # Valid: has family param
        valid_href = "https://fonts.googleapis.com/css2?family=Instrument+Serif&display=swap"
        link = GoogleFontLink(href=valid_href, preconnect_origins=[])
        assert "family=" in link.href

    def test_goodhart_href_rejects_missing_display_swap(self):
        """GoogleFontLink must reject hrefs that don't end with &display=swap"""
        with pytest.raises(Exception):
            GoogleFontLink(
                href="https://fonts.googleapis.com/css2?family=Instrument+Serif",
                preconnect_origins=[]
            )

    def test_goodhart_href_rejects_wrong_domain(self):
        """GoogleFontLink must reject hrefs pointing to non-Google Fonts domains"""
        with pytest.raises(Exception):
            GoogleFontLink(
                href="https://fonts.example.com/css2?family=Roboto&display=swap",
                preconnect_origins=[]
            )


# ─── isValidToolSlug + toolPath consistency ───

class TestGoodhartCrossFunction:

    def test_goodhart_valid_slugs_produce_valid_paths(self):
        """Every string accepted by isValidToolSlug must produce a valid path via toolPath"""
        for slug in TOOL_SLUGS:
            assert isValidToolSlug(slug) is True
            path = toolPath(slug)
            assert path == f"/{slug}"

    def test_goodhart_tool_slugs_and_validator_agree(self):
        """TOOL_SLUGS entries and isValidToolSlug must agree on exactly which strings are valid"""
        # All TOOL_SLUGS entries should be valid
        for slug in TOOL_SLUGS:
            assert isValidToolSlug(slug) is True

        # A broad sample of non-slug strings should be invalid
        non_slugs = ["", "foo", "bar", "test", "tool", "slug", "home", "app",
                      "123", "constrain1", "1constrain"]
        for s in non_slugs:
            if s not in set(TOOL_SLUGS):
                assert isValidToolSlug(s) is False, f"isValidToolSlug({s!r}) should be False"
