# Social Trends CLI — Test Plan & Results

## Test Philosophy
All tests run without API keys or network access using demo/curated fallback data.
Tests verify schema correctness, CLI command routing, JSON output, and business logic.

## Test Matrix

| Module | Test Class | Tests | Covers |
|--------|-----------|-------|--------|
| youtube_scraper | TestYouTubeScraper | 11 | Hashtag extraction, demo data, get_trending schema, limit enforcement |
| tiktok_scraper | TestTikTokScraper | 6 | Hashtag extraction, demo data, get_trending schema, music extraction |
| hashtag_analyzer | TestHashtagAnalyzer | 13 | Ranking, tier classification, niche hashtags, auto-recommendation, optimal sets |
| music_tracker | TestMusicTracker | 12 | DB validation, platform/genre/mood filters, niche recommendations, DB matching |
| account_optimizer | TestAccountOptimizer | 10 | Schedule structure, bio optimization, growth playbooks, account auditing |
| theme_page_guide | TestThemePageGuide | 12 | Niche guides, checklists, content methods, brand pitch generation |
| CLI E2E (trends) | TestTrendsCommands | 9 | All trends subcommands, JSON mode, region param |
| CLI E2E (hashtags) | TestHashtagsCommands | 7 | niche, recommend, analyze subcommands, JSON mode |
| CLI E2E (music) | TestMusicCommands | 6 | trending, for-niche, platform/genre filters |
| CLI E2E (optimize) | TestOptimizeCommands | 9 | schedule, bio, playbook, audit, all-accounts |
| CLI E2E (themepage) | TestThemePageCommands | 12 | niches, checklist, content-methods, pitch |
| CLI E2E (config) | TestConfigCommands | 3 | show, set, JSON mode |
| CLI E2E (accounts) | TestAccountsCommands | 2 | list, JSON mode |
| JSON Output Mode | TestJSONOutputMode | 1 | All 8 major commands produce valid JSON dicts |

**Total: 112 tests**

## Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/user/CLI-Anything/social-trends/agent-harness
collected 112 items

112 passed in 0.28s
============================================================
```

**Result: 112/112 PASSED (100%)**

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e .
pip install pytest

# Run all tests
PYTHONPATH=. python3 -m pytest cli_anything/social_trends/tests/ -v

# Run specific module
PYTHONPATH=. python3 -m pytest cli_anything/social_trends/tests/test_core.py -v
PYTHONPATH=. python3 -m pytest cli_anything/social_trends/tests/test_full_e2e.py -v

# Run with coverage
pip install pytest-cov
PYTHONPATH=. python3 -m pytest cli_anything/social_trends/tests/ --cov=cli_anything.social_trends --cov-report=term-missing
```

## Key Test Behaviors

### Demo Fallback
All scraping functions fall back to curated demo data when no API keys are present.
Tests validate this fallback produces correct schemas — same output format as live scraping.

### Schema Contracts
Every dict-returning function is tested for required keys. This ensures agent pipelines
can rely on consistent output regardless of the data source (API, yt-dlp, demo).

### JSON Mode
The `--json` flag is tested across all major command groups. Output is parsed with
`json.loads()` and validated as a dict — confirming agent-consumable output.

### Edge Cases
- Empty hashtag lists
- Invalid niche names
- Zero follower counts
- Missing API keys (graceful degradation)
- Accounts with no posts registered
