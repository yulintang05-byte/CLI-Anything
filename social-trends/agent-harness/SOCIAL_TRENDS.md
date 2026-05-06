# cli-anything-social-trends — Architecture & SOP

## Overview

`cli-anything-social-trends` is a CLI harness that scrapes viral trends from TikTok and YouTube,
generates optimized hashtag sets, builds content calendars, and teaches theme page strategy.
No GUI, no browser automation — pure HTTP requests and intelligent data processing.

---

## Commands Reference

```
cli-anything-social-trends [--json]

TRENDS:
  trends youtube [--region US] [--api-key KEY] [--limit 20] [--hashtags-only]
  trends tiktok  [--region US] [--limit 30]
  trends sounds  <tiktok|youtube> [--region] [--niche]
  trends all     [--region] [--niche]

HASHTAGS:
  hashtags niche    <niche> [--platform tiktok] [--format list|inline|newline|spaced]
  hashtags optimize --niche <n> [--platform] [--branded tag] [--format]
  hashtags score    <tag1> <tag2> ...
  hashtags niches

OPTIMIZE:
  optimize schedule <platform|all>  [--timezone EST]
  optimize profile  <platform|all>
  optimize calendar --niche <n>     [--platforms tiktok,instagram] [--days 7] [--start YYYY-MM-DD]
  optimize growth   -s <start> -e <end> -d <days>

THEME PAGES:
  theme about
  theme niches
  theme niche     <niche>
  theme checklist [--phase "monetization"]
  theme repost    <tiktok|instagram|youtube_shorts>
  theme monetize  [--followers N]

CONFIG:
  config set <youtube_api_key|region> <value>
  config get [key]
  config path

SESSION:
  session status | history | undo | redo
```

---

## Architecture

```
social-trends/agent-harness/
├── setup.py
├── SOCIAL_TRENDS.md
└── cli_anything/social_trends/
    ├── __init__.py
    ├── __main__.py
    ├── social_trends_cli.py          ← Click CLI + REPL entry point
    ├── core/
    │   ├── youtube.py                ← YouTube trending scraper (API + web fallback)
    │   ├── tiktok.py                 ← TikTok hashtag/sound scraper + niche tag library
    │   ├── hashtags.py               ← Hashtag classification, scoring, and set builder
    │   ├── music.py                  ← Viral sound tracker + niche sound suggestions
    │   ├── optimizer.py              ← Posting times, profile audit, content calendar
    │   ├── theme_pages.py            ← Theme page strategy, niche ranking, monetization
    │   └── session.py                ← Command history + undo/redo
    ├── utils/
    │   ├── repl_skin.py              ← Unified REPL terminal UI (cli-anything standard)
    │   └── trends_backend.py         ← Config, HTTP helpers, API key resolution
    └── tests/
        ├── __init__.py
        └── test_core.py              ← 81 unit tests (100% pass, no network required)
```

---

## Data Sources

### YouTube
| Method | Requirements | Data |
|--------|-------------|------|
| `fetch_trending_api()` | YouTube Data API v3 key | Videos, stats, tags, thumbnails |
| `fetch_trending_scrape()` | None (free) | Titles, channels, hashtags from `ytInitialData` |

**API key setup:**
```bash
# Option 1: environment variable
export YOUTUBE_API_KEY=AIza...

# Option 2: CLI config
cli-anything-social-trends config set youtube_api_key AIza...

# Without a key, the CLI falls back to web scraping automatically
```

### TikTok
| Method | Requirements | Data |
|--------|-------------|------|
| `fetch_trending_hashtags()` | None | Hashtag name, video count, view count |
| `fetch_trending_sounds()` | None | Sound title, artist, duration |
| `get_niche_hashtags()` | None | Curated static list (8 niches, 15 tags each) |

**Note:** TikTok's scraping is brittle — the `__UNIVERSAL_DATA_FOR_REHYDRATION__` structure
changes periodically. The library includes a curated fallback library for all 8 niches.

