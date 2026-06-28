# cli-anything-social-trends

Agent-native CLI harness for viral trend discovery on YouTube and TikTok. Fetches trending videos, extracts hashtags and music, manages social media accounts, generates content calendars, and provides complete theme page strategy guides.

## Install

```bash
pip install cli-anything-social-trends
pip install yt-dlp  # required for live trend fetching
```

## Quick Start

```bash
# Create a project
social-trends project new "my-brand"
social-trends project save my-brand.json

# Fetch trending content (requires yt-dlp)
social-trends trends fetch --platform both --category fitness --region US

# Generate hashtag set for TikTok
social-trends hashtags generate-set fitness --platform tiktok --mix balanced

# Get trending music
social-trends music trending --platform tiktok

# Add and optimize an account
social-trends accounts add "Main TikTok" --platform tiktok --handle myhandle --niche fitness
social-trends accounts stats myhandle --platform tiktok --followers 5000 --posts 30 --avg-views 1000
social-trends accounts optimize myhandle --platform tiktok

# Generate 4-week content calendar
social-trends calendar generate --platform tiktok --niche fitness --weeks 4

# Theme page strategy
social-trends theme-page guide
social-trends theme-page strategy luxury_lifestyle
social-trends theme-page niches
```

## YouTube API Key (Optional but Recommended)

Without an API key, YouTube trends are fetched via yt-dlp. With a key, you get richer metadata:

```bash
social-trends project set-config youtube_api_key YOUR_KEY_HERE
```

Get a free key at [console.developers.google.com](https://console.developers.google.com).

## Commands

| Group | Command | Description |
|-------|---------|-------------|
| `project` | `new NAME` | Create project |
| `project` | `open PATH` | Open saved project |
| `project` | `set-config KEY VALUE` | Set config (API key, region, niche) |
| `trends` | `fetch` | Fetch live trends from YouTube/TikTok |
| `trends` | `list` | List cached trends |
| `trends` | `search QUERY` | Search trends by keyword |
| `trends` | `top` | Top trends by view count |
| `trends` | `extract-hashtags` | Pull all hashtags from cached trends |
| `hashtags` | `research TOPIC` | Research hashtags for a topic |
| `hashtags` | `score TAG` | Score a hashtag's competitiveness |
| `hashtags` | `generate-set NICHE` | Generate a ready-to-use hashtag set |
| `music` | `trending` | Fetch trending sounds |
| `music` | `recommend NICHE` | Recommend music for a niche |
| `accounts` | `add NAME` | Add an account |
| `accounts` | `optimize HANDLE` | Full optimization report |
| `theme-page` | `guide` | Complete theme page guide |
| `theme-page` | `strategy NICHE` | Strategy for a specific niche |
| `theme-page` | `niches` | List all supported niches |
| `calendar` | `generate` | Generate content calendar |
| `calendar` | `view` | Browse calendar entries |
| `calendar` | `export` | Export as JSON/CSV/text |

## JSON Mode

All commands support `--json` for agent-compatible output:

```bash
social-trends --json trends fetch --platform tiktok
```
