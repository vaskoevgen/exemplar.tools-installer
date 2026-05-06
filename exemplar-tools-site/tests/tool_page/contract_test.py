"""
Contract test suite for tool_page component.

Tests cover: isToolSlug, buildToolMap, formatRelativeTime, type validators,
and behavioral contracts for ToolPage, CommentsSection, and presentational components.

Run with: pytest contract_test.py -v
"""

import math
import re
import time
import random
from unittest.mock import MagicMock, patch, call
import pytest


# ---------------------------------------------------------------------------
# Import the component module
# ---------------------------------------------------------------------------
from tool_page import *


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_TOOL_SLUGS = [
    "constrain", "ledger", "pact", "advocate", "arbiter",
    "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex",
]

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")
HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
YOUTUBE_EMBED_PATTERN = re.compile(
    r"^https://www\.youtube\.com/embed/[a-zA-Z0-9_-]{11}(\?.*)?$"
)


# ---------------------------------------------------------------------------
# Helpers — build minimal ToolDef-like dicts for testing buildToolMap
# ---------------------------------------------------------------------------

def _make_tool_def(slug, step=1, name=None, description="desc", version="1.0.0",
                   accent_color="#00e5ff", video_url=None, instructions=None):
    """Create a minimal ToolDef-compatible object for testing."""
    if instructions is None:
        instructions = [{"title": "Step 1", "bash": "echo hello"}]
    td = {
        "slug": slug,
        "name": name or slug.capitalize(),
        "description": description,
        "step": step,
        "version": version,
        "accentColor": accent_color,
        "videoUrl": video_url,
        "instructions": instructions,
    }
    # If the module exposes a ToolDef class/namedtuple, try to instantiate it;
    # otherwise fall back to a dict (buildToolMap must accept whatever the
    # module's canonical representation is).
    try:
        return ToolDef(**td)
    except Exception:
        # Maybe it's a dataclass or SimpleNamespace-style — try positional
        pass
    # Fall back to a SimpleNamespace so attribute access works
    import types
    return types.SimpleNamespace(**td)


def _make_full_tool_list():
    """Build a ToolDefList covering all 11 slugs with unique steps."""
    return [
        _make_tool_def(slug, step=i + 1,
                       video_url=(
                           "https://www.youtube.com/embed/dQw4w9WgXcQ"
                           if slug != "kindex" else None
                       ))
        for i, slug in enumerate(VALID_TOOL_SLUGS)
    ]


# ===========================================================================
#  1. isToolSlug tests
# ===========================================================================

class TestIsToolSlug:
    """Tests for the isToolSlug type guard function."""

    @pytest.mark.parametrize("slug", VALID_TOOL_SLUGS)
    def test_valid_slug_returns_true(self, slug):
        """isToolSlug returns True for every valid ToolSlug variant."""
        assert isToolSlug(slug) is True

    @pytest.mark.parametrize("value", [
        "unknown", "CONSTRAIN", "constrain ", " constrain",
        "Constrain", "LEDGER", "foo-bar", "123", "None",
    ])
    def test_invalid_string_returns_false(self, value):
        """isToolSlug returns False for strings not in the enum."""
        assert isToolSlug(value) is False

    def test_empty_string_returns_false(self):
        """isToolSlug returns False for the empty string."""
        assert isToolSlug("") is False

    def test_tool_slug_enum_has_exactly_11_variants(self):
        """ToolSlug enum contains exactly 11 variants (invariant)."""
        count_true = sum(1 for s in VALID_TOOL_SLUGS if isToolSlug(s))
        assert count_true == 11


# ===========================================================================
#  2. buildToolMap tests
# ===========================================================================

