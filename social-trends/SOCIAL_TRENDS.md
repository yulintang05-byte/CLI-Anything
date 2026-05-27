# Social Trends — Viral Intelligence & Account Optimizer

Agent-native CLI harness for scraping YouTube/TikTok viral trends, ranking hashtags, discovering trending music, and generating full account optimization plans.

## What This Does

| Command | What It Gives You |
|---|---|
| `trends youtube` | Live YouTube trending videos (all categories) |
| `trends tiktok` | Live TikTok trending videos + sounds |
| `hashtags rank` | Hashtags ranked by viral score from live trend data |
| `music tiktok-charts` | TikTok Creative Center top sounds chart |
| `optimize audit` | Full account audit with score, issues, action plan |
| `optimize all-platforms` | Optimized bio + hashtag stack for TikTok+IG+YT+X |
| `theme-page guide` | Complete theme page playbook for your niche |
| `full-report` | Everything at once — the full viral intelligence pipeline |

## Setup

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Commands

### Fetch Trending Now

```bash
# YouTube trending (US)
social-trends trends youtube --limit 20

# TikTok trending
social-trends trends tiktok --limit 20 --region US

# Both platforms at once
social-trends trends all --limit 20
```

### Get Top Viral Hashtags

```bash
# Scrape trends + rank all hashtags by viral score
social-trends hashtags rank --platform all --top-n 30

# Google Trends for specific keywords
social-trends hashtags google-trends "fitness" "gym" "workout"
```

### Trending Music/Sounds

```bash
# TikTok Creative Center top 20 sounds
social-trends music tiktok-charts --limit 20

# Trending music across platforms
social-trends music trending --platform all --limit 20
```

### Account Audit

```bash
social-trends optimize audit \
  --platform tiktok \
  --username @my_account \
  --niche fitness \
  --followers 5000 \
  --avg-views 1200 \
  --avg-likes 300 \
  --bio "Daily fitness tips 💪 Follow for workouts" \
  --hashtags-used "#fitness,#gym,#workout" \
  --posting-freq "1x/day"
```

Returns: score (0-100), grade, wins, issues by severity, action plan, recommended hashtags.

### Optimize All Platforms at Once

```bash
# Get optimized bio + hashtag stack + content calendar for all 4 platforms
social-trends optimize all-platforms --niche fitness
```

### Theme Page Playbook

```bash
# Full guide for creating a fitness theme page
social-trends theme-page guide --niche fitness --goal monetize --followers 0

# Converting a personal page to a theme page
social-trends theme-page guide --niche luxury --goal convert --followers 10000

# Monetization roadmap for current follower count
social-trends theme-page monetization --followers 25000 --niche finance
```

### Full Viral Intelligence Report

```bash
# One command: trends + hashtags + music + audit + theme page guide
social-trends full-report \
  --niche fitness \
  --platform tiktok \
  --username @my_account \
  --followers 5000 \
  --region US
```

## Output Format

All commands output **structured JSON** — pipe to `jq` for filtering:

```bash
# Top 5 hashtags only
social-trends hashtags rank | jq '.top_hashtags[:5]'

# Current monetization stage
social-trends theme-page guide --niche finance | jq '.monetization_roadmap[] | select(.is_current)'

# Just the action plan
social-trends optimize audit --platform tiktok --username test --niche comedy | jq '.action_plan'
```

## Theme Page Playbook Summary

### What Is a Theme Page?
A theme page is a content account built around a **topic**, not a person. The creator stays anonymous. You curate/create content in one niche (luxury cars, motivation quotes, funny dogs, etc.). Multiple pages can run simultaneously.

### Income Potential
| Followers | Monthly Revenue |
|---|---|
| 10K | $100–300 (shoutouts) |
| 50K | $500–1,500 (sponsorships) |
| 100K | $1,000–5,000 (UGC deals, affiliate) |
| 500K+ | $5,000–20,000+ (major brands, page sales) |

### Converting a Personal Page
1. Announce the rebrand in a post
2. Archive off-niche content (don't delete)
3. Update profile completely (new username, bio, pfp)
4. Pre-load 20+ niche posts before promoting
5. Post daily for 30 days — algo re-learns your niche in 2–4 weeks

### Top Growth Hacks
- **Comment farming** — drop thoughtful comments on viral niche posts within 5 minutes
- **Trend surfing** — every morning check TikTok Discover + YouTube Trending, make a niche version same day
- **Cross-platform funnel** — TikTok first, then repost to Reels + Shorts
- **Hashtag rotation** — never use the same hashtag stack twice in a row
- **Engagement pods** — join niche Telegram groups to boost first-hour engagement

## Architecture

```
social-trends/agent-harness/
├── cli_anything/social_trends/
│   ├── trends.py       ← YouTube + TikTok scrapers
│   ├── hashtags.py     ← extraction, ranking, Google Trends
│   ├── music.py        ← sound/music aggregator + CC charts
│   ├── optimizer.py    ← account audit + profile optimizer
│   ├── theme_pages.py  ← complete theme page knowledge base
│   └── cli.py          ← Click CLI entry-point
├── tests/
│   └── test_core.py    ← 17 unit tests (no network)
└── setup.py
```
