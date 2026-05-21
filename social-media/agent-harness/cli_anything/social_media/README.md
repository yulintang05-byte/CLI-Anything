# Social Media CLI

An agent-native CLI for viral trend scraping, account optimization, and theme page conversion — built on the CLI-Anything framework.

## What It Does

| Command Group | What It Does |
|---|---|
| `trends fetch` | Scrapes trending videos from TikTok & YouTube |
| `trends hashtags` | Gets trending hashtags by platform and region |
| `trends sounds` | Gets trending TikTok sounds + YouTube music |
| `trends niche` | Digs into top videos for a specific hashtag |
| `account optimize` | Scores your account and gives specific recommendations |
| `account batch` | Analyzes multiple accounts at once from JSON |
| `theme-page niches` | Lists all proven niches with monetization data |
| `theme-page analyze` | Deep-dives a niche with 90-day roadmap |
| `theme-page strategy` | Full growth + posting strategy per platform |
| `theme-page convert` | Conversion tactics for sales, follows, affiliates |

## Prerequisites

- Python 3.10+
- `requests` and `click` (installed automatically)

**Optional but recommended:**
- YouTube Data API v3 key — for deeper trend data (free tier: 10,000 units/day)
- TikTok session ID — for authenticated trend access (higher rate limits)

## Install

```bash
cd social-media/agent-harness
pip install -e .
```

## Configure

```bash
# YouTube Data API v3 key (get from console.cloud.google.com)
social-media config set youtube_api_key YOUR_API_KEY

# TikTok session ID (from browser cookies — sessionid field)
social-media config set tiktok_session_id YOUR_SESSION_ID

# Or use environment variables
export YOUTUBE_API_KEY=YOUR_API_KEY
export TIKTOK_SESSION_ID=YOUR_SESSION_ID
```

## Examples

```bash
# Get trending content across all platforms
social-media trends fetch --platform all --region US

# Get TikTok trending hashtags for the UK
social-media trends hashtags --platform tiktok --region GB --limit 50

# Get trending sounds
social-media trends sounds --region US

# Dig into a niche hashtag
social-media trends niche fitness

# Analyze your TikTok account
social-media account optimize \
  --handle @mycreator \
  --platform tiktok \
  --followers 12500 \
  --avg-views 8400 \
  --avg-likes 620 \
  --avg-comments 45 \
  --freq 7 \
  --niche "fitness motivation" \
  --bio "Daily workout content | 5 free programs in bio"

# Get all niches with monetization data
social-media theme-page niches

# Deep-dive a niche
social-media theme-page analyze --niche luxury_lifestyle

# Get TikTok growth strategy
social-media theme-page strategy --platform tiktok

# Get conversion tactics for affiliate sales
social-media theme-page convert \
  --platform tiktok \
  --goal affiliate_clicks \
  --current-rate 1.2

# Output everything as JSON (for agents)
social-media --json trends hashtags --platform tiktok
```

## Supported Niches

luxury_lifestyle, fitness_motivation, finance_money, pets, food,
relationships, tech, mindset_motivation, beauty_fashion, travel

## Notes on Scraping

- TikTok and YouTube update their page structures. If scraping fails, use the API key path.
- TikTok's `sessionid` cookie is found in browser DevTools → Application → Cookies → tiktok.com.
- YouTube Data API v3 is free for 10,000 quota units/day (each trending fetch = ~1-3 units).
