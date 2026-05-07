# cli-anything-social-trends

Agent-native CLI for viral trend scraping, hashtag optimization, account growth, and theme page strategy.

## Install

```bash
pip install -e .
# With real YouTube scraping (no API key needed):
pip install -e ".[youtube]"
# With TikTok scraping:
pip install -e ".[all]"
```

## Quick Start

```bash
# Fetch what's trending right now
cli-anything-social-trends trends fetch --platform tiktok
cli-anything-social-trends trends fetch --platform youtube --region US

# Get trending music/sounds
cli-anything-social-trends trends music --limit 20

# Generate optimized hashtags for your niche
cli-anything-social-trends hashtags optimize --niche fitness --platform tiktok
cli-anything-social-trends hashtags sets --niche finance --platform instagram

# Optimize your account
cli-anything-social-trends account bio --platform tiktok
cli-anything-social-trends account audit --platform tiktok --niche fitness

# Theme page playbook
cli-anything-social-trends theme guide
cli-anything-social-trends theme niches --sort monetization
cli-anything-social-trends theme plan --niche finance --days 7
cli-anything-social-trends theme monetize --niche fitness
cli-anything-social-trends theme convert

# Interactive REPL
cli-anything-social-trends
```

## Commands

### `trends`
| Command | Description |
|---------|-------------|
| `trends fetch --platform <youtube\|tiktok\|all>` | Fetch trending videos/hashtags |
| `trends music` | Trending sounds and music |
| `trends viral --niche <niche>` | Viral patterns, hooks, and formats |

### `hashtags`
| Command | Description |
|---------|-------------|
| `hashtags optimize --niche <n> --platform <p>` | Copy-ready hashtag set |
| `hashtags sets --niche <n>` | 3 sets for A/B/C rotation |
| `hashtags analyze --tag <tag>` | Analyze a hashtag's tier |
| `hashtags niches` | List all 11 supported niches |
| `hashtags strategy --platform <p>` | Full platform hashtag guide |

### `account`
| Command | Description |
|---------|-------------|
| `account bio --platform <p>` | Bio formula + examples |
| `account strategy --platform <p> --niche <n>` | Content pillars + frequency |
| `account schedule --platform <p> --niche <n>` | Weekly schedule |
| `account engagement --platform <p>` | Engagement tactics by impact |
| `account audit --platform <p> --niche <n>` | Full optimization checklist |

### `theme`
| Command | Description |
|---------|-------------|
| `theme guide` | Complete theme page playbook |
| `theme niches` | Profitable niches ranked |
| `theme plan --niche <n> --days 7` | Content calendar |
| `theme monetize --niche <n>` | Monetization strategies |
| `theme convert` | Follower → customer conversion |

## Config

```bash
# Add YouTube Data API v3 key for live trending data (optional)
cli-anything-social-trends config set youtube_api_key YOUR_KEY

# The CLI works without an API key using intelligent fallbacks
```

## Supported Niches

`fitness` `food` `fashion` `travel` `finance` `motivation` `beauty` `gaming` `music` `business` `pets`

## JSON Output

All commands support `--json` for agent consumption:

```bash
cli-anything-social-trends --json hashtags optimize --niche fitness --platform tiktok
```
