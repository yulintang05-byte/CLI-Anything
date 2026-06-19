# cli-anything-trends

Viral trend scraper and account optimizer for YouTube and TikTok.  
Scrapes trending videos, hashtags, music, and sounds — then generates platform-specific account optimization guides, hashtag packs, and content calendars.

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Interactive setup
cli-anything-trends config setup

# YouTube trending (requires API key)
cli-anything-trends trends youtube --region US --category music

# TikTok trending (cookie-based or public)
cli-anything-trends trends tiktok --region US

# Full cross-platform report
cli-anything-trends trends report --niche fitness --region US

# Account optimization guide
cli-anything-trends trends optimize --platform tiktok --niche fitness --followers 5000

# 2-week content calendar
cli-anything-trends trends calendar --niche lifestyle --weeks 2

# Hashtag packs (all platforms)
cli-anything-trends trends hashtags --platform all --niche fitness

# JSON output (pipe-friendly)
cli-anything-trends --json trends report --niche gaming
```

## Authentication

### YouTube Data API v3 (Required for YouTube)

1. Go to https://console.cloud.google.com
2. Create project → Enable "YouTube Data API v3"
3. Create API Key credential
4. Set key: `cli-anything-trends config set youtube_api_key <key>`  
   Or: `export YOUTUBE_API_KEY=<key>`

### TikTok (3 options, priority order)

**Option A — TikTok Research API** (most data, requires approval)
```bash
# Apply at: https://developers.tiktok.com/products/research-api/
cli-anything-trends config set tiktok_api_key <access_token>
```

**Option B — Browser Cookies** (good data, self-service)
1. Open TikTok in Chrome → Login
2. DevTools → Application → Cookies → `www.tiktok.com`
3. Copy `sessionid`, `ttwid`, `tt_webid` values
4. `cli-anything-trends config set tiktok_cookies "sessionid=xxx; ttwid=yyy"`

**Option C — Public Scrape** (limited, no auth needed)  
No setup needed — falls back automatically.

## Commands

```
trends youtube     Fetch YouTube trending by region/category
trends tiktok      Fetch TikTok trending (sounds, videos, hashtags)
trends music       Trending music from YouTube + TikTok sounds
trends hashtags    Ranked hashtag packs across platforms
trends report      Full cross-platform trend intelligence report
trends optimize    Account optimization guide (bio, posting, growth)
trends calendar    2-week content calendar with posting times
trends hashtag-info <tag>  Stats for a specific TikTok hashtag

config setup       Interactive API key wizard
config set         Set a config value
config get         Get config values
config delete      Remove a config value

session history    View command history
session undo/redo  Undo/redo last command
```

## Regions

`US` `GB` `CA` `AU` `DE` `FR` `JP` `KR` `BR` `IN` `MX` `IT`

## Categories (YouTube)

`all` `music` `gaming` `entertainment` `news` `howto` `sports` `film` `comedy` `science`
