"""
Contract test suite for home_page component.

Tests cover:
- Tier 1: Pure projection functions (toQuickStartRow, toDiagramNode, toQuickStartRows, toDiagramNodes)
- Tier 1: Circular layout computation (computeNodePosition)
- Invariants: purity, ordering, count, coordinate bounds

Execution: pytest contract_test.py -v
"""
import math
import pytest
from unittest.mock import MagicMock, patch
from copy import deepcopy

# ---------------------------------------------------------------------------
# Import the component module
# ---------------------------------------------------------------------------
from home_page import (
    toQuickStartRow,
    toDiagramNode,
    toQuickStartRows,
    toDiagramNodes,
    computeNodePosition,
)

# Try importing canonical types if available; tests will work with dicts too
try:
    from home_page import (
        ToolDef,
        ToolSlug,
        StepNumber,
        HexColor,
        QuickStartRow,
        DiagramNode,
        CircularLayoutPoint,
    )
    HAS_TYPES = True
except ImportError:
    HAS_TYPES = False


# ---------------------------------------------------------------------------
# Canonical slug/step/color data matching the 11-tool contract
# ---------------------------------------------------------------------------
TOOL_SPECS = [
    {"slug": "constrain",   "step": 1,  "name": "Constrain",   "accentColor": "#00e5ff", "description": "Constrain desc"},
    {"slug": "ledger",      "step": 2,  "name": "Ledger",      "accentColor": "#76ff03", "description": "Ledger desc"},
    {"slug": "pact",        "step": 3,  "name": "Pact",        "accentColor": "#ffea00", "description": "Pact desc"},
    {"slug": "advocate",    "step": 4,  "name": "Advocate",    "accentColor": "#ff6d00", "description": "Advocate desc"},
    {"slug": "arbiter",     "step": 5,  "name": "Arbiter",     "accentColor": "#d500f9", "description": "Arbiter desc"},
    {"slug": "baton",       "step": 6,  "name": "Baton",       "accentColor": "#00b0ff", "description": "Baton desc"},
    {"slug": "sentinel",    "step": 7,  "name": "Sentinel",    "accentColor": "#1de9b6", "description": "Sentinel desc"},
    {"slug": "chronicler",  "step": 8,  "name": "Chronicler",  "accentColor": "#f50057", "description": "Chronicler desc"},
    {"slug": "stigmergy",   "step": 9,  "name": "Stigmergy",   "accentColor": "#651fff", "description": "Stigmergy desc"},
    {"slug": "apprentice",  "step": 10, "name": "Apprentice",  "accentColor": "#ff9100", "description": "Apprentice desc"},
    {"slug": "kindex",      "step": 11, "name": "Kindex",      "accentColor": "#00e676", "description": "Kindex desc"},
]


def _make_tool_def(overrides=None, **kwargs):
    """Factory for a single ToolDef-like dict with sensible defaults."""
    base = {
        "slug": "constrain",
        "name": "Constrain",
        "description": "Constrain description",
        "step": 1,
        "version": "1.0.0",
        "accentColor": "#00e5ff",
        "videoUrl": "https://youtube.com/embed/abc",
        "instructions": [{"title": "Install", "bash": "npm install"}],
    }
    if overrides:
        base.update(overrides)
    base.update(kwargs)
    # If the module exposes a ToolDef constructor, try to use it
    if HAS_TYPES:
        try:
            return ToolDef(**base)
        except Exception:
            pass
    return base


def _make_tool_def_from_spec(spec):
    """Create a ToolDef from one of the TOOL_SPECS entries."""
    return _make_tool_def(
        slug=spec["slug"],
        step=spec["step"],
        name=spec["name"],
        description=spec["description"],
        accentColor=spec["accentColor"],
    )


def _make_all_tool_defs():
    """Create the canonical sorted list of 11 ToolDefs."""
    return [_make_tool_def_from_spec(s) for s in TOOL_SPECS]


def _get(obj, key):
    """Attribute or dict access helper."""
    if isinstance(obj, dict):
        return obj[key]
    return getattr(obj, key)


# ===========================================================================
# Tier 1: toQuickStartRow
# ===========================================================================

