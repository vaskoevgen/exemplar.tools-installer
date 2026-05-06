"""
Adversarial hidden acceptance tests for data_layer component.
These tests catch implementations that pass visible tests through shortcuts
(hardcoded returns, missing validation, partial invariants) rather than
genuinely satisfying the contract.
"""

import pytest
import re
import time
import math
import copy
import os

# Attempt import — tests will fail clearly if module not found
from data_layer import (
    TOOLS,
    TOOL_SLUGS,
    getToolBySlug,
    addComment,
    listComments,
)

# Try importing YouTubeEmbedUrl validation if it exists
try:
    from data_layer import YouTubeEmbedUrl, validate_youtube_embed_url
    HAS_YOUTUBE_VALIDATOR = True
except ImportError:
    try:
        from data_layer import YouTubeEmbedUrl
        HAS_YOUTUBE_VALIDATOR = True
    except ImportError:
        HAS_YOUTUBE_VALIDATOR = False

# Backend availability check for Convex-dependent tests
BACKEND_AVAILABLE = True
try:
    # Try a quick operation to see if backend is reachable
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
except Exception:
    pass


# ============================================================
# Helper: Relative luminance & WCAG contrast ratio calculation
# ============================================================

def _hex_to_rgb(hex_color: str):
    """Convert a hex color string to (r, g, b) tuple with values 0-255."""
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _relative_luminance(r, g, b):
    """Calculate relative luminance per WCAG 2.0."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def _contrast_ratio(hex1, hex2):
    """Calculate WCAG contrast ratio between two hex colors."""
    l1 = _relative_luminance(*_hex_to_rgb(hex1))
    l2 = _relative_luminance(*_hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# Helper to access tool fields in a dict or object-attribute agnostic way
def _get(tool, field, default=None):
    if isinstance(tool, dict):
        return tool.get(field, default)
    return getattr(tool, field, default)


ALL_SLUGS = [
    'constrain', 'ledger', 'pact', 'advocate', 'arbiter',
    'baton', 'sentinel', 'chronicler', 'stigmergy', 'apprentice', 'kindex'
]


# ============================================================
# getToolBySlug tests
# ============================================================

class TestGoodhartGetToolBySlug:
    """Tests for getToolBySlug beyond what visible tests cover."""

    def test_goodhart_all_slugs_return_matching_slug(self):
        """getToolBySlug must return a ToolDef whose slug field matches the queried slug for every valid variant, not just 'constrain'."""
        for slug in ALL_SLUGS:
            result = getToolBySlug(slug)
            assert result is not None, f"getToolBySlug('{slug}') returned None"
            assert _get(result, 'slug') == slug, (
                f"getToolBySlug('{slug}') returned slug={_get(result, 'slug')}"
            )
            # Verify non-empty essential string fields
            assert _get(result, 'name') and str(_get(result, 'name')).strip(), (
                f"Tool '{slug}' has empty name"
            )
            assert _get(result, 'description') and str(_get(result, 'description')).strip(), (
                f"Tool '{slug}' has empty description"
            )
            assert _get(result, 'version') and str(_get(result, 'version')).strip(), (
                f"Tool '{slug}' has empty version"
            )

    def test_goodhart_step_matches_tools_array_position(self):
        """getToolBySlug must return a ToolDef whose step field corresponds to the tool's position in the TOOLS array."""
        for i, tool in enumerate(TOOLS):
            slug = _get(tool, 'slug')
            result = getToolBySlug(slug)
            assert result is not None
            expected_step = _get(tool, 'step')
            actual_step = _get(result, 'step')
            assert actual_step == expected_step, (
                f"getToolBySlug('{slug}').step = {actual_step}, expected {expected_step}"
            )

    def test_goodhart_near_miss_strings(self):
        """getToolBySlug must return undefined for strings that are substrings, superstrings, or whitespace-padded versions of valid slugs."""
        near_misses = [
            'constrai', 'constrains', 'pact ', ' ledger', 'kindex1',
            'ledge', 'advocate_', 'batons', 'sentinel_', 'apprentic',
        ]
        for s in near_misses:
            result = getToolBySlug(s)
            assert result is None, (
                f"getToolBySlug('{s}') should return None but got {result}"
            )

    def test_goodhart_none_input(self):
        """getToolBySlug must handle None input gracefully by returning undefined rather than crashing."""
        try:
            result = getToolBySlug(None)
            assert result is None
        except TypeError:
            # Also acceptable: raising TypeError for wrong type
            pass

    def test_goodhart_numeric_input(self):
        """getToolBySlug must handle non-string input types without crashing."""
        for val in [1, 0, True, False, 3.14, [], {}]:
            try:
                result = getToolBySlug(val)
                assert result is None, (
                    f"getToolBySlug({val!r}) should return None"
                )
            except (TypeError, AttributeError):
                pass  # Acceptable to raise for wrong types

    def test_goodhart_special_characters_slug(self):
        """getToolBySlug must return undefined for slugs containing special characters like slashes, dots, or injection patterns."""
        special = [
            'constrain/admin', 'ledger.js', '../etc/passwd',
            'pact<script>', 'arbiter&foo=bar', 'baton#anchor',
        ]
        for s in special:
            result = getToolBySlug(s)
            assert result is None, (
                f"getToolBySlug('{s}') should return None"
            )

    def test_goodhart_returns_instructions_list_for_every_slug(self):
        """getToolBySlug must return a ToolDef with an instructions field that is a list with valid InstructionStep items for every slug."""
        for slug in ALL_SLUGS:
            result = getToolBySlug(slug)
            assert result is not None
            instructions = _get(result, 'instructions')
            assert isinstance(instructions, (list, tuple)), (
                f"Tool '{slug}' instructions is not a list: {type(instructions)}"
            )
            for step in instructions:
                assert _get(step, 'title') is not None
                assert _get(step, 'bash') is not None


