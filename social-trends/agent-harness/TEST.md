# TEST.md — cli-anything-social-trends

## Test Summary

| Suite | Tests | Pass | Fail |
|-------|-------|------|------|
| Unit (test_core.py) | 40 | 40 | 0 |
| **Total** | **40** | **40** | **0** |

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```

## Test Coverage

### optimizer
- `score_trend`: zero engagement, high views, rising-trend bonus, score cap at 100
- `rank_trends`: descending sort, virality_score field added
- `build_hashtag_set`: niche seeds included, count within platform limits, trending tags in result, no duplicates, Instagram max respected
- `generate_posting_schedule`: returns list of dicts, required fields, posts_per_week respected, platform in schedule
- `generate_account_report`: report structure, non-empty checklist, 4 content pillars, unknown niche default pillars

### theme_pages
- `list_niches`: returns list, required fields, sort by difficulty
- `get_niche_detail`: exact match, fuzzy keyword match, not found returns None
- `get_playbook`: 7 steps, step filter
- `get_conversion_tips`: all categories present, single category filter

### config
- `load_config`: returns dict
- `load_accounts`: returns list
- `add_account`: stores entry, deduplicates by platform+handle
- `remove_account`: removes entry, returns False for missing

### youtube helpers
- `extract_trending_hashtags_from_titles`: from titles/descriptions, empty input, deduplication + counting

### tiktok helpers
- `_walk_for_hashtags`: empty dict, nested challengeName extraction
