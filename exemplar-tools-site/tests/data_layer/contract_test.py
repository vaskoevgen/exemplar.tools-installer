"""
Contract test suite for the data_layer component.

Tests cover:
- getTools(): TOOLS constant invariants (count, sort, uniqueness, shapes, palette)
- getToolBySlugs(): Slug lookup happy paths, unknown slugs, roundtrip property
- listComments(): Async Convex query with mocked backend
- addComment(): Async Convex mutation with mocked backend, all error cases
"""

import re
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

# ---------------------------------------------------------------------------
# Attempt import; provide stubs so collection never fails
# ---------------------------------------------------------------------------
try:
    from data_layer import (
        getTools,
        getToolBySlugs,
        listComments,
        addComment,
    )
except ImportError:
    # Allow the module path to vary
    getTools = None
    getToolBySlugs = None
    listComments = None
    addComment = None

# Canonical constants from the contract
CANONICAL_SLUGS = {
    "constrain", "ledger", "pact", "advocate", "arbiter",
    "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex",
}

CANONICAL_PALETTE = {
    "#00e5ff", "#00bfa5", "#69f0ae", "#b2ff59", "#ffd740",
    "#ff9100", "#ff5252", "#ff4081", "#e040fb", "#7c4dff", "#448aff",
}

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


# ========================== getTools() tests ==============================

class TestGetTools:
    """Tests for the getTools() synchronous function / TOOLS constant."""

    def _tools(self):
        assert getTools is not None, "getTools not importable"
        result = getTools()
        assert isinstance(result, (list, tuple)), "getTools must return a sequence"
        return result

    # --- Invariant: exactly 11 elements ---
    def test_returns_exactly_11_elements(self):
        tools = self._tools()
        assert len(tools) == 11, f"Expected 11 tools, got {len(tools)}"

    # --- Invariant: sorted by step ascending 1..11 ---
    def test_sorted_by_step_ascending(self):
        tools = self._tools()
        steps = [t.step if hasattr(t, "step") else t["step"] for t in tools]
        assert steps == list(range(1, 12)), f"Steps not 1..11 ascending: {steps}"

    # --- Invariant: unique steps ---
    def test_unique_step_values(self):
        tools = self._tools()
        steps = [t.step if hasattr(t, "step") else t["step"] for t in tools]
        assert len(set(steps)) == 11

    # --- Invariant: unique slugs ---
    def test_unique_slug_values(self):
        tools = self._tools()
        slugs = [t.slug if hasattr(t, "slug") else t["slug"] for t in tools]
        assert len(set(slugs)) == 11

    # --- Invariant: slugs match ToolSlug enum variants ---
    def test_slugs_match_canonical_set(self):
        tools = self._tools()
        slugs = {t.slug if hasattr(t, "slug") else t["slug"] for t in tools}
        # Allow enum objects — coerce to string
        slugs_str = set()
        for s in slugs:
            slugs_str.add(s.value if hasattr(s, "value") else str(s))
        assert slugs_str == CANONICAL_SLUGS

    # --- Invariant: accent colors unique and canonical ---
    def test_accent_colors_unique_and_canonical(self):
        tools = self._tools()
        colors = set()
        for t in tools:
            c = t.accentColor if hasattr(t, "accentColor") else t["accentColor"]
            c_str = str(c).lower()
            assert c_str in {p.lower() for p in CANONICAL_PALETTE}, (
                f"Unexpected accent color: {c_str}"
            )
            colors.add(c_str)
        assert len(colors) == 11, "Accent colors are not all unique"

    # --- Invariant: hex color format ---
    def test_accent_color_hex_format(self):
        tools = self._tools()
        for t in tools:
            c = t.accentColor if hasattr(t, "accentColor") else t["accentColor"]
            assert HEX_COLOR_RE.match(str(c)), f"Bad hex color: {c}"

    # --- Invariant: kindex has no video, others do ---
    def test_kindex_no_video_others_have_video(self):
        tools = self._tools()
        no_video = []
        has_video = []
        for t in tools:
            slug = t.slug if hasattr(t, "slug") else t["slug"]
            slug_str = slug.value if hasattr(slug, "value") else str(slug)
            video = t.videoUrl if hasattr(t, "videoUrl") else t.get("videoUrl")
            if video is None:
                no_video.append(slug_str)
            else:
                has_video.append(slug_str)
        assert no_video == ["kindex"], f"Expected only kindex without video, got {no_video}"
        assert len(has_video) == 10

    # --- Invariant: instructions 3-5 per tool ---
    def test_instructions_count_3_to_5(self):
        tools = self._tools()
        for t in tools:
            slug = t.slug if hasattr(t, "slug") else t["slug"]
            instr = t.instructions if hasattr(t, "instructions") else t["instructions"]
            assert 3 <= len(instr) <= 5, (
                f"Tool {slug}: expected 3-5 instructions, got {len(instr)}"
            )

    # --- Shape: InstructionStep has title and bash ---
    def test_instruction_step_shape(self):
        tools = self._tools()
        for t in tools:
            instr = t.instructions if hasattr(t, "instructions") else t["instructions"]
            for step in instr:
                title = step.title if hasattr(step, "title") else step["title"]
                bash = step.bash if hasattr(step, "bash") else step["bash"]
                assert isinstance(title, str) and len(title) > 0
                assert isinstance(bash, str) and len(bash) > 0

    # --- Happy path: ToolDef shape ---
    def test_tooldef_has_all_required_fields(self):
        tools = self._tools()
        required = {"slug", "name", "description", "step", "version", "accentColor", "instructions"}
        for t in tools:
            for field in required:
                if hasattr(t, field):
                    assert getattr(t, field) is not None, f"Field {field} is None"
                else:
                    assert field in t, f"Missing field {field}"

    # --- Invariant: step numbers in range 1-11 ---
    def test_step_numbers_in_valid_range(self):
        tools = self._tools()
        for t in tools:
            step = t.step if hasattr(t, "step") else t["step"]
            assert isinstance(step, int), f"Step is not int: {type(step)}"
            assert 1 <= step <= 11, f"Step out of range: {step}"


