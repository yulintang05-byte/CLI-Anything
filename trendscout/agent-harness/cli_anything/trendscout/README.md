# TrendScout — Viral Trend Intelligence for Social Media

Agent-native CLI for scraping YouTube & TikTok trending content, auditing social media accounts, and executing the full theme page creation playbook.

## Install

```bash
pip install -e ".[live]"   # includes yt-dlp + requests for live data
# or
pip install -e .            # demo/offline mode only
```

## Quick Start

```bash
# Fetch trending content
trendscout trends fetch youtube --category music --region us
trendscout trends fetch tiktok --limit 30
trendscout trends fetch music
trendscout trends cross --category fitness
trendscout trends hashtags --niche beauty
trendscout trends times --platform tiktok
trendscout trends fyp --limit 20

# Account management & optimization
trendscout account add --handle mypage --platform tiktok --niche fitness --followers 5000
trendscout account list
trendscout account audit acc0
trendscout account audit acc0 --completed bio_keywords,profile_pic,pinned_videos
trendscout account checklist tiktok
trendscout account optimize-all
trendscout account plan acc0 --goal 100000 --weeks 24

# Theme page playbook
trendscout theme-page playbook
trendscout theme-page playbook --step 1
trendscout theme-page niches --sort opportunity
trendscout theme-page formats --platform tiktok
trendscout theme-page monetize --niche fitness
trendscout theme-page quickstart --niche gaming --platform youtube

# JSON output (for agents)
trendscout --json trends cross --category gaming
trendscout --json account audit acc0

# Interactive REPL
trendscout
```

## Features

### Trend Scraping
- **YouTube trending** — videos, hashtags, view counts via yt-dlp (no API key required)
- **TikTok trending** — hashtags, sounds, FYP signals via public HTTP endpoints
- **YouTube Music** — trending music charts
- **Cross-platform ranking** — unified hashtag scores weighted across both platforms
- **Niche hashtag reports** — 30 curated + trending hashtags per niche
- **Best posting times** — research-backed schedules for TikTok, YouTube, Instagram

### Account Optimization
- Track unlimited accounts across TikTok, YouTube, Instagram, Twitter
- **Profile audit** — weighted checklist scoring (0–100, A–F grade)
- **Top priority actions** — ordered by impact weight
- **Optimize all** — batch audit with worst-score-first ordering
- **Growth plan** — 3-phase week-by-week roadmap to any follower goal
- Full undo/redo history

### Theme Page Playbook
- **7-step creation guide** — niche selection → monetization
- **20 profitable niches** — with CPM data, competition level, monetization methods
- **Content format rankings** — virality-ordered formats for TikTok + YouTube
- **10 monetization methods** — with income ranges, difficulty, and how-to guidance
- **Quick-start guide** — personalized 1-page plan for any niche + platform

## Commands Reference

```
trends fetch <youtube|tiktok|music>  Fetch trending content
trends cross                          Cross-platform trend ranking
trends hashtags --niche <niche>      Hashtag strategy report
trends times --platform <p>          Best posting schedule
trends fyp                            TikTok FYP signals

account add                           Register account
account list                          List tracked accounts
account audit <id>                    Profile score + action plan
account checklist <platform>          Optimization checklist
account optimize-all                  Batch audit all accounts
account plan <id>                     Growth roadmap

theme-page playbook [--step N]        Step-by-step creation guide
theme-page niches                     Profitable niche comparison
theme-page formats                    Content formats by virality
theme-page monetize                   Monetization strategies
theme-page quickstart                 Personalized quick-start

session undo / redo / status / history
```

## Live Data

Install `yt-dlp` for real YouTube trending data:
```bash
pip install yt-dlp
```

TikTok live data is fetched via public HTTP — works without authentication.
All commands fall back to curated demo data if network is unavailable.
