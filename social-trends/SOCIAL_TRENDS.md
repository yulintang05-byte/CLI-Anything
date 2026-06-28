# Social Trends — CLI Harness SOP

## Tool Purpose

`cli-anything-social-trends` is an agent-native CLI harness for viral trend discovery on YouTube and TikTok. It enables AI agents (Claude Code, OpenCode, Codex) and humans to:

- Fetch trending videos from YouTube (via yt-dlp or official Data API) and TikTok (via yt-dlp)
- Extract hashtags and music from trending content
- Research and generate platform-optimized hashtag sets
- Manage social media accounts and generate optimization reports
- Build 4-8 week content calendars with trend-informed suggestions
- Learn theme page strategy: niche selection, content pillars, converting visitors to revenue

## Prerequisites

```bash
pip install cli-anything-social-trends
pip install yt-dlp          # for live trend fetching
```

Optional:
```bash
# For richer YouTube metadata
social-trends project set-config youtube_api_key YOUR_KEY
```

## Command Reference

### Project Management
```bash
social-trends project new "brand-name"
social-trends project open project.json
social-trends project set-config youtube_api_key KEY
social-trends session save project.json
```

### Trend Fetching
```bash
# Fetch from both platforms
social-trends trends fetch --platform both --category fitness --region US --limit 20

# Available categories: all, music, gaming, entertainment, fitness, beauty, travel, food, fashion, sports
# Available regions: US, GB, CA, AU, IN, DE, FR, BR, JP, KR, ...

# List cached trends
social-trends trends list --platform tiktok
social-trends trends top --n 10
social-trends trends search "workout"
social-trends trends extract-hashtags
```

### Hashtag Research
```bash
# Research hashtags for a niche
social-trends hashtags research fitness --platform tiktok --limit 30

# Score a specific hashtag
social-trends hashtags score "#fitness"

# Generate a ready-to-use set (copies directly to caption)
social-trends hashtags generate-set fitness --platform tiktok --mix balanced
social-trends hashtags generate-set beauty --platform instagram --mix safe
social-trends hashtags list
```

### Trending Music
```bash
social-trends music trending --platform tiktok --limit 20
social-trends music recommend fitness --platform tiktok
social-trends music search "lofi"
social-trends music list
```

### Account Optimization
```bash
# Add accounts
social-trends accounts add "Main TikTok" --platform tiktok --handle myhandle --niche fitness
social-trends accounts add "YT Channel" --platform youtube --handle mychannel --niche gaming

# Update stats
social-trends accounts stats myhandle --platform tiktok \
  --followers 10000 --posts 50 --avg-views 5000 --avg-likes 300 --avg-comments 20

# Get full optimization report (A-F grade + actionable tips)
social-trends accounts optimize myhandle --platform tiktok
social-trends accounts list
```

### Theme Page Strategy
```bash
# Full step-by-step converting guide
social-trends theme-page guide

# Browse niches
social-trends theme-page niches

# Deep strategy for a niche
social-trends theme-page strategy luxury_lifestyle
social-trends theme-page strategy finance_money --monetization affiliate

# Content pillars breakdown
social-trends theme-page content-pillars fitness

# Posting schedule
social-trends theme-page posting-schedule gaming --platform tiktok
```

### Content Calendar
```bash
# Generate 4-week calendar
social-trends calendar generate --platform tiktok --niche fitness --weeks 4 --posts-per-day 2

# View and filter
social-trends calendar view --platform tiktok --status planned --week 0

# Add manual entry
social-trends calendar add --date 2025-07-01 --platform tiktok \
  --type trending_repost --title "Viral gym clip" --niche fitness

# Mark as posted
social-trends calendar update-status ENTRY_ID posted

# Export
social-trends calendar export --format csv > schedule.csv
social-trends calendar export --format text
```

## JSON Mode (Agent Use)

All commands support `--json` flag for structured output:

```bash
social-trends --json trends fetch --platform tiktok
social-trends --json hashtags generate-set fitness
social-trends --json accounts optimize myhandle --platform tiktok
social-trends --json calendar generate --platform tiktok --niche fitness
```

## Supported Niches (Theme Pages)

| Key | Label | Difficulty | Revenue Potential |
|-----|-------|------------|-------------------|
| `luxury_lifestyle` | Luxury Lifestyle | Easy | Very High |
| `motivation` | Motivation & Success | Easy | High |
| `fitness` | Fitness & Health | Medium | Very High |
| `finance_money` | Finance & Money | Medium | Very High |
| `dark_humor` | Dark Humor & Memes | Easy | Medium |
| `travel` | Travel & Adventure | Hard | High |
| `gaming` | Gaming Highlights | Easy | High |
| `beauty_makeup` | Beauty & Makeup | Medium | Very High |
| `pets_animals` | Pets & Animals | Very Easy | Medium |

## Architecture

```
social-trends/
└── agent-harness/
    └── cli_anything/
        └── social_trends/
            ├── social_trends_cli.py   # Click CLI entry point
            ├── core/
            │   ├── session.py         # State + undo/redo
            │   ├── project.py         # Project management
            │   ├── trends.py          # Trend fetching + cache
            │   ├── hashtags.py        # Hashtag research + sets
            │   ├── music.py           # Sound discovery
            │   ├── accounts.py        # Account optimization
            │   ├── theme_pages.py     # Theme page strategy
            │   └── content_calendar.py # Calendar generation
            ├── utils/
            │   ├── youtube_backend.py  # YouTube API + yt-dlp
            │   ├── tiktok_backend.py   # TikTok via yt-dlp
            │   └── repl_skin.py        # Interactive REPL
            └── tests/
                ├── test_core.py        # Unit tests (~100)
                └── test_full_e2e.py    # CLI + subprocess tests (~90)
```
