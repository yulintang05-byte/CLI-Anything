# CLI-Anything Social Trends

**Agent-native CLI for viral trend scraping, account optimization, and theme page monetization.**

Covers YouTube, TikTok, and Instagram. Zero API keys required for core functionality.

---

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# Fetch all trending content from YouTube + TikTok
cli-anything-social-trends trends fetch --platform all --count 20

# Get trending music/sounds
cli-anything-social-trends trends music --platform tiktok

# Get trending hashtags for your niche
cli-anything-social-trends trends hashtags --niche fitness --count 30

# Generate account optimization plan
cli-anything-social-trends account optimize --niche fitness --platform tiktok --followers 5000 --avg-views 2000 --avg-likes 150

# Multi-account optimization report
cli-anything-social-trends account report \
  --account "FitPage:fitness:tiktok:12000:8000:500" \
  --account "TravelVibes:travel:instagram:5000:1200:80"

# List available theme page niches
cli-anything-social-trends theme-page list

# Get full theme page guide
cli-anything-social-trends theme-page guide --niche fitness_transformation

# Get monetization conversion strategy
cli-anything-social-trends theme-page strategy --niche finance_tips --monetization affiliate

# Full combined report (trends + optimization + theme pages)
cli-anything-social-trends report --niches fitness,finance,travel --json -o report.json
```

---

## Commands Reference

### `trends`

| Command | Description |
|---|---|
| `trends fetch` | Fetch trending videos, hashtags, sounds from YouTube/TikTok |
| `trends music` | Fetch trending music tracks and sounds |
| `trends hashtags` | Fetch trending hashtags, optionally filtered by niche |

### `account`

| Command | Description |
|---|---|
| `account optimize` | Generate personalized posting schedule, content mix, hashtag strategy, and 30-day action plan |
| `account report` | Multi-account batch optimization report |

### `theme-page`

| Command | Description |
|---|---|
| `theme-page list` | List all supported niches with difficulty and monetization timeline |
| `theme-page guide` | Full setup checklist + 30-day plan + content templates for a niche |
| `theme-page strategy` | Monetization conversion playbook (affiliate / brand-deals / digital-products) |

### `report`

| Command | Description |
|---|---|
| `report` | Full combined report: live trends + account optimization + theme page guides |

---

## Supported Niches

- `fitness` / `fitness_transformation`
- `cooking` / `aesthetic_food`
- `travel` / `travel_destinations`
- `finance` / `finance_tips`
- `fashion`
- `beauty`
- `gaming` / `tech_reviews`
- `luxury_lifestyle`
- `motivational_quotes`
- `pet_content`

---

## Output

All commands support `--json` for structured JSON output, enabling agent pipelines:

```bash
# Pipe trends into an optimizer
cli-anything-social-trends trends fetch --json | jq '.tiktok.hashtags[:10]'

# Save full report for agent consumption
cli-anything-social-trends report --json -o report.json
```

---

## Architecture

```
social-trends/agent-harness/
├── setup.py
└── cli_anything/social_trends/
    ├── social_trends_cli.py     # Main CLI entry point
    ├── scrapers/
    │   ├── youtube.py           # YouTube Innertube API scraper
    │   └── tiktok.py            # TikTok trend scraper + viral patterns
    ├── optimizer/
    │   └── account_optimizer.py # Account scoring + action plan generator
    └── theme_pages/
        └── guide.py             # Theme page setup + conversion playbooks
```

## Data Sources

- **YouTube**: Innertube API (`/youtubei/v1/browse?browseId=FEtrending`) — no key needed
- **TikTok**: Discover challenge API + curated viral pattern database
- **Optimization**: Rule-based engine trained on niche-specific growth strategies
