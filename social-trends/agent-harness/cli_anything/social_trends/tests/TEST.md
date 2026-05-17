# Social Trends CLI — Test Plan & Results

## Test Suite Summary

| Suite | Tests | Status |
|-------|-------|--------|
| test_core.py (unit) | 55 | PASS |
| test_full_e2e.py (CLI) | 32 | PASS |
| **TOTAL** | **87** | **100%** |

## Test Categories

### Unit Tests (test_core.py) — 55 tests

| Class | Tests | Coverage |
|-------|-------|----------|
| TestHashtagAnalyzer | 11 | tag cleaning, tier boundaries, reach estimation, cross-platform detection, strategy building, compare |
| TestMusicTracker | 10 | title normalization, niche detection, sound recommendations, feeding YT/TT data, export |
| TestAccountOptimizer | 12 | tier classification, ER benchmarking, bio auditing, full account audits, gap analysis, report generation |
| TestThemePage | 12 | milestone detection, plan creation, calendar validation, guide structure, revenue estimation, all niches, engagement pods, branding |
| TestTikTokScraper | 6 | video normalization, engagement calc, HTML state extraction, hashtag extraction, niche hashtags |
| TestYouTubeScraper | 4 | ISO date generation, hashtag extraction, music filtering |
| TestSocialBackend | 2 | config initialization, account add/remove |

### E2E CLI Tests (test_full_e2e.py) — 32 tests

| Class | Tests | Coverage |
|-------|-------|----------|
| TestStatusCommand | 2 | status output, JSON mode |
| TestSetupCommands | 3 | region, niche, youtube-key |
| TestAccountsCommands | 6 | add youtube, add tiktok, list empty, list populated, remove, remove nonexistent |
| TestScrapeYouTube | 3 | requires API key check, mocked scrape, JSON output |
| TestScrapeTikTok | 2 | HTTP mode scrape, save report |
| TestHashtagCommands | 3 | strategy with reports, compare, graceful no-reports |
| TestMusicCommands | 2 | no reports warning, with reports |
| TestOptimizeCommands | 3 | tiktok audit, youtube no-key fallback, no accounts |
| TestThemePageCommands | 5 | plan, JSON plan, conversion guide, branding, all niches |
| TestReportCommands | 3 | list empty, list with reports, show by path |

## Running Tests

```bash
cd social-trends/agent-harness
pip install click prompt-toolkit requests google-api-python-client beautifulsoup4 \
            pandas tabulate rich pytest responses
PYTHONPATH=. pytest cli_anything/social_trends/tests/ -v
```

## Last Run

```
87 passed in 0.23s
Platform: linux, Python 3.11.15
```