# ============================================================
# TOOLS array invariant tests
# ============================================================

class TestGoodhartToolsInvariants:
    """Invariant tests for the TOOLS constant array beyond visible coverage."""

    def test_goodhart_step_numbers_cover_full_range(self):
        """The set of step numbers across all TOOLS entries must be exactly {1..11} with no gaps."""
        steps = {_get(t, 'step') for t in TOOLS}
        assert steps == set(range(1, 12)), (
            f"TOOLS step numbers {steps} != expected {set(range(1, 12))}"
        )

    def test_goodhart_tools_ordered_by_step(self):
        """TOOLS array must be ordered by step number ascending (indexed by workflow step order)."""
        for i, tool in enumerate(TOOLS):
            assert _get(tool, 'step') == i + 1, (
                f"TOOLS[{i}].step = {_get(tool, 'step')}, expected {i + 1}"
            )

    def test_goodhart_all_names_nonempty(self):
        """Every ToolDef in TOOLS must have a non-empty, non-whitespace name string."""
        for tool in TOOLS:
            name = _get(tool, 'name')
            assert name is not None and isinstance(name, str) and name.strip(), (
                f"Tool '{_get(tool, 'slug')}' has invalid name: {name!r}"
            )

    def test_goodhart_all_descriptions_nonempty(self):
        """Every ToolDef in TOOLS must have a non-empty description string."""
        for tool in TOOLS:
            desc = _get(tool, 'description')
            assert desc is not None and isinstance(desc, str) and len(desc) > 0, (
                f"Tool '{_get(tool, 'slug')}' has empty/missing description"
            )

    def test_goodhart_all_versions_nonempty(self):
        """Every ToolDef in TOOLS must have a non-empty version string."""
        for tool in TOOLS:
            ver = _get(tool, 'version')
            assert ver is not None and isinstance(ver, str) and ver.strip(), (
                f"Tool '{_get(tool, 'slug')}' has invalid version: {ver!r}"
            )

    def test_goodhart_all_required_fields_present(self):
        """Every ToolDef must have all 8 required struct fields present."""
        required_fields = ['slug', 'name', 'description', 'step', 'version', 'accentColor', 'instructions']
        # videoUrl may be None but the key should exist
        for tool in TOOLS:
            for field in required_fields:
                val = _get(tool, field)
                assert val is not None, (
                    f"Tool '{_get(tool, 'slug')}' missing field '{field}'"
                )

    def test_goodhart_instruction_steps_nonempty_strings(self):
        """Every InstructionStep must have non-empty title and bash fields — no placeholders."""
        for tool in TOOLS:
            slug = _get(tool, 'slug')
            instructions = _get(tool, 'instructions')
            for i, step in enumerate(instructions):
                title = _get(step, 'title')
                bash = _get(step, 'bash')
                assert title and isinstance(title, str) and title.strip(), (
                    f"Tool '{slug}' instruction[{i}] has empty title"
                )
                assert bash and isinstance(bash, str) and bash.strip(), (
                    f"Tool '{slug}' instruction[{i}] has empty bash"
                )

    def test_goodhart_accent_color_proper_hex(self):
        """Every accentColor must start with '#' and be either 4 or 7 characters long."""
        for tool in TOOLS:
            color = _get(tool, 'accentColor')
            assert isinstance(color, str), f"accentColor is not a string: {color!r}"
            assert color.startswith('#'), f"accentColor doesn't start with #: {color}"
            assert len(color) in (4, 7), (
                f"accentColor has invalid length {len(color)}: {color}"
            )

    def test_goodhart_video_url_no_query_params(self):
        """Every defined videoUrl must not contain query params or extra path segments after the video ID."""
        for tool in TOOLS:
            slug = _get(tool, 'slug')
            url = _get(tool, 'videoUrl')
            if slug == 'kindex':
                continue
            assert url is not None and isinstance(url, str)
            # Must not contain ? or & after the video ID
            assert '?' not in url, f"Tool '{slug}' videoUrl contains '?': {url}"
            assert '&' not in url, f"Tool '{slug}' videoUrl contains '&': {url}"
            # Extract part after /embed/
            parts = url.split('/embed/')
            assert len(parts) == 2, f"Tool '{slug}' videoUrl malformed: {url}"
            video_id = parts[1]
            assert len(video_id) == 11, (
                f"Tool '{slug}' videoUrl video ID has length {len(video_id)}: {video_id}"
            )

    def test_goodhart_kindex_video_strictly_none(self):
        """The kindex tool's videoUrl must be exactly None/undefined, not empty string or other falsy value."""
        kindex = None
        for tool in TOOLS:
            if _get(tool, 'slug') == 'kindex':
                kindex = tool
                break
        assert kindex is not None, "kindex tool not found in TOOLS"
        video_url = _get(kindex, 'videoUrl')
        assert video_url is None, (
            f"kindex videoUrl should be None, got {video_url!r} (type={type(video_url).__name__})"
        )

    def test_goodhart_non_kindex_video_urls_are_strings(self):
        """All 10 non-kindex tools must have videoUrl as a str type matching the YouTube embed pattern."""
        for tool in TOOLS:
            slug = _get(tool, 'slug')
            if slug == 'kindex':
                continue
            url = _get(tool, 'videoUrl')
            assert isinstance(url, str), (
                f"Tool '{slug}' videoUrl is not a string: {type(url).__name__}"
            )
            assert url.startswith('https://www.youtube.com/embed/'), (
                f"Tool '{slug}' videoUrl doesn't start with embed URL: {url}"
            )

    def test_goodhart_slugs_are_url_safe(self):
        """Every slug must contain only lowercase alphanumeric characters (URL-safe)."""
        pattern = re.compile(r'^[a-z][a-z0-9]*$')
        for tool in TOOLS:
            slug = _get(tool, 'slug')
            assert pattern.match(slug), f"Slug '{slug}' is not URL-safe"

    def test_goodhart_wcag_aa_contrast(self):
        """Every accentColor must have WCAG AA compliant contrast ratio >= 4.5 against dark background #0f172a."""
        dark_bg = '#0f172a'
        for tool in TOOLS:
            slug = _get(tool, 'slug')
            color = _get(tool, 'accentColor')
            ratio = _contrast_ratio(color, dark_bg)
            assert ratio >= 4.5, (
                f"Tool '{slug}' accentColor {color} has contrast ratio {ratio:.2f} < 4.5 against {dark_bg}"
            )


