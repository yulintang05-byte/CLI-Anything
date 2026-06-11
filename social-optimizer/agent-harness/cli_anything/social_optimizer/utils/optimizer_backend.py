"""Social Optimizer backend — account management, scheduling, and content strategy data."""

from __future__ import annotations

import json
import os
from datetime import date, timedelta, datetime
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "cli-anything-social"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"
CONFIG_FILE = CONFIG_DIR / "config.json"

SUPPORTED_PLATFORMS = ["tiktok", "youtube", "instagram", "twitter", "facebook"]


# ── Config & Accounts ─────────────────────────────────────────────────────

def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def load_accounts() -> dict:
    if not ACCOUNTS_FILE.exists():
        return {}
    try:
        with open(ACCOUNTS_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_accounts(accounts: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f, indent=2)
    ACCOUNTS_FILE.chmod(0o600)


def add_account(platform: str, handle: str, niche: str = "", goal: str = "") -> dict:
    """Register an account in the local profile store."""
    platform = platform.lower()
    if platform not in SUPPORTED_PLATFORMS:
        raise ValueError(f"Unsupported platform: {platform}. Choose from: {SUPPORTED_PLATFORMS}")
    handle = handle.lstrip("@").strip()
    accounts = load_accounts()
    key = f"{platform}/{handle}"
    accounts[key] = {
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "goal": goal,
        "added": date.today().isoformat(),
    }
    save_accounts(accounts)
    return accounts[key]


def list_accounts() -> list[dict]:
    accounts = load_accounts()
    return list(accounts.values())


def get_account(handle: str, platform: str | None = None) -> dict | None:
    accounts = load_accounts()
    handle = handle.lstrip("@")
    for key, acct in accounts.items():
        if acct["handle"] == handle:
            if platform is None or acct["platform"] == platform.lower():
                return acct
    return None


def remove_account(handle: str, platform: str) -> bool:
    accounts = load_accounts()
    key = f"{platform.lower()}/{handle.lstrip('@')}"
    if key in accounts:
        del accounts[key]
        save_accounts(accounts)
        return True
    return False


# ── Theme Page Playbook ────────────────────────────────────────────────────

THEME_PAGE_PLAYBOOK = {
    "what_is_a_theme_page": (
        "A theme page is an account built around a niche topic (not a personal brand). "
        "You curate, repost, or create content about that niche without showing your face. "
        "Examples: @fitness.motivations, @luxurycars.daily, @mindset.quotes. "
        "Revenue comes from shoutouts, sponsored posts, account flipping, or affiliate links."
    ),
    "phase_1_setup": {
        "title": "Phase 1: Setup (Days 1-3)",
        "steps": [
            "Choose a hyper-specific niche (not just 'fitness', but 'home gym equipment reviews')",
            "Pick a platform: TikTok for fastest growth, Instagram for monetization, YouTube for longevity",
            "Create a memorable username: [niche]+[word] (e.g. @gymlife.daily, @crypto.gems)",
            "Write a bio with: what you post | posting frequency | CTA (follow for daily X)",
            "Create or source a clean, niche-matched profile picture (no faces needed)",
            "Set to Creator/Business account for analytics access",
        ],
    },
    "phase_2_content_strategy": {
        "title": "Phase 2: Content Strategy (Days 4-14)",
        "steps": [
            "Identify 10 top accounts in your niche — study their top 10 posts",
            "Find 5 content pillars for your niche (e.g. fitness: tips, transformations, gear, motivation, humor)",
            "Source content legally: create original, use royalty-free clips, or repost with credit + permission",
            "Create a 30-day content calendar BEFORE posting (don't improvise)",
            "Batch-create 7-14 days of content before going live",
            "Post 1-3x per day consistently for the first 30 days (volume beats quality early on)",
        ],
    },
    "phase_3_growth": {
        "title": "Phase 3: Growth Hacking (Days 15-90)",
        "steps": [
            "Engage with every comment on your videos for the first hour after posting",
            "Comment on top creators' posts in your niche (adds 5-15 followers/day from visibility)",
            "Use trending sounds/hashtags that align with your niche daily",
            "Run a 'follow + comment to win' giveaway with a related prize at 1K followers",
            "DM 5-10 accounts in similar niche per day for follow-for-follow or collaborations",
            "Study your analytics weekly: double down on content types with >50% avg watch time",
            "Create series content: 'Day 1 of X', 'Part 1 of Y' — drives followers for the next episode",
        ],
    },
    "phase_4_monetization": {
        "title": "Phase 4: Monetization (1K-10K followers)",
        "milestones": {
            "1K followers":   "Start selling shoutouts ($10-50/post), add affiliate links in bio",
            "5K followers":   "Charge $50-200/shoutout, approach small brands in your niche",
            "10K followers":  "Charge $200-500/post, launch TikTok Creator Fund, offer paid promotions",
            "50K followers":  "Brand deals $500-2,000, sell the account ($3,000-15,000 value)",
            "100K followers": "Brand deals $2,000-10,000, launch own products/courses",
        },
        "monetization_methods": [
            "Paid shoutouts — most common for theme pages",
            "Affiliate marketing — post links to products you review (10-30% commission)",
            "Account flipping — build then sell accounts ($1,000+ at 10K followers)",
            "Digital products — sell presets, templates, guides related to your niche",
            "Sponsored posts — charge brands for featured posts",
            "Link in bio services — use Linktree to monetize multiple streams at once",
        ],
    },
    "niches_with_highest_roi": [
        "Finance / Crypto (highest CPM, easiest affiliate)",
        "Fitness / Weight Loss (massive demand, easy products)",
        "Luxury Lifestyle (high-end brand sponsorships)",
        "Pets / Animals (viral content, huge audience)",
        "Motivational Quotes (mass appeal, passive curation)",
        "Beauty / Skincare (affiliate commissions are high)",
        "Travel (brand deals from tourism industry)",
        "Food / Recipes (easiest viral content format)",
        "Cars / Automotive (male 18-34 demographic = high ad rates)",
        "Relationships / Dating (emotional content = high shares)",
    ],
    "mistakes_to_avoid": [
        "Posting without a niche strategy — pick ONE niche and stick to it for 90 days",
        "Using copyrighted music without licensing — always use TikTok/YouTube's royalty-free library",
        "Ignoring analytics — check every 7 days and drop underperforming content types",
        "Buying fake followers — kills your engagement rate and account reach permanently",
        "Not building an email list — social accounts can be banned; own your audience",
        "Posting inconsistently — the algorithm punishes gaps over 3+ days",
        "Engaging with negative comments publicly — mute/block only",
        "Reposting without credit — creates legal risk and community backlash",
    ],
    "conversion_from_personal_brand": {
        "title": "Converting Your Personal Brand to a Theme Page",
        "steps": [
            "Step 1: Define the niche angle your personal content will now represent",
            "Step 2: Change username to niche-themed name (redirect followers via pinned post)",
            "Step 3: Purge off-brand posts or archive them (keep engagement rate healthy)",
            "Step 4: Rewrite bio to reflect the new niche direction",
            "Step 5: Announce the 'pivot' in a video/post — transparency retains 60-70% of followers",
            "Step 6: Post 5 niche-specific videos before un-pinning the transition post",
            "Step 7: Engage existing followers to comment on new content to reset algorithm signals",
        ],
    },
}

# ── Content Calendar Generator ────────────────────────────────────────────

CONTENT_TYPES = {
    "tiktok": [
        "Educational tip (problem → solution)",
        "Transformation / before-after",
        "Story time (personal anecdote in niche)",
        "Trending sound + niche overlay",
        "Q&A (ask followers a question)",
        "Day-in-life (niche POV)",
        "Myth-busting ('Don't believe X')",
        "Product review / recommendation",
        "Challenge / trend in your niche",
        "Collab / duet with niche creator",
    ],
    "youtube": [
        "Long-form tutorial (10-20 min)",
        "YouTube Short (60 sec tip)",
        "Listicle ('Top 10 ...')",
        "Case study ('I tried X for 30 days')",
        "Comparison ('A vs B')",
        "Review (product / service)",
        "Day-in-life / vlog",
        "Interview / collaboration",
        "Reaction / commentary",
        "Full guide / documentary",
    ],
    "instagram": [
        "Carousel post (educational slides)",
        "Reel (15-30 sec tip)",
        "Story poll / Q&A",
        "Single image quote",
        "Behind-the-scenes story",
        "Product/affiliate showcase Reel",
        "Collab post with niche account",
        "Before/after transformation",
        "Infographic carousel",
        "Trending audio Reel",
    ],
}

POSTING_CADENCE = {
    "tiktok":    {"per_day": 2, "per_week": 14},
    "youtube":   {"per_day": 0.5, "per_week": 3},
    "instagram": {"per_day": 1, "per_week": 7},
    "twitter":   {"per_day": 3, "per_week": 21},
}


def generate_content_calendar(
    platform: str = "tiktok",
    niche: str = "fitness",
    days: int = 30,
    posts_per_day: int = 2,
) -> list[dict]:
    """Generate a content calendar for the given platform and niche."""
    platform = platform.lower()
    content_types = CONTENT_TYPES.get(platform, CONTENT_TYPES["tiktok"])
    cadence = POSTING_CADENCE.get(platform, {"per_day": 1, "per_week": 7})
    actual_ppd = posts_per_day or cadence["per_day"]

    calendar: list[dict] = []
    start = date.today()
    type_idx = 0

    for day_offset in range(days):
        current_date = start + timedelta(days=day_offset)
        day_name = current_date.strftime("%A").lower()
        posts_today = max(1, round(actual_ppd))

        for slot in range(posts_today):
            ctype = content_types[type_idx % len(content_types)]
            type_idx += 1

            calendar.append({
                "date": current_date.isoformat(),
                "day": day_name,
                "platform": platform,
                "slot": slot + 1,
                "content_type": ctype,
                "niche": niche,
                "status": "planned",
                "notes": "",
            })

    return calendar


# ── Cross-platform trend report ───────────────────────────────────────────

def build_combined_report(
    tiktok_data: dict | None = None,
    youtube_data: dict | None = None,
    niche: str = "",
) -> dict:
    """Combine TikTok and YouTube trend data into a unified report."""
    from datetime import date as _date

    common_tags: list[str] = []
    if tiktok_data and youtube_data:
        tt_tags = {t["hashtag"] for t in tiktok_data.get("trending_hashtags", [])}
        yt_tags = {t["tag"] for t in youtube_data.get("trending_tags", [])}
        common_tags = sorted(tt_tags & yt_tags)

    report = {
        "date": _date.today().isoformat(),
        "niche": niche or "general",
        "cross_platform_tags": common_tags,
        "tiktok_trends": tiktok_data or {},
        "youtube_trends": youtube_data or {},
        "action_items": _generate_action_items(tiktok_data, youtube_data, common_tags),
    }
    return report


def _generate_action_items(tt: dict | None, yt: dict | None, common: list[str]) -> list[str]:
    items = []
    if common:
        items.append(f"Cross-platform mega tags (post on BOTH today): " + ", ".join(f"#{t}" for t in common[:5]))
    if tt:
        top_tt = [h["hashtag"] for h in tt.get("trending_hashtags", [])[:3]]
        if top_tt:
            items.append("TikTok priority hashtags: " + " ".join(f"#{t}" for t in top_tt))
        sounds = tt.get("trending_sounds", [])[:2]
        for s in sounds:
            items.append(f"Use trending TikTok sound: '{s['title']}' by {s.get('artist', 'unknown')}")
    if yt:
        top_kw = yt.get("trending_keywords", [])[:3]
        if top_kw:
            items.append("YouTube title keywords to include: " + ", ".join(top_kw))
    if not items:
        items.append("Run 'trends fetch' on both platforms to populate action items")
    return items


# ── Hashtag strategy ──────────────────────────────────────────────────────

PLATFORM_HASHTAG_RULES = {
    "tiktok": {
        "optimal_count": "3-5",
        "placement": "In the caption",
        "rules": [
            "1 mega hashtag (#fitness, 50B+ views)",
            "1-2 niche hashtags (#homeworkout, 5B+ views)",
            "1-2 micro hashtags (#morningworkout, 50M+ views)",
            "Rotate sets every 7 days to avoid shadow bans",
        ],
    },
    "youtube": {
        "optimal_count": "3 (displayed), 10-15 (in description/tags)",
        "placement": "Last line of description (shown as clickable links) + Tags section",
        "rules": [
            "First 3 hashtags appear below video title — make them count",
            "Keep total hashtags under 15 or YouTube ignores all",
            "Use keyword-based hashtags, not generic ones",
            "Match hashtags to video title keywords for SEO boost",
        ],
    },
    "instagram": {
        "optimal_count": "5-10",
        "placement": "In the caption or first comment",
        "rules": [
            "Avoid using the same 30 hashtags on every post (shadow ban risk)",
            "Mix sizes: 2 large (1M+) + 4 medium (100K-1M) + 4 niche (<100K)",
            "Research hashtag recent posts before adding (avoid inactive ones)",
            "Add location hashtags for local niche businesses",
        ],
    },
}


def get_hashtag_rules(platform: str) -> dict:
    key = platform.lower()
    return PLATFORM_HASHTAG_RULES.get(key, PLATFORM_HASHTAG_RULES["tiktok"])
