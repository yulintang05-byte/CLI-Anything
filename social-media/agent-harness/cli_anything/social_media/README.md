# cli-anything-social-media

A cli-anything harness for viral trend scraping, social media account optimization,
and theme page intelligence across YouTube and TikTok.

## Install

```bash
pip install yt-dlp          # Required dependency
pip install -e .            # Install this harness
```

## Commands

### Trend Scraping

```bash
# Scrape YouTube trending videos, hashtags, and music
cli-anything-social-media trends youtube
cli-anything-social-media trends youtube --category music --max 30
cli-anything-social-media trends youtube --region GB --json

# Scrape TikTok viral content by niche
cli-anything-social-media trends tiktok
cli-anything-social-media trends tiktok --niche fitness --max 50
cli-anything-social-media trends tiktok --niche finance --json

# Analyze a specific TikTok user
cli-anything-social-media trends user @username

# Research a specific hashtag
cli-anything-social-media trends hashtag fitness
```

### Cross-Platform Report

```bash
# Generate a full cross-platform viral intelligence report
cli-anything-social-media report
cli-anything-social-media report --niche fitness --region GB
cli-anything-social-media report --save report.json
```

### Account Optimization

```bash
# Register an account
cli-anything-social-media account add \
  --platform tiktok --username myaccount \
  --followers 5000 --niche fitness \
  --avg-views 10000 --posting-freq daily

# List registered accounts
cli-anything-social-media account list

# Optimize a specific account
cli-anything-social-media account optimize \
  --platform tiktok --username myaccount --with-trends

# Optimize ALL accounts at once
cli-anything-social-media account optimize-all --with-trends

# Save reports to a directory
cli-anything-social-media account optimize-all --save-dir ./reports
```

### Theme Pages

```bash
# Browse all available niches
cli-anything-social-media theme niches

# Get deep analysis for a niche
cli-anything-social-media theme niche --name fitness

# Generate full launch playbook
cli-anything-social-media theme playbook --niche motivation
cli-anything-social-media theme playbook --niche fitness --platform instagram

# Follower-to-revenue conversion strategies
cli-anything-social-media theme convert
cli-anything-social-media theme convert --difficulty beginner

# Compare niches side by side
cli-anything-social-media theme compare fitness finance travel
```

### Interactive REPL

```bash
cli-anything-social-media  # No args = interactive REPL
```

## Output Modes

Every command supports `--json` for machine-readable output:

```bash
cli-anything-social-media trends tiktok --niche fitness --json | jq '.top_hashtags[:5]'
cli-anything-social-media report --json > trend_report.json
```

## Architecture

```
cli_anything/social_media/
├── social_media_cli.py        # Main Click CLI + REPL
├── core/
│   ├── youtube_scraper.py     # YouTube trending content scraper
│   ├── tiktok_scraper.py      # TikTok viral content scraper
│   ├── trends_aggregator.py   # Cross-platform trend merger
│   ├── account_optimizer.py   # Account scoring & optimization engine
│   └── theme_pages.py         # Theme page playbooks & conversion strategies
├── utils/
│   ├── repl_skin.py           # Unified REPL UI
│   └── social_backend.py      # Dependency checks
└── tests/
    ├── TEST.md
    ├── test_core.py            # Unit tests
    └── test_full_e2e.py        # End-to-end tests
```
