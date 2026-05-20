# CLI-Anything TrendScraper

Agent-native CLI for scraping viral trends from YouTube and TikTok, optimizing social media accounts, and building high-converting theme pages.

## Features

- **YouTube Scraping** — Trending videos, hashtags, and music via YouTube Data API v3 (+ no-key scrape fallback)
- **TikTok Scraping** — Trending hashtags and sounds via Research API or web scrape
- **Cross-Platform Trends** — Merge and score trends across both platforms with virality scoring
- **Caption Optimizer** — Generate optimized captions with trending hashtags per platform
- **Content Calendar** — 7-day content plan with post ideas and optimal posting times
- **Account Analyzer** — Grade your account and get specific growth recommendations
- **Theme Page Playbooks** — Full niche analysis, monetization strategies, and page-flip roadmaps

## Setup

```bash
pip install -e .
```

### API Keys (optional but recommended)

**YouTube (strongly recommended for accurate data):**
```bash
# 1. Get a free API key: https://console.cloud.google.com/apis/credentials
# 2. Enable YouTube Data API v3 in your Google Cloud project
trendscraper config set --youtube-api-key YOUR_KEY
# or: export YOUTUBE_API_KEY=YOUR_KEY
```

**TikTok Research API (optional — scrape fallback works without it):**
```bash
# Apply at: https://developers.tiktok.com/products/research-api/
trendscraper config set --tiktok-token YOUR_TOKEN
# or: export TIKTOK_ACCESS_TOKEN=YOUR_TOKEN
```

## Usage

### Scraping

```bash
# YouTube trending videos + hashtags + music
trendscraper scrape youtube --region US --limit 50

# TikTok trending hashtags + sounds
trendscraper scrape tiktok --region US --limit 30

# Cross-platform merged trends
trendscraper scrape all --region US --output trends.json

# Save YouTube music category
trendscraper scrape youtube --category 10 --region US
```

### Trend Analysis

```bash
# Full trend report with action items
trendscraper trends report --region US --output report.json --csv hashtags.csv

# Top trending hashtags
trendscraper trends hashtags --platform all --region US --top 20

# Trending music and sounds
trendscraper trends music --platform tiktok --region US
```

### Account Optimization

```bash
# Optimized caption with live trending hashtags
trendscraper optimize caption \
  --text "My morning routine changed my life" \
  --platform instagram \
  --niche motivation

# 7-day content calendar
trendscraper optimize calendar \
  --niche fitness \
  --platform tiktok \
  --days 7 \
  --output calendar.json

# Account health analysis + recommendations
trendscraper optimize account \
  --platform tiktok \
  --followers 12000 \
  --avg-views 3500 \
  --avg-likes 280 \
  --niche luxury

# Best posting times
trendscraper optimize times --platform instagram
```

### Theme Pages

```bash
# Analyze a niche
trendscraper theme niche --name luxury

# Compare all niches (score, CPM, saturation)
trendscraper theme compare

# Specific niche comparison
trendscraper theme compare --niches "luxury,finance,fitness,cars"

# Monetization strategy deep-dive
trendscraper theme monetize --method affiliate
trendscraper theme monetize --method page_flipping
trendscraper theme monetize --method digital_products

# Platform growth playbook
trendscraper theme playbook --platform tiktok

# Full page-flip roadmap
trendscraper theme flip \
  --niche luxury \
  --platform instagram \
  --target 50000 \
  --budget 0

# Overview of all strategies
trendscraper theme strategies
```

### Interactive REPL

```bash
trendscraper repl
```

### JSON Output

All commands support `--json` for machine-readable output:
```bash
trendscraper --json scrape all --region US
trendscraper --json theme compare
```

## Theme Page Quick Start

1. **Pick your niche**: Run `trendscraper theme compare` — recommended starting niches: **luxury, cars, finance**
2. **Set up accounts**: Create profiles on TikTok + Instagram (same username)
3. **Scrape trends daily**: `trendscraper scrape all --output daily_trends.json`
4. **Generate content calendar**: `trendscraper optimize calendar --niche luxury --platform tiktok`
5. **Optimize every caption**: `trendscraper optimize caption --platform tiktok --niche luxury`
6. **Track growth**: Re-run `trendscraper optimize account` weekly to measure progress
7. **Monetize at 5K+**: Start with shoutouts → affiliate → brand deals → page flip at 50K+

## Monetization Methods (ranked by beginner accessibility)

| Method | Start At | Difficulty | Income Potential |
|--------|----------|------------|-----------------|
| Shoutouts | 500 followers | Easy | $5-$500/post |
| Affiliate | Any size | Medium | $50-$10K/month |
| Digital Products | 2K followers | Medium | $200-$50K/month |
| Brand Deals | 10K followers | Medium | $100-$100K/post |
| Page Flipping | Any | Medium | $500-$50K/sale |
| Paid Community | 5K followers | High | $500-$20K/month |
| Newsletter | Any | High | $100-$50K/month |

## Supported Platforms

| Platform | Trending Data | Optimal Times | Hashtag Strategy |
|----------|--------------|---------------|-----------------|
| TikTok | ✅ | ✅ | ✅ |
| Instagram | ✅ (via scrape) | ✅ | ✅ |
| YouTube | ✅ (API + scrape) | ✅ | ✅ |
| Twitter/X | — | ✅ | ✅ |
| YouTube Shorts | ✅ | ✅ | ✅ |
