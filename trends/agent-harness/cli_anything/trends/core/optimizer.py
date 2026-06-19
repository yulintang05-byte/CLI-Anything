"""Account optimizer — generates platform-specific optimization packs from trend data."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


# ── Optimal posting times (research-backed) ─────────────────────────────────

POSTING_TIMES = {
    "tiktok": {
        "Mon": ["6:00 AM", "10:00 AM", "10:00 PM"],
        "Tue": ["2:00 AM", "4:00 AM", "9:00 AM"],
        "Wed": ["7:00 AM", "8:00 AM", "11:00 PM"],
        "Thu": ["9:00 AM", "12:00 PM", "7:00 PM"],
        "Fri": ["5:00 AM", "1:00 PM", "3:00 PM"],
        "Sat": ["11:00 AM", "7:00 PM", "8:00 PM"],
        "Sun": ["7:00 AM", "8:00 AM", "4:00 PM"],
        "note": "Post 3x/day. Hook viewers in first 2 seconds. 7-15 sec for trending sounds.",
    },
    "youtube_shorts": {
        "Mon": ["3:00 PM", "5:00 PM"],
        "Tue": ["3:00 PM", "5:00 PM"],
        "Wed": ["3:00 PM", "5:00 PM"],
        "Thu": ["3:00 PM", "5:00 PM"],
        "Fri": ["3:00 PM", "6:00 PM"],
        "Sat": ["10:00 AM", "2:00 PM"],
        "Sun": ["10:00 AM", "2:00 PM"],
        "note": "Post daily. Shorts feed peaks weekday afternoons EST.",
    },
    "youtube_long": {
        "Mon": ["2:00 PM", "4:00 PM"],
        "Tue": ["2:00 PM", "4:00 PM"],
        "Wed": ["2:00 PM", "4:00 PM"],
        "Thu": ["2:00 PM", "5:00 PM"],
        "Fri": ["2:00 PM", "5:00 PM"],
        "Sat": ["9:00 AM", "11:00 AM"],
        "Sun": ["9:00 AM", "11:00 AM"],
        "note": "Post 2-3x/week. Minimum 8 minutes for full ad revenue.",
    },
    "instagram": {
        "Mon": ["6:00 AM", "10:00 AM", "3:00 PM"],
        "Tue": ["6:00 AM", "10:00 AM", "3:00 PM"],
        "Wed": ["6:00 AM", "11:00 AM", "3:00 PM"],
        "Thu": ["6:00 AM", "12:00 PM", "3:00 PM"],
        "Fri": ["6:00 AM", "11:00 AM", "3:00 PM"],
        "Sat": ["9:00 AM", "2:00 PM"],
        "Sun": ["9:00 AM", "2:00 PM"],
        "note": "Reels > feed posts for reach. Use all 30 hashtags. Story polls boost engagement.",
    },
}

# Hashtag count recommendations
HASHTAG_COUNTS = {
    "tiktok": {"optimal": 5, "max": 8, "note": "3-5 niche + 1-2 trending + 1 broad"},
    "youtube": {"optimal": 3, "max": 15, "note": "First 3 in description are shown as tags"},
    "instagram": {"optimal": 25, "max": 30, "note": "Mix of small (<50K), mid (50K-500K), large (>500K)"},
}


def generate_hashtag_pack(
    trend_report: dict,
    niche: str = "general",
    platform: str = "all",
    pack_size: int = 30,
) -> dict:
    """Generate optimized hashtag packs from trend data for a given niche."""
    all_tags = trend_report.get("top_hashtags", [])
    cross_tags = trend_report.get("cross_platform_hashtags", [])

    # Prioritize cross-platform tags
    cross_set = {t["hashtag"] for t in cross_tags}
    sorted_tags = sorted(all_tags, key=lambda x: (
        x["hashtag"] in cross_set,
        x.get("combined_score", x.get("score", 0))
    ), reverse=True)

    top_tags = [t["hashtag"] for t in sorted_tags[:pack_size]]

    packs = {}

    if platform in ("all", "tiktok"):
        cfg = HASHTAG_COUNTS["tiktok"]
        packs["tiktok"] = {
            "hashtags": top_tags[:cfg["max"]],
            "note": cfg["note"],
            "copy_paste": " ".join(top_tags[:5]),
        }

    if platform in ("all", "youtube"):
        cfg = HASHTAG_COUNTS["youtube"]
        packs["youtube"] = {
            "hashtags": top_tags[:cfg["max"]],
            "note": cfg["note"],
            "copy_paste": " ".join(top_tags[:3]),
        }

    if platform in ("all", "instagram"):
        cfg = HASHTAG_COUNTS["instagram"]
        packs["instagram"] = {
            "hashtags": top_tags[:cfg["max"]],
            "note": cfg["note"],
            "copy_paste": " ".join(top_tags[:30]),
        }

    return {
        "niche": niche,
        "generated_at": datetime.utcnow().isoformat(),
        "cross_platform_tags": list(cross_set)[:10],
        "packs": packs,
    }


def generate_content_calendar(
    trend_report: dict,
    niche: str = "general",
    platforms: list[str] = None,
    weeks: int = 2,
) -> dict:
    """Generate a content calendar based on trending topics and optimal posting times."""
    if platforms is None:
        platforms = ["tiktok", "youtube_shorts", "instagram"]

    topics = trend_report.get("trending_topics", [])[:10]
    themes = trend_report.get("content_themes", [])[:5]
    hashtags = trend_report.get("top_hashtags", [])[:20]
    sounds = trend_report.get("tiktok_sounds", [])[:5]
    music = trend_report.get("music_trends", [])[:5]

    # Generate content ideas from topics and themes
    content_ideas = _generate_content_ideas(topics, themes, niche)

    calendar = []
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    idea_idx = 0

    for week in range(1, weeks + 1):
        for day_num, day in enumerate(days_of_week):
            day_posts = []
            for platform in platforms:
                times = POSTING_TIMES.get(platform, {}).get(day, [])
                for post_time in times[:2]:  # max 2 posts per platform per day
                    idea = content_ideas[idea_idx % len(content_ideas)]
                    tag_pack = [h["hashtag"] for h in hashtags[:5]]
                    sound = sounds[idea_idx % len(sounds)]["title"] if sounds else None
                    artist = music[idea_idx % len(music)]["artist"] if music else None

                    day_posts.append({
                        "platform": platform,
                        "time": post_time,
                        "content_idea": idea["title"],
                        "content_type": idea["type"],
                        "hashtags": tag_pack,
                        "trending_sound": sound,
                        "trending_music": artist,
                        "hook": idea["hook"],
                        "cta": idea["cta"],
                    })
                    idea_idx += 1

            if day_posts:
                calendar.append({
                    "week": week,
                    "day": day,
                    "posts": day_posts,
                })

    return {
        "niche": niche,
        "platforms": platforms,
        "weeks": weeks,
        "total_posts": sum(len(d["posts"]) for d in calendar),
        "calendar": calendar,
        "notes": [
            "All times are in your local timezone — adjust for audience location.",
            "Reuse top-performing content across platforms within 24-48h.",
            "Replace trending sounds weekly as new ones emerge.",
            "A/B test hooks — change first 2 seconds, keep rest same.",
        ],
    }


def generate_account_optimization(
    trend_report: dict,
    platform: str,
    niche: str = "general",
    current_followers: int = 0,
) -> dict:
    """Generate a full account optimization guide for a platform."""
    topics = [t["topic"] for t in trend_report.get("trending_topics", [])[:5]]
    themes = [t["theme"] for t in trend_report.get("content_themes", [])[:3]]
    hashtags = [h["hashtag"] for h in trend_report.get("top_hashtags", [])[:10]]
    sounds = [s["title"] for s in trend_report.get("tiktok_sounds", [])[:3]]

    bio_keywords = topics[:3] + [niche] if topics else [niche]
    bio_keywords = list(dict.fromkeys(bio_keywords))[:4]

    growth_phase = _determine_growth_phase(current_followers)

    optimizations = {
        "platform": platform,
        "niche": niche,
        "growth_phase": growth_phase,
        "profile": {
            "username": f"Use niche keyword + personal brand (e.g., @{niche.replace(' ', '_')}hacks)",
            "bio": _generate_bio_template(niche, bio_keywords, platform),
            "profile_photo": "High-contrast face or niche logo. No text overlays.",
            "link_in_bio": "Use Linktree/Beacons — point to lead magnet or product.",
        },
        "content_strategy": {
            "posting_frequency": POSTING_TIMES.get(platform, {}).get("note", "Post consistently."),
            "content_mix": _content_mix_for_phase(growth_phase),
            "trending_topics_to_use": topics[:5],
            "trending_themes": themes,
            "hook_formulas": _hook_formulas(niche),
            "cta_examples": _cta_examples(platform),
        },
        "hashtag_strategy": {
            "recommended_tags": hashtags,
            "strategy": HASHTAG_COUNTS.get(platform, {}).get("note", ""),
            "trending_sounds_to_use": sounds if platform == "tiktok" else [],
        },
        "growth_tactics": _growth_tactics(platform, growth_phase, niche),
        "monetization_readiness": _monetization_checklist(platform, current_followers),
    }

    return optimizations


def _determine_growth_phase(followers: int) -> str:
    if followers < 1_000:
        return "seed"
    elif followers < 10_000:
        return "growth"
    elif followers < 100_000:
        return "scaling"
    else:
        return "established"


def _generate_bio_template(niche: str, keywords: list[str], platform: str) -> str:
    kw_str = " | ".join(keywords[:3]) if keywords else niche
    if platform == "tiktok":
        return f"🔥 {niche.title()} content daily\n{kw_str}\n👇 Free [lead magnet] below"
    elif platform in ("youtube", "youtube_shorts"):
        return f"{niche.title()} | {kw_str} | New videos every week\n👇 Subscribe for free [value]"
    else:
        return f"{niche.title()} | {kw_str}\n📩 DM for collabs\n👇 [Free resource] link below"


def _content_mix_for_phase(phase: str) -> dict:
    mixes = {
        "seed": {"trending_remakes": 50, "educational": 30, "personal": 20,
                 "note": "Hook with trending formats. Build first 1K fast."},
        "growth": {"trending_remakes": 30, "educational": 40, "personal": 20, "promo": 10,
                   "note": "Build authority. Mix trending with original takes."},
        "scaling": {"original": 40, "educational": 30, "trending": 20, "promo": 10,
                    "note": "Own your voice. Collab with peers."},
        "established": {"original": 50, "educational": 25, "promo": 15, "community": 10,
                        "note": "Focus on retention and monetization."},
    }
    return mixes.get(phase, mixes["seed"])


def _hook_formulas(niche: str) -> list[str]:
    return [
        f"POV: You discovered the {niche} secret nobody talks about",
        f"Stop doing THIS if you're into {niche} (I wish someone told me)",
        f"The {niche} trick that blew up my account in 7 days",
        f"Wait until you see what happens when you [do niche thing]...",
        f"I tested every {niche} method so you don't have to — here's what works",
        f"Day 1 vs Day 30 of [niche challenge] — the results shocked me",
        f"Unpopular opinion: {niche} advice you've been told is WRONG",
    ]


def _cta_examples(platform: str) -> list[str]:
    if platform == "tiktok":
        return [
            "Follow for part 2",
            "Comment 'YES' if this helped",
            "Duet this with your results",
            "Save this for later",
            "Tag someone who needs this",
        ]
    elif platform in ("youtube", "youtube_shorts"):
        return [
            "Subscribe and hit the bell",
            "Comment your biggest question below",
            "Like if this helped you",
            "Watch my next video [linked]",
            "Join the free community in the description",
        ]
    else:
        return [
            "Save this post",
            "Share to your story",
            "DM me 'FREE' for the guide",
            "Tag a friend who needs this",
            "Follow for daily tips",
        ]


def _growth_tactics(platform: str, phase: str, niche: str) -> list[str]:
    base = [
        "Reply to every comment in the first hour of posting (boosts algorithm).",
        "Engage with top creators in your niche — be genuinely helpful in comments.",
        "Post at the exact same times each day to train the algorithm.",
        "Study your top-performing post's first 3 seconds and replicate the hook.",
        "Cross-post to all platforms within 24 hours of original publish.",
    ]
    platform_tactics = {
        "tiktok": [
            "Use trending sounds — even a 1-second clip counts for algorithm boost.",
            "Stitch or duet viral content in your niche for borrowed reach.",
            "Go live 2-3x/week once you hit 1K followers for FYP boost.",
            "Delete posts under 20% average watch time — they hurt your score.",
        ],
        "youtube": [
            "Click-through rate matters more than views — A/B test thumbnails.",
            "Add chapters to all videos over 5 minutes for watch time retention.",
            "End screen + cards pointing to related content reduces bounce rate.",
            "Shorts funnel viewers to long-form — use Shorts to build channel.",
        ],
        "instagram": [
            "Reels get 3-5x the reach of static posts — prioritize Reels.",
            "Collab posts with similar-sized accounts 2x your reach instantly.",
            "Story polls and questions boost you to top of feed for followers.",
            "Use keyword-rich captions — Instagram's search is SEO-driven now.",
        ],
    }
    return base + platform_tactics.get(platform, [])


def _monetization_checklist(platform: str, followers: int) -> dict:
    thresholds = {
        "tiktok": {
            "creator_fund": {"required": 10_000, "met": followers >= 10_000},
            "tiktok_shop": {"required": 1_000, "met": followers >= 1_000},
            "live_gifts": {"required": 1_000, "met": followers >= 1_000},
            "brand_deals": {"required": 5_000, "met": followers >= 5_000},
            "affiliate": {"required": 0, "met": True},
        },
        "youtube": {
            "adsense_shorts": {"required": 500, "met": followers >= 500},
            "adsense_long": {"required": 1_000, "met": followers >= 1_000},
            "channel_memberships": {"required": 500, "met": followers >= 500},
            "super_thanks": {"required": 500, "met": followers >= 500},
            "brand_deals": {"required": 10_000, "met": followers >= 10_000},
        },
        "instagram": {
            "gifts_reels": {"required": 0, "met": True},
            "subscriptions": {"required": 10_000, "met": followers >= 10_000},
            "brand_deals": {"required": 5_000, "met": followers >= 5_000},
            "badges_live": {"required": 0, "met": True},
            "affiliate_collab": {"required": 0, "met": True},
        },
    }
    plat = platform.split("_")[0]  # youtube_shorts → youtube
    return thresholds.get(plat, {})


def _generate_content_ideas(
    topics: list[dict],
    themes: list[dict],
    niche: str,
) -> list[dict]:
    """Generate concrete content ideas from topic and theme data."""
    ideas = []

    # Topic-based ideas
    for t in topics[:5]:
        word = t.get("topic", "topic")
        ideas += [
            {
                "title": f"Why {word} is blowing up right now — explained",
                "type": "educational",
                "hook": f"Everyone's talking about {word} but nobody explains WHY",
                "cta": "Follow for more breakdowns like this",
            },
            {
                "title": f"My take on the {word} trend — honest review",
                "type": "opinion",
                "hook": f"Hot take: the {word} trend is [good/bad] and here's why",
                "cta": "Comment your opinion below",
            },
        ]

    # Theme-based ideas
    for th in themes[:3]:
        theme = th.get("theme", "lifestyle")
        ideas += [
            {
                "title": f"{theme.title()} content that's actually going viral in {datetime.utcnow().year}",
                "type": "trend_commentary",
                "hook": f"POV: You want to make it in {theme} content",
                "cta": "Save this — you'll need it",
            },
            {
                "title": f"A day in my life as a {niche} creator — raw and unfiltered",
                "type": "vlog",
                "hook": f"Nobody shows the real side of {theme}...",
                "cta": "Follow if you want more of this",
            },
        ]

    # Fallback generic ideas
    if not ideas:
        ideas = [
            {
                "title": f"The {niche} mistake everyone makes (and how to fix it)",
                "type": "educational",
                "hook": "I wish someone told me this when I started",
                "cta": "Save for when you need it",
            },
            {
                "title": f"Reacting to the most viral {niche} content this week",
                "type": "reaction",
                "hook": "Wait till you see this...",
                "cta": "Follow for weekly roundups",
            },
        ]

    return ideas if ideas else [{"title": "Content idea", "type": "general", "hook": "", "cta": ""}]
