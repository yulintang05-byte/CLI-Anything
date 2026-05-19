# Social Trend Scout — CLI Architecture

## Purpose

CLI harness for viral trend intelligence across YouTube and TikTok. Provides:
- Real-time trending video, hashtag, and music data
- Cross-platform trend correlation (YouTube × TikTok)
- Account optimization (posting times, bio, engagement tactics)
- Theme page creation and monetization playbooks
- 30-day content calendar generation

## Architecture

```
social_trend_scout_cli.py          Main Click CLI (groups: config, trends, optimize, theme-page, calendar)
core/
  session.py                       Persistent config, API keys, trend cache, account registry
  youtube_trends.py                YouTube Data API v3 — trending videos, hashtags, music
  tiktok_trends.py                 TikTokApi (Playwright) + Research API — hashtags, sounds, niche trends
  trend_analyzer.py                Cross-platform merge, viral pattern detection, action plans
  account_optimizer.py             Posting schedules, profile checklists, bio generator, engagement tactics
  theme_pages.py                   Niche guides, content sourcing, conversion strategies, monetization
  content_calendar.py              30-day calendar generation with hooks, CTAs, hashtag rotation
utils/
  output.py                        Table/JSON/CSV formatting, number formatters, viral score display
tests/
  test_core.py                     Unit tests (no external API required) — 95 tests
  test_full_e2e.py                 E2E CLI tests via Click CliRunner — 45 tests
```

## Data Flow

```
API Keys (session.py)
       ↓
YouTubeTrends / TikTokTrends       ← fetch raw trend data
       ↓
TrendAnalyzer                      ← merge, score, classify velocity
       ↓
AccountOptimizer / ThemePageStrategy / ContentCalendar  ← apply to accounts
       ↓
CLI commands (JSON | table | CSV)
```

## State Management

Config stored at `~/.config/social-trend-scout/config.json`:
- `api_keys`: YouTube, TikTok ms_token, TikTok Research API token
- `accounts`: registered platform accounts with niche
- `preferences`: default region, timezone

Trend cache at `~/.config/social-trend-scout/trend_cache.json`:
- TTL: 1 hour (configurable per-call)
- Keyed by `{platform}_{type}_{niche}`

## Supported Niches

motivation, cars, fitness, anime, finance, food, luxury, gaming, beauty

## Platform Support

| Platform  | Method              | Auth Required          |
|-----------|---------------------|------------------------|
| YouTube   | Data API v3         | API key (free tier)    |
| TikTok    | TikTokApi (Playwright) | ms_token (optional) |
| TikTok    | Research API        | Approved token         |

## Installation

```bash
pip install -e .
playwright install chromium   # for TikTok scraping
cli-anything-social-trend-scout --help
```

## Quick Start

```bash
# 1. Set YouTube API key
cli-anything-social-trend-scout config set-key youtube YOUR_KEY

# 2. Fetch all YouTube trends
cli-anything-social-trend-scout trends youtube --region US --type all

# 3. Fetch TikTok trends (no key needed, uses fallback)
cli-anything-social-trend-scout trends tiktok --type hashtags

# 4. Get cross-platform merged report
cli-anything-social-trend-scout trends cross-platform --niche fitness

# 5. Full account audit
cli-anything-social-trend-scout optimize audit tiktok fitness @myaccount

# 6. Theme page playbook
cli-anything-social-trend-scout theme-page playbook motivation

# 7. 30-day content calendar
cli-anything-social-trend-scout calendar generate fitness tiktok --days 30
```
