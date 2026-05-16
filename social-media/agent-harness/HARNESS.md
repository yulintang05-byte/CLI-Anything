# Social Media CLI — Agent Harness

## What It Does
- Scrapes **YouTube** and **TikTok** for viral trends, hashtags, and trending music
- Runs **account optimization audits** (bio score, engagement rate, posting schedule)
- Generates **hashtag strategy** per niche and platform
- Provides a full **theme page playbook**: niches, conversion funnels, monetization roadmap
- Tracks multiple accounts and logs metrics over time

## Install
```bash
cd social-media/agent-harness
pip install -e .
```

## Quick Commands
```bash
# Scrape trends
social-cli trends youtube --region US --type videos
social-cli trends tiktok --type hashtags
social-cli trends cross-platform --region US

# Hashtag strategy
social-cli hashtags strategy --niche fitness --platform tiktok
social-cli hashtags trending --platform tiktok

# Account management
social-cli account add @mypage --platform tiktok --niche fitness --bio "💪 Daily workouts" --followers 2500
social-cli account audit @mypage --platform tiktok
social-cli account list
social-cli account optimize-all

# Posting schedule
social-cli schedule --platform tiktok --timezone EST

# Theme page intelligence
social-cli theme-page list
social-cli theme-page guide --niche motivation_luxury
social-cli theme-page full-guide
social-cli theme-page monetize

# JSON output (for agents)
social-cli --json trends youtube
```

## Architecture
```
social-media/agent-harness/
├── setup.py
├── HARNESS.md
├── tests/
│   └── test_core.py
└── cli_anything/social_media/
    ├── social_cli.py          # Main CLI entry point
    └── core/
        ├── trends.py          # YouTube + TikTok scraping
        ├── account_optimizer.py  # Bio analysis, hashtags, schedule
        ├── theme_pages.py     # Theme page niches + conversion playbook
        └── account_manager.py # Multi-account tracking (~/.cli-anything/social-media/)
```

## Notes
- YouTube trends use `yt-dlp` (no API key required)
- TikTok scrapes public pages (public data only)
- For production TikTok access, configure [TikTok Research API](https://developers.tiktok.com/products/research-api/)
- Account data stored locally at `~/.cli-anything/social-media/accounts.json`
