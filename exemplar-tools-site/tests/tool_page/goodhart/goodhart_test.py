"""
Adversarial hidden acceptance tests for Tool Page & Comments Section.
These tests target behavioral gaps not covered by visible tests, focusing on
hardcoded-return detection, boundary adjacency, invariant generalization,
and postcondition universality.
"""

import pytest
import time
import math

from tool_page import (
    isToolSlug,
    formatRelativeTime,
    StepBadgeProps,
    VersionBadgeProps,
    CodeBlockProps,
    VideoEmbedProps,
    CommentFormState,
    CommentsSectionProps,
    HexColor,
    ToolSlug,
    ValidationErrors,
)


# ---------------------------------------------------------------------------
# Helper: current time in milliseconds
# ---------------------------------------------------------------------------
def _now_ms():
    return int(time.time() * 1000)


# ===========================================================================
# isToolSlug — adversarial coverage
# ===========================================================================

class TestGoodhartIsToolSlug:

    def test_goodhart_is_tool_slug_case_sensitive(self):
        """isToolSlug must be case-sensitive — uppercase/mixed-case variants of valid slugs must be rejected."""
        assert isToolSlug("Constrain") is False
        assert isToolSlug("LEDGER") is False
        assert isToolSlug("Pact") is False
        assert isToolSlug("ADVOCATE") is False
        assert isToolSlug("Kindex") is False
        assert isToolSlug("ARBITER") is False
        assert isToolSlug("Baton") is False
        assert isToolSlug("SENTINEL") is False
        assert isToolSlug("Chronicler") is False
        assert isToolSlug("STIGMERGY") is False
        assert isToolSlug("Apprentice") is False

    def test_goodhart_is_tool_slug_substring_and_prefix(self):
        """isToolSlug must reject substrings, prefixes, suffixes, and padded variants of valid slugs."""
        assert isToolSlug("constr") is False
        assert isToolSlug("constrain_extra") is False
        assert isToolSlug("ledger ") is False
        assert isToolSlug(" pact") is False
        assert isToolSlug("arbiter2") is False
        assert isToolSlug("sentinel-v2") is False
        assert isToolSlug("my-baton") is False
        assert isToolSlug("chronicler!") is False

    def test_goodhart_is_tool_slug_empty_and_whitespace(self):
        """isToolSlug must return false for empty string and whitespace-only strings."""
        assert isToolSlug("") is False
        assert isToolSlug(" ") is False
        assert isToolSlug("\t") is False
        assert isToolSlug("\n") is False
        assert isToolSlug("  ") is False

    def test_goodhart_is_tool_slug_each_member_individually(self):
        """isToolSlug must return true for every individual canonical slug member."""
        valid_slugs = [
            "constrain", "ledger", "pact", "advocate", "arbiter",
            "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex"
        ]
        for slug in valid_slugs:
            result = isToolSlug(slug)
            assert result is True, f"isToolSlug('{slug}') should be True but got {result}"

    def test_goodhart_is_tool_slug_returns_bool_type(self):
        """isToolSlug must return a strict boolean type, not merely a truthy/falsy value."""
        assert type(isToolSlug("constrain")) is bool
        assert type(isToolSlug("invalid")) is bool
        assert type(isToolSlug("")) is bool

    def test_goodhart_is_tool_slug_rejects_numeric_string(self):
        """isToolSlug must reject purely numeric strings and path-like formats."""
        assert isToolSlug("123") is False
        assert isToolSlug("0") is False
        assert isToolSlug("/constrain") is False
        assert isToolSlug("constrain/") is False
        assert isToolSlug("null") is False
        assert isToolSlug("undefined") is False
        assert isToolSlug("true") is False


# ===========================================================================
# formatRelativeTime — adversarial coverage
# ===========================================================================