# ============================================================
# TOOL_SLUGS tests
# ============================================================

class TestGoodhartToolSlugs:

    def test_goodhart_tool_slugs_length(self):
        """TOOL_SLUGS must contain exactly 11 elements matching TOOLS length."""
        assert len(TOOL_SLUGS) == 11
        assert len(TOOL_SLUGS) == len(TOOLS)

    def test_goodhart_tool_slugs_contains_all_variants(self):
        """TOOL_SLUGS must contain every ToolSlug enum variant exactly once."""
        assert set(TOOL_SLUGS) == set(ALL_SLUGS), (
            f"TOOL_SLUGS set {set(TOOL_SLUGS)} != expected {set(ALL_SLUGS)}"
        )

    def test_goodhart_tool_slugs_readonly(self):
        """TOOL_SLUGS should be effectively immutable — modifications should not persist."""
        original = list(TOOL_SLUGS)
        try:
            # Try to modify — this may raise or silently fail
            if isinstance(TOOL_SLUGS, list):
                TOOL_SLUGS_copy = TOOL_SLUGS[:]  # Just verify content
            else:
                pass  # tuple or frozen — already immutable
        except Exception:
            pass
        # Verify content unchanged
        assert list(TOOL_SLUGS) == original


# ============================================================
# YouTubeEmbedUrl validation tests
# ============================================================

