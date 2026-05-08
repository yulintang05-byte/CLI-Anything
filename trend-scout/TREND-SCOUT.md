# Trend Scout

YouTube & TikTok viral trend scraper, account optimizer, and theme page strategist — built as a CLI-Anything agent harness.

## What it does

- **Scrapes** YouTube and TikTok for trending videos, hashtags, music, and sounds
- **Optimizes** social media accounts with data-driven action plans
- **Generates** content calendars using live trend data
- **Guides** you through creating and monetizing theme pages (niche content pages)
- **Analyzes** competitor channels and creators

Works without API keys using curated static data. Gets dramatically better with live API access.

## Installation

```bash
cd trend-scout/agent-harness
pip install -e .                    # basic (no live scraping)
pip install -e ".[all]"             # all scrapers: YouTube API + yt-dlp + TikTokApi
```

## API Keys (optional but recommended)

```bash
# YouTube Data API v3 — free, 10,000 units/day
# Get it: console.cloud.google.com → Create project → Enable YouTube Data API v3
trend-scout config set YOUTUBE_API_KEY your-key-here

# TikTok ms_token — from your browser cookies after logging in to TikTok
# Get it: DevTools (F12) → Application → Cookies → tiktok.com → msToken
trend-scout config set TIKTOK_MS_TOKEN your-token-here

trend-scout setup    # check status
```

## Quick Start

```bash
# 1. Add your accounts
trend-scout account add tiktok @yourhandle --niche fitness --followers 1200
trend-scout account add youtube @yourchannel --niche fitness --followers 800
trend-scout account add instagram @yourhandle --niche fitness --followers 2000

# 2. Get trending data for your niche
trend-scout trends --niche fitness --region US

# 3. Get hashtag strategy
trend-scout hashtags fitness --followers 1200

# 4. Get trending music/sounds
trend-scout music --region US --niche fitness

# 5. Optimize your TikTok account
trend-scout optimize tiktok fitness --username yourhandle --followers 1200

# 6. Optimize ALL accounts at once
trend-scout optimize-all

# 7. Generate a content calendar
trend-scout schedule weekly --niche fitness --platforms tiktok,youtube,instagram

# 8. Learn theme pages
trend-scout theme-pages guide
```

## Commands

### `trends` — Scrape trending content
```bash
trend-scout trends --niche fitness --platform all --region US --limit 20
trend-scout trends --niche gaming --platform youtube
trend-scout trends --niche beauty --platform tiktok
```

### `hashtags` — Hashtag strategy
```bash
trend-scout hashtags fitness                       # generic strategy
trend-scout hashtags finance --followers 5000      # tailored to your account size
trend-scout hashtags fashion --platform tiktok
```

### `music` — Trending music & sounds
```bash
trend-scout music --region US
trend-scout music --niche fitness                  # sounds that work for your niche
```

### `optimize` — Account optimization
```bash
trend-scout optimize tiktok fitness --followers 1200 --username myhandle
trend-scout optimize youtube gaming --followers 500
trend-scout optimize instagram fashion --followers 8000 --issues no_bio --issues inconsistent
```

**`--issues` flags:**
- `no_bio` — empty bio
- `no_link` — no link in bio
- `inconsistent` — irregular posting
- `no_hashtags` — not using hashtags
- `mixed_niche` — posting too many topics
- `no_growth` — stalled growth

### `optimize-all` — Optimize all configured accounts
```bash
trend-scout optimize-all --region US
```

### `bio` — Generate optimized bios
```bash
trend-scout bio tiktok fitness
trend-scout bio youtube gaming
trend-scout bio instagram fashion
```

### `engagement` — Engagement boost tactics
```bash
trend-scout engagement tiktok fitness --followers 1200
```

### `niche` — Deep niche analysis
```bash
trend-scout niche fitness --region US
trend-scout niche "luxury lifestyle"
```

### `competitor` — Competitor analysis
```bash
trend-scout competitor https://youtube.com/@MrBeast --platform youtube
trend-scout competitor charlidamelio --platform tiktok
```

### `theme-pages` — Theme page strategy

```bash
# Complete guide to creating a theme page
trend-scout theme-pages guide --niche fitness

# All profitable niches ranked by RPM
trend-scout theme-pages niches

# Deep analysis of one niche
trend-scout theme-pages analyze finance

# Monetization playbook based on follower count
trend-scout theme-pages monetize fitness --followers 5000

# How to convert your personal account to a theme page
trend-scout theme-pages convert --from-type personal --to-type theme_page
```

### `schedule` — Content calendars

```bash
# 7-day calendar with trending data
trend-scout schedule weekly --niche fitness --platforms tiktok,youtube,instagram --posts-per-day 2

# Export formats
trend-scout schedule weekly --niche fitness --output csv > calendar.csv
trend-scout schedule weekly --niche fitness --output notion  # paste into Notion
trend-scout schedule weekly --niche fitness --output json

# 30-day plan
trend-scout schedule monthly --niche fitness --posts-per-week 14

# Posting frequency advice
trend-scout schedule frequency tiktok --followers 1200
```

### `account` — Manage accounts
```bash
trend-scout account add tiktok @handle --niche fitness --followers 1200
trend-scout account list
trend-scout account remove tiktok @handle
```

### `repl` — Interactive mode
```bash
trend-scout repl
# Then type commands interactively
```

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
trend-scout --json trends --niche fitness
trend-scout --json hashtags fitness
trend-scout --json optimize tiktok fitness --followers 1200
```

## Theme Pages Guide Summary

A **theme page** is a social media account built around a specific topic (not your personal brand). You curate, create, or aggregate content — no face required.

**Top niches by earning potential:**
| Niche | RPM | Difficulty |
|-------|-----|------------|
| Finance/Wealth | $20-$60 | Medium |
| Luxury Lifestyle | $15-$40 | Low |
| Travel | $12-$30 | Medium |
| Fitness | $10-$25 | Low-Medium |
| Horror/Mystery | $10-$22 | Low |
| Food | $8-$18 | Low |

**Monetization path:**
1. Month 1-2: Affiliate links (set up from day 1)
2. Month 2-3: First brand gifted collab
3. Month 3-4: Digital product ($7-$27)
4. Month 4-6: Paid brand deals
5. Month 6+: Multiple streams simultaneously

## Configuration Storage

```
~/.cli-anything-trend-scout/
├── config.json     # API keys and preferences
└── accounts.json   # your social media accounts
```

## Architecture

```
trend-scout/agent-harness/
├── cli_anything/trend_scout/
│   ├── core/
│   │   ├── youtube_scraper.py   # YouTube Data API v3 + yt-dlp fallback
│   │   ├── tiktok_scraper.py    # TikTokApi + curated static data fallback
│   │   ├── analyzer.py          # Cross-platform trend aggregation
│   │   ├── optimizer.py         # Account optimization plans
│   │   ├── theme_pages.py       # Theme page strategy and monetization
│   │   └── scheduler.py         # Content calendar generator
│   ├── utils/
│   │   ├── config.py            # Config and account management
│   │   └── output.py            # CLI output formatting
│   └── trend_scout_cli.py       # Click CLI entry point + REPL
├── tests/                        # 119 passing tests
└── setup.py
```
