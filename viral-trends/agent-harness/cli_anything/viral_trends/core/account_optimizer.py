"""Social media account optimizer.

Manages account profiles, analyzes performance, generates posting schedules,
and produces optimized captions + hashtag sets for each post.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONFIG_DIR  = Path.home() / ".config" / "viral-trends"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.json"

# Optimal posting windows by platform (UTC hour ranges, most-active days)
POSTING_WINDOWS = {
    "tiktok": {
        "best_days":  ["Tuesday", "Thursday", "Friday"],
        "best_hours": [6, 10, 19, 22],   # UTC
        "frequency":  "1–3 posts/day",
        "notes": "TikTok's algorithm rewards consistency; post at same times daily.",
    },
    "youtube_shorts": {
        "best_days":  ["Saturday", "Sunday", "Wednesday"],
        "best_hours": [14, 15, 16, 20],
        "frequency":  "1 Short/day + 1–2 long-form/week",
        "notes": "Shorts get dedicated shelf placement; separate from main feed.",
    },
    "instagram": {
        "best_days":  ["Monday", "Wednesday", "Friday"],
        "best_hours": [9, 12, 17, 19],
        "frequency":  "4–7 Reels/week",
        "notes": "Reels outperform static posts 3–4× in reach; carousels save for engagement.",
    },
    "twitter_x": {
        "best_days":  ["Tuesday", "Wednesday", "Thursday"],
        "best_hours": [8, 12, 17],
        "frequency":  "3–5 tweets/day",
        "notes": "Threads with images or video get 10× more impressions.",
    },
}

BIO_TEMPLATES = {
    "brand":     "🔥 {niche} content | Tips, tricks & trends | New videos every {frequency} | Link below 👇",
    "theme":     "{emoji} {niche} | Curated for {audience} | DM for collabs 📩",
    "personal":  "{name} | {niche} creator | {cta} | {link}",
    "business":  "{brand_name} | {tagline} | Shop 👇 | {location}",
}

CAPTION_TEMPLATES = [
    "POV: you just discovered {topic} 🤯\n\n{hook}\n\n{hashtags}",
    "{hook} 👇\n\n{body}\n\n{cta}\n\n{hashtags}",
    "Stop scrolling! This {topic} tip will change everything 💡\n\n{body}\n\n{hashtags}",
    "I tested {topic} for 30 days — here's what happened 📊\n\n{body}\n\n{cta}\n\n{hashtags}",
    "The {topic} secret no one tells you:\n\n{body}\n\n{hashtags}",
    "Day {n} of posting about {topic} and here's what I learned:\n\n{body}\n\n{hashtags}",
]

GROWTH_PLAYBOOK = {
    "0_1k": {
        "title": "0 → 1K Followers",
        "focus": "Consistency & niche definition",
        "actions": [
            "Post every single day for 30 days minimum",
            "Pick ONE niche and stick to it — no mixed content",
            "Engage with 10+ accounts in your niche daily (comment first)",
            "Stitch or Duet 3–5 viral videos in your niche per week",
            "Study your 3 best-performing videos and make more like them",
        ],
    },
    "1k_10k": {
        "title": "1K → 10K Followers",
        "focus": "Content quality & hook optimization",
        "actions": [
            "Hook must capture attention in first 0–2 seconds",
            "Test 3 different hook styles per week (question, stat, POV)",
            "Add captions/text overlays — 80% of users watch without sound",
            "Collab with 2–3 creators at same follower count",
            "Add a clear CTA in every video (follow, comment, share)",
            "Build an email list — don't rely on platform alone",
        ],
    },
    "10k_100k": {
        "title": "10K → 100K Followers",
        "focus": "Viral mechanics & monetization foundation",
        "actions": [
            "Identify your 'format' — a recurring series drives loyalty",
            "Reply to EVERY comment for first 30 min after posting",
            "Study analytics weekly — double down on top performers",
            "Start a newsletter / Discord to own your audience",
            "Test paid promotion on top-performing organic posts",
            "Apply for brand deals — most brands start at 10K+",
        ],
    },
    "100k_plus": {
        "title": "100K+ Followers",
        "focus": "Monetization & team scale",
        "actions": [
            "Diversify to 3+ platforms to reduce platform risk",
            "Hire an editor to increase output volume",
            "Launch a digital product (course, ebook, preset pack)",
            "Negotiate brand deals at $100–500 per 10K followers benchmark",
            "Build systems: batch content 2 weeks ahead",
        ],
    },
}


# ── Account storage ───────────────────────────────────────────────────────────

def _load_accounts() -> dict:
    if not ACCOUNTS_FILE.exists():
        return {}
    try:
        return json.loads(ACCOUNTS_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def _save_accounts(accounts: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ACCOUNTS_FILE.write_text(json.dumps(accounts, indent=2))
    ACCOUNTS_FILE.chmod(0o600)


def list_accounts() -> list[dict]:
    accounts = _load_accounts()
    return list(accounts.values())


def add_account(
    handle: str,
    platform: str,
    niche: str = "",
    followers: int = 0,
    following: int = 0,
    avg_views: int = 0,
    link: str = "",
) -> dict:
    accounts = _load_accounts()
    key = f"{platform}:{handle}"
    accounts[key] = {
        "handle":    handle,
        "platform":  platform,
        "niche":     niche,
        "followers": followers,
        "following": following,
        "avg_views": avg_views,
        "link":      link,
        "added_at":  datetime.now(timezone.utc).isoformat(),
        "updated_at":datetime.now(timezone.utc).isoformat(),
    }
    _save_accounts(accounts)
    return accounts[key]


def update_account(handle: str, platform: str, **kwargs: Any) -> dict | None:
    accounts = _load_accounts()
    key = f"{platform}:{handle}"
    if key not in accounts:
        return None
    accounts[key].update(kwargs)
    accounts[key]["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_accounts(accounts)
    return accounts[key]


def remove_account(handle: str, platform: str) -> bool:
    accounts = _load_accounts()
    key = f"{platform}:{handle}"
    if key not in accounts:
        return False
    del accounts[key]
    _save_accounts(accounts)
    return True


def get_account(handle: str, platform: str) -> dict | None:
    return _load_accounts().get(f"{platform}:{handle}")


# ── Optimization ──────────────────────────────────────────────────────────────

def get_posting_schedule(platform: str) -> dict:
    """Return optimal posting schedule for the platform."""
    return POSTING_WINDOWS.get(platform.lower().replace(" ", "_"), {
        "best_days":  ["Monday", "Wednesday", "Friday"],
        "best_hours": [10, 14, 18],
        "frequency":  "3–5 posts/week",
        "notes": "Consistency is more important than exact timing.",
    })


def generate_bio(template: str, **kwargs: Any) -> str:
    """Fill a bio template with provided values."""
    tmpl = BIO_TEMPLATES.get(template, BIO_TEMPLATES["brand"])
    try:
        return tmpl.format(**kwargs)
    except KeyError as e:
        key = str(e).strip("'")
        return tmpl.replace("{" + key + "}", f"[{key}]")


def generate_caption(template_idx: int = 0, **kwargs: Any) -> str:
    """Fill a caption template."""
    idx = template_idx % len(CAPTION_TEMPLATES)
    tmpl = CAPTION_TEMPLATES[idx]
    try:
        return tmpl.format(**kwargs)
    except KeyError:
        return tmpl


def analyze_account(handle: str, platform: str) -> dict:
    """Return optimization recommendations for a stored account."""
    acct = get_account(handle, platform)
    if not acct:
        return {"error": f"Account {platform}:{handle} not found. Add it first with account add."}

    followers = acct.get("followers", 0)
    avg_views = acct.get("avg_views", 0)
    niche     = acct.get("niche", "general")

    # Engagement rate estimate (views/followers)
    er = (avg_views / followers * 100) if followers > 0 else 0

    tier_key = (
        "0_1k"    if followers < 1_000   else
        "1k_10k"  if followers < 10_000  else
        "10k_100k" if followers < 100_000 else
        "100k_plus"
    )

    schedule = get_posting_schedule(platform)

    return {
        "account":          acct,
        "engagement_rate":  f"{er:.1f}%",
        "engagement_label": "Great" if er > 5 else "Good" if er > 2 else "Needs improvement",
        "growth_stage":     GROWTH_PLAYBOOK[tier_key]["title"],
        "priority_actions": GROWTH_PLAYBOOK[tier_key]["actions"],
        "posting_schedule": schedule,
        "niche_tip":        f"Focus all content on '{niche}' — mixed niches hurt algorithm reach by up to 60%.",
        "next_milestone":   _next_milestone(followers),
    }


def _next_milestone(followers: int) -> dict:
    milestones = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000, 500_000, 1_000_000]
    for m in milestones:
        if followers < m:
            return {"target": m, "gap": m - followers}
    return {"target": "1M+", "gap": 0}


def get_growth_playbook(stage: str = "") -> dict:
    if stage in GROWTH_PLAYBOOK:
        return GROWTH_PLAYBOOK[stage]
    return GROWTH_PLAYBOOK
