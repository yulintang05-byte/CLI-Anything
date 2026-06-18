# SOCIAL_MEDIA.md — CLI-Anything Methodology for Social Media Intelligence

## Software Overview

**Tool**: Social Media Intelligence & Automation  
**Backends**: YouTube Data API v3 · TikTok Web API · youtubesearchpython  
**Purpose**: Scrape viral trends, hashtags, and music; optimize accounts; build converting theme pages  

## Backend Architecture

```
YouTubeBackend
├── Official YouTube Data API v3 (when YOUTUBE_API_KEY configured)
│   └── videos().list(chart="mostPopular") → trending videos
│   └── search().list(q=..., order="viewCount") → search
└── youtubesearchpython fallback (no API key needed)
    └── VideosSearch(query, limit=N) → search results

TikTokBackend
├── TikTokApi (Playwright-based, requires: pip install playwright)
│   └── api.hashtag(name=...).info() → hashtag stats
│   └── api.trending.videos() → trending feed
└── requests fallback (always available)
    └── tiktok.com/api/suggest/get/ → hashtag suggestions
    └── tiktok.com/api/discover/music/ → trending sounds
    └── tiktok.com/api/search/item/full/ → video search
```

## Data Flow

```
1. Scrape Phase
   ├── YouTubeBackend.get_trending_videos(region, category, max)
   ├── YouTubeBackend.get_trending_hashtags(region, category)
   ├── YouTubeBackend.get_trending_music(region)
   ├── TikTokBackend.get_trending_hashtags(category, region)
   ├── TikTokBackend.get_trending_sounds(region)
   └── TikTokBackend.get_trending_videos(region, category)

2. Aggregate Phase
   └── trends.aggregate_trends(yt_videos, yt_hashtags, yt_music, tt_hashtags, tt_sounds, tt_videos)
       ├── Compute virality scores (0–100)
       ├── Rank all items by score
       ├── Detect cross-platform hashtag overlap
       └── Generate actionable insights

3. Strategy Phase
   ├── hashtags.generate_hashtag_set(niche, platform) → tier-optimized set
   ├── music.format_music_report(yt_music, tt_sounds, content_type) → tips
   ├── account_optimizer.full_account_audit(profile) → improvements
   └── theme_page.monetization_roadmap(niche, followers) → revenue plan

4. Output Phase
   └── REPL or JSON (--json flag) → all commands machine-readable
```

## Virality Score Algorithm

```python
def compute_virality_score(views, likes, comments, shares=0):
    engagement_rate = (likes + comments*2 + shares*3) / max(views, 1)
    view_score  = min(100, (views / 1_000_000) * 50)  # 0–50 pts for reach
    eng_score   = min(50, engagement_rate * 500)        # 0–50 pts for engagement
    return view_score + eng_score  # total: 0–100
```

## Hashtag Tier System

| Tier   | Post Count        | Avg ER  | Purpose                        |
|--------|-------------------|---------|--------------------------------|
| mega   | 50M+              | 0.3%    | Maximum reach                  |
| large  | 10–50M            | 0.7%    | Broad audience                 |
| medium | 1–10M             | 2.0%    | Balanced reach + engagement    |
| small  | 100K–1M           | 6.0%    | Niche community                |
| micro  | 1K–100K           | 15.0%   | Highly targeted, best ER       |

**Optimal Mix (Instagram)**:  2 mega + 4 large + 6 medium + 8 small + 5 micro = 25 total  
**Optimal Mix (TikTok)**:     1 mega + 2 large + 4 medium + 5 small + 3 micro = 15 total  

## State / Session Model

```
No "project file" — this tool is stateless per run.
Persistence via ~/.cli-anything-social/:
├── accounts/*.json         — AccountProfile dataclasses
├── trend_reports/*.json    — timestamped trend aggregates
├── music_reports/*.json    — timestamped music reports
├── schedule.json           — ScheduledPost list
├── youtube_config.json     — API key
└── {youtube,tiktok}_cache.json — TTL-cached API responses
```

## Key Design Decisions

1. **No-API-key fallback**: Works day-one without configuration; API key unlocks better data
2. **TikTok web scraping**: TikTok doesn't offer a public API; requests-based scraping is the only option; Playwright fallback for deeper data
3. **Research-backed data**: Hashtag tiers, posting times, engagement benchmarks are from published social media research
4. **Niche database**: 11 documented niches with CPM, affiliate programs, shoutout rates — validated against creator economy reports
5. **JSON output on all commands**: `--json` flag on root group enables agent-native consumption

## Caching Strategy

- YouTube API: 1-hour TTL (API quota is 10,000 units/day)
- TikTok web: 30-minute TTL (scraping should be rate-limited)
- Cache bypass: `--no-cache` flag on `trends scrape`

## Test Strategy

- **Unit tests** (`test_core.py`): All pure-function logic, no network
- **E2E tests** (`test_full_e2e.py`): Real API calls, skipped without keys
- **CLI integration tests**: `subprocess.run` against installed CLI binary
- **Fixtures**: `tmp_path` monkeypatching for filesystem-dependent tests
