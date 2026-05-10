# social-trends — Tool SOP

## Overview

`social-trends` is an agent-native CLI harness for viral trend intelligence across YouTube and TikTok. It scrapes trending videos, hashtags, and sounds; analyzes them into actionable signals; generates platform-specific account optimization plans; and provides a full theme-page creation and monetization playbook.

**Use case:** Content creators, social media managers, and theme-page operators who want data-driven trend intelligence without manual platform browsing.

## Backend Architecture

| Concern | Solution |
|---------|----------|
| YouTube trending (no key) | YouTube innertube API (`/youtubei/v1/browse`) |
| YouTube trending (with key) | YouTube Data API v3 (`/youtube/v3/videos?chart=mostPopular`) |
| TikTok trending | TikTok Creative Center public API + SIGI_STATE HTML extraction |
| TikTok hashtag data | Creative Center `/creative_radar_api/v1/popular_trend/hashtag/list` |
| TikTok sounds | Creative Center `/creative_radar_api/v1/popular_trend/music/list` |
| Cross-platform analysis | `analyzers/trends.py` — weighted merge (TikTok × 3) |
| Account strategy | `optimizers/account.py` — phase-aware growth playbook |
| Theme page guide | `theme_pages/guide.py` — niche ranking + 4-phase SOP |

## Setup

```bash
# Python package
cd social-trends/agent-harness
pip install -e .

# Verify
social-trends --version
social-trends --help
```

### Optional: YouTube Data API v3 (recommended for deeper data)

```bash
# Get a key at https://console.cloud.google.com → YouTube Data API v3
export YOUTUBE_API_KEY="YOUR_KEY_HERE"
```

Without the API key the tool uses YouTube's innertube (same data, no account needed).

## Commands

### `scrape youtube` — Fetch YouTube trending

```bash
# Basic (innertube, no key needed)
social-trends scrape youtube

# With region + category
social-trends scrape youtube --region US --category music --limit 50

# All US categories
for cat in all music gaming entertainment news sports; do
  social-trends scrape youtube --region US --category $cat -o yt_${cat}.json
done

# With API key
YOUTUBE_API_KEY=YOUR_KEY social-trends scrape youtube --region US -o yt.json
```

**Options:**
| Flag | Default | Description |
|------|---------|-------------|
| `--region` | `US` | Region code (US, GB, CA, AU, IN, BR, DE, FR, JP, KR, MX, NG) |
| `--category` | `all` | all, music, gaming, entertainment, news, sports, science, howto, film |
| `--limit` | `25` | Max videos (1–50) |
| `--api-key` | env | YouTube Data API v3 key (or `YOUTUBE_API_KEY` env var) |
| `--output` | stdout | JSON output path |

---

### `scrape tiktok` — Fetch TikTok trending

```bash
social-trends scrape tiktok --region US -o tt.json
social-trends scrape tiktok --region GB --limit 50
```

**Output includes:** videos, hashtags (ranked), sounds (ranked), scraped_at.

---

### `scrape hashtag` — Deep-dive a specific TikTok hashtag

```bash
social-trends scrape hashtag fyp
social-trends scrape hashtag fitness --limit 50 -o fitness.json
social-trends scrape hashtag "ai" -o ai_tag.json
```

---

### `analyze hashtags` — Cross-platform hashtag intelligence

```bash
social-trends analyze hashtags --youtube-data yt.json --tiktok-data tt.json
social-trends analyze hashtags --tiktok-data tt.json -o hashtags.json
```

**Output includes:**
- `top_hashtags` — ranked by weighted score (TikTok × 3 + YouTube × 1)
- `cross_platform` — tags hot on BOTH YouTube and TikTok (highest ROI)
- `tiktok_only` — TikTok-specific reach drivers
- `youtube_only` — YouTube-specific tags

---

### `analyze music` — Trending sounds intelligence

```bash
social-trends analyze music --tiktok-data tt.json
```

**Output includes:** ranked sounds, original vs. licensed split, actionable insights.

---

### `analyze topics` — Content angle extraction

```bash
social-trends analyze topics --youtube-data yt.json --tiktok-data tt.json
```

**Output includes:** top keywords, top phrases, content angles derived from trending signals.

---

### `report` — Full trend report (one command)

```bash
# Auto-scrapes both platforms then analyzes
social-trends report -o full_report.json

# Specific region
social-trends report --region GB --limit 50 -o uk_report.json

# Pre-scraped data (faster, avoids re-fetching)
social-trends report --youtube-data yt.json --tiktok-data tt.json -o report.json
```

**Output includes:** summary (top 5 tags, top 3 sounds, top 5 keywords), hashtags, music, topics, action_items.

---

### `optimize` — Account optimization plan

```bash
# Full plan for your niche and follower count
social-trends optimize --platform all --niche finance --followers 5000

# TikTok only, with trend-aware tips
social-trends optimize --platform tiktok --niche fitness \
  --followers 12000 --trend-report report.json -o plan.json

# Starting from zero
social-trends optimize --niche gaming
```

**Output includes:**
- Platform specs (video length, aspect ratio, hashtag limits, best times, algorithm signals)
- Growth strategy (phase-appropriate actions + what to avoid)
- Trend-specific tips (from real scraped data)
- Hashtag formula per platform
- Bio templates (3 per platform)
- 7-day content calendar
- Monetization roadmap with milestone tracking

---

### `theme` — Theme page playbook

