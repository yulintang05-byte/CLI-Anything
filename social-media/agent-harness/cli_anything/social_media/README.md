# Social Media CLI — Agent-Native Trend Intelligence

**cli-anything harness for social media automation** — Scrape viral trends from YouTube and TikTok, generate optimized hashtag sets, build content strategies, and get complete theme page conversion playbooks.

## Installation

```bash
cd social-media/agent-harness
pip install -e .
```

Requires: Python 3.10+, `click`, `requests`, `beautifulsoup4`

## Quick Start

```bash
# Scrape YouTube trending now
social-media trends youtube --limit 20 --region US

# TikTok trending hashtags
social-media trends tiktok --type hashtags --limit 30

# Trending music (both platforms)
social-media trends music --region US

# Cross-platform hashtag aggregation for a niche
social-media trends hashtags --niche fitness --platform all

# Full trend snapshot
social-media trends all --region US
```

## Account Optimization

```bash
# Profile optimization checklist
social-media optimize profile --platform tiktok --niche fitness

# Generate optimized hashtag set
social-media optimize hashtags --platform tiktok --niche finance --count 30

# Full content strategy with weekly calendar
social-media optimize strategy --niche luxury --posts-per-week 7

# Best posting times
social-media optimize schedule --platform tiktok --timezone EST
```

## Theme Page Conversion

```bash
# Evaluate niche viability
social-media theme-page evaluate --niche luxury

# Complete step-by-step playbook (90-day roadmap)
social-media theme-page playbook --niche finance

# Monetization strategies with setup guides
social-media theme-page monetize --niche fitness

# Convert an existing account
social-media theme-page convert --from-type personal --niche cars --platform tiktok
```

## JSON Output (for agents)

Add `--json` before any subcommand for machine-readable output:

```bash
social-media --json trends tiktok --type hashtags
social-media --json optimize hashtags --niche fitness --platform tiktok
social-media --json theme-page evaluate --niche luxury
```

## Interactive REPL

```bash
social-media repl
# social-media> trends youtube --limit 10
# social-media> optimize strategy --niche fitness
# social-media> quit
```

## Cache Management

Trend data is cached locally for 1 hour to avoid hammering scrapers.

```bash
social-media cache info    # Show cached entries
social-media cache clear   # Force fresh scrape on next run
```

## Architecture

```
cli_anything/social_media/
├── social_media_cli.py       # Main CLI entry point
└── core/
    ├── youtube_scraper.py    # YouTube trending page parser (ytInitialData)
    ├── tiktok_scraper.py     # TikTok discover/API trend scraper
    ├── trend_aggregator.py   # Cross-platform aggregation & scoring
    ├── account_optimizer.py  # Profile, hashtag, strategy optimization
    ├── theme_page_guide.py   # Theme page playbooks & monetization
    └── cache.py              # Local disk cache (~/.cli_anything/social_media_cache)
```

## How Scraping Works

- **YouTube**: Parses `ytInitialData` JSON embedded in trending pages — no API key needed
- **TikTok**: Uses TikTok's discover page + public recommendation endpoint
- **Cache**: Results cached for 1h (TikTok) / 1h (YouTube) in `~/.cli_anything/social_media_cache/`
- **Fallback**: Multiple scraping strategies with graceful error messages

## No API Keys Required

All scrapers work with publicly available data. For higher rate limits or more data:
- YouTube Data API v3 (free 10,000 quota/day)
- TikTok Research API (requires application approval)
