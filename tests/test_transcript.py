"""Tests for tubescribe_mcp.transcript — library layer."""

from __future__ import annotations

import pytest

from tubescribe_mcp.transcript import _format_ts, extract_video_id


class TestExtractVideoId:
    def test_bare_id(self):
        assert extract_video_id("79-bApI3GIU") == "79-bApI3GIU"

    def test_bare_id_whitespace(self):
        assert extract_video_id("  79-bApI3GIU  ") == "79-bApI3GIU"

    def test_watch_url(self):
        assert (
            extract_video_id("https://www.youtube.com/watch?v=79-bApI3GIU")
            == "79-bApI3GIU"
        )

    def test_watch_url_extra_params(self):
        assert (
            extract_video_id(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42"
            )
            == "dQw4w9WgXcQ"
        )

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/79-bApI3GIU") == "79-bApI3GIU"

    def test_shorts_url(self):
        assert (
            extract_video_id("https://www.youtube.com/shorts/79-bApI3GIU")
            == "79-bApI3GIU"
        )

    def test_embed_url(self):
        assert (
            extract_video_id("https://www.youtube.com/embed/79-bApI3GIU")
            == "79-bApI3GIU"
        )

    def test_live_url(self):
        assert (
            extract_video_id("https://www.youtube.com/live/79-bApI3GIU")
            == "79-bApI3GIU"
        )

    def test_mobile_url(self):
        assert (
            extract_video_id("https://m.youtube.com/watch?v=79-bApI3GIU")
            == "79-bApI3GIU"
        )

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="Cannot extract"):
            extract_video_id("https://example.com/nope")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            extract_video_id("")


class TestFormatTs:
    def test_seconds_only(self):
        assert _format_ts(45) == "0:45"

    def test_minutes_seconds(self):
        assert _format_ts(125) == "2:05"

    def test_hours(self):
        assert _format_ts(3661) == "1:01:01"

    def test_zero(self):
        assert _format_ts(0) == "0:00"

    def test_float_truncated(self):
        assert _format_ts(62.9) == "1:02"
