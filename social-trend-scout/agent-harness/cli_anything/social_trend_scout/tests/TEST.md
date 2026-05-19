# Social Trend Scout — Test Plan & Results

## Test Inventory

### Unit Tests (`test_core.py`) — 95 tests

| Module | Tests | Coverage |
|--------|-------|----------|
| YouTubeTrends | 12 | Hashtag extraction, video parsing, viral scoring, duration parsing |
| TikTokTrends | 8 | Fallback hashtags, niche seeds, Research API gating, date formatting |
| TrendAnalyzer | 10 | Hashtag merge, viral patterns, velocity classification, action plan |
| AccountOptimizer | 16 | Posting times, profile checklist, hashtag optimization, bio gen, engagement |
| ThemePageStrategy | 18 | All niches, launch checklist, first-30-days, sourcing, conversion, monetization |
| ContentCalendar | 12 | Day count, post count, fields, hashtag rotation, CSV rows, sprint |
| Session | 11 | API keys, cache TTL, account registry, dedup, preferences |
| OutputUtils | 8 | Number formatting, viral score emoji, table structure |

### E2E Tests (`test_full_e2e.py`) — 45 tests

| Group | Tests | Notes |
|-------|-------|-------|
| Config commands | 9 | set-key, add-account, list-accounts, clear-cache |
| Status command | 2 | table + JSON output |
| Optimize commands | 14 | All subcommands, all platforms, JSON variants |
| Theme-page commands | 15 | All niches, all subcommands, file output |
| Calendar commands | 9 | 7/30-day, CSV/JSON, multi-post, file save |
| Trends (graceful failure) | 3 | No-key behavior |

## Test Results

```
tests/test_core.py      — 95 passed
tests/test_full_e2e.py  — 45 passed
Total: 140 tests, 100% pass rate
```

Run tests:
```bash
cd agent-harness
pip install -e ".[test]"
pytest cli_anything/social_trend_scout/tests/ -v --tb=short
```

## Notes

- All unit tests use synthetic data — no external API calls
- E2E tests use Click's CliRunner — isolated from real filesystem via monkeypatch
- TikTok tests rely on fallback paths since Playwright/browser not available in CI
- YouTube API tests are skipped without a real API key; CLI exits with helpful error
