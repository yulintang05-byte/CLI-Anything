# CLI-Anything Social Trends

Scrape YouTube & TikTok for viral trends, hashtags, and music. Optimize social media accounts. Build profitable theme pages.

## Install

```bash
pip install yt-dlp httpx beautifulsoup4 click prompt-toolkit
pip install -e .
```

## Quick Start

### Scrape YouTube Trending
```bash
social-trends trends scrape-youtube --region US --limit 20
social-trends trends scrape-youtube --region US --category music --json
```

### Scrape TikTok Trending
```bash
social-trends trends scrape-tiktok --region US --limit 20
```

### Get Trending Hashtags
```bash
# TikTok trending hashtags
social-trends trends hashtags --platform tiktok --region US

# YouTube top hashtags for a niche
social-trends trends hashtags --platform youtube --niche fitness

# Analyze a specific hashtag
social-trends trends hashtags --platform tiktok --hashtag fitness
```

### Get Trending Sounds (TikTok)
```bash
social-trends trends sounds --region US
```

### Merged Cross-Platform Report
```bash
# Full trend report (YouTube + TikTok merged)
social-trends trends report --region US -o report.json --format markdown

# JSON output for agent consumption
social-trends --json trends report --region US
```

### Account Optimization
```bash
# Analyze a single account
social-trends account optimize \
  --platform tiktok \
  --username @myaccount \
  --followers 5000 \
  --avg-views 2000 \
  --avg-likes 150 \
  --niche fitness \
  --freq 3 \
  --has-link

# Bulk optimize from JSON file
social-trends account bulk-optimize accounts.json -o results.json

# Get optimal posting schedule
social-trends account schedule --platform tiktok --niche fitness
```

### Theme Pages
```bash
# Full creation playbook
social-trends theme-pages guide
social-trends theme-pages guide --section phase_3_monetization --format markdown

# Browse profitable niches
social-trends theme-pages niches --sort avg_cpm_usd
social-trends theme-pages niches --sort conversion_potential --max-competition medium
social-trends theme-pages niches --search luxury

# Niche deep-dive
social-trends theme-pages niche-detail finance_investing

# Personalized quick-start plan
social-trends theme-pages quick-start --niche fitness --followers 0 --platform tiktok

# Content calendar
social-trends theme-pages calendar --niche finance_investing --days 7 --platforms tiktok,youtube
social-trends theme-pages calendar --niche food_recipes --days 30 -o calendar.md --format markdown
```

### Interactive REPL
```bash
social-trends repl
```

## Agent-Optimized JSON Output

All commands support `--json` flag for structured agent consumption:

```bash
social-trends --json trends report --region US
social-trends --json account optimize --platform tiktok --username test --followers 1000
social-trends --json theme-pages niches --sort conversion_potential
```

## Available Niches

| Key | Name | Avg CPM | Growth Speed |
|-----|------|---------|-------------|
| `finance_investing` | Finance & Investing | $18 | Medium |
| `tech_gadgets` | Tech & Gadgets | $14 | Medium |
| `luxury_lifestyle` | Luxury Lifestyle | $12.50 | Fast |
| `beauty_skincare` | Beauty & Skincare | $11 | Fast |
| `travel` | Travel | $9 | Medium |
| `fitness_motivation` | Fitness & Motivation | $8 | Medium |
| `food_recipes` | Food & Recipes | $7 | Fast |
| `pets_animals` | Pets & Animals | $5.50 | Very Fast |
| `quotes_mindset` | Quotes & Mindset | $4 | Slow |

## Architecture

```
social-trends/agent-harness/
├── setup.py
├── README.md
└── cli_anything/social_trends/
    ├── social_trends_cli.py     # Main CLI entry point
    ├── _repl.py                 # Interactive REPL
    ├── scrapers/
    │   ├── youtube.py           # YouTube trend scraper (yt-dlp)
    │   └── tiktok.py            # TikTok trend scraper (yt-dlp + httpx)
    ├── core/
    │   └── trends.py            # Data models + cross-platform merge
    ├── optimizer/
    │   └── account.py           # Account scoring + recommendations
    ├── theme_pages/
    │   ├── guide.py             # Full theme page playbook
    │   ├── niches.py            # Niche database (9 niches)
    │   └── content_calendar.py  # Weekly/monthly calendar generator
    └── utils/
        └── export.py            # JSON/CSV/Markdown export
```
