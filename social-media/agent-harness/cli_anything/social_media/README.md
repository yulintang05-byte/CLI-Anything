# cli-anything-social-media

> Social media intelligence & automation — scrape YouTube & TikTok for viral trends, optimize accounts, build and convert theme pages.

## Installation

```bash
# Install from source
pip install -e .

# Install with TikTok Playwright support (for deeper scraping)
pip install -e ".[tiktok-browser]"
playwright install chromium

# Install with Instagram support
pip install -e ".[instagram]"
```

## Quick Start

```bash
# Scrape viral trends
cli-anything-social trends scrape --niche fitness --region US --save

# Generate optimized hashtag set
cli-anything-social hashtags generate --niche fitness --platform tiktok

# Get trending sounds
cli-anything-social music trending --platform tiktok --content-type dance

# Audit your account
cli-anything-social account add --platform tiktok --handle myhandle --niche fitness --followers 5000
cli-anything-social account audit --platform tiktok --handle myhandle

# Theme page guide
cli-anything-social theme guide
cli-anything-social theme niches --interests fitness finance
cli-anything-social theme calendar --niche finance --days 30 --save
cli-anything-social theme monetize --niche fitness --followers 10000

# Schedule content
cli-anything-social schedule add --platform tiktok --time "2024-06-20T18:00:00" --caption "My post" --content-type video
cli-anything-social schedule list --days 7

# Interactive REPL
cli-anything-social
```

## Configuration

### YouTube API Key (optional — improves data quality)
```bash
cli-anything-social auth youtube --api-key YOUR_KEY
# Get a free key: https://console.cloud.google.com/apis/library/youtube.googleapis.com
```

Or set via environment variable:
```bash
export YOUTUBE_API_KEY=your_key_here
```

### Without API Key
The tool works without any API keys using:
- **YouTube**: `youtubesearchpython` library (no key needed)
- **TikTok**: Requests-based web scraping + research-backed trend data

## Commands

| Command | Description |
|---------|-------------|
| `trends scrape` | Scrape YouTube + TikTok for viral trends |
| `trends show` | View last trend report |
| `trends diff` | What changed since last report |
| `hashtags generate` | Generate optimal hashtag set |
| `hashtags analyze` | Analyze existing hashtag set |
| `music trending` | Trending sounds on TikTok + YouTube |
| `account add` | Add/update account profile |
| `account audit` | Full account audit |
| `account analyze-bio` | Score and improve bio |
| `account engagement` | Calculate engagement rate |
| `account schedule-optimize` | Best posting times |
| `theme guide` | Full theme page guide |
| `theme niches` | Niche recommendations |
| `theme calendar` | Content calendar |
| `theme monetize` | Monetization roadmap |
| `schedule add` | Schedule a post |
| `schedule list` | View upcoming posts |
| `schedule export` | Export to CSV/JSON |

## Supported Platforms

- **TikTok** — trending hashtags, sounds, videos
- **YouTube** — trending videos, hashtags (derived), music
- **Instagram** — account optimization, hashtag strategy
- **Twitter/X** — account optimization, hashtag strategy

## Data Storage

All data is stored locally at `~/.cli-anything-social/`:
```
~/.cli-anything-social/
├── accounts/              # Account profiles
├── trend_reports/         # Saved trend reports
├── music_reports/         # Music trend reports
├── schedule.json          # Post schedule
├── youtube_config.json    # YouTube API key
└── youtube_cache.json     # API response cache (1h TTL)
```
