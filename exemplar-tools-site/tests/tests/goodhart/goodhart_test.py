"""
Adversarial hidden acceptance tests for the Test Harness & Smoke Tests component.

These tests catch implementations that pass visible tests via shortcuts
(hardcoded returns, incomplete validation, etc.) rather than genuinely
satisfying the contract.
"""

import re
import pytest
from tests import (
    configure_vitest,
    initialize_setup_file,
    validate_tools_array_length,
    validate_tools_slugs_ordered,
    validate_tool_required_fields,
    validate_kindex_no_video_url,
    validate_non_kindex_have_video_url,
    execute_test_suite,
    VitestConfigBlock,
    SetupFilePath,
    GlobPattern,
    ExitCode,
    TestSuiteResult,
    VitestEnvironment,
    ToolFieldName,
    TestFile,
    DevDependency,
    ConvexMockConfig,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool(**overrides):
    """Create a minimal valid tool dict, with optional overrides."""
    base = {
        "name": "Test Tool",
        "description": "A test tool description",
        "version": "1.0.0",
        "accentColor": "#abcdef",
        "step": 5,
        "slug": "test-tool",
        "videoUrl": "https://example.com/video.mp4",
    }
    base.update(overrides)
    return base


def _make_tools_list(n=11, slugs=None):
    """Create a list of n tool dicts with unique slugs."""
    if slugs is None:
        slugs = [f"tool-{i}" for i in range(n)]
    tools = []
    for i, slug in enumerate(slugs):
        tools.append(_make_tool(
            name=f"Tool {i}",
            slug=slug,
            step=min(i + 1, 11),
            videoUrl="https://example.com/v.mp4" if slug != "kindex" else None,
        ))
    return tools


# ---------------------------------------------------------------------------
# configure_vitest: structural and type-level checks
# ---------------------------------------------------------------------------

class TestGoodhartConfigureVitest:
    """Tests that configure_vitest returns a properly structured VitestConfigBlock."""

    def test_goodhart_setupfiles_is_list_of_exactly_one(self, tmp_path, monkeypatch):
        """The setupFiles field must be a list containing exactly one entry."""
        # Ensure vite.config.ts exists for precondition
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable or raised precondition error")
        assert isinstance(result.setupFiles, list), "setupFiles must be a list"
        assert len(result.setupFiles) == 1, "setupFiles must have exactly one entry"

    def test_goodhart_include_is_list_of_exactly_one(self, tmp_path, monkeypatch):
        """The include field must be a list containing exactly one glob pattern."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable or raised precondition error")
        assert isinstance(result.include, list), "include must be a list"
        assert len(result.include) == 1, "include must have exactly one entry"

    def test_goodhart_returns_struct_with_named_attributes(self, tmp_path, monkeypatch):
        """Return value must expose all four VitestConfigBlock fields as attributes."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        for attr in ("environment", "globals", "setupFiles", "include"):
            assert hasattr(result, attr), f"Missing attribute: {attr}"

    def test_goodhart_setup_path_matches_regex(self, tmp_path, monkeypatch):
        """setupFiles[0] must conform to the SetupFilePath regex validator."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        path = result.setupFiles[0]
        assert re.match(r"^\./src/__tests__/[a-zA-Z0-9_-]+\.ts$", path), (
            f"setupFiles path '{path}' does not match SetupFilePath regex"
        )

    def test_goodhart_include_pattern_matches_regex(self, tmp_path, monkeypatch):
        """include[0] must conform to the GlobPattern regex validator."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        pattern = result.include[0]
        assert re.match(r"^src/.+\.test\.\{[a-z,]+\}$", pattern), (
            f"include pattern '{pattern}' does not match GlobPattern regex"
        )

    def test_goodhart_idempotent_calls(self, tmp_path, monkeypatch):
        """Multiple invocations must return structurally equivalent results."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            r1 = configure_vitest()
            r2 = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        assert r1.environment == r2.environment
        assert r1.globals == r2.globals
        assert r1.setupFiles == r2.setupFiles
        assert r1.include == r2.include

    def test_goodhart_globals_is_bool_true_not_truthy(self, tmp_path, monkeypatch):
        """globals must be exactly boolean True, not 1 or 'true'."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        assert result.globals is True, "globals must be boolean True"
        assert type(result.globals) is bool, "globals must be bool type"

    def test_goodhart_environment_is_string_jsdom(self, tmp_path, monkeypatch):
        """environment must be the plain string 'jsdom'."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        assert result.environment == "jsdom"
        assert isinstance(result.environment, str)

    def test_goodhart_include_contains_tsx_and_ts(self, tmp_path, monkeypatch):
        """The include glob must reference both ts and tsx extensions."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        pattern = result.include[0]
        assert "tsx" in pattern, "include pattern must contain tsx"
        assert "ts" in pattern, "include pattern must contain ts"

    def test_goodhart_include_uses_double_star(self, tmp_path, monkeypatch):
        """The include pattern must use '**' for recursive matching."""
        vite_cfg = tmp_path / "vite.config.ts"
        vite_cfg.write_text("export default {}")
        monkeypatch.chdir(tmp_path)
        try:
            result = configure_vitest()
        except Exception:
            pytest.skip("configure_vitest unavailable")
        assert "**" in result.include[0], "include pattern must contain ** for recursion"


# ---------------------------------------------------------------------------
# validate_tools_array_length: boundary and type checks
# ---------------------------------------------------------------------------

class TestGoodhartValidateToolsArrayLength:

    def test_goodhart_rejects_none_input(self):
        """Must reject None input, not silently return True."""
        with pytest.raises(Exception):
            validate_tools_array_length(None)

    def test_goodhart_rejects_string_of_length_11(self):
        """A string with 11 characters must not pass the cardinality check."""
        with pytest.raises(Exception):
            validate_tools_array_length("abcdefghijk")

    def test_goodhart_rejects_ten_items(self):
        """10 items (one below required) must be rejected."""
        tools = _make_tools_list(10)
        with pytest.raises(Exception):
            validate_tools_array_length(tools)

    def test_goodhart_rejects_twelve_items(self):
        """12 items (one above required) must be rejected."""
        tools = _make_tools_list(12)
        with pytest.raises(Exception):
            validate_tools_array_length(tools)

    def test_goodhart_accepts_exactly_eleven(self):
        """Exactly 11 items must return True."""
        tools = _make_tools_list(11)
        assert validate_tools_array_length(tools) is True


# ---------------------------------------------------------------------------
# validate_tool_required_fields: comprehensive field validation
# ---------------------------------------------------------------------------

class TestGoodhartValidateToolRequiredFields:

    def test_goodhart_name_none_raises(self):
        """None name must trigger missing_name, not just empty string."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(name=None))

    def test_goodhart_description_none_raises(self):
        """None description must trigger missing_description."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(description=None))

    def test_goodhart_version_none_raises(self):
        """None version must trigger missing_version."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(version=None))

    def test_goodhart_step_negative_raises(self):
        """Negative step must be rejected, testing beyond visible 0 and 12."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(step=-1))

    def test_goodhart_step_float_raises(self):
        """Float step (e.g. 5.5) must be rejected as not an integer."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(step=5.5))

    def test_goodhart_step_string_raises(self):
        """String step (e.g. '5') must be rejected as wrong type."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(step="5"))

    def test_goodhart_step_large_positive_raises(self):
        """Step=100 must be rejected, not just values 12 and above the visible tests."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(step=100))

    def test_goodhart_accent_color_no_hash_raises(self):
        """Hex digits without '#' prefix must be rejected."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(accentColor="abcdef"))

    def test_goodhart_accent_color_8digit_raises(self):
        """8-digit hex (with alpha) must be rejected."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(accentColor="#abcdef99"))

    def test_goodhart_accent_color_non_hex_chars_raises(self):
        """Non-hex characters in color must be rejected."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(accentColor="#gggggg"))

    def test_goodhart_accent_color_empty_string_raises(self):
        """Empty accentColor string must be rejected."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(accentColor=""))

    def test_goodhart_accent_color_uppercase_accepted(self):
        """Uppercase hex digits must be accepted per the regex."""
        assert validate_tool_required_fields(_make_tool(accentColor="#ABCDEF")) is True

    def test_goodhart_accent_color_mixed_case_accepted(self):
        """Mixed-case hex digits must be accepted."""
        assert validate_tool_required_fields(_make_tool(accentColor="#aB3Cd9")) is True

    def test_goodhart_step_midrange_accepted(self):
        """Mid-range step=6 must be accepted (not just boundaries 1 and 11)."""
        assert validate_tool_required_fields(_make_tool(step=6)) is True

    def test_goodhart_name_whitespace_only_raises(self):
        """Whitespace-only name should be treated as empty."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(name="   "))

    def test_goodhart_missing_name_key_entirely_raises(self):
        """Tool dict missing 'name' key entirely must raise."""
        tool = _make_tool()
        del tool["name"]
        with pytest.raises(Exception):
            validate_tool_required_fields(tool)

    def test_goodhart_name_is_number_raises(self):
        """Numeric name (non-string) must be rejected."""
        with pytest.raises(Exception):
            validate_tool_required_fields(_make_tool(name=42))


# ---------------------------------------------------------------------------
# validate_tools_slugs_ordered: ordering and uniqueness checks
# ---------------------------------------------------------------------------

class TestGoodhartValidateToolsSlugsOrdered:

    def test_goodhart_duplicate_slugs_rejected(self):
        """Array with duplicate slugs must fail even if length is correct."""
        canonical = [f"slug-{i}" for i in range(11)]
        duplicated = list(canonical)
        duplicated[1] = duplicated[0]  # duplicate first slug into second position
        tools = _make_tools_list(11, slugs=duplicated)
        with pytest.raises(Exception):
            validate_tools_slugs_ordered(tools, canonical)

    def test_goodhart_first_last_swap_rejected(self):
        """Swapping first and last slugs must be detected as mismatch."""
        canonical = [f"slug-{i}" for i in range(11)]
        swapped = list(canonical)
        swapped[0], swapped[10] = swapped[10], swapped[0]
        tools = _make_tools_list(11, slugs=swapped)
        with pytest.raises(Exception):
            validate_tools_slugs_ordered(tools, canonical)

    def test_goodhart_empty_slug_value_rejected(self):
        """A tool with empty string slug must not match canonical array."""
        canonical = [f"slug-{i}" for i in range(11)]
        modified = list(canonical)
        modified[5] = ""
        tools = _make_tools_list(11, slugs=modified)
        with pytest.raises(Exception):
            validate_tools_slugs_ordered(tools, canonical)

    def test_goodhart_correct_order_accepted(self):
        """Exact match in order must return True."""
        canonical = [f"slug-{i}" for i in range(11)]
        tools = _make_tools_list(11, slugs=canonical)
        assert validate_tools_slugs_ordered(tools, canonical) is True


# ---------------------------------------------------------------------------
# validate_kindex_no_video_url: edge cases
# ---------------------------------------------------------------------------

class TestGoodhartValidateKindexNoVideoUrl:

    def test_goodhart_kindex_videourl_none_is_undefined(self):
        """kindex with videoUrl=None should pass (treated as undefined)."""
        tools = _make_tools_list(11, slugs=[f"t-{i}" for i in range(10)] + ["kindex"])
        kindex_tool = next(t for t in tools if t["slug"] == "kindex")
        kindex_tool["videoUrl"] = None
        assert validate_kindex_no_video_url(tools) is True

    def test_goodhart_kindex_videourl_absent_key_passes(self):
        """kindex without videoUrl key should pass (undefined)."""
        tools = _make_tools_list(11, slugs=[f"t-{i}" for i in range(10)] + ["kindex"])
        kindex_tool = next(t for t in tools if t["slug"] == "kindex")
        kindex_tool.pop("videoUrl", None)
        assert validate_kindex_no_video_url(tools) is True

    def test_goodhart_kindex_videourl_empty_string_raises(self):
        """kindex with videoUrl='' has a defined value and should raise."""
        tools = _make_tools_list(11, slugs=[f"t-{i}" for i in range(10)] + ["kindex"])
        kindex_tool = next(t for t in tools if t["slug"] == "kindex")
        kindex_tool["videoUrl"] = ""
        with pytest.raises(Exception):
            validate_kindex_no_video_url(tools)


# ---------------------------------------------------------------------------
# validate_non_kindex_have_video_url: edge cases
# ---------------------------------------------------------------------------

class TestGoodhartValidateNonKindexHaveVideoUrl:

    def test_goodhart_whitespace_only_videourl_raises(self):
        """Non-kindex tool with whitespace-only videoUrl should be rejected."""
        slugs = [f"tool-{i}" for i in range(10)] + ["kindex"]
        tools = _make_tools_list(11, slugs=slugs)
        # Set a non-kindex tool's videoUrl to whitespace
        non_kindex = next(t for t in tools if t["slug"] != "kindex")
        non_kindex["videoUrl"] = "   "
        with pytest.raises(Exception):
            validate_non_kindex_have_video_url(tools)

    def test_goodhart_none_videourl_raises(self):
        """Non-kindex tool with videoUrl=None must be rejected."""
        slugs = [f"tool-{i}" for i in range(10)] + ["kindex"]
        tools = _make_tools_list(11, slugs=slugs)
        non_kindex = next(t for t in tools if t["slug"] != "kindex")
        non_kindex["videoUrl"] = None
        with pytest.raises(Exception):
            validate_non_kindex_have_video_url(tools)

    def test_goodhart_all_non_kindex_valid_passes(self):
        """All non-kindex tools with valid videoUrl must pass."""
        slugs = [f"tool-{i}" for i in range(10)] + ["kindex"]
        tools = _make_tools_list(11, slugs=slugs)
        # Ensure all non-kindex have valid URLs
        for t in tools:
            if t["slug"] != "kindex":
                t["videoUrl"] = "https://example.com/video.mp4"
        assert validate_non_kindex_have_video_url(tools) is True


# ---------------------------------------------------------------------------
# initialize_setup_file: return value and content checks
# ---------------------------------------------------------------------------

class TestGoodhartInitializeSetupFile:

    def test_goodhart_returns_none(self, tmp_path, monkeypatch):
        """initialize_setup_file must return None (side-effect only function)."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "src" / "__tests__").mkdir(parents=True, exist_ok=True)
        mock_config = ConvexMockConfig(
            useQuery_default=None,
            useMutation_default="vi.fn()",
        )
        try:
            result = initialize_setup_file(mock_config)
        except Exception:
            pytest.skip("initialize_setup_file precondition not met")
        assert result is None, "initialize_setup_file must return None"

    def test_goodhart_setup_file_created(self, tmp_path, monkeypatch):
        """initialize_setup_file must create the setup.ts file on disk."""
        monkeypatch.chdir(tmp_path)
        tests_dir = tmp_path / "src" / "__tests__"
        tests_dir.mkdir(parents=True, exist_ok=True)
        mock_config = ConvexMockConfig(
            useQuery_default=None,
            useMutation_default="vi.fn()",
        )
        try:
            initialize_setup_file(mock_config)
        except Exception:
            pytest.skip("initialize_setup_file precondition not met")
        setup_file = tests_dir / "setup.ts"
        assert setup_file.exists(), "setup.ts must be created"

    def test_goodhart_setup_file_contains_convex_react_mock(self, tmp_path, monkeypatch):
        """The generated setup.ts must contain 'convex/react' as the mock target string."""
        monkeypatch.chdir(tmp_path)
        tests_dir = tmp_path / "src" / "__tests__"
        tests_dir.mkdir(parents=True, exist_ok=True)
        mock_config = ConvexMockConfig(
            useQuery_default=None,
            useMutation_default="vi.fn()",
        )
        try:
            initialize_setup_file(mock_config)
        except Exception:
            pytest.skip("initialize_setup_file precondition not met")
        content = (tests_dir / "setup.ts").read_text()
        assert "convex/react" in content, "setup.ts must mock 'convex/react'"

    def test_goodhart_setup_file_contains_jest_dom_import(self, tmp_path, monkeypatch):
        """The generated setup.ts must import @testing-library/jest-dom."""
        monkeypatch.chdir(tmp_path)
        tests_dir = tmp_path / "src" / "__tests__"
        tests_dir.mkdir(parents=True, exist_ok=True)
        mock_config = ConvexMockConfig(
            useQuery_default=None,
            useMutation_default="vi.fn()",
        )
        try:
            initialize_setup_file(mock_config)
        except Exception:
            pytest.skip("initialize_setup_file precondition not met")
        content = (tests_dir / "setup.ts").read_text()
        assert "@testing-library/jest-dom" in content, (
            "setup.ts must import @testing-library/jest-dom"
        )


# ---------------------------------------------------------------------------
# SetupFilePath: additional regex boundary checks
# ---------------------------------------------------------------------------

class TestGoodhartSetupFilePath:

    def test_goodhart_rejects_js_extension(self):
        """Only .ts extension is valid; .js must be rejected."""
        pattern = r"^\./src/__tests__/[a-zA-Z0-9_-]+\.ts$"
        assert re.match(pattern, "./src/__tests__/setup.js") is None
        try:
            result = SetupFilePath("./src/__tests__/setup.js")
            # If constructor doesn't raise, check it was rejected
            pytest.fail("SetupFilePath should reject .js extension")
        except Exception:
            pass

    def test_goodhart_rejects_nested_subdirectory(self):
        """Paths with subdirectories under __tests__/ must be rejected."""
        try:
            result = SetupFilePath("./src/__tests__/sub/setup.ts")
            pytest.fail("SetupFilePath should reject nested subdirectory paths")
        except Exception:
            pass

    def test_goodhart_accepts_valid_hyphenated_name(self):
        """A hyphenated filename under __tests__/ should be accepted."""
        try:
            result = SetupFilePath("./src/__tests__/my-setup-file.ts")
            # Should not raise
        except Exception:
            pytest.fail("SetupFilePath should accept hyphenated filenames")

    def test_goodhart_rejects_dot_in_filename(self):
        """Dots in the filename (before .ts) are not in [a-zA-Z0-9_-] and must be rejected."""
        try:
            result = SetupFilePath("./src/__tests__/setup.extra.ts")
            pytest.fail("SetupFilePath should reject dots in filename")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# GlobPattern: additional regex boundary checks
# ---------------------------------------------------------------------------

class TestGoodhartGlobPattern:

    def test_goodhart_rejects_uppercase_brace_group(self):
        """Brace group with uppercase letters must be rejected per [a-z,]+ regex."""
        try:
            result = GlobPattern("src/**/*.test.{TS,TSX}")
            pytest.fail("GlobPattern should reject uppercase extensions in brace group")
        except Exception:
            pass

    def test_goodhart_rejects_empty_brace_group(self):
        """Empty brace group {} is not matched by [a-z,]+ (requires one or more)."""
        try:
            result = GlobPattern("src/**/*.test.{}")
            pytest.fail("GlobPattern should reject empty brace group")
        except Exception:
            pass

    def test_goodhart_accepts_single_extension_brace(self):
        """A brace group with a single extension like {ts} should be accepted."""
        try:
            result = GlobPattern("src/**/*.test.{ts}")
        except Exception:
            pytest.fail("GlobPattern should accept single-extension brace group")


# ---------------------------------------------------------------------------
# ExitCode: mid-range acceptance
# ---------------------------------------------------------------------------

class TestGoodhartExitCode:

    def test_goodhart_accepts_one(self):
        """ExitCode 1 is within [0, 255] and must be accepted."""
        try:
            ec = ExitCode(1)
        except Exception:
            pytest.fail("ExitCode should accept value 1")

    def test_goodhart_accepts_127(self):
        """ExitCode 127 is within [0, 255] and must be accepted."""
        try:
            ec = ExitCode(127)
        except Exception:
            pytest.fail("ExitCode should accept value 127")

    def test_goodhart_rejects_float(self):
        """ExitCode must reject float values even if within range."""
        with pytest.raises(Exception):
            ExitCode(1.5)

    def test_goodhart_rejects_negative_boundary(self):
        """ExitCode -1 (just below 0) must be rejected."""
        with pytest.raises(Exception):
            ExitCode(-1)


# ---------------------------------------------------------------------------
# TestSuiteResult: structural validation
# ---------------------------------------------------------------------------

class TestGoodhartTestSuiteResult:

    def test_goodhart_rejects_failed_nonzero(self):
        """Any nonzero failed count (e.g., 2) must be rejected, not just 1."""
        with pytest.raises(Exception):
            TestSuiteResult(
                exit_code=ExitCode(1),
                total_tests=10,
                passed=8,
                failed=2,
                test_files_count=3,
                duration_ms=1000,
            )

    def test_goodhart_rejects_test_files_count_zero(self):
        """test_files_count=0 must be rejected (validator >=2)."""
        with pytest.raises(Exception):
            TestSuiteResult(
                exit_code=ExitCode(0),
                total_tests=6,
                passed=6,
                failed=0,
                test_files_count=0,
                duration_ms=1000,
            )

    def test_goodhart_accepts_minimum_valid(self):
        """The minimum valid TestSuiteResult per contract constraints must be accepted."""
        try:
            result = TestSuiteResult(
                exit_code=ExitCode(0),
                total_tests=6,
                passed=6,
                failed=0,
                test_files_count=2,
                duration_ms=500,
            )
        except Exception:
            pytest.fail("Minimum valid TestSuiteResult should be accepted")