class TestToQuickStartRow:
    """Tests for toQuickStartRow pure projection function."""

    def test_happy_path_all_fields_projected(self):
        """toQuickStartRow returns QuickStartRow with all fields from valid ToolDef."""
        tool = _make_tool_def(step=1, slug="constrain", name="Constrain",
                              description="Constrain desc", accentColor="#00e5ff")
        result = toQuickStartRow(tool)
        assert _get(result, "step") == 1
        assert _get(result, "slug") == "constrain"
        assert _get(result, "name") == "Constrain"
        assert _get(result, "description") == "Constrain desc"
        assert _get(result, "accentColor") == "#00e5ff"

    def test_happy_path_all_11_slugs(self):
        """toQuickStartRow works for each of the 11 canonical ToolSlug values."""
        for spec in TOOL_SPECS:
            tool = _make_tool_def_from_spec(spec)
            result = toQuickStartRow(tool)
            assert _get(result, "step") == spec["step"]
            assert _get(result, "slug") == spec["slug"]
            assert _get(result, "name") == spec["name"]
            assert _get(result, "description") == spec["description"]
            assert _get(result, "accentColor") == spec["accentColor"]

    def test_error_null_tool(self):
        """toQuickStartRow raises on None input (invalid_tool_def)."""
        with pytest.raises(Exception) as exc_info:
            toQuickStartRow(None)
        assert "invalid_tool_def" in str(exc_info.value).lower() or exc_info.type is not None

    def test_error_missing_required_field_name(self):
        """toQuickStartRow raises when 'name' field is missing."""
        tool = _make_tool_def()
        # Remove the name field
        if isinstance(tool, dict):
            del tool["name"]
        else:
            # For dataclass-like objects, set to None or remove
            try:
                delattr(tool, "name")
            except Exception:
                tool = {k: v for k, v in vars(tool).items() if k != "name"}
        with pytest.raises(Exception):
            toQuickStartRow(tool)

    def test_error_missing_required_field_step(self):
        """toQuickStartRow raises when 'step' field is missing."""
        tool = _make_tool_def()
        if isinstance(tool, dict):
            del tool["step"]
        else:
            try:
                delattr(tool, "step")
            except Exception:
                tool = {k: v for k, v in vars(tool).items() if k != "step"}
        with pytest.raises(Exception):
            toQuickStartRow(tool)

    def test_edge_step_lower_boundary(self):
        """toQuickStartRow accepts step=1 (lower boundary)."""
        tool = _make_tool_def(step=1)
        result = toQuickStartRow(tool)
        assert _get(result, "step") == 1

    def test_edge_step_upper_boundary(self):
        """toQuickStartRow accepts step=11 (upper boundary)."""
        tool = _make_tool_def(step=11, slug="kindex", name="Kindex",
                              description="Kindex desc", accentColor="#00e676")
        result = toQuickStartRow(tool)
        assert _get(result, "step") == 11

    def test_edge_hex_color_uppercase(self):
        """toQuickStartRow accepts uppercase hex color."""
        tool = _make_tool_def(accentColor="#00E5FF")
        result = toQuickStartRow(tool)
        assert _get(result, "accentColor") == "#00E5FF"

    def test_edge_hex_color_lowercase(self):
        """toQuickStartRow accepts lowercase hex color."""
        tool = _make_tool_def(accentColor="#00e5ff")
        result = toQuickStartRow(tool)
        assert _get(result, "accentColor") == "#00e5ff"

    def test_invariant_purity(self):
        """toQuickStartRow is pure: identical inputs produce identical outputs."""
        tool = _make_tool_def(step=3, slug="pact", name="Pact",
                              description="Pact desc", accentColor="#ffea00")
        result_a = toQuickStartRow(tool)
        result_b = toQuickStartRow(tool)
        for field in ("step", "slug", "name", "description", "accentColor"):
            assert _get(result_a, field) == _get(result_b, field)


# ===========================================================================
# Tier 1: toDiagramNode
# ===========================================================================

