# Social Trends — Agent-Native Social Media Intelligence

## Overview

The `social-trends` CLI harness makes viral trend data, hashtag recommendations,
music intelligence, account optimisation playbooks, and theme page creation guides
all accessible via structured CLI commands — for both human operators and AI agents.

## What It Does

| Capability | Description |
|-----------|-------------|
| **YouTube Trending** | Scrapes trending videos across 4 categories (Now, Music, Gaming, Movies) |
| **TikTok Trending** | Scrapes Discover page hashtags and trending sounds/music |
| **Hashtag Engine** | Niche-specific packs, cross-platform merge, caption audit |
| **Music Intelligence** | Trending tracks by genre, mood, BPM, and best content use |
| **Account Optimizer** | Platform playbooks for TikTok, YouTube, and Instagram |
| **Theme Page Guide** | Niche research, launch playbook, monetisation funnels, sourcing rules |
| **Report Generator** | Full JSON trend snapshots for downstream automation |

## CLI Location

```
social-trends/agent-harness/
```

## Usage

```bash
# Install
cd social-trends/agent-harness
pip install -e .

# Interactive REPL
social-trends

# Quick commands
social-trends tiktok hashtags --limit 20
social-trends youtube trending --category music
social-trends hashtags recommend --niche fitness
social-trends account optimize tiktok
social-trends theme-page playbook
social-trends report snapshot --niche fashion -o trends.json
```

## JSON/Agent Mode

```bash
social-trends --json tiktok hashtags | jq '.hashtags[:10]'
social-trends --json account audit tiktok --followers 5000 --avg-views 400
```

## Testing

```bash
cd social-trends/agent-harness
python -m pytest tests/ -v
```
