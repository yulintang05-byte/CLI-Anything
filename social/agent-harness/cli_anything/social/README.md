# cli-anything-social

Social media CLI — viral trend scraping, account optimisation, and theme page conversion playbooks.

## Install

```bash
pip install -e .
```

## Quickstart

```bash
# Set credentials (recommended — avoids passing flags every time)
export YOUTUBE_API_KEY="AIza..."
export TIKTOK_SESSION="your_sessionid_cookie"

# Scrape YouTube trending
cli-anything-social trends youtube --yt-key $YOUTUBE_API_KEY

# Scrape TikTok trending hashtags
cli-anything-social trends tiktok-hashtags --tt-session $TIKTOK_SESSION

# Cross-platform trend report + recommendations
cli-anything-social trends all

# Audit a TikTok account
cli-anything-social account audit-tiktok @username

# Get optimised bio templates
cli-anything-social account bio --platform tiktok --niche fitness

# Theme page playbook (finance on TikTok → 50K followers)
cli-anything-social theme playbook --niche finance --platform tiktok --goal 50000

# Content calendar (4 weeks)
cli-anything-social schedule calendar --platform tiktok --niche fitness --weeks 4

# Interactive REPL
cli-anything-social repl
```

## Commands

| Group | Command | Description |
|-------|---------|-------------|
| `trends` | `youtube` | Fetch trending YouTube videos, hashtags, topics |
| `trends` | `youtube-search` | Search YouTube for a keyword |
| `trends` | `tiktok-hashtags` | Fetch trending TikTok hashtags |
| `trends` | `tiktok-music` | Fetch trending TikTok sounds |
| `trends` | `tiktok-feed` | Fetch TikTok FYP trending videos |
| `trends` | `all` | Cross-platform trends + recommendations |
| `trends` | `extract-hashtags` | Extract hashtags from any text |
| `account` | `audit-youtube` | Full YouTube channel audit |
| `account` | `audit-tiktok` | Full TikTok account audit |
| `account` | `bio` | Generate optimised bio templates |
| `account` | `hashtags` | Tiered hashtag strategy |
| `account` | `post-times` | Optimal posting times and days |
| `theme` | `niches` | List all niches with key metrics |
| `theme` | `analyse` | Deep niche analysis + opportunity score |
| `theme` | `monetise` | Ranked monetisation strategies |
| `theme` | `revenue` | Monthly revenue estimates |
| `theme` | `playbook` | Phased theme page launch playbook |
| `theme` | `valuation` | Account flip / sale valuation |
| `schedule` | `calendar` | Generate content calendar |
| `schedule` | `frequency` | Posting frequency advice |
| `schedule` | `hooks` | Content hook templates |
| `schedule` | `repurpose` | Cross-platform repurposing plan |

## Getting Credentials

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable "YouTube Data API v3"
3. Create an API key → copy it
4. Free tier: 10,000 units/day (~100 trending requests)

### TikTok Session Cookie
1. Open TikTok web in Chrome → log in
2. Open DevTools → Application → Cookies → www.tiktok.com
3. Find `sessionid` → copy the value
4. Session expires after ~30 days

## Supported Niches

fitness · finance · luxury · motivation · food · travel · pets · gaming · beauty · crypto

## Tests

```bash
# Offline tests (no credentials needed)
PYTHONPATH=. pytest tests/test_core.py -v

# E2E tests (requires credentials)
YOUTUBE_API_KEY=... TIKTOK_SESSION=... pytest tests/test_full_e2e.py -v
```
