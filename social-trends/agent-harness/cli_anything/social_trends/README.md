# cli-anything-social-trends

Viral trend research, hashtag analysis, music discovery, account optimization, and theme page strategies — all from the command line.

## What it does

- **YouTube Trends** — Pull the Most Popular chart by region and category via YouTube Data API v3
- **TikTok Hashtags** — Fetch trending hashtags from public TikTok endpoints (no API key needed)
- **Trending Music** — Discover what sounds are going viral and how to use them legally
- **Hashtag Research** — Curated niche hashtag sets + competitor analysis + scoring
- **Account Optimization** — Platform-specific checklists for YouTube, TikTok, and Instagram
- **Theme Pages** — Complete guide to building and monetizing anonymous theme pages

## Installation

```bash
pip install -e .
```

## Setup

### YouTube API Key (required for YouTube features)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable **YouTube Data API v3**
3. Credentials → Create API Key (restrict to YouTube Data API v3)

```bash
social-trends auth setup --youtube-api-key YOUR_KEY
```

TikTok features (hashtags, sounds, optimization) work without any API key.

## Usage

```bash
# YouTube trending videos (US, all categories)
social-trends youtube trending

# YouTube trending by category (10=Music, 17=Sports, 20=Gaming)
social-trends youtube trending --region US --category 10 --limit 25

# Search YouTube for trending content around a keyword
social-trends youtube search "morning routine" --days 7

# Audit a YouTube channel
social-trends youtube audit UCnUYZLuoy1rq1aVMwx4aTzw

# Extract hashtags from trending videos
social-trends youtube hashtags --region US

# TikTok trending hashtags (no API key needed)
social-trends tiktok hashtags

# TikTok trending sounds guide
social-trends tiktok sounds

# TikTok account optimization checklist
social-trends tiktok checklist

# TikTok 7-day content calendar
social-trends tiktok calendar --niche finance --posts-per-day 2

# Hashtag strategy for a niche
social-trends hashtags niche finance
social-trends hashtags suggest finance --platform tiktok
social-trends hashtags research fitness

# Music for your content niche
social-trends music guide
social-trends music niche fitness
social-trends music find motivation

# Account optimization
social-trends optimize schedule --platform all
social-trends optimize checklist --platform tiktok
social-trends optimize plan --platform tiktok --niche finance --followers 500

# Theme page strategies
social-trends theme list
social-trends theme guide
social-trends theme research --niche finance
social-trends theme compare finance fitness

# Interactive REPL (enter any command above without the 'social-trends' prefix)
social-trends repl

# JSON output (for AI agent integration)
social-trends --json tiktok hashtags
social-trends --json theme research --niche luxury
```

## Available Niches

Hashtag sets and theme page research available for:
`finance`, `fitness`, `motivation`, `luxury`, `tech`, `aesthetic`, `pets`

## YouTube API Quota

YouTube Data API v3 provides **10,000 units/day** free.
- Trending videos fetch: ~1-3 units
- Search: 100 units per request

## TikTok API Note

TikTok's public discover endpoint is used for hashtag data. For research-scale access,
apply for the [TikTok Research API](https://developers.tiktok.com/products/research-api/).

## Running Tests

```bash
cd agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```
