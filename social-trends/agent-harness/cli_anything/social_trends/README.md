# cli-anything-social-trends

**Social Media Trend Intelligence & Account Optimization CLI**

Scrape YouTube & TikTok for viral trends, hashtags, and music. Optimize your accounts. Build and convert niche theme pages — all from the command line.

## Features

- **YouTube Trending**: Scrape viral videos via yt-dlp (no API key) or YouTube Data API v3
- **TikTok Trending**: Fetch trending hashtags and sounds via TikTok web API
- **Hashtag Intelligence**: Cross-platform hashtag scoring, recommendations, and analysis
- **Trending Music**: Discover viral sounds with genre/mood classification and content use cases
- **Account Optimization**: Engagement rate analysis, monetization eligibility, bio generation, posting schedules
- **Theme Pages**: Complete niche database, conversion playbooks, content strategies, monetization timelines
- **JSON Output**: Every command supports `--json` for agent/automation consumption
- **Interactive REPL**: Persistent session with command history

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# No API keys required — works out of the box
cli-anything-social-trends trends tiktok --region US
cli-anything-social-trends trends youtube --region US --hashtags
cli-anything-social-trends hashtags recommend --niche fitness --platform tiktok
cli-anything-social-trends music trending --platform tiktok
cli-anything-social-trends accounts analyze --followers 5000 --avg-views 10000 \
    --avg-likes 800 --avg-comments 50 --platform tiktok
cli-anything-social-trends theme-page convert --from personal --to fitness --followers 2000
cli-anything-social-trends theme-page guide
```

## Optional API Keys

```bash
# Add YouTube Data API v3 for richer data (category filtering, tags, etc.)
cli-anything-social-trends auth setup --youtube-api-key YOUR_KEY_HERE

# Get a free YouTube API key at:
# https://console.cloud.google.com/apis/api/youtube.googleapis.com
```

## Command Reference

```
cli-anything-social-trends [--json] COMMAND [ARGS]...

  auth          API key management
    setup       Save API credentials
    status      Check configured credentials

  trends        Discover viral trends
    youtube     YouTube trending videos (yt-dlp or API)
    tiktok      TikTok trending hashtags + sounds
    all         Cross-platform trend summary

  hashtags      Hashtag strategy
    recommend   Get a niche-specific hashtag mix
    analyze     Audit a set of hashtags
    discover    Browse trending hashtags ranked by opportunity
    lookup      Look up stats for a specific hashtag

  music         Trending audio
    trending    Discover trending sounds by platform
    strategy    Get audio strategy for your niche

  accounts      Account optimization
    analyze     Full account audit with recommendations
    bio         Generate an optimized profile bio
    schedule    Get optimal posting times
    list        List saved account profiles
    load        Load a saved profile

  theme-page    Theme page toolkit
    niches      Browse profitable niches
    info        Detailed niche information
    convert     Step-by-step conversion playbook
    content     Content pillars and posting schedule
    guide       Complete theme page playbook
```

## Architecture

- **`core/youtube.py`** — YouTube scraper (yt-dlp + API)
- **`core/tiktok.py`** — TikTok scraper (web API + curated fallbacks)
- **`core/hashtags.py`** — Hashtag scoring, analysis, recommendations
- **`core/music.py`** — Trending sound discovery and strategy
- **`core/accounts.py`** — Account analysis and optimization engine
- **`core/theme_pages.py`** — Theme page niche database and playbooks
- **`utils/social_backend.py`** — HTTP sessions, config, caching
- **`utils/repl_skin.py`** — Unified REPL interface

## Data Sources

| Feature | Without API Key | With API Key |
|---------|----------------|--------------|
| YouTube Trending | yt-dlp (public feed) | YouTube Data API v3 (categories, tags) |
| TikTok Hashtags | Web scraping + curated | TikTok Research API |
| TikTok Sounds | Curated top charts | TikTok Music API |
| Analysis | Fully local | Fully local |

## License

MIT
