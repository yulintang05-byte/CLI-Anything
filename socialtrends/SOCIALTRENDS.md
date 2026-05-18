# SocialTrends — CLI-Anything Social Media Intelligence Module

Agent-native CLI for viral trend research, hashtag optimization, music discovery,
account auditing, and a complete theme page conversion system.

## Platforms Covered
- **TikTok** — trending hashtags, sounds, content strategy
- **YouTube** — trending videos, hashtag extraction, music charts
- **Instagram** — posting schedule, caption formulas, Reels optimization
- **Spotify** — top charts for music selection

## Quick Start

```bash
# Install
cd socialtrends/agent-harness
pip install -e .

# Configure (YouTube API key is free — get one at console.cloud.google.com)
socialtrends auth setup --youtube-key YOUR_KEY

# Fetch live YouTube trends
socialtrends trends youtube --region US

# Get TikTok trends (no key needed — uses Google Trends bridge + curated DB)
socialtrends trends tiktok --niche fitness

# Get optimized hashtag set
socialtrends hashtags suggest --niche fitness --platform tiktok

# Get music recommendations
socialtrends music recommend --niche travel

# Run account audit
socialtrends account optimize --platform tiktok --niche fitness \
  --followers 25000 --avg-likes 800 --avg-comments 40

# Generate a viral caption
socialtrends account caption --topic "how to lose belly fat" --niche fitness

# Theme page niche research
socialtrends theme-page niches
socialtrends theme-page guide --niche luxury
socialtrends theme-page convert --strategy email_list_building
socialtrends theme-page playbook --stage 0_to_10k

# Revenue estimates
socialtrends theme-page revenue --niche fitness --followers 50000

# Interactive REPL
socialtrends
```

## Command Reference

### `auth`
| Command | Description |
|---------|-------------|
| `auth setup --youtube-key KEY` | Configure YouTube API v3 key |
| `auth setup --tiktok-token TOKEN` | Configure TikTok Research API token |
| `auth status` | Show configured credentials |
| `auth clear` | Remove all credentials |

### `trends`
| Command | Description |
|---------|-------------|
| `trends youtube --region US` | YouTube trending videos + hashtags |
| `trends tiktok --niche fitness` | TikTok trends (Research API or Google bridge) |
| `trends all --region US` | All platforms simultaneously |

### `hashtags`
| Command | Description |
|---------|-------------|
| `hashtags suggest --niche fitness` | Generate optimized 30-hashtag set |
| `hashtags score '#gym'` | Score a hashtag's virality (0–100) |
| `hashtags analyze '#fyp' '#gym' '#fitness'` | Analyze set for tier balance |
| `hashtags niches` | List all 13 niche categories |

### `music`
| Command | Description |
|---------|-------------|
| `music trending --region US` | YouTube + Spotify top charts |
| `music recommend --niche fitness` | Music mood & evergreen sounds for niche |

### `account`
| Command | Description |
|---------|-------------|
| `account optimize --platform tiktok --niche fitness --followers 5000` | Full audit |
| `account bio --platform instagram --niche food --name "Chef Maria"` | Bio template |
| `account schedule --platform tiktok --timezone PT` | Optimal posting schedule |
| `account caption --topic "lose belly fat" --niche fitness` | Viral caption |
| `account engagement --followers 10000 --likes 500 --comments 30` | ER calculator |

### `theme-page`
| Command | Description |
|---------|-------------|
| `theme-page niches` | 9 profitable niches ranked by revenue potential |
| `theme-page guide --niche luxury` | Full niche breakdown (content, monetization, audience) |
| `theme-page convert` | List all 6 conversion strategies |
| `theme-page convert --strategy email_list_building` | Step-by-step blueprint |
| `theme-page sourcing` | Legal content sourcing methods |
| `theme-page playbook --stage 0_to_10k` | Growth playbook by milestone |
| `theme-page revenue --niche fitness --followers 25000` | Revenue estimate |

## API Setup

### YouTube Data API v3 (Free)
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project → Enable "YouTube Data API v3"
3. Create Credentials → API Key
4. Run: `socialtrends auth setup --youtube-key YOUR_KEY`
- **Free quota**: 10,000 units/day (a trending fetch costs ~50 units)

### TikTok Research API (Optional)
- Requires approval from TikTok for researchers/businesses
- Apply at: https://developers.tiktok.com/products/research-api/
- Without this token, the CLI uses Google Trends + curated database (always available)

## Architecture

```
socialtrends/
└── agent-harness/
    └── cli_anything/socialtrends/
        ├── socialtrends_cli.py     # Main CLI (Click groups + REPL)
        ├── core/
        │   ├── youtube_trends.py   # YouTube Data API v3 integration
        │   ├── tiktok_trends.py    # Research API + Google Trends bridge
        │   ├── music_trends.py     # YouTube Music + Spotify + evergreen sounds
        │   ├── hashtag_analyzer.py # Scoring engine + 13-niche knowledge base
        │   ├── account_optimizer.py # Platform specs + caption/bio/schedule/audit
        │   └── theme_pages.py      # 9 niches + 6 conversion strategies + playbooks
        └── utils/
            ├── config.py           # ~/.config/cli-anything/socialtrends/
            ├── cache.py            # ~/.cache/cli-anything/socialtrends/ (6h TTL)
            └── repl_skin.py        # REPL UI (banner, tables, colors)
```

## Tests

```bash
cd socialtrends/agent-harness
pip install pytest
pytest tests/ -v
```

All tests run without network access (no API keys needed for tests).
