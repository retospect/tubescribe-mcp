# tubescribe-mcp

MCP server for fetching [YouTube](https://www.youtube.com/) video transcripts. Thin wrapper around [`youtube-transcript-api`](https://pypi.org/project/youtube-transcript-api/).

No API key required.

## Install

```bash
pip install tubescribe-mcp
```

## Usage

```bash
tubescribe-mcp
```

The server runs on stdio transport (MCP standard).

## Tools

**`get_transcript(video, languages?, timestamps?)`** — fetch a video transcript as plain text.

- `video` — YouTube URL or bare 11-char video ID
- `languages` — comma-separated preference codes, e.g. `"en,de"` (default: English)
- `timestamps` — prefix each line with `[MM:SS]` (default: false)

**`list_transcript_languages(video)`** — list available transcript languages for a video.

## Library

```python
from tubescribe_mcp.transcript import fetch_transcript, list_languages, extract_video_id

text = fetch_transcript("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
langs = list_languages("dQw4w9WgXcQ")
vid = extract_video_id("https://youtu.be/dQw4w9WgXcQ")
```

## License

GPL-3.0-or-later
