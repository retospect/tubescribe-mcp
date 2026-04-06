"""tubescribe-mcp — library layer for YouTube transcript fetching.

Thin shim around ``youtube-transcript-api``.  No API key required.
"""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

_VIDEO_ID_RE = re.compile(r"^[\w-]{11}$")

_api = YouTubeTranscriptApi()


def extract_video_id(video: str) -> str:
    """Extract an 11-character YouTube video ID from a URL or bare ID.

    Accepts:
      - ``https://www.youtube.com/watch?v=ID``
      - ``https://youtu.be/ID``
      - ``https://www.youtube.com/shorts/ID``
      - ``https://www.youtube.com/embed/ID``
      - ``https://www.youtube.com/live/ID``
      - bare 11-char ID (e.g. ``79-bApI3GIU``)

    Raises ``ValueError`` if the ID cannot be determined.
    """
    video = video.strip()

    if _VIDEO_ID_RE.match(video):
        return video

    parsed = urlparse(video)
    host = (parsed.hostname or "").lower().removeprefix("www.")

    if host in ("youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            ids = parse_qs(parsed.query).get("v")
            if ids:
                return ids[0]
        for prefix in ("/shorts/", "/embed/", "/live/"):
            if parsed.path.startswith(prefix):
                segment = parsed.path[len(prefix) :].split("/")[0]
                if segment:
                    return segment
    elif host == "youtu.be":
        segment = parsed.path.lstrip("/").split("/")[0]
        if segment:
            return segment

    raise ValueError(f"Cannot extract YouTube video ID from: {video!r}")


def list_languages(video: str) -> list[dict[str, str | bool]]:
    """Return available transcript languages for a video.

    Each entry: ``{language, code, is_generated, is_translatable}``.
    """
    video_id = extract_video_id(video)
    transcript_list = _api.list(video_id)
    return [
        {
            "language": t.language,
            "code": t.language_code,
            "is_generated": t.is_generated,
            "is_translatable": t.is_translatable,
        }
        for t in transcript_list
    ]


def _format_ts(seconds: float) -> str:
    """Format seconds as ``MM:SS`` or ``H:MM:SS`` for longer videos."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_transcript(
    video: str,
    languages: list[str] | None = None,
    timestamps: bool = False,
) -> str:
    """Fetch a video transcript as plain text.

    Parameters
    ----------
    video:
        YouTube URL or 11-char video ID.
    languages:
        Preferred language codes in priority order. Defaults to ``["en"]``.
    timestamps:
        If True, prefix each segment with ``[MM:SS]``.

    Returns
    -------
    str
        Transcript text.  On error, returns a human-readable error message
        (never raises).
    """
    try:
        video_id = extract_video_id(video)
    except ValueError as exc:
        return str(exc)

    if languages is None:
        languages = ["en"]

    try:
        snippets = _api.fetch(video_id, languages=languages)
    except TranscriptsDisabled:
        return f"Transcripts are disabled for video {video_id}."
    except NoTranscriptFound:
        return (
            f"No transcript found for video {video_id} "
            f"in languages {languages}. "
            "Use list_languages to see what is available."
        )
    except VideoUnavailable:
        return f"Video {video_id} is unavailable."
    except Exception as exc:
        return f"Error fetching transcript: {exc}"

    if timestamps:
        lines = [f"[{_format_ts(s.start)}] {s.text}" for s in snippets]
    else:
        lines = [s.text for s in snippets]

    return "\n".join(lines)
