# social-trends — Agent-Native Social Media Trend Intelligence

CLI harness for scraping viral trends from YouTube and TikTok, analysing hashtags and music, optimising social media accounts, and learning how to build converting theme pages.

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# TikTok trending hashtags
social-trends tiktok hashtags --limit 20

# YouTube trending videos (music category)
social-trends youtube trending --category music

# Recommend hashtag pack for fitness niche
social-trends hashtags recommend --niche fitness --platform tiktok

# Trending music for dance content
social-trends music for-content dance

# Full TikTok account optimisation playbook
social-trends account optimize tiktok

# 7-day cross-platform posting calendar
social-trends account calendar --platforms tiktok,instagram,youtube

# Audit your caption's hashtags
social-trends hashtags audit "#fitness #gym #fyp #foryoupage"

# Theme page niche comparison table
social-trends theme-page niches

# Deep dive into the finance niche
social-trends theme-page niche-detail finance_investing

# Full launch playbook for theme pages
social-trends theme-page playbook

# Full trends snapshot saved as JSON
social-trends report snapshot --niche fitness -o report.json

# Launch interactive REPL
social-trends
```

## Commands

### `tiktok`
| Command | Description |
|---------|-------------|
| `tiktok hashtags [--limit N]` | Scrape TikTok Discover trending hashtags |
| `tiktok sounds [--limit N]` | Scrape TikTok trending sounds/music |
| `tiktok all` | Hashtags + sounds in one call |

### `youtube`
| Command | Description |
|---------|-------------|
| `youtube trending [--category now\|music\|gaming\|movies]` | YouTube trending videos |
| `youtube hashtags` | Extract hashtags from trending videos |
| `youtube music` | Extract music references from trending videos |
| `youtube all-categories` | Trending across all categories |

### `hashtags`
| Command | Description |
|---------|-------------|
| `hashtags recommend --niche <niche>` | Niche-specific hashtag pack with copy-paste output |
| `hashtags audit '<caption>'` | Audit hashtags in an existing caption |
| `hashtags merge` | Merge YouTube + TikTok tags into ranked cross-platform list |
| `hashtags niches` | List supported niches |

**Supported niches:** fitness, food, fashion, beauty, gaming, finance, travel, motivation, pets, tech

### `music`
| Command | Description |
|---------|-------------|
| `music trending [--genre pop] [--mood chill]` | Trending music with BPM and mood data |
| `music for-content <type>` | Best music for a content type (dance, travel, comedy …) |
| `music platform-guide <platform>` | Platform-specific music + posting timing guide |
| `music genres` | List all genres and moods |

### `account`
| Command | Description |
|---------|-------------|
| `account optimize <platform>` | Full optimisation playbook (algorithm signals, checklist, hooks) |
| `account audit <platform> [--followers N --avg-views N]` | Health score + prioritised action plan |
| `account calendar [--platforms tiktok,instagram,youtube]` | 7-day cross-platform posting calendar |
| `account hooks <platform>` | Proven hook / title formulas |

**Supported platforms:** tiktok, youtube, instagram (and aliases: tt, yt, ig)

### `theme-page`
| Command | Description |
|---------|-------------|
| `theme-page niches [--min-monetisation high]` | All niches ranked by CPM |
| `theme-page niche-detail <niche>` | Hooks, rate card, top content types |
| `theme-page playbook` | 5-phase launch playbook (Foundation → Automation) |
| `theme-page funnel <type>` | Conversion funnel (affiliate/shoutout/digital_product) |
| `theme-page sourcing` | Legal content sourcing and reposting best practices |

### `report`
| Command | Description |
|---------|-------------|
| `report snapshot [--niche N] [-o file.json]` | Full YouTube + TikTok trend snapshot |

## JSON Output

All commands accept a global `--json` flag for machine-readable output:

```bash
social-trends --json tiktok hashtags | jq '.hashtags[:5]'
social-trends --json hashtags recommend --niche fitness | jq '.copy_paste'
social-trends --json account audit tiktok --followers 5000 --avg-views 500
```

## Agent Usage (Claude Code / OpenCode / Codex)

```bash
# Pull current trends and pipe into a caption generator
TRENDS=$(social-trends --json hashtags merge)
echo "$TRENDS" | jq '.merged_hashtags[:15] | [.[].hashtag] | join(" ")'

# Get music recommendations for a video type and pass to Clipper
social-trends --json music for-content dance | jq '.tracks[0]'

# Full account audit as structured data for LLM processing
social-trends --json account audit tiktok --followers 12000 --avg-views 800 --posts-per-week 5
```

## Architecture

```
social-trends/agent-harness/
├── cli_anything/
│   └── social_trends/
│       ├── social_trends_cli.py   # Click CLI entrypoint
│       ├── core/
│       │   ├── youtube.py         # YouTube trending scraper
│       │   ├── tiktok.py          # TikTok trending scraper
│       │   ├── hashtags.py        # Hashtag analysis & recommendations
│       │   ├── music.py           # Music trend intelligence
│       │   ├── account.py         # Account optimisation engine
│       │   └── theme_page.py      # Theme page creation guide
│       └── utils/
│           ├── scraper.py         # HTTP fetch utilities
│           └── repl_skin.py       # REPL UI
└── tests/
    ├── test_core.py               # Unit tests (no network)
    └── test_full_e2e.py           # Integration tests
```

## Testing

```bash
cd social-trends/agent-harness
python -m pytest tests/ -v
```

All unit tests run without a network connection.
