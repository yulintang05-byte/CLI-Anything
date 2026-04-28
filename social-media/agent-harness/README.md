# cli-anything-social-media

A fully stateful CLI for social media automation: scrape YouTube and TikTok viral trends, audit and optimize accounts using 2026 algorithm research, and generate complete theme page conversion plans.

## Install

```bash
pip install -e .
# With yt-dlp for deeper YouTube scraping:
pip install -e ".[ytdlp]"
```

## Commands

### Trend Scraping

```bash
# YouTube trending (now / music / gaming / movies)
cli-anything-social-media trends youtube --category music --limit 20

# TikTok trending hashtags (live scrape + curated fallback)
cli-anything-social-media trends tiktok --niche fitness --limit 30

# Cross-platform analysis (YouTube + TikTok merged)
cli-anything-social-media trends analyze --niche business

# Specific TikTok hashtag deep-dive
cli-anything-social-media trends hashtag fitness

# Single YouTube video metadata + hashtags
cli-anything-social-media trends video https://www.youtube.com/watch?v=VIDEO_ID
```

### Account Optimization

```bash
# Full account audit with recommendations
cli-anything-social-media optimize audit \
  --platform tiktok \
  --username @myaccount \
  --followers 10000 \
  --avg-views 2500 \
  --avg-shares 30 \
  --avg-saves 80 \
  --posts-per-week 4 \
  --niche fitness \
  --bio-cta \
  --link-in-bio

# Show platform algorithm signals
cli-anything-social-media optimize signals tiktok

# Best posting times
cli-anything-social-media optimize times tiktok
```

### Theme Page Creation

```bash
# Full theme page plan with 90-day roadmap
cli-anything-social-media theme create --niche finance --archetype educator

# List niches by monetization score
cli-anything-social-media theme niches

# Conversion funnel walkthrough
cli-anything-social-media theme funnel

# Content calendar
cli-anything-social-media theme calendar --niche business --weeks 4 --posts-per-week 4
```

### JSON Output (for agents)

All commands support `--json` flag for structured JSON output:

```bash
cli-anything-social-media --json trends analyze --niche fitness
cli-anything-social-media --json theme create --niche finance --archetype educator
```

### Interactive REPL

```bash
cli-anything-social-media repl
```

## Architecture

```
social-media/agent-harness/
└── cli_anything/social_media/
    ├── social_media_cli.py      # Main CLI entry point (Click)
    ├── core/
    │   ├── session.py           # Workspace state + undo/redo
    │   ├── youtube_scraper.py   # YouTube trending scraper
    │   ├── tiktok_scraper.py    # TikTok hashtag/sound scraper
    │   ├── trend_analyzer.py    # Cross-platform trend merging + scoring
    │   ├── account_optimizer.py # 2026 algorithm audit + recommendations
    │   └── theme_page.py        # Theme page plans + conversion funnels
    └── utils/
        └── repl_skin.py         # Interactive REPL interface
```

## 2026 Algorithm Key Facts

**TikTok**: Completion rate (70%+ target), shares, saves are the top 3 signals. 3-4 quality posts/week beats daily volume. Spoken keywords are indexed for search.

**YouTube Shorts**: Completion rate + low swipe-away rate = primary distribution signals.

**Instagram Reels**: Shares > saves > completion > comments > likes in 2026.

**Theme Pages**: Focus on niche specificity → build trust → offer lead magnet → convert. The AI Tools niche scores 99/100 monetization potential in 2026.
