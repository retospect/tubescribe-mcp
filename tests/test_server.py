"""Tests for tubescribe_mcp.server — MCP tool layer."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from tubescribe_mcp.server import get_transcript, list_transcript_languages


def _snippet(start: float, text: str):
    """Mimic a youtube_transcript_api FetchedTranscriptSnippet."""
    return SimpleNamespace(start=start, duration=5.0, text=text)


class TestGetTranscript:
    @patch("tubescribe_mcp.transcript._api")
    def test_plain_text(self, mock_api):
        mock_api.fetch.return_value = [
            _snippet(0.0, "Hello"),
            _snippet(5.0, "World"),
        ]
        result = get_transcript("dQw4w9WgXcQ")
        assert result == "Hello\nWorld"
        mock_api.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["en"])

    @patch("tubescribe_mcp.transcript._api")
    def test_with_timestamps(self, mock_api):
        mock_api.fetch.return_value = [
            _snippet(0.0, "Hello"),
            _snippet(65.0, "World"),
        ]
        result = get_transcript("dQw4w9WgXcQ", timestamps=True)
        assert "[0:00] Hello" in result
        assert "[1:05] World" in result

    @patch("tubescribe_mcp.transcript._api")
    def test_custom_languages(self, mock_api):
        mock_api.fetch.return_value = [_snippet(0.0, "Hallo")]
        result = get_transcript("dQw4w9WgXcQ", languages="de,en")
        mock_api.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["de", "en"])

    def test_invalid_video_returns_error(self):
        result = get_transcript("not-a-valid-url-at-all")
        assert "Cannot extract" in result

    @patch("tubescribe_mcp.transcript._api")
    def test_url_input(self, mock_api):
        mock_api.fetch.return_value = [_snippet(0.0, "Hi")]
        result = get_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        mock_api.fetch.assert_called_once_with("dQw4w9WgXcQ", languages=["en"])


class TestListTranscriptLanguages:
    @patch("tubescribe_mcp.transcript._api")
    def test_lists_languages(self, mock_api):
        t1 = MagicMock()
        t1.language = "English"
        t1.language_code = "en"
        t1.is_generated = True
        t1.is_translatable = True

        t2 = MagicMock()
        t2.language = "French"
        t2.language_code = "fr"
        t2.is_generated = False
        t2.is_translatable = False

        mock_api.list.return_value = [t1, t2]

        result = list_transcript_languages("dQw4w9WgXcQ")
        assert "English [en]" in result
        assert "auto-generated" in result
        assert "French [fr]" in result

    @patch("tubescribe_mcp.transcript._api")
    def test_empty_list(self, mock_api):
        mock_api.list.return_value = []
        result = list_transcript_languages("dQw4w9WgXcQ")
        assert "No transcripts" in result

    @patch("tubescribe_mcp.transcript._api")
    def test_error_handled(self, mock_api):
        mock_api.list.side_effect = Exception("network fail")
        result = list_transcript_languages("dQw4w9WgXcQ")
        assert "Error" in result
        assert "network fail" in result
