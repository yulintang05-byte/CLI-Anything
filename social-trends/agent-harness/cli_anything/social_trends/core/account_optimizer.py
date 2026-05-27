"""Account optimizer — platform-specific recommendations.

Generates concrete, actionable optimisation advice for TikTok, YouTube,
and Instagram accounts based on niche, current metrics, and best practices.
"""

from __future__ import annotations

import json
from pathlib import Path

from cli_anything.social_trends.utils.scraper_backend import load_config, save_config

# ── Account profile storage ───────────────────────────────────────────────────

PROFILES_FILE = Path.home() / ".cli-anything-social-trends" / "accounts.json"


def _load_profiles() -> dict:
    if not PROFILES_FILE.exists():
        return {}
    with open(PROFILES_FILE) as f:
        return json.load(f)


def _save_profiles(profiles: dict):
    PROFILES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles, f, indent=2)


def add_account(platform: str, username: str, niche: str,
                followers: int = 0, avg_views: int = 0) -> dict:
    """Register an account for tracking and optimisation."""
    profiles = _load_profiles()
    key = f"{platform}:{username}"
    profiles[key] = {
        "platform": platform.lower(),
        "username": username,
        "niche": niche.lower(),
        "followers": followers,
        "avg_views": avg_views,
    }
    _save_profiles(profiles)
    return {"added": key, "profile": profiles[key]}


def list_accounts() -> list[dict]:
    profiles = _load_profiles()
    return list(profiles.values())


def remove_account(platform: str, username: str) -> dict:
    profiles = _load_profiles()
    key = f"{platform}:{username}"
    if key not in profiles:
        raise KeyError(f"Account not found: {key}")
    del profiles[key]
    _save_profiles(profiles)
    return {"removed": key}


# ── Optimisation engine ───────────────────────────────────────────────────────

def optimise_account(platform: str, username: str | None = None,
                     niche: str = "", followers: int = 0,
                     avg_views: int = 0) -> dict:
    """Generate a full optimisation report for a given account."""
    if username:
        profiles = _load_profiles()
        key = f"{platform}:{username}"
        if key in profiles:
            p = profiles[key]
            niche = p.get("niche", niche)
            followers = p.get("followers", followers)
            avg_views = p.get("avg_views", avg_views)

    platform = platform.lower()
    if platform == "tiktok":
        return _optimise_tiktok(niche, followers, avg_views)
    if platform == "youtube":
        return _optimise_youtube(niche, followers, avg_views)
    if platform in ("instagram", "ig"):
        return _optimise_instagram(niche, followers, avg_views)
    raise ValueError(f"Unsupported platform: {platform}. Use tiktok/youtube/instagram.")


# ── Per-platform optimisers ───────────────────────────────────────────────────

def _optimise_tiktok(niche: str, followers: int, avg_views: int) -> dict:
    er = _engagement_rate(followers, avg_views)
    stage = _growth_stage(followers)

    return {
        "platform": "tiktok",
        "niche": niche or "general",
        "growth_stage": stage,
        "engagement_rate": f"{er:.1f}%",
        "engagement_benchmark": _tt_er_benchmark(er),
        "profile_checklist": [
            "Profile photo: clear, high-contrast face or logo (no text)",
            "Bio: one hook sentence + niche keyword + CTA (e.g. 'Link in bio')",
            "Username: short, searchable, matches niche (avoid numbers/underscores)",
            "Pinned videos: pin your 3 best-performing or most representative videos",
            "Link in bio: use a link-in-bio tool (Linktree, Beacons) with 3-5 links",
        ],
        "content_strategy": _tt_content_strategy(niche, stage),
        "posting_schedule": _tt_posting_schedule(stage),
        "hashtag_formula": _tt_hashtag_formula(niche),
        "growth_tactics": _tt_growth_tactics(stage, er),
        "monetisation_readiness": _tt_monetisation(followers),
        "quick_wins": _tt_quick_wins(er, followers),
    }


