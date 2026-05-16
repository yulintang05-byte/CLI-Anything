# Social Trends CLI

Agent-native viral trend tracker and social account optimizer for YouTube, TikTok, and Google Trends.

## Install

```bash
cd social-trends/agent-harness
pip install -e .
```

## API Keys

| Platform | Variable | Where to get |
|---|---|---|
| YouTube | `YOUTUBE_API_KEY` | [console.cloud.google.com](https://console.cloud.google.com) → YouTube Data API v3 |
| TikTok | `TIKTOK_CLIENT_KEY` + `TIKTOK_CLIENT_SECRET` | [developers.tiktok.com](https://developers.tiktok.com) → Research API |
| Google Trends | *(none required)* | Public endpoint |

```bash
export YOUTUBE_API_KEY=AIza...
export TIKTOK_CLIENT_KEY=awxxxxxx
export TIKTOK_CLIENT_SECRET=xxxxxxxxx
```

## Quick Start

```bash
# No API key needed — Google Trends
social-trends trends fetch google
social-trends trends fetch google --type realtime --geo GB

# YouTube (requires YOUTUBE_API_KEY)
social-trends trends fetch youtube --type hashtags --category music --region US
social-trends trends fetch youtube --type videos --category gaming --max 30

# TikTok (requires TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET)
social-trends trends fetch tiktok --type hashtags --category all
social-trends trends fetch tiktok --type sounds --region US
social-trends trends fetch tiktok --type videos --category fitness

# Account optimizer (no API key needed)
social-trends account score --platform tiktok --followers 1200 --avg-views 5000 --posts-per-week 7
social-trends account schedule --platform tiktok --posts-per-week 14
social-trends account best-practices --platform youtube

# YouTube channel audit (requires YOUTUBE_API_KEY)
social-trends account audit-youtube UCxxxxxxxxxxxxxxxxxxxxxx

# Theme page strategy
social-trends theme-page niches
social-trends theme-page niches --difficulty Easy
social-trends theme-page niche-info finance
social-trends theme-page playbook
social-trends theme-page playbook --phase 1
social-trends theme-page checklist --niche "ai productivity" --platforms tiktok,youtube,instagram
social-trends theme-page pillars
social-trends theme-page monetization
social-trends theme-page tools

# JSON output for agents
social-trends --json trends fetch google | jq '.[0:5]'
social-trends --json account score --platform tiktok --followers 500

# Interactive REPL
social-trends
```

## Command Reference

### `trends fetch youtube`
Fetch YouTube trending data. Types: `videos`, `hashtags`, `music`.

Options: `--category`, `--region`, `--max`, `--type`

### `trends fetch tiktok`
Fetch TikTok trending data via Research API. Types: `videos`, `hashtags`, `sounds`.

Options: `--category`, `--region`, `--max`, `--type`

### `trends fetch google`
Fetch Google trending searches (no API key). Types: `daily`, `realtime`.

Options: `--geo`, `--type`, `--limit`

### `account score`
Score your account 0–100 with actionable recommendations.

Required: `--platform`. Optional: `--followers`, `--avg-views`, `--posts`, `--avg-hashtags`, `--posts-per-week`, `--bio`, `--has-link/--no-link`

### `account schedule`
Generate optimized weekly posting schedule.

Options: `--platform`, `--posts-per-week`, `--tz-offset`

### `account best-practices`
Show platform-specific best practices reference.

Options: `--platform`

### `account audit-youtube CHANNEL_ID`
Full channel audit with optimization score and recommendations.

### `theme-page niches`
List all profitable theme page niches with RPM estimates, difficulty, and monetization paths.

### `theme-page playbook [--phase N]`
4-phase conversion playbook: Foundation → Content Engine → Growth Hack → Monetize.

### `theme-page checklist --niche X --platforms Y`
Personalized launch checklist for your specific niche and platforms.

### `theme-page pillars`
5 content pillars (Educate/Entertain/Inspire/Engage/Promote) with recommended ratio.

### `theme-page monetization`
Platform-specific follower/view thresholds for monetization eligibility.

### `theme-page tools`
Free and paid tools for running a faceless theme page.
