# CLI-Anything Social Trends — SOP

## Purpose
Agent-native CLI for scraping viral trends from YouTube and TikTok, analyzing hashtags and music, optimizing social media accounts, and building profitable theme pages.

## Installation

```bash
cd social-trends/agent-harness
pip install -e .                    # base install
pip install -e ".[youtube]"         # + yt-dlp for YouTube scraping
pip install -e ".[full]"            # + TikTokApi (playwright) scraping
playwright install chromium         # required only for TikTokApi
```

## Quick Start

```bash
# Fetch trending content
social-trends trends tiktok
social-trends trends youtube --category music
social-trends trends all --region US

# Hashtag research
social-trends hashtags niche fitness
social-trends hashtags recommend "morning workout routine"
social-trends hashtags analyze #fyp #fitness #gymtok --niche fitness

# Music discovery
social-trends music trending --platform tiktok
social-trends music for-niche luxury

# Account optimization
social-trends optimize schedule --platform tiktok --timezone-offset -5
social-trends optimize bio --platform tiktok --niche fitness --followers 5000
social-trends optimize playbook 5000 --platform tiktok
social-trends optimize audit --platform tiktok --username @myaccount \
  --followers 5000 --following 800 --posts 90 --avg-views 2000 --avg-likes 150

# Theme page guide
social-trends themepage niches
social-trends themepage niches --niche luxury
social-trends themepage checklist
social-trends themepage checklist --phase 2
social-trends themepage content-methods
social-trends themepage pitch --handle @mypage --brand Nike --niche fitness \
  --followers 50000 --engagement 5.2 --rate 500 --name "Alex" --email alex@email.com

# Config
social-trends config set youtube_api_key AIza...
social-trends config set rapidapi_key abc123...
social-trends config show

# Account tracking
social-trends accounts add tiktok @myaccount --followers 5000 --niche fitness
social-trends accounts list

# JSON output (for agent pipelines)
social-trends --json trends tiktok

# Interactive REPL
social-trends repl
```

## Command Reference

### `trends` — Viral Content Scraping

| Command | Description |
|---------|-------------|
| `trends youtube` | YouTube trending (yt-dlp or API) |
| `trends tiktok` | TikTok trending (RapidAPI or TikTokApi) |
| `trends all` | Both platforms simultaneously |
| `trends search <query>` | Search YouTube by topic |
| `trends hashtag <tag>` | TikTok hashtag top videos |

### `hashtags` — Hashtag Intelligence

| Command | Description |
|---------|-------------|
| `hashtags niche <niche>` | Seed hashtags for your niche |
| `hashtags recommend <description>` | Auto-recommend from content description |
| `hashtags analyze [tags...]` | Score and rank a hashtag set |

**Available niches:** motivation, fitness, luxury, aesthetic, food, fashion, finance, travel, pets, gaming, beauty, themepage

### `music` — Viral Audio Discovery

| Command | Description |
|---------|-------------|
| `music trending` | Current viral tracks (curated database) |
| `music for-niche <niche>` | Best audio for your content niche |

### `optimize` — Account Optimization

| Command | Description |
|---------|-------------|
| `optimize schedule` | Optimal posting times by platform |
| `optimize bio` | Generate optimized bio |
| `optimize playbook <followers>` | Growth playbook for your stage |
| `optimize audit` | Full account audit with action items |
| `optimize all-accounts` | Audit all registered accounts |

### `themepage` — Theme Page Building

| Command | Description |
|---------|-------------|
| `themepage niches` | All profitable niches ranked |
| `themepage niches --niche <niche>` | Detailed niche guide |
| `themepage checklist` | 6-phase setup checklist |
| `themepage content-methods` | Legal content repurposing guide |
| `themepage pitch` | Generate brand partnership email |

### `accounts` — Account Management

| Command | Description |
|---------|-------------|
| `accounts add <platform> <username>` | Register an account |
| `accounts list` | List all accounts |

### `config` — API Keys

| Command | Description |
|---------|-------------|
| `config set <key> <value>` | Set API key or preference |
| `config show` | View current config |

## API Key Setup

### YouTube Data API v3 (Free — 10,000 units/day)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create project → Enable YouTube Data API v3
3. Create credentials → API Key
4. `social-trends config set youtube_api_key YOUR_KEY`

### RapidAPI TikTok (Free tier available)
1. Sign up at [rapidapi.com](https://rapidapi.com)
2. Subscribe to "TikTok Scraper" API (free tier: 100 requests/month)
3. `social-trends config set rapidapi_key YOUR_KEY`

### TikTokApi (Playwright — Advanced)
```bash
pip install TikTokApi playwright
playwright install chromium
# No API key needed — uses browser session
social-trends trends tiktok --use-playwright
```

## Environment Variables

```bash
export YOUTUBE_API_KEY=AIza...
export RAPIDAPI_KEY=abc123...
export SOCIAL_TRENDS_REGION=US
```

## Output Modes

- **Human-readable** (default): formatted text optimized for reading
- **JSON** (`--json` flag): structured output for agent pipelines and automation

```bash
# Pipe JSON to jq for filtering
social-trends --json trends tiktok | jq '.top_hashtags[:5]'
social-trends --json music trending | jq '.tracks[].title'
```

## Agent Usage (Claude Code)

```
# In Claude Code, you can use social-trends as a backend tool:
Run: social-trends --json trends tiktok --limit 10
Then: social-trends --json hashtags niche fitness
Then: social-trends --json optimize playbook 5000

# Full pipeline: scrape → analyze → optimize
social-trends trends all --json | python -c "import sys,json; d=json.load(sys.stdin); print(d['tiktok']['top_hashtags'][:5])"
```

## Scraping Notes

- **No API key**: Uses curated demo data + yt-dlp fallback for YouTube
- **YouTube API**: Best quality data, rate limited to 10K units/day (free)
- **RapidAPI**: Best for TikTok, paid tiers for higher volume
- **TikTokApi**: Playwright-based, most data but requires browser setup
- All scraping functions return identical schema regardless of source

## Ethical Guidelines

- Respect robots.txt and platform Terms of Service
- Do not scrape at rates that could impact platform performance
- Credit original content creators when repurposing
- Use only public, non-authenticated data unless you have explicit permission
- Do not store or sell scraped personal data
