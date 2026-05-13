# cli-anything-social-trends

Agent-native viral trend intelligence, account optimization, and theme page strategy for YouTube and TikTok.

## What it does

- **Scrape YouTube trending** — videos, hashtags, and music via YouTube Data API v3
- **Scrape TikTok trending** — hashtags, sounds, and viral signals (live with session cookie, curated fallback)
- **Hashtag strategy** — tiered hashtag sets (mega/large/medium/niche/micro) per platform
- **Account optimization** — scoring, engagement analysis, posting time optimization
- **Content calendar** — 7-14 day calendars with video ideas, hooks, sounds, and hashtags
- **Theme page playbook** — 10 niche strategies, 30-day action plans, monetization roadmaps, conversion funnels

## Install

```bash
pip install -e .
```

## Quick start

```bash
# Set YouTube API key (free at console.cloud.google.com)
social-trends config set --youtube-key YOUR_KEY

# Fetch YouTube trending
social-trends trends fetch youtube --region US --category entertainment

# Fetch TikTok trending (no key needed)
social-trends trends fetch tiktok

# Build hashtag strategy
social-trends hashtags strategy --niche finance --platform tiktok

# Generate 2-week content calendar
social-trends calendar generate --niche finance --weeks 2

# Explore theme page niches
social-trends theme-page niches
social-trends theme-page strategy --niche ai-tools
social-trends theme-page roadmap
social-trends theme-page conversion
```

## API keys

| Platform | Key | Get it |
|----------|-----|--------|
| YouTube | YouTube Data API v3 | console.cloud.google.com (free, 10K units/day) |
| TikTok | sessionid cookie | Optional — curated data works without it |

Store once: `social-trends config set --youtube-key AIza...`
