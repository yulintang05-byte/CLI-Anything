# Social Trends Harness — Test Plan & Results

## Test Architecture

**Unit tests** (`test_core.py`): All core module functions tested with synthetic data — no external API calls required. Covers YouTube trends, TikTok trends, account optimizer, theme pages, and session management.

**E2E tests** (`test_full_e2e.py`): CLI invocation tests via Click test runner. Tests full command dispatch, JSON output, session persistence, and error handling.

---

## Test Coverage

### YouTube Trends (`core/youtube_trends.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_parse_duration_seconds` | ISO 8601 PT30S → 30 | ✅ Pass |
| `test_parse_duration_minutes` | ISO 8601 PT5M30S → 330 | ✅ Pass |
| `test_parse_duration_hours` | ISO 8601 PT1H2M3S → 3723 | ✅ Pass |
| `test_parse_duration_empty` | PT0S → 0 | ✅ Pass |
| `test_parse_duration_invalid` | "" → 0 | ✅ Pass |
| `test_engagement_rate_calculation` | (likes+comments)/views*100 | ✅ Pass |
| `test_engagement_rate_zero_views` | No division by zero | ✅ Pass |
| `test_extract_trending_hashtags` | Returns ranked hashtag list | ✅ Pass |
| `test_extract_hashtags_deduplication` | No duplicate tags | ✅ Pass |
| `test_analyze_trending_patterns_empty` | Empty input → empty dict | ✅ Pass |
| `test_analyze_trending_patterns` | All fields present | ✅ Pass |
| `test_analyze_patterns_calculates_avg_views` | Math correct | ✅ Pass |
| `test_region_codes_exist` | US/GB/IN present | ✅ Pass |
| `test_category_ids_exist` | Music/Gaming categories | ✅ Pass |

### TikTok Trends (`core/tiktok_trends.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_normalize_web_video_structure` | All fields mapped correctly | ✅ Pass |
| `test_engagement_rate_calculation` | (likes+comments+shares)/views*100 | ✅ Pass |
| `test_extract_trending_hashtags` | Returns ranked list with trend_score | ✅ Pass |
| `test_extract_trending_hashtags_ranking` | Non-empty sorted list | ✅ Pass |
| `test_extract_trending_sounds` | sound1 (2 uses) ranked first | ✅ Pass |
| `test_extract_sounds_sorted_by_usage` | Descending usage count order | ✅ Pass |
| `test_analyze_tiktok_patterns_empty` | Empty input → empty dict | ✅ Pass |
| `test_analyze_tiktok_patterns` | All fields present | ✅ Pass |
| `test_duration_breakdown_correct` | 15s=under_15, 30s+20s=15_30 | ✅ Pass |
| `test_normalize_research_video` | Research API format mapped | ✅ Pass |

### Account Optimizer (`core/account_optimizer.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_generate_posting_schedule_returns_list` | Returns N slots | ✅ Pass |
| `test_posting_schedule_structure` | date/day/hour/quality fields | ✅ Pass |
| `test_posting_schedule_respects_platform` | YT/TT both work | ✅ Pass |
| `test_unknown_platform_defaults` | Falls back gracefully | ✅ Pass |
| `test_utc_to_tz_conversion` | UTC→EST includes timezone | ✅ Pass |
| `test_build_hashtag_strategy_structure` | All required fields | ✅ Pass |
| `test_build_hashtag_strategy_respects_limits` | ≤ platform limit | ✅ Pass |
| `test_build_hashtag_strategy_blends_trending` | Trending tags blended | ✅ Pass |
| `test_generate_content_calendar_structure` | All post fields present | ✅ Pass |
| `test_content_calendar_post_numbering` | Sequential 1..N | ✅ Pass |
| `test_audit_account_structure` | engagement/recs/score fields | ✅ Pass |
| `test_audit_high_engagement_grade` | Viral/good grade for high eng | ✅ Pass |
| `test_audit_low_posting_frequency_recommendation` | Consistency rec triggered | ✅ Pass |
| `test_audit_score_grade_boundaries` | Grade A-F, total 0-100 | ✅ Pass |
| `test_optimize_bio_returns_templates` | Templates + tips returned | ✅ Pass |
| `test_platform_best_times_coverage` | All 5 platforms covered | ✅ Pass |
| `test_niche_hashtag_sets_coverage` | 6 niches with ≥10 tags each | ✅ Pass |

