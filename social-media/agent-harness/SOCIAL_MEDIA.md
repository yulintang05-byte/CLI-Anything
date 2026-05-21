# Social Media Agent Harness

## Overview

This harness makes social media trend intelligence and account optimization **agent-native**.
It enables AI agents (Claude Code, OpenCode, Codex, etc.) to:

1. **Scrape viral trends** from TikTok and YouTube (videos, hashtags, sounds/music)
2. **Score and optimize** social media accounts with specific, actionable recommendations
3. **Build and convert** theme pages with niche strategies, content calendars, and monetization roadmaps

## Agent Workflow

### Discover Trends → Optimize → Post

```
Agent Task: "Find what's trending in fitness on TikTok and optimize our account"

Step 1: social-media --json trends fetch --platform tiktok --region US
Step 2: social-media --json trends hashtags --platform tiktok --region US
Step 3: social-media --json account optimize --handle @fitnesscreator --platform tiktok \
          --followers 8000 --avg-views 3200 --avg-likes 280 --freq 5 --niche fitness
Step 4: Parse recommendations → generate post ideas → schedule via content calendar
```

### Full Theme Page Setup

```
Agent Task: "Set up a converting theme page in the luxury lifestyle niche"

Step 1: social-media --json theme-page analyze --niche luxury_lifestyle
Step 2: social-media --json theme-page strategy --platform tiktok
Step 3: social-media --json theme-page convert --platform tiktok --goal affiliate_clicks
Step 4: social-media --json trends sounds --region US  # Find trending audio
Step 5: Build content calendar from analysis output
```

## Quick Start for Agents

```bash
# Install
pip install -e social-media/agent-harness/

# Always use --json for machine-readable output
social-media --json trends fetch --platform all
social-media --json trends hashtags --platform tiktok
social-media --json account optimize --handle @test --platform tiktok --followers 1000
social-media --json theme-page niches
```

## Key JSON Schemas

### Account Optimize Output
```json
{
  "handle": "@myaccount",
  "platform": "tiktok",
  "score": 72,
  "max_score": 100,
  "grade": "B+",
  "engagement_rate": 4.2,
  "strengths": ["..."],
  "recommendations": ["..."],
  "best_posting_times_utc": ["07:00 UTC", "..."],
  "ideal_frequency_per_week": {"min": 7, "max": 21, "sweet_spot": 14},
  "hashtag_strategy": {"formula": "...", "tips": ["..."]},
  "growth_hacks": ["..."]
}
```

### Trending Hashtag Output
```json
{
  "tiktok": [
    {"hashtag": "#fitness", "view_count": 45000000, "video_count": 890000},
    ...
  ]
}
```

### Theme Page Niche Output
```json
{
  "niche": "luxury_lifestyle",
  "monetization": ["brand deals", "dropshipping"],
  "avg_rpm": "$8-25 CPM",
  "content_types": ["repost viral clips", "compilations"],
  "90_day_roadmap": ["..."],
  "content_calendar": {"monday": "...", ...}
}
```