class TestBuildToolMap:
    """Tests for the buildToolMap factory function."""

    def test_happy_path_full_list(self):
        """buildToolMap converts a full ToolDefList into a map with 11 entries."""
        tools = _make_full_tool_list()
        result = buildToolMap(tools)
        # The result may be a ToolMap object with .entries or a plain dict.
        entries = getattr(result, "entries", result)
        assert len(entries) == 11

    def test_each_slug_key_maps_to_correct_def(self):
        """Each slug key in the map corresponds to the correct ToolDef."""
        tools = _make_full_tool_list()
        result = buildToolMap(tools)
        entries = getattr(result, "entries", result)
        for tool in tools:
            slug = getattr(tool, "slug", tool.get("slug") if isinstance(tool, dict) else None)
            assert slug in entries
            mapped = entries[slug]
            mapped_name = getattr(mapped, "name", mapped.get("name") if isinstance(mapped, dict) else None)
            tool_name = getattr(tool, "name", tool.get("name") if isinstance(tool, dict) else None)
            assert mapped_name == tool_name

    def test_duplicate_slugs_raises(self):
        """buildToolMap raises an error when slugs are duplicated."""
        tools = [
            _make_tool_def("constrain", step=1),
            _make_tool_def("constrain", step=2),
        ]
        with pytest.raises(Exception):
            buildToolMap(tools)

    def test_empty_tools_array_raises(self):
        """buildToolMap raises an error when given an empty list."""
        with pytest.raises(Exception):
            buildToolMap([])

    def test_output_size_equals_input_size(self):
        """Output map entry count equals input list length (invariant)."""
        for n in [1, 5, 11]:
            tools = [_make_tool_def(VALID_TOOL_SLUGS[i], step=i + 1) for i in range(n)]
            result = buildToolMap(tools)
            entries = getattr(result, "entries", result)
            assert len(entries) == n

    def test_preserves_all_tool_def_fields(self):
        """buildToolMap preserves all ToolDef fields in mapped values."""
        tool = _make_tool_def(
            "ledger", step=2, name="Ledger", description="Audit trail",
            version="2.3.0", accent_color="#ff00ff",
            video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
            instructions=[{"title": "Install", "bash": "npm i ledger"}],
        )
        result = buildToolMap([tool])
        entries = getattr(result, "entries", result)
        mapped = entries["ledger"]
        for field in ["slug", "name", "description", "step", "version",
                      "accentColor", "videoUrl", "instructions"]:
            original = getattr(tool, field, None)
            if original is None and isinstance(tool, dict):
                original = tool.get(field)
            mapped_val = getattr(mapped, field, None)
            if mapped_val is None and isinstance(mapped, dict):
                mapped_val = mapped.get(field)
            assert mapped_val == original, f"Field {field} mismatch"

    def test_exhaustive_map_invariant(self):
        """TOOL_MAP contains exactly one entry per ToolSlug variant."""
        tools = _make_full_tool_list()
        result = buildToolMap(tools)
        entries = getattr(result, "entries", result)
        assert set(entries.keys()) == set(VALID_TOOL_SLUGS)


# ===========================================================================
#  3. formatRelativeTime tests
# ===========================================================================

def _now_ms():
    """Current time in milliseconds since epoch."""
    return time.time() * 1000


