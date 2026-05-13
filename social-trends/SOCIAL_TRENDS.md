# Social Trends — Tool SOP

## Overview

Social Trends is an agent-native CLI harness for social media intelligence. It scrapes YouTube and TikTok for viral signals, generates optimized hashtag sets, recommends trending music, audits account health, and provides a complete playbook for building and monetizing theme pages.

**Use case:** Content creators, social media managers, and theme page operators who want to automate viral trend research and account optimization.

## Backend Analysis

| Concern | Solution |
|---------|----------|
| YouTube scraping | HTML scrape of `ytInitialData` JSON blob; yt-dlp fallback |
| TikTok scraping | Public explore API + `__NEXT_DATA__` HTML fallback |
| Hashtag intelligence | Curated niche banks + cross-platform volume estimates |
| Music tracking | Curated viral database with trend velocity, BPM, mood metadata |
| Account optimization | Evidence-based posting windows + content pillar framework |
| Theme page strategy | Conversion funnel, SOP, niche guides, monetization timelines |

## Setup

```bash
# System dependencies (optional — for yt-dlp fallback)
pip install yt-dlp

# Python package
cd social-trends/agent-harness
pip install -e .

# Verify
social-trends --help
```

## Command Reference

### Trends

```bash
# YouTube trending
social-trends trends youtube --category now|music|gaming|movies --limit 20

# TikTok trending
social-trends trends tiktok --limit 20
social-trends trends tiktok --sounds        # trending sounds only
social-trends trends tiktok --hashtags      # aggregate hashtags from videos

# Cross-platform report
social-trends trends report --niche fitness
```

### Hashtags

```bash
# Optimized set for a niche + platform
social-trends hashtags suggest fitness --platform tiktok
social-trends hashtags suggest beauty --platform instagram --no-viral

# Analyze existing hashtags
social-trends hashtags analyze "#fyp" "#fitness" "#gym" --platform tiktok

# Full cross-platform strategy
social-trends hashtags cross finance
```

### Music

```bash
# Trending viral tracks
social-trends music trending --platform tiktok --genre Pop --limit 10

# Recommend for content type
social-trends music recommend "workout highlights" --mood energetic
social-trends music recommend "GRWM"

# Weekly calendar
social-trends music calendar fitness
```

### Account

```bash
# Optimal posting schedule
social-trends account schedule --platform tiktok --posts-per-week 7

# Full account audit
social-trends account audit --platform tiktok \
  --followers 5000 --posts 45 --avg-views 800 \
  --posts-per-week 3.5 --bio --pic --no-link --uses-hashtags --no-audio

# Bio template
social-trends account bio fitness --platform tiktok --cta link
social-trends account bio beauty --platform instagram --cta shop

# Content pillars
social-trends account pillars finance --posts-per-week 7
```

### Theme Pages

```bash
# Rank niches
social-trends theme-page niches --sort monetization
social-trends theme-page niches --sort speed --difficulty Beginner

# Niche-specific guide
social-trends theme-page guide "Luxury & Cars"
social-trends theme-page guide "Finance & Wealth"

# Conversion funnel
social-trends theme-page funnel --niche fitness

# Daily/weekly SOP
social-trends theme-page sop --niche beauty
```

## Architecture

```
social-trends/agent-harness/
  cli_anything/social_trends/
    social_trends_cli.py   — Click CLI entry point (all commands)
    core/
      youtube.py           — YouTube HTML scraper + yt-dlp fallback
      tiktok.py            — TikTok public API + HTML scraper
      hashtags.py          — Hashtag intelligence + cross-platform strategy
      music.py             — Viral music database + content calendar
      account.py           — Posting schedules, audits, bios, content pillars
      theme_pages.py       — Niche guides, conversion funnel, SOP
    tests/
      test_core.py
```

## Agent Usage Patterns

```bash
# Agent: find best hashtags for a fitness post on TikTok
social-trends --json hashtags suggest fitness --platform tiktok | \
  jq '.hashtags | join(" ")'

# Agent: get top 5 trending sounds with their best content types
social-trends --json music trending --limit 5 | \
  jq '.[] | {title, best_content_types, trend_velocity}'

# Agent: audit an account and extract quick wins
social-trends --json account audit --platform tiktok --followers 2000 \
  --posts-per-week 1.5 --no-bio --no-audio | jq '.quick_wins'

# Agent: find the most beginner-friendly high-paying theme page niche
social-trends --json theme-page niches --sort monetization --difficulty Beginner | \
  jq '.[0] | {name, avg_monthly_revenue_at_10k, monetization_methods}'
```

## Ethical Notes

- YouTube scraping reads public trending pages (same as opening the tab in a browser)
- TikTok API endpoint used is the same public explore feed endpoint TikTok's own web app calls
- All curated music/hashtag data is based on publicly available trend information
- No authentication credentials are stored or required
- Always credit original creators when reposting content on theme pages
