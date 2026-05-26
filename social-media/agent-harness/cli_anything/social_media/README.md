# CLI-Anything Social Media

Agent-native CLI for viral trend scraping, account optimization, and theme page strategy across TikTok, YouTube, and Instagram.

## Install

```bash
pip install -e .
```

## Commands

### Trend Scraping

```bash
# YouTube trending (no API key needed)
social-cli trends youtube --no-api --region US --max 20

# YouTube with API key (full stats)
social-cli trends youtube --api-key YOUR_KEY --category music --region US

# TikTok trending hashtags + sounds
social-cli trends tiktok --niche finance --region US --max-sounds 10

# Combined YouTube + TikTok report
social-cli trends all --niche fitness --region US

# JSON output for agent pipelines
social-cli --json trends tiktok --niche lifestyle
```

### Account Optimization

```bash
# Profile audit with score and fixes
social-cli optimize audit --platform tiktok --username mypage --followers 5000

# Phase-specific growth playbook
social-cli optimize playbook --platform tiktok --followers 8000 --niche finance

# 7-day content calendar with hooks and CTAs
social-cli optimize calendar --platform tiktok --niche motivation --posts-per-day 3

# Optimize multiple accounts from config
social-cli optimize all --config accounts.json
```

**accounts.json format:**
```json
[
  {"platform": "tiktok", "username": "mypage", "followers": 5000, "niche": "finance"},
  {"platform": "youtube", "username": "mychannel", "followers": 1200, "niche": "fitness"}
]
```

### Theme Pages

```bash
# Full blueprint: sourcing, content, monetization, timeline
social-cli theme blueprint --niche finance

# Conversion funnel strategy
social-cli theme convert --niche motivation --followers 10000 --page-type theme_page

# List available niches
social-cli theme niches
```

### Interactive REPL

```bash
social-cli repl
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key for full trending stats |

Get a free YouTube API key at: https://console.cloud.google.com → Enable "YouTube Data API v3"

## Supported Niches

`general` · `lifestyle` · `finance` · `fitness` · `food` · `motivation` · `aesthetic`

## What It Does

- **YouTube scraper**: Pulls trending videos, view counts, top hashtags, and viral music using the Data API v3 or a no-API fallback page scraper
- **TikTok scraper**: Returns curated 2025 trending sounds, hashtag sets by niche, posting schedule, viral content formats, and optional live page scrape
- **Account optimizer**: Profile audit (scored 0-100), phase-specific growth playbook (launch → growth → scale → authority), and 7-day content calendar
- **Theme page toolkit**: Niche blueprints with content sourcing rules, monetization stacks, conversion funnels, legal notes, and full growth timelines
