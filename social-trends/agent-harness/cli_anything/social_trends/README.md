# social-trends — CLI Harness

Agent-native social media trend scraping, hashtag research, account optimization, and theme-page strategy.

## Commands

### trends
```bash
social-trends trends fetch --platform both --limit 10
social-trends trends list
social-trends trends search "workout"
social-trends trends export -o trends.json
```

### hashtags
```bash
social-trends hashtags research fitness --platform tiktok --limit 20
social-trends hashtags rank --by engagement
social-trends hashtags suggest --niche finance --count 30
social-trends hashtags export -o hashtags.json
```

### music
```bash
social-trends music trending --platform tiktok --genre pop --limit 15
social-trends music list
social-trends music search "taylor"
social-trends music export -o music.json
```

### accounts
```bash
social-trends accounts add --platform tiktok --username mypage --niche fitness
social-trends accounts list
social-trends accounts optimize acc_abc123
social-trends accounts score acc_abc123
social-trends accounts export -o accounts.json
```

### theme-pages
```bash
social-trends theme-pages niches
social-trends theme-pages guide --niche finance
social-trends theme-pages strategy crypto
social-trends theme-pages convert acc_abc123 --to luxury
```

### schedule
```bash
social-trends schedule optimize acc_abc123
social-trends schedule calendar acc_abc123 --days 14
social-trends schedule export acc_abc123 -o schedule.json
```

## JSON output

All commands support `--json` for structured output:

```bash
social-trends --json trends fetch --platform youtube --limit 5
```

## TikTok API

Live TikTok data requires a Research API token:

```bash
export TIKTOK_API_TOKEN=your_token_here
social-trends music trending --platform tiktok
```

Without a token, all TikTok commands return rich mock data.

## Session persistence

All data is cached to `~/.social_trends_session.json`.
