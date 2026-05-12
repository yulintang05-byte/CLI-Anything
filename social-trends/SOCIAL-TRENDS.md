# Social Trends CLI — Architecture SOP

`cli-anything-social-trends` is the agent-native CLI harness for viral trend research, account optimization, and theme page strategy across YouTube and TikTok.

---

## Overview

| Capability | Backend | Notes |
|------------|---------|-------|
| YouTube trending videos | YouTube Data API v3 | Free, 10k units/day quota |
| YouTube trending music | YouTube Data API v3 (music category) | Free |
| TikTok trending videos | TikTok Research API | Requires application approval |
| TikTok trending sounds | TikTok Research API | Derived from video queries |
| Hashtag aggregation | Internal engine | Cross-platform merge + scoring |
| Account optimization | Internal engine | Per-platform recommendations |
| Theme page guide | Internal knowledge base | 10 niches, full strategy |
| Content calendar | Internal engine | 7-day, trend-informed |

---

## API Setup

### YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable "YouTube Data API v3"
3. Create credentials → API Key
4. Set environment variable:
   ```bash
   export YOUTUBE_API_KEY="your-key-here"
   ```
   **Free quota: 10,000 units/day** (1 trending fetch = 1 unit)

### TikTok Research API

1. Apply at [developers.tiktok.com](https://developers.tiktok.com/products/research-api/)
2. Academic/commercial research access required
3. Set environment variables:
   ```bash
   export TIKTOK_CLIENT_KEY="your-client-key"
   export TIKTOK_CLIENT_SECRET="your-client-secret"
   ```
   **Note:** Use `--mock` flag for demo mode without API keys.

---

## Installation

```bash
cd social-trends/agent-harness
pip install -e .

# Verify
which cli-anything-social-trends
cli-anything-social-trends --help
```

---

## Quick Start (Mock Mode — No API Keys)

```bash
# 1. Create a session
cli-anything-social-trends session new my-brand --region US --niche fitness

# 2. Add your social accounts
cli-anything-social-trends --project my-brand.trends.json account add tiktok @fitpage
cli-anything-social-trends --project my-brand.trends.json account add instagram @fitpage.ig
cli-anything-social-trends --project my-brand.trends.json account add youtube FitPageYT

# 3. Fetch trends (--mock for demo, remove flag with real API keys)
cli-anything-social-trends --project my-brand.trends.json trends fetch all --mock

# 4. Get hashtag recommendations
cli-anything-social-trends --project my-brand.trends.json hashtags recommend
cli-anything-social-trends --project my-brand.trends.json hashtags sets

# 5. Check trending sounds
cli-anything-social-trends --project my-brand.trends.json music trending --mock

# 6. Optimize all accounts
cli-anything-social-trends --project my-brand.trends.json optimize run

# 7. Generate content calendar
cli-anything-social-trends --project my-brand.trends.json optimize calendar --days 7

# 8. Explore niche opportunities
cli-anything-social-trends theme-page niches
cli-anything-social-trends theme-page guide fitness_wellness
cli-anything-social-trends theme-page score finance_investing
```

---

## Full CLI Reference

### `session` — Manage research sessions

```bash
# Create new session
cli-anything-social-trends session new <name> [--region US] [--niche fitness] [-o path]

# View session summary
cli-anything-social-trends --project <path> session info
cli-anything-social-trends --project <path> --json session info

# Save session
cli-anything-social-trends --project <path> session save
```

### `account` — Manage social accounts

```bash
# Add accounts (platform: tiktok | instagram | youtube)
cli-anything-social-trends --project <path> account add tiktok @handle [--niche fitness]
cli-anything-social-trends --project <path> account add instagram @handle
cli-anything-social-trends --project <path> account add youtube ChannelName

# List accounts
cli-anything-social-trends --project <path> account list

# Remove account
cli-anything-social-trends --project <path> account remove @handle
```

### `trends` — Fetch viral trends

```bash
# Fetch from all platforms (requires API keys, or use --mock)
cli-anything-social-trends --project <path> trends fetch all [--region US] [--niche fitness] [--mock]

# Fetch from specific platform
cli-anything-social-trends --project <path> trends fetch youtube [--region GB]
cli-anything-social-trends --project <path> trends fetch tiktok [--mock]

# View cached trends
cli-anything-social-trends --project <path> trends list [--top 20]
cli-anything-social-trends --project <path> --json trends list
```

### `hashtags` — Hashtag research

```bash
# Recommend hashtags from current trend data
cli-anything-social-trends --project <path> hashtags recommend [--top 30]

# Get ready-to-paste hashtag sets
cli-anything-social-trends --project <path> hashtags sets [--niche fitness]

# Score a specific hashtag
cli-anything-social-trends --project <path> hashtags score fyp
```

### `music` — Trending sounds

```bash
# Fetch trending sounds
cli-anything-social-trends --project <path> music trending [--mock] [--region US] [--top 20]
cli-anything-social-trends --project <path> --json music trending --mock
```

### `optimize` — Account optimization

```bash
# Generate full optimization report for all accounts
cli-anything-social-trends --project <path> optimize run
cli-anything-social-trends --project <path> --json optimize run > report.json

# Generate content calendar
cli-anything-social-trends --project <path> optimize calendar [--days 7]

# Score a content idea
cli-anything-social-trends --project <path> optimize score-idea "My morning routine" \
  --hashtags fyp --hashtags motivation --hashtags grwm
```

### `theme-page` — Theme page strategy

```bash
# Browse niche opportunities
cli-anything-social-trends theme-page niches [--sort monetization_ease|avg_cpm|competition]

# Full strategy guide for a niche
cli-anything-social-trends theme-page guide <niche_key>
cli-anything-social-trends --json theme-page guide luxury_lifestyle > luxury_guide.json

# Score a niche
cli-anything-social-trends theme-page score <niche_key>
```

### Available Niches

| Key | Name | Avg CPM | Competition | Monetization |
|-----|------|---------|-------------|--------------|
| `finance_investing` | Finance & Investing | $12.00 | Medium | Very High |
| `tech_gadgets` | Tech & Gadgets | $9.00 | Medium | High |
| `luxury_lifestyle` | Luxury Lifestyle | $8.50 | Medium | High |
| `travel` | Travel & Adventure | $6.00 | Medium | High |
| `fitness_wellness` | Fitness & Wellness | $5.50 | High | Very High |
| `food_recipes` | Food & Recipes | $4.50 | High | High |
| `motivation_quotes` | Motivation & Mindset | $4.00 | High | Medium |
| `aesthetic_photography` | Aesthetic/Photography | $3.50 | Low | Medium |
| `funny_animals` | Funny Animals & Pets | $3.00 | Medium | Medium |
| `gaming_clips` | Gaming Highlights | $2.50 | Very High | Medium |

---

## Agent JSON Mode

Every command supports `--json` for machine-readable output:

```bash
# Get trending hashtag sets as JSON
cli-anything-social-trends --project session.trends.json --json hashtags sets
# Output:
# {
#   "viral": ["fyp", "viral", "trending", "fitness", "gym", ...],
#   "niche": ["fitness", "workout", "gym", "transformation", ...],
#   "balanced": ["fyp", "fitness", "viral", "gym", "workout", ...]
# }

# Get full optimization report as JSON
cli-anything-social-trends --project session.trends.json --json optimize run
# Output: Full JSON report with per-account recommendations, calendar, tactics

# Get theme page guide as JSON
cli-anything-social-trends --json theme-page guide luxury_lifestyle
# Output: Complete guide with setup, strategy, monetization roadmap, tools
```

---

## REPL Mode

Run bare command to enter interactive session:

```bash
cli-anything-social-trends
# Enters REPL with prompt:
# ◆ social-trends [my-brand] ❯
```

Type `help` for all commands, `quit` to exit.

---

## Scoring Methodology

### Trend Score
`score = engagement_rate × log10(views)`

Where `engagement_rate = (likes + comments×2 + shares×3) / views × 1000`

Higher score = viral potential. Weighted to balance absolute size (log views) with relative engagement.

### Cross-Platform Hashtag Boost
Tags appearing on both YouTube and TikTok receive a **1.5× multiplier** — cross-platform virality is a strong signal that a trend is broadly mainstream vs. platform-specific.

### Niche Opportunity Score
`opportunity = views_normalized × (1 - competition_factor × 0.5)`

Combines searchable interest (log views) with competition penalty. Best niches have high views AND manageable competition.

---

## Architecture Notes

- **No scraping** — All data via official APIs (YouTube Data API v3, TikTok Research API)
- **Mock mode** — `--mock` flag on all fetch commands for testing without API keys
- **Offline-capable** — Once trends are fetched and saved in session, all analysis commands work offline
- **Session file** — Plain JSON (`.trends.json`), easily inspectable and version-controllable
- **Stateless analysis** — `trends.py`, `optimizer.py`, `theme_pages.py` are pure functions, no side effects
