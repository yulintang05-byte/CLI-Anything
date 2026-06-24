# cli-anything-social-trends

CLI harness for social media trend research, account optimization, and theme page monetization.

## Features

- **YouTube Trends** — Fetch trending videos, extract hashtags, find viral music (YouTube Data API v3)
- **TikTok Trends** — Niche hashtag research, optimal mix generator, trending sound discovery, content ideas
- **Account Optimizer** — Bio scoring, weekly posting schedules, 30-day action plans, growth stage analysis
- **Theme Pages** — Complete creation blueprints, monetization deep-dives, conversion funnel, scaling system

## Quick Start

```bash
pip install -e .

# Setup YouTube API (free key from console.developers.google.com)
cli-anything-social config setup-youtube --key YOUR_API_KEY

# Get YouTube trending videos
cli-anything-social trends youtube --region US --category music

# Research TikTok trends for your niche
cli-anything-social trends tiktok --niche fitness --sounds

# Get optimal hashtag mix (ready to paste)
cli-anything-social hashtags mix --niche motivation

# Full account audit with 30-day plan
cli-anything-social account optimize --platform tiktok --handle @mypage --niche motivation --followers 2500

# Theme page blueprint
cli-anything-social theme blueprint --niche finance_wealth

# Monetization strategy
cli-anything-social theme monetize --method affiliate_marketing

# Interactive mode
cli-anything-social repl
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `trends youtube` | YouTube trending videos by region/category |
| `trends tiktok` | TikTok trend report for a niche |
| `trends music` | Trending TikTok sounds/music |
| `hashtags niche` | Hashtags ranked for a niche |
| `hashtags mix` | Ready-to-paste optimal 5-7 tag mix |
| `hashtags youtube` | Hashtags extracted from YouTube trending |
| `account add` | Register an account to track |
| `account optimize` | Full account audit + action plan |
| `account schedule` | Weekly posting schedule |
| `account bio-score` | Score and improve your bio |
| `theme blueprint` | Complete theme page setup guide |
| `theme monetize` | Deep-dive monetization strategies |
| `theme funnel` | 5-stage conversion funnel |
| `theme scale` | Multi-page scaling system |
| `config setup-youtube` | Save YouTube API key |
| `config setup-tiktok` | Save TikTok session token |

## Requirements

- Python 3.10+
- `google-api-python-client` + `isodate` (for YouTube features)
- Optional: `TikTokApi` + `playwright` (for live TikTok data)
- YouTube Data API v3 key (free, 10,000 units/day quota)
