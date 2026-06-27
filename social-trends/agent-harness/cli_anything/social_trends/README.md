# social-trends CLI

Agent-native viral trend intelligence for TikTok, YouTube, and Instagram.

Scrapes YouTube and TikTok for viral trends, hashtags, and music. Audits and
optimizes social media accounts. Provides theme page conversion playbooks and
step-by-step monetization strategies.

---

## Installation

```bash
cd social-trends/agent-harness
pip install -e .
```

---

## Quick Start

```bash
# Fetch trending content (YouTube + TikTok)
social-trends trends fetch --platform all --region us --limit 20

# Get optimized hashtags for fitness content on TikTok
social-trends hashtags mix fitness --platform tiktok --count 5

# Find trending music for fashion content
social-trends music fetch && social-trends music recommend fashion

# Full account audit
social-trends account add @myaccount tiktok \
  --followers 8500 \
  --bio "Fitness content | DM for coaching | link below 💪" \
  --has-link \
  --niche fitness \
  --avg-views 15000 --avg-likes 900 --avg-comments 80 \
  --posts-per-week 14
social-trends account audit

# See all theme page blueprints
social-trends theme list

# Get the fitness theme page blueprint
social-trends theme show fitness

# Affiliate marketing playbook
social-trends theme monetize affiliate

# Assess your account for monetization readiness
social-trends theme assess --followers 8500 --niche fitness --has-link

# Growth roadmap for 1K→10K phase
social-trends theme roadmap 1k_to_10k
```

---

## Commands Reference

### `trends`

| Command | Description |
|---------|-------------|
| `trends fetch` | Fetch viral content from YouTube and/or TikTok |
| `trends insights` | Summarize cached trends: top hashtags, music, creators |

Options for `trends fetch`:
- `--platform` — `youtube`, `tiktok`, or `all` (default: `all`)
- `--region` — Country code: `us`, `uk`, `ca`, `au`, `in`, `de`, `fr`, `jp`, `br` (default: `us`)
- `--category` — `all`, `music`, `gaming`, `news`, `sports`, `entertainment`, `tech`
- `--limit` — Max results per platform (default: 20)
- `--apify-key` — Apify API key for production-grade TikTok scraping (env: `APIFY_KEY`)

### `hashtags`

| Command | Description |
|---------|-------------|
| `hashtags mix <niche>` | Generate optimal hashtag mix (3-5 tags, broad+mid+niche) |
| `hashtags audit <tags...>` | Score each hashtag on competition/reach |
| `hashtags caption <text> <niche>` | Build full caption with hashtag block |
| `hashtags niches` | List all 16+ supported niches |

### `music`

| Command | Description |
|---------|-------------|
| `music fetch` | Fetch trending music from Apple Music, Billboard, TikTok |
| `music recommend <niche>` | Filter trending music by niche mood match |

### `account`

| Command | Description |
|---------|-------------|
| `account add <username> <platform>` | Register an account profile |
| `account audit` | Full optimization audit (bio, engagement, schedule) |
| `account schedule` | Peak posting times and frequency recommendations |
| `account bio-audit <bio>` | Audit a bio string |

### `theme`

| Command | Description |
|---------|-------------|
| `theme list` | List all 10+ theme page blueprints |
| `theme show <name>` | Full blueprint: content pillars, hashtags, growth hacks |
| `theme monetize <strategy>` | Step-by-step monetization playbook |
| `theme assess` | What monetization you're ready for by follower count |
| `theme roadmap <phase>` | Action plan for 0→1K, 1K→10K, or 10K→100K |

Monetization strategies: `affiliate`, `tiktok_shop`, `paid_shoutouts`, `digital_products`, `brand_deals`

---

## JSON Output Mode

All commands support `--json` for agent-consumable output:

```bash
social-trends --json trends fetch --platform tiktok --limit 5
social-trends --json hashtags mix fitness
social-trends --json theme show fitness
social-trends --json account audit
```

---

## REPL Mode

Run without a subcommand to enter interactive REPL:

```bash
social-trends
```

```
╔══════════════════════════════════════════════════════╗
║          social-trends  v1.0.0                       ║
║  Viral trend intelligence: TikTok · YouTube · IG     ║
║  Type 'help' for commands, 'exit' to quit            ║
╚══════════════════════════════════════════════════════╝
social-trends> trends fetch --platform youtube --limit 5
social-trends[fitness]> hashtags mix fitness
social-trends[fitness]> theme show fitness
social-trends> exit
```

---

## Production TikTok Scraping (Apify)

TikTok aggressively blocks unauthenticated scrapers. For reliable, production-grade
trending data use the Apify actor:

```bash
export APIFY_KEY=your_apify_api_key
social-trends trends fetch --platform tiktok --apify-key $APIFY_KEY
```

Get a free Apify account at [apify.com](https://apify.com) — the free tier
provides ~$5/month of compute, enough for ~50-100 trend fetches/day.

---

## Theme Page Blueprints

Pre-built blueprints covering:

| Blueprint | Niche | Difficulty |
|-----------|-------|-----------|
| Quiet Luxury Lifestyle | fashion/lifestyle | medium |
| Gym & Fitness Motivation | fitness | easy |
| Finance & Wealth Building | finance | medium |
| Dark Academia | lifestyle/aesthetic | easy |
| Food & Recipe (Viral) | food | easy |
| Crypto & Web3 Alpha | crypto | hard |
| Pet Theme (Dogs/Cats) | pets | easy |
| Luxury Travel | travel | hard |
| Motivation & Mindset | motivation | medium |
| Aesthetic Nature / Cottagecore | lifestyle | easy |

---

## Monetization Playbooks

Five complete playbooks with step-by-step instructions:

- **Affiliate Marketing** — $500–$10,000+/month, any follower count
- **TikTok Shop** — $200–$50,000+/month, 1,000+ followers
- **Paid Shoutouts** — $100–$5,000/month, 5,000+ followers
- **Digital Products** — $1,000–$100,000+/month, audience trust required
- **Brand Partnerships** — $500–$50,000+/month, 10,000+ followers

---

## Caching

All HTTP responses are cached for 1 hour in `~/.cache/cli-social-trends/`.
Clear the cache:

```bash
social-trends cache clear
```

---

## FTC Compliance Note

When promoting affiliate links or sponsored content, FTC regulations require
disclosure. Always include `#ad`, `#affiliate`, or `#sponsored` in your caption.
The `hashtags caption` command does **not** add these automatically — you must
add disclosure tags manually.
