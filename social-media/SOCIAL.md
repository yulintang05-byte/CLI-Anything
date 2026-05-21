# Social Media Intelligence CLI — Tool SOP

## Overview

`social` is an agent-native CLI harness for social media intelligence. It scrapes viral trends from YouTube and TikTok, researches hashtag strategies, tracks trending music/sounds, generates account optimization plans, and provides a complete theme page creation playbook — all with structured JSON output for agent consumption.

**Platforms covered:** TikTok, Instagram, YouTube, Twitter/X

## Backend Analysis

| Concern | Solution |
|---------|----------|
| YouTube trending (no key) | Parse `ytInitialData` JSON from `youtube.com/feed/trending` |
| YouTube trending (with key) | YouTube Data API v3 `videos.list?chart=mostPopular` |
| TikTok hashtag trends | TikTok Creative Center public API (no auth required) |
| TikTok music trends | TikTok Creative Center public API (no auth required) |
| Hashtag strategy | Curated niche bank + platform-specific rules engine |
| Account optimization | Evidence-based framework from creator economy research |
| Theme page guide | Full static playbook with phased roadmap |
| Output | JSON (default) or plain-text table via `--output` flag |

## Setup

```bash
# System dependency: Python 3.10+ and pip
cd social-media/agent-harness
pip install -e .

# Optional: YouTube Data API key for higher rate limits
export YOUTUBE_API_KEY="your_key_here"

# Verify
social --help
social trends youtube --limit 5
```

## Command Reference

### Trends

```bash
# YouTube trending (scrapes if no API key, uses API if YOUTUBE_API_KEY set)
social trends youtube --region US --category all --limit 20
social trends youtube --category music --output json

# TikTok trending hashtags (no auth required)
social trends tiktok --region US --period 7 --limit 30

# Trending music on TikTok and YouTube
social trends music --platform all --region US --limit 20

# Full cross-platform trend report (JSON)
social trends report --region US --limit 10
```

### Hashtags

```bash
# Research hashtag strategy for a niche
social hashtags research fitness --platform tiktok
social hashtags research finance --platform instagram --limit 20

# Score a single hashtag
social hashtags score "#fitness"
social hashtags score bodybuilding

# List all available niches
social hashtags niches
```

### Accounts

```bash
# Full optimization plan for a platform + stage
social accounts optimize --platform tiktok --niche fitness --stage growing
social accounts optimize --platform youtube --stage new_account

# Account audit checklist
social accounts audit @myhandle --platform instagram

# Track accounts in session
social accounts add --platform tiktok --handle @myaccount --niche finance
social accounts list --platform tiktok
```

### Theme Pages

```bash
# Full theme page creation and monetization playbook
social theme-pages guide
social theme-pages guide --niche "Luxury Lifestyle"

# List top converting theme page niches
social theme-pages niches
social theme-pages niches --output json
```

## Key Workflows

### Daily Trend Monitoring

```bash
# Morning routine: full trend snapshot
social trends report --region US --limit 15 > trends_$(date +%Y%m%d).json

# Check top TikTok hashtags
social trends tiktok --region US --limit 20

# Check trending music for content creation
social trends music --platform tiktok --limit 10
```

### New Account Launch

```bash
# 1. Choose niche
social hashtags niches

# 2. Get full optimization plan
social accounts optimize --platform tiktok --niche fitness --stage new_account

# 3. Get hashtag strategy
social hashtags research fitness --platform tiktok

# 4. Start tracking the account
social accounts add --platform tiktok --handle @myfitnesspage --niche fitness
```

### Theme Page Research

```bash
# Discover best niches
social theme-pages niches

# Get full playbook for a niche
social theme-pages guide --niche finance

# Get competing hashtag strategy
social hashtags research finance --platform tiktok
social hashtags research finance --platform instagram
```

### Content Strategy for Existing Account

```bash
# Audit current account
social accounts audit @myhandle --platform instagram

# Get platform-specific optimization
social accounts optimize --platform instagram --niche food --stage monetized

# Trending content to use today
social trends youtube --category all --limit 10 --output table
social trends tiktok --limit 20 --output table
```

## Output Examples

### `social trends tiktok --limit 3 --output table`
```
+------+--------------+----------+----------+-------+
| rank | hashtag      | posts    | views    | trend |
+------+--------------+----------+----------+-------+
| 1    | #fyp         | 54000000 | 12000000 | up    |
| 2    | #viral       | 32000000 | 9000000  | up    |
| 3    | #trending    | 28000000 | 7500000  | up    |
+------+--------------+----------+----------+-------+
```

### `social hashtags research fitness --output json` (excerpt)
```json
{
  "niche": "fitness",
  "platform": "tiktok",
  "recommended": ["#fitness", "#gymlife", "#workoutmotivation", "#homeworkout", "#gymtok", "#fyp"],
  "strategy": {
    "mega_tags": ["#fitness", "#workout", "#gym"],
    "mid_tags":  ["#fitlife", "#gymlife"],
    "micro_tags": ["#homeworkout", "#calisthenics"],
    "viral_tags": ["#75hard", "#gymtok"]
  },
  "platform_rules": {"max": 5, "ideal": "3-5", "note": "..."}
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key (optional — enables higher limits and metadata) |

## Known Limitations

1. **TikTok Creative Center**: Occasionally requires a regional IP or returns empty on certain regions.
2. **YouTube scraping**: Page structure may change; API key is recommended for production use.
3. **Rate limits**: YouTube API has a daily quota of 10,000 units; scraping has no hard limit but respect robots.txt.
4. **TikTok account data**: Public APIs don't expose individual account metrics — account audit uses a heuristic checklist.

## Test

```bash
cd social-media/agent-harness
pip install -e .
pytest tests/test_core.py -v
```

All tests run without network access.
