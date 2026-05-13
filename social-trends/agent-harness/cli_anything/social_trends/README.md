# Social Trends CLI

Agent-native social media intelligence: scrape YouTube/TikTok viral trends, generate hashtag sets, optimize accounts, and build converting theme pages.

## Install

```bash
cd social-trends/agent-harness
pip install -e .
# Optional: yt-dlp fallback for YouTube scraping
pip install -e ".[scraper]"
```

## Quick Start

```bash
# Trending YouTube videos
social-trends trends youtube --category now --limit 20

# TikTok trending sounds
social-trends trends tiktok --sounds

# Full cross-platform trend report for a niche
social-trends trends report --niche fitness

# Optimized hashtag set
social-trends hashtags suggest fitness --platform tiktok

# Trending viral music
social-trends music trending --limit 10

# Music recommendations for your content type
social-trends music recommend "GRWM" --mood upbeat

# Optimal posting schedule
social-trends account schedule --platform tiktok --posts-per-week 7

# Account audit
social-trends account audit --platform tiktok --followers 5000 --posts 45 \
  --avg-views 800 --posts-per-week 3 --no-bio --no-audio

# Generate bio template
social-trends account bio fitness --platform tiktok --cta link

# Theme page niches ranked by monetization
social-trends theme-page niches --sort monetization

# Full guide for a niche
social-trends theme-page guide "Finance & Wealth"

# Conversion funnel
social-trends theme-page funnel --niche fitness

# Daily SOP
social-trends theme-page sop --niche beauty
```

## JSON Output

All commands support `--json` for agent-parseable output:

```bash
social-trends --json trends youtube | jq '.[] | {title, channel, views}'
social-trends --json hashtags suggest fitness | jq '.hashtags'
social-trends --json theme-page niches | jq '.[] | select(.monetization_potential == "$$$")'
```