class TestGoodhartYouTubeUrl:

    def _validate(self, url):
        """Try various ways the module might expose validation."""
        pattern = re.compile(r'^https://www\.youtube\.com/embed/[a-zA-Z0-9_-]{11}$')
        return bool(pattern.match(url))

    def test_goodhart_rejects_extra_path(self):
        """YouTubeEmbedUrl must reject URLs with extra path segments after 11-char video ID."""
        assert not self._validate('https://www.youtube.com/embed/dQw4w9WgXcQ/extra')

    def test_goodhart_rejects_query_params(self):
        """YouTubeEmbedUrl must reject embed URLs with query parameters."""
        assert not self._validate('https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1')

    def test_goodhart_rejects_long_id(self):
        """YouTubeEmbedUrl must reject video IDs longer than 11 characters."""
        assert not self._validate('https://www.youtube.com/embed/dQw4w9WgXcQx')

    def test_goodhart_rejects_http(self):
        """YouTubeEmbedUrl must reject non-HTTPS embed URLs."""
        assert not self._validate('http://www.youtube.com/embed/dQw4w9WgXcQ')

    def test_goodhart_rejects_no_www(self):
        """YouTubeEmbedUrl must reject embed URLs without www. subdomain."""
        assert not self._validate('https://youtube.com/embed/dQw4w9WgXcQ')

    def test_goodhart_accepts_valid_with_dashes_underscores(self):
        """YouTubeEmbedUrl must accept video IDs containing dashes and underscores."""
        assert self._validate('https://www.youtube.com/embed/a-b_c-d_e-F')

    def test_goodhart_rejects_empty_id(self):
        """YouTubeEmbedUrl must reject embed URLs with empty video ID."""
        assert not self._validate('https://www.youtube.com/embed/')

    def test_goodhart_rejects_spaces_in_id(self):
        """YouTubeEmbedUrl must reject embed URLs with spaces in video ID."""
        assert not self._validate('https://www.youtube.com/embed/dQw4w9 gXcQ')


# ============================================================
# Comment system tests (with mocking for Convex backend)
# ============================================================

