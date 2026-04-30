# Social Media CLI — Agent Harness

> **CLI-Anything** harness for viral trend scraping, hashtag optimization, account growth, and theme page conversion.

## What This Does

This harness gives AI agents (and humans) a structured CLI to:

1. **Scrape viral trends** from YouTube and TikTok — trending videos, hashtags, sounds, and creator data
2. **Generate optimized hashtag sets** for any niche and platform with reach scoring
3. **Identify trending music/sounds** to maximize algorithmic distribution
4. **Optimize social media accounts** with full audit: bio, posting schedule, hooks, monetization roadmap
5. **Convert theme page followers to customers** via a proven 5-stage funnel with DM scripts

## Architecture

```
social-media/agent-harness/
├── cli_anything/social_media/
│   ├── social_media_cli.py         # Main CLI (Click-based)
│   ├── core/
│   │   ├── trends.py               # Trend aggregation + analysis
│   │   ├── hashtags.py             # Hashtag generation + scoring
│   │   ├── music.py                # Sound identification + recommendations
│   │   ├── accounts.py             # Account optimization
│   │   ├── theme_pages.py          # Theme page conversion guide
│   │   └── session.py              # Session + undo/redo
│   └── utils/
│       ├── youtube_scraper.py      # YouTube: yt-dlp + RSS fallback
│       ├── tiktok_scraper.py       # TikTok: API + curated fallback
│       └── repl_skin.py            # Interactive REPL
└── setup.py
```

## Data Sources

| Platform | Primary Method | Fallback |
|----------|---------------|---------|
| YouTube | `yt-dlp` (trending playlist) | Public RSS Atom feed |
| TikTok | Discover API endpoint | Curated trend patterns |
| Both | Live scraping | Curated high-signal data |

> **Note:** Both platforms implement anti-scraping measures. Live data requires `yt-dlp` (YouTube) and may be rate-limited (TikTok). The curated fallback uses real trend patterns and is always available.

## Agent Usage Examples

```bash
# Full workflow: fetch → analyze → generate hashtags → optimize account
cli-anything-social-media project new --name "MyBrand" --output myproject.json
cli-anything-social-media trends fetch --platforms tiktok,youtube --country US
cli-anything-social-media trends analyze
cli-anything-social-media hashtags generate --niche finance --platform tiktok --strategy balanced
cli-anything-social-media account add mybrand tiktok finance --followers 12500 --bio "Daily finance tips 💰 Link ↓"
cli-anything-social-media account optimize mybrand

# JSON output for agent parsing
cli-anything-social-media --json trends fetch | jq '.data.tiktok.trending_sounds[:5]'
cli-anything-social-media --json hashtags generate --niche fitness | jq '.hashtags'

# Theme page setup
cli-anything-social-media theme-page niches
cli-anything-social-media theme-page guide --niche finance
cli-anything-social-media theme-page funnel 4          # Conversion stage
cli-anything-social-media theme-page dm-scripts
```

## Install

```bash
cd social-media/agent-harness
pip install -e .

# For live YouTube data:
pip install -e ".[live]"   # installs yt-dlp
```