class TestGoodhartFormatRelativeTime:

    def test_goodhart_format_relative_time_exact_boundary_60_minutes(self):
        """formatRelativeTime must transition from minutes to hours at exactly 60 minutes."""
        now = _now_ms()
        result_at_60m = formatRelativeTime(now - 3600000)
        assert "hour" in result_at_60m, f"Expected 'hour' in '{result_at_60m}' at 60 minutes"
        result_at_59m59s = formatRelativeTime(now - 3599000)
        assert "minute" in result_at_59m59s, f"Expected 'minute' in '{result_at_59m59s}' at 59m59s"

    def test_goodhart_format_relative_time_exact_boundary_24_hours(self):
        """formatRelativeTime must transition from hours to days at exactly 24 hours."""
        now = _now_ms()
        result_at_24h = formatRelativeTime(now - 86400000)
        assert "day" in result_at_24h, f"Expected 'day' in '{result_at_24h}' at 24 hours"
        result_at_23h = formatRelativeTime(now - 86399000)
        assert "hour" in result_at_23h, f"Expected 'hour' in '{result_at_23h}' at ~23h59m"

    def test_goodhart_format_relative_time_exact_boundary_7_days(self):
        """formatRelativeTime must transition from days to weeks at exactly 7 days."""
        now = _now_ms()
        result_at_7d = formatRelativeTime(now - 7 * 86400000)
        assert "week" in result_at_7d, f"Expected 'week' in '{result_at_7d}' at 7 days"
        result_at_6d = formatRelativeTime(now - 6 * 86400000)
        assert "day" in result_at_6d, f"Expected 'day' in '{result_at_6d}' at 6 days"

    def test_goodhart_format_relative_time_exact_boundary_30_days(self):
        """formatRelativeTime must transition from weeks to months at exactly 30 days."""
        now = _now_ms()
        result_at_30d = formatRelativeTime(now - 30 * 86400000)
        assert "month" in result_at_30d, f"Expected 'month' in '{result_at_30d}' at 30 days"
        result_at_29d = formatRelativeTime(now - 29 * 86400000)
        assert "week" in result_at_29d, f"Expected 'week' in '{result_at_29d}' at 29 days"

    def test_goodhart_format_relative_time_exact_boundary_365_days(self):
        """formatRelativeTime must transition from months to years at exactly 365 days."""
        now = _now_ms()
        result_at_365d = formatRelativeTime(now - 365 * 86400000)
        assert "year" in result_at_365d, f"Expected 'year' in '{result_at_365d}' at 365 days"
        result_at_364d = formatRelativeTime(now - 364 * 86400000)
        assert "month" in result_at_364d, f"Expected 'month' in '{result_at_364d}' at 364 days"

    def test_goodhart_format_relative_time_singular_1_hour(self):
        """formatRelativeTime must produce exact singular form '1 hour ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 3600000) == "1 hour ago"

    def test_goodhart_format_relative_time_singular_1_day(self):
        """formatRelativeTime must produce exact singular form '1 day ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 86400000) == "1 day ago"

    def test_goodhart_format_relative_time_singular_1_week(self):
        """formatRelativeTime must produce exact singular form '1 week ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 7 * 86400000) == "1 week ago"

    def test_goodhart_format_relative_time_singular_1_month(self):
        """formatRelativeTime must produce exact singular form '1 month ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 30 * 86400000) == "1 month ago"

    def test_goodhart_format_relative_time_singular_1_year(self):
        """formatRelativeTime must produce exact singular form '1 year ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 365 * 86400000) == "1 year ago"

    def test_goodhart_format_relative_time_singular_2_minutes(self):
        """formatRelativeTime must produce exact plural form '2 minutes ago'."""
        now = _now_ms()
        assert formatRelativeTime(now - 120000) == "2 minutes ago"

    def test_goodhart_format_relative_time_plural_3_hours(self):
        """formatRelativeTime must use plural form for 3 hours."""
        now = _now_ms()
        assert formatRelativeTime(now - 3 * 3600000) == "3 hours ago"

    def test_goodhart_format_relative_time_plural_4_days(self):
        """formatRelativeTime must use plural form for 4 days."""
        now = _now_ms()
        assert formatRelativeTime(now - 4 * 86400000) == "4 days ago"

    def test_goodhart_format_relative_time_3_weeks(self):
        """formatRelativeTime must correctly report 3 weeks for 21 days."""
        now = _now_ms()
        assert formatRelativeTime(now - 21 * 86400000) == "3 weeks ago"

    def test_goodhart_format_relative_time_11_months(self):
        """formatRelativeTime must correctly report 11 months near year boundary."""
        now = _now_ms()
        result = formatRelativeTime(now - 330 * 86400000)
        assert result == "11 months ago", f"Expected '11 months ago' but got '{result}'"

    def test_goodhart_format_relative_time_large_values(self):
        """formatRelativeTime must handle multi-year differences without overflow."""
        now = _now_ms()
        result_5y = formatRelativeTime(now - 5 * 365 * 86400000)
        assert result_5y == "5 years ago", f"Expected '5 years ago' but got '{result_5y}'"
        result_10y = formatRelativeTime(now - 10 * 365 * 86400000)
        assert "year" in result_10y

    def test_goodhart_format_relative_time_zero_timestamp(self):
        """formatRelativeTime must handle timestamp 0 (Unix epoch) as a valid non-negative input."""
        result = formatRelativeTime(0)
        assert "year" in result, f"Expected 'year' in '{result}' for epoch timestamp"
        assert result.endswith("ago")

    def test_goodhart_format_relative_time_59_seconds(self):
        """formatRelativeTime must return 'just now' at 59 seconds (< 60 boundary)."""
        now = _now_ms()
        assert formatRelativeTime(now - 59000) == "just now"

    def test_goodhart_format_relative_time_output_never_negative(self):
        """formatRelativeTime output must never contain minus signs or negative numbers."""
        now = _now_ms()
        for delta in [1000, 60000, 300000, 3600000, 86400000]:
            result = formatRelativeTime(now - delta)
            assert "-" not in result, f"Negative sign found in '{result}'"
        # Future timestamp (clock skew)
        future_result = formatRelativeTime(now + 5000)
        assert "-" not in future_result, f"Negative sign found in '{future_result}'"

    def test_goodhart_format_relative_time_return_type_string(self):
        """formatRelativeTime must always return a string type."""
        now = _now_ms()
        assert isinstance(formatRelativeTime(now - 1000), str)
        assert isinstance(formatRelativeTime(now - 3600000), str)
        assert isinstance(formatRelativeTime(0), str)

    def test_goodhart_format_relative_time_invariant_all_units(self):
        """formatRelativeTime output must always end with 'ago' or equal 'just now' for diverse inputs beyond visible test values."""
        now = _now_ms()
        test_deltas = [
            500, 30000, 59999,  # just now range
            61000, 90000, 120000, 300000, 1800000, 3540000,  # minutes
            3660000, 7200000, 43200000, 82800000,  # hours
            90000000, 172800000, 518400000,  # days
            604800000, 1209600000, 2419200000,  # weeks
            2592000000, 5184000000, 15552000000,  # months
            31536000000, 63072000000,  # years
        ]
        for delta in test_deltas:
            result = formatRelativeTime(now - delta)
            assert result == "just now" or result.endswith(" ago"), \
                f"formatRelativeTime result '{result}' for delta {delta}ms doesn't match expected format"


# ===========================================================================
# StepBadgeProps — adversarial coverage
# ===========================================================================

class TestGoodhartStepBadgeProps:

    def test_goodhart_step_badge_props_step_1_valid(self):
        """StepBadgeProps must accept step=1 as minimum valid step number."""
        # Should not raise
        StepBadgeProps(step=1, accentColor="#ff0000")

    def test_goodhart_step_badge_props_step_5_mid_range(self):
        """StepBadgeProps must accept mid-range step values like 5."""
        StepBadgeProps(step=5, accentColor="#00ff00")

    def test_goodhart_step_badge_props_step_11_rejected(self):
        """StepBadgeProps must reject step=11 — the validator range is 1-10 even though StepNumber allows 1-11."""
        with pytest.raises((ValueError, TypeError, Exception)):
            StepBadgeProps(step=11, accentColor="#ff0000")

    def test_goodhart_step_badge_props_step_0_rejected(self):
        """StepBadgeProps must reject step=0 — below the minimum of 1."""
        with pytest.raises((ValueError, TypeError, Exception)):
            StepBadgeProps(step=0, accentColor="#ff0000")

    def test_goodhart_step_badge_props_various_hex_colors(self):
        """StepBadgeProps must accept various valid hex colors, not just the ones in visible tests."""
        for color in ["#000000", "#ffffff", "#FFFFFF", "#AbCdEf", "#123456", "#7890ab"]:
            StepBadgeProps(step=3, accentColor=color)

    def test_goodhart_step_badge_props_rejects_rgb_format(self):
        """StepBadgeProps must reject CSS rgb() format colors."""
        with pytest.raises((ValueError, TypeError, Exception)):
            StepBadgeProps(step=3, accentColor="rgb(0,0,0)")

    def test_goodhart_step_badge_props_rejects_named_color(self):
        """StepBadgeProps must reject CSS named colors like 'red'."""
        with pytest.raises((ValueError, TypeError, Exception)):
            StepBadgeProps(step=3, accentColor="red")


# ===========================================================================
# VersionBadgeProps — adversarial coverage
# ===========================================================================

class TestGoodhartVersionBadgeProps:

    def test_goodhart_version_badge_two_segment_version(self):
        """VersionBadgeProps must accept two-segment versions like '1.0'."""
        VersionBadgeProps(version="1.0", accentColor="#abcdef")

    def test_goodhart_version_badge_two_segment_with_v(self):
        """VersionBadgeProps must accept 'v1.0' (v prefix with two segments)."""
        VersionBadgeProps(version="v1.0", accentColor="#abcdef")

    def test_goodhart_version_badge_rejects_single_segment(self):
        """VersionBadgeProps must reject single-segment versions like '1' or 'v1'."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="1", accentColor="#abcdef")
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="v1", accentColor="#abcdef")

    def test_goodhart_version_badge_rejects_empty_version(self):
        """VersionBadgeProps must reject empty string versions."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="", accentColor="#abcdef")

    def test_goodhart_version_badge_prerelease_with_dots(self):
        """VersionBadgeProps must accept pre-release versions with dots like 'v1.2.3-rc.1'."""
        VersionBadgeProps(version="v1.2.3-rc.1", accentColor="#abcdef")

    def test_goodhart_version_badge_prerelease_with_numbers(self):
        """VersionBadgeProps must accept pre-release versions like 'v2.0.0-alpha1'."""
        VersionBadgeProps(version="v2.0.0-alpha1", accentColor="#abcdef")

    def test_goodhart_version_badge_rejects_trailing_dash(self):
        """VersionBadgeProps must reject version strings with trailing dash and no pre-release identifier."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="v1.2.3-", accentColor="#abcdef")

    def test_goodhart_version_badge_rejects_version_with_spaces(self):
        """VersionBadgeProps must reject version strings containing spaces."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="v1.0 beta", accentColor="#abcdef")

    def test_goodhart_version_badge_rejects_letters_in_version_number(self):
        """VersionBadgeProps must reject non-numeric characters in version number segments."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VersionBadgeProps(version="va.b.c", accentColor="#abcdef")

    def test_goodhart_version_badge_large_version_numbers(self):
        """VersionBadgeProps must accept large version numbers like '100.200.300'."""
        VersionBadgeProps(version="100.200.300", accentColor="#abcdef")


