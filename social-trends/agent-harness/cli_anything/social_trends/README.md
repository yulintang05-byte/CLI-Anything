# cli-anything-social-trends

**YouTube + TikTok viral trend intelligence for AI agents and content creators.**

Scrapes trending videos, hashtags, and music from YouTube and TikTok, runs
account optimisation audits, and generates complete theme-page conversion
strategies — all from the command line.

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
pip install yt-dlp requests beautifulsoup4
```

## Quick Start

```bash
# Fetch trending YouTube videos (music category)
social-trends-cli trends youtube --category music --limit 20

# Fetch trending TikTok hashtags (mock mode — no network required)
social-trends-cli --mock trends tiktok --hashtags-only --limit 20

# Cross-platform trend aggregation for the fitness niche
social-trends-cli trends aggregate --niche fitness

# Trending music across both platforms
social-trends-cli trends music --platform both

# Account audit
social-trends-cli account audit tiktok @mypage \
  --niche fitness --followers 12000 --avg-views 8000 --avg-likes 640

# Best posting times
social-trends-cli account posting-times tiktok --niche fitness

# Generate optimised bio
social-trends-cli account bio-suggest tiktok --niche fitness --handle fitdaily

# Full niche theme page playbook
social-trends-cli theme niche-guide finance

# Theme page conversion masterclass
social-trends-cli theme conversion-guide

# 30-day content calendar
social-trends-cli theme calendar fitness --days 30 --posts-per-day 2

# All as JSON (agent-friendly)
social-trends-cli --json trends aggregate --niche beauty
```

## Commands

### `trends`
| Command | Description |
|---|---|
| `trends youtube` | Trending YouTube videos (general/music/gaming/movies) |
| `trends tiktok` | Trending TikTok content (videos, hashtags, music) |
| `trends hashtags` | Trending hashtags from both platforms |
| `trends music` | Trending music/sounds across platforms |
| `trends aggregate` | Combined cross-platform trend summary |
| `trends velocity` | Hot vs rising vs fading trend analysis |
| `trends hashtag-stats HASHTAG` | Stats for a specific TikTok hashtag |

### `account`
| Command | Description |
|---|---|
| `account add PLATFORM HANDLE` | Register an account |
| `account audit PLATFORM HANDLE` | Full scored audit with action items |
| `account optimize-all` | Audit all registered accounts with live trends |
| `account posting-times PLATFORM` | Best UTC posting windows |
| `account bio-suggest PLATFORM` | Generate optimised bio template |
| `account engagement-rate` | Calculate + benchmark engagement rate |
| `account hashtags NICHE` | Generate hashtag strategy |

### `theme`
| Command | Description |
|---|---|
| `theme niche-guide NICHE` | Full playbook for a niche theme page |
| `theme conversion-guide` | 4-phase theme page masterclass |
| `theme calendar NICHE` | Auto-generated content calendar |
| `theme monetization NICHE` | Ranked monetization strategies |
| `theme list-niches` | All supported niches |
| `theme faceless-formats` | Content formats (no face required) |

### Global Flags
| Flag | Description |
|---|---|
| `--json` | Output as JSON (for AI agents) |
| `--mock` | Use sample data (no network) |
| `--session-id ID` | Resume a saved session |

## Supported Niches

`fitness` · `beauty` · `fashion` · `food` · `finance` · `travel` · `gaming`
· `comedy` · `motivation` · `pets` · `tech` · `dance` · `music` · `art` · `education`

## Notes

- **YouTube scraping** uses `yt-dlp` — very reliable, no API key needed.
- **TikTok scraping** uses public web endpoints — TikTok may rate-limit; use
  `--mock` for offline development or CI testing.
- All outputs are fully JSON-serializable for consumption by AI agents.

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```
