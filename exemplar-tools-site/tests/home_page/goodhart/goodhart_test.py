"""
Hidden adversarial acceptance tests for the Home Page component.

These tests target gaps in the visible test suite to catch implementations
that hardcode returns or take shortcuts based on visible test inputs.
"""
import copy
import pytest

from home_page import (
    toQuickStartRow,
    toDiagramNode,
    ToolName,
    ToolDescription,
    StepNumber,
    ToolSlug,
    HexColor,
    ClosedLoopDiagramProps,
    QuickStartTableProps,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tool_def(**overrides):
    """Create a minimal valid ToolDef dict with sensible defaults, applying overrides."""
    base = {
        "slug": "constrain",
        "name": "Constrain",
        "description": "Define project boundaries",
        "step": 1,
        "version": "1.0.0",
        "accentColor": "#00e5ff",
        "videoUrl": None,
        "instructions": [],
    }
    base.update(overrides)
    return base


def _make_diagram_node(**overrides):
    """Create a minimal valid DiagramNode dict."""
    base = {
        "slug": "constrain",
        "name": "Constrain",
        "step": 1,
        "accentColor": "#00e5ff",
    }
    base.update(overrides)
    return base


def _make_quick_start_row(**overrides):
    """Create a minimal valid QuickStartRow dict."""
    base = {
        "step": 1,
        "slug": "constrain",
        "name": "Constrain",
        "description": "Define project boundaries",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# toQuickStartRow tests
# ---------------------------------------------------------------------------

class TestGoodhartToQuickStartRow:

    def test_goodhart_unfamiliar_tooldef_values(self):
        """toQuickStartRow must project arbitrary ToolDef fields correctly, not just recognize known tool slugs — verifies the function is a generic projection, not a lookup table keyed on slug."""
        tool = _make_tool_def(slug="arbiter", name="Arbiter-X", description="Synthetic test desc", step=5)
        result = toQuickStartRow(tool)
        assert result["step"] == 5
        assert result["slug"] == "arbiter"
        assert result["name"] == "Arbiter-X"
        assert result["description"] == "Synthetic test desc"

    def test_goodhart_description_special_chars_passthrough(self):
        """toQuickStartRow must faithfully pass through the description field verbatim, including special characters."""
        desc = 'Desc with <html> & "quotes" + unicode: café'
        tool = _make_tool_def(description=desc)
        result = toQuickStartRow(tool)
        assert result["description"] == desc

    def test_goodhart_name_whitespace_preserved(self):
        """toQuickStartRow must pass through the name field exactly, detecting implementations that normalize or transform the name."""
        tool = _make_tool_def(name=" Leading Spaces ")
        result = toQuickStartRow(tool)
        assert result["name"] == " Leading Spaces "

    def test_goodhart_excludes_non_projected_fields(self):
        """toQuickStartRow must exclude all ToolDef fields not in {step, slug, name, description}."""
        tool = _make_tool_def(
            version="2.0.0",
            accentColor="#ff00ff",
            videoUrl="https://youtube.com/x",
            instructions=[{"title": "t", "bash": "b"}],
        )
        result = toQuickStartRow(tool)
        assert "version" not in result
        assert "accentColor" not in result
        assert "videoUrl" not in result
        assert "instructions" not in result
        assert set(result.keys()) == {"step", "slug", "name", "description"}

    def test_goodhart_empty_dict_raises(self):
        """toQuickStartRow must raise invalid_tool_def for an empty dict with no required fields."""
        with pytest.raises(Exception):
            toQuickStartRow({})

    def test_goodhart_missing_name_only_raises(self):
        """toQuickStartRow must validate each required field individually — missing only 'name' must fail."""
        tool = {"step": 1, "slug": "constrain", "description": "valid"}
        with pytest.raises(Exception):
            toQuickStartRow(tool)

    def test_goodhart_missing_step_only_raises(self):
        """toQuickStartRow must validate presence of step field — missing only 'step' must fail."""
        tool = {"slug": "constrain", "name": "Constrain", "description": "valid"}
        with pytest.raises(Exception):
            toQuickStartRow(tool)

    def test_goodhart_step_boundary_1(self):
        """toQuickStartRow must correctly handle step=1 (minimum boundary)."""
        tool = _make_tool_def(step=1)
        result = toQuickStartRow(tool)
        assert result["step"] == 1

    def test_goodhart_step_boundary_11(self):
        """toQuickStartRow must correctly handle step=11 (maximum boundary)."""
        tool = _make_tool_def(step=11, slug="kindex", name="Kindex")
        result = toQuickStartRow(tool)
        assert result["step"] == 11

    def test_goodhart_does_not_mutate_input(self):
        """toQuickStartRow must not mutate the input ToolDef object — pure function invariant."""
        tool = _make_tool_def()
        original = copy.deepcopy(tool)
        toQuickStartRow(tool)
        assert tool == original

    def test_goodhart_different_inputs_different_outputs(self):
        """toQuickStartRow must produce different outputs for different inputs — detects hardcoded single return value."""
        tool1 = _make_tool_def(slug="constrain", name="Constrain", step=1, description="Desc A")
        tool2 = _make_tool_def(slug="kindex", name="Kindex", step=11, description="Desc B")
        result1 = toQuickStartRow(tool1)
        result2 = toQuickStartRow(tool2)
        assert result1 != result2
        assert result1["slug"] != result2["slug"]
        assert result1["step"] != result2["step"]

    def test_goodhart_none_description_raises(self):
        """toQuickStartRow must raise invalid_tool_def when description field is None rather than a string."""
        tool = _make_tool_def(description=None)
        with pytest.raises(Exception):
            toQuickStartRow(tool)

    def test_goodhart_returns_new_object(self):
        """toQuickStartRow must return a new object — modifying the result must not affect the input."""
        tool = _make_tool_def()
        result = toQuickStartRow(tool)
        result["name"] = "MUTATED"
        assert tool["name"] != "MUTATED"


# ---------------------------------------------------------------------------
# toDiagramNode tests
# ---------------------------------------------------------------------------

class TestGoodhartToDiagramNode:

    def test_goodhart_unfamiliar_values(self):
        """toDiagramNode must be a generic projection, not hardcoded per tool."""
        tool = _make_tool_def(slug="sentinel", name="Sentinel-Altered", step=7, accentColor="#abcdef")
        result = toDiagramNode(tool)
        assert result["slug"] == "sentinel"
        assert result["name"] == "Sentinel-Altered"
        assert result["step"] == 7
        assert result["accentColor"] == "#abcdef"

    def test_goodhart_excludes_description_and_others(self):
        """toDiagramNode must exclude description, version, videoUrl, instructions."""
        tool = _make_tool_def(description="should not appear")
        result = toDiagramNode(tool)
        assert "description" not in result
        assert "version" not in result
        assert "videoUrl" not in result
        assert "instructions" not in result
        assert set(result.keys()) == {"slug", "name", "step", "accentColor"}

    def test_goodhart_missing_slug_raises(self):
        """toDiagramNode must validate slug presence — missing slug must raise invalid_tool_def."""
        tool = {"name": "Test", "step": 3, "accentColor": "#ffffff"}
        with pytest.raises(Exception):
            toDiagramNode(tool)

    def test_goodhart_missing_name_raises(self):
        """toDiagramNode must validate name presence — missing name must raise invalid_tool_def."""
        tool = {"slug": "pact", "step": 3, "accentColor": "#ffffff"}
        with pytest.raises(Exception):
            toDiagramNode(tool)

    def test_goodhart_missing_step_raises(self):
        """toDiagramNode must validate step presence — missing step must raise invalid_tool_def."""
        tool = {"slug": "pact", "name": "Pact", "accentColor": "#ffffff"}
        with pytest.raises(Exception):
            toDiagramNode(tool)

    def test_goodhart_accent_color_case_preserved(self):
        """toDiagramNode must preserve the exact casing of accentColor hex string."""
        tool = _make_tool_def(accentColor="#AaBbCc")
        result = toDiagramNode(tool)
        assert result["accentColor"] == "#AaBbCc"

    def test_goodhart_does_not_mutate_input(self):
        """toDiagramNode must not mutate the input ToolDef object — pure function invariant."""
        tool = _make_tool_def()
        original = copy.deepcopy(tool)
        toDiagramNode(tool)
        assert tool == original

    def test_goodhart_different_inputs_different_outputs(self):
        """toDiagramNode must produce different outputs for different inputs — detects hardcoded single return value."""
        tool1 = _make_tool_def(slug="constrain", name="Constrain", step=1, accentColor="#000000")
        tool2 = _make_tool_def(slug="kindex", name="Kindex", step=11, accentColor="#ffffff")
        result1 = toDiagramNode(tool1)
        result2 = toDiagramNode(tool2)
        assert result1 != result2


# ---------------------------------------------------------------------------
# HexColor tests
# ---------------------------------------------------------------------------

class TestGoodhartHexColor:

    def test_goodhart_uppercase_accepted(self):
        """HexColor must accept uppercase hex digits since CSS hex colors are case-insensitive."""
        # Should not raise
        HexColor("#FF00AA")

    def test_goodhart_no_hash_rejected(self):
        """HexColor must reject hex-like strings without the leading '#' character."""
        with pytest.raises(Exception):
            HexColor("00e5ff")

    def test_goodhart_extra_digits_rejected(self):
        """HexColor must reject strings with too many hex digits (8-digit RGBA)."""
        with pytest.raises(Exception):
            HexColor("#00e5ff00")

    def test_goodhart_empty_string_rejected(self):
        """HexColor must reject empty string."""
        with pytest.raises(Exception):
            HexColor("")

    def test_goodhart_spaces_rejected(self):
        """HexColor must reject hex strings with embedded spaces."""
        with pytest.raises(Exception):
            HexColor("# 00e5ff")


# ---------------------------------------------------------------------------
# StepNumber tests
# ---------------------------------------------------------------------------

class TestGoodhartStepNumber:

    def test_goodhart_float_rejected(self):
        """StepNumber must be an integer — floating point values within range should be rejected."""
        with pytest.raises(Exception):
            StepNumber(1.5)

    def test_goodhart_12_rejected(self):
        """StepNumber must reject 12, the value immediately above the valid range boundary."""
        with pytest.raises(Exception):
            StepNumber(12)


# ---------------------------------------------------------------------------
# ToolSlug tests
# ---------------------------------------------------------------------------

class TestGoodhartToolSlug:

    def test_goodhart_invalid_string_rejected(self):
        """ToolSlug must reject arbitrary strings not in the enum."""
        with pytest.raises(Exception):
            ToolSlug("nonexistent_tool")

    def test_goodhart_case_sensitive(self):
        """ToolSlug must be case-sensitive — 'Constrain' must be rejected."""
        with pytest.raises(Exception):
            ToolSlug("Constrain")


# ---------------------------------------------------------------------------
# ToolDescription boundary tests
# ---------------------------------------------------------------------------

class TestGoodhartToolDescription:

    def test_goodhart_boundary_256_accepted(self):
        """ToolDescription must accept a string of exactly 256 characters (boundary maximum)."""
        ToolDescription("x" * 256)

    def test_goodhart_boundary_257_rejected(self):
        """ToolDescription must reject a string of exactly 257 characters (one past boundary)."""
        with pytest.raises(Exception):
            ToolDescription("x" * 257)

    def test_goodhart_single_char_accepted(self):
        """ToolDescription must accept a single character string (boundary len=1)."""
        ToolDescription("x")


# ---------------------------------------------------------------------------
# ToolName boundary tests
# ---------------------------------------------------------------------------

class TestGoodhartToolName:

    def test_goodhart_boundary_101_rejected(self):
        """ToolName must reject a string of exactly 101 characters (one past boundary)."""
        with pytest.raises(Exception):
            ToolName("x" * 101)


# ---------------------------------------------------------------------------
# Props validation tests
# ---------------------------------------------------------------------------

class TestGoodhartPropsValidation:

    def test_goodhart_quick_start_table_props_multiple_rows(self):
        """QuickStartTableProps must accept lists with more than 1 row."""
        rows = [_make_quick_start_row(step=i) for i in range(1, 6)]
        QuickStartTableProps(rows=rows)

    def test_goodhart_closed_loop_diagram_props_11_nodes(self):
        """ClosedLoopDiagramProps must accept a list of exactly 11 nodes — the production cardinality."""
        nodes = [_make_diagram_node(step=i, slug=f"tool{i}") for i in range(1, 12)]
        ClosedLoopDiagramProps(nodes=nodes)

    def test_goodhart_closed_loop_diagram_props_boundary_2(self):
        """ClosedLoopDiagramProps must accept exactly 2 nodes — the minimum valid count."""
        nodes = [
            _make_diagram_node(step=1, slug="constrain"),
            _make_diagram_node(step=2, slug="ledger"),
        ]
        ClosedLoopDiagramProps(nodes=nodes)
