# cli-anything-social-trends

> **Discover viral trends, optimize your accounts, and build converting theme pages — from the CLI.**

Part of the [cli-anything](https://github.com/yourusername/CLI-Anything) ecosystem: agent-native CLI harnesses for any platform.

---

## What it does

| Feature | Description |
|---|---|
| **YouTube Trend Scraping** | Trending videos, hashtags & music via YouTube Data API v3 |
| **TikTok Trend Scraping** | Trending videos, sounds & hashtags via yt-dlp (no API key needed) |
| **Cross-Platform Trends** | Merges YouTube + TikTok trends into a unified ranked list |
| **Hashtag Optimizer** | Builds optimized hashtag sets per platform + niche |
| **Account Optimizer** | Scores your profile, posting cadence, hashtags, and engagement |
| **Growth Planner** | Week-by-week growth plan to reach any follower target |
| **Theme Page Guide** | 10 high-converting niches, 30-day launch plan, income calculator |
| **Monetization Tactics** | Affiliate, shoutouts, digital products, brand deals |

---

## Installation

```bash
pip install -e .
# or
pip install cli-anything-social-trends
```

**Optional — YouTube API (needed for YouTube trend features):**
```bash
pip install "cli-anything-social-trends[youtube]"
```

**Required for TikTok features:**
```bash
pip install yt-dlp
```

---

## Quick Start

### 1. Set your YouTube API key (free at console.cloud.google.com)
```bash
cli-anything-social-trends config set-key youtube AIzaSy...
```

### 2. Fetch trending content
```bash
# YouTube trending videos
cli-anything-social-trends trends youtube --region US --category music

# TikTok trending (no API key needed)
cli-anything-social-trends trends tiktok --count 30

# Trending music
cli-anything-social-trends trends music --platform tiktok

# Cross-platform hashtag trends
cli-anything-social-trends trends cross-platform --top 20
```

### 3. Optimize your hashtags
```bash
# Build optimal hashtag set for your niche
cli-anything-social-trends hashtags optimize --platform tiktok --niche fitness

# Analyze hashtags you're currently using
cli-anything-social-trends hashtags analyze "#fyp #fitness #gym #workout"

# See all niches with preset hashtag packs
cli-anything-social-trends hashtags niches
```

### 4. Optimize your account
```bash
# Add your account with current stats
cli-anything-social-trends account add tiktok @myhandle \
  --followers 5200 \
  --avg-views 3000 \
  --avg-likes 180 \
  --avg-comments 25 \
  --niche fitness \
  --posts-per-week 4 \
  --hashtag-count 5 \
  --has-bio \
  --has-link \
  --uses-trending-audio

# Get full optimization score + action plan
cli-anything-social-trends account score tiktok @myhandle

# Get a 12-week growth plan to 100K followers
cli-anything-social-trends account growth-plan tiktok @myhandle --goal 100000
```

### 5. Theme page strategy
```bash
# Browse all niches ranked by income potential
cli-anything-social-trends theme-pages niches --sort monetization

# Get full strategy for fitness on TikTok
cli-anything-social-trends theme-pages guide --niche fitness --platform tiktok

# Get personalized niche recommendations
cli-anything-social-trends theme-pages recommend --fast-growth --easy-start

# See the complete 30-day launch plan
cli-anything-social-trends theme-pages 30-day-plan

# Estimate income at 50K followers with 3.5% engagement
cli-anything-social-trends theme-pages income --followers 50000 --er 3.5

# Learn monetization tactics
cli-anything-social-trends theme-pages monetization
cli-anything-social-trends theme-pages monetization --tactic affiliate_links
```

### 6. Interactive REPL
```bash
cli-anything-social-trends
```

---

## Commands Reference

```
config
  set-key <platform> <key>     Set API key for youtube or tiktok
  set-region <code>            Set default region (US, GB, JP, etc.)
  show                         Show current config
  check                        Verify API keys and tools

trends
  youtube                      YouTube trending videos (requires API key)
  tiktok                       TikTok trending videos (requires yt-dlp)
  music                        Trending music/sounds
  cross-platform               Merged YouTube + TikTok hashtag trends

hashtags
  trending                     Top trending hashtags by platform
  optimize                     Build optimal hashtag set for niche
  analyze "<tags>"             Score and analyze your current hashtags
  niches                       Show niche hashtag presets

account
  add <platform> <handle>      Add account with stats
  list                         List all tracked accounts
  score <platform> <handle>    Full optimization audit
  growth-plan                  Week-by-week growth plan
  remove                       Remove a tracked account

theme-pages
  niches                       Browse all niches with income/growth ratings
  guide --niche X              Full content strategy for a niche
  recommend                    Personalized niche recommendations
  30-day-plan                  Complete 30-day launch roadmap
  monetization                 Monetization tactics guide
  income                       Monthly income calculator

status                         Session overview
```

---

## Output format

Every command supports `--json` for agent-friendly output:

```bash
cli-anything-social-trends --json trends youtube | jq '.[] | .title'
```

---

## Theme Page Niches

| Niche | Difficulty | Income Potential |
|---|---|---|
| Finance | Medium | Very High |
| Beauty | Medium | Very High |
| Fitness | Medium | Very High |
| Crypto | Hard | Very High |
| Travel | Easy | High |
| Luxury | Easy | High |
| Relationships | Easy | High |
| Food | Easy | Medium |
| Motivation | Easy | Medium |
| Pets | Very Easy | Medium |

---

## How TikTok Scraping Works

TikTok does not have a public consumer API. This harness uses two methods:

1. **yt-dlp** — An open-source video downloader that fetches public TikTok video metadata (title, views, hashtags, duration, audio) without credentials. Install: `pip install yt-dlp`
2. **TikTok Discover API** — Hits TikTok's public discover endpoint for trending hashtags. Falls back to extracting from videos if the endpoint is unavailable.

No cookies or login are required for public trending data. For private account analytics, provide a `--cookie` string.

---

## YouTube API Setup

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable **YouTube Data API v3**
3. Create credentials → API Key
4. Set the key: `cli-anything-social-trends config set-key youtube <YOUR_KEY>`

Free tier: **10,000 units/day**. Fetching 50 trending videos costs ~1 unit.

---

## License

MIT — cli-anything contributors
