# Social Media CLI — Harness Overview

Agent-native CLI harness for social media trend intelligence, account optimization, and theme page building.

## What It Does

| Command Group | Purpose |
|---|---|
| `trends youtube` | Scrape YouTube trending videos, hashtags, view counts |
| `trends tiktok` | Scrape TikTok trending hashtags, sounds, and videos |
| `trends music` | Aggregate trending music across both platforms |
| `trends hashtags` | Cross-platform hashtag aggregation with niche filtering |
| `optimize profile` | Profile bio, format, and SEO optimization checklist |
| `optimize hashtags` | Generate optimized hashtag sets (30% mega / 40% mid / 30% niche) |
| `optimize strategy` | Full content strategy: pillars, hooks, weekly calendar, KPIs |
| `optimize schedule` | Best posting windows by platform and timezone |
| `theme-page evaluate` | Score a niche: competition, CPM, monetization potential |
| `theme-page playbook` | Complete 90-day theme page build playbook |
| `theme-page monetize` | All monetization methods with setup guides |
| `theme-page convert` | Convert personal/blank accounts to theme pages |

## Installation

```bash
cd social-media/agent-harness && pip install -e .
```

## Agent Usage

```bash
# Get structured JSON for any command
social-media --json trends hashtags --platform all --niche fitness

# Full trend dump
social-media --json trends all --region US

# Generate hashtags ready to paste
social-media --json optimize hashtags --niche luxury --platform tiktok
```

## No API Keys Needed

Scrapes publicly available data from YouTube (`ytInitialData` page parsing)
and TikTok (discover page + recommendation endpoint). Data cached for 1h at
`~/.cli_anything/social_media_cache/`.
