# Social Trends CLI — Test Plan & Results

## Test Architecture

| Layer | What it tests | File |
|-------|---------------|------|
| **Unit tests** | Core session management, trend engine, optimizer, theme pages | `test_core.py` |
| **CLI integration tests** | All Click commands via test runner (mock data, no API keys) | `test_core.py::TestCLIIntegration` |
| **E2E workflow test** | Full pipeline: session → fetch → hashtags → music → optimize | `test_core.py::test_full_workflow_mock` |

## Running Tests

```bash
# From agent-harness directory
python -m pytest cli_anything/social_trends/tests/ -v

# With coverage
python -m pytest cli_anything/social_trends/tests/ -v --tb=short

# Specific class
python -m pytest cli_anything/social_trends/tests/test_core.py::TestCLIIntegration -v

# E2E workflow only
python -m pytest cli_anything/social_trends/tests/test_core.py::TestCLIIntegration::test_full_workflow_mock -v -s
```

## Test Results

```
================================ Test Summary ================================
social-trends   (run: python -m pytest cli_anything/social_trends/tests/ -v)
──────────────────────────────────────────────────────────────────────────────
TOTAL        95 passed  ✅   100% pass rate
  TrendSession           16 unit tests
  TrendsEngine           18 unit tests
  Optimizer              11 unit tests
  ThemePages             18 unit tests
  CLIIntegration         32 integration + e2e tests (incl. full workflow)
```

## Test Coverage

### TrendSession (core.py)
- [x] Create session with name/region/niche
- [x] Save and load from JSON
- [x] JSON structure validity
- [x] Set YouTube trends (marks modified)
- [x] Set TikTok trends (marks modified)
- [x] Add account (platform/handle/niche)
- [x] Remove existing account
- [x] Remove nonexistent account returns False
- [x] Top hashtags sorted by score
- [x] All trends combines both platforms
- [x] Summary dict structure
- [x] Modified flag cleared on save
- [x] Default session path format
- [x] Session exists check
- [x] Full roundtrip with all data types

### Trends Engine (trends.py)
- [x] merge_hashtags deduplicates cross-platform tags
- [x] merge_hashtags applies 1.5x cross-platform boost
- [x] merge_hashtags sorted by score descending
- [x] merge_trends combines both platform lists
- [x] merge_trends sorted by score
- [x] generate_hashtag_sets returns viral/niche/balanced keys
- [x] generate_hashtag_sets always includes base tags (fyp, viral, trending)
- [x] generate_hashtag_sets max 15 tags per set
- [x] score_content_idea high relevance detection
- [x] score_content_idea low relevance detection
- [x] score_content_idea empty inputs
- [x] analyze_niche_opportunity structure
- [x] _hashtag_recommendation viral cross-platform
- [x] _hashtag_recommendation high value single-platform
- [x] _suggest_content_angles known niche
- [x] _suggest_content_angles unknown niche fallback
- [x] _optimal_posting_times known niche
- [x] _optimal_posting_times default fallback

### Optimizer (optimizer.py)
- [x] generate_optimization_report full structure
- [x] Per-account fields presence
- [x] Empty accounts handled gracefully
- [x] build_content_calendar 7-day output
- [x] Calendar day structure (day/theme/content_idea/hashtags/time/platforms)
- [x] Calendar with no trends (inspired_by is empty string)
- [x] _content_pillars fitness-specific
- [x] _content_pillars generic fallback
- [x] _posting_frequency_rec all platforms present
- [x] _engagement_hooks minimum count
- [x] _growth_tactics structure validation

### Theme Pages (theme_pages.py)
- [x] list_niches returns all 10 niches
- [x] list_niches has required keys
- [x] list_niches sorted by CPM descending
- [x] list_niches sorted by competition ascending
- [x] get_niche valid key returns data
- [x] get_niche invalid key returns None
- [x] score_niche valid key structure
- [x] score_niche invalid key error
- [x] score_niche finance scores highest CPM
- [x] score_niche gaming lower CPM than finance
- [x] get_theme_page_guide full structure
- [x] get_theme_page_guide general (empty key)
- [x] Account setup steps count
- [x] Monetization roadmap milestones
- [x] Common mistakes minimum count
- [x] Growth playbook phases
- [x] All niches have content_sources
- [x] All niches have hashtags
- [x] Tools section has all categories

### CLI Integration (cli.py)
- [x] --version flag
- [x] session new creates file
- [x] session new --json output
- [x] session new duplicate fails
- [x] account add to session
- [x] account add --json output
- [x] account list empty
- [x] account add then list
- [x] trends fetch --mock (all platforms)
- [x] trends fetch --mock --json
- [x] trends list empty session
- [x] hashtags recommend after fetch
- [x] hashtags sets after recommend
- [x] music trending --mock
- [x] music trending --mock --json
- [x] optimize run without accounts fails
- [x] optimize run with full session
- [x] optimize calendar
- [x] optimize score-idea
- [x] theme-page niches
- [x] theme-page niches --json
- [x] theme-page guide
- [x] theme-page guide --json
- [x] theme-page score
- [x] theme-page score --json
- [x] no project graceful failure
- [x] session info
- [x] session info --json
- [x] hashtags score found
- [x] hashtags score not found
- [x] **Full E2E workflow (mock)** — 9-step pipeline
