# Social Trends: Project-Specific Analysis & SOP

## Architecture Summary

Social Trends is an agent-native CLI for scraping viral trends from TikTok and YouTube,
generating account optimization reports, and delivering a complete theme-page playbook.
It requires **no credentials** for TikTok (unofficial path) and a free YouTube Data API
key for YouTube features.

```
┌─────────────────────────────────────────────────────┐
│              Social Trends CLI                       │
│  ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │  TikTok    │ │  YouTube   │ │   Theme Page     │  │
│  │  Scraper   │ │  Scraper   │ │   Playbook       │  │
│  └─────┬──────┘ └─────┬──────┘ └────────┬─────────┘  │
│        │               │                │            │
│  ┌─────┴───────────────┴────────────────┴─────────┐  │
│  │               Optimizer Engine                  │  │
│  │  Engagement scoring · Hashtag blending          │  │
│  │  Posting time intelligence · Caption hooks      │  │
│  └──────────────────┬──────────────────────────────┘  │
│                     │                               │
│  ┌──────────────────┴──────────────────────────┐    │
│  │  Click CLI  (JSON / human output)            │    │
│  │  Groups: tt · yt · optimize · theme          │    │
│  └──────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

## Environment Variables

| Variable               | Required For                       | Where to Get                          |
|------------------------|------------------------------------|---------------------------------------|
| `YOUTUBE_API_KEY`      | All `yt` commands                  | https://console.cloud.google.com (free, 10K units/day) |
| `TIKTOK_CLIENT_KEY`    | Official TikTok API (optional)     | https://developers.tiktok.com         |
| `TIKTOK_CLIENT_SECRET` | Official TikTok API (optional)     | https://developers.tiktok.com         |

TikTok commands work without credentials via the unofficial scraper path.

## Command Map: Agent Action → CLI Command

| Agent Action                               | CLI Command                                                          |
|--------------------------------------------|----------------------------------------------------------------------|
| Get TikTok trending videos                 | `tt trends --count 20`                                               |
| Get TikTok trending hashtags               | `tt hashtags --count 30`                                             |
| Get TikTok trending sounds/music           | `tt sounds --count 20`                                               |
| Full TikTok report                         | `tt report --count 20`                                               |
| Get YouTube trending videos (US)           | `yt trends --region US --count 25`                                   |
| Get YouTube trending music                 | `yt music --region US`                                               |
| Extract YouTube top hashtags               | `yt hashtags --region US`                                            |
| Search YouTube by keyword/hashtag          | `yt search "fitness motivation"`                                     |
| Full YouTube report                        | `yt report --region US`                                              |
| Cross-platform trend snapshot              | `all-trends --region US`                                             |
| TikTok-only snapshot                       | `all-trends --no-yt`                                                 |
| Best posting times for platform            | `optimize posting-times tiktok`                                      |
| Profile optimization checklist            | `optimize checklist instagram`                                       |
| Generate caption hooks                     | `optimize caption-hooks "weight loss"`                               |
| Build optimal hashtag set                  | `optimize hashtag-set tiktok --niche fitness --niche health`         |
| Full account optimization report           | `optimize full-report tiktok "fitness" --niche gym --niche workout`  |
| Browse theme page niches                   | `theme niches --keyword finance`                                     |
| Growth phase playbook (0 → 100K)          | `theme growth`                                                       |
| Monetization methods & earnings            | `theme monetize`                                                     |
| Free content sources                       | `theme content-sources`                                              |
| Complete theme page playbook               | `theme playbook`                                                     |

All commands accept `--json` flag for structured agent output.

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
# Then:
social-trends --help
```

## Quick Start

```bash
# No API key needed — TikTok unofficial scraper
social-trends tt report

# With YouTube API key
export YOUTUBE_API_KEY=AIza...
social-trends all-trends

# Account optimization
social-trends optimize full-report tiktok "travel" --niche wanderlust --niche adventure

# Theme page playbook
social-trends theme playbook

# Machine-readable output for agents
social-trends --json tt hashtags --count 30
```