class TestToDiagramNode:
    """Tests for toDiagramNode pure projection function."""

    def test_happy_path_all_fields_projected(self):
        """toDiagramNode returns DiagramNode with slug, name, step, accentColor."""
        tool = _make_tool_def(step=5, slug="arbiter", name="Arbiter",
                              description="Arbiter desc", accentColor="#d500f9")
        result = toDiagramNode(tool)
        assert _get(result, "slug") == "arbiter"
        assert _get(result, "name") == "Arbiter"
        assert _get(result, "step") == 5
        assert _get(result, "accentColor") == "#d500f9"

    def test_error_null_tool(self):
        """toDiagramNode raises on None input (invalid_tool_def)."""
        with pytest.raises(Exception):
            toDiagramNode(None)

    def test_error_missing_required_field_slug(self):
        """toDiagramNode raises when 'slug' field is missing."""
        tool = _make_tool_def()
        if isinstance(tool, dict):
            del tool["slug"]
        else:
            try:
                delattr(tool, "slug")
            except Exception:
                tool = {k: v for k, v in vars(tool).items() if k != "slug"}
        with pytest.raises(Exception):
            toDiagramNode(tool)

    def test_error_missing_required_field_accentColor(self):
        """toDiagramNode raises when 'accentColor' field is missing."""
        tool = _make_tool_def()
        if isinstance(tool, dict):
            del tool["accentColor"]
        else:
            try:
                delattr(tool, "accentColor")
            except Exception:
                tool = {k: v for k, v in vars(tool).items() if k != "accentColor"}
        with pytest.raises(Exception):
            toDiagramNode(tool)

    def test_invariant_purity(self):
        """toDiagramNode is pure: identical inputs produce identical outputs."""
        tool = _make_tool_def(step=7, slug="sentinel", name="Sentinel",
                              description="Sentinel desc", accentColor="#1de9b6")
        result_a = toDiagramNode(tool)
        result_b = toDiagramNode(tool)
        for field in ("slug", "name", "step", "accentColor"):
            assert _get(result_a, field) == _get(result_b, field)


# ===========================================================================
# Tier 1: toQuickStartRows
# ===========================================================================

class TestToQuickStartRows:
    """Tests for toQuickStartRows batch projection function."""

    def test_happy_path_11_tools(self):
        """toQuickStartRows maps 11 sorted ToolDefs to 11 QuickStartRows in order."""
        tools = _make_all_tool_defs()
        result = toQuickStartRows(tools)
        assert len(result) == 11
        for i in range(11):
            assert _get(result[i], "step") == i + 1
            assert _get(result[i], "slug") == TOOL_SPECS[i]["slug"]
            assert _get(result[i], "name") == TOOL_SPECS[i]["name"]
            assert _get(result[i], "description") == TOOL_SPECS[i]["description"]
            assert _get(result[i], "accentColor") == TOOL_SPECS[i]["accentColor"]

    def test_error_none_input(self):
        """toQuickStartRows raises invalid_tool_list when tools is None."""
        with pytest.raises(Exception) as exc_info:
            toQuickStartRows(None)
        # Accept any exception indicating invalid input
        assert exc_info.type is not None

    def test_error_empty_list(self):
        """toQuickStartRows raises invalid_tool_list when tools is empty list."""
        with pytest.raises(Exception):
            toQuickStartRows([])

    def test_error_wrong_length_10(self):
        """toQuickStartRows raises invalid_tool_list when tools has 10 elements."""
        tools = _make_all_tool_defs()[:10]
        with pytest.raises(Exception):
            toQuickStartRows(tools)

    def test_error_wrong_length_12(self):
        """toQuickStartRows raises invalid_tool_list when tools has 12 elements."""
        tools = _make_all_tool_defs()
        tools.append(_make_tool_def(step=12, slug="constrain"))
        with pytest.raises(Exception):
            toQuickStartRows(tools)

    def test_error_unsorted_input(self):
        """toQuickStartRows raises unsorted_input when tools are reversed."""
        tools = list(reversed(_make_all_tool_defs()))
        with pytest.raises(Exception):
            toQuickStartRows(tools)

    def test_error_unsorted_input_swapped_pair(self):
        """toQuickStartRows raises unsorted_input when two adjacent tools are swapped."""
        tools = _make_all_tool_defs()
        tools[3], tools[4] = tools[4], tools[3]  # swap step 4 and 5
        with pytest.raises(Exception):
            toQuickStartRows(tools)

    def test_invariant_purity(self):
        """toQuickStartRows is pure: identical inputs produce identical outputs."""
        tools = _make_all_tool_defs()
        result_a = toQuickStartRows(tools)
        result_b = toQuickStartRows(tools)
        assert len(result_a) == len(result_b)
        for i in range(11):
            for field in ("step", "slug", "name", "description", "accentColor"):
                assert _get(result_a[i], field) == _get(result_b[i], field)

    def test_invariant_exactly_11(self):
        """Output always has exactly 11 entries."""
        tools = _make_all_tool_defs()
        result = toQuickStartRows(tools)
        assert len(result) == 11

    def test_invariant_step_ascending(self):
        """Output is sorted by step ascending 1..11."""
        tools = _make_all_tool_defs()
        result = toQuickStartRows(tools)
        for i in range(11):
            assert _get(result[i], "step") == i + 1