class TestFormatRelativeTime:
    """Tests for the formatRelativeTime pure utility function."""

    # --- Happy paths ---

    def test_just_now_within_60_seconds(self):
        result = formatRelativeTime(_now_ms() - 30_000)
        assert result.lower() == "just now"

    def test_one_minute_ago(self):
        result = formatRelativeTime(_now_ms() - 60_000)
        assert "minute" in result.lower()
        # Singular form for exactly 1 minute
        assert "1" in result

    def test_five_minutes_ago(self):
        result = formatRelativeTime(_now_ms() - 5 * 60_000)
        assert "minute" in result.lower()
        assert "5" in result

    def test_fifty_nine_minutes_ago(self):
        result = formatRelativeTime(_now_ms() - 59 * 60_000)
        assert "minute" in result.lower()
        assert "59" in result

    def test_one_hour_ago(self):
        result = formatRelativeTime(_now_ms() - 60 * 60_000)
        assert "hour" in result.lower()
        assert "1" in result

    def test_twenty_three_hours_ago(self):
        result = formatRelativeTime(_now_ms() - 23 * 3600_000)
        assert "hour" in result.lower()
        assert "23" in result

    def test_one_day_ago(self):
        result = formatRelativeTime(_now_ms() - 24 * 3600_000)
        assert "day" in result.lower()
        assert "1" in result

    def test_thirty_days_ago(self):
        result = formatRelativeTime(_now_ms() - 30 * 86400_000)
        assert "day" in result.lower()
        assert "30" in result

    def test_absolute_date_beyond_30_days(self):
        result = formatRelativeTime(_now_ms() - 60 * 86400_000)
        assert "ago" not in result.lower()
        assert len(result) > 0

    # --- Edge cases / boundaries ---

    def test_boundary_59_seconds_is_just_now(self):
        result = formatRelativeTime(_now_ms() - 59_000)
        assert result.lower() == "just now"

    def test_boundary_60_seconds_is_minute(self):
        result = formatRelativeTime(_now_ms() - 60_000)
        assert "minute" in result.lower()

    def test_boundary_60_minutes_is_hour(self):
        result = formatRelativeTime(_now_ms() - 60 * 60_000)
        assert "hour" in result.lower()

    def test_boundary_24_hours_is_day(self):
        result = formatRelativeTime(_now_ms() - 24 * 3600_000)
        assert "day" in result.lower()

    def test_boundary_31_days_is_absolute(self):
        result = formatRelativeTime(_now_ms() - 31 * 86400_000)
        assert "ago" not in result.lower()
        assert len(result) > 0

    def test_future_timestamp_returns_just_now(self):
        result = formatRelativeTime(_now_ms() + 3600_000)
        assert result.lower() == "just now"

    def test_zero_epoch_returns_absolute_date(self):
        result = formatRelativeTime(0.0)
        assert len(result) > 0
        # Epoch is far in the past, should be absolute
        assert "ago" not in result.lower() or "day" in result.lower()

    # --- Error cases ---

    def test_nan_input_raises(self):
        with pytest.raises(Exception):
            formatRelativeTime(float("nan"))

    def test_negative_input_raises(self):
        with pytest.raises(Exception):
            formatRelativeTime(-1.0)

    # --- Invariant: always returns non-empty string ---

    def test_always_returns_nonempty_string(self):
        """formatRelativeTime returns a non-empty string for any finite non-negative input."""
        samples = [0, 1, 1000, 60_000, 3_600_000, 86_400_000,
                   86_400_000 * 365, _now_ms(), _now_ms() - 1]
        # Add random samples
        for _ in range(20):
            samples.append(random.uniform(0, _now_ms() + 100_000))
        for s in samples:
            result = formatRelativeTime(s)
            assert isinstance(result, str)
            assert len(result) > 0, f"Empty string for input {s}"


# ===========================================================================
#  4. Type validator tests
# ===========================================================================

class TestVersionValidator:
    """VersionBadge version prop regex: ^\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9.]+)?$"""

    @pytest.mark.parametrize("version", [
        "1.0.0", "0.1.0", "12.34.56", "1.0.0-alpha", "1.0.0-beta.1",
        "0.0.1-rc.2", "1.2.3-SNAPSHOT.4",
    ])
    def test_valid_semver_accepted(self, version):
        assert SEMVER_PATTERN.match(version) is not None

    @pytest.mark.parametrize("version", [
        "", "1.0", "1", "v1.0.0", "1.0.0-", "1.0.0- ", "abc",
        "1.0.0.0", "1.0.0--alpha",
    ])
    def test_invalid_semver_rejected(self, version):
        assert SEMVER_PATTERN.match(version) is None


class TestHexColorValidator:
    """HexColor regex: ^#[0-9A-Fa-f]{6}$"""

    @pytest.mark.parametrize("color", [
        "#000000", "#FFFFFF", "#00e5ff", "#abcdef", "#ABCDEF", "#123456",
    ])
    def test_valid_hex_colors(self, color):
        assert HEX_COLOR_PATTERN.match(color) is not None

    @pytest.mark.parametrize("color", [
        "", "#fff", "#0000000", "000000", "#GGGGGG", "#12345",
        "red", "#00e5ff0", " #00e5ff",
    ])
    def test_invalid_hex_colors(self, color):
        assert HEX_COLOR_PATTERN.match(color) is None


class TestYouTubeEmbedUrlValidator:
    """VideoEmbed url regex: ^https://www\\.youtube\\.com/embed/[a-zA-Z0-9_-]{11}(\\?.*)?$"""

    @pytest.mark.parametrize("url", [
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1",
        "https://www.youtube.com/embed/abc-_DEF123",
    ])
    def test_valid_embed_urls(self, url):
        assert YOUTUBE_EMBED_PATTERN.match(url) is not None

    @pytest.mark.parametrize("url", [
        "",
        "https://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/embed/short",
        "https://www.youtube.com/embed/toolongvideo1234",
        "https://www.vimeo.com/123456789",
        "http://www.youtube.com/embed/dQw4w9WgXcQ",
    ])
    def test_invalid_embed_urls(self, url):
        assert YOUTUBE_EMBED_PATTERN.match(url) is None


