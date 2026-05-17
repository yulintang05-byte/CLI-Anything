# cli-anything-social-trends

Scrape viral YouTube + TikTok trends, build hashtag strategies, track trending music, audit and optimize your social accounts, and generate complete theme page creation playbooks — all from the CLI.

## Installation

```bash
pip install -e .
playwright install chromium  # for TikTok playwright mode
```

## Quick Start

```bash
# 1. Configure your API key (YouTube Data API v3 — free at console.cloud.google.com)
cli-anything-social-trends setup youtube-key AIza...

# 2. Set your niche
cli-anything-social-trends setup niche fitness

# 3. Register your accounts
cli-anything-social-trends accounts add youtube MyChannel --channel-id UC12345
cli-anything-social-trends accounts add tiktok @myTikTok

# 4. Scrape latest trends
cli-anything-social-trends scrape all

# 5. Get your hashtag strategy
cli-anything-social-trends hashtags strategy

# 6. See trending music/sounds
cli-anything-social-trends music trending

# 7. Audit all your accounts
cli-anything-social-trends optimize all-accounts

# 8. Generate theme page plan
cli-anything-social-trends theme-page plan fitness --platform tiktok --followers 5000
```

## TikTok Setup (Optional but Recommended)

For richer TikTok data, provide your `ms_token`:
1. Open TikTok in Chrome, log in
2. DevTools (F12) → Application → Cookies → tiktok.com → `ms_token`
3. Copy the value:

```bash
cli-anything-social-trends setup tiktok-token YOUR_MS_TOKEN_VALUE
```

## Supported Niches

`fitness` · `food` · `travel` · `tech` · `beauty` · `gaming` · `motivation` · `finance` · `fashion` · `comedy`

## All Commands

| Command | Description |
|---------|-------------|
| `setup youtube-key KEY` | Set YouTube Data API v3 key |
| `setup tiktok-token TOKEN` | Set TikTok session token |
| `setup region CODE` | Set region (US, GB, AU, CA) |
| `setup niche NICHE` | Set default niche |
| `accounts add PLATFORM USER` | Register an account |
| `accounts list` | List registered accounts |
| `scrape youtube --trending` | Scrape YouTube trending videos + hashtags |
| `scrape tiktok --trending` | Scrape TikTok trending videos + sounds |
| `scrape all` | Scrape both platforms (auto-saves) |
| `hashtags strategy` | Build ready-to-paste hashtag block |
| `hashtags compare #tag1 #tag2` | Compare specific hashtags |
| `music trending` | Show trending sounds and tracks |
| `optimize account tiktok user` | Full audit of one account |
| `optimize all-accounts` | Audit all registered accounts |
| `theme-page plan NICHE` | Growth plan + monetization estimate |
| `theme-page conversion-guide NICHE` | Step-by-step theme page setup |
| `theme-page branding NICHE NAME` | Branding checklist |
| `report list` | List saved reports |
| `status` | Show configuration status |

## JSON Output

Every command supports `--json` for machine-readable output:

```bash
cli-anything-social-trends --json hashtags strategy --niche fitness
cli-anything-social-trends --json theme-page plan finance --platform youtube
```

## Interactive REPL

Run without arguments to enter interactive mode:

```bash
cli-anything-social-trends
# > scrape all
# > hashtags strategy
# > optimize all-accounts
# > exit
```

## Reports

All scraped data and analysis is saved to `~/.cli-anything-social-trends/reports/`.
Reports are timestamped JSON files you can query later:

```bash
cli-anything-social-trends report list
cli-anything-social-trends report show 1
```