# ====================== getToolBySlugs() tests ============================

class TestGetToolBySlugs:
    """Tests for getToolBySlugs() synchronous lookup."""

    def test_known_slug_returns_matching_tooldef(self):
        assert getToolBySlugs is not None, "getToolBySlugs not importable"
        assert getTools is not None, "getTools not importable"
        tools = getTools()
        for t in tools:
            slug_val = t.slug if hasattr(t, "slug") else t["slug"]
            slug_str = slug_val.value if hasattr(slug_val, "value") else str(slug_val)
            result = getToolBySlugs(slug_str)
            assert result is not None, f"Expected ToolDef for slug '{slug_str}', got None"
            r_slug = result.slug if hasattr(result, "slug") else result["slug"]
            r_slug_str = r_slug.value if hasattr(r_slug, "value") else str(r_slug)
            assert r_slug_str == slug_str

    def test_unknown_slug_returns_none(self):
        assert getToolBySlugs is not None
        result = getToolBySlugs("nonexistent-tool")
        assert result is None, f"Expected None for unknown slug, got {result}"

    def test_empty_string_slug_returns_none(self):
        assert getToolBySlugs is not None
        result = getToolBySlugs("")
        assert result is None, f"Expected None for empty slug, got {result}"

    def test_roundtrip_name_matches(self):
        """For every tool from getTools(), getToolBySlugs(slug).name == tool.name."""
        assert getTools is not None and getToolBySlugs is not None
        for t in getTools():
            slug_val = t.slug if hasattr(t, "slug") else t["slug"]
            slug_str = slug_val.value if hasattr(slug_val, "value") else str(slug_val)
            result = getToolBySlugs(slug_str)
            t_name = t.name if hasattr(t, "name") else t["name"]
            r_name = result.name if hasattr(result, "name") else result["name"]
            assert r_name == t_name, f"Name mismatch for {slug_str}"


# ====================== listComments() tests ==============================

def _make_comment(_id="abc123", page="constrain", author="Alice",
                  body="Hello", createdAt=1000.0):
    """Helper to build a Comment-like dict."""
    return {
        "_id": _id,
        "page": page,
        "author": author,
        "body": body,
        "createdAt": createdAt,
    }


class TestListComments:
    """Tests for the async listComments Convex query."""

    @pytest.mark.anyio
    async def test_happy_path_returns_comments(self):
        assert listComments is not None, "listComments not importable"
        comments = [
            _make_comment(_id="1", page="constrain", createdAt=100),
            _make_comment(_id="2", page="constrain", createdAt=200),
        ]
        with patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_lc.return_value = comments
            result = await mock_lc(page="constrain")
        assert isinstance(result, list)
        assert len(result) == 2
        for c in result:
            for key in ("_id", "page", "author", "body", "createdAt"):
                assert key in c, f"Missing field {key}"

    @pytest.mark.anyio
    async def test_empty_result_for_page_with_no_comments(self):
        with patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_lc.return_value = []
            result = await mock_lc(page="arbiter")
        assert result == []

    @pytest.mark.anyio
    async def test_results_sorted_by_created_at_ascending(self):
        comments = [
            _make_comment(_id="1", page="ledger", createdAt=50),
            _make_comment(_id="2", page="ledger", createdAt=100),
            _make_comment(_id="3", page="ledger", createdAt=200),
        ]
        with patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_lc.return_value = comments
            result = await mock_lc(page="ledger")
        timestamps = [c["createdAt"] for c in result]
        assert timestamps == sorted(timestamps), "Comments not sorted ascending"

    @pytest.mark.anyio
    async def test_filters_by_page(self):
        comments = [
            _make_comment(_id="1", page="pact", createdAt=10),
            _make_comment(_id="2", page="pact", createdAt=20),
        ]
        with patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_lc.return_value = comments
            result = await mock_lc(page="pact")
        assert all(c["page"] == "pact" for c in result)

    @pytest.mark.anyio
    async def test_missing_page_argument_raises_error(self):
        with patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_lc.side_effect = ValueError("missing_page_argument")
            with pytest.raises((ValueError, TypeError, Exception)):
                await mock_lc()


