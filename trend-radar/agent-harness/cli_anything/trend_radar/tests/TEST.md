# Trend Radar — Test Plan & Results

## Part 1: Test Plan

### Unit Tests (`test_core.py`)

All unit tests use synthetic data only — no network access, no API keys required.

| Module | Test Class | Tests |
|--------|-----------|-------|
| trend_backend.py | TestTrendBackend | Cache key determinism, cache roundtrip, expiry, corruption handling |
| tiktok_trends.py | TestTikTokTrends | API fallback, sound/video fallback, live response parsing, limit enforcement, trend arrows |
| youtube_trends.py | TestYouTubeTrends | API key resolution, video parsing, days_ago format, API call mock |
| hashtag_optimizer.py | TestHashtagOptimizer | Set structure, platform limits (TikTok=10, Twitter=3), fallback niche, copy-ready format, tier validation, analyze balance |
| content_calendar.py | TestContentCalendar | Structure, week count, required fields, total_posts accuracy, JSON export, CSV export |
| account_optimizer.py | TestAccountOptimizer | Audit categories, niche tips, unknown niche, schedule structure, all-platform schedule, per-platform schedule |
| theme_page_guide.py | TestThemePageGuide | Guide topics, guide-all, fallback, find_niches all, sort order, category filter, conversion known/unknown, setup checklist |

### E2E Tests (`test_full_e2e.py`)

Tests the CLI as a subprocess. Tests that require `YOUTUBE_API_KEY` are automatically skipped when the key is not set.

| Command Group | Test Class | Tests |
|---------------|-----------|-------|
| CLI smoke | TestCLISmoke | --version, --help, subgroup help |
| tiktok | TestTikTokCLI | hashtags (human+JSON), sounds (human+JSON), trending JSON, sort/period variants |
| optimize | TestOptimizeCLI | hashtags all platforms, schedule all platforms, account audit |
| calendar | TestCalendarCLI | generate (human+JSON), export JSON, export CSV, posts-per-week |
| theme | TestThemeCLI | guide all topics, niches (all+category), convert, setup checklist |
| youtube (live) | TestYouTubeCLILive | trending, music category, hashtag search (skipped without key) |
| error handling | TestErrorHandling | missing required args, no API key |

---

## Part 2: Test Results

### Results — 2026-06-10

