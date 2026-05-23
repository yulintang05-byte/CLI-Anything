# cli-anything-social-trends

TikTok + YouTube viral trend scraping, account optimization, and theme page strategy CLI.

## Install

```bash
pip install -e social-trends/agent-harness
```

For enhanced TikTok scraping (uses Playwright):
```bash
pip install "cli-anything-social-trends[tiktok]"
playwright install chromium
```

## Setup

```bash
cli-anything-social-trends setup
```

Configure API keys in `.env`:
```
YOUTUBE_API_KEY=AIzaSy...       # https://console.cloud.google.com/
TIKTOK_SESSION_ID=abc123...     # optional — from browser cookies
```

## Commands

### Scan TikTok for viral trends
```bash
cli-anything-social-trends tiktok scan --region US
cli-anything-social-trends tiktok hashtags --count 30
cli-anything-social-trends tiktok sounds --count 20
cli-anything-social-trends tiktok search "gym workout"
```

### Scan YouTube trends
```bash
cli-anything-social-trends youtube scan --region US
cli-anything-social-trends youtube music --count 20
```

### Cross-platform analysis
```bash
cli-anything-social-trends analyze --region US
cli-anything-social-trends analyze --platform tiktok  # TikTok only
```

### Optimize your account
```bash
cli-anything-social-trends optimize \
  --handle @yourpage \
  --platform tiktok \
  --followers 10000 \
  --avg-views 2000 \
  --avg-likes 150 \
  --avg-comments 30 \
  --posts-per-week 5 \
  --niche fitness \
  --has-link
```

### Theme page strategy
```bash
cli-anything-social-trends theme-page --niche finance
cli-anything-social-trends theme-page --niche luxury --followers 5000
cli-anything-social-trends list-niches
```

### Generate content calendar
```bash
cli-anything-social-trends content-plan \
  --niche fitness \
  --platform tiktok \
  --days 7 \
  --posts-per-day 2 \
  --use-trends           # fetch live trends
```

### Save reports
Add `--save` to any command to export JSON:
```bash
cli-anything-social-trends analyze --region US --save
cli-anything-social-trends tiktok scan --save
```

### JSON output (for agent use)
```bash
cli-anything-social-trends --json tiktok scan
cli-anything-social-trends --json analyze
cli-anything-social-trends --json theme-page --niche finance
```

### Interactive REPL
```bash
cli-anything-social-trends repl
```

## Theme Page Niches

High-converting niches with monetization potential:

| Niche | Potential | Shoutout Rate |
|-------|-----------|---------------|
| Finance | ⭐⭐⭐⭐⭐ | $200-800/post |
| Luxury | ⭐⭐⭐⭐⭐ | $300-1500/post |
| Crypto | ⭐⭐⭐⭐⭐ | $500-5000/post |
| Cars | ⭐⭐⭐⭐ | $200-1000/post |
| Fitness | ⭐⭐⭐⭐ | $100-500/post |
| Fashion | ⭐⭐⭐⭐ | $150-800/post |
| Food | ⭐⭐⭐ | $100-400/post |
| Motivation | ⭐⭐⭐ | $50-200/post |

## Tests

```bash
cd social-trends/agent-harness
pip install -e ".[dev]"
pytest cli_anything/social_trends/tests/ -v
```