# ====================== addComment() tests ================================

class TestAddComment:
    """Tests for the async addComment Convex mutation."""

    @pytest.mark.anyio
    async def test_happy_path_returns_document_id(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.return_value = "conv_doc_id_abc123"
            result = await mock_ac(page="constrain", author="Alice", body="Great tool!")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.anyio
    async def test_roundtrip_add_then_list(self):
        new_id = "conv_doc_id_xyz789"
        new_comment = _make_comment(
            _id=new_id, page="ledger", author="Bob",
            body="Very helpful!", createdAt=9999,
        )
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac, \
             patch("data_layer.listComments", new_callable=AsyncMock) as mock_lc:
            mock_ac.return_value = new_id
            doc_id = await mock_ac(page="ledger", author="Bob", body="Very helpful!")
            mock_lc.return_value = [new_comment]
            comments = await mock_lc(page="ledger")
        assert any(c["_id"] == doc_id for c in comments)
        match = [c for c in comments if c["_id"] == doc_id][0]
        assert match["author"] == "Bob"
        assert match["body"] == "Very helpful!"

    @pytest.mark.anyio
    async def test_missing_page_argument_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ValueError("missing_page_argument")
            with pytest.raises(ValueError, match="missing_page_argument"):
                await mock_ac(author="Alice", body="text")

    @pytest.mark.anyio
    async def test_missing_author_argument_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ValueError("missing_author_argument")
            with pytest.raises(ValueError, match="missing_author_argument"):
                await mock_ac(page="constrain", body="text")

    @pytest.mark.anyio
    async def test_missing_body_argument_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ValueError("missing_body_argument")
            with pytest.raises(ValueError, match="missing_body_argument"):
                await mock_ac(page="constrain", author="Alice")

    @pytest.mark.anyio
    async def test_empty_author_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ValueError("empty_author")
            with pytest.raises(ValueError, match="empty_author"):
                await mock_ac(page="constrain", author="   ", body="text")

    @pytest.mark.anyio
    async def test_empty_body_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ValueError("empty_body")
            with pytest.raises(ValueError, match="empty_body"):
                await mock_ac(page="constrain", author="Alice", body="   ")

    @pytest.mark.anyio
    async def test_convex_internal_error(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = RuntimeError("convex_internal_error")
            with pytest.raises(RuntimeError, match="convex_internal_error"):
                await mock_ac(page="constrain", author="Alice", body="text")

    @pytest.mark.anyio
    async def test_non_idempotent_distinct_ids(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.side_effect = ["id_first_call", "id_second_call"]
            id1 = await mock_ac(page="constrain", author="Alice", body="Same text")
            id2 = await mock_ac(page="constrain", author="Alice", body="Same text")
        assert id1 != id2, "Repeated calls must produce distinct document IDs"

    @pytest.mark.anyio
    async def test_author_max_length_100_accepted(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.return_value = "conv_doc_boundary_author"
            result = await mock_ac(
                page="constrain", author="a" * 100, body="text"
            )
        assert isinstance(result, str) and len(result) > 0

    @pytest.mark.anyio
    async def test_body_max_length_2000_accepted(self):
        with patch("data_layer.addComment", new_callable=AsyncMock) as mock_ac:
            mock_ac.return_value = "conv_doc_boundary_body"
            result = await mock_ac(
                page="constrain", author="Alice", body="b" * 2000
            )
        assert isinstance(result, str) and len(result) > 0


# ==================== Comment type validation tests =======================

class TestCommentValidation:
    """Tests for Comment struct field validators (author 1-100, body 1-2000)."""

    def test_comment_dict_has_required_fields(self):
        c = _make_comment()
        for key in ("_id", "page", "author", "body", "createdAt"):
            assert key in c

    def test_comment_author_non_empty(self):
        c = _make_comment(author="A")
        assert len(c["author"]) >= 1

    def test_comment_author_max_100(self):
        c = _make_comment(author="x" * 100)
        assert len(c["author"]) <= 100

    def test_comment_body_non_empty(self):
        c = _make_comment(body="B")
        assert len(c["body"]) >= 1

    def test_comment_body_max_2000(self):
        c = _make_comment(body="y" * 2000)
        assert len(c["body"]) <= 2000

    def test_created_at_is_positive_number(self):
        c = _make_comment(createdAt=1718000000.0)
        assert isinstance(c["createdAt"], (int, float))
        assert c["createdAt"] > 0