# ===========================================================================
# Tier 1: toDiagramNodes
# ===========================================================================

class TestToDiagramNodes:
    """Tests for toDiagramNodes batch projection function."""

    def test_happy_path_11_tools(self):
        """toDiagramNodes maps 11 sorted ToolDefs to 11 DiagramNodes in order."""
        tools = _make_all_tool_defs()
        result = toDiagramNodes(tools)
        assert len(result) == 11
        for i in range(11):
            assert _get(result[i], "step") == i + 1
            assert _get(result[i], "slug") == TOOL_SPECS[i]["slug"]
            assert _get(result[i], "name") == TOOL_SPECS[i]["name"]
            assert _get(result[i], "accentColor") == TOOL_SPECS[i]["accentColor"]

    def test_error_none_input(self):
        """toDiagramNodes raises invalid_tool_list when tools is None."""
        with pytest.raises(Exception):
            toDiagramNodes(None)

    def test_error_empty_list(self):
        """toDiagramNodes raises invalid_tool_list when tools is empty list."""
        with pytest.raises(Exception):
            toDiagramNodes([])

    def test_error_wrong_length(self):
        """toDiagramNodes raises invalid_tool_list when tools has 5 elements."""
        tools = _make_all_tool_defs()[:5]
        with pytest.raises(Exception):
            toDiagramNodes(tools)

    def test_error_unsorted_input(self):
        """toDiagramNodes raises unsorted_input when tools order is shuffled."""
        tools = _make_all_tool_defs()
        # Shuffle: move last to front
        tools = [tools[-1]] + tools[:-1]
        with pytest.raises(Exception):
            toDiagramNodes(tools)

    def test_invariant_purity(self):
        """toDiagramNodes is pure: identical inputs produce identical outputs."""
        tools = _make_all_tool_defs()
        result_a = toDiagramNodes(tools)
        result_b = toDiagramNodes(tools)
        assert len(result_a) == len(result_b)
        for i in range(11):
            for field in ("step", "slug", "name", "accentColor"):
                assert _get(result_a[i], field) == _get(result_b[i], field)


# ===========================================================================
# Tier 1: computeNodePosition
# ===========================================================================

