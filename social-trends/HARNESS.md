# Social Trends — Tool SOP

## Overview

Social Trends is an agent-native CLI harness for scraping and tracking viral trends, generating
platform-optimized hashtag strategies, discovering trending music, optimizing social accounts, and
building converting theme pages across TikTok, YouTube, and Instagram.

## Architecture

| Module | Purpose |
|--------|---------|
| `core/trends.py` | Trend scraping (yt-dlp → seed fallback), local JSON cache |
| `core/hashtags.py` | Hashtag engine — niche × platform × goal optimization |
| `core/music.py` | Trending sounds/music database with use-case search |
| `core/account.py` | Account optimization checklists, posting schedules, growth roadmaps |
| `core/theme_page.py` | Theme page blueprints, monetization stacks, content calendars |

## Setup

```bash
cd social-trends/agent-harness
pip install -e .

# Optional: live YouTube trend scraping
pip install yt-dlp

# Verify
python3 -m cli_anything.social_trends --help
```

## Data Flow

```
trends fetch  →  tries yt-dlp (YouTube)  →  falls back to seed data (May 2026)
             →  saves to ~/.social-trends/trends_cache.json  (24h TTL)
trends list  →  reads cache  →  returns structured trend objects
```

All other modules (hashtags, music, account, theme_page) use built-in curated data and
require no live network access.

## Command Reference

### Trends
```bash
social-trends trends fetch --platform [all|tiktok|youtube]   # refresh cache
social-trends trends list --platform tiktok --status peaking  # filter
social-trends trends show tt_001                               # detail view
social-trends trends add --platform tiktok --title "My Trend" --hashtags "#fyp,#viral"
social-trends trends cache-info                                # cache metadata
```

### Hashtags
```bash
social-trends hashtags suggest --niche fitness --platform tiktok --goal viral
social-trends hashtags all-platforms --niche finance           # all 3 platforms at once
social-trends hashtags trending --platform instagram           # current trending tags
social-trends hashtags niches                                  # list all niches
```

### Music
```bash
social-trends music trending --platform tiktok
social-trends music search "phonk"
social-trends music by-use-case "morning routine"
social-trends music by-trend "Phonk Dance Challenge"
social-trends music genres
```

### Account
```bash
social-trends account optimize --platform youtube              # full checklist
social-trends account schedule --platform tiktok               # posting schedule
social-trends account analyze --platform instagram --niche fitness
social-trends account roadmap --platform tiktok --followers 2500
```

### Theme Page
```bash
social-trends theme-page niches                                # list profitable niches
social-trends theme-page create --niche ai_tools               # full blueprint
social-trends theme-page compare finance ai_tools fitness      # side-by-side
social-trends theme-page monetize --niche finance              # monetization playbook
social-trends theme-page content-calendar --niche motivation --days 30
```

### JSON output (for agents)
Every command supports `--json` flag:
```bash
social-trends --json hashtags suggest --niche tech --platform tiktok
social-trends --json theme-page create --niche finance
```

## Supported Niches

| Niche ID | Name | Monthly Potential |
|----------|------|------------------|
| `motivation` | Motivation / Mindset | $500-$5K |
| `finance` | Personal Finance / Wealth | $2K-$20K |
| `fitness` | Fitness / Body Transformation | $1K-$15K |
| `ai_tools` | AI Tools / Automation | $3K-$30K |
| `luxury_aesthetic` | Quiet Luxury / Aesthetic | $500-$8K |
| `crypto_web3` | Crypto / Web3 / DeFi | $5K-$50K |
| `gaming` | Gaming / Esports | $500-$10K |
| `food` | Food / Recipes / Cooking | $500-$7K |
| `self_improvement` | Self-Improvement / Productivity | $1.5K-$15K |

## Theme Page Conversion Playbook (May 2026)

1. **Pick a niche** — AI Tools and Finance are highest-RPM in 2026 with lowest saturation
2. **Platform selection** — TikTok for fastest growth; YouTube for highest ad revenue
3. **Account setup** — Complete 100% of critical checklist items before posting
4. **Content bank** — Create 10 pieces before going live; consistency beats volume
5. **Monetization from day 1** — Add affiliate link to bio immediately (no follower minimum)
6. **Stack revenue streams** — Creators with 3+ streams earn 3.2× more than single-stream
7. **Conversion hook** — Free digital product (PDF/template) captures email → backend funnel

## Known Limitations

1. **Live TikTok scraping**: TikTok blocks automated access; tool uses curated seed data
2. **Live YouTube**: Requires `yt-dlp` installed; falls back to seed data without it
3. **Cache TTL**: 24 hours — run `trends fetch --force` to bypass
4. **Music search**: Database is curated, not exhaustive; add trends with `trends add`

## Test Video / Test Data

Unit tests use `monkeypatch` to isolate cache from `~/.social-trends`. E2E tests
invoke the CLI as a subprocess using `python -m cli_anything.social_trends`.

```bash
cd social-trends/agent-harness
python -m pytest tests/ -v   # 77 tests (46 unit + 31 E2E), 100% pass rate
```
