# cli-anything-social-trends

Viral trend intelligence CLI for YouTube & TikTok — scrape trending videos,
analyze hashtags and sounds, optimize your accounts, and build monetizing theme pages.

## Install

```bash
pip install -e .
# With TikTokApi support (playwright-based):
pip install -e ".[tiktok]"
playwright install chromium
```

## Quick Start

```bash
# YouTube trending videos
social-trends youtube trending --category music --region US

# TikTok trending with hashtags + sounds
social-trends tiktok trending --limit 30 --hashtags --sounds

# Generate optimized hashtag set
social-trends hashtags generate --topic fitness --platform tiktok --strategy balanced

# Analyze trending sounds across platforms
social-trends music analyze --niche fitness

# Audit your account
social-trends account audit --platform tiktok --handle @yourhandle

# Generate 4-week content calendar
social-trends account calendar --niche beauty --platform tiktok --weeks 4

# Get growth recommendations
social-trends account grow --platform tiktok --niche fitness --followers 5000 --avg-views 300 --posts-per-week 3

# Theme page playbook
social-trends theme playbook --niche motivation --platform tiktok

# Niche opportunity ranking
social-trends theme niches

# Theme page → business conversion guide
social-trends theme convert

# Interactive REPL
social-trends repl

# JSON output (pipe to jq)
social-trends --json hashtags generate --topic cars | jq '.tags'
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Optional (improves data quality) |
| `TIKTOK_CLIENT_KEY` | TikTok Research API client key | Optional |
| `TIKTOK_CLIENT_SECRET` | TikTok Research API client secret | Optional |
| `TIKTOK_MS_TOKEN` | TikTok session token for TikTokApi | Optional |

Without credentials, the CLI falls back to InnerTube (YouTube) and public
endpoints (TikTok) — data quality is lower but no keys are required.

## Command Reference

### `youtube`
| Command | Description |
|---------|-------------|
| `youtube trending` | Trending videos by category and region |
| `youtube hashtags` | Hashtags aggregated from trending videos |

### `tiktok`
| Command | Description |
|---------|-------------|
| `tiktok trending` | Trending TikTok videos |
| `tiktok sounds` | Trending sounds/audio |

### `hashtags`
| Command | Description |
|---------|-------------|
| `hashtags generate` | Generate optimized hashtag set for a topic |
| `hashtags niches` | List all supported niche categories |
| `hashtags merge` | Cross-platform hashtag ranking |

### `music`
| Command | Description |
|---------|-------------|
| `music analyze` | Sound trend intelligence + strategy guide |

### `account`
| Command | Description |
|---------|-------------|
| `account audit` | Self-assessment checklist with score + action items |
| `account schedule` | Optimal posting times for a platform |
| `account calendar` | Auto-generated content calendar (1–12 weeks) |
| `account grow` | Personalized growth diagnoses + 30-day action plan |

### `theme`
| Command | Description |
|---------|-------------|
| `theme playbook` | Complete theme page playbook for a niche |
| `theme niches` | Rank niches by monetization potential |
| `theme convert` | Guide: theme page → real business |
