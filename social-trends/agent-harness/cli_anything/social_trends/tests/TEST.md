# Test Plan — cli-anything-social-trends

## Scope

All tests use synthetic data and mock network calls. No real API keys or internet
access are required.

## Test Categories

### Unit Tests (`test_core.py`) — 55 tests

| Module | Tests | Description |
|---|---|---|
| `youtube_trends` | 10 | YouTubeVideo dataclass, URL construction, engagement rate, tag extraction, category ID mapping, duration parsing, list_categories |
| `tiktok_trends` | 7 | TikTokHashtag/Sound/Video dataclasses, URL building, region/niche lists |
| `hashtag_analyzer` | 12 | Scoring pipeline, recommendation marking, caption set building, niche suggestion, cross-platform merge |
| `music_tracker` | 8 | TrackEntry virality labels, to_dict, merge logic, genre identification |
| `account_optimizer` | 7 | Checklist generation, priority presence, schedule sorting, bio templates |
| `theme_page` | 11 | Niche ranking/sorting, roadmap phases, conversion funnel stages, ethics guide |

### E2E CLI Tests (`test_full_e2e.py`) — 27 tests

| Command | Tests |
|---|---|
| `trends fetch youtube` | 5 (exit code, output content, JSON, tag display, error handling) |
| `trends fetch tiktok` | 2 (exit code, JSON structure) |
| `hashtags suggest` | 3 (curated fallback, JSON, count) |
| `music trending` | 2 (exit code, JSON) |
| `account optimize` | 2 (checklist display, JSON) |
| `account schedule` | 1 |
| `account bio` | 1 |
| `theme-page niches` | 2 |
| `theme-page strategy` | 2 |
| `theme-page convert` | 1 |
| `theme-page ethics` | 2 |
| `--version`, `--help`, subcommand help | 3 |

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```

## Test Results

```
=============== 82 passed in X.Xs ===============
```