class TestComputeNodePosition:
    """Tests for computeNodePosition trigonometric layout function."""

    # --- Happy path: known positions ---

    def test_step1_of_11_top_center(self):
        """step=1 of 11 at center=(250,250) radius=200 yields top-center (~250, 50)."""
        result = computeNodePosition(1, 11, 250.0, 250.0, 200.0)
        x, y = _get(result, "x"), _get(result, "y")
        assert x == pytest.approx(250.0, abs=0.01)
        assert y == pytest.approx(50.0, abs=0.01)

    def test_step1_of_4_top(self):
        """step=1 of 4 at center=(250,250) radius=100 yields (250, 150) — top."""
        result = computeNodePosition(1, 4, 250.0, 250.0, 100.0)
        x, y = _get(result, "x"), _get(result, "y")
        assert x == pytest.approx(250.0, abs=0.01)
        assert y == pytest.approx(150.0, abs=0.01)

    def test_step2_of_4_right(self):
        """step=2 of 4 at center=(250,250) radius=100 yields (350, 250) — right."""
        result = computeNodePosition(2, 4, 250.0, 250.0, 100.0)
        x, y = _get(result, "x"), _get(result, "y")
        assert x == pytest.approx(350.0, abs=0.01)
        assert y == pytest.approx(250.0, abs=0.01)

    def test_step3_of_4_bottom(self):
        """step=3 of 4 at center=(250,250) radius=100 yields (250, 350) — bottom."""
        result = computeNodePosition(3, 4, 250.0, 250.0, 100.0)
        x, y = _get(result, "x"), _get(result, "y")
        assert x == pytest.approx(250.0, abs=0.01)
        assert y == pytest.approx(350.0, abs=0.01)

    def test_step4_of_4_left(self):
        """step=4 of 4 at center=(250,250) radius=100 yields (150, 250) — left."""
        result = computeNodePosition(4, 4, 250.0, 250.0, 100.0)
        x, y = _get(result, "x"), _get(result, "y")
        assert x == pytest.approx(150.0, abs=0.01)
        assert y == pytest.approx(250.0, abs=0.01)

    # --- Edge case: single node ---

    def test_single_node(self):
        """step=1, totalNodes=1 yields top of circle."""
        result = computeNodePosition(1, 1, 250.0, 250.0, 100.0)
        x, y = _get(result, "x"), _get(result, "y")
        # angle = (0/1)*2pi - pi/2 = -pi/2 => cos(-pi/2)=0, sin(-pi/2)=-1
        assert x == pytest.approx(250.0, abs=0.01)
        assert y == pytest.approx(150.0, abs=0.01)

    # --- Edge case: step equals totalNodes (last position) ---

    def test_step_equals_total(self):
        """step=totalNodes is a valid position (last node before closing loop)."""
        result = computeNodePosition(11, 11, 250.0, 250.0, 200.0)
        x, y = _get(result, "x"), _get(result, "y")
        # Verify it's a valid point on the circle
        dx = x - 250.0
        dy = y - 250.0
        dist = math.sqrt(dx * dx + dy * dy)
        assert dist == pytest.approx(200.0, abs=0.01)

    # --- Invariant: all points within bounds ---

    def test_all_11_within_bounds(self):
        """All 11 positions lie within [centerX-radius, centerX+radius] and same for y."""
        for step in range(1, 12):
            result = computeNodePosition(step, 11, 250.0, 250.0, 200.0)
            x, y = _get(result, "x"), _get(result, "y")
            assert 50.0 - 0.01 <= x <= 450.0 + 0.01, f"x={x} out of bounds for step={step}"
            assert 50.0 - 0.01 <= y <= 450.0 + 0.01, f"y={y} out of bounds for step={step}"

    # --- Invariant: all points distinct ---

    def test_all_11_positions_distinct(self):
        """All 11 computed positions are distinct."""
        points = []
        for step in range(1, 12):
            result = computeNodePosition(step, 11, 250.0, 250.0, 200.0)
            x, y = _get(result, "x"), _get(result, "y")
            points.append((round(x, 4), round(y, 4)))
        assert len(set(points)) == 11

    # --- Invariant: all points lie on the circle ---

    def test_all_11_on_circle(self):
        """All 11 positions are at distance=radius from center."""
        for step in range(1, 12):
            result = computeNodePosition(step, 11, 250.0, 250.0, 200.0)
            x, y = _get(result, "x"), _get(result, "y")
            dist = math.sqrt((x - 250.0) ** 2 + (y - 250.0) ** 2)
            assert dist == pytest.approx(200.0, abs=0.01), f"step={step} not on circle"

    # --- Invariant: CircularLayoutPoint x,y within 0..500 for default viewBox ---

    def test_circularLayoutPoint_x_range(self):
        """x values within [0.0, 500.0] for center=250, radius=200."""
        for step in range(1, 12):
            result = computeNodePosition(step, 11, 250.0, 250.0, 200.0)
            x = _get(result, "x")
            assert 0.0 <= x <= 500.0

    def test_circularLayoutPoint_y_range(self):
        """y values within [0.0, 500.0] for center=250, radius=200."""
        for step in range(1, 12):
            result = computeNodePosition(step, 11, 250.0, 250.0, 200.0)
            y = _get(result, "y")
            assert 0.0 <= y <= 500.0

    # --- Error cases ---

    def test_error_step_zero(self):
        """computeNodePosition raises step_out_of_range when step=0."""
        with pytest.raises(Exception):
            computeNodePosition(0, 11, 250.0, 250.0, 200.0)

    def test_error_step_exceeds_total(self):
        """computeNodePosition raises step_out_of_range when step > totalNodes."""
        with pytest.raises(Exception):
            computeNodePosition(12, 11, 250.0, 250.0, 200.0)

    def test_error_negative_step(self):
        """computeNodePosition raises step_out_of_range when step < 0."""
        with pytest.raises(Exception):
            computeNodePosition(-1, 11, 250.0, 250.0, 200.0)

    def test_error_zero_radius(self):
        """computeNodePosition raises invalid_radius when radius=0."""
        with pytest.raises(Exception):
            computeNodePosition(1, 11, 250.0, 250.0, 0.0)

    def test_error_negative_radius(self):
        """computeNodePosition raises invalid_radius when radius < 0."""
        with pytest.raises(Exception):
            computeNodePosition(1, 11, 250.0, 250.0, -50.0)

    # --- Verify the trigonometric formula directly ---

    def test_formula_step6_of_11(self):
        """Verify manual formula computation for step=6 of 11."""
        step = 6
        total = 11
        cx, cy, r = 250.0, 250.0, 200.0
        angle = ((step - 1) / total) * 2 * math.pi - math.pi / 2
        expected_x = cx + r * math.cos(angle)
        expected_y = cy + r * math.sin(angle)

        result = computeNodePosition(step, total, cx, cy, r)
        assert _get(result, "x") == pytest.approx(expected_x, abs=0.01)
        assert _get(result, "y") == pytest.approx(expected_y, abs=0.01)

    def test_formula_all_steps(self):
        """Verify trigonometric formula for all 11 steps."""
        cx, cy, r, total = 250.0, 250.0, 200.0, 11
        for step in range(1, 12):
            angle = ((step - 1) / total) * 2 * math.pi - math.pi / 2
            expected_x = cx + r * math.cos(angle)
            expected_y = cy + r * math.sin(angle)
            result = computeNodePosition(step, total, cx, cy, r)
            assert _get(result, "x") == pytest.approx(expected_x, abs=0.001)
            assert _get(result, "y") == pytest.approx(expected_y, abs=0.001)


