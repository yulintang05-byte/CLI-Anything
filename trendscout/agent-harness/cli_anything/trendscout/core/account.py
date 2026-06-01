"""TrendScout – account management and optimization.

Tracks multiple social media accounts and generates data-driven
optimization recommendations.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from cli_anything.trendscout.core.session import Session


# ── Account CRUD ──────────────────────────────────────────────────────────────

def add_account(
    session: Session,
    handle: str,
    platform: str,
    niche: str = "general",
    followers: int = 0,
    notes: str = "",
) -> Dict[str, Any]:
    """Register a social media account for tracking."""
    platform_lower = platform.lower()
    if platform_lower not in ("tiktok", "youtube", "instagram", "twitter", "x"):
        raise ValueError(f"Unsupported platform '{platform}'. Choose: tiktok, youtube, instagram, twitter")

    # Normalize handle
    clean_handle = handle.lstrip("@")

    accounts = session.config["accounts"]
    for acc in accounts:
        if acc["handle"].lower() == clean_handle.lower() and acc["platform"] == platform_lower:
            raise ValueError(f"Account @{clean_handle} on {platform_lower} already exists.")

    acc_id = f"acc{len(accounts)}"
    account = {
        "id": acc_id,
        "handle": clean_handle,
        "platform": platform_lower,
        "niche": niche,
        "followers": followers,
        "notes": notes,
        "added_at": datetime.now(timezone.utc).isoformat(),
        "profile_score": None,
        "recommendations": [],
    }

    session.snapshot(f"Add account @{clean_handle} ({platform_lower})")
    accounts.append(account)

    return {"success": True, "id": acc_id, "handle": clean_handle, "platform": platform_lower, "niche": niche}


def remove_account(session: Session, account_id: str) -> Dict[str, Any]:
    accounts = session.config["accounts"]
    acc = _find_account(accounts, account_id)
    session.snapshot(f"Remove account {account_id}")
    session.config["accounts"] = [a for a in accounts if a["id"] != account_id]
    return {"success": True, "removed_id": account_id, "handle": acc["handle"]}


def list_accounts(session: Session) -> List[Dict[str, Any]]:
    return [
        {
            "id": a["id"],
            "handle": a["handle"],
            "platform": a["platform"],
            "niche": a["niche"],
            "followers": a["followers"],
            "profile_score": a.get("profile_score"),
            "notes": a.get("notes", ""),
        }
        for a in session.config["accounts"]
    ]


def update_account(
    session: Session,
    account_id: str,
    followers: Optional[int] = None,
    niche: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    accounts = session.config["accounts"]
    acc = _find_account(accounts, account_id)
    session.snapshot(f"Update account {account_id}")

    if followers is not None:
        acc["followers"] = followers
    if niche is not None:
        acc["niche"] = niche
    if notes is not None:
        acc["notes"] = notes

    return {"success": True, "id": account_id, "handle": acc["handle"], "followers": acc["followers"]}


# ── Profile optimization audit ────────────────────────────────────────────────

_PLATFORM_CHECKLIST: Dict[str, List[Dict[str, Any]]] = {
    "tiktok": [
        {"id": "bio_keywords", "label": "Bio contains niche keywords", "weight": 15, "tip": "Include 2–3 niche keywords in your 80-char bio (e.g. 'Fitness coach | Home workouts | Daily tips')."},
        {"id": "profile_pic", "label": "High-res, face-visible profile photo", "weight": 10, "tip": "Faces get 38% more clicks than logos on TikTok. Use a bright, high-contrast headshot."},
        {"id": "link_in_bio", "label": "Link-in-bio tool connected (Linktree/Stan)", "weight": 10, "tip": "Use Stan.store or Linktree to capture leads. Must be on 1,000+ follower accounts."},
        {"id": "username_niche", "label": "Username reflects niche", "weight": 8, "tip": "Niche-relevant usernames rank better in search. E.g. @fitnesswith_mike vs @mike_xyz."},
        {"id": "pinned_videos", "label": "3 pinned videos cover hook + value + CTA", "weight": 12, "tip": "Pin your best-performing video, a 'who I am' intro, and a tutorial/value video."},
        {"id": "consistent_posting", "label": "Posts at least 4x/week", "weight": 15, "tip": "TikTok's algorithm favors consistent posters. Schedule content using a content calendar."},
        {"id": "sound_strategy", "label": "Uses trending sounds within 24h", "weight": 12, "tip": "Check TikTok Creative Center daily. Use trending sounds early for algorithmic boost."},
        {"id": "hashtag_mix", "label": "3-5 hashtag mix: niche + trending + broad", "weight": 10, "tip": "Avoid hashtag stuffing. Use 1–2 niche tags + 1–2 trending tags + #fyp/#foryou."},
        {"id": "cta_in_video", "label": "Clear CTA in captions or video", "weight": 8, "tip": "'Follow for daily [niche] tips' in captions drives 25% more follows per view."},
    ],
    "youtube": [
        {"id": "channel_art", "label": "Channel banner is 2560x1440, brand-aligned", "weight": 8, "tip": "Use Canva's YouTube banner template. Show your niche and upload schedule."},
        {"id": "channel_description", "label": "Channel description has keywords + upload schedule", "weight": 12, "tip": "First 100 chars appear in search. Include primary keyword, schedule, and value prop."},
        {"id": "custom_url", "label": "Custom URL claimed", "weight": 5, "tip": "Claim youtube.com/c/YourBrand at 100 subscribers. Makes you look established."},
        {"id": "thumbnails", "label": "Custom thumbnails with consistent branding", "weight": 15, "tip": "Consistent color palette + font + face expression = recognizable thumbnail style."},
        {"id": "playlists", "label": "Content organized into playlists", "weight": 10, "tip": "Playlists increase session time (a key YouTube ranking signal). Create 3–5 topic playlists."},
        {"id": "end_screens", "label": "End screens on all videos", "weight": 10, "tip": "Add end screen at -20s with 1 video + 1 subscribe button. Boosts watch time."},
        {"id": "chapters", "label": "Video chapters in descriptions", "weight": 8, "tip": "Chapters (timestamps) improve search snippets and reduce drop-off."},
        {"id": "seo_titles", "label": "SEO-optimized video titles", "weight": 15, "tip": "Primary keyword first, then hook. E.g. 'Home Workout for Beginners (No Equipment Needed)'."},
        {"id": "upload_consistency", "label": "Consistent upload schedule", "weight": 12, "tip": "2–3 videos/week grows faster than sporadic uploads. Tell viewers your schedule."},
        {"id": "shorts_strategy", "label": "YouTube Shorts alongside long-form", "weight": 5, "tip": "Shorts introduce new audiences who then migrate to long-form. 1 Short per long-form video."},
    ],
    "instagram": [
        {"id": "business_account", "label": "Business/Creator account (not Personal)", "weight": 12, "tip": "Business accounts unlock analytics, contact buttons, and promoted posts."},
        {"id": "bio_link", "label": "Link in bio active (Linktree/standalone)", "weight": 10, "tip": "Change the link to match each new post/campaign. Mention it in captions."},
        {"id": "highlight_covers", "label": "Story Highlights with branded covers", "weight": 8, "tip": "Create 4–6 Highlight categories with matching cover icons. Shows visitors you're professional."},
        {"id": "reel_cadence", "label": "4–7 Reels/week", "weight": 18, "tip": "Reels get 2× the reach of static posts. Prioritize Reels over carousels in growth phase."},
        {"id": "grid_aesthetic", "label": "Cohesive grid aesthetic (color palette)", "weight": 10, "tip": "Plan your grid 9 posts ahead using Planoly or Preview. Consistent look = more follows from profile visits."},
        {"id": "hashtag_research", "label": "Hashtag research done per post", "weight": 10, "tip": "Use 5–10 targeted hashtags (not all #100M+ tags). Mix sizes: 10k–100k + 100k–1M + 1M+."},
        {"id": "caption_hooks", "label": "First line of caption hooks before 'more' fold", "weight": 12, "tip": "Instagram truncates captions at ~125 chars. Put the hook here, not 'Hi guys today...'"},
        {"id": "stories_daily", "label": "3–10 Stories daily", "weight": 10, "tip": "Stories keep you top-of-feed. Use polls + questions to boost algorithmic engagement."},
        {"id": "collab_content", "label": "Collab posts and Duets used", "weight": 10, "tip": "Instagram Collabs split the reach — your content shows on both profiles."},
    ],
    "twitter": [
        {"id": "bio_keywords", "label": "Bio has niche keywords + personality", "weight": 15, "tip": "Twitter bio appears in search. Include what you do + what value followers get."},
        {"id": "header_image", "label": "Branded header/banner image", "weight": 8, "tip": "Use header to show latest project, product, or a CTA."},
        {"id": "pinned_tweet", "label": "Pinned tweet is your best lead magnet", "weight": 15, "tip": "Pin a thread, free resource, or viral tweet. This is your first impression."},
        {"id": "tweet_frequency", "label": "3–10 tweets/day", "weight": 15, "tip": "Twitter rewards volume. Threads + quote tweets + replies all count. Mix formats."},
        {"id": "thread_content", "label": "Weekly thread on niche topic", "weight": 15, "tip": "Threads get 20× more impressions than single tweets. End with a CTA."},
        {"id": "engagement_ratio", "label": "Reply to 10+ accounts daily", "weight": 12, "tip": "Replying to bigger accounts in your niche puts you in front of their audience."},
        {"id": "spaces", "label": "Twitter Spaces participation", "weight": 10, "tip": "Host or speak in weekly Spaces. Audio presence builds authority faster than text."},
        {"id": "newsletter_cta", "label": "Newsletter or community CTA visible", "weight": 10, "tip": "Twitter is best used as a funnel. Drive followers to email list or Discord."},
    ],
}

# Add 'x' as alias for 'twitter'
_PLATFORM_CHECKLIST["x"] = _PLATFORM_CHECKLIST["twitter"]


def audit_account(
    session: Session,
    account_id: str,
    completed_items: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Run a profile optimization audit and generate a score + action plan."""
    accounts = session.config["accounts"]
    acc = _find_account(accounts, account_id)

    platform = acc["platform"]
    checklist = _PLATFORM_CHECKLIST.get(platform, [])
    completed = set(completed_items or [])

    score = 0
    total_weight = sum(item["weight"] for item in checklist)
    done_items = []
    todo_items = []

    for item in checklist:
        if item["id"] in completed:
            score += item["weight"]
            done_items.append(item)
        else:
            todo_items.append(item)

    pct_score = round((score / total_weight) * 100) if total_weight > 0 else 0

    # Sort todos by weight descending (highest impact first)
    todo_items.sort(key=lambda x: x["weight"], reverse=True)

    grade = "A" if pct_score >= 90 else "B" if pct_score >= 75 else "C" if pct_score >= 60 else "D" if pct_score >= 45 else "F"

    result = {
        "account_id": account_id,
        "handle": acc["handle"],
        "platform": platform,
        "niche": acc["niche"],
        "followers": acc["followers"],
        "score": pct_score,
        "grade": grade,
        "completed_count": len(done_items),
        "todo_count": len(todo_items),
        "top_priority_actions": [
            {"action": item["label"], "tip": item["tip"], "impact": item["weight"]}
            for item in todo_items[:5]
        ],
        "completed_items": [item["label"] for item in done_items],
        "all_checklist": checklist,
    }

    # Cache result in session
    session.snapshot(f"Audit account {account_id}")
    acc["profile_score"] = pct_score
    acc["recommendations"] = [item["tip"] for item in todo_items[:5]]

    return result


