# Viral Trends — Tool SOP

## Overview

Viral Trends is an agent-native harness for scraping YouTube and TikTok to surface trending hashtags, music, and content. It feeds directly into account optimization and theme page strategy.

**Use case:** Identify what's going viral right now → apply it to your accounts → grow theme pages faster.

## Backend Analysis

| Concern | Solution |
|---------|----------|
| YouTube trending | `yt-dlp --flat-playlist` on trending feed URLs |
| TikTok hashtag videos | `yt-dlp --flat-playlist` on `/tag/<hashtag>` pages |
| Hashtag extraction | Regex `#(\w+)` on title + description + tags |
| Cross-platform ranking | Composite score: TikTok 60% + YouTube 40% weighting |
| Music/sounds | Parse `track` + `artist` fields from yt-dlp metadata |
| Account optimization | Rules engine: posting windows, hashtag mix, bio templates |
| Theme page guide | Structured 7-step knowledge base with monetization tiers |

## Setup

```bash
# System dependency
apt install yt-dlp        # Ubuntu
brew install yt-dlp       # macOS
pip install yt-dlp        # pip (any OS)

# Python package
cd viral-trends/agent-harness
pip install -e .

# Verify
viral-trends --version
viral-trends --help
```

## Command Reference

### Fetch Trending Content

```bash
# YouTube trending (general, music, gaming, films)
viral-trends trending youtube --category music --limit 20

# TikTok top videos for a hashtag
viral-trends trending tiktok --hashtag fitness --limit 10
```

### Hashtag Intelligence

```bash
# Top hashtags from YouTube trending
viral-trends hashtags youtube --category general

# Top hashtags from TikTok
viral-trends hashtags tiktok --hashtag gym

# BEST: Cross-platform merged ranking (YouTube + TikTok combined score)
viral-trends hashtags cross-platform --yt-category general --tt-hashtag fitness --limit 20
```

### Trending Music / Sounds

```bash
# Rank trending sounds from TikTok videos in a niche
viral-trends music tiktok --hashtag motivation --limit 30
```

### Account Optimization (Full Audit)

```bash
# Run a full optimization audit for your platform + niche
viral-trends optimize \
  --platform tiktok \
  --niche "fitness" \
  --tt-hashtag gym \
  --niche-tags "mygym,fitcheck" \
  --cta "free workout plan below"
```

Returns:
- Optimal posting schedule (UTC windows)
- Curated hashtag set (cross-platform strategy)
- Content pillar breakdown (30/40/15/15% split)
- Optimized bio template

### Niche Opportunity Detection (Proactive)

```bash
# Find hashtags blowing up on TikTok but underused on YouTube
# = untapped cross-posting goldmine
viral-trends niche-opps --tt-hashtag finance --yt-category general
```

### Theme Page Playbook

```bash
# Full 7-step guide + monetization stack
viral-trends theme-pages guide

# Just one step
viral-trends theme-pages step 3

# Monetization timeline only
viral-trends theme-pages monetize

# Content pillar framework for your niche
viral-trends theme-pages content-pillars "luxury lifestyle"
```

## Theme Page Quick Reference

| Milestone | Action |
|-----------|--------|
| 0 → 1k   | Post 3x/day, trending audio every post, reply to all comments |
| 1k → 10k | Pin a "start here" video, giveaway at 5k, test affiliate links |
| 10k+     | TikTok Creator Fund, brand DMs, digital product launch |
| 50k+     | Sponsorships $50–$500/post, paid community (Discord/Whop) |
| 100k+    | Course launch, newsletter, agent/tool licensing |

## Workflow: Proactive Weekly Trend Run

```bash
#!/usr/bin/env bash
NICHE="fitness"
PLATFORM="tiktok"

# 1. Pull cross-platform trends
viral-trends hashtags cross-platform \
  --yt-category general \
  --tt-hashtag "$NICHE" \
  --limit 25 \
  --top 15 > trends.json

# 2. Find niche opportunities
viral-trends niche-opps \
  --tt-hashtag "$NICHE" \
  --limit 25 > opps.json

# 3. Get trending sounds
viral-trends music tiktok \
  --hashtag "$NICHE" \
  --limit 30 > sounds.json

# 4. Full account audit
viral-trends optimize \
  --platform "$PLATFORM" \
  --niche "$NICHE" \
  --tt-hashtag "$NICHE" > audit.json

echo "Trend report ready: trends.json, opps.json, sounds.json, audit.json"
```

## Converting Theme Page Metrics

Track these to know if your theme page is converting:

| Metric | Target |
|--------|--------|
| Save rate (saves ÷ views) | >3% |
| Follow rate (follows ÷ views) | >1% |
| Link click rate (clicks ÷ profile visits) | >10% |
| Watch time | >50% on TikTok, >40% on Reels |

## Known Limitations

1. **TikTok rate limits:** Scraping too many videos in quick succession may get temporarily blocked. Add `--limit 10` for initial runs.
2. **yt-dlp updates:** TikTok frequently changes its site structure. Run `pip install -U yt-dlp` if scraping fails.
3. **YouTube auth:** Some trending categories require cookies. Pass `--cookies-from-browser chrome` to yt-dlp if needed.
4. **Music metadata:** Not all TikTok videos expose track/artist metadata via yt-dlp — "original sound" is filtered out automatically.
