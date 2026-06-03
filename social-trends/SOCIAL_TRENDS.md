# Social Trends Harness

Agent-native CLI for social media trend intelligence, account optimization, and theme page strategy.

## What It Does

- **Scrapes YouTube & TikTok** for viral videos, trending hashtags, and music
- **Optimizes all your accounts** with audit scores, bio generators, and posting schedules
- **Teaches theme pages** — from niche selection to converting funnels
- Works in **REPL mode** or as a one-shot CLI for AI agent pipelines

## Location

`social-trends/agent-harness/`

## Install

```bash
cd social-trends/agent-harness
pip install -e .
social-trends --help
```

## API Keys (Optional)

The tool works without API keys using demo data. Add keys for live scraping:

```bash
social-trends config set-key youtube YOUR_KEY       # YouTube Data API v3 (free)
social-trends config set-key tiktok_apify YOUR_KEY  # Apify (free tier)
social-trends config set-key rapidapi YOUR_KEY      # RapidAPI (free tier)
```

## Agent Usage

```bash
# Get viral hashtags for any niche (JSON for agent pipelines)
social-trends --json trends hashtags --niche fitness

# Full account audit
social-trends --json accounts audit tiktok_mypagename

# Get step-by-step conversion funnel
social-trends --json theme-page playbook dm_funnel --niche finance
```