### Google Trends
Future integration point — pytrends library can be added to correlate search trends
with social media hashtag performance.

---

## Hashtag Strategy Engine

### Tier Classification
| Tier | View Count | Strategy |
|------|-----------|----------|
| mega | 500M+ | 2 per post — broad reach, low feature probability |
| large | 100M–500M | 3 per post — competition is high |
| medium | 10M–100M | 8 per post — **sweet spot** |
| small | 1M–10M | 5 per post — higher feature probability |
| micro | <1M | 5 per post — tight community reach |

### Optimal Mix (23 tags + 2–3 branded)
```
#fyp #viral                           ← 2 mega (universal reach)
[top trending tags x3]                ← 3 large (current momentum)
[niche-specific x8]                   ← 8 medium (discoverability)
[sub-niche x5]                        ← 5 small (community)
[micro-niche x5]                      ← 5 micro (superfan)
[#yourbrand x1-3]                     ← branded (recognition)
```

---

## Account Optimization

### Posting Time Data Source
Research-backed optimal posting windows per platform (EST):
- **TikTok:** 6–10 AM and 8–11 PM — when users scroll before/after work
- **Instagram:** 6 AM–6 PM — business hours for B2B; evenings for B2C
- **YouTube:** 2–5 PM EST — US afternoon aligns with global morning

### Content Calendar Algorithm
1. Start from `start_date` (default: today)
2. For each day, look up weekday → optimal posting times
3. Rotate through 7 content type templates (educational, trending audio, BTS, tutorial, relatable, hot take, transformation)
4. Assign one post per platform per day

---

## Theme Page Strategy

### Niche Scoring Formula
```
total_score = demand + (10 - competition) + monetization + content_availability
```
- Grade A: ≥35 points
- Grade B: 28–34 points  
- Grade C: <28 points

### Top Niches by Score
1. **Finance** — demand:9 + low comp + monetization:10 = Grade A
2. **Fitness** — demand:9 + broad content + monetization:8 = Grade A
3. **Motivation** — demand:10 + infinite content = Grade A
4. **Beauty** — demand:9 + strong affiliate market = Grade A
5. **Tech** — demand:8 + high-ticket affiliates = Grade A

### 6-Phase Setup
1. Niche Selection → 2. Account Creation → 3. Content Pipeline →
4. Posting Strategy → 5. Growth (0–10K) → 6. Monetization (10K+)

---

## Configuration

Config stored at `~/.cli-anything-social-trends/config.json`:

```json
{
  "youtube_api_key": "AIza...",
  "region": "US"
}
```

Environment variables override config:
- `YOUTUBE_API_KEY` or `YT_API_KEY`
- `SOCIAL_TRENDS_REGION`

---

## Testing

```bash
# Run all unit tests (no network required)
cd social-trends/agent-harness
pip install pytest
python -m pytest cli_anything/social_trends/tests/test_core.py -v

# 81 tests across 14 test classes:
# TestYoutubeHashtagExtraction, TestYoutubeAggregation, TestYoutubeVideoParser
# TestTikTokNicheHashtags, TestTikTokHashtagParser
# TestHashtagClassification, TestHashtagScoring, TestHashtagFormatting, TestBuildOptimalSet
# TestOptimalTimes, TestPostingFrequency, TestProfileAudit, TestContentCalendar, TestGrowthCalculator
# TestNicheEvaluation, TestSetupChecklist, TestMonetizationRoadmap, TestRepostGuide
# TestMusicExtraction, TestSoundSuggestions
# TestSession, TestTrendsBackend
```

---

## Install & Run

```bash
cd social-trends/agent-harness
pip install -e .

# Interactive REPL
cli-anything-social-trends

# One-shot commands
cli-anything-social-trends trends tiktok --region US
cli-anything-social-trends hashtags optimize --niche fitness --platform tiktok --format inline
cli-anything-social-trends optimize calendar --niche fitness --platforms tiktok,instagram --days 14
cli-anything-social-trends theme niches --json
cli-anything-social-trends theme monetize --followers 12000
```