def _optimise_youtube(niche: str, followers: int, avg_views: int) -> dict:
    er = _engagement_rate(followers, avg_views)
    stage = _growth_stage(followers)

    return {
        "platform": "youtube",
        "niche": niche or "general",
        "growth_stage": stage,
        "avg_views": avg_views,
        "subscriber_benchmark": _yt_sub_benchmark(followers),
        "channel_checklist": [
            "Banner: 2560×1440px, shows value proposition + upload schedule",
            "Profile photo: 800×800px, face or brand logo",
            "Channel description: keyword-rich first 2 sentences (above the fold)",
            "About section: keywords, links, email for collabs",
            "Channel trailer: 60-90s for non-subscribers, hook in first 5s",
            "Playlists: group videos into 3-5 themed playlists",
            "End screens: add subscribe + next video to last 20s of every video",
            "Cards: add cards at engagement drop-off points",
        ],
        "content_strategy": _yt_content_strategy(niche, stage),
        "upload_schedule": _yt_upload_schedule(stage),
        "seo_checklist": [
            "Title: keyword first, 60 chars max, curiosity gap or number",
            "Description: keyword in first sentence, timestamp chapters, links",
            "Tags: 5-8 exact match tags, 5-8 broad niche tags",
            "Thumbnail: 1280×720px, 3-rule composition, face + text overlay",
            "Chapters: add timestamps for videos >8 min",
        ],
        "growth_tactics": _yt_growth_tactics(stage),
        "monetisation_readiness": _yt_monetisation(followers, avg_views),
    }


def _optimise_instagram(niche: str, followers: int, avg_views: int) -> dict:
    er = _engagement_rate(followers, avg_views)
    stage = _growth_stage(followers)

    return {
        "platform": "instagram",
        "niche": niche or "general",
        "growth_stage": stage,
        "engagement_rate": f"{er:.1f}%",
        "profile_checklist": [
            "Username: searchable niche keyword if possible",
            "Name field: include your main keyword (e.g. 'Fitness Coach | John')",
            "Bio: problem → solution → CTA in 3 lines, max 150 chars",
            "Profile photo: bright, smiling face or clean logo",
            "Story highlights: 5-8 covers with branded icons, label clearly",
            "Link in bio: link-in-bio page with lead magnet or product",
        ],
        "content_mix": _ig_content_mix(niche),
        "reels_strategy": [
            "Post 4-7 Reels per week — Instagram's primary reach driver",
            "Hook in first 0.5s (text on screen or action)",
            "Use trending audio — check Instagram audio trending page",
            "Aspect ratio: 9:16 full-screen (1080×1920)",
            "Add 3-5 relevant hashtags in caption (not in comments)",
            "Reply to every comment in first 60 minutes",
        ],
        "hashtag_strategy": _ig_hashtag_strategy(niche, followers),
        "posting_times": _ig_posting_times(),
        "growth_tactics": _ig_growth_tactics(stage, er),
        "monetisation_readiness": _ig_monetisation(followers, er),
    }


# ── Content strategy helpers ──────────────────────────────────────────────────

def _tt_content_strategy(niche: str, stage: str) -> list[str]:
    base = [
        "Hook formula: question / shocking stat / 'Wait till you see...' in first 1s",
        "Video length: 7-15s for viral reach; 30-60s for depth/authority",
        "Post original audio or trending sounds (check Creative Center)",
        "Show face on camera — accounts with faces get 3x more engagement",
        "End with a question to boost comments (comments = more reach)",
        "Stitch/Duet trending content in your niche weekly",
        "Post B-roll + voiceover — low effort, high retention format",
        "Series content: '5-part series' keeps viewers coming back",
    ]
    if stage == "starter":
        base.insert(0, "Post 2-3x daily — volume is your fastest growth lever right now")
    elif stage == "growing":
        base.insert(0, "Consistency over volume: 1-2x daily at optimal times")
    else:
        base.insert(0, "Protect your ER: don't sacrifice quality for frequency")
    return base


def _tt_posting_schedule(stage: str) -> dict:
    if stage == "starter":
        return {
            "frequency": "2-3x per day",
            "best_times": ["6-9 AM", "12-2 PM", "7-11 PM"],
            "timezone": "Audience local time",
            "note": "Consistency matters more than perfect timing at this stage",
        }
    if stage == "growing":
        return {
            "frequency": "1-2x per day",
            "best_times": ["7-9 AM", "12 PM", "7-9 PM"],
            "timezone": "Audience local time",
            "note": "Check your analytics for your specific peak hours",
        }
    return {
        "frequency": "5-7x per week",
        "best_times": ["8 AM", "1 PM", "8 PM"],
        "timezone": "Audience local time",
        "note": "Quality > quantity; use analytics to refine",
    }


