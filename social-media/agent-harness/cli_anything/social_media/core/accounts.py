"""Account management and optimization for social media platforms."""

from datetime import datetime
from typing import Optional


_PLATFORM_CONFIGS = {
    "tiktok": {
        "max_bio_chars": 80,
        "link_in_bio": True,
        "optimal_post_freq": "1-3x daily",
        "best_times": ["6-9 AM", "12-2 PM", "7-10 PM"],
        "content_length_optimal": "15-60 seconds",
        "algorithm_signals": ["watch time", "completion rate", "saves", "shares", "comments"],
    },
    "instagram": {
        "max_bio_chars": 150,
        "link_in_bio": True,
        "optimal_post_freq": "1x daily feed + 5-7 stories",
        "best_times": ["6-8 AM", "11 AM-1 PM", "7-9 PM"],
        "content_length_optimal": "Reels: 7-15 seconds for max reach",
        "algorithm_signals": ["saves", "shares", "comments", "reach", "story replies"],
    },
    "youtube": {
        "max_bio_chars": 1000,
        "link_in_bio": True,
        "optimal_post_freq": "2-3x weekly (long form) + daily Shorts",
        "best_times": ["2-4 PM", "8-11 PM"],
        "content_length_optimal": "Shorts: 15-60s | Long form: 8-20 min",
        "algorithm_signals": ["CTR", "watch time", "satisfaction", "subscriptions driven"],
    },
    "twitter": {
        "max_bio_chars": 160,
        "link_in_bio": True,
        "optimal_post_freq": "3-7x daily",
        "best_times": ["8-10 AM", "12-1 PM", "5-6 PM"],
        "content_length_optimal": "280 chars for max engagement",
        "algorithm_signals": ["likes", "retweets", "replies", "profile visits"],
    },
}

_NICHE_CONTENT_RATIOS = {
    "finance": {"educational": 60, "personal_story": 20, "promotional": 10, "entertainment": 10},
    "fitness": {"educational": 40, "personal_story": 30, "promotional": 15, "entertainment": 15},
    "lifestyle": {"personal_story": 50, "educational": 20, "entertainment": 20, "promotional": 10},
    "fashion": {"showcasing": 50, "educational": 20, "personal_story": 20, "promotional": 10},
    "food": {"tutorial": 50, "review": 20, "personal_story": 20, "promotional": 10},
    "beauty": {"tutorial": 45, "review": 25, "personal_story": 20, "promotional": 10},
    "motivation": {"educational": 40, "personal_story": 35, "entertainment": 15, "promotional": 10},
    "travel": {"vlog": 40, "educational": 30, "personal_story": 20, "promotional": 10},
    "general": {"educational": 40, "entertainment": 30, "personal_story": 20, "promotional": 10},
}


def add_account(project: dict, username: str, platform: str, niche: str,
                followers: int = 0, bio: str = "") -> dict:
    """Add a social media account to the project."""
    account = {
        "id": f"{platform}_{username}",
        "username": username,
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "bio": bio,
        "added_at": datetime.utcnow().isoformat() + "Z",
        "optimization_score": 0,
        "posting_schedule": {},
        "notes": [],
    }
    project.setdefault("accounts", []).append(account)
    return account


def remove_account(project: dict, account_id: str) -> dict:
    accounts = project.get("accounts", [])
    for i, acc in enumerate(accounts):
        if acc["id"] == account_id or acc["username"] == account_id:
            removed = accounts.pop(i)
            return removed
    raise ValueError(f"Account not found: {account_id}")


def list_accounts(project: dict) -> list[dict]:
    return project.get("accounts", [])


def get_account(project: dict, account_id: str) -> dict:
    for acc in project.get("accounts", []):
        if acc["id"] == account_id or acc["username"] == account_id:
            return acc
    raise ValueError(f"Account not found: {account_id}")


def optimize_account(project: dict, account_id: str) -> dict:
    """Generate a full optimization report for an account."""
    acc = get_account(project, account_id)
    platform = acc.get("platform", "tiktok")
    niche = acc.get("niche", "general")
    followers = acc.get("followers", 0)
    bio = acc.get("bio", "")
    cfg = _PLATFORM_CONFIGS.get(platform, _PLATFORM_CONFIGS["tiktok"])

    issues = []
    wins = []
    score = 0

    # Bio optimization
    bio_score, bio_issues, bio_wins = _audit_bio(bio, platform, cfg)
    score += bio_score
    issues.extend(bio_issues)
    wins.extend(bio_wins)

    # Growth stage
    growth_stage = _classify_growth_stage(followers)

    # Content ratio
    content_ratio = _NICHE_CONTENT_RATIOS.get(niche, _NICHE_CONTENT_RATIOS["general"])

    # Posting schedule
    posting_plan = _generate_posting_plan(platform, niche, growth_stage, cfg)

    # Hook templates
    hook_templates = _hook_templates(niche)

    # Monetization roadmap
    monetization = _monetization_roadmap(followers, niche)

    acc["optimization_score"] = min(100, score)
    acc["last_optimized"] = datetime.utcnow().isoformat() + "Z"

    return {
        "account": acc["username"],
        "platform": platform,
        "niche": niche,
        "followers": followers,
        "growth_stage": growth_stage,
        "optimization_score": min(100, score),
        "issues": issues,
        "wins": wins,
        "content_ratio": content_ratio,
        "posting_plan": posting_plan,
        "hook_templates": hook_templates,
        "monetization_roadmap": monetization,
        "profile_checklist": _profile_checklist(acc, platform, cfg),
        "algorithm_tips": cfg["algorithm_signals"],
    }


