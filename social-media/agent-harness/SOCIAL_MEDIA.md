# CLI-Anything Social Media

**Agent-native social media growth toolkit** — viral trend discovery, hashtag optimizer, account auditor, content calendar, and the complete theme-page monetization playbook.

---

## Install

```bash
cd social-media/agent-harness
pip install -e .

# Optional: Google Trends + YouTube live scraping
pip install -e ".[trends]"
```

---

## Commands

### Trends

```bash
# YouTube trending (uses yt-dlp if installed, otherwise curated fallback)
social-media trends youtube --region US --limit 15

# TikTok trending hashtags with growth %
social-media trends tiktok-hashtags --limit 20

# TikTok trending sounds / music with BPM
social-media trends tiktok-sounds --limit 10

# Google Trends interest comparison (requires pytrends)
social-media trends google --keywords "fitness,gym,calisthenics" --geo US --timeframe "now 7-d"
```

### Hashtags

```bash
# Generate optimized hashtag set (mix strategy: mega + large + medium + niche)
social-media hashtags get --niche fitness --platform tiktok --max 25

# Audit your existing hashtags for banned/shadowban tags
social-media hashtags audit "#fyp #like4like #follow4follow #gym"

# List all available niche databases
social-media hashtags list-niches
```

**Available niches:** `fitness`, `finance`, `lifestyle`, `business`, `food`, `tech`, `themepage`, `beauty`, `travel`

### Account Optimizer

```bash
# Full account audit with score, grade, and priority action list
social-media optimize audit \
  --platform tiktok \
  --followers 12000 \
  --views 45000 \
  --likes 800 \
  --comments 50 \
  --days-per-week 5 \
  --has-cta-bio \
  --has-link-bio

# Optimal posting schedule (adjusted to your timezone)
social-media optimize schedule --platform tiktok --tz-offset -5   # EST
social-media optimize schedule --platform instagram --tz-offset 1  # CET

# Bio generator
social-media optimize bio \
  --platform tiktok \
  --account-type themepage \
  --niche motivation \
  --audience "young entrepreneurs" \
  --outcome "build their dream life"

# Full platform specs (algorithm signals, growth tactics, video lengths)
social-media optimize specs --platform tiktok
social-media optimize specs --platform instagram
social-media optimize specs --platform youtube
```

### Content Tools

```bash
# Generate viral hooks for your niche
social-media content hooks --niche finance --type curiosity --count 5
social-media content hooks --niche fitness --type all --count 10

# Hook types: all, curiosity, fear_of_missing_out, aspirational, educational, social_proof

# 2-week content calendar with daily post types and hooks
social-media content calendar --niche motivation --weeks 2
social-media content calendar --niche fitness --weeks 4 --start 2025-06-01

# Fill-in-the-blank viral post templates
social-media content templates --niche finance
```

### Theme Page Playbook

```bash
# Full overview + 30-day action plan
social-media theme-pages playbook

# Detailed stage instructions (stages 1-6)
social-media theme-pages stage --number 1   # Niche Selection
social-media theme-pages stage --number 2   # Account Setup
social-media theme-pages stage --number 3   # Content System
social-media theme-pages stage --number 4   # Growth Tactics
social-media theme-pages stage --number 5   # Monetization
social-media theme-pages stage --number 6   # Scaling

# Monetization methods + revenue benchmarks by follower count
social-media theme-pages monetization

# Full tools stack (CapCut, Canva, Stan.store, etc.)
social-media theme-pages tools

# Copyright rules — how to avoid DMCA strikes
social-media theme-pages copyright

# Content pillars by niche
social-media theme-pages content-pillars --niche motivation
```

### JSON Output (for agents)

Add `--json` to any command:

```bash
social-media --json trends tiktok-hashtags --limit 10
social-media --json hashtags get --niche fitness
social-media --json optimize audit --platform tiktok --followers 50000 --views 100000 --likes 2000 --comments 100 --days-per-week 7
```

### Interactive REPL

```bash
social-media repl
```

---

## Architecture

```
cli_anything/social_media/
  cli.py                    ← Click CLI entry point
  core/
    trends.py               ← YouTube (yt-dlp/RSS), TikTok, Google Trends
    hashtags.py             ← Niche hashtag DB + mix strategy + audit
    optimizer.py            ← Account audit, posting schedule, bio gen
    content.py              ← Hook library, calendar, viral templates
    theme_pages.py          ← Full theme page playbook (6 stages)
```

---

## Live Data Sources

| Source | Method | Requires |
|--------|--------|---------|
| YouTube Trending | `yt-dlp` scrape | `pip install yt-dlp` |
| YouTube Trending (fallback) | RSS feed | nothing |
| TikTok Trending Hashtags | TikTok Creative Center | nothing (link provided) |
| TikTok Trending Sounds | Curated chart data | nothing |
| Google Trends | `pytrends` | `pip install pytrends` |
| Billboard/Charts | Curated + link | nothing |

For **live TikTok data**, always visit:
- Hashtags: https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en
- Sounds: https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en
- Videos: https://ads.tiktok.com/business/creativecenter/inspiration/popular/creator/pc/en

---

## Running Tests

```bash
cd social-media/agent-harness
pip install -e ".[dev]"
pytest tests/ -v
```

---

## Theme Page Revenue Benchmarks

| Followers | Monthly Revenue |
|-----------|----------------|
| 10K | $50–200 (affiliate + small shoutouts) |
| 50K | $200–800 (shoutouts + affiliate + digital product) |
| 100K | $500–2,500 (brand deals + all above) |
| 500K | $2,000–10,000 (premium brand deals) |
| 1M+ | $5,000–30,000+ |
