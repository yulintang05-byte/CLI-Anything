# cli-anything-tiktok

CLI harness for TikTok — viral trends, hashtag analytics, music discovery, and account optimization from the terminal.

## Features

- **Trending videos** — fetch the FYP feed by region with hashtag and music breakdowns
- **Trending hashtags** — sorted by total views with keyword filtering
- **Trending music/sounds** — discover what sounds are going viral before they peak
- **Hashtag strategy builder** — generates a 6-tag mix (mega + niche + custom) for any niche
- **Hashtag analytics** — audience size, avg views per video, and usage recommendation
- **Account auditing** — followers, engagement rate, health score, and personalized recommendations
- **Optimization checklist** — profile, content strategy, growth tactics, and analytics tracking
- **Theme page guide** — 4-phase playbook: Foundation → Content Engine → Growth → Monetization
- **Niche analysis** — competition, CPM, best content formats, and affiliate product suggestions
- **Interactive REPL** — prompt_toolkit-powered shell with history and auto-suggest

## Installation

```bash
cd tiktok/agent-harness
pip install -e .
```

## API Keys

The CLI works in **demo mode** without any keys (returns sample data). For live data, configure one or both:

### RapidAPI Key (trending videos, music, hashtag analytics, account info)

1. Go to [rapidapi.com](https://rapidapi.com) and search for a TikTok API (e.g., "TikTok API6" or "TikTok Scraper")
2. Subscribe to a plan (free tiers available)
3. Copy your RapidAPI key from the dashboard

### Apify Token (trending hashtag scraper)

1. Sign up at [apify.com](https://apify.com)
2. Go to Settings → Integrations → API token
3. Copy your personal API token

### Configure keys

```bash
cli-anything-tiktok auth setup --rapidapi-key YOUR_KEY --apify-token YOUR_TOKEN
```

Or set environment variables:

```bash
export RAPIDAPI_KEY=your_key_here
export APIFY_TOKEN=your_token_here
```

## Usage

```bash
# Check configuration status
cli-anything-tiktok auth status

# Trending videos (US, top 20)
cli-anything-tiktok trends videos

# Trending videos for a different region
cli-anything-tiktok trends videos --region GB --limit 10

# Trending hashtags with keyword filter
cli-anything-tiktok trends hashtags --keyword fitness

# Trending music/sounds
cli-anything-tiktok trends music --region AU

# Build a hashtag strategy for your niche
cli-anything-tiktok trends hashtag-strategy --niche finance

# Analyze a specific hashtag
cli-anything-tiktok trends analyze-hashtag --hashtag fyp

# Audit a TikTok account
cli-anything-tiktok account audit @username

# Get the optimization checklist
cli-anything-tiktok account optimize

# Full theme page monetization guide
cli-anything-tiktok strategy theme-page

# Analyze a niche for theme page potential
cli-anything-tiktok strategy niche-analysis --niche luxury

# JSON output (pipe-friendly)
cli-anything-tiktok trends videos --json | jq '.top_hashtags_in_trending'

# Interactive REPL
cli-anything-tiktok repl
```

## Project Structure

```
tiktok/agent-harness/
├── setup.py
└── cli_anything/
    ├── __init__.py
    └── tiktok/
        ├── __init__.py
        ├── tiktok_cli.py          # Main Click CLI entrypoint
        ├── core/
        │   ├── __init__.py
        │   ├── trends.py          # Trending content discovery
        │   ├── account.py         # Account auditing & optimization
        │   └── strategy.py        # Theme page & niche strategy
        └── utils/
            ├── __init__.py
            ├── tiktok_backend.py  # HTTP data fetching layer
            └── repl_skin.py       # Shared REPL UI (cli-anything standard)
```