def score_account(project: dict, account_id: str) -> dict:
    """Quick score of account health without full optimization."""
    acc = get_account(project, account_id)
    bio = acc.get("bio", "")
    platform = acc.get("platform", "tiktok")
    cfg = _PLATFORM_CONFIGS.get(platform, _PLATFORM_CONFIGS["tiktok"])
    bio_score, issues, _ = _audit_bio(bio, platform, cfg)
    has_schedule = bool(acc.get("posting_schedule"))
    has_niche = bool(acc.get("niche"))

    total = bio_score
    if has_schedule:
        total += 20
    if has_niche:
        total += 15

    return {
        "account": acc["username"],
        "platform": platform,
        "score": min(100, total),
        "rating": _score_rating(min(100, total)),
        "top_issues": issues[:3],
        "quick_wins": _quick_wins(acc, platform),
    }


def set_posting_schedule(project: dict, account_id: str, schedule: dict) -> dict:
    """Set posting schedule for an account."""
    acc = get_account(project, account_id)
    acc["posting_schedule"] = schedule
    return {"account": acc["username"], "schedule": schedule}


def update_account(project: dict, account_id: str, **kwargs) -> dict:
    """Update account fields."""
    acc = get_account(project, account_id)
    allowed = {"username", "niche", "followers", "bio", "platform"}
    for k, v in kwargs.items():
        if k in allowed:
            acc[k] = v
    return acc


def _audit_bio(bio: str, platform: str, cfg: dict) -> tuple[int, list[str], list[str]]:
    score = 30
    issues = []
    wins = []
    max_chars = cfg["max_bio_chars"]

    if not bio:
        issues.append("No bio — add a clear value proposition. What do you give followers?")
    elif len(bio) < 20:
        issues.append("Bio too short — expand to clearly state your niche and value.")
        score += 5
    elif len(bio) > max_chars:
        issues.append(f"Bio too long ({len(bio)} chars). Platform max: {max_chars}.")
        score += 10
    else:
        score += 20
        wins.append("Bio length is good.")

    if bio and any(w in bio.lower() for w in ["follow", "subscribe", "link", "↓", "⬇", "👇"]):
        score += 10
        wins.append("Bio has a clear call-to-action.")
    elif bio:
        issues.append("Add a CTA to your bio: 'Link below ↓' or 'New video every [day]'")

    if bio and any(e in bio for e in ["🔥", "✨", "💡", "🎯", "📱", "💰", "🌍", "💪", "🎬", "📈"]):
        score += 5
        wins.append("Emojis make bio scannable.")
    elif bio:
        issues.append("Add 1-2 relevant emojis to make your bio more scannable.")

    return score, issues, wins


def _classify_growth_stage(followers: int) -> dict:
    if followers < 1000:
        return {"stage": "nano", "label": "Nano (0–1K)", "priority": "Content quality + posting consistency"}
    elif followers < 10000:
        return {"stage": "micro", "label": "Micro (1K–10K)", "priority": "Niche down + engage comments aggressively"}
    elif followers < 100000:
        return {"stage": "mid", "label": "Mid-tier (10K–100K)", "priority": "Collaborations + brand deals + email list"}
    elif followers < 1000000:
        return {"stage": "macro", "label": "Macro (100K–1M)", "priority": "Diversify platforms + productize"}
    else:
        return {"stage": "mega", "label": "Mega (1M+)", "priority": "Brand, book deals, investing in other creators"}


def _generate_posting_plan(platform: str, niche: str, growth_stage: dict, cfg: dict) -> dict:
    return {
        "frequency": cfg["optimal_post_freq"],
        "best_times": cfg["best_times"],
        "content_types": _content_types_for_niche(niche, platform),
        "weekly_structure": _weekly_structure(niche, platform),
        "stage_specific": growth_stage["priority"],
    }