### Theme Pages (`core/theme_pages.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_score_niche_structure` | total_score/grade/breakdown | ✅ Pass |
| `test_score_niche_unknown` | Returns error dict | ✅ Pass |
| `test_score_all_niches` | All 10 niches score 1-100 | ✅ Pass |
| `test_get_niche_starter_kit_structure` | All required fields | ✅ Pass |
| `test_get_niche_starter_kit_unknown` | Returns error dict | ✅ Pass |
| `test_get_playbook_all_phases` | 6 phases returned | ✅ Pass |
| `test_get_playbook_specific_phase` | Phase 1 has steps+deliverable | ✅ Pass |
| `test_get_playbook_invalid_phase` | Returns error dict | ✅ Pass |
| `test_estimate_revenue_structure` | monthly_estimates_usd fields | ✅ Pass |
| `test_estimate_revenue_increases_with_followers` | 500K > 1K revenue | ✅ Pass |
| `test_compare_niches_sorted_by_score` | Descending score order | ✅ Pass |
| `test_compare_niches_ignores_unknowns` | Unknown niches skipped | ✅ Pass |
| `test_conversion_strategies_exist` | All 4 strategies present | ✅ Pass |
| `test_niche_data_completeness` | All 10 required fields per niche | ✅ Pass |

### Session (`core/session.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_new_session_structure` | accounts/api_keys/history keys | ✅ Pass |
| `test_save_and_load_session` | Persists to disk correctly | ✅ Pass |
| `test_add_and_get_account` | Account stored and retrieved | ✅ Pass |
| `test_cache_set_and_get` | Cache round-trip works | ✅ Pass |
| `test_cache_miss_returns_none` | Missing key → None | ✅ Pass |
| `test_cache_expired_returns_none` | Expired entry → None | ✅ Pass |
| `test_cache_clear_all` | Deletes all entries | ✅ Pass |
| `test_get_api_key_from_env` | Reads from environment var | ✅ Pass |
| `test_log_history_appends` | History entry added | ✅ Pass |
| `test_log_history_capped_at_100` | Max 100 entries enforced | ✅ Pass |

### E2E CLI Tests (`test_full_e2e.py`)
| Test | Description | Status |
|------|-------------|--------|
| `test_cli_help` | --help returns 0 | ✅ Pass |
| `test_yt_group_help` | yt --help works | ✅ Pass |
| `test_tt_group_help` | tt --help works | ✅ Pass |
| `test_account_group_help` | account --help works | ✅ Pass |
| `test_theme_group_help` | theme --help works | ✅ Pass |
| `test_account_add_command` | Adds account to session | ✅ Pass |
| `test_account_list_empty` | Lists empty accounts gracefully | ✅ Pass |
| `test_account_audit_not_found` | Error message for missing account | ✅ Pass |
| `test_account_schedule_json_output` | Valid JSON schedule output | ✅ Pass |
| `test_account_hashtags_json_output` | Valid JSON hashtag strategy | ✅ Pass |
| `test_account_calendar_json_output` | Valid JSON calendar | ✅ Pass |
| `test_account_bio_json_output` | Valid JSON bio templates | ✅ Pass |
| `test_theme_niches_json_output` | Valid JSON niche list | ✅ Pass |
| `test_theme_niche_json_output` | Valid JSON niche kit | ✅ Pass |
| `test_theme_compare_json_output` | Valid JSON comparison | ✅ Pass |
| `test_theme_playbook_json_output` | Valid JSON playbook | ✅ Pass |
| `test_theme_revenue_json_output` | Valid JSON revenue estimate | ✅ Pass |
| `test_theme_strategy_json_output` | Valid JSON strategy | ✅ Pass |
| `test_theme_strategy_unknown` | Error on unknown strategy | ✅ Pass |
| `test_config_set_command` | API key stored in session | ✅ Pass |
| `test_cache_clear_command` | Cache cleared successfully | ✅ Pass |
| `test_yt_trends_no_api_key` | Error message when key missing | ✅ Pass |
| `test_tt_hashtag_info_command` | Returns dict (no API required) | ✅ Pass |

---

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```

## API Keys Required for Live Tests

- **YouTube Data API v3**: Get free key at https://console.cloud.google.com
  ```bash
  social-trends config set YOUTUBE_API_KEY <your_key>
  # or
  export YOUTUBE_API_KEY=<your_key>
  ```

- **TikTok Research API** (optional): Apply at https://developers.tiktok.com/products/research-api
  ```bash
  social-trends config set TIKTOK_RESEARCH_TOKEN <your_token>
  ```
  Without this token, TikTok commands fall back to web scraping automatically.