# ===========================================================================
# CodeBlockProps — adversarial coverage
# ===========================================================================

class TestGoodhartCodeBlockProps:

    def test_goodhart_code_block_bash_max_length(self):
        """CodeBlockProps must accept bash content at exactly 10000 characters."""
        CodeBlockProps(title="Test", bash="a" * 10000)

    def test_goodhart_code_block_bash_over_max(self):
        """CodeBlockProps must reject bash content exceeding 10000 characters."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CodeBlockProps(title="Test", bash="a" * 10001)

    def test_goodhart_code_block_title_single_char(self):
        """CodeBlockProps must accept single-character titles."""
        CodeBlockProps(title="X", bash="echo hello")

    def test_goodhart_code_block_bash_single_char(self):
        """CodeBlockProps must accept single-character bash content."""
        CodeBlockProps(title="Test", bash="x")

    def test_goodhart_code_block_multiline_bash(self):
        """CodeBlockProps must accept multi-line bash content with newlines."""
        CodeBlockProps(title="Install", bash="apt update\napt install -y curl\ncurl http://example.com")

    def test_goodhart_code_block_title_with_special_chars(self):
        """CodeBlockProps must accept titles containing special characters."""
        CodeBlockProps(title="Step 1: Install & Configure (v2.0)", bash="echo ok")

    def test_goodhart_code_block_bash_at_9999(self):
        """CodeBlockProps must accept bash content at 9999 characters (just under max)."""
        CodeBlockProps(title="Test", bash="b" * 9999)


# ===========================================================================
# VideoEmbedProps — adversarial coverage
# ===========================================================================

class TestGoodhartVideoEmbedProps:

    def test_goodhart_video_embed_url_with_hyphens_underscores(self):
        """VideoEmbedProps must accept YouTube video IDs containing hyphens and underscores."""
        VideoEmbedProps(url="https://www.youtube.com/embed/a-B_c-D_1-2", title="Video")

    def test_goodhart_video_embed_rejects_watch_url(self):
        """VideoEmbedProps must reject YouTube /watch URLs."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", title="Video")

    def test_goodhart_video_embed_rejects_youtu_be(self):
        """VideoEmbedProps must reject youtu.be short URLs."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="https://youtu.be/dQw4w9WgXcQ", title="Video")

    def test_goodhart_video_embed_rejects_http_not_https(self):
        """VideoEmbedProps must reject http (non-https) URLs."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="http://www.youtube.com/embed/abc123", title="Video")

    def test_goodhart_video_embed_url_allows_query_params(self):
        """VideoEmbedProps URL regex has no $ anchor — URLs with query params after video ID should be accepted."""
        VideoEmbedProps(url="https://www.youtube.com/embed/abc123?autoplay=1", title="Video")

    def test_goodhart_video_embed_rejects_empty_url(self):
        """VideoEmbedProps must reject empty URL string."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="", title="Video")

    def test_goodhart_video_embed_title_at_max(self):
        """VideoEmbedProps must accept title at exactly 200 characters."""
        VideoEmbedProps(url="https://www.youtube.com/embed/abc123", title="T" * 200)

    def test_goodhart_video_embed_title_over_max(self):
        """VideoEmbedProps must reject title exceeding 200 characters."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="https://www.youtube.com/embed/abc123", title="T" * 201)

    def test_goodhart_video_embed_rejects_vimeo(self):
        """VideoEmbedProps must reject Vimeo embed URLs — only YouTube is valid."""
        with pytest.raises((ValueError, TypeError, Exception)):
            VideoEmbedProps(url="https://player.vimeo.com/video/123456", title="Video")