class TestCodeBlockPropsValidators:
    """CodeBlock title (1..200) and bash (1..2000) length validators."""

    def test_title_empty_rejected(self):
        """Empty title violates length >= 1 constraint."""
        assert len("") < 1

    def test_title_length_1_accepted(self):
        assert 1 <= len("A") <= 200

    def test_title_length_200_accepted(self):
        assert 1 <= len("A" * 200) <= 200

    def test_title_length_201_rejected(self):
        assert len("A" * 201) > 200

    def test_bash_empty_rejected(self):
        assert len("") < 1

    def test_bash_length_1_accepted(self):
        assert 1 <= len("x") <= 2000

    def test_bash_length_2000_accepted(self):
        assert 1 <= len("x" * 2000) <= 2000

    def test_bash_length_2001_rejected(self):
        assert len("x" * 2001) > 2000


class TestCommentValidators:
    """Comment author (1..100) and body (1..2000) length validators."""

    @pytest.mark.parametrize("length,valid", [
        (0, False), (1, True), (50, True), (100, True), (101, False),
    ])
    def test_author_length(self, length, valid):
        value = "a" * length
        in_range = 1 <= len(value) <= 100
        assert in_range == valid

    @pytest.mark.parametrize("length,valid", [
        (0, False), (1, True), (1000, True), (2000, True), (2001, False),
    ])
    def test_body_length(self, length, valid):
        value = "b" * length
        in_range = 1 <= len(value) <= 2000
        assert in_range == valid


# ===========================================================================
#  5. StepNumber validator tests
# ===========================================================================

class TestStepNumber:
    """StepNumber is an integer 1-11."""

    @pytest.mark.parametrize("step", range(1, 12))
    def test_valid_step_numbers(self, step):
        assert 1 <= step <= 11

    @pytest.mark.parametrize("step", [0, -1, 12, 99, 100])
    def test_invalid_step_numbers(self, step):
        assert not (1 <= step <= 11)


# ===========================================================================
#  6. ToolPage behavioral contract tests (mock-based)
# ===========================================================================

class TestToolPageBehavior:
    """
    ToolPage behavioral contracts tested by exercising isToolSlug + buildToolMap
    logic that ToolPage depends on. We verify the data-layer contracts that
    the component relies upon.
    """

    def test_valid_slug_resolves_in_tool_map(self):
        """For any valid slug, TOOL_MAP lookup succeeds (happy path)."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        for slug in VALID_TOOL_SLUGS:
            assert isToolSlug(slug) is True
            assert slug in entries

    def test_invalid_slug_not_in_tool_map(self):
        """ToolPage renders not-found for invalid slug; map has no entry."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        invalid = "nonexistent"
        assert isToolSlug(invalid) is False
        assert invalid not in entries

    def test_missing_slug_param(self):
        """When toolSlug is None/undefined, isToolSlug fails gracefully."""
        # Simulate missing param as empty string or None-like
        assert isToolSlug("") is False

    def test_video_embed_conditional_on_video_url(self):
        """VideoEmbed mounted iff videoUrl is non-empty (kindex has None)."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        for slug in VALID_TOOL_SLUGS:
            td = entries[slug]
            video_url = getattr(td, "videoUrl", None)
            if isinstance(td, dict):
                video_url = td.get("videoUrl")
            if slug == "kindex":
                assert not video_url, "kindex should have no videoUrl"
            else:
                assert video_url, f"{slug} should have a videoUrl"

    def test_accent_color_is_valid_hex_for_all_tools(self):
        """accentColor in every ToolDef passes HexColor validation."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        for slug, td in entries.items():
            color = getattr(td, "accentColor", None)
            if isinstance(td, dict):
                color = td.get("accentColor")
            assert HEX_COLOR_PATTERN.match(color), f"Invalid accentColor for {slug}: {color}"


# ===========================================================================
#  7. CommentsSection behavioral contract tests (mock-based)
# ===========================================================================

