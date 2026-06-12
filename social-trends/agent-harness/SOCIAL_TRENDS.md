# Social Trends CLI — Architecture & Design

## Purpose

`cli-anything-social-trends` provides agent-native access to viral trend data
from YouTube and TikTok. It enables AI agents (and humans) to:

1. **Scrape** trending videos, hashtags, and sounds from YouTube + TikTok
2. **Analyze** cross-platform hashtag performance and sound velocity
3. **Optimize** social media accounts with data-driven posting schedules
4. **Build** theme pages with playbooks, niche scoring, and monetization roadmaps

---

## Architecture

### Data Flow

```
YouTube InnerTube API ──┐
YouTube Data API v3  ──┤──► youtube_trends.py ──┐
youtubesearchpython  ──┘                          │
                                                   ├──► hashtag_analyzer.py
TikTok Research API  ──┐                          │──► music_tracker.py
TikTokApi (playwright)─┤──► tiktok_trends.py ───┘
Public /explore API  ──┘

hashtag_analyzer.py ──► CLI: `hashtags generate/merge/niches`
account_optimizer.py──► CLI: `account audit/schedule/calendar/grow`
theme_page_strategy.py► CLI: `theme playbook/niches/convert`
music_tracker.py ────► CLI: `music analyze`
```

### Data Sources (Fallback Chain)

**YouTube:**
1. YouTube Data API v3 (if `YOUTUBE_API_KEY` set) — highest quality, official
2. InnerTube API — YouTube's own internal API, no key required
3. `youtubesearchpython` — community library, last resort

**TikTok:**
1. TikTok Research API (if `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` set)
2. TikTokApi via playwright (if `TIKTOK_MS_TOKEN` set)
3. Public `/api/explore/item_list/` endpoint — no auth, rate-limited

### Rate Limiting

All HTTP calls go through `utils/http_client.py` which enforces:
- Minimum 1.2s between requests
- Random jitter (0–0.5s) for bot-detection avoidance
- Browser-realistic User-Agent rotation

---

## Module Reference

### `core/youtube_trends.py`
- `get_trending(category, region, max_results)` → `List[TrendingVideo]`
- `get_trending_hashtags(videos, top_n)` → `List[HashtagCount]`
- `get_trending_music(videos)` → `List[MusicTrack]`

### `core/tiktok_trends.py`
- `get_trending(max_results)` → `List[TikTokVideo]`
- `get_trending_hashtags(videos, top_n)` → `List[TikTokHashtag]`
- `get_trending_sounds(videos, top_n)` → `List[TikTokSound]`

### `core/hashtag_analyzer.py`
- `generate_hashtag_set(topic, platform, strategy, live_tags)` → `HashtagSet`
- `merge_platform_hashtags(youtube_tags, tiktok_tags)` → `List[RankedHashtag]`
- `get_niche_list()` → `List[str]`

### `core/music_tracker.py`
- `analyze_sounds(tiktok_sounds, youtube_music)` → `MusicInsight`
- `get_sound_strategy(niche)` → `Dict`

### `core/account_optimizer.py`
- `audit_account(platform, handle, self_assessment)` → `ProfileAudit`
- `get_posting_schedule(platform, posts_per_week, timezone_offset)` → `List[PostSlot]`
- `generate_content_calendar(niche, platform, start_date, weeks, ...)` → `List[ContentCalendarEntry]`
- `get_growth_recommendations(platform, niche, followers, avg_views, ...)` → `Dict`

### `core/theme_page_strategy.py`
- `get_playbook(niche, platform)` → `ThemePagePlaybook`
- `score_niches(niches)` → `List[NicheScore]`
- `get_conversion_guide()` → `Dict`

---

## Niche Support

Built-in niche seeds: `fitness`, `beauty`, `food`, `travel`, `finance`,
`gaming`, `motivation`, `fashion`, `pets`, `entrepreneurship`

Unknown niches get generic hashtag seeds — all data models accept any string.

---

## State Model

This CLI is **stateless** — each command invocation is independent.
No project files or session state are maintained between runs.
Results are returned as Python data structures and optionally serialized to JSON.

---

## Output Formats

All commands support `--json` flag for machine-readable output:

```bash
social-trends --json hashtags generate --topic fitness | jq '.tags[]'
social-trends --json account calendar --niche fitness --weeks 2 | jq '.[0]'
social-trends --json theme playbook --niche motivation | jq '.week1_checklist'
```

Human-readable output uses ANSI colors, tables, and structured sections.