def _content_types_for_niche(niche: str, platform: str) -> list[str]:
    mapping = {
        "finance": ["Educational tips", "Personal income breakdowns", "Investment walkthroughs", "Money mindset"],
        "fitness": ["Workout demos", "Transformation check-ins", "Meal prep", "Exercise tutorials"],
        "lifestyle": ["Day in my life", "Morning/evening routines", "Room tours", "Habits"],
        "fashion": ["Outfit of the day", "Style tips", "Hauls", "Outfit challenges"],
        "food": ["Recipes", "Restaurant reviews", "Mukbang", "Cooking hacks"],
        "beauty": ["GRWM", "Skincare routines", "Product reviews", "Tutorials"],
        "motivation": ["Mindset tips", "Success stories", "Challenges", "Daily affirmations"],
        "travel": ["Destination guides", "Travel hacks", "Day vlogs", "Budget breakdowns"],
    }
    return mapping.get(niche, ["Educational", "Entertainment", "Personal story", "Behind the scenes"])


def _weekly_structure(niche: str, platform: str) -> dict:
    return {
        "Monday": "Educational/Tutorial content (highest save rate)",
        "Tuesday": "Personal story / Behind the scenes",
        "Wednesday": "Trending sound + hook format",
        "Thursday": "Niche deep-dive or Q&A",
        "Friday": "Entertainment / Relatable content",
        "Saturday": "Engagement post (polls, this or that)",
        "Sunday": "Best-of repost or motivational content",
    }


def _hook_templates(niche: str) -> list[str]:
    universal = [
        "Stop scrolling if you want to {goal}…",
        "I spent {time} testing this so you don't have to",
        "The {niche} thing nobody tells you about…",
        "POV: you just discovered {solution}",
        "Why 99% of {niche} content is lying to you",
    ]
    niche_hooks = {
        "finance": [
            "I made ${amount} doing this ONE thing…",
            "Your bank account in 6 months if you do this",
            "Why your money is shrinking even when you save",
        ],
        "fitness": [
            "The workout that changed my body in 30 days",
            "Why you're not losing weight (it's not what you think)",
            "I trained like [celebrity] for a week — here's the truth",
        ],
        "lifestyle": [
            "My morning routine that made me 10× more productive",
            "I deleted this app and my anxiety disappeared",
            "The habit that changed everything for me",
        ],
        "fashion": [
            "This outfit formula works for every body type",
            "I styled {piece} 5 different ways",
            "Why you only need {number} pieces in your wardrobe",
        ],
    }
    return universal + niche_hooks.get(niche, [])


def _monetization_roadmap(followers: int, niche: str) -> list[dict]:
    roadmap = []
    if followers < 1000:
        roadmap.append({"milestone": "0–1K", "strategy": "Build content library. No monetization yet — focus on growth.", "timeline": "0-3 months"})
    if followers < 10000:
        roadmap.append({"milestone": "1K–10K", "strategy": "UGC (User Generated Content) brand deals — no follower minimum. Start affiliate links.", "timeline": "1-6 months"})
    if followers < 100000:
        roadmap.append({"milestone": "10K–100K", "strategy": "Paid sponsorships ($100–$1,000/post). Sell digital products. TikTok Creator Fund.", "timeline": "3-12 months"})
    if followers >= 10000:
        roadmap.append({"milestone": "100K+", "strategy": "Premium sponsorships ($1K–$10K+). Courses, coaching. Own brand launch.", "timeline": "6-24 months"})
    roadmap.append({
        "milestone": "Platform-agnostic",
        "strategy": "Build email list NOW regardless of follower count — it's your owned audience.",
        "timeline": "Start today",
    })
    return roadmap


def _profile_checklist(acc: dict, platform: str, cfg: dict) -> list[dict]:
    bio = acc.get("bio", "")
    return [
        {"item": "Profile photo (clear, branded, recognizable)", "status": "unknown — verify manually"},
        {"item": f"Bio under {cfg['max_bio_chars']} chars with CTA", "status": "ok" if bio and len(bio) <= cfg["max_bio_chars"] else "needs_work"},
        {"item": "Username is niche-relevant and memorable", "status": "unknown — verify manually"},
        {"item": "Link in bio set up (Linktree, Beacons, or direct)", "status": "unknown — verify manually"},
        {"item": "Pinned posts showcase best content", "status": "unknown — verify manually"},
        {"item": "Content is posting-ready (drafts queued)", "status": "unknown — verify manually"},
        {"item": "Analytics/Creator mode enabled", "status": "unknown — verify manually"},
    ]


def _quick_wins(acc: dict, platform: str) -> list[str]:
    wins = []
    if not acc.get("bio"):
        wins.append("Add a bio immediately — this is the #1 conversion point")
    if not acc.get("posting_schedule"):
        wins.append("Set a posting schedule — consistency beats virality")
    wins.append(f"Enable Creator/Business account on {platform} for analytics")
    wins.append("Pin your 3 best-performing posts to profile")
    return wins


def _score_rating(score: int) -> str:
    if score >= 80:
        return "Excellent"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Needs Work"
    return "Critical — major improvements needed"
