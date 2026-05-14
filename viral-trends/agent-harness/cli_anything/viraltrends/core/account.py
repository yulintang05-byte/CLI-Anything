"""Account optimization: posting schedule, bio, hashtag strategy, profile audit."""

from __future__ import annotations
import json
from datetime import datetime


# Best posting windows based on aggregated engagement studies (UTC offsets by region)
_BEST_TIMES: dict[str, dict[str, list[str]]] = {
    "tiktok": {
        "Mon": ["06:00", "10:00", "22:00"],
        "Tue": ["02:00", "04:00", "09:00"],
        "Wed": ["07:00", "08:00", "23:00"],
        "Thu": ["09:00", "12:00", "19:00"],
        "Fri": ["05:00", "13:00", "15:00"],
        "Sat": ["11:00", "19:00", "20:00"],
        "Sun": ["07:00", "08:00", "16:00"],
    },
    "youtube": {
        "Mon": ["14:00", "16:00"],
        "Tue": ["14:00", "16:00"],
        "Wed": ["14:00", "16:00"],
        "Thu": ["14:00", "16:00"],
        "Fri": ["14:00", "16:00"],
        "Sat": ["09:00", "11:00"],
        "Sun": ["09:00", "11:00"],
    },
    "instagram": {
        "Mon": ["11:00", "14:00"],
        "Tue": ["11:00", "14:00"],
        "Wed": ["11:00", "14:00"],
        "Thu": ["11:00", "14:00"],
        "Fri": ["10:00", "14:00"],
        "Sat": ["10:00"],
        "Sun": ["10:00"],
    },
}

_HASHTAG_STRATEGY = {
    "tiktok": {
        "optimal_count": "3-5",
        "mix": "1 mega (>1B views) + 2 large (100M-1B) + 2 niche (<10M)",
        "always_include": ["#fyp", "#foryou", "#foryoupage"],
        "tip": "Put hashtags in the caption, not the comments — TikTok's algorithm reads captions.",
    },
    "youtube": {
        "optimal_count": "3-5 (in description, max 15 before penalty)",
        "mix": "1-2 broad + 1-2 mid-tail + 1-2 niche",
        "always_include": [],
        "tip": "First 3 hashtags appear above the title. Make them count.",
    },
    "instagram": {
        "optimal_count": "5-15 (up to 30 allowed)",
        "mix": "3 large + 5 medium + 5 niche + 2 brand-specific",
        "always_include": [],
        "tip": "Use niche hashtags for discovery; mega hashtags bury small accounts.",
    },
}

_BIO_TEMPLATE = {
    "tiktok": (
        "🎯 {niche} content\n"
        "📲 Follow for {value_prop}\n"
        "🔗 Link in bio → {cta}\n"
        "⬇️ DM for {offer}"
    ),
    "youtube": (
        "{channel_name} — {niche} videos every {schedule}.\n"
        "Subscribe for {value_prop}.\n"
        "{cta}"
    ),
    "instagram": (
        "✨ {niche}\n"
        "📍 {location_or_niche_tag}\n"
        "👇 {cta}\n"
        "🔗 linkin.bio/{handle}"
    ),
}


def posting_schedule(platform: str, timezone_offset: int = 0) -> dict:
    """Return optimal posting schedule for a platform, adjusted for UTC offset."""
    platform = platform.lower()
    raw = _BEST_TIMES.get(platform, _BEST_TIMES["tiktok"])
    adjusted = {}
    for day, times in raw.items():
        adj_times = []
        for t in times:
            h, m = map(int, t.split(":"))
            h = (h + timezone_offset) % 24
            adj_times.append(f"{h:02d}:{m:02d}")
        adjusted[day] = adj_times

    return {
        "platform": platform,
        "timezone_offset_hours": timezone_offset,
        "schedule": adjusted,
        "note": "Times are UTC-adjusted. Test for 2 weeks and refine with your analytics.",
    }


def hashtag_strategy(platform: str, niche: str = "", trending_tags: list[str] | None = None) -> dict:
    """Build a hashtag strategy for a given platform and niche."""
    platform = platform.lower()
    strategy = _HASHTAG_STRATEGY.get(platform, _HASHTAG_STRATEGY["tiktok"]).copy()
    suggested = list(strategy.get("always_include", []))
    if trending_tags:
        suggested.extend(trending_tags[:5])
    if niche:
        slug = niche.lower().replace(" ", "")
        suggested += [f"#{slug}", f"#{slug}tok" if platform == "tiktok" else f"#{slug}tube"]

    strategy["suggested_tags"] = list(dict.fromkeys(suggested))[:15]
    strategy["niche"] = niche
    return strategy