```bash
# See all profitable niches ranked by revenue potential
social-trends theme --list-niches

# Full guide for a specific niche
social-trends theme --niche finance

# Guide + current phase advice
social-trends theme --niche fitness --followers 5000 -o guide.json

# Starting fresh
social-trends theme --niche motivation
```

**Output includes:**
- Top 10 niches ranked by profit score (RPM × growth speed × competition)
- 4-phase SOP (setup → content engine → growth hacking → monetization)
- Monetization paths (shoutouts, affiliate, AdSense, digital products, brand deals)
- Content repurposing tools (free vs. paid)
- Legal notes (copyright, FTC, music licensing)
- Conversion checklist

## Typical Workflows

### Daily trend check + post strategy

```bash
# 1. Fetch today's trends
social-trends report --region US -o reports/$(date +%Y-%m-%d).json

# 2. Generate content calendar based on trends
social-trends optimize --platform all --niche fitness \
  --followers 8000 \
  --trend-report reports/$(date +%Y-%m-%d).json \
  -o plans/$(date +%Y-%m-%d)_plan.json

# 3. Check top hashtags to use today
cat plans/$(date +%Y-%m-%d)_plan.json | python3 -c "
import json,sys
plan = json.load(sys.stdin)
ht = plan['hashtag_strategy'].get('tiktok', {}).get('example_combo', [])
print('Use these hashtags:', ' '.join(ht))
"
```

### Starting a theme page from scratch

```bash
# 1. Pick niche
social-trends theme --list-niches | python3 -c "
import json,sys
niches = json.load(sys.stdin)['top_niches_by_profit']
for n in niches[:5]:
    print(f\"{n['niche']:12} RPM:{n['avg_rpm']:8} speed:{n['growth_speed']}\")
"

# 2. Get full playbook
social-trends theme --niche finance -o finance_playbook.json

# 3. Fetch trends for your niche region
social-trends scrape tiktok --region US -o tt.json
social-trends scrape youtube --region US --category finance -o yt.json

# 4. Optimize accounts
social-trends optimize --platform all --niche finance \
  --trend-report $(social-trends report --tiktok-data tt.json --youtube-data yt.json -o /tmp/r.json && echo /tmp/r.json) \
  -o finance_plan.json
```

## Agent Workflow Example

An AI agent can fully automate trend intelligence with this sequence:

```python
import subprocess, json

def fetch_trends(region="US", niche="fitness"):
    r = subprocess.run(
        ["social-trends", "report", "--region", region, "--limit", "30"],
        capture_output=True, text=True
    )
    report = json.loads(r.stdout)

    r2 = subprocess.run(
        ["social-trends", "optimize",
         "--platform", "tiktok", "--niche", niche,
         "--followers", "8000"],
        input=json.dumps(report),
        capture_output=True, text=True
    )
    return json.loads(r2.stdout)

plan = fetch_trends()
print(plan["growth_strategy"]["actions"][0])
```

## Output JSON Schema

### `scrape youtube` output
```json
{
  "region": "US",
  "category": "0",
  "videos": [
    {
      "id": "...",
      "url": "https://www.youtube.com/watch?v=...",
      "title": "...",
      "channel": "...",
      "description": "...",
      "tags": [],
      "views": "1500000",
      "likes": "45000",
      "duration": "PT10M30S"
    }
  ],
  "total": 25,
  "source": "innertube | youtube_data_api_v3",
  "scraped_at": "2025-05-10T12:00:00Z"
}
```

### `scrape tiktok` output
```json
{
  "region": "US",
  "videos": [...],
  "hashtags": [
    {"tag": "#fyp", "video_count": 1000000, "view_count": 500000000000, "rank": 1}
  ],
  "sounds": [
    {"id": "...", "title": "...", "author": "...", "use_count": 500000}
  ],
  "total_videos": 25,
  "total_hashtags": 50,
  "total_sounds": 30,
  "scraped_at": "2025-05-10T12:00:00Z"
}
```

### `report` output
```json
{
  "summary": {
    "top_5_hashtags": ["#fyp", "#ai", "#finance", ...],
    "top_3_sounds": ["Trending Beat", ...],
    "top_5_keywords": ["tutorial", "money", ...],
    "cross_platform_opportunities": 5
  },
  "hashtags": { "top_hashtags": [...], "cross_platform": [...] },
  "music": { "sounds": [...], "insights": [...] },
  "topics": { "top_keywords": [...], "content_angles": [...] },
  "action_items": [
    "Use cross-platform hashtags in ALL posts: ...",
    "Use trending audio NOW: '...'",
    ...
  ]
}
```

## Known Limitations

1. **TikTok rate limiting:** High-frequency scraping may trigger IP-based rate limits. Space requests at least 2–3 seconds apart.
2. **TikTok auth wall:** Some TikTok endpoints return limited data without a logged-in session cookie. The Creative Center endpoints are the most reliable public source.
3. **YouTube innertube stability:** The innertube API is an internal YouTube API that may change without notice. Use `--api-key` for production workloads.
4. **Copyright:** When reposting content to theme pages, always verify usage rights and credit creators. See `social-trends theme` → `legal_notes`.
5. **Geographic availability:** Some trending data varies by VPN/IP region regardless of the `--region` flag.

## Running Tests

```bash
cd social-trends/agent-harness
pip install -e ".[test]"
pytest tests/ -v
```

All tests run without network access (fully mocked fixture data).
