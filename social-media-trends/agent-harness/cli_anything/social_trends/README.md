# cli-anything-social-trends

Scrape YouTube & TikTok for viral trends, optimize your accounts, and build
high-converting theme pages — all from the command line.

## Quick Start

```bash
pip install -e .
cp config.example.env .env && nano .env   # add YOUTUBE_API_KEY
export $(cat .env | xargs)

# No API key needed — TikTok Creative Center is public:
social-trends tiktok hashtags --region US --period 7
social-trends tiktok songs --region US
social-trends theme niches
social-trends theme playbook --niche finance
```

## Commands

### YouTube (requires `YOUTUBE_API_KEY`)

```bash
social-trends youtube trending            # Top 25 trending videos (US)
social-trends youtube trending --region GB --limit 50
social-trends youtube hashtags            # Extract trending hashtags from trending videos
social-trends youtube music               # Top trending music videos
social-trends youtube search-sounds "lo-fi beats"
```

Get a free API key: [console.cloud.google.com](https://console.cloud.google.com)
→ Enable "YouTube Data API v3" → Create API key
Free tier: 10,000 units/day (one trending fetch ≈ 100 units)

### TikTok (no key needed for Creative Center commands)

```bash
social-trends tiktok hashtags             # Trending hashtags (7-day, US)
social-trends tiktok hashtags --region GB --period 30
social-trends tiktok songs                # Trending sounds/music
social-trends tiktok creators             # Trending creators
social-trends tiktok videos               # Research API (needs TIKTOK_RESEARCH_TOKEN)
```

### Cross-Platform Trend Analysis

```bash
# Merge YouTube + TikTok hashtag signals into one ranked list
social-trends trends merge --niche finance

# Find trending topics (keywords) across both platforms
social-trends trends topics

# Generate ready-to-paste hashtag sets for your niche
social-trends trends hashtag-sets --niche fitness
```

### Account Optimizer

```bash
# Full profile audit with score + priority fixes
social-trends account audit \
  --platform tiktok \
  --username myaccount \
  --bio "Daily finance tips | Side hustles | Free guide below" \
  --followers 12000 \
  --following 800 \
  --posts 87 \
  --avg-views 4200 \
  --avg-likes 310 \
  --avg-comments 45 \
  --niche finance \
  --has-link

# 7-day content calendar built from current trends
social-trends account calendar --platform tiktok --niche fitness --days 7

# 3 optimized bio templates for your niche
social-trends account bio --niche finance --cta-url https://stan.store/yourpage

# Best posting times
social-trends account schedule --platform tiktok
```

### Theme Page Strategy

```bash
# Rank profitable niches by trend score + monetization
social-trends theme niches

# Full playbook: 90-day roadmap, monetization, viral formats
social-trends theme playbook --niche finance
social-trends theme playbook --niche fitness
social-trends theme playbook --niche tech

# The 6-stage viewer→buyer conversion funnel
social-trends theme funnel

# Most expensive mistakes to avoid
social-trends theme mistakes
```

### Score a Content Idea

```bash
social-trends score --title "5 money mistakes killing your savings" --niche finance
social-trends score --title "Morning routine that doubled my energy" --niche fitness
```

### JSON Output (for piping / agent use)

```bash
social-trends --json tiktok hashtags | jq '.[:10]'
social-trends --json trends merge --niche finance > trends_$(date +%Y%m%d).json
social-trends --json theme playbook --niche finance | jq '.monetization_methods'
```

## Configuration

| Variable | Required | Description |
|---|---|---|
| `YOUTUBE_API_KEY` | For `youtube` commands | YouTube Data API v3 key |
| `TIKTOK_RESEARCH_TOKEN` | Optional | TikTok Research API (approved devs only) |

TikTok Creative Center commands (`hashtags`, `songs`, `creators`) work with **no key**.

## Theme Page Conversion Guide (2025 Research)

### Most Profitable Niches (ranked by trend score)

| Niche | RPM | Competition | Top Monetization |
|---|---|---|---|
| Tech / AI tools | $6–12 | High | Affiliate + AdSense |
| Finance | $8–15 | High | Affiliate + digital products |
| Fitness | $4–8 | Very high | Coaching + programs |
| Beauty | $4–9 | Very high | Brand deals + TikTok Shop |
| Motivation | $3–6 | Medium | Digital products + community |
| Luxury lifestyle | $10–20 | Medium | Brand deals + affiliate |

### The 6-Stage Conversion Funnel

```
Video (hook + value + CTA) → Profile visit → Link in bio click
→ Landing page (lead magnet) → Email sequence → Sale
```

**Key stats:**
- TikTok link-in-bio CTR: 0.5–3% (higher with explicit verbal CTA)
- Landing page opt-in rate with strong lead magnet: 20–40%
- Email list conversion to sale: 2–5%
- TikTok Creator Rewards: $0.40–$1.00/1K views (videos >1 min)
- TikTok Shop commissions: 8–30% depending on category

### Critical Rules

1. **Stay in one niche per account for 90 days minimum** — niche drift kills algorithmic distribution
2. **Personal account until 1K followers** — Business accounts lose trending sounds (kills organic reach)
3. **Link in bio from day 1** — Start building an email list before you think you need it
4. **Keyword in spoken audio + on-screen text + caption** — TikTok indexes all four locations
5. **Never delete underperforming videos** — TikTok resurfaces "sleeper" videos days/weeks later
6. **Post 3–5x/week consistently** — Gaps >3 days reduce algorithmic distribution

## Install

```bash
# Development install
git clone https://github.com/HKUDS/CLI-Anything
cd CLI-Anything/social-media-trends/agent-harness
pip install -e .

# Production
pip install cli-anything-social-trends
```

## Requirements

- Python 3.10+
- `click>=8.0.0`
- `prompt-toolkit>=3.0.0`
- YouTube Data API v3 key (for `youtube` commands)
- No key needed for TikTok Creative Center, theme page, or account bio/schedule commands