def bio_template(platform: str, niche: str, value_prop: str, cta: str) -> dict:
    """Generate a fill-in-the-blank bio template."""
    template = _BIO_TEMPLATE.get(platform.lower(), _BIO_TEMPLATE["tiktok"])
    filled = template.format(
        niche=niche,
        value_prop=value_prop,
        cta=cta,
        offer="collab/promo",
        schedule="week",
        channel_name=niche,
        location_or_niche_tag=f"#{niche.lower().replace(' ','')}",
        handle=niche.lower().replace(" ", ""),
    )
    return {
        "platform": platform,
        "bio": filled,
        "char_count": len(filled),
        "limit": {"tiktok": 80, "youtube": 1000, "instagram": 150}.get(platform.lower(), 200),
    }


def profile_audit_checklist(platform: str) -> list[dict]:
    """Return a platform-specific profile optimization checklist."""
    common = [
        {"item": "Profile photo", "tip": "High-contrast face or logo, no text, 400x400px min"},
        {"item": "Username", "tip": "Memorable, brandable, consistent across platforms"},
        {"item": "Bio / About", "tip": "Clear niche + value proposition + CTA in first 2 lines"},
        {"item": "Link in bio", "tip": "Use Linktree/Stan.store to capture leads"},
        {"item": "Pinned content", "tip": "Pin your best-performing or most representative video/post"},
        {"item": "Content consistency", "tip": "Same aesthetic/thumbnail style for brand recognition"},
    ]
    platform_specific = {
        "tiktok": [
            {"item": "TikTok LIVE eligibility", "tip": "Reach 1K followers → go LIVE to boost reach"},
            {"item": "Creator marketplace", "tip": "Enable at 10K followers for brand deals"},
            {"item": "Series feature", "tip": "Group related videos → boosts watch time"},
        ],
        "youtube": [
            {"item": "Channel banner", "tip": "2560x1440px, shows on TV — include posting schedule"},
            {"item": "Channel trailer", "tip": "60-90s hook for new visitors — show what you post"},
            {"item": "Playlists", "tip": "Group videos → increases session watch time significantly"},
            {"item": "End screens + cards", "tip": "Link related videos in final 20 seconds"},
            {"item": "Chapters in descriptions", "tip": "Timestamps improve retention and SEO"},
        ],
        "instagram": [
            {"item": "Story highlights", "tip": "Organize: About, FAQ, Products, Reviews"},
            {"item": "Reels cover art", "tip": "Consistent cover template for grid aesthetics"},
            {"item": "Shop tab", "tip": "Enable shopping if selling products"},
        ],
    }
    return common + platform_specific.get(platform.lower(), [])


def content_calendar(
    platform: str,
    niche: str,
    posts_per_week: int = 5,
    trending_tags: list[str] | None = None,
) -> list[dict]:
    """Generate a 7-day content calendar with post ideas."""
    tag_str = " ".join((trending_tags or [])[:3])
    templates = {
        "tiktok": [
            f"Day {{d}}: Hook video — '{niche} secret nobody tells you' {tag_str}",
            f"Day {{d}}: POV trend — apply trending audio to your {niche} niche",
            f"Day {{d}}: Tutorial — step-by-step {niche} tip in under 60s",
            f"Day {{d}}: React/duet — engage with a viral {niche} video",
            f"Day {{d}}: Behind the scenes — your {niche} process/workflow",
            f"Day {{d}}: Story time — personal experience in {niche}",
            f"Day {{d}}: Q&A — answer comments from last week",
        ],
        "youtube": [
            f"Day {{d}}: Long-form deep dive — '{niche}: Complete Guide' (10-20 min)",
            f"Day {{d}}: YouTube Short — repurpose top TikTok clip",
            f"Day {{d}}: Listicle — 'Top 10 {niche} tips for beginners'",
            f"Day {{d}}: Collab or reaction video with another {niche} creator",
            f"Day {{d}}: Case study / results video — proof-of-concept in {niche}",
            f"Day {{d}}: Q&A / community post — engage subscribers",
            f"Day {{d}}: Trending topic tie-in — connect {niche} to current events",
        ],
        "instagram": [
            f"Day {{d}}: Carousel — '5 {niche} tips' (saves = algorithm boost)",
            f"Day {{d}}: Reel — trending audio + {niche} content",
            f"Day {{d}}: Story poll — engage audience around {niche} topic",
            f"Day {{d}}: Infographic post — shareable {niche} stats",
            f"Day {{d}}: UGC repost — share customer/fan {niche} content",
            f"Day {{d}}: Behind the scenes Story → Highlight",
            f"Day {{d}}: Collab post with {niche} influencer",
        ],
    }
    ideas = templates.get(platform.lower(), templates["tiktok"])
    calendar = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    times = _BEST_TIMES.get(platform.lower(), _BEST_TIMES["tiktok"])
    post_days = days[:posts_per_week]
    for i, day in enumerate(post_days):
        idea = ideas[i % len(ideas)].format(d=day)
        calendar.append({
            "day": day,
            "post_time": times.get(day, ["12:00"])[0],
            "content_idea": idea,
            "hashtag_strategy": f"Use mix: 1 trending + 2 niche + {platform}-specific",
        })
    return calendar
