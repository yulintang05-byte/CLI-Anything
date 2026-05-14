# ViralTrends — Tool SOP

## Overview

ViralTrends is an agent-native social media trend intelligence CLI built on the cli-anything methodology. It scrapes YouTube and TikTok for viral trends, hashtags, and music — and provides account optimization and theme page creation tools.

**Use cases:** Track viral content in real time, find trending hashtags for your niche, discover trending music/sounds, optimize posting schedules, build theme pages, and learn to convert followers into revenue.

## Backend Analysis

| Concern | Solution |
|---------|----------|
| YouTube trending | `yt-dlp --flat-playlist` against trending feed URLs |
| YouTube fallback | YouTube internal browse API (no key needed for public data) |
| TikTok trending | TikTok public discover/explore API endpoints |
| TikTok music | TikTok discover music endpoint + derivation from trending videos |
| TikTok hashtags | TikTok challenge discover endpoint + derivation |
| Cross-platform ranking | Engagement score: `(likes + 2×comments + 3×shares) / plays × 100` |
| Account optimization | Evidence-based posting schedules + hashtag strategy database |
| Theme page playbook | Niche database with CPM, monetization paths, content strategies |

## Setup

```bash
# System dependency (for YouTube scraping)
pip install yt-dlp

# Python package
cd viral-trends/agent-harness
pip install -e .

# Verify
viraltrends --help
python3 -m cli_anything.viraltrends --help
```

## Command Reference

```
viraltrends [--json] [--region REGION] COMMAND

Options:
  --json          Output machine-readable JSON
  --region TEXT   Region code: US, GB, JP, BR, etc. (default: US)

Commands:
  trends      Fetch trending videos
  hashtags    Get trending hashtags
  music       Get trending music/sounds
  niche       Filter trends by niche keywords
  account     Account optimization tools
  themepage   Theme page creation tools
```

## Workflow Examples

### Get today's viral TikTok trends
```bash
viraltrends trends tiktok --limit 20
viraltrends trends tiktok --json > tiktok_trends.json
```

### Find trending hashtags across platforms
```bash
viraltrends hashtags both --limit 20
viraltrends hashtags gaps        # Find hashtag opportunities
```

### Discover trending music for TikTok
```bash
viraltrends music tiktok --limit 20
viraltrends music youtube        # YouTube music chart
```

### Filter trends by your niche
```bash
viraltrends niche filter fitness gym workout --platform tiktok
viraltrends niche filter finance investing money --platform youtube
```

### Optimize a TikTok account
```bash
# Full optimization report
viraltrends account optimize tiktok --niche-name fitness --tz-offset -5

# Specific tools
viraltrends account schedule tiktok --tz-offset -5
viraltrends account hashtags tiktok --niche-name fitness
viraltrends account bio tiktok --niche-name "fitness tips" --value-prop "daily workouts" --cta "Free plan below"
viraltrends account audit youtube
viraltrends account calendar tiktok --niche-name fitness --posts-per-week 7
```

### Build a theme page
```bash
# Browse all niches
viraltrends themepage niches

# Research a niche
viraltrends themepage research finance
viraltrends themepage research crypto

# Get full playbook
viraltrends themepage playbook finance --platform tiktok
viraltrends themepage playbook luxury --platform instagram

# Learn to convert followers to revenue
viraltrends themepage converting

# Learn to sell accounts for profit
viraltrends themepage selling
```

### Agent workflow (JSON pipeline)
```bash
# Get trending data → pipe to analysis
viraltrends --json trends tiktok | jq '.[] | select(.plays > 1000000)'

# Get hashtags → use in content calendar
TAGS=$(viraltrends --json hashtags tiktok | jq -r '.[0:5][].tag' | tr '\n' ' ')

# Full account optimization in one shot
viraltrends --json account optimize tiktok --niche-name fitness > optimization.json
```

## Output Fields

### Trending Video (TikTok)
| Field | Description |
|-------|-------------|
| `rank` | Position in trending list |
| `platform` | `tiktok` or `youtube` |
| `id` | Platform video ID |
| `url` | Direct URL to video |
| `description` | Caption (truncated) |
| `author` | Creator handle |
| `plays` | View/play count |
| `likes` / `comments` / `shares` | Engagement counts |
| `hashtags` | Extracted hashtags |
| `music_title` / `music_author` | Trending sound info |
| `duration_sec` | Video length |

### Trending Video (YouTube)
| Field | Description |
|-------|-------------|
| `rank` | Position in trending |
| `title` | Video title |
| `channel` | Channel name |
| `views` / `likes` | Engagement |
| `hashtags` | Hashtags from title/description |
| `url` | YouTube URL |

## Theme Page Niches

| Key | Niche | Difficulty | CPM | Growth |
|-----|-------|-----------|-----|--------|
| `motivation` | Motivation/Mindset | Low | $2-8 | Fast |
| `finance` | Personal Finance | Medium | $15-40 | Medium |
| `fitness` | Fitness/Gym | Medium | $4-12 | Medium |
| `luxury` | Luxury Lifestyle | High | $8-20 | Fast |
| `animals` | Animals/Pets | Low | $1-4 | Very Fast |
| `cooking` | Food/Recipes | Low-Med | $3-10 | Med-Fast |
| `gaming` | Gaming | Med-High | $3-8 | Slow-Med |
| `fashion` | Fashion/Style | Medium | $4-15 | Med-Fast |
| `crypto` | Crypto/Web3 | High | $20-60 | Volatile |

## Known Limitations

1. **TikTok rate limiting:** TikTok aggressively rate-limits scrapers. Use `--json` and cache results.
2. **YouTube without yt-dlp:** Falls back to internal API which may return fewer fields.
3. **Region accuracy:** Trending content varies by region. Use `--region` to target your market.
4. **Music discovery:** TikTok music endpoint may return empty; falls back to derivation from trending videos.
5. **No authentication:** All data is from public endpoints only. Does not post to accounts.

## Integration with Clipper

Use ViralTrends output to drive Clipper workflows:
```bash
# Find trending music → use in your clip
viraltrends --json music tiktok | jq '.[0].title'

# Find trending hashtags → append to your TikTok export metadata
viraltrends --json hashtags tiktok > trending_tags.json
```
