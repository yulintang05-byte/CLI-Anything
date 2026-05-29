# Viral Trends — Agent-Native Trend Analysis & Content Scheduling

CLI harness for YouTube/TikTok viral trend tracking, account optimization,
and content calendar generation.

## Installation

```bash
cd viral-trends/agent-harness && pip install -e .
```

## Quick Start

```bash
# Create a workspace for your gaming page
viral-trends workspace new --name my_page --niche gaming -o page.json

# Fetch trending content (mock data, offline)
viral-trends --workspace page.json trends fetch --platform youtube
viral-trends --workspace page.json trends fetch --platform tiktok --niche gaming

# Fetch live data (requires yt-dlp: pip install yt-dlp)
viral-trends --workspace page.json trends fetch --platform youtube --live

# Optimize your account
viral-trends --workspace page.json optimize profile --niche gaming
viral-trends --workspace page.json optimize hashtags --niche gaming --platform tiktok
viral-trends --workspace page.json optimize times --platform tiktok

# Generate a 7-day content calendar
viral-trends --workspace page.json schedule generate --niche gaming --platforms tiktok,youtube
viral-trends --workspace page.json schedule calendar
```

## Theme Page Guides

```bash
viral-trends guide theme-page       # Full theme page masterclass
viral-trends guide converting       # How to convert followers into buyers
viral-trends guide hashtags         # Hashtag strategy
viral-trends guide posting-times    # Optimal posting windows
viral-trends guide hooks            # Caption hook frameworks
viral-trends guide youtube          # YouTube trending guide
viral-trends guide tiktok           # TikTok viral content guide
viral-trends guide list             # List all guides
```

## JSON Mode (for AI agents)

```bash
viral-trends --json trends fetch --platform tiktok
viral-trends --json optimize profile --niche finance
viral-trends --json schedule list
viral-trends --json guide theme-page
```

## Interactive REPL

```bash
viral-trends
# or
viral-trends --workspace page.json
```

## Commands Reference

### workspace
- `workspace new --name NAME --niche NICHE [-o PATH]`
- `workspace open PATH`
- `workspace save [PATH]`
- `workspace info`
- `workspace niches`

### trends
- `trends fetch --platform youtube|tiktok|both [--country US] [--niche all] [--live]`
- `trends list`
- `trends show SNAP_ID`
- `trends remove SNAP_ID`

### optimize
- `optimize profile --niche NICHE [--platform tiktok]`
- `optimize hashtags --niche NICHE [--platform tiktok] [--count 10]`
- `optimize times --platform tiktok [--day monday]`
- `optimize hooks --type curiosity [--niche general]`

### schedule
- `schedule generate --niche NICHE [--platforms tiktok,youtube] [--posts-per-day 2]`
- `schedule calendar`
- `schedule list [--day monday] [--platform tiktok]`
- `schedule add --day monday --time 19:00 --platform tiktok`
- `schedule mark ENTRY_ID --status published`
- `schedule remove ENTRY_ID`

### guide
- `guide theme-page` / `guide converting` / `guide hashtags`
- `guide posting-times` / `guide hooks` / `guide youtube` / `guide tiktok`
- `guide overview` / `guide schedule` / `guide list`

### session
- `session undo` / `session redo` / `session status` / `session history`
