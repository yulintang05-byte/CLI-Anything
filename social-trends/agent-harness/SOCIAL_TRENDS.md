# SOCIAL_TRENDS.md — Architecture SOP for cli-anything-social-trends

## Overview

`cli-anything-social-trends` is an agent-native CLI for social media trend intelligence
and account optimization. It follows the CLI-Anything 7-phase methodology:

1. Analyze → 2. Design → 3. Implement → 4. Plan Tests → 5. Write Tests → 6. Document → 7. Publish

## Architecture

### Data Layers

```
Platform APIs / Web         yt-dlp / requests + BeautifulSoup
        │                              │
        ▼                              ▼
  social_backend.py  ◄─── config, sessions, cache (~30min TTL)
        │
        ▼
  Core Modules          Normalized data structures (VideoResult, HashtagResult, etc.)
  ├── youtube.py        YouTube: yt-dlp OR Data API v3
  ├── tiktok.py         TikTok: web API OR Research API
  ├── hashtags.py       Analysis engine (pure Python, no network)
  ├── music.py          Sound discovery + genre/mood classification
  ├── accounts.py       Engagement analysis + optimization engine
  └── theme_pages.py    Niche database + conversion playbooks
        │
        ▼
  social_trends_cli.py  Click groups: auth, trends, hashtags, music, accounts, theme-page
        │
        ▼
  --json / human-readable output  +  REPL (repl_skin.py)
```

### Key Design Decisions

**Dual-mode scrapers**: Every scraper has a primary (API) and fallback (scraping/curated) mode.
The CLI is fully functional without any API keys — yt-dlp handles YouTube trending, and
TikTok hashtags fall back to a curated top-30 list that is accurate to within days.

**Cache layer**: All network responses are cached for 30 minutes in
`~/.cli-anything-social-trends/cache/`. This prevents redundant requests and makes
the REPL fast for repeated queries.

**Analysis is always local**: The hashtag scoring, account analysis, engagement
calculations, and theme page playbooks are all pure Python with no network dependency.
This means `accounts analyze`, `hashtags recommend`, and `theme-page convert` always
work instantly.

**Normalized output format**: All platform-specific data is normalized to common dicts
before reaching the CLI layer. `youtube.py` and `tiktok.py` both produce `VideoResult`-
like structures with the same keys, so the CLI and tests are platform-agnostic.

### Virality Score Formula

```
virality_score = reach_component + volume_component + engagement_component

reach_component    = min(50, log10(view_count) × 5)       # 0-50 points
volume_component   = min(30, log10(video_count) × 3.5)    # 0-30 points
engagement_comp.   = min(20, engagement_rate × 2)          # 0-20 points
```

### Opportunity Score Formula

```
opportunity_score = min(100, log10(avg_views_per_video) × 10)

Where avg_views_per_video = view_count / video_count

High opportunity = many views relative to competition (niche sweet spot)
```

### Engagement Rate

```
TikTok:    (likes + comments + shares) / plays × 100
Instagram: (likes + comments + saves) / impressions × 100
YouTube:   (likes + comments) / views × 100

Benchmarks (good threshold):
  TikTok:    3%+  (excellent: 6%+)
  Instagram: 1.5% (excellent: 3.5%+)
  YouTube:   2%+  (excellent: 4%+)
```

## Critical Lessons

| Lesson | Detail |
|--------|--------|
| TikTok API instability | TikTok's internal web endpoints change. Always provide curated fallbacks for hashtags and sounds. Never hard-fail on TikTok API errors. |
| yt-dlp for YouTube | yt-dlp is the most reliable YouTube data source without an API key. It handles geo-restrictions and playlist formats automatically. |
| Cache everything | Platform scrapers should cache for at minimum 15 minutes. Over-requesting TikTok causes IP blocks. |
| Normalize early | Convert platform-specific formats to canonical dicts at the scraper boundary, not in the CLI layer. |
| Tests must not network | All unit tests use mock/patch for network calls. E2E tests may test the CLI runner but not real platform APIs. |

## File Structure

```
social-trends/agent-harness/
├── setup.py                                     # pip install -e .
├── SOCIAL_TRENDS.md                             # This file
└── cli_anything/social_trends/
    ├── __init__.py
    ├── __main__.py
    ├── README.md
    ├── social_trends_cli.py                     # Main CLI (Click groups)
    ├── core/
    │   ├── __init__.py
    │   ├── youtube.py                           # YouTube scraper
    │   ├── tiktok.py                            # TikTok scraper
    │   ├── hashtags.py                          # Hashtag intelligence
    │   ├── music.py                             # Trending audio
    │   ├── accounts.py                          # Account optimization
    │   └── theme_pages.py                       # Theme page toolkit
    ├── utils/
    │   ├── __init__.py
    │   ├── repl_skin.py                         # Branded REPL interface
    │   └── social_backend.py                    # HTTP, config, cache
    └── tests/
        ├── __init__.py
        ├── TEST.md
        ├── test_core.py                         # Unit tests (85+ tests)
        └── test_full_e2e.py                     # E2E CLI tests (40+ tests)
```

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"

# Unit tests (no network, no API keys needed)
python -m pytest cli_anything/social_trends/tests/test_core.py -v

# E2E tests (CLI runner, no real network)
python -m pytest cli_anything/social_trends/tests/test_full_e2e.py -v

# All tests
python -m pytest cli_anything/social_trends/tests/ -v

# With installed CLI
CLI_ANYTHING_FORCE_INSTALLED=1 python -m pytest cli_anything/social_trends/tests/ -v -s
```
