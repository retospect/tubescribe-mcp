"""tubescribe-mcp — MCP server for YouTube video transcripts.

Wraps ``youtube-transcript-api``.  No API key required.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from tubescribe_mcp.transcript import (
    fetch_transcript,
    list_languages as _list_languages,
)

mcp = FastMCP("tubescribe")


@mcp.tool()
def get_transcript(
    video: str,
    languages: str = "",
    timestamps: bool = False,
) -> str:
    """Fetch the transcript of a YouTube video.

    video: YouTube URL (https://www.youtube.com/watch?v=ID, https://youtu.be/ID,
           https://www.youtube.com/shorts/ID) or bare 11-char video ID.
    languages: comma-separated language codes in preference order (e.g. "en,de").
               Defaults to English.
    timestamps: if true, prefix each line with [MM:SS] timestamps.

    Returns plain text transcript.
    """
    lang_list = [c.strip() for c in languages.split(",") if c.strip()] or None
    return fetch_transcript(video, languages=lang_list, timestamps=timestamps)


@mcp.tool()
def list_transcript_languages(video: str) -> str:
    """List available transcript languages for a YouTube video.

    video: YouTube URL or bare 11-char video ID.

    Returns one line per available transcript with language name, code,
    and whether it is auto-generated or translatable.
    """
    try:
        langs = _list_languages(video)
    except Exception as exc:
        return f"Error listing languages: {exc}"

    if not langs:
        return "No transcripts available for this video."

    lines: list[str] = []
    for entry in langs:
        flags = []
        if entry.get("is_generated"):
            flags.append("auto-generated")
        if entry.get("is_translatable"):
            flags.append("translatable")
        suffix = f"  ({', '.join(flags)})" if flags else ""
        lines.append(f"- {entry['language']} [{entry['code']}]{suffix}")

    return "\n".join(lines)


def main():
    """Run the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