## Data Sources

### TikTok
- **Unofficial path** (default, no credentials): Queries TikTok's mobile API endpoints
  (`/api/recommend/item_list/`, `/api/discover/challenge/`). Returns FYP-level trending
  content. Subject to TikTok rate limiting; suitable for personal & research use.
- **Official Research API** (requires approved app): Full video search, hashtag stats,
  creator analytics. Access: https://developers.tiktok.com/products/research-api/

### YouTube
- **YouTube Data API v3** (free): `videos.list` with `chart=mostPopular` for trending,
  `search.list` for hashtag queries. 10,000 free quota units/day.
  Get key: https://console.cloud.google.com/apis/library/youtube.googleapis.com

## Output Schemas

### TikTok Video Object
```json
{
  "video_id": "7...",
  "username": "creator",
  "description": "#viral caption",
  "hashtags": ["#viral", "#trending"],
  "like_count": 50000,
  "comment_count": 1200,
  "share_count": 800,
  "view_count": 2500000,
  "music_title": "Trending Sound",
  "music_author": "Artist Name",
  "url": "https://tiktok.com/@creator/video/7...",
  "source": "unofficial_scraper"
}
```

### TikTok Hashtag Object
```json
{
  "hashtag": "#viral",
  "video_count": 450000,
  "view_count": 98000000000,
  "source": "unofficial_scraper"
}
```

### TikTok Sound Object
```json
{
  "music_id": "6...",
  "title": "Trending Sound",
  "author": "Artist Name",
  "original": false,
  "duration": 30,
  "video_count": 12
}
```

### YouTube Video Object
```json
{
  "video_id": "dQw4...",
  "title": "Trending Video Title",
  "channel": "Channel Name",
  "published_at": "2025-05-15T10:00:00Z",
  "view_count": 5000000,
  "like_count": 200000,
  "comment_count": 15000,
  "tags": ["tag1", "tag2"],
  "hashtags": ["#viral"],
  "category_id": "10",
  "url": "https://youtube.com/watch?v=dQw4..."
}
```

### Optimization Report Object
```json
{
  "platform": "tiktok",
  "generated_at": "2025-05-19T12:00:00Z",
  "top_trending_videos": [...],
  "recommended_hashtags": ["#viral", "#trending", "#myniche"],
  "posting_schedule": {
    "cadence": "3-5 posts/day",
    "best_hours_utc": [6, 7, 10, 19, 20, 21, 22],
    "next_optimal_slot_utc": 19,
    "hours_until_next_slot": 3
  },
  "caption_hooks": ["POV: fitness ...", "..."],
  "profile_checklist": ["Bio ≤ 80 chars ...", "..."],
  "top_hashtags_raw": [...]
}
```

## Theme Page — Key Concepts

A **theme page** (faceless/niche account) curates content around a single topic
without the creator appearing on camera. Key advantages:
- Scalable: multiple accounts, VA-operated
- No personal brand risk
- Monetizes via affiliate, brand deals, digital products, ad revenue

### Top Converting Niches (2025)
| Niche | CPM Range | Growth Speed |
|-------|-----------|--------------|
| Finance/Crypto | $15-40 | Moderate |
| AI/Tech | $12-35 | Very Fast |
| Luxury Lifestyle | $8-20 | Fast |
| Fitness | $6-18 | Fast |
| Motivation | $4-12 | Very Fast |

See `theme playbook` for the complete guide.

## Test Coverage

```
tests/test_core.py      — 24 unit tests, all mocked, no API keys
tests/test_full_e2e.py  — CLI structure + theme/optimizer e2e (always pass)
                          YouTube live tests (skip without YOUTUBE_API_KEY)
                          TikTok live tests (skip without TIKTOK_E2E=1)
```

Run: `pytest social-trends/agent-harness/ -v`
