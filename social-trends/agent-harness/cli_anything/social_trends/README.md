# cli-anything-social-trends

Agent-native CLI for scraping YouTube & TikTok viral trends, tracking hashtags and music,
optimizing social media accounts, and building converting theme pages.

## Install

```bash
pip install -e .
```

## Quick Start

```bash
# Fetch YouTube trending videos
cli-anything-social-trends trends fetch youtube --region US --category music

# Fetch TikTok viral trends
cli-anything-social-trends trends fetch tiktok --hashtag fyp --limit 20

# Analyze trending hashtags
cli-anything-social-trends hashtags analyze --platform all --niche fitness

# Track viral music / sounds
cli-anything-social-trends music trending --platform youtube --days 7

# Optimize your account profile
cli-anything-social-trends account optimize --platform tiktok --niche gym

# Get theme page conversion strategy
cli-anything-social-trends theme-page strategy --niche travel

# Interactive REPL
cli-anything-social-trends repl
```

## Commands

| Command | Description |
|---|---|
| `trends fetch youtube` | Scrape YouTube trending videos, tags, and metadata |
| `trends fetch tiktok` | Scrape TikTok Creative Center viral content |
| `trends report` | Combined cross-platform trend report |
| `hashtags analyze` | Rank hashtags by reach, engagement, and trend velocity |
| `hashtags suggest` | Suggest optimal hashtag sets for your niche |
| `music trending` | List viral sounds/songs dominating feeds |
| `music search` | Search for a track's virality score |
| `account optimize` | Generate a full account optimization checklist |
| `account schedule` | Build an optimal posting schedule |
| `theme-page strategy` | Step-by-step theme page monetization roadmap |
| `theme-page niches` | Rank profitable theme page niches |
| `theme-page convert` | Conversion funnel templates for theme pages |
| `repl` | Interactive REPL mode |

## Requirements

- Python 3.10+
- `YOUTUBE_API_KEY` env var (optional but recommended — falls back to yt-dlp)
- No TikTok API key needed (uses Creative Center public data)
