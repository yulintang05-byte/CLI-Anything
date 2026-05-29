# Social Trends — Agent Harness

## Overview

The `social-trends` harness makes social media intelligence fully agent-native. It provides viral trend scraping from YouTube and TikTok, hashtag research and optimization, trending music tracking, account optimization, and a comprehensive theme-page strategy engine.

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# Fetch viral trends from both platforms
social-trends trends fetch --platform both --limit 10

# Research hashtags for a niche
social-trends hashtags research fitness --limit 20

# Get an optimized hashtag mix
social-trends hashtags suggest --niche finance --count 30

# Track trending audio
social-trends music trending --platform tiktok

# Register and optimize a social account
social-trends accounts add --platform tiktok --username mypage --niche fitness
social-trends accounts optimize acc_XXXXXXXX

# Theme page strategy
social-trends theme-pages niches
social-trends theme-pages guide --niche crypto
social-trends theme-pages strategy finance

# Content calendar
social-trends schedule calendar acc_XXXXXXXX --days 14
```

## Interactive REPL

```bash
social-trends
# or
social-trends repl
```

## JSON Output (for agent use)

```bash
social-trends --json trends fetch --platform both
social-trends --json hashtags suggest --niche luxury --count 20
social-trends --json accounts optimize acc_XXXXXXXX
```

## Data Sources

| Feature | Live Source | Fallback |
|---------|------------|---------|
| YouTube trends | yt-initial-data (public HTML) | Rich mock data |
| TikTok trends | TikTok Research API (TIKTOK_API_TOKEN) | Rich mock data |
| Hashtags | Built-in niche database | — |
| Music | TikTok Research API / YouTube mock | Rich mock data |
| Account optimization | Built-in strategy engine | — |
| Theme page strategies | Built-in niche intelligence | — |

## Architecture

```
social_trends/
  core/
    store.py        — Lightweight JSON persistence (~/.social_trends_session.json)
    trends.py       — YouTube scraping + TikTok API + mock fallback
    hashtags.py     — Niche hashtag database + ranking engine
    music.py        — Trending audio tracker
    accounts.py     — Account profile + optimization engine
    theme_pages.py  — Niche strategy intelligence (10 niches)
    scheduler.py    — Content calendar generator
  utils/
    repl_skin.py    — Branded REPL UI
```

## Tests

```bash
cd social-trends/agent-harness
pip install pytest
pytest tests/test_core.py -v
```