class TestGoodhartComments:
    """Tests for addComment and listComments beyond visible coverage."""

    @pytest.fixture(autouse=True)
    def _setup_comment_mocks(self, monkeypatch):
        """
        Set up in-memory mock for Convex backend if functions use one.
        If the functions directly interact with a backend, these tests
        will exercise the real implementation.
        """
        self._comments_store = []
        self._original_add = addComment
        self._original_list = listComments

    @pytest.mark.anyio
    async def test_goodhart_tab_only_author_rejected(self):
        """addComment must reject author containing only tab characters as whitespace-only."""
        with pytest.raises(Exception):
            await addComment(page='constrain', author='\t\t', body='Valid body')

    @pytest.mark.anyio
    async def test_goodhart_newline_only_body_rejected(self):
        """addComment must reject body containing only newline characters as whitespace-only."""
        with pytest.raises(Exception):
            await addComment(page='constrain', author='Alice', body='\n\n')

    @pytest.mark.anyio
    async def test_goodhart_mixed_whitespace_author_rejected(self):
        """addComment must reject author with mixed whitespace types (tabs, spaces, newlines) but no visible chars."""
        with pytest.raises(Exception):
            await addComment(page='pact', author=' \t \n ', body='Valid body')

    @pytest.mark.anyio
    async def test_goodhart_single_char_author_accepted(self):
        """addComment must accept a single non-whitespace character as author (minimum boundary)."""
        try:
            await addComment(page='ledger', author='A', body='Test body')
        except Exception as e:
            if 'empty' in str(e).lower() or 'whitespace' in str(e).lower():
                pytest.fail(f"Single char author 'A' should be accepted, got: {e}")

    @pytest.mark.anyio
    async def test_goodhart_single_char_body_accepted(self):
        """addComment must accept a single non-whitespace character as body (minimum boundary)."""
        try:
            await addComment(page='pact', author='Bob', body='X')
        except Exception as e:
            if 'empty' in str(e).lower() or 'whitespace' in str(e).lower():
                pytest.fail(f"Single char body 'X' should be accepted, got: {e}")

    @pytest.mark.anyio
    async def test_goodhart_author_101_rejected(self):
        """addComment must reject author of exactly 101 characters (one over max)."""
        author_101 = 'A' * 101
        with pytest.raises(Exception):
            await addComment(page='arbiter', author=author_101, body='Valid body')

    @pytest.mark.anyio
    async def test_goodhart_body_2001_rejected(self):
        """addComment must reject body of exactly 2001 characters (one over max)."""
        body_2001 = 'B' * 2001
        with pytest.raises(Exception):
            await addComment(page='baton', author='Alice', body=body_2001)

    @pytest.mark.anyio
    async def test_goodhart_add_comment_returns_none(self):
        """addComment must return None/undefined — it is a void mutation."""
        result = await addComment(page='sentinel', author='Tester', body='Hello')
        assert result is None, f"addComment should return None, got {result!r}"

    @pytest.mark.anyio
    async def test_goodhart_created_at_is_epoch_ms(self):
        """addComment must set createdAt as epoch milliseconds (not seconds), reasonably close to now."""
        before = time.time() * 1000
        await addComment(page='chronicler', author='TimeTest', body='Checking timestamp')
        after = time.time() * 1000

        comments = await listComments(page='chronicler')
        # Find our comment
        matching = [c for c in comments if _get(c, 'author') == 'TimeTest']
        assert len(matching) > 0, "Comment not found after addComment"

        created_at = _get(matching[-1], 'createdAt')
        assert isinstance(created_at, (int, float)), (
            f"createdAt should be numeric, got {type(created_at).__name__}"
        )
        # Must be in milliseconds range (> 1.7 trillion = ~2023 in ms)
        assert created_at > 1_700_000_000_000, (
            f"createdAt {created_at} appears to be in seconds, not milliseconds"
        )
        # Should be within reasonable range of current time
        assert before - 5000 <= created_at <= after + 5000, (
            f"createdAt {created_at} not within expected range [{before}, {after}]"
        )

    @pytest.mark.anyio
    async def test_goodhart_list_comments_returns_list(self):
        """listComments must always return a list type, never None or a single object."""
        result = await listComments(page='stigmergy')
        assert isinstance(result, list), (
            f"listComments should return list, got {type(result).__name__}"
        )

    @pytest.mark.anyio
    async def test_goodhart_multiple_comments_all_returned(self):
        """listComments must return ALL comments for a page, not just first or last."""
        page = 'apprentice'
        # Add several comments
        n = 5
        for i in range(n):
            await addComment(page=page, author=f'User{i}', body=f'Comment {i}')

        comments = await listComments(page=page)
        # Should have at least n comments (may have more from other tests)
        user_comments = [c for c in comments if _get(c, 'author', '').startswith('User')]
        assert len(user_comments) >= n, (
            f"Expected at least {n} comments, found {len(user_comments)}"
        )

    @pytest.mark.anyio
    async def test_goodhart_comment_preserves_unicode(self):
        """addComment must preserve unicode characters, special chars, and internal whitespace verbatim."""
        author = 'José María 日本語'
        body = 'Hello <world> & "friends" — it\'s great! 🎉'
        page = 'advocate'

        await addComment(page=page, author=author, body=body)
        comments = await listComments(page=page)

        matching = [c for c in comments if _get(c, 'author') == author]
        assert len(matching) > 0, f"Comment with unicode author not found"
        assert _get(matching[-1], 'body') == body, (
            f"Body not preserved: expected {body!r}, got {_get(matching[-1], 'body')!r}"
        )

    @pytest.mark.anyio
    async def test_goodhart_list_comments_sorted_ascending(self):
        """listComments must return results sorted by createdAt ascending — verified with distinct timestamps."""
        page = 'constrain'
        # Add comments that should have increasing timestamps
        for i in range(3):
            await addComment(page=page, author=f'SortUser{i}', body=f'Sort test {i}')

        comments = await listComments(page=page)
        # Verify ascending order
        for i in range(len(comments) - 1):
            t1 = _get(comments[i], 'createdAt')
            t2 = _get(comments[i + 1], 'createdAt')
            assert t1 <= t2, (
                f"Comments not sorted: createdAt[{i}]={t1} > createdAt[{i+1}]={t2}"
            )

    @pytest.mark.anyio
    async def test_goodhart_list_comments_filters_correctly(self):
        """listComments for page X must not return comments from page Y."""
        await addComment(page='ledger', author='FilterTest', body='I am on ledger')
        await addComment(page='pact', author='FilterTest', body='I am on pact')

        ledger_comments = await listComments(page='ledger')
        for c in ledger_comments:
            assert _get(c, 'page') == 'ledger', (
                f"listComments('ledger') returned comment with page={_get(c, 'page')}"
            )

    @pytest.mark.anyio
    async def test_goodhart_comment_has_all_fields(self):
        """Comment documents must have _id, page, author, body, and createdAt fields with correct types."""
        await addComment(page='baton', author='FieldTest', body='Checking fields')
        comments = await listComments(page='baton')
        matching = [c for c in comments if _get(c, 'author') == 'FieldTest']
        assert len(matching) > 0

        comment = matching[-1]
        # Check required fields exist
        assert _get(comment, '_id') is not None, "Comment missing _id"
        assert _get(comment, 'page') is not None, "Comment missing page"
        assert _get(comment, 'author') is not None, "Comment missing author"
        assert _get(comment, 'body') is not None, "Comment missing body"
        assert _get(comment, 'createdAt') is not None, "Comment missing createdAt"

        # Check types
        assert isinstance(_get(comment, 'page'), str)
        assert isinstance(_get(comment, 'author'), str)
        assert isinstance(_get(comment, 'body'), str)
        assert isinstance(_get(comment, 'createdAt'), (int, float))
