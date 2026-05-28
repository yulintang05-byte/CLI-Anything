# TEST.md — cli-anything-social-trends Test Plan and Results

## Test Strategy

| Layer | File | Coverage |
|-------|------|----------|
| Unit tests | `test_core.py` | All core module logic with synthetic data |
| E2E tests | `test_full_e2e.py` | Full CLI command invocation via Click test runner |
| CLI subprocess | `test_full_e2e.py::TestCLIInstalled` | Installed CLI binary (requires `CLI_ANYTHING_FORCE_INSTALLED=1`) |

## Unit Test Coverage (test_core.py)

### hashtags.py
- `TestViralityScore`: zero inputs, high scores, bounded 0-100, monotonicity
- `TestCompetitionLevel`: low/medium/high/oversaturated, boundary cases
- `TestRecommendHashtagMix`: TikTok/YouTube modes, unknown niches, all DB niches
- `TestAnalyzeHashtagSet`: too many tags, all-broad detection, score range, duplicates
- `TestRankHashtags`: sorting by opportunity, adds fields, empty list

### accounts.py
- `TestEngagementRate`: TikTok (includes shares), YouTube (excludes shares), zero views, grade labels, suggestions
- `TestAnalyzeAccount`: required keys, score range, recommendations list, follow ratio, zero followers safety
- `TestMonetizationEligibility`: TikTok Creator Rewards, TikTok Shop, YouTube YPP, small account
- `TestGenerateBio`: returns string, TikTok char limit, Instagram char limit, custom CTA, tips present

### theme_pages.py
- `TestNicheDatabase`: returns list, required keys, fitness profitability
- `TestGetNicheInfo`: exact match, partial match, unknown niche defaults
- `TestConversionPlaybook`: hard_pivot (small), gradual_pivot (medium), start_fresh (large), all sections, roadmap not empty, 10 branding items
- `TestContentPillars`: pillars present, 10+ ideas, 7-day schedule, viral formats

### music.py
- `TestMusicClassification`: hip-hop, pop, k-pop, unknown→other
- `TestMoodClassification`: hype, emotional, neutral default
- `TestSoundStrategy`: fitness→hip-hop, 3+ tips, unknown niche defaults

### tiktok.py
- `TestTikTokHelpers`: hashtag extraction, engagement rate, zero plays, fallback hashtags/sounds, video normalization

### youtube.py
- `TestYouTubeHelpers`: yt-dlp normalization, zero views ER, hashtag extraction from videos, categories dict

### social_backend.py
- `TestSocialBackend`: cache set/get, cache miss, empty config, save/load config, session headers, API raises without key

## E2E Test Coverage (test_full_e2e.py)

### Auth commands
- `auth status` — no keys, JSON mode
- `auth setup` — saves key to config

### Trends commands
- `trends tiktok` — output, JSON, with sounds
- `trends youtube` — output, JSON

### Hashtag commands
- `hashtags recommend` — fitness/tiktok, unknown niche, JSON
- `hashtags analyze` — good set, too many tags, JSON
- `hashtags discover` — ranked output
- `hashtags lookup` — single tag stats

### Music commands
- `music trending` — TikTok, JSON
- `music strategy` — fitness, JSON

### Accounts commands
- `accounts analyze` — basic, JSON, monetization eligibility
- `accounts bio` — fitness/tiktok, JSON
- `accounts schedule` — TikTok, JSON
- `accounts list` — empty profiles

### Theme page commands
- `theme-page niches` — list, JSON, sort by competition
- `theme-page info` — fitness, JSON
- `theme-page convert` — small (hard pivot), large (start fresh), JSON
- `theme-page content` — cooking, JSON (10+ ideas)
- `theme-page guide` — full guide output

## Test Results

```
================================ Test Summary ================================
test_core.py           87 passed  ✅
test_full_e2e.py       40 passed  ✅
──────────────────────────────────────────────────────────────────────────────
TOTAL                 127 passed  ✅   100% pass rate
```

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"

python -m pytest cli_anything/social_trends/tests/ -v
```
