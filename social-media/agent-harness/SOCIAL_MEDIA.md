# Social Media Harness — Architecture & Methodology

## Overview

The Social Media harness follows the cli-anything 7-phase pipeline to deliver:

1. **YouTube + TikTok viral trend scraping** — trending videos, hashtags, sounds
2. **Cross-platform intelligence reports** — unified signals from both platforms
3. **Account optimization engine** — scored analysis with concrete action plans
4. **Theme page playbooks** — step-by-step guide to building and monetizing theme pages

## Backend Selection

**yt-dlp** was chosen as the primary backend because:
- Zero API keys required — works immediately
- Supports both YouTube and TikTok natively
- Extracts rich metadata: views, likes, comments, music, hashtags, duration
- Open source, actively maintained, battle-tested

Optional enhancements (future phases):
- YouTube Data API v3 — for official trending lists by country
- TikTok Research API — for creators with approved access
- RapidAPI TikTok scrapers — for higher volume commercial use

## Module Architecture

### youtube_scraper.py
- Uses `yt-dlp --dump-json` for video metadata extraction
- Flat-playlist mode for efficient trending page scraping
- Falls back to `ytsearch{N}:query` if trending page requires auth
- Extracts hashtags from title, description, and tags fields
- Detects background music via regex patterns in description
- Computes engagement rate: (likes + comments) / views × 100

### tiktok_scraper.py
- Uses `tiktoksearch{N}:query` via yt-dlp for niche-based discovery
- User feed scraping via profile URL
- Computes virality score: weighted combination of raw plays, share ratio, follower multiplier
- Generates content strategy from aggregated trend signals

### trends_aggregator.py
- Merges YouTube + TikTok hashtag scores with platform-specific weighting
- TikTok tags weighted 1.2× (stronger viral amplifier for discovery)
- Cross-platform tags receive 1.5× bonus (validated on both platforms)
- Produces `CrossPlatformReport` with a prioritized action plan

### account_optimizer.py
- Local account registry stored in `~/.cli-anything-social-media/accounts.json`
- Scoring rubric (0-100) across 6 dimensions:
  - Profile completeness (20%)
  - Content strategy (15%)
  - Hashtag quality (15%)
  - Posting consistency (20%)
  - Engagement health (20%)
  - Growth trajectory (10%)
- Platform-specific benchmarks for YouTube, TikTok, and Instagram
- Generates: critical fixes, quick wins, strategic recommendations,
  hashtag overhaul plan, bio rewrite, 7-day content calendar, monetization paths

### theme_pages.py
- Niche database: 8 monetization-ranked niches with CPM, commission, and growth data
- 4-phase launch playbook: Launch (1-7) → Grow (8-30) → Scale (31-90) → Monetize (90+)
- 5 conversion strategies: bio funnels, shoutouts, affiliate stacks, digital products, communities
- Hashtag rotation sets and bio templates ready to copy-paste

## Data Flow

```
scrape_youtube_trending()  ──┐
                              ├──→ generate_cross_platform_report()
scrape_tiktok_trending()   ──┘         │
                                        ▼
                              CrossPlatformReport
                                        │
                                        ▼
                              optimize_account(account, trending_tags)
                                        │
                                        ▼
                              OptimizationReport → CLI output / JSON
```

## Testing Strategy

- **Unit tests**: Synthetic data, no network calls — test parsing, scoring, aggregation logic
- **E2E tests**: Real yt-dlp calls — FAIL (not skip) if yt-dlp not installed
- Both test suites must pass before any release

## Zero Configuration

```bash
pip install yt-dlp
pip install -e .
cli-anything-social-media --help
```
