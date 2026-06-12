# TEST.md — social-trends CLI Test Plan & Results

## Overview

Full test suite for the `cli-anything-social-trends` harness.
Tests cover unit logic, CLI integration (via Click test runner), and optional live integration tests.

---

## Test Strategy

### Layers

| Layer | File | Description |
|-------|------|-------------|
| Unit | `test_core.py` | Pure-Python module logic, no network |
| CLI Integration | `test_full_e2e.py` | CLI commands via Click test runner |
| Live Integration | `test_full_e2e.py` (marked `integration`) | Real YouTube/TikTok API calls |

### Test Markers

```
pytest                    # Unit + CLI tests (no network)
pytest -m integration     # Include live API tests (requires env vars)
pytest --cov=cli_anything/social_trends  # With coverage
```

---

## Module Coverage

### `youtube_trends.py`
- [x] `_extract_hashtags()` — regex extraction, dedup
- [x] `_parse_count()` — M/K/B suffix parsing, edge cases
- [x] `get_trending_hashtags()` — aggregation, sorting, top_n
- [x] InnerTube API path (integration)
- [x] Data API v3 path (integration, requires YOUTUBE_API_KEY)

### `tiktok_trends.py`
- [x] `get_trending_hashtags()` — view count aggregation
- [x] `get_trending_sounds()` — usage count aggregation, sort order
- [x] Research API path (integration, requires TIKTOK_CLIENT_KEY/SECRET)
- [x] Public endpoint path (integration)

### `hashtag_analyzer.py`
- [x] `generate_hashtag_set()` — all strategies, all platforms, limit enforcement
- [x] `_match_niche()` — keyword matching, fuzzy match
- [x] `merge_platform_hashtags()` — cross-platform merge, platform labels
- [x] `_assign_bucket()` — all bucket thresholds
- [x] `get_niche_list()` — returns sorted list

### `account_optimizer.py`
- [x] `audit_account()` — no assessment, all pass, all fail
- [x] `get_posting_schedule()` — count, timezone adjustment
- [x] `generate_content_calendar()` — entries created, date ordering
- [x] `get_growth_recommendations()` — diagnoses, engagement calculation
- [x] Engagement benchmarks structure

### `theme_page_strategy.py`
- [x] `get_playbook()` — all fields populated
- [x] `score_niches()` — all niches, specific niches
- [x] `get_conversion_guide()` — 4 phases, valuation multiples
- [x] `MONETIZATION_TIERS` — ascending order

### `music_tracker.py`
- [x] `analyze_sounds()` — returns insight, top/rising sounds
- [x] `_score_velocity()` — velocity scoring
- [x] `get_sound_strategy()` — known niche, unknown niche

### CLI Commands (`social_trends_cli.py`)
- [x] `hashtags generate` — all strategies × platforms, JSON output
- [x] `hashtags niches` — list, JSON
- [x] `account schedule` — count, JSON
- [x] `account calendar` — date ordering, entry structure
- [x] `account grow` — engagement calculation, diagnoses
- [x] `theme playbook` — all fields, human + JSON
- [x] `theme niches` — ranking, JSON
- [x] `theme convert` — 4 phases, human + JSON

---

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```

### With coverage:
```bash
pytest cli_anything/social_trends/tests/ -v \
    --cov=cli_anything/social_trends \
    --cov-report=term-missing
```

### Integration tests only:
```bash
export YOUTUBE_API_KEY=your_key_here
export TIKTOK_CLIENT_KEY=your_key_here
export TIKTOK_CLIENT_SECRET=your_secret_here
pytest cli_anything/social_trends/tests/ -m integration -v
```

---

## Test Results

| Test Class | Tests | Status |
|-----------|-------|--------|
| TestYouTubeUtils | 7 | PASS |
| TestYouTubeHashtagAggregation | 2 | PASS |
| TestTikTokUtils | 3 | PASS |
| TestHashtagAnalyzer | 7 | PASS |
| TestAccountOptimizer | 8 | PASS |
| TestThemePageStrategy | 6 | PASS |
| TestMusicTracker | 4 | PASS |
| TestHashtagCommands (CLI) | 6 | PASS |
| TestAccountCommands (CLI) | 5 | PASS |
| TestThemePageCommands (CLI) | 5 | PASS |
| **Total** | **53** | **PASS** |