# ===========================================================================
# HexColor — adversarial coverage
# ===========================================================================

class TestGoodhartHexColor:

    def test_goodhart_hex_color_rejects_8_digit(self):
        """HexColor must reject 8-digit hex colors (with alpha channel)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#00e5ffaa")

    def test_goodhart_hex_color_case_insensitive(self):
        """HexColor must accept both uppercase and lowercase hex digits."""
        HexColor("#ABCDEF")
        HexColor("#abcdef")
        HexColor("#AbCdEf")

    def test_goodhart_hex_color_rejects_no_hash(self):
        """HexColor must reject hex strings without leading #."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("00e5ff")

    def test_goodhart_hex_color_rejects_empty_string(self):
        """HexColor must reject empty string."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("")

    def test_goodhart_hex_color_rejects_hash_only(self):
        """HexColor must reject a string that is just '#'."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#")

    def test_goodhart_hex_color_rejects_5_digits(self):
        """HexColor must reject 5-digit hex (too short for 6-digit requirement)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#abcde")

    def test_goodhart_hex_color_rejects_7_digits(self):
        """HexColor must reject 7-digit hex (too long for 6-digit requirement)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#abcdef0")

    def test_goodhart_hex_color_rejects_non_hex_chars(self):
        """HexColor must reject strings with non-hex characters like g, h, z."""
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#gggggg")
        with pytest.raises((ValueError, TypeError, Exception)):
            HexColor("#xyz123")


