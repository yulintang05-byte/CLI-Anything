# CLI-Anything Social Media

Agent-native CLI for viral trend scraping, hashtag optimization, account growth, and theme page conversion.

## Features

- **YouTube + TikTok Trend Scraping** — Fetches trending videos, hashtags, and music in real-time
- **Cross-Platform Trend Analysis** — Aggregates viral signals across platforms with actionable insights
- **Hashtag Optimizer** — Generates niche-specific hashtag sets with reach scoring for TikTok, Instagram, YouTube
- **Trending Music/Sounds** — Identifies viral sounds to boost algorithmic reach
- **Account Optimizer** — Full optimization reports: bio, posting schedule, hooks, monetization roadmap
- **Theme Page Conversion Guide** — Complete 5-stage funnel from follower to paying customer
- **DM Automation Scripts** — Ready-to-use DM templates for follower conversion

## Quick Start

```bash
# Fetch viral trends from both platforms
python -m cli_anything.social_media trends fetch --platforms tiktok,youtube --country US

# Analyze cross-platform insights
python -m cli_anything.social_media trends analyze

# Generate hashtags for your niche
python -m cli_anything.social_media hashtags generate --niche finance --platform tiktok

# Score your existing hashtags
python -m cli_anything.social_media hashtags score "#fyp #money #investing" --platform tiktok

# Get trending music
python -m cli_anything.social_media music trending --platform tiktok

# Add and optimize an account
python -m cli_anything.social_media account add myhandle tiktok finance --followers 5000 --bio "Money tips for gen z 💰 Link below ↓"
python -m cli_anything.social_media account optimize myhandle

# Theme page conversion guide
python -m cli_anything.social_media theme-page guide --niche finance
python -m cli_anything.social_media theme-page niches

# Interactive REPL
python -m cli_anything.social_media repl
```

## Output Formats

All commands support `--json` for machine-readable output:

```bash
python -m cli_anything.social_media --json trends fetch | jq '.data.tiktok.trending_sounds'
```

## Commands

| Group | Commands |
|-------|----------|
| `project` | `new`, `open`, `save`, `info`, `json` |
| `trends` | `fetch`, `analyze`, `latest`, `history` |
| `hashtags` | `generate`, `score`, `list`, `niches` |
| `music` | `trending`, `recommend`, `categories` |
| `account` | `add`, `remove`, `list`, `optimize`, `score`, `update`, `schedule` |
| `theme-page` | `guide`, `niches`, `niche`, `funnel`, `dm-scripts` |
| `session` | `status`, `undo`, `redo`, `history` |
