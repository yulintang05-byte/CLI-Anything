# cli-anything-social-trends

**Agent-native CLI for YouTube & TikTok viral trend intelligence, account optimisation, and theme page conversion.**

## What It Does

- **Scrape viral trends** from YouTube (via Data API v3 or RSS) and TikTok Creative Center (no auth required)
- **Research & generate hashtags** with the proven mix-size strategy (mega + mid + micro + niche)
- **Discover trending sounds** on TikTok and music on YouTube
- **Optimise your accounts** with platform-specific checklists, posting schedules, and growth audits
- **Convert theme pages** — complete guide to starting, growing, and monetising niche content pages

---

## Installation

```bash
pip install -e .
```

Or from PyPI (when published):
```bash
pip install cli-anything-social-trends
```

---

## Quick Start

```bash
# TikTok trending hashtags (no API key needed)
cli-anything-social-trends trends tiktok --region US

# YouTube trending videos (RSS, no API key)
cli-anything-social-trends trends youtube

# Generate optimised hashtag sets for a niche
cli-anything-social-trends hashtags generate fitness --posts 7

# Find trending TikTok sounds
cli-anything-social-trends music tiktok --region US

# Get account optimisation checklist
cli-anything-social-trends accounts optimize tiktok --niche fitness

# Get optimal posting schedule
cli-anything-social-trends accounts schedule tiktok --timezone US/Eastern

# Run account growth audit
cli-anything-social-trends accounts audit tiktok --followers 5000 --niche food

# Theme page creation guide
cli-anything-social-trends theme-pages guide --niche luxury

# Rank niches by monetisation potential
cli-anything-social-trends theme-pages niches --top 10

# Get monetisation blueprint
cli-anything-social-trends theme-pages monetize fitness

# Generate 4-week content calendar
cli-anything-social-trends theme-pages calendar fashion --platform instagram --weeks 4
```

---

## Optional: YouTube Data API v3

For full YouTube stats (views, likes, tags), add a free API key:

```bash
cli-anything-social-trends config set youtube_api_key YOUR_KEY_HERE
```

Get a key at: [console.cloud.google.com](https://console.cloud.google.com/) → YouTube Data API v3 → Credentials

---

## All Commands

### `trends`
| Command | Description |
|---------|-------------|
| `trends youtube` | Trending YouTube videos |
| `trends tiktok` | Trending TikTok hashtags + videos |
| `trends compare TOPIC` | Cross-platform trend comparison |
| `trends yt-categories` | YouTube video categories |

### `hashtags`
| Command | Description |
|---------|-------------|
| `hashtags research TOPIC` | Research hashtags for a topic |
| `hashtags generate NICHE` | Generate optimised hashtag sets |
| `hashtags analyze HASHTAG` | Metrics and competition level |

### `music`
| Command | Description |
|---------|-------------|
| `music tiktok` | Trending TikTok sounds |
| `music youtube` | Trending YouTube music videos |
| `music cross-platform` | Sounds trending on BOTH platforms |
| `music search QUERY` | Search TikTok sounds by keyword |

### `accounts`
| Command | Description |
|---------|-------------|
| `accounts optimize PLATFORM` | Profile checklist + growth strategies |
| `accounts schedule PLATFORM` | Optimal posting schedule |
| `accounts audit PLATFORM` | Growth phase audit + action plan |

Platforms: `tiktok`, `youtube`, `instagram`, `all`

### `theme-pages`
| Command | Description |
|---------|-------------|
| `theme-pages guide` | Complete theme page creation guide |
| `theme-pages niches` | Niche rankings by monetisation potential |
| `theme-pages monetize NICHE` | Monetisation blueprint |
| `theme-pages calendar NICHE` | Content calendar generator |

### `cache`
| Command | Description |
|---------|-------------|
| `cache clear` | Remove all cached responses |
| `cache stats` | Show cache statistics |

### `config`
| Command | Description |
|---------|-------------|
| `config set KEY VALUE` | Set a config value |
| `config show` | Show current config |

### `repl`
Interactive prompt with autocomplete and history.

---

## Theme Page Niches (Ranked by Monetisation Potential)

| Rank | Niche | Score | Avg RPM |
|------|-------|-------|---------|
| 1 | Crypto | 10/10 | $20-60 |
| 1 | Luxury | 10/10 | $15-40 |
| 1 | Business | 10/10 | $15-50 |
| 4 | Fitness | 9/10 | $8-25 |
| 4 | Travel | 9/10 | $10-30 |
| 4 | Cars | 9/10 | $12-35 |
| 4 | Beauty | 9/10 | $8-25 |

---

## Architecture

```
social-trends/agent-harness/
├── setup.py
└── cli_anything/social_trends/
    ├── social_trends_cli.py     # Click CLI entry point
    ├── core/
    │   ├── trends.py            # YouTube + TikTok trend scraping
    │   ├── hashtags.py          # Hashtag research & generation
    │   ├── music.py             # Trending sounds/music
    │   ├── accounts.py          # Account optimisation
    │   └── theme_pages.py       # Theme page strategies
    ├── utils/
    │   ├── scraper_backend.py   # HTTP + caching
    │   └── repl_skin.py         # Interactive REPL
    └── tests/
        ├── test_core.py         # Unit tests (no network)
        └── test_full_e2e.py     # E2E tests (network)
```