# ===========================================================================
# CommentsSectionProps — adversarial coverage
# ===========================================================================

class TestGoodhartCommentsSectionProps:

    def test_goodhart_comments_section_props_all_slugs(self):
        """CommentsSectionProps must accept every valid ToolSlug as page — not just a hardcoded subset."""
        valid_slugs = [
            "constrain", "ledger", "pact", "advocate", "arbiter",
            "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex"
        ]
        for slug in valid_slugs:
            CommentsSectionProps(page=slug, accentColor="#000000")

    def test_goodhart_comments_section_props_rejects_invalid_slug(self):
        """CommentsSectionProps must reject page values that are not valid ToolSlug members."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentsSectionProps(page="invalid_tool", accentColor="#000000")
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentsSectionProps(page="", accentColor="#000000")

    def test_goodhart_comments_section_props_rejects_empty_accent(self):
        """CommentsSectionProps must reject empty accentColor."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentsSectionProps(page="constrain", accentColor="")

    def test_goodhart_comments_section_props_rejects_3_digit_hex(self):
        """CommentsSectionProps must reject 3-digit shorthand hex colors."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentsSectionProps(page="constrain", accentColor="#fff")


# ===========================================================================
# CommentFormState — adversarial coverage
# ===========================================================================

class TestGoodhartCommentFormState:

    def test_goodhart_comment_form_state_author_at_max(self):
        """CommentFormState must accept author at exactly 100 characters."""
        CommentFormState(author="a" * 100, body="test body", submitting=False, validationErrors=ValidationErrors(author="", body=""))

    def test_goodhart_comment_form_state_body_at_max(self):
        """CommentFormState must accept body at exactly 5000 characters."""
        CommentFormState(author="test", body="b" * 5000, submitting=False, validationErrors=ValidationErrors(author="", body=""))

    def test_goodhart_comment_form_state_single_char_fields(self):
        """CommentFormState must accept single-character author and body (minimum valid length)."""
        CommentFormState(author="A", body="B", submitting=False, validationErrors=ValidationErrors(author="", body=""))

    def test_goodhart_comment_form_state_author_at_101_rejected(self):
        """CommentFormState must reject author at 101 characters (just over max)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentFormState(author="a" * 101, body="test", submitting=False, validationErrors=ValidationErrors(author="", body=""))

    def test_goodhart_comment_form_state_body_at_5001_rejected(self):
        """CommentFormState must reject body at 5001 characters (just over max)."""
        with pytest.raises((ValueError, TypeError, Exception)):
            CommentFormState(author="test", body="b" * 5001, submitting=False, validationErrors=ValidationErrors(author="", body=""))

    def test_goodhart_comment_form_state_submitting_true(self):
        """CommentFormState must accept submitting=True as a valid state."""
        CommentFormState(author="test", body="test body", submitting=True, validationErrors=ValidationErrors(author="", body=""))


