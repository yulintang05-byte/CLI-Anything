# cli-anything · Social Trends

Agent-native social media trend intelligence CLI. Scrape YouTube & TikTok for viral trends, hashtags, and music. Optimize all your accounts. Build and monetize converting theme pages.

## Quick Start

```bash
pip install -e .

# Set API keys
social-trends config set-key youtube YOUR_YOUTUBE_DATA_API_KEY
social-trends config set-key tiktok_apify YOUR_APIFY_TOKEN       # optional
social-trends config set-key rapidapi YOUR_RAPIDAPI_KEY           # optional

# Fetch viral trends
social-trends trends fetch --platform both --region US

# Get hashtags for your niche
social-trends trends hashtags --niche fitness

# Trending sounds
social-trends trends music --type rising

# Add and audit your accounts
social-trends accounts add tiktok @mypagename fitness --followers 5000
social-trends accounts audit tiktok_mypagename
social-trends accounts optimize-bio tiktok_mypagename

# Learn about theme pages
social-trends theme-page learn

# Browse niches
social-trends theme-page niches

# Create a theme page plan
social-trends theme-page create "FitLife Daily" fitness_motivation tiktok instagram

# Get a conversion playbook
social-trends theme-page playbook dm_funnel --niche fitness
```

## API Keys

| Key | Where to get | Cost |
|-----|-------------|------|
| `youtube` | [Google Cloud Console](https://console.cloud.google.com) → APIs → YouTube Data API v3 | Free (10K req/day) |
| `tiktok_apify` | [Apify Console](https://console.apify.com) → API tokens | Free tier available |
| `rapidapi` | [RapidAPI](https://rapidapi.com) → TikTok Trending Videos API | Free tier available |

**Works without API keys** — demo data is returned so you can explore the tool before setting up credentials.

## Commands

### `config`
- `config set-key <name> <value>` — Store an API key
- `config set-niche <niches...>` — Set your target niches
- `config set-region <codes...>` — Set target regions (US, GB, etc.)
- `config show` — View current config (keys masked)

### `trends`
- `trends fetch` — Fetch viral trending content from YouTube + TikTok
- `trends hashtags --niche <niche>` — Curated + live hashtag sets
- `trends music` — Trending sounds sorted by lifecycle (rising/peak/evergreen)
- `trends viral-patterns` — High-performing formats, hook formulas, posting windows

### `accounts`
- `accounts add <platform> <username> <niche>` — Track a social account
- `accounts list` — Show all accounts with scores
- `accounts audit <id>` — Full optimization audit (score, issues, recommendations)
- `accounts bulk-audit` — Audit all accounts at once
- `accounts optimize-bio <id>` — Generate 4 bio variants with CTAs
- `accounts schedule <id>` — Posting schedule + 7-day content calendar
- `accounts update <id>` — Update account fields

### `theme-page`
- `theme-page learn` — Complete beginner guide (what, why, how)
- `theme-page niches` — Browse 8+ monetizable niches with CPM data
- `theme-page niche-detail <id>` — Deep dive into a specific niche
- `theme-page create <name> <niche_id> <platforms...>` — Generate a full launch plan
- `theme-page list` — Show your theme pages
- `theme-page funnels` — List conversion funnel types
- `theme-page playbook <funnel>` — Step-by-step conversion guide

## Supported Niches

| ID | Niche | Monetization Potential |
|----|-------|----------------------|
| `luxury_lifestyle` | Luxury Lifestyle | Very High |
| `money_mindset` | Money & Wealth Mindset | Very High |
| `entrepreneurship` | Entrepreneurship | Very High |
| `fitness_motivation` | Fitness Motivation | High |
| `travel_aesthetic` | Travel Aesthetic | High |
| `relationship_advice` | Relationships & Dating | High |
| `pet_content` | Cute Pets / Animals | Medium |
| `dark_motivation` | Dark / Anti-Motivational | Medium |

## JSON Output

All commands support `--json` for agent-friendly output:

```bash
social-trends --json trends fetch --platform tiktok | jq '.tiktok.top_hashtags[:5]'
social-trends --json accounts audit tiktok_mypage
social-trends --json theme-page playbook dm_funnel
```

## REPL

```bash
social-trends   # launches interactive REPL with tab-completion and history
```
