# Social Media Tools — Test Plan & Results

## Test Summary

| Category | Tests | Status |
|---|---|---|
| Session persistence | 7 | ✅ PASS |
| Account optimizer | 8 | ✅ PASS |
| Theme page engine | 10 | ✅ PASS |
| Trend analyzer | 7 | ✅ PASS |
| YouTube scraper (unit) | 2 | ✅ PASS |
| TikTok scraper (unit) | 4 | ✅ PASS |
| CLI integration | 9 | ✅ PASS |
| **TOTAL** | **47** | **47/47 ✅** |

## Run Tests

```bash
cd social-media-tools/agent-harness
PYTHONPATH=. python3 -m pytest cli_anything/social/tests/test_core.py -v
```

## Test Coverage

### Unit Tests (no network)
- Session create/read/write/persistence/expiry
- Account profile analysis (bio, engagement, growth stages)
- Hashtag set generation (all sizes, niche inclusion, dedup)
- Theme page guide structure, 30-day plan, niche rankings
- Account value estimation (revenue multiplier, engagement bonus, niche premium)
- Hashtag merging, music merging, cross-platform detection
- YouTube view count parser, HTML extractor
- TikTok view count parser, item parser, JSON walker

### CLI Integration Tests
- `--help` invocation
- `--json` output purity (no status messages mixed in)
- `optimize account` → validates JSON schema
- `theme niches` → validates list structure  
- `theme value` → validates value estimate
- `optimize schedule` → validates schedule structure
- `accounts add/list` → validates persistence
- Missing required args → validates error exit code

## Live CLI Demo

```bash
# Get cross-platform trends
social trends combined --limit 20

# Generate hashtag set
social hashtags generate --niche fitness --platform tiktok

# Optimize an account
social optimize account -p tiktok -h @yourpage -n fitness \
  --bio "Your bio here" --followers 5000

# Get posting schedule
social optimize schedule -p youtube

# Theme page guide
social theme guide --niche finance
social theme niches
social theme value -p instagram -f 50000 -r 500 -e 4.2
```