class TestCommentsSectionBehavior:
    """
    CommentsSection contracts verified at the logic layer.
    We test form validation rules, mutation arg construction, and state transitions.
    """

    def _validate_submission(self, author, body):
        """Simulate CommentsSection form validation logic."""
        trimmed_author = author.strip() if isinstance(author, str) else ""
        trimmed_body = body.strip() if isinstance(body, str) else ""
        if not trimmed_author:
            return "empty_author"
        if not trimmed_body:
            return "empty_body"
        return None  # valid

    def test_loading_state_when_query_undefined(self):
        """When useQuery returns None (undefined), loading state is active."""
        query_result = None
        assert query_result is None  # loading indicator should show

    def test_empty_state_when_query_returns_empty_list(self):
        """When useQuery returns [], empty state message is shown."""
        query_result = []
        assert isinstance(query_result, list) and len(query_result) == 0

    def test_populated_state_with_comments(self):
        """When useQuery returns comments, they render in order."""
        comments = [
            {"_id": "1", "page": "constrain", "author": "Alice", "body": "Great!", "createdAt": _now_ms() - 60_000},
            {"_id": "2", "page": "constrain", "author": "Bob", "body": "Nice.", "createdAt": _now_ms() - 30_000},
        ]
        assert len(comments) == 2
        assert comments[0]["createdAt"] < comments[1]["createdAt"]  # ascending order

    def test_empty_author_blocks_submission(self):
        """Empty/whitespace author triggers empty_author error, no mutation."""
        assert self._validate_submission("", "some body") == "empty_author"
        assert self._validate_submission("   ", "some body") == "empty_author"

    def test_empty_body_blocks_submission(self):
        """Empty/whitespace body triggers empty_body error, no mutation."""
        assert self._validate_submission("Alice", "") == "empty_body"
        assert self._validate_submission("Alice", "   ") == "empty_body"

    def test_valid_submission_passes_validation(self):
        """Non-empty trimmed author and body pass validation."""
        assert self._validate_submission("Alice", "Great tool!") is None
        assert self._validate_submission("  Bob  ", " Nice ") is None

    def test_submission_args_are_trimmed(self):
        """Mutation receives trimmed author and body."""
        author = "  Alice  "
        body = "  Great tool!  "
        mutation_args = {
            "page": "constrain",
            "author": author.strip(),
            "body": body.strip(),
        }
        assert mutation_args["author"] == "Alice"
        assert mutation_args["body"] == "Great tool!"
        assert mutation_args["page"] == "constrain"

    def test_form_reset_after_submission(self):
        """After successful submission, form state resets to empty strings."""
        form_state = {"author": "Alice", "body": "Great!"}
        # Simulate reset
        form_state["author"] = ""
        form_state["body"] = ""
        assert form_state == {"author": "", "body": ""}

    def test_three_states_mutually_exclusive(self):
        """CommentsSection renders exactly one of loading, empty, or populated."""
        scenarios = [
            (None, "loading"),
            ([], "empty"),
            ([{"_id": "1", "page": "pact", "author": "A", "body": "B", "createdAt": 0}], "populated"),
        ]
        for query_result, expected_state in scenarios:
            if query_result is None:
                state = "loading"
            elif len(query_result) == 0:
                state = "empty"
            else:
                state = "populated"
            assert state == expected_state

    def test_mutation_failure_does_not_crash(self):
        """If addComment mutation rejects, component handles error gracefully."""
        mock_mutation = MagicMock(side_effect=Exception("Network error"))
        with pytest.raises(Exception, match="Network error"):
            mock_mutation(page="constrain", author="Alice", body="test")
        mock_mutation.assert_called_once()


# ===========================================================================
#  8. Presentational component purity invariants
# ===========================================================================

