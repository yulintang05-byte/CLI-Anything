# Social Trends — Viral Intelligence & Account Optimizer

Agent-native CLI harness for scraping YouTube and TikTok viral trends, building hashtag strategies, optimizing social media accounts, generating content calendars, and learning the full theme page playbook.

## Features

| Feature | Command |
|---------|---------|
| YouTube trending (videos, hashtags, music) | `trends fetch youtube` |
| TikTok trending (hashtags, sounds, viral signals) | `trends fetch tiktok` |
| Cross-platform trend report | `trends fetch all` |
| Trending music/sounds | `trends music` |
| Account optimization report | `account optimize` |
| Optimized posting schedule | `account schedule` |
| Tiered hashtag strategy | `hashtags strategy` |
| Quick hashtag recommendations | `hashtags recommend` |
| Content calendar with video ideas | `calendar generate` |
| Theme page niche rankings | `theme-page niches` |
| Full niche strategy + 30-day plan | `theme-page strategy` |
| Theme page creation roadmap | `theme-page roadmap` |
| Conversion & monetization playbook | `theme-page conversion` |

## Install

```bash
cd social-trends/agent-harness
pip install -e .
```

## Command Reference

### Trends

```bash
# YouTube — requires free API key from console.cloud.google.com
social-trends trends fetch youtube --region US --category entertainment --max 25

# TikTok — works with curated data, better with session cookie
social-trends trends fetch tiktok --count 30 --session-cookie YOUR_COOKIE

# Both platforms combined
social-trends trends fetch all --region US

# Trending music
social-trends trends music --platform tiktok --count 15
social-trends trends music --platform all
```

### Account Management

```bash
# Register accounts
social-trends account add --platform tiktok --handle myhandle --niche finance
social-trends account add --platform youtube --handle mychannel --niche fitness
social-trends account list

# Full optimization report
social-trends account optimize --platform tiktok \
  --handle myhandle \
  --followers 5000 \
  --avg-views 2000 \
  --avg-likes 150 \
  --avg-comments 20 \
  --posts-per-week 7

# YouTube channel deep audit (requires API key + channel ID)
social-trends account optimize --platform youtube \
  --channel-id UCxxxxxx \
  --followers 10000 \
  --avg-views 5000

# Posting schedule
social-trends account schedule --platforms tiktok,youtube,instagram \
  --niche finance \
  --posts-per-day 2 \
  --timezone EST
```

### Hashtag Strategy

```bash
# Full tiered strategy
social-trends hashtags strategy --niche finance --platform tiktok --count 10
social-trends hashtags strategy --niche beauty --platform instagram

# Quick 5-tag recommendation
social-trends hashtags recommend --niche gaming --platform tiktok
```

### Content Calendar

```bash
# 2-week calendar with video ideas, hooks, sounds, hashtags
social-trends calendar generate --niche finance --platforms tiktok,youtube --weeks 2

# Run trends fetch first to inject live trending data into calendar
social-trends trends fetch tiktok
social-trends calendar generate --niche business --weeks 1
```

### Theme Pages

```bash
# Rank niches by opportunity
social-trends theme-page niches
social-trends theme-page niches --sort growth_speed
social-trends theme-page niches --sort difficulty

# Deep dive into a specific niche
social-trends theme-page strategy --niche ai-tools
social-trends theme-page strategy --niche finance-investing
social-trends theme-page strategy --niche luxury-lifestyle

# Full creation roadmap
social-trends theme-page roadmap

# Conversion & monetization playbook
social-trends theme-page conversion
```

### Configuration

```bash
# Store API keys
social-trends config set --youtube-key AIzaSy...
social-trends config set --tiktok-cookie xxxx...
social-trends config set --region US --niche finance

# Check config
social-trends config show
```

### JSON Output (for agents)

Every command supports `--json` for structured agent consumption:

```bash
social-trends --json trends fetch tiktok | jq '.hashtags.hashtags[:5]'
social-trends --json hashtags strategy --niche finance | jq '.strategy'
social-trends --json theme-page niches | jq '.[] | select(.difficulty == "easy")'
social-trends --json account optimize --platform tiktok --followers 5000 --avg-views 2000
```

### REPL (interactive session)

```bash
social-trends  # launches REPL
> trends fetch tiktok
> hashtags strategy --niche finance
> theme-page niches
> theme-page roadmap
> quit
```

## Available Theme Page Niches

| Niche ID | Name | Difficulty | Monetization |
|----------|------|------------|--------------|
| `luxury-lifestyle` | Luxury Lifestyle | Easy | Very High |
| `ai-tools` | AI Tools & Productivity | Medium | Very High |
| `finance-investing` | Finance & Investing | Medium | Very High |
| `crypto-web3` | Crypto & Web3 | Hard | Very High |
| `fitness-wellness` | Fitness & Wellness | Medium | High |
| `relationship-advice` | Relationship & Dating | Easy | High |
| `fashion-style` | Fashion & Style | Medium | High |
| `gaming` | Gaming | Hard | High |
| `food-recipes` | Food & Recipes | Medium | Medium-High |
| `motivation-quotes` | Motivation & Mindset | Easy | Medium |

## Getting YouTube API Key (Free)

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or use existing)
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → **Create API Key**
5. Run: `social-trends config set --youtube-key YOUR_KEY`

Free quota: **10,000 units/day** (fetching 50 trending videos costs ~1 unit)

## Getting TikTok Session Cookie (Optional)

Without a cookie, the tool uses high-quality curated trending data. For live data:

1. Open TikTok in Chrome → Login
2. Open DevTools → Application → Cookies → `www.tiktok.com`
3. Find `sessionid` → Copy the value
4. Run: `social-trends config set --tiktok-cookie YOUR_SESSIONID`

## Architecture

```
social-trends/agent-harness/
├── cli_anything/social_trends/
│   ├── social_trends_cli.py    # Main CLI (click groups: trends/account/hashtags/calendar/theme-page/config)
│   ├── core/
│   │   ├── youtube.py          # YouTube Data API v3 + channel optimizer
│   │   ├── tiktok.py           # TikTok trends (live API + curated fallback)
│   │   ├── optimizer.py        # Hashtag strategy, posting schedule, content calendar, account metrics
│   │   ├── theme_pages.py      # 10 niche databases, roadmaps, conversion playbook
│   │   ├── config.py           # API key storage (~/.social-trends/config.json)
│   │   └── session.py          # In-memory cache for trend data
│   └── utils/
│       └── repl_skin.py        # REPL banner, tables, prompts
└── tests/
    └── test_core.py            # Unit tests for all core modules
```

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest tests/ -v
```
