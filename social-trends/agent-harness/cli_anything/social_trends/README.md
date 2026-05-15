# CLI-Anything: Social Trends

Viral trend scraping + account optimization for YouTube & TikTok — zero API keys required.

## Features

- **YouTube trending** — videos, music, hashtags (via yt-dlp + HTML fallback)
- **TikTok trending** — hashtags, sounds, videos, creators (via Creative Center public API)
- **Billboard Hot 100** — real-time music chart scraping
- **Account optimizer** — posting schedule, hashtag stacks, engagement analysis
- **Theme page engine** — niche strategies, revenue estimates, conversion roadmap

## Installation

```bash
pip install -e .
# Optional: enhanced YouTube extraction
pip install yt-dlp
```

## Quick Start

```bash
# See what's trending RIGHT NOW
social-trends dashboard

# Fetch TikTok trending hashtags for fitness niche
social-trends scrape tiktok --type hashtags --region US

# Get viral sounds to use in your videos
social-trends scrape tiktok --type sounds

# Build optimized hashtag set for your niche
social-trends hashtags --platform tiktok --niche fitness

# Analyze and optimize your account
social-trends optimize account --platform tiktok --niche fitness --followers 5000 --avg-views 800 --posts-week 3

# Get optimal posting schedule
social-trends optimize schedule --platform tiktok --tz-offset -5

# Generate content angles from trending topics
social-trends optimize angles --niche fitness --platform tiktok

# Theme page strategies
social-trends theme-pages list
social-trends theme-pages strategy --niche fitness_motivation
social-trends theme-pages roadmap --followers 0
social-trends theme-pages revenue --platform tiktok --niche fitness_motivation --followers 10000
```

## All Commands

| Command | Description |
|---------|-------------|
| `dashboard` | Full trends dashboard — YouTube + TikTok + Billboard in one view |
| `scrape youtube` | YouTube trending videos, music, or hashtags |
| `scrape tiktok` | TikTok trending hashtags, sounds, videos, or creators |
| `hashtags` | Build optimized hashtag set for a niche + platform |
| `music` | Trending music from Billboard, Spotify, or TikTok |
| `optimize account` | Full account analysis with actionable recommendations |
| `optimize schedule` | Optimal weekly posting schedule per platform |
| `optimize angles` | Viral content angles derived from trending topics |
| `theme-pages list` | All niche strategies with monetization potential |
| `theme-pages strategy` | Deep-dive strategy for a specific niche |
| `theme-pages roadmap` | Step-by-step conversion roadmap from 0 to monetized |
| `theme-pages revenue` | Revenue estimate for your account |

## Output Modes

All commands support `--json` flag for machine-readable output:

```bash
social-trends --json scrape tiktok --type hashtags | jq '.[:5]'
social-trends --json optimize account --platform tiktok --niche fitness --followers 10000
```

## Data Sources

| Source | Method | Rate Limit |
|--------|--------|------------|
| YouTube trending | yt-dlp (preferred) + HTML fallback | None |
| TikTok Creative Center | Public API endpoints | ~100 req/day |
| Billboard Hot 100 | HTML scraping | Respectful |
| Spotify Viral 50 | Public chart page | Respectful |

## Theme Page Niches

| Key | Niche | Monetization |
|-----|-------|-------------|
| `luxury_lifestyle` | Supercars, jets, mansions | VERY HIGH |
| `fitness_motivation` | Workouts, transformations | HIGH |
| `financial_freedom` | Investing, side hustles | VERY HIGH |
| `aesthetic_nature` | Satisfying, chill, nature | MEDIUM |
| `comedy_memes` | Memes, funny clips | MEDIUM-HIGH |
| `pets_animals` | Cute dogs/cats | MEDIUM-HIGH |
