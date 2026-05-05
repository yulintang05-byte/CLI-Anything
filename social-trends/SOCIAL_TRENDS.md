# Social Trends CLI — Agent-Native Social Media Intelligence

> Part of the **CLI-Anything** ecosystem — making social media automation agent-ready.

## What it does

| Feature | Description |
|---|---|
| **YouTube Trends** | Scrapes trending videos, top hashtags, keywords, and music titles via yt-dlp |
| **TikTok Trends** | Fetches viral hashtags, trending sounds, and niche-specific tag sets |
| **Account Optimizer** | Generates a full playbook: posting schedule, hooks, content pillars, monetization roadmap |
| **Theme Page Guide** | Complete 5-step creation guide + 90-day plan + 6 monetization strategies |
| **Full Scan** | One command — trends + optimization + guide merged into an executive report |

## Install

```bash
cd social-trends/agent-harness
pip install -e .
```

## Quick Start

```bash
# Fetch trends from both platforms for the fitness niche
social-trends trends fetch --platform all --niche fitness

# Get viral hashtag sets
social-trends trends hashtags --niche fashion

# Trending music/sounds
social-trends trends music --niche beauty

# Full account optimization playbook
social-trends account optimize --platform tiktok --niche fitness \
  --followers 5000 --avg-views 1200 --posts-per-week 7 --goals growth

# Theme page guide — luxury niche, account flipping strategy
social-trends theme-page guide --niche luxury --monetization account_flipping

# 90-day action plan
social-trends theme-page 90-day-plan --niche finance

# List all profitable niches
social-trends theme-page niches

# ONE command full intelligence report
social-trends full-scan --niche fitness --platform all --followers 5000 --goals monetization

# All commands with JSON output (agent-friendly)
social-trends --json full-scan --niche beauty

# Interactive REPL
social-trends repl
```

## Commands

### `trends fetch`
```
Options:
  -p, --platform  youtube | tiktok | all
  -n, --niche     fitness | fashion | food | beauty | finance | motivation |
                  gaming | travel | pets | education | general
  -c, --category  all | music | gaming | movies  (YouTube only)
  -m, --max-items Max results per platform (default 25)
```

### `account optimize`
```
Options:
  -p, --platform      tiktok | youtube | instagram  [required]
  -n, --niche         Content niche
  -f, --followers     Current follower count
  -v, --avg-views     Average views per post
  -w, --posts-per-week  Weekly posting frequency
  -g, --goals         growth | monetization | engagement
```

### `theme-page guide`
```
Options:
  -n, --niche         Content niche for the theme page
  -m, --monetization  affiliate | shoutouts | digital_products |
                      account_flipping | email_list | ugc_creator
```

## Agent Usage Example

```python
import subprocess, json

result = subprocess.run(
    ["social-trends", "--json", "full-scan",
     "--niche", "fitness", "--platform", "all", "--followers", "10000"],
    capture_output=True, text=True
)
data = json.loads(result.stdout)

top_hashtags = data["executive_summary"]["top_tiktok_hashtags"]
action_items = data["executive_summary"]["immediate_action_items"]
```

## Requirements

- Python 3.10+
- `yt-dlp` — YouTube trend data (`pip install yt-dlp`)
- `click` — CLI framework
- `requests` — HTTP fallback scraping

No API keys required. All data sourced from public endpoints.
