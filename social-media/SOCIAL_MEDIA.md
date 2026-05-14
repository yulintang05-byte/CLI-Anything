# Social Media — Agent-Native Growth Tool

## Overview

`socials` is a CLI harness that makes social media research and growth strategy
fully agent-controllable. It covers the full growth stack:

| Capability | What it does |
|---|---|
| **Trend scraping** | Fetch viral YouTube/TikTok content (official API + public endpoints) |
| **Hashtag research** | Build optimized tag sets, score difficulty, fetch trending tags |
| **Music/sounds** | Trending TikTok sounds + YouTube music + posting time windows |
| **Account optimization** | Bio scoring, content plans, growth playbooks |
| **Theme pages** | Niche blueprints, conversion roadmaps, page acquisition guide |

## Setup

```bash
cd social-media/agent-harness
pip install -e .

# Optional — enables YouTube Data API (free, 10K queries/day)
export YOUTUBE_API_KEY="your_key_here"
```

Get a free YouTube API key at https://console.cloud.google.com/ → Enable "YouTube Data API v3".

## Quick Start

```bash
# Fetch today's TikTok viral trends (no API key needed)
socials trends tiktok --region US --limit 20

# Fetch YouTube trending (no API key — scrapes public page)
socials trends youtube --region US --category all

# Fetch BOTH platforms at once
socials trends all --region US --limit 15

# Get trending TikTok sounds right now
socials music trending --platform tiktok --period 7

# Best times to post on TikTok
socials music times tiktok --region US

# Build hashtag set for fitness niche
socials hashtags build fitness --strategy balanced --max-tags 25

# Research a specific hashtag
socials hashtags research "#gymtok" --platform tiktok

# Score your existing hashtag set
socials hashtags score "#fyp" "#fitness" "#gymtok" "#workout" "#gains"

# Audit your TikTok account
socials account audit tiktok @yourhandle \
  --bio "Daily gym motivation 💪" \
  --posts-per-week 3 \
  --followers 1200 \
  --avg-views 800 \
  --uses-hashtags

# Get bio templates for Instagram
socials account bio-guide instagram

# Score your bio
socials account score-bio tiktok "💪 Fitness tips daily | Helping you hit your goals | 👇 Free workout plan"

# Weekly content plan
socials account content-plan fitness --platform tiktok --posts-per-week 7

# Growth playbook for your stage
socials account playbook --followers 5000

# List all theme page niches
socials theme-pages list

# Full blueprint for a fitness theme page
socials theme-pages blueprint fitness

# Niche recommendations based on your interests
socials theme-pages recommend --interests fitness motivation --risk medium

# Theme page conversion roadmap
socials theme-pages roadmap

# What to do at your follower count
socials theme-pages stage 8500

# Guide to buying existing theme pages
socials theme-pages acquire
```

## JSON Output (Agent Mode)

All commands output structured JSON by default — optimized for agent parsing:

```bash
socials trends tiktok --region US --limit 5
```
```json
{
  "platform": "tiktok",
  "region": "US",
  "category": "viral",
  "fetched_at": "2026-05-14T13:00:00Z",
  "count": 5,
  "trends": [
    {
      "rank": 1,
      "title": "POV: you finally started...",
      "platform": "tiktok",
      "url": "https://www.tiktok.com/@creator/video/123",
      "views": 4200000,
      "likes": 380000,
      "hashtags": ["#fyp", "#motivation"],
      "music": "original sound - creator",
      "creator": "creator_handle"
    }
  ]
}
```

## Human-Readable Mode

Add `--human` before any subcommand for pretty-printed output:

```bash
socials --human theme-pages blueprint motivation
socials --human account playbook --stage 1k_to_10k
```

## Interactive REPL

```bash
socials repl
socials> trends tiktok --limit 10
socials> hashtags build fitness --strategy balanced
socials> theme-pages blueprint motivation
socials> exit
```

## Architecture

```
social-media/agent-harness/
├── setup.py
└── cli_anything/social_media/
    ├── __init__.py
    ├── cli.py           ← Click CLI entry point (all subcommands)
    ├── trends.py        ← YouTube Data API + TikTok public scraper
    ├── hashtags.py      ← TikTok Creative Center + niche seed sets
    ├── music.py         ← Trending sounds + posting time windows
    ├── account.py       ← Bio scoring + content plans + growth playbooks
    └── theme_pages.py   ← Niche blueprints + conversion roadmap + acquisition guide
```

## API Key Notes

| Platform | Endpoint | Auth Required? |
|---|---|---|
| YouTube trending | YouTube Data API v3 | Optional (falls back to page scraping) |
| TikTok hashtags | TikTok Creative Center | None (public) |
| TikTok sounds | TikTok Creative Center | None (public) |
| TikTok videos | TikTok web scraping | None (rate-limited) |
| Instagram hashtags | None (estimated) | N/A |

**TikTok ToS note:** TikTok's Creative Center endpoints are publicly accessible and used
by TikTok's own business dashboard. Direct video scraping is used for research purposes
only — always credit original creators and comply with TikTok's community guidelines.

## Environment Variables

| Variable | Used by | Description |
|---|---|---|
| `YOUTUBE_API_KEY` | `trends youtube`, `music trending` | YouTube Data API v3 key |

## Running Tests

```bash
cd social-media/agent-harness
pip install -e ".[dev]"
pytest tests/ -v
```
