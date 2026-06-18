# cli-anything-social-media — Test Plan

## Test Coverage Summary

| Module | Unit Tests | E2E Tests | Status |
|--------|-----------|-----------|--------|
| core/trends.py | 7 | 2 | ✓ Planned |
| core/hashtags.py | 12 | 2 | ✓ Planned |
| core/music.py | 5 | 2 | ✓ Planned |
| core/theme_page.py | 10 | 0 | ✓ Planned |
| core/account_optimizer.py | 12 | 0 | ✓ Planned |
| core/scheduler.py | 6 | 0 | ✓ Planned |
| social_media_cli.py | 0 | 8 | ✓ Planned |

## Running Tests

```bash
# Install in dev mode
pip install -e ".[dev]"

# Unit tests only (no network)
pytest tests/test_core.py -v

# E2E tests (requires network)
pytest tests/test_full_e2e.py -v

# Full suite with coverage
pytest --cov=cli_anything.social_media --cov-report=term-missing
```

## Unit Test Design (test_core.py)

All unit tests in `test_core.py` run **without network access** and
**without real API keys**. They verify:

- Virality score calculation boundaries (0–100)
- Hashtag set generation for all known niches
- Hashtag deduplication and format validation
- Bio analysis scoring and suggestions
- Engagement rate calculation and tier classification
- Content calendar structure and day count
- Monetization roadmap phase coverage
- Scheduler CRUD operations (using tmp_path fixtures)
- CSV/JSON export correctness

## E2E Test Design (test_full_e2e.py)

End-to-end tests verify real API connectivity. They are **skipped**
when API credentials are not configured:

```python
@pytest.mark.skipif(not os.environ.get("YOUTUBE_API_KEY"), reason="No YouTube API key")
def test_youtube_trending_live():
    ...
```

### Covered E2E scenarios:
1. YouTube trending videos fetch (live API)
2. YouTube hashtag derivation from live trending data
3. TikTok hashtag scraping (web fallback)
4. TikTok sound scraping (web fallback)
5. Full trends scrape → aggregate → save → load cycle
6. CLI command integration: `cli-anything-social trends scrape --niche fitness`
7. CLI command: `hashtags generate --niche fitness --platform tiktok`
8. CLI command: `theme niches --interests fitness finance`

## Known Limitations

- **TikTok Playwright tests** require `pip install playwright && playwright install chromium`
- **TikTok web scraping** may be blocked by TikTok's anti-bot measures;
  the fallback to research-based data is always available
- **YouTube quota**: YouTube Data API v3 has a 10,000 unit/day free tier;
  tests use caching to minimize API calls
