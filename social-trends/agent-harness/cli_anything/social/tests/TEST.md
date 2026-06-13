# Social Trends CLI — Test Plan

## Overview
Unit tests for social-trends core modules. All tests run without network access (mocked or data-driven).

## Test Suites

### TestYouTubeTrends (7 tests)
- `test_extract_hashtags_from_text` — regex extracts #tags from text
- `test_extract_hashtags_empty` — empty input returns empty list
- `test_extract_trending_hashtags_frequency` — frequency counting and sorting
- `test_extract_trending_hashtags_empty` — handles empty video list
- `test_extract_trending_music_filters_correctly` — music keyword detection
- `test_extract_trending_music_empty` — handles empty input

### TestTikTokTrends (10 tests)
- `test_fmt_views_trillion/billion/million/thousand/small/none` — view count formatting
- `test_fallback_hashtags_not_empty` — fallback data populated correctly
- `test_fallback_sounds_not_empty` — fallback sounds populated
- `test_get_tiktok_trends_structure` — mocked scrape returns correct schema

### TestHashtagAnalyzer (11 tests)
- `test_build_hashtag_set_tiktok/instagram` — platform-specific sets
- `test_build_hashtag_set_unknown_niche_fallback` — graceful unknown niche
- `test_build_hashtag_set_trending_injection` — trending hashtags injected
- `test_build_hashtag_set_count_override` — count parameter respected
- `test_cross_platform_merge_finds_overlap` — cross-platform detection
- `test_cross_platform_merge_no_overlap` — no false positives
- `test_generate_hashtag_calendar_structure` — calendar schema and length
- `test_all_niches_have_required_tiers` — data completeness check

### TestMusicTrends (6 tests)
- `test_get_music_trends_structure` — output schema validation
- `test_get_music_trends_cross_platform_detection` — cross-platform matching
- `test_royalty_free_sources_populated` — sources list completeness
- `test_trending_genres_populated` — genres list completeness
- `test_action_items_with_tracks` — action items generated from data

### TestAccountOptimizer (7 tests)
- `test_optimize_account_structure` — full report schema
- `test_optimize_account_platforms` — all 4 platforms covered
- `test_optimize_all_platforms_covers_all` — multi-platform report
- `test_generate_content_calendar_length` — correct day count
- `test_generate_content_calendar_structure` — post schema per day
- `test_posting_times_all_days` — 7 days present per platform

### TestThemePageGuide (11 tests)
- `test_guide_structure` — full guide schema
- `test_guide_niche_lookup` — fitness niche resolved
- `test_guide_business_niche` — business niche resolved
- `test_all_niches_populated` — all niches have required fields
- `test_growth_phases_count` — 4 phases present
- `test_30_day_plan_covers_all_stages` — 7 milestones in plan
- `test_key_rules_not_empty` — rules list populated
- `test_monetization_rate_card` — all rate card sections present
- `test_dm_templates_exist` — key DM templates present

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social/tests/test_core.py -v
```

## Results

| Suite                  | Tests | Status |
|------------------------|-------|--------|
| TestYouTubeTrends      | 6     | ✅ PASS |
| TestTikTokTrends       | 10    | ✅ PASS |
| TestHashtagAnalyzer    | 11    | ✅ PASS |
| TestMusicTrends        | 6     | ✅ PASS |
| TestAccountOptimizer   | 7     | ✅ PASS |
| TestThemePageGuide     | 11    | ✅ PASS |
| **TOTAL**              | **51**| **✅ ALL PASS** |
