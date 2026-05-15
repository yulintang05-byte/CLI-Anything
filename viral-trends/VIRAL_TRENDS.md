# viral-trends — Tool SOP

## Overview

`viral-trends` is an agent-native CLI harness for scraping viral content trends from YouTube and TikTok, optimizing social media accounts, and learning converting theme page strategy.

**Use cases:**
- Discover trending hashtags, sounds, and video formats in real-time
- Generate data-driven optimization reports for any social media account
- Learn and execute the personal → theme page conversion playbook
- Run a full pipeline: scrape → analyze → optimize in one command

## Backend

| Concern | Solution |
|---------|----------|
| YouTube scraping | `yt-dlp ytsearchN:<query>` + YouTube Data API v3 (when key set) |
| TikTok scraping | `yt-dlp https://www.tiktok.com/tag/<tag>` |
| Hashtag ranking | Frequency × view-weight scoring |
| Music extraction | `yt-dlp` metadata (`track`, `artist`, `music` fields) |
| Account optimization | Rule-based engagement rate + view-ratio analysis |
| Theme page guides | Built-in playbooks for 8 high-converting niches |

## Setup

```bash
# System dependency
apt install python3-pip   # Ubuntu
brew install python       # macOS

# Install yt-dlp (required for live scraping)
pip install yt-dlp

# Install the harness
cd viral-trends/agent-harness
pip install -e .

# Verify
viral-trends --help
```

## Environment Variables (optional)

| Variable | Purpose |
|----------|---------|
| `YOUTUBE_API_KEY` | YouTube Data API v3 key for higher-quality trend data |

Without `YOUTUBE_API_KEY`, the tool falls back to `yt-dlp` search — fully functional but less precise.

## Commands

### `fetch` — Scrape trending videos
```bash
# Both platforms, US, 20 videos each
viral-trends fetch --platform both --region US --count 20 --output trends.json

# TikTok only, specific hashtag
viral-trends fetch --platform tiktok --hashtag "#fitness" --count 30 --output fitness.json

# YouTube music category
viral-trends fetch --platform youtube --category music --count 20
```

### `hashtags` — Trending hashtag extraction
```bash
# From saved data
viral-trends hashtags --input trends.json --top 20

# Live fetch + extract
viral-trends hashtags --platform tiktok --count 30 --top 15

# JSON output for agent consumption
viral-trends --json hashtags --input trends.json
```

### `music` — Trending sounds
```bash
# TikTok trending sounds
viral-trends music --platform tiktok --top 15

# From saved data
viral-trends music --input trends.json --top 10
```

### `analyze` — Full trend report
```bash
viral-trends analyze --input trends.json --output report.json
```

### `optimize account` — Account optimization
```bash
# Generate template first
viral-trends optimize template --output myaccount.json

# Edit myaccount.json with your real stats, then:
viral-trends optimize account --profile myaccount.json

# With trend data for trend-aware recommendations
viral-trends optimize account --profile myaccount.json --trends trends.json
```

### `optimize template` — Account profile template
```bash
viral-trends optimize template --output account.json
```

### `theme-page niches` — List converting niches
```bash
viral-trends theme-page niches
```

### `theme-page guide` — Deep-dive guide for a niche
```bash
viral-trends theme-page guide fitness
viral-trends theme-page guide finance
viral-trends theme-page guide tech
```

### `theme-page convert` — Personal → theme page playbook
```bash
viral-trends theme-page convert
```

### `theme-page phases` — Growth phases 0→500K
```bash
viral-trends theme-page phases
```

### `theme-page hooks` — Viral hook formulas
```bash
viral-trends theme-page hooks
```

### `pipeline` — Full scrape → analyze → optimize in one shot
```bash
viral-trends pipeline --platform both --profile myaccount.json --output full_report.json
```

## Agent Workflow Examples

### Discover what to post this week
```bash
viral-trends --json fetch --platform both --count 20 --output /tmp/trends.json
viral-trends --json analyze --input /tmp/trends.json
viral-trends --json hashtags --input /tmp/trends.json --top 10
viral-trends --json music --input /tmp/trends.json --top 5
```

### Full account audit with trend data
```bash
viral-trends optimize template --output /tmp/account.json
# (agent fills in account.json with real metrics)
viral-trends --json pipeline --platform tiktok --profile /tmp/account.json --output /tmp/report.json
```

### Theme page conversion
```bash
viral-trends --json theme-page niches      # Pick a niche
viral-trends --json theme-page guide fitness   # Get full playbook
viral-trends --json theme-page convert         # Conversion steps
```

## Account Profile Schema

```json
{
  "platform": "tiktok",
  "niche": "fitness",
  "followers": 10000,
  "avg_views": 5000,
  "avg_likes": 300,
  "avg_comments": 25,
  "post_frequency": "3x per week",
  "hashtags_used": ["#fitness", "#workout", "#gym"]
}
```

To optimize multiple accounts at once, pass an array:
```json
[
  { "platform": "tiktok", "niche": "fitness", "followers": 10000, ... },
  { "platform": "youtube", "niche": "finance", "followers": 50000, ... }
]
```

## Theme Page: Converting Niches

| Niche | CPM | Conversion Rate | Difficulty |
|-------|-----|-----------------|------------|
| Finance | $8-15 | 3-8% | Low |
| Tech | $10-20 | 4-10% | Medium |
| Fitness | $4-8 | 2-5% | Medium |
| Beauty | $3-7 | 3-6% | Medium |
| Food | $3-5 | 2-4% | Low |
| Fashion | $3-6 | 3-7% | Medium |
| Travel | $3-6 | 1-3% | High |
| Motivation | $2-5 | 1-3% | Low |

## Known Limitations

1. **TikTok rate limiting:** yt-dlp may be rate-limited on high-volume requests. Space fetches by 30s+ intervals.
2. **YouTube without API key:** Falls back to search results which are less precise than the trending feed.
3. **TikTok music metadata:** Available only when yt-dlp can access the video's full metadata.
4. **Regional trends:** yt-dlp search is not strictly region-locked; use `YOUTUBE_API_KEY` for precise regional trending.
