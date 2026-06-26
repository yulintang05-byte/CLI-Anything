# Social Media CLI — CLI-Anything Harness

Agent-native CLI for viral trend intelligence, hashtag optimization, theme page strategy, and account optimization across TikTok, YouTube, and Instagram.

## Install

```bash
cd social-media/agent-harness
pip install -e .
# Optional live scraping:
pip install -e ".[scraping]"
```

## Commands

### Trends

```bash
# TikTok viral trends (sounds, hashtags, formats, cultural moments)
social-media trends tiktok
social-media trends tiktok --section sounds
social-media trends tiktok --live   # attempts live scrape from tokchart.com

# YouTube Shorts trends
social-media trends youtube
social-media trends youtube --section niches

# Both platforms combined
social-media trends all
```

### Hashtags

```bash
social-media hashtags fitness --platform tiktok
social-media hashtags finance --platform youtube --count 5
social-media hashtags lifestyle --platform instagram
social-media hashtags sports --no-trending
```

### Music / Audio

```bash
social-media music                         # TikTok trending sounds
social-media music --platform youtube      # YouTube audio tips
social-media music --platform both         # Both
social-media music --category dance        # Filter by category
```

### Account Optimization

```bash
# Full checklist for a platform
social-media accounts optimize tiktok --niche fitness --followers 2500
social-media accounts optimize all

# Quick audit of your account
social-media accounts audit tiktok --handle @yourhandle --followers 1200 --niche finance --bio --link
```

### Theme Pages

```bash
# Find high-converting niches
social-media themes niches
social-media themes niches -k fitness -k motivation
social-media themes niches --monetization affiliate

# Step-by-step launch guide
social-media themes setup

# Full viewer → buyer conversion funnel
social-media themes funnel --niche finance

# Weekly content calendar
social-media themes calendar --niche fitness
```

### Full Optimization Report

```bash
social-media optimize --platform tiktok --niche finance --followers 500
social-media optimize --niche fitness   # all platforms
```

### JSON Output (for AI agents)

Append `--json` to any command:

```bash
social-media --json trends tiktok | jq '.trending_sounds[0]'
social-media --json hashtags fitness | jq '.formatted'
social-media --json themes niches -k money | jq '.[0].monetization'
```

### Interactive REPL

```bash
social-media   # launches interactive REPL
```

## Environment Variables

| Variable | Purpose |
|---|---|
| `YOUTUBE_API_KEY` | Enables live YouTube Data API v3 queries |

## Architecture

```
cli_anything/social_media/
├── social_media_cli.py   # Main CLI (Click)
├── scrapers/
│   ├── tiktok.py         # TikTok trend scraper + curated June 2026 data
│   └── youtube.py        # YouTube Shorts scraper + YouTube Data API
├── core/
│   ├── accounts.py       # Account optimization playbooks (TikTok/YT/IG)
│   ├── hashtags.py       # Hashtag generation engine
│   └── theme_pages.py    # Theme page creation + conversion strategy
```
