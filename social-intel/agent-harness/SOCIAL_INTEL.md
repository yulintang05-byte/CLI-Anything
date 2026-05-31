# social-intel Agent Harness

CLI harness for **social media intelligence** — scrape YouTube and TikTok for viral trends, optimize accounts, and build converting theme pages.

## What it does

| Command group | Purpose |
|---|---|
| `youtube trending` | YouTube Data API v3 — mostPopular chart + extracted hashtags |
| `youtube music` | Trending music videos with TikTok-safe audio indicator |
| `youtube hashtag` | Engagement + competition analysis for any hashtag |
| `tiktok trending` | Public discover page — trending sounds and hashtag challenges |
| `tiktok hashtag` | TikTok hashtag view count, video count, opportunity score |
| `tiktok search` | Research API — videos by keyword with top hashtags and sounds |
| `optimize` | Full account optimization report (times, hooks, bio, hashtags, checklist) |
| `theme niches` | Score 10 niches by monetization, competition, CPM |
| `theme niche` | Deep-dive: sub-niches, affiliate programs, content sources, hooks |
| `theme roadmap` | Monetization path by follower tier (0–1K → 100K+) |
| `theme funnel` | AIDA conversion funnel: Awareness → Retention |
| `theme curation` | Legal guidelines, free sources, tools (CapCut, Canva, Buffer) |
| `theme calendar` | 1-week content calendar with content types and CTAs |

## Install

```bash
cd social-intel/agent-harness
pip install -e .
```

## Setup

### YouTube (required for `youtube` commands)

1. Go to [console.developers.google.com](https://console.developers.google.com)
2. Create a project → Enable **YouTube Data API v3**
3. Create an API key (free, 10,000 units/day quota)

```bash
social-intel auth setup --youtube-api-key YOUR_KEY
```

### TikTok Research API (optional, for `tiktok search`)

1. Apply at [developers.tiktok.com/application/research-api](https://developers.tiktok.com/application/research-api)
2. Approval takes 1–2 weeks

```bash
social-intel auth setup --tiktok-api-key YOUR_BEARER_TOKEN
```

> **Note:** `tiktok trending` and `tiktok hashtag` work without an API key via public endpoints, but TikTok rate-limits aggressively — results are cached locally on success.

## Usage examples

```bash
# YouTube trending videos (US, all categories)
social-intel youtube trending --region US --category all --count 25

# Trending music with TikTok-safe indicator
social-intel youtube music --region US

# Analyze a hashtag competition level
social-intel youtube hashtag fitness --count 20

# TikTok trending sounds + hashtag challenges
social-intel tiktok trending --region US

# TikTok hashtag opportunity score
social-intel tiktok hashtag gymtok

# Research API: viral videos for keywords
social-intel tiktok search -k viral -k fyp -k trending --count 50

# Full optimization report — JSON
social-intel --json optimize --platform tiktok --niche fitness

# Niche scoring
social-intel theme niches
social-intel theme niche finance_crypto

# Monetization roadmap for your follower count
social-intel theme roadmap --followers 8000

# Conversion funnel
social-intel theme funnel

# Legal curation guide + tools
social-intel theme curation

# 7-day content calendar
social-intel theme calendar --niche fitness --platform tiktok --posts-per-week 14

# Interactive REPL
social-intel repl

# All output as JSON (pipe-friendly)
social-intel --json youtube trending --region US | python -m json.tool
```

## Architecture

```
social-intel/agent-harness/
├── cli_anything/social_intel/
│   ├── social_intel_cli.py      # Click CLI entry point + REPL
│   ├── core/
│   │   ├── youtube.py           # YouTube Data API v3 client
│   │   ├── tiktok.py            # TikTok Research API + public scraper
│   │   ├── optimizer.py         # Account optimization engine
│   │   └── theme_pages.py       # Niche scoring, monetization, curation
│   └── utils/
│       ├── backend.py           # Config/cache persistence
│       └── repl_skin.py         # REPL prompt styling
└── tests/
    ├── test_core.py             # Unit tests (no API keys needed)
    └── test_full_e2e.py         # CLI integration tests (no API keys needed)
```

## Credentials

Stored at `~/.cli-anything/social-intel/config.json` (never committed).

Cache files saved at `~/.cli-anything/social-intel/*.cache.json` — the TikTok scraper falls back to cache on rate-limit.

## Available niches (theme pages)

`fitness` · `cars` · `motivational_quotes` · `travel` · `food` · `luxury_lifestyle` · `pets` · `finance_crypto` · `gaming` · `fashion`

Each niche includes: sub-niches, monetization score, competition level, average CPM, best platforms, affiliate programs, content sources, and hook topics.

## Tests

```bash
cd social-intel/agent-harness
pytest tests/ -v
```

All 49 tests pass without any API keys — only the live `youtube` and `tiktok search` commands require credentials.