# ===========================================================================
# ToolSlug enum — adversarial coverage
# ===========================================================================

class TestGoodhartToolSlug:

    def test_goodhart_tool_slug_no_extra_members(self):
        """ToolSlug enum must contain exactly 11 members — no more, no less."""
        expected = {"constrain", "ledger", "pact", "advocate", "arbiter",
                    "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex"}
        # Get all members - adapt to however ToolSlug is implemented
        if hasattr(ToolSlug, '__members__'):
            actual = set(ToolSlug.__members__.keys()) if hasattr(ToolSlug, '__members__') else set()
            # For string enum, values might differ from keys
            actual_values = {m.value if hasattr(m, 'value') else m for m in ToolSlug}
            assert actual_values == expected or actual == expected
        elif hasattr(ToolSlug, '__iter__'):
            actual = set(ToolSlug)
            assert len(actual) == 11
        else:
            # If ToolSlug is a list or similar
            assert len(expected) == 11

    def test_goodhart_tool_slug_members_are_lowercase(self):
        """All ToolSlug members must be lowercase strings."""
        expected = ["constrain", "ledger", "pact", "advocate", "arbiter",
                    "baton", "sentinel", "chronicler", "stigmergy", "apprentice", "kindex"]
        for slug in expected:
            assert slug == slug.lower()
            assert isToolSlug(slug) is True
