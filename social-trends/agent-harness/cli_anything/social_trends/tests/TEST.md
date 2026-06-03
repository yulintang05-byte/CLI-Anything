# social-trends Test Plan

## Overview

90 tests across 2 files covering all core modules.

| File | Tests | Coverage |
|------|-------|----------|
| `test_core.py` | 57 | Unit tests — no network, no external deps |
| `test_full_e2e.py` | 33 | E2E CLI subprocess + mocked network |
| **Total** | **90** | **100% pass** |

## Test Modules

### Session (8 tests)
- `record`, `history`, `undo`, `redo`, persistence, `status`
- `HistoryEntry.to_dict` / `from_dict`

### Backend Helpers (20 tests)
- `_extract_hashtags` — basic, no tags, dedup, empty
- `_normalize_tiktok_video` — fields, hashtags, music, URL, missing music, empty
- `get_trending_hashtags` — ranking, top field, required fields, empty, top_n
- `get_tiktok_trending_sounds` — count ranking, ignores None, view accumulation, empty
- Cache — save/load, expired, missing

### Trends Analysis (9 tests)
- `analyze_trends` — keys, platform breakdown, empty input, hashtag ranking, recommendations
- `_extract_content_patterns` — title format detection, keyword extraction
- `_compute_engagement_stats` — basic, empty

### Optimizer (9 tests)
- `optimize_account` — full structure, hashtag plan, posting schedule, monetization stages
- `_next_milestone` — boundary values
- Account registry — add, dedup, remove, remove nonexistent

### Theme Page (10 tests)
- `list_supported_niches` — returns all niches
- `get_niche_guide` — known niche, unknown niche (generic fallback)
- `CONVERTING_ELEMENTS` — bio formula, link-in-bio stack
- `CONVERSION_FUNNEL` — all 4 stages present with tactics
- `PROVEN_NICHES` — all required fields present for all niches
- `get_conversion_tips` — returns list, more tips with followers

### E2E CLI (17 tests)
- Smoke: `--help`, `trends --help`, `account --help`, `theme-page --help`, `config --help`, invalid command
- Theme page: niches list, guide (fitness, finance), unknown niche, convert, calendar — human + JSON
- Account/Config: list, config set/get/path/json, session history/status
- JSON output: guide structure, niches list, session status

### Scraper Mocked (7 tests)
- `analyze_trends` on mock data
- `get_all_hashtags` on mock data
- `get_all_sounds` on mock data
- `scrape_platform` YouTube (mocked subprocess)
- `scrape_platform` TikTok (mocked requests)
- `optimize_account` with mock trend data
- `optimize_all_accounts` with no registered accounts

## Running Tests

```bash
# All tests
cd social-trends/agent-harness
PYTHONPATH=. pytest cli_anything/social_trends/tests/ -v

# Unit tests only (fast, no network)
PYTHONPATH=. pytest cli_anything/social_trends/tests/test_core.py -v

# E2E tests
PYTHONPATH=. pytest cli_anything/social_trends/tests/test_full_e2e.py -v
```

## Results (2026-06-03)

```
90 passed in 1.71s
```
