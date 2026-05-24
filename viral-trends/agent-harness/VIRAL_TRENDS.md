# Viral Trends — CLI-Anything Agent Harness

A complete social media intelligence tool for agents: scrape YouTube & TikTok for viral trends, hashtags, and music, then generate account optimization plans and theme page strategies.

---

## Commands

| Command | Description |
|---|---|
| `viral-trends youtube-trending` | Fetch YouTube trending videos + hashtags |
| `viral-trends youtube-music` | Fetch YouTube Music trending tracks |
| `viral-trends youtube-hashtag #TAG` | Fetch top YouTube videos for a hashtag |
| `viral-trends tiktok-trending` | Fetch TikTok trending videos, sounds, hashtags |
| `viral-trends tiktok-sounds` | Fetch TikTok trending sounds only |
| `viral-trends tiktok-hashtag #TAG` | Fetch top TikTok videos for a hashtag |
| `viral-trends tiktok-creators` | Fetch trending TikTok creators |
| `viral-trends all-trends` | Aggregate cross-platform trends (YouTube + TikTok) |
| `viral-trends hashtags` | Top viral hashtags, optionally filtered by niche |
| `viral-trends sounds` | Trending music/sounds across both platforms |
| `viral-trends optimize-account` | Full account audit: bio, schedule, hashtags |
| `viral-trends content-calendar` | 7-day content calendar using live trends |
| `viral-trends growth-hacks` | Platform-specific growth tactics |
| `viral-trends theme-page` | Theme page roadmap, niches, conversion tactics |
| `viral-trends daily-brief` | One-command morning brief with all trends + posting plan |

---

## Quick Start

```bash
pip install -e .

# Morning brief — everything you need to post today
viral-trends daily-brief --region us --niche finance

# All trends from both platforms
viral-trends all-trends --region us

# Get hashtag strategy for your niche
viral-trends hashtags --niche fitness --region us

# TikTok trending right now
viral-trends tiktok-trending --region us --limit 20

# Generate a 7-day content calendar
viral-trends content-calendar --niche finance --platforms tiktok,youtube_shorts

# Audit your TikTok account
viral-trends optimize-account --platform tiktok --type theme_page --niche finance

# Theme page full roadmap
viral-trends theme-page --action roadmap --niche finance --followers 0

# Best niches to start a theme page
viral-trends theme-page --action niches

# Conversion tactics
viral-trends theme-page --action conversion

# All output as JSON (for agents)
viral-trends --json all-trends --region us
```

---

## Options

All commands support `--json` for structured JSON output (ideal for agent pipelines).

| Flag | Description |
|---|---|
| `--json` | Output as JSON instead of human-readable |
| `--region` | Country code: `us`, `uk`, `ca`, `au`, `in`, `br`, `de`, `fr`, `jp`, `kr` |
| `--limit` | Max results to return (default 20) |
| `--niche` | Filter/personalize for your content niche |
| `--platform` | `tiktok`, `youtube`, `youtube_shorts`, `instagram` |
| `--type` | Account type: `theme_page`, `personal_brand`, `educational`, `entertainment`… |

---

## Architecture

```
viral-trends/
  agent-harness/
    setup.py
    requirements.txt
    VIRAL_TRENDS.md
    cli_anything/
      viral_trends/
        viral_trends_cli.py      ← CLI entry point (all commands)
        core/
          youtube_scraper.py     ← YouTube trending/hashtag scraper
          tiktok_scraper.py      ← TikTok trending/sound/creator scraper
          trend_analyzer.py      ← Cross-platform aggregation + scoring
          account_optimizer.py   ← Profile audit, calendar, growth hacks
          theme_page_guide.py    ← Theme page roadmap + conversion guide
        tests/
          test_core.py           ← Unit tests (no network)
          test_cli.py            ← CLI integration tests (mocked)
```

---

## Running Tests

```bash
cd viral-trends/agent-harness
pip install -e ".[test]"
pytest cli_anything/viral_trends/tests/ -v
```