def _tt_hashtag_formula(niche: str) -> dict:
    return {
        "total_tags": "5-7 per video",
        "formula": "2 discovery + 2 large-niche + 2-3 micro-niche",
        "example": f"#fyp #foryoupage #{niche or 'yourniche'} #trending + 2-3 specific tags",
        "placement": "First comment OR end of caption — both work equally",
        "avoid": "Banned hashtags; irrelevant tags; more than 10 tags",
    }


def _tt_growth_tactics(stage: str, er: float) -> list[str]:
    tactics = [
        "Engage for 30 mins after posting (reply comments = more reach)",
        "Go Live 2x/week once you hit 1K — TikTok pushes live content",
        "Follow/engage 20-30 accounts in your niche daily",
        "Stitch or duet at least 2 viral videos/week in your niche",
        "Analyse your top 3 performing videos — make 5 more like them",
        "Cross-post to Instagram Reels and YouTube Shorts",
        "Collab with creators 2x your size (split-screen or mention)",
    ]
    if er < 3:
        tactics.insert(0, "Low ER: focus on stronger hooks and end CTAs before scaling")
    if stage == "starter":
        tactics.append("Comment on 50 viral videos/day in your niche — this builds exposure")
    return tactics


def _tt_monetisation(followers: int) -> dict:
    if followers >= 10_000:
        return {
            "tiktok_creator_fund": "Eligible (apply in app)",
            "tiktok_creativity_program": "Eligible if 18+",
            "brand_deals": "Start pitching brands in your niche",
            "tiktok_shop": "Apply for TikTok Shop affiliate",
            "live_gifts": "Eligible — go Live regularly",
            "estimated_monthly": "$200-2000+ depending on niche & engagement",
        }
    if followers >= 1_000:
        return {
            "tiktok_creator_fund": "Not yet eligible (need 10K)",
            "brand_deals": "Micro-influencer deals possible ($50-500/post)",
            "affiliate_marketing": "Add affiliate links in bio now",
            "digital_products": "Sell e-books, presets, templates via bio link",
            "focus": "Reach 10K followers to unlock all monetisation features",
        }
    return {
        "focus": "Reach 1K followers first, then monetise",
        "meanwhile": [
            "Build email list from day 1 via bio link",
            "Create digital product to launch at 1K",
            "Document your journey — authenticity sells",
        ],
    }


def _tt_quick_wins(er: float, followers: int) -> list[str]:
    wins = []
    if er < 5:
        wins.append("Change your hook — test 3 different opening lines this week")
    if followers < 100:
        wins.append("Post your top 5 pieces of value as separate videos today")
    wins.extend([
        "Pin your best video — update every 30 days",
        "Add a keyword to your TikTok name field",
        "Reply to every comment with a question — doubles comment count",
        "Share your TikToks to Instagram Stories with a 'watch more' CTA",
    ])
    return wins


def _yt_content_strategy(niche: str, stage: str) -> list[str]:
    return [
        "A/B test thumbnails: upload video → change thumbnail after 48h if CTR < 4%",
        "Hook: deliver on your title promise within first 30 seconds",
        "Pattern interrupt every 90 seconds (cut, zoom, music change)",
        "Call to subscribe mid-video when retention is highest",
        "Create video series — playlists multiply watch time and subscribers",
        "Research competitors' most-viewed videos and cover the same topics",
        "Long-form (10-20 min) for authority; Shorts (< 60s) for discovery",
        "Timestamps/chapters improve watch time and SEO",
    ]


def _yt_upload_schedule(stage: str) -> dict:
    if stage == "starter":
        return {"frequency": "2-3x/week", "note": "Consistency beats quality early on"}
    if stage == "growing":
        return {"frequency": "1-2x/week + 3-5 Shorts/week", "note": "Shorts are key for reach"}
    return {"frequency": "1x/week long-form + Shorts as needed", "note": "Quality first"}


def _yt_growth_tactics(stage: str) -> list[str]:
    return [
        "YouTube Shorts: post 3-5/week — fastest free reach on the platform",
        "Community posts: post 3-4x/week once you hit 500 subs",
        "Respond to every comment in the first 24h",
        "Collaborate: appear on a channel 5-10x your size",
        "SEO: use TubeBuddy/vidIQ to find keywords with high search, low competition",
        "End screens + cards on every video",
        "Promote on Reddit/Quora by genuinely answering questions (link to video)",
    ]


