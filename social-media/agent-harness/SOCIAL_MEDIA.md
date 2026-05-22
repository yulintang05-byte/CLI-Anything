# Social Media Trend Intelligence & Account Optimizer

Agent-native CLI for scraping YouTube + TikTok viral trends, optimizing accounts,
and building profitable converting theme pages.

## Setup

```bash
cd social-media/agent-harness
pip install -e .
```

### API Keys (optional but recommended)

| Key | Where to get | Cost |
|-----|-------------|------|
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → YouTube Data API v3 | Free (10k units/day) |
| `RAPIDAPI_KEY` | [rapidapi.com](https://rapidapi.com) → subscribe to `tiktok-api23` | Free tier available |

```bash
export YOUTUBE_API_KEY="your-key-here"
export RAPIDAPI_KEY="your-rapidapi-key-here"
```

Without keys the CLI runs in **demo mode** with sample trend data.

---

## Commands

### `trends` — Scrape viral trends

```bash
# Pull trending hashtags + music from YouTube and TikTok
social-media trends

# Specify region
social-media trends --region GB

# Save to file for later use
social-media trends > trends.json

# Human-readable output
social-media trends --human
```

**Output:**
- YouTube top hashtags by frequency
- TikTok top hashtags by frequency
- Trending music/sounds (title, artist, use count)
- Cross-platform hashtags (appear on both)

---

### `optimize` — Optimize a post

```bash
# Basic post optimization
social-media optimize \
  --caption "Check out my morning routine!" \
  --hashtags "morning,routine,lifestyle" \
  --platform tiktok \
  --followers 5000 \
  --likes 200 \
  --comments 15 \
  --shares 30

# Use live trend data
social-media trends > trends.json
social-media optimize \
  --caption "My productivity hack" \
  --hashtags "productivity,tips" \
  --platform tiktok \
  --followers 10000 \
  --trends-file trends.json
```

**Output:** Score (0–100), suggestions, recommended hashtags to add, trending music picks.

---

### `bio` — Optimize profile bio

```bash
social-media bio \
  --bio "I post fitness stuff. Follow me." \
  --niche fitness \
  --platform tiktok \
  --trends-file trends.json
```

**Output:** Score, issues found, suggested rewritten bio.

---

### `account` — Full account health report

```bash
social-media account \
  --platform tiktok \
  --username myaccount \
  --followers 12000 \
  --following 800 \
  --posts 45 \
  --avg-views 3200 \
  --avg-likes 180 \
  --avg-comments 22 \
  --avg-shares 14 \
  --niche fitness \
  --trends-file trends.json
```

**Output:** Health score, engagement rate, F/F ratio, issues, recommendations, 6-step growth playbook.

---

### `niche` — Analyze a theme page niche

```bash
social-media niche fitness
social-media niche finance
social-media niche motivation
```

**Output:** Content types, monetization methods, peak post times, revenue estimates at 10k/50k/100k followers.

---

### `calendar` — Generate posting calendar

```bash
# 7-day calendar (default)
social-media calendar fitness

# 30-day calendar
social-media calendar motivation --days 30
```

**Output:** Day-by-day content format, post times, hashtags, hook ideas, CTAs.

---

### `funnel` — Conversion funnel guide

```bash
social-media funnel finance
```

**Output:** 4-stage funnel (Awareness → Engagement → Trust → Conversion) with specific actions per stage, recommended tools for each.

---

### `niches` — List available niches

```bash
social-media niches
```

**Available niches:** motivation, finance, fitness, luxury, relationships, food, pets

---

## Agent Usage Examples

```python
# Agent calls: scrape trends → optimize post → save report
import subprocess, json

trends = json.loads(subprocess.check_output(["social-media", "trends"]))
result = json.loads(subprocess.check_output([
    "social-media", "optimize",
    "--caption", "Morning routine that changed my life",
    "--hashtags", "morning,routine",
    "--platform", "tiktok",
    "--followers", "5000",
]))
print(result["optimized_hashtags"])
```

---

## Theme Page Guide

### What is a theme page?
A theme page aggregates content around a niche topic without the creator
appearing on camera. You curate/repost/create content around a theme
(fitness, finance, motivation, etc.) and monetize through ads, affiliate
links, digital products, and brand deals.

### The 5 steps to a profitable theme page

1. **Pick a niche** — run `social-media niches` and `social-media niche <name>`
2. **Set up accounts** — create TikTok + Instagram + YouTube Shorts (all same handle)
3. **Content pipeline** — run `social-media calendar <niche>` for a daily posting schedule
4. **Trend stack** — run `social-media trends` daily and use top hashtags + music
5. **Monetize** — run `social-media funnel <niche>` for the conversion roadmap

### Critical rules for theme pages
- **Never post without trending audio** on TikTok — it's the #1 reach multiplier
- **First 3 seconds = everything** — hook must stop the scroll
- **Post 3x/day minimum** for the first 30 days
- **Engage for 30 min** after posting (reply to comments, watch other videos)
- **Cross-post everything** to all 3 platforms (TikTok, Reels, Shorts)
- **Build the email list from day 1** — platforms can ban accounts, email can't be taken

### Converting theme page checklist
- [ ] Optimized bio with niche + CTA + link (`social-media bio`)
- [ ] Pinned post: your best-performing video
- [ ] Link in bio → Beacons/Stan.store with lead magnet
- [ ] TikTok series/playlist set up for niche content
- [ ] Posting schedule locked in (`social-media calendar`)
- [ ] Daily trend check (`social-media trends`)
- [ ] Email list started (ConvertKit free)
- [ ] Affiliate links ready (Amazon Associates, Impact, ClickBank)
