# cli-anything-youtube

CLI harness for YouTube — Trending videos, hashtags, music discovery & channel optimization.

Part of the [CLI-Anything](https://github.com/yourusername/cli-anything) framework for agent-native CLIs.

## Features

- **Trending videos** — Fetch mostPopular chart by region and category via YouTube Data API v3
- **Music discovery** — Trending music videos for use as Shorts/Reels audio
- **Hashtag research** — Search YouTube by hashtag with competition analysis
- **Topic trends** — Category-level trend signals with creator tips
- **Channel audit** — Subscriber/view health score + YPP eligibility check
- **Optimization checklist** — Branding, video SEO, growth tactics, analytics
- **Shorts strategy** — Formula, schedule, and repurposing workflow
- **Monetization roadmap** — 0 → $10K/month milestone guide
- **SEO strategy** — Niche-specific title formulas, keywords, and upload cadence
- **CPM guide** — Niche CPM ranges for monetization planning
- **Interactive REPL** — Persistent shell with history and autocomplete

## Setup

### 1. Get a YouTube Data API v3 key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Enable the **YouTube Data API v3**
4. Create an API key under **Credentials**

### 2. Install the harness

```bash
cd youtube/agent-harness
pip install -e .
```

### 3. Configure your API key

```bash
cli-anything-youtube auth setup --api-key YOUR_API_KEY
```

Or set the environment variable:

```bash
export YOUTUBE_API_KEY=YOUR_API_KEY
```

Without an API key the CLI runs in **demo mode** with sample data.

## Usage

```bash
# Check API key status
cli-anything-youtube auth status

# Trending videos (US, all categories)
cli-anything-youtube trends videos --region US --limit 10

# Trending music for Shorts audio
cli-anything-youtube trends music --region US

# Topic-level trend signals
cli-anything-youtube trends topics

# Hashtag research
cli-anything-youtube trends hashtag fitness --limit 20

# Audit a channel
cli-anything-youtube channel audit @MrBeast

# Full optimization checklist
cli-anything-youtube channel optimize

# Shorts growth strategy
cli-anything-youtube strategy shorts

# Monetization roadmap
cli-anything-youtube strategy monetization

# SEO strategy for a niche
cli-anything-youtube strategy seo --niche finance

# CPM guide by niche
cli-anything-youtube strategy cpm-guide

# JSON output (pipe-friendly)
cli-anything-youtube trends videos --json | jq '.trending_hashtags'

# Interactive REPL
cli-anything-youtube repl
```

## API Quota

The YouTube Data API v3 free tier provides **10,000 units/day**.

Approximate unit costs:
- `videos.list` (trending): 1 unit per call
- `search.list` (hashtag): 100 units per call
- `channels.list` (audit): 1 unit per call

For most use cases the free tier is sufficient.