# ===========================================================================
# Tier 3: Integration — full pipeline without mocking intermediary functions
# ===========================================================================

class TestIntegrationPipeline:
    """Integration tests composing projection functions end-to-end."""

    def test_full_pipeline_quick_start(self):
        """toQuickStartRows produces valid output from canonical tool list."""
        tools = _make_all_tool_defs()
        rows = toQuickStartRows(tools)
        assert len(rows) == 11
        # Verify step ordering
        steps = [_get(r, "step") for r in rows]
        assert steps == list(range(1, 12))
        # Verify slugs match
        slugs = [_get(r, "slug") for r in rows]
        expected_slugs = [s["slug"] for s in TOOL_SPECS]
        assert slugs == expected_slugs

    def test_full_pipeline_diagram_nodes(self):
        """toDiagramNodes produces valid output from canonical tool list."""
        tools = _make_all_tool_defs()
        nodes = toDiagramNodes(tools)
        assert len(nodes) == 11
        steps = [_get(n, "step") for n in nodes]
        assert steps == list(range(1, 12))
        slugs = [_get(n, "slug") for n in nodes]
        expected_slugs = [s["slug"] for s in TOOL_SPECS]
        assert slugs == expected_slugs

    def test_pipeline_consistency(self):
        """QuickStartRows and DiagramNodes from same input share step and slug values."""
        tools = _make_all_tool_defs()
        rows = toQuickStartRows(tools)
        nodes = toDiagramNodes(tools)
        for i in range(11):
            assert _get(rows[i], "step") == _get(nodes[i], "step")
            assert _get(rows[i], "slug") == _get(nodes[i], "slug")
            assert _get(rows[i], "accentColor") == _get(nodes[i], "accentColor")
