# CLI-Anything Social Trends — SOP Document

## Overview

`cli-anything-social-trends` is an agent-native CLI for scraping viral trends from YouTube and TikTok, generating hashtag strategies, tracking trending music/sounds, auditing and optimizing your social media accounts, and providing complete theme page creation + conversion playbooks.

---

## Architecture

```
social_trends_cli.py          # Click CLI entry point (REPL + subcommands)
core/
  youtube_scraper.py          # YouTube Data API v3 wrapper
  tiktok_scraper.py           # TikTokApi (playwright) + HTTP fallback
  hashtag_analyzer.py         # Cross-platform hashtag scoring + strategy
  music_tracker.py            # Trending sound/track detection + ranking
  account_optimizer.py        # Account auditing + optimization engine
  theme_page.py               # Theme page playbook + conversion guide
utils/
  social_backend.py           # Config, credentials, account registry, report caching
  repl_skin.py                # CLI branding + styled output (shared across all CLIs)
tests/
  test_core.py                # 100+ unit tests (no external deps)
  test_full_e2e.py            # End-to-end CLI tests (mocked HTTP)
```

---

## Backend Engines

### YouTube Data API v3
- Official Google API — requires free API key (10,000 units/day free tier)
- Endpoints used:
  - `videos.list` — trending videos by category and region
  - `search.list` — niche-targeted trending search
  - `channels.list` — channel stats for account audits
  - `playlistItems.list` — upload history for performance analysis
  - `videoCategories.list` — category ID mapping

### TikTokApi (Primary)
- Unofficial Python library using Playwright browser sessions
- Supports trending feed, hashtag videos, sound data
- Requires `playwright install chromium` once
- Optional `ms_token` cookie for enhanced access

### HTTP Fallback (TikTok)
- Direct HTTP scraping of TikTok public pages
- Parses `__UNIVERSAL_DATA_FOR_REHYDRATION__` JSON blob from HTML
- No authentication required — limited data, best-effort

---

## Key Design Decisions

### Stateless scraping, stateful config
- API credentials and account registry persisted at `~/.cli-anything-social-trends/`
- Reports saved as timestamped JSON files — queryable by type
- No database required — flat JSON files, zero-setup

### Dual-platform cross-correlation
- Hashtags and music trending on BOTH platforms get priority boost (1.5× score multiplier)
- Cross-platform correlation catches truly viral signals vs platform-specific noise

### Hashtag scoring formula
```
trend_score = (yt_count × 0.5 + tt_count × 1.5) × cross_platform_bonus
competition = tier(estimated_reach)  # niche/low/medium/high/mega
estimated_reach = (yt_count × 50,000) + (tt_count × 200,000)
```
TikTok weighted higher (1.5×) because TikTok signals virality faster than YouTube.

### Account optimization benchmarks
Engagement rate benchmarks by tier and platform (industry averages):
```
                YouTube     TikTok
micro (0-10K)    6.0%       9.0%
small (10K-100K) 3.5%       6.0%
mid (100K-1M)    2.0%       4.5%
large (1M+)      1.2%       3.0%
```

### Theme page revenue estimation
```
yt_adsense = (followers × 0.15 × 4 videos) / 1000 × niche_rpm
tt_fund    = (followers × 0.30 × 20 posts) / 1000 × 0.03
affiliates = followers × 0.001 × $5_avg_commission
brand_deals = (followers / 10,000) × $100_per_10k  [if ≥10K]
```

---

## Command Reference

```
cli-anything-social-trends [--json] <command>

setup
  youtube-key <KEY>           Store YouTube Data API v3 key
  tiktok-token <TOKEN>        Store TikTok ms_token cookie
  region <CODE>               Set default region (US, GB, AU, CA...)
  niche <NICHE>               Set default niche

accounts
  add <platform> <username>   Register an account for tracking
  remove <platform> <user>    Remove a registered account
  list                        Show all registered accounts

scrape
  youtube [--trending] [--niche NICHE] [--category ID] [--save]
  tiktok  [--trending] [--hashtag TAG] [--niche NICHE] [--save]
  all     [--niche NICHE]     Scrape both platforms, auto-save reports

hashtags
  strategy [--niche N] [--platform P] [--max-tags 30]
  compare  #tag1 #tag2 ...    Compare tags against scraped data

music
  trending [--platform P] [--limit 15]

optimize
  account <platform> <user> [--channel-id ID] [--niche N]
  all-accounts [--niche N]    Audit all registered accounts

theme-page
  plan <niche> [--platform P] [--followers N] [--page-name NAME]
  conversion-guide <niche>    Full step-by-step conversion guide
  branding <niche> <name>     Branding checklist

report
  list [--type TYPE]          List saved reports
  show <index|path>           Display a saved report

status                        Show configuration and account overview
```

---

## Supported Niches

fitness · food · travel · tech · beauty · gaming · motivation · finance · fashion · comedy

Each niche has pre-configured:
- Content pillars (5 core content types)
- Hashtag seed lists for TikTok and YouTube
- Posting schedules (optimal days + UTC hours)
- Monetization strategies and revenue estimates
- Reputable source accounts to monitor

---

## Data Flow

```
scrape youtube/tiktok
  → raw videos, hashtags, music saved to report files

hashtags strategy
  → reads latest yt + tt reports
  → HashtagAnalyzer cross-correlates signals
  → builds pillar/niche/micro tag buckets
  → outputs ready-to-paste tag block

optimize account
  → fetches live channel data (YouTube API / TikTok HTTP)
  → reads trending data from latest reports
  → AccountOptimizer computes ER vs benchmark
  → bio audit + content gap analysis
  → quick wins action list

theme-page plan
  → ThemePageConverter reads niche config
  → generates weekly calendar with trending sounds
  → calculates milestone roadmap and revenue estimate
  → full branding checklist and engagement pod guide
```

---

## Critical Implementation Notes

1. **YouTube API quota**: Each `videos.list` call = 1 unit. `search.list` = 100 units. Stay within 10K/day free tier by caching reports and re-using them.

2. **TikTok rate limiting**: Space requests ≥300ms apart. The HTTP fallback is rate-limited by TikTok; use Playwright mode for bulk scraping.

3. **ms_token refresh**: TikTok session tokens expire. If playwright mode fails, refresh token from browser cookies.

4. **Hashtag competition tiers**: The reach estimates are heuristics (50K per YouTube mention, 200K per TikTok mention). Real reach varies by niche — treat as directional signals, not exact counts.

5. **Revenue estimates**: All revenue figures are illustrative averages. Actual income depends heavily on niche RPM, audience geography, engagement quality, and negotiation skill.

6. **Content gaps**: Gap analysis compares video titles + tags against trending topics. Add more tags to your videos to reduce false positives.