def _yt_monetisation(subscribers: int, avg_views: int) -> dict:
    if subscribers >= 1_000 and avg_views >= 4_000:
        return {
            "adsense": "Eligible — apply for YouTube Partner Programme",
            "memberships": "Available at 500 subs",
            "super_thanks": "Available",
            "brand_deals": "Pitch brands in your niche — $10-50 CPM typical",
            "merch_shelf": "Available at 10K subs",
        }
    return {
        "focus": f"Need: 1,000 subs ({subscribers} now) + 4,000 watch hours/year",
        "meanwhile": [
            "Affiliate links in description (Amazon, etc.)",
            "Sell digital products via channel links",
            "Patreon/Ko-fi for early access",
        ],
    }


def _ig_content_mix(niche: str) -> dict:
    return {
        "reels": "60% — primary reach driver",
        "carousels": "25% — highest save rate of any format",
        "stories": "10% — daily, for engagement and DMs",
        "static_posts": "5% — avoid unless carousel-format",
        "ratio": "80% value / 10% personal / 10% promotional",
    }


def _ig_hashtag_strategy(niche: str, followers: int) -> dict:
    if followers < 1_000:
        size = "small (<500K posts)"
    elif followers < 10_000:
        size = "medium (500K-2M posts)"
    else:
        size = "large (2M+ posts)"
    return {
        "count": "3-5 in caption",
        "target_size": size,
        "formula": "1-2 broad + 2-3 niche-specific",
        "example": f"#{niche or 'yourniche'} + 2 specific sub-niche tags",
        "avoid": "All mega-tags (>50M posts) — your content gets buried",
    }


def _ig_posting_times() -> dict:
    return {
        "reels": ["Mon-Fri 6-9 AM", "Tue-Fri 12-2 PM", "Mon/Wed/Fri 7-10 PM"],
        "stories": "Daily, 3-5 times spread through day",
        "carousels": "Tue/Thu/Sat 10 AM-12 PM",
        "note": "Check Instagram Insights > Most Active Times for your audience",
    }


def _ig_growth_tactics(stage: str, er: float) -> list[str]:
    tactics = [
        "Reply to every comment within 1 hour of posting",
        "DM everyone who follows you — introduce yourself",
        "Engage 30 min before and after posting (IG rewards this)",
        "Use Instagram Collab feature with creators in your niche",
        "Cross-promote: share Reels to TikTok, Stories to Facebook",
        "Share user-generated content (repost with credit)",
        "Polls, Questions, Quizzes in Stories daily for engagement",
    ]
    if er < 2:
        tactics.insert(0, "Low ER warning: post a question-based Story right now to re-engage")
    return tactics


def _ig_monetisation(followers: int, er: float) -> dict:
    if followers >= 10_000 and er > 2:
        return {
            "instagram_subscriptions": "Eligible",
            "badges_in_live": "Eligible",
            "brand_deals": f"Estimated $100-500/post at {followers:,} followers",
            "affiliate": "Instagram native affiliate + external links",
            "digital_products": "Sell via link-in-bio",
        }
    if followers >= 1_000:
        return {
            "brand_deals": "Micro-influencer deals ($25-150/post)",
            "affiliate_marketing": "Best option right now",
            "digital_products": "E-books, templates, presets via Gumroad",
        }
    return {
        "focus": "Reach 1K followers to unlock Creator tools",
        "meanwhile": ["Build email list via lead magnet in bio link"],
    }


# ── Engagement helpers ────────────────────────────────────────────────────────

def _engagement_rate(followers: int, avg_views: int) -> float:
    if followers == 0:
        return 0.0
    return round((avg_views / followers) * 100, 2)


def _growth_stage(followers: int) -> str:
    if followers < 1_000:
        return "starter"
    if followers < 10_000:
        return "growing"
    if followers < 100_000:
        return "established"
    return "authority"


def _tt_er_benchmark(er: float) -> str:
    if er > 10:
        return "Excellent (>10% — top 5%)"
    if er > 5:
        return "Good (5-10% — above average)"
    if er > 2:
        return "Average (2-5%)"
    return "Below average (<2%) — focus on hooks and CTAs"


def _yt_sub_benchmark(subs: int) -> str:
    if subs >= 1_000_000:
        return "Elite (1M+)"
    if subs >= 100_000:
        return "Established (100K+)"
    if subs >= 10_000:
        return "Growing (10K+)"
    if subs >= 1_000:
        return "Early (1K+)"
    return "Starter (<1K)"
