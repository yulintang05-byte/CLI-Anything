# cli-anything-social-media — Test Plan & Results

## Test Inventory

### Unit Tests (test_core.py) — 68 tests, no network required

| Class | Tests | Description |
|---|---|---|
| TestYouTubeHashtagExtraction | 5 | Regex extraction, lowercase, dedup |
| TestYouTubeEngagement | 3 | Zero views, normal, high engagement |
| TestYouTubeAggregation | 7 | Hashtag counts/sorting, music aggregation, viral patterns |
| TestTikTokHashtagExtraction | 2 | Basic and embedded extraction |
| TestTikTokEngagement | 2 | Zero plays, typical engagement |
| TestTikTokVirality | 2 | High plays, zero plays virality score |
| TestTikTokAggregation | 4 | Hashtags, music, patterns, strategy |
| TestAccountScoring | 10 | All 6 scoring dimensions + engagement rate |
| TestOptimizationRecommendations | 8 | Critical fixes, quick wins, strategy, hashtag plan, calendar, monetization |
| TestAccountRegistry | 5 | Register, list, retrieve, remove, nonexistent |
| TestNicheAnalysis | 7 | Get, list, unknown, compare |
| TestThemePagePlaybook | 3 | Fitness/TikTok playbook, any niche, to_dict |
| TestConversionStrategies | 4 | All, beginner filter, intermediate filter, structure |
| TestTrendsAggregator | 6 | Merge hashtags, cross-platform bonus, empty inputs, sounds, actions |

### E2E Tests (test_full_e2e.py) — 20 tests (network tests marked separately)

| Class | Tests | Requires Network |
|---|---|---|
| TestDependencies | 5 | No (checks local yt-dlp install) |
| TestYouTubeScraperE2E | 6 | Yes — real YouTube scrape |
| TestTikTokScraperE2E | 3 | Yes — real TikTok scrape |
| TestTrendsAggregatorE2E | 5 | Yes — real scrape both platforms |
| TestAccountOptimizerE2E | 4 | No (pure logic) |
| TestThemePagesE2E | 4 | No (pure logic) |
| TestCLIEntryPointE2E | 7 | No (subprocess CLI calls) |

## Running Tests

```bash
# Unit tests only (fast, no network)
cd social-media/agent-harness
PYTHONPATH=. python -m pytest cli_anything/social_media/tests/test_core.py -v

# E2E tests (no network)
PYTHONPATH=. python -m pytest cli_anything/social_media/tests/test_full_e2e.py \
  ::TestDependencies ::TestAccountOptimizerE2E ::TestThemePagesE2E ::TestCLIEntryPointE2E -v

# Full E2E (requires network + yt-dlp)
PYTHONPATH=. python -m pytest cli_anything/social_media/tests/test_full_e2e.py -v

# All tests
PYTHONPATH=. python -m pytest cli_anything/social_media/tests/ -v
```

## Test Results (Phase 6)

```
============================= test session starts ==============================
platform linux -- Python 3.11.15, pytest-9.0.3
collected 68 unit tests

68 passed in 0.12s

============================= test session starts ==============================
collected 20 e2e tests (non-network subset)

20 passed in 1.57s

Total: 88 tests passed, 0 failed, 0 errors
```

## Test Scenarios Covered

### Realistic Workflows

1. **New creator launching a fitness theme page**:
   - `theme niche --name fitness` → review CPM, monetization paths
   - `theme playbook --niche fitness --platform tiktok` → full 4-phase plan
   - `theme convert --difficulty beginner` → bio funnel + affiliate setup

2. **Existing account optimization**:
   - `account add --platform tiktok --username mypage --followers 8500 --niche fitness`
   - `account optimize --platform tiktok --username mypage --with-trends`
   - Reviews: score breakdown, critical fixes, hashtag overhaul, bio rewrite

3. **Cross-platform trend intelligence**:
   - `report --niche fitness --region US`
   - Returns: master hashtags, trending sounds, prioritized action plan

4. **Hashtag research before posting**:
   - `trends hashtag fitness` → view volumes and engagement rates for #fitness

5. **Comparing niches before choosing**:
   - `theme compare fitness personal_finance travel tech`
   - Side-by-side: competition, monetization potential, CPM, growth speed
