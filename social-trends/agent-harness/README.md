# cli-anything-social-trends

A CLI harness for scraping viral trends from YouTube and TikTok, optimizing social media accounts, and building high-converting theme pages.

## Install

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# 1. Set up YouTube API key (free at console.cloud.google.com)
cli-anything-social-trends config set-key --youtube-key YOUR_KEY

# 2. Set your region
cli-anything-social-trends config set-key --region US --tz-offset -5

# 3. Fetch trending YouTube videos
cli-anything-social-trends youtube trending

# 4. Get trending TikTok hashtags for your niche
cli-anything-social-trends tiktok hashtags --niche fitness

# 5. Aggregate both platforms
cli-anything-social-trends trends aggregate --niche beauty

# 6. Score your profile
cli-anything-social-trends account score --platform tiktok --username yourhandle --bio "Your bio" --has-photo --has-link --followers 5000 --posts 30

# 7. Get theme page roadmap
cli-anything-social-trends theme-page roadmap --niche fitness_health --followers 0
```

## Commands

| Group | Command | Description |
|-------|---------|-------------|
| `config` | `status` | Show credential/config status |
| `config` | `set-key` | Store YouTube API key, TikTok session, region |
| `config` | `setup-guide` | Step-by-step setup instructions |
| `youtube` | `trending` | Trending YouTube videos by category |
| `youtube` | `hashtags` | Extract trending hashtags from top videos |
| `youtube` | `music` | Trending music videos |
| `youtube` | `search` | Search trending content by topic |
| `tiktok` | `hashtags` | Trending TikTok hashtags (with niche filter) |
| `tiktok` | `sounds` | Trending TikTok sounds/music |
| `tiktok` | `niche-tags` | Curated hashtags for a specific niche |
| `tiktok` | `niches` | List available niches |
| `trends` | `aggregate` | Cross-platform trend report |
| `trends` | `content-ideas` | AI-generated content ideas from trends |
| `hashtags` | `score` | Score a hashtag set (shadowban check + grade) |
| `hashtags` | `build` | Build optimal hashtag set for niche/platform |
| `hashtags` | `suggest` | Suggest hashtags from caption text |
| `account` | `score` | Profile optimization score + recommendations |
| `account` | `schedule` | Optimal posting schedule |
| `account` | `optimize-all` | Full optimization report |
| `theme-page` | `niches` | All available theme page niches |
| `theme-page` | `roadmap` | Milestone roadmap for your niche |
| `theme-page` | `monetization` | Monetization strategy guide |
| `theme-page` | `conversion-tips` | Turn followers into buyers |
| `theme-page` | `full-guide` | Complete theme page playbook |

## YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → Enable **YouTube Data API v3**
3. Create credentials → API Key
4. `cli-anything-social-trends config set-key --youtube-key YOUR_KEY`

Free quota: 10,000 units/day (trending fetch ≈ 3 units).

## TikTok (No Official API Required)

TikTok trends work via:
1. **With session ID**: Authenticated requests to TikTok Discover API
2. **Without session ID**: Curated niche-specific hashtag seeds (auto fallback)

To get session ID: DevTools → Application → Cookies → tiktok.com → `sessionid`

## JSON Output

All commands support `--json` for structured output:

```bash
cli-anything-social-trends --json trends aggregate --niche fitness
cli-anything-social-trends --json hashtags build --niche beauty --platform tiktok
cli-anything-social-trends --json theme-page roadmap --niche luxury_lifestyle
```

## Run Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```
