# trends-scout

Viral trend intelligence CLI for YouTube & TikTok. Scrapes trending videos,
hashtags, and music. Optimizes account strategy. Full theme page conversion playbook.

## Install

```bash
cd trends-scout/agent-harness
pip install -e .
```

## Quick Start

```bash
# All-in-one trend scan (no setup required)
trends-scout scan --region US --niche fitness --platform both

# TikTok trending
trends-scout tiktok trending
trends-scout tiktok hashtags
trends-scout tiktok sounds

# YouTube trending
trends-scout youtube trending --region US
trends-scout youtube hashtags
trends-scout youtube music

# Cross-platform viral music
trends-scout music viral
trends-scout music cross-hits

# Account optimization
trends-scout account add --platform tiktok --handle @yourpage --niche fitness
trends-scout account optimize
trends-scout account hashtags --niche fitness --platform tiktok --live

# Theme page strategy
trends-scout theme-page learn          # Crash course
trends-scout theme-page niches         # Best niches ranked
trends-scout theme-page strategy --niche motivation
trends-scout theme-page monetize --platform tiktok
trends-scout theme-page repurpose --platform tiktok_video

# Interactive mode
trends-scout repl
```

## API Keys (All Optional)

Works without any API keys. Keys unlock higher quality data:

```bash
# YouTube Data API v3 — free at console.developers.google.com
trends-scout config set-key youtube_api_key YOUR_KEY

# TikTok Research API — apply at developers.tiktok.com
trends-scout config set-key tiktok_client_key YOUR_KEY
trends-scout config set-key tiktok_client_secret YOUR_SECRET

# Last.fm (free) — last.fm/api/account/create
trends-scout config set-key lastfm_api_key YOUR_KEY

# Spotify — developers.spotify.com
trends-scout config set-key spotify_client_id YOUR_ID
trends-scout config set-key spotify_client_secret YOUR_SECRET
```

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
trends-scout --json tiktok trending | jq '.top_hashtags'
trends-scout --json account audit --platform tiktok --handle @page --niche fitness
```
