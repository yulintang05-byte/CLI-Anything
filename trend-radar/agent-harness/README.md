# cli-anything-trend-radar

Viral trend intelligence for YouTube, TikTok, and social media — built with the CLI-Anything framework.

## What it does

Scrapes and aggregates trending data from YouTube Data API v3 and TikTok Creative Center, then turns those signals into:

- **Trending hashtags/sounds/videos** by region and time window
- **Optimized hashtag sets** per niche and platform (Instagram, TikTok, YouTube, Twitter)
- **Best posting schedules** with per-day engagement scores
- **Content calendars** auto-generated from trend data, exportable to CSV/JSON
- **Account audit reports** with platform-specific actionable recommendations
- **Theme page playbook** — niches, conversion guides, setup checklists, monetization paths

## Installation

```bash
pip install -e .
# or when published: pip install cli-anything-trend-radar
```

## Quick start

```bash
# TikTok trends (no API key needed)
cli-anything-trend-radar tiktok hashtags --region US --limit 20
cli-anything-trend-radar tiktok sounds --period 7
cli-anything-trend-radar tiktok trending --json

# YouTube trends (requires free API key)
export YOUTUBE_API_KEY=AIza...
cli-anything-trend-radar youtube trending --region US --category music
cli-anything-trend-radar youtube hashtags --niche fitness

# Generate optimized hashtag set
cli-anything-trend-radar optimize hashtags --niche fitness --platform instagram
cli-anything-trend-radar optimize hashtags --niche food --platform tiktok --json

# Account optimization
cli-anything-trend-radar optimize schedule --platform instagram
cli-anything-trend-radar optimize account --platform tiktok --niche fitness --username mypage

# Content calendar
cli-anything-trend-radar calendar generate --niche travel --weeks 4 --posts-per-week 5
cli-anything-trend-radar calendar export calendar.csv --niche fitness --weeks 4

# Theme page guide
cli-anything-trend-radar theme guide --topic overview
cli-anything-trend-radar theme guide --topic monetize
cli-anything-trend-radar theme niches --category fitness
cli-anything-trend-radar theme convert --from-type personal --to-type theme
cli-anything-trend-radar theme setup --niche fitness --platform instagram

# Interactive REPL
cli-anything-trend-radar repl
```

## API keys

| Platform | Key | How to get | Cost |
|----------|-----|-----------|------|
| YouTube | `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → Enable YouTube Data API v3 | Free (10K requests/day) |
| TikTok | None | Uses Creative Center public data | Free |

## JSON output

Every command supports `--json` for machine-readable output:

```bash
cli-anything-trend-radar tiktok hashtags --json | jq '.[].hashtag_name'
cli-anything-trend-radar optimize hashtags --niche fitness --json | jq '.copy_ready'
cli-anything-trend-radar calendar generate --niche food --json | jq '.weeks[0].posts'
```

## Usage as a library

```python
from cli_anything.trend_radar.core.tiktok_trends import TikTokTrends
from cli_anything.trend_radar.core.hashtag_optimizer import HashtagOptimizer
from cli_anything.trend_radar.core.content_calendar import ContentCalendar

# Trending TikTok hashtags (no API key)
tt = TikTokTrends()
hashtags = tt.get_trending_hashtags(region="US", period=7, limit=20)

# Optimized hashtag set
ho = HashtagOptimizer()
result = ho.generate_set(niche="fitness", platform="instagram", count=30)
print(result["copy_ready"])  # #fitness #gym #workout ...

# 4-week content calendar
cc = ContentCalendar()
cal = cc.generate(niche="food", platform="instagram", weeks=4, posts_per_week=5)
cc.export_csv(cal, "food_calendar.csv")
```

## Running tests

```bash
pytest -v                              # all tests (unit + E2E)
YOUTUBE_API_KEY=AIza... pytest -v      # includes YouTube live API tests
```

## Command reference

```
cli-anything-trend-radar
├── youtube
│   ├── trending     --region --category --limit --api-key
│   ├── hashtags     --niche --region --limit --api-key
│   └── music        --region --limit --api-key
├── tiktok
│   ├── trending     --region --period --limit
│   ├── hashtags     --region --period --limit --sort
│   └── sounds       --region --period --limit
├── optimize
│   ├── hashtags     --niche --platform --count
│   ├── schedule     --platform --niche --timezone
│   └── account      --platform --niche --username
├── calendar
│   ├── generate     --niche --platform --weeks --posts-per-week --output
│   └── export       OUTPUT_FILE --niche --platform --weeks --posts-per-week
├── theme
│   ├── guide        --topic (overview|setup|content|growth|monetize|all)
│   ├── niches       --category --platform
│   ├── convert      --from-type --to-type --platform
│   └── setup        --niche --platform
└── repl
```