def optimize_all_accounts(session: Session) -> Dict[str, Any]:
    """Run a baseline audit on all accounts (no completed items assumed)."""
    results = []
    for acc in session.config["accounts"]:
        audit = audit_account(session, acc["id"], completed_items=[])
        results.append({
            "id": acc["id"],
            "handle": acc["handle"],
            "platform": acc["platform"],
            "niche": acc["niche"],
            "score": audit["score"],
            "grade": audit["grade"],
            "top_action": audit["top_priority_actions"][0] if audit["top_priority_actions"] else None,
        })

    results.sort(key=lambda x: x["score"])  # Worst-score first (most urgent)

    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "total_accounts": len(results),
        "accounts": results,
        "overall_avg_score": round(sum(r["score"] for r in results) / len(results)) if results else 0,
    }


def growth_plan(
    session: Session,
    account_id: str,
    goal_followers: int = 10000,
    timeframe_weeks: int = 12,
) -> Dict[str, Any]:
    """Generate a week-by-week growth plan for an account."""
    accounts = session.config["accounts"]
    acc = _find_account(accounts, account_id)

    current = acc["followers"]
    gap = max(0, goal_followers - current)
    weekly_target = gap // timeframe_weeks if timeframe_weeks > 0 else gap

    platform = acc["platform"]
    niche = acc["niche"]

    phases = [
        {
            "phase": 1,
            "weeks": "1–4",
            "focus": "Foundation",
            "tasks": [
                f"Complete all profile optimization checklist items for {platform}",
                "Define content pillars (3 main topics within your niche)",
                f"Post at optimal times for {platform} (see 'trends times' command)",
                "Build a 30-day content calendar using trend data",
                "Study top 10 accounts in your niche — note what works",
            ],
            "weekly_follower_target": weekly_target // 3,
        },
        {
            "phase": 2,
            "weeks": "5–8",
            "focus": "Acceleration",
            "tasks": [
                "Run 2 trending hashtag/sound challenges per week",
                "Engage with 20–30 accounts in your niche daily",
                "Collaborate or duet/stitch 1 creator/week",
                "Analyze your analytics — double down on what works",
                "Repurpose top content across platforms",
            ],
            "weekly_follower_target": weekly_target,
        },
        {
            "phase": 3,
            "weeks": "9–12",
            "focus": "Scale",
            "tasks": [
                "Launch a viral challenge or hashtag campaign",
                "Post 1 'bait' piece weekly (controversial/polarizing in your niche)",
                "Run cross-promotions with 2–3 similar-size creators",
                "Introduce a recurring series to build habit viewing",
                "Start converting followers: newsletter, community, or product",
            ],
            "weekly_follower_target": weekly_target * 2,
        },
    ]

    return {
        "account_id": account_id,
        "handle": acc["handle"],
        "platform": platform,
        "niche": niche,
        "current_followers": current,
        "goal_followers": goal_followers,
        "timeframe_weeks": timeframe_weeks,
        "weekly_follower_target": weekly_target,
        "phases": phases,
        "key_metrics_to_track": [
            "Follower growth rate (weekly %)",
            "Average views per video",
            "Engagement rate (likes+comments / views)",
            "Profile visit → follow conversion rate",
            "Best-performing hashtags (weekly review)",
        ],
    }


def get_checklist(platform: str) -> List[Dict[str, Any]]:
    """Return the full optimization checklist for a platform."""
    plat = platform.lower()
    if plat not in _PLATFORM_CHECKLIST:
        raise ValueError(f"Unknown platform '{platform}'. Choose: tiktok, youtube, instagram, twitter")
    return _PLATFORM_CHECKLIST[plat]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _find_account(accounts: List[Dict[str, Any]], account_id: str) -> Dict[str, Any]:
    for acc in accounts:
        if acc["id"] == account_id:
            return acc
    available = [a["id"] for a in accounts]
    raise ValueError(f"Account '{account_id}' not found. Available: {available}")
