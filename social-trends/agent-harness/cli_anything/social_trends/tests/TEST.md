# Social Trends CLI — Test Plan & Results

## Overview

| Category | Count | Status |
|---|---|---|
| Unit tests (no network) | 60 | ✅ Pass |
| **Total** | **60** | **100%** |

## Test Modules

### `test_core.py`

#### `TestYouTubeHelpers` (8 tests)
- `test_extract_hashtags_basic` — parses hashtags from mixed text
- `test_extract_hashtags_empty` — returns [] for text without hashtags
- `test_extract_hashtags_deduplication` — deduplicates repeated tags
- `test_parse_music_title_dash` — splits "Artist - Track" correctly
- `test_parse_music_title_no_separator` — handles titles with no separator
- `test_parse_music_title_pipe` — splits on `|` separator
- `test_days_ago_iso_format` — returns ISO 8601 format string
- `test_missing_api_key_raises` — raises RuntimeError when YOUTUBE_API_KEY not set

#### `TestTikTokHelpers` (10 tests)
- `test_extract_hashtags` — extracts hashtags from TikTok description
- `test_days_ago_str_format` — returns 8-digit date string
- `test_today_str_format` — returns today as 8-digit date
- `test_aggregate_hashtags_empty` — returns [] for empty video list
- `test_aggregate_hashtags_counts` — correctly sums video_count and total_views
- `test_aggregate_sounds_empty` — returns [] for empty video list
- `test_aggregate_sounds_counts` — correctly aggregates sound usage
- `test_parse_tiktok_next_data_no_script` — returns [] when no __NEXT_DATA__
- `test_has_research_api_false` — returns False without env vars
- `test_has_research_api_true` — returns True with env vars set

#### `TestAccountOptimizer` (22 tests)
- `test_posting_schedule_tiktok` — returns schedule with required keys
- `test_posting_schedule_youtube` — includes Thursday or Friday
- `test_posting_schedule_with_niche` — includes niche_tip for fitness
- `test_content_mix_tiktok` — shares sum to 100, ≥4 types
- `test_content_mix_youtube` — shares sum to 100
- `test_growth_roadmap_zero_followers` — phase includes "0"
- `test_growth_roadmap_5k_followers` — correct phase returned
- `test_growth_roadmap_100k_plus` — returns 100K+ phase
- `test_bio_template_tiktok` — bio contains niche, 80-char limit noted
- `test_bio_template_youtube` — bio contains niche
- `test_hashtag_strategy_tiktok` — tip mentions hashtag count
- `test_hashtag_strategy_youtube` — tip mentions description placement
- `test_monetization_readiness_zero` — all milestones locked at 0 followers
- `test_monetization_readiness_10k` — at least one feature unlocked at 10K
- `test_identify_issues_empty_bio` — flags empty bio
- `test_identify_issues_low_videos` — flags low video count
- `test_audit_unsupported_platform` — raises ValueError
- `test_parse_follower_range` — "0–1K" → (0, 1000)
- `test_parse_follower_range_millions` — "1M+" → (1_000_000, ...)
- `test_generate_quick_wins_has_items` — returns ≥4 wins
- `test_niche_posting_tip_finance` — tip relevant to finance niche
- `test_niche_posting_tip_food` — tip relevant to food niche

#### `TestThemePages` (18 tests)
- `test_get_profitable_niches_returns_list` — returns ≥5 niches
- `test_get_profitable_niches_max_results` — respects max_results
- `test_get_profitable_niches_filter_difficulty` — filters correctly
- `test_get_profitable_niches_sort_growth_speed` — sorted ascending
- `test_get_profitable_niches_filter_platform` — filters by platform name
- `test_generate_strategy_returns_keys` — has all required keys
- `test_generate_strategy_content_pillar_sum` — pillar shares sum to 100
- `test_generate_strategy_thirty_day_plan_four_weeks` — 4 weeks in plan
- `test_get_conversion_guide_full` — has phases, mistakes, legal
- `test_get_conversion_guide_section` — returns specific phase by name
- `test_get_conversion_guide_invalid_section` — returns error dict
- `test_compare_niches_returns_comparison` — has comparison + recommendation
- `test_get_monetization_timeline` — has income_by_stage, methods
- `test_starter_hashtags_structure` — has niche_specific, broad, community
- `test_find_niche_by_keyword` — finds niche from keyword "dogs"
- `test_find_niche_unknown` — returns fallback for unknown niche
- `test_content_pillars_sum_100` — pillar shares always sum to 100
- `test_recommend_between` — recommends better-scoring niche

#### `TestSocialSession` (7 tests)
- `test_session_defaults` — default niche None, platform tiktok
- `test_session_set_niche` — setter works correctly
- `test_session_add_account` — adds account with metadata
- `test_session_cache_and_retrieve` — caches and retrieves data
- `test_session_cache_expired` — returns None for old cache entries
- `test_session_round_trip` — serialize/deserialize preserves data
- `test_get_env_status_structure` — all keys have required fields

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v --cov=cli_anything.social_trends
```

## Environment Variables

| Variable | Required | Purpose |
|---|---|---|
| `YOUTUBE_API_KEY` | For YouTube commands | YouTube Data API v3 |
| `TIKTOK_API_KEY` | Optional | TikTok Research API (scraping works without) |
| `TIKTOK_API_SECRET` | Optional | TikTok Research API auth |

Get a free YouTube API key: https://console.cloud.google.com/apis/library/youtube.googleapis.com
