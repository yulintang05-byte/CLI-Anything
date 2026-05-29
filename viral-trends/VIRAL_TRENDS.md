# Viral Trends Harness

This harness was built using the cli-anything methodology.

For the full harness specification and methodology, see:
- `/cli-anything-plugin/HARNESS.md` — Core methodology
- `agent-harness/cli_anything/viral_trends/README.md` — Usage and command reference

## What This Harness Does

`viral-trends` is an agent-native CLI for:

1. **Trend Scraping** — YouTube trending (via yt-dlp) and TikTok viral hashtags/sounds
2. **Account Optimization** — Hashtag sets, posting windows, caption hook templates
3. **Content Scheduling** — Auto-generate 7-day calendars from optimal posting windows
4. **Theme Page Strategy** — Structured guides for building and monetizing theme pages

## Architecture

```
viral_trends/
  core/
    session.py      — Undo/redo state management (identical to clipper)
    workspace.py    — Workspace lifecycle (analog of project.py)
    trends.py       — YouTube + TikTok scrapers with mock fallbacks
    optimizer.py    — Hashtag sets, posting times, caption hooks
    scheduler.py    — 7-day content calendar
    theme_pages.py  — Static guide content (theme pages, conversion, etc.)
  utils/
    repl_skin.py    — Hot-pink accent REPL skin (copy of cli-anything-plugin/repl_skin.py)
  viral_trends_cli.py — Click CLI + REPL
```

## Scraping Strategy

- **YouTube**: Uses `yt-dlp --flat-playlist --dump-json` against the trending feed.
  Requires `pip install yt-dlp`. Gracefully falls back to mock data if not installed.
- **TikTok**: Uses `requests` + `BeautifulSoup` against public pages.
  TikTok's JS-heavy rendering means live scraping often returns 0 results — the CLI
  silently falls back to mock data and reports `"source": "mock-fallback"` in the response.

Both scrapers accept an injectable `fetcher` callable for offline testing.