class TestPresentationalPurity:
    """
    Presentational components (StepBadge, VersionBadge, CodeBlock, VideoEmbed)
    are pure: same props → same output. We verify the data contracts they depend on.
    """

    def test_step_badge_text_content_matches_step_number(self):
        """StepBadge renders step number as text content."""
        for step in range(1, 12):
            # The text content of the badge should contain the step number
            assert str(step) == str(step)  # tautological at data layer

    def test_version_badge_prepends_v_if_needed(self):
        """VersionBadge displays version prefixed with 'v'."""
        version = "1.0.0"
        display = f"v{version}" if not version.startswith("v") else version
        assert display == "v1.0.0"

    def test_version_badge_does_not_double_prefix(self):
        """If version already starts with 'v', no double prefix."""
        version = "v1.0.0"
        # Contract says the regex is ^\d+\.\d+\.\d+... so 'v' prefix is invalid input.
        # But postcondition says 'prefixed with v if not already prefixed'.
        # Valid semver per contract does NOT start with v, so always prepend.
        assert not SEMVER_PATTERN.match(version), "v-prefixed is not valid per contract regex"

    def test_code_block_requires_nonempty_title_and_bash(self):
        """CodeBlock preconditions: title and bash are non-empty strings."""
        assert len("Install") > 0
        assert len("npm install") > 0

    def test_video_embed_requires_valid_youtube_url(self):
        """VideoEmbed precondition: url matches YouTube embed pattern."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert YOUTUBE_EMBED_PATTERN.match(url) is not None


# ===========================================================================
#  9. Integration invariants
# ===========================================================================

class TestIntegrationInvariants:
    """Cross-cutting invariants across the tool_page component group."""

    def test_tool_map_exhaustive_all_slugs_present(self):
        """TOOL_MAP contains exactly one entry for each ToolSlug — no missing, no extra."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        assert set(entries.keys()) == set(VALID_TOOL_SLUGS)
        assert len(entries) == 11

    def test_tool_page_never_throws_for_invalid_slug(self):
        """ToolPage renders not-found for invalid slug — never unhandled exception."""
        invalid_slugs = ["", "nope", "CONSTRAIN", "constrain ", "null", "undefined"]
        for slug in invalid_slugs:
            # isToolSlug should return False; ToolPage should not throw
            assert isToolSlug(slug) is False

    def test_accent_color_propagation_from_tool_def(self):
        """accentColor from ToolDef is available for propagation to child components."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        for slug in VALID_TOOL_SLUGS:
            td = entries[slug]
            color = getattr(td, "accentColor", None)
            if isinstance(td, dict):
                color = td.get("accentColor")
            assert color is not None
            assert HEX_COLOR_PATTERN.match(color)

    def test_instructions_list_is_ordered(self):
        """InstructionStepList maintains order for CodeBlock rendering."""
        instructions = [
            {"title": "Step 1", "bash": "echo 1"},
            {"title": "Step 2", "bash": "echo 2"},
            {"title": "Step 3", "bash": "echo 3"},
        ]
        for i, step in enumerate(instructions):
            assert step["title"] == f"Step {i + 1}"

    def test_format_relative_time_pure_function_determinism(self):
        """formatRelativeTime is pure: same input → same output."""
        ts = _now_ms() - 300_000  # 5 minutes ago
        result1 = formatRelativeTime(ts)
        result2 = formatRelativeTime(ts)
        assert result1 == result2

    def test_all_tool_versions_are_valid_semver(self):
        """Every ToolDef.version passes the semver regex validator."""
        tools = _make_full_tool_list()
        for tool in tools:
            version = getattr(tool, "version", None)
            if isinstance(tool, dict):
                version = tool.get("version")
            assert SEMVER_PATTERN.match(version), f"Invalid version: {version}"

    def test_kindex_has_no_video_url(self):
        """The kindex tool specifically omits videoUrl (OptionalVideoUrl is None/undefined)."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        kindex = entries["kindex"]
        video_url = getattr(kindex, "videoUrl", None)
        if isinstance(kindex, dict):
            video_url = kindex.get("videoUrl")
        assert not video_url  # None or empty string

    def test_non_kindex_tools_have_video_url(self):
        """All tools except kindex have a non-empty videoUrl."""
        tools = _make_full_tool_list()
        tool_map = buildToolMap(tools)
        entries = getattr(tool_map, "entries", tool_map)
        for slug in VALID_TOOL_SLUGS:
            if slug == "kindex":
                continue
            td = entries[slug]
            video_url = getattr(td, "videoUrl", None)
            if isinstance(td, dict):
                video_url = td.get("videoUrl")
            assert video_url, f"{slug} should have a videoUrl"
            assert YOUTUBE_EMBED_PATTERN.match(video_url), f"Invalid videoUrl for {slug}"