```
platform linux -- Python 3.11.15, pytest-9.0.3

test_core.py::TestTrendBackend::test_cache_key_deterministic PASSED
test_core.py::TestTrendBackend::test_cache_key_different_for_different_urls PASSED
test_core.py::TestTrendBackend::test_cache_roundtrip PASSED
test_core.py::TestTrendBackend::test_expired_cache_returns_none PASSED
test_core.py::TestTrendBackend::test_corrupt_cache_returns_none PASSED
test_core.py::TestTikTokTrends::test_get_trending_hashtags_fallback PASSED
test_core.py::TestTikTokTrends::test_get_trending_sounds_fallback PASSED
test_core.py::TestTikTokTrends::test_get_trending_videos_fallback PASSED
test_core.py::TestTikTokTrends::test_hashtags_live_api_response_parsed PASSED
test_core.py::TestTikTokTrends::test_limit_respected PASSED
test_core.py::TestTikTokTrends::test_trend_arrow_positive PASSED
test_core.py::TestYouTubeTrends::test_require_key_raises_without_key PASSED
test_core.py::TestYouTubeTrends::test_require_key_returns_env_key PASSED
test_core.py::TestYouTubeTrends::test_require_key_prefers_explicit PASSED
test_core.py::TestYouTubeTrends::test_parse_video PASSED
test_core.py::TestYouTubeTrends::test_days_ago_format PASSED
test_core.py::TestYouTubeTrends::test_get_trending_calls_api PASSED
test_core.py::TestHashtagOptimizer::test_generate_set_returns_correct_structure PASSED
test_core.py::TestHashtagOptimizer::test_generate_set_respects_platform_limit PASSED
test_core.py::TestHashtagOptimizer::test_generate_set_instagram_limit PASSED
test_core.py::TestHashtagOptimizer::test_generate_set_twitter_limit PASSED
test_core.py::TestHashtagOptimizer::test_generate_set_fallback_to_general PASSED
test_core.py::TestHashtagOptimizer::test_copy_ready_has_hashtag_prefix PASSED
test_core.py::TestHashtagOptimizer::test_all_tiers_present PASSED
test_core.py::TestHashtagOptimizer::test_analyze_hashtags_returns_structure PASSED
test_core.py::TestHashtagOptimizer::test_analyze_hashtags_recommendations_not_empty PASSED
test_core.py::TestContentCalendar::test_generate_returns_correct_structure PASSED
test_core.py::TestContentCalendar::test_generate_correct_week_count PASSED
test_core.py::TestContentCalendar::test_each_post_has_required_fields PASSED
test_core.py::TestContentCalendar::test_total_posts_matches_actual_posts PASSED
test_core.py::TestContentCalendar::test_export_json PASSED
test_core.py::TestContentCalendar::test_export_csv PASSED
test_core.py::TestAccountOptimizer::test_audit_returns_categories PASSED
test_core.py::TestAccountOptimizer::test_audit_includes_niche_tips_for_known_niches PASSED
test_core.py::TestAccountOptimizer::test_audit_no_crash_unknown_niche PASSED
test_core.py::TestAccountOptimizer::test_get_best_times_returns_schedule PASSED
test_core.py::TestAccountOptimizer::test_get_best_times_all_platforms PASSED
test_core.py::TestAccountOptimizer::test_get_best_times_tiktok PASSED
test_core.py::TestAccountOptimizer::test_audit_all_platforms PASSED
test_core.py::TestThemePageGuide::test_get_guide_overview PASSED
test_core.py::TestThemePageGuide::test_get_guide_all PASSED
test_core.py::TestThemePageGuide::test_get_guide_unknown_falls_back PASSED
test_core.py::TestThemePageGuide::test_find_niches_all PASSED
test_core.py::TestThemePageGuide::test_find_niches_sorted_by_growth PASSED
test_core.py::TestThemePageGuide::test_find_niches_by_category PASSED
test_core.py::TestThemePageGuide::test_get_conversion_tips_known PASSED
test_core.py::TestThemePageGuide::test_get_conversion_tips_unknown_has_fallback PASSED
test_core.py::TestThemePageGuide::test_get_setup_checklist PASSED
test_core.py::TestThemePageGuide::test_setup_checklist_mentions_niche PASSED

test_full_e2e.py::TestCLISmoke::test_version PASSED
test_full_e2e.py::TestCLISmoke::test_help_shows_commands PASSED
test_full_e2e.py::TestCLISmoke::test_youtube_help PASSED
test_full_e2e.py::TestCLISmoke::test_tiktok_help PASSED
test_full_e2e.py::TestCLISmoke::test_optimize_help PASSED
test_full_e2e.py::TestCLISmoke::test_calendar_help PASSED
test_full_e2e.py::TestCLISmoke::test_theme_help PASSED
test_full_e2e.py::TestTikTokCLI::test_hashtags_human_output PASSED
test_full_e2e.py::TestTikTokCLI::test_hashtags_json_output PASSED
test_full_e2e.py::TestTikTokCLI::test_sounds_human_output PASSED
test_full_e2e.py::TestTikTokCLI::test_sounds_json_output PASSED
test_full_e2e.py::TestTikTokCLI::test_trending_json_output PASSED
test_full_e2e.py::TestTikTokCLI::test_hashtags_rise_sort PASSED
test_full_e2e.py::TestTikTokCLI::test_hashtags_30day_period PASSED
test_full_e2e.py::TestOptimizeCLI::test_hashtags_human_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_hashtags_json_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_hashtags_platform_tiktok PASSED
test_full_e2e.py::TestOptimizeCLI::test_hashtags_platform_youtube PASSED
test_full_e2e.py::TestOptimizeCLI::test_hashtags_platform_twitter PASSED
test_full_e2e.py::TestOptimizeCLI::test_schedule_human_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_schedule_json_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_schedule_all_platforms PASSED
test_full_e2e.py::TestOptimizeCLI::test_account_audit_human_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_account_audit_json_output PASSED
test_full_e2e.py::TestOptimizeCLI::test_account_audit_with_username PASSED
test_full_e2e.py::TestCalendarCLI::test_generate_human_output PASSED
test_full_e2e.py::TestCalendarCLI::test_generate_json_output PASSED
test_full_e2e.py::TestCalendarCLI::test_generate_export_json PASSED
test_full_e2e.py::TestCalendarCLI::test_generate_export_csv PASSED
test_full_e2e.py::TestCalendarCLI::test_export_command_json PASSED
test_full_e2e.py::TestCalendarCLI::test_export_command_csv PASSED
test_full_e2e.py::TestCalendarCLI::test_posts_per_week_respected PASSED
test_full_e2e.py::TestThemeCLI::test_guide_overview PASSED
test_full_e2e.py::TestThemeCLI::test_guide_json_output PASSED
test_full_e2e.py::TestThemeCLI::test_guide_all_topics PASSED
test_full_e2e.py::TestThemeCLI::test_niches_all_json PASSED
test_full_e2e.py::TestThemeCLI::test_niches_by_category PASSED
test_full_e2e.py::TestThemeCLI::test_convert_personal_to_theme PASSED
test_full_e2e.py::TestThemeCLI::test_convert_json_output PASSED
test_full_e2e.py::TestThemeCLI::test_setup_checklist_output PASSED
test_full_e2e.py::TestThemeCLI::test_setup_checklist_json PASSED
test_full_e2e.py::TestYouTubeCLILive::test_trending_us SKIPPED (YOUTUBE_API_KEY not set)
test_full_e2e.py::TestYouTubeCLILive::test_trending_music_category SKIPPED (YOUTUBE_API_KEY not set)
test_full_e2e.py::TestYouTubeCLILive::test_hashtags_niche SKIPPED (YOUTUBE_API_KEY not set)
test_full_e2e.py::TestErrorHandling::test_youtube_no_api_key_exits_nonzero PASSED
test_full_e2e.py::TestErrorHandling::test_optimize_hashtags_missing_niche PASSED
test_full_e2e.py::TestErrorHandling::test_calendar_generate_missing_niche PASSED
test_full_e2e.py::TestErrorHandling::test_theme_setup_missing_niche PASSED

94 passed, 3 skipped in 7.91s
```
