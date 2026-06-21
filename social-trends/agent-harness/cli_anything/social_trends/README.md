# cli-anything-social-trends

**YouTube & TikTok viral trends, hashtags, music, and account optimization CLI.**

Part of the [CLI-Anything](https://github.com/cli-anything/cli-anything) framework — making any software agent-native.

## What it does

- **Trending videos** — Top YouTube and TikTok trending with full engagement metrics
- **Hashtag research** — Trending hashtags aggregated from viral content
- **Music/sounds** — Trending audio on both platforms (critical for algorithm reach)
- **Account optimization** — Data-driven posting schedule, hashtag strategy, and growth tactics for your tier
- **Viral potential scoring** — Score any video idea 0-100 before you post
- **Theme page strategy** — Complete system for building converting niche pages from scratch

## Setup

```bash
pip install -e .
```

### API Keys Required

**YouTube Data API v3 (Free — 10,000 units/day)**
1. Go to [Google Cloud Console](https://console.developers.google.com/)
2. Create a project → Enable **YouTube Data API v3**
3. Create credentials → API Key

```bash
social-trends config set youtube_api_key YOUR_KEY
```

**TikTok via RapidAPI (Freemium — 500 req/month free)**
1. Go to [RapidAPI](https://rapidapi.com)
2. Search **"TikTok Scraper"** → Subscribe to free plan
3. Copy your API key

```bash
social-trends config set rapidapi_key YOUR_KEY
```

Or run the setup wizard:
```bash
social-trends config setup
```

## Usage

```bash
# Trending videos
social-trends trending youtube --region US --category music
social-trends trending tiktok --region US

# Hashtag research
social-trends hashtags youtube --region US
social-trends hashtags tiktok --region US
social-trends hashtags youtube --search fitness   # search specific hashtag

# Music/sounds
social-trends music youtube --region US
social-trends music tiktok

# Cross-platform combined feed
social-trends all-trends --region US

# Account optimization
social-trends optimize --platform tiktok --followers 5000 --niche fitness \
    --avg-views 3000 --avg-likes 200 --posts-per-week 2

# Score a video idea
social-trends score "5 Money Mistakes That Keep You Broke" --niche finance

# Theme page strategy
social-trends theme-page guide
social-trends theme-page niches
social-trends theme-page playbook --niche finance --platform tiktok
social-trends theme-page monetize
social-trends theme-page niche-detail finance

# JSON output (agent-friendly)
social-trends --json trending youtube --limit 10

# Interactive REPL
social-trends repl
```

## Theme Page — Quick Start

A **converting theme page** reposts viral niche content without needing a face on camera.
It's the fastest path to a monetizable social account.

```bash
# 1. Find your best niche
social-trends theme-page niches

# 2. Get your 30-day launch playbook
social-trends theme-page playbook --niche "Personal Finance / Wealth"

# 3. See revenue milestones
social-trends theme-page monetize

# 4. Get trending content to post today
social-trends trending tiktok --region US
social-trends hashtags tiktok --region US
```

## Supported Regions

`US` `GB` `CA` `AU` `IN` `BR` `MX` `DE` `FR` `JP` `KR` + any ISO 3166-1 alpha-2 code

## Architecture

```
cli_anything/social_trends/
├── social_trends_cli.py      # Main Click CLI entry point
├── core/
│   ├── config.py             # Config management (~/.cli-anything-social-trends/)
│   ├── youtube_trends.py     # YouTube Data API v3 integration
│   ├── tiktok_trends.py      # TikTok Research API + RapidAPI integration
│   ├── account_optimizer.py  # Engagement benchmarks + growth tactics engine
│   └── theme_page.py         # Theme page strategy + monetization blueprints
├── utils/
│   └── repl_skin.py          # Unified REPL interface (cli-anything standard)
└── tests/
    └── test_core.py          # 50 unit + CLI smoke tests
```

## Tests

```bash
pytest cli_anything/social_trends/tests/ -v
```

All tests run without API keys (unit tests use synthetic data; API-dependent
tests are integration-only and skipped without keys).
