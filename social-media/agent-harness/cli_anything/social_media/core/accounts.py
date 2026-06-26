"""Account optimization engine.

Generates platform-specific optimization checklists and profile audits
for TikTok, YouTube, and Instagram accounts.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AccountProfile:
    platform: str
    handle: str = ""
    niche: str = ""
    follower_count: int = 0
    avg_views: int = 0
    posting_frequency: str = ""
    bio_set: bool = False
    link_in_bio: bool = False
    profile_pic_set: bool = False
    pinned_post: bool = False
    highlight_covers: bool = False  # Instagram only


# ── Platform-specific optimization playbooks ──────────────────────────────────

TIKTOK_OPTIMIZATION = {
    "profile": [
        "Username: short, memorable, matches your niche keyword (e.g. @dailymotivationn, @gymroutineclub)",
        "Profile photo: high-contrast face or bold logo — visible at 40px thumbnail size",
        "Bio: 1 power line + 1 CTA + 1 emoji max. Example: 'Daily side hustle tips 💰 | Free blueprint ↓'",
        "Link in bio: use a link aggregator (Linktree / Stan.store / Beacons) NOT a direct product link",
        "Pinned videos: pin your 3 best-performing videos — these are your permanent first impression",
        "Category: set account category to match niche (Creator Tools > Niche > Specific)",
    ],
    "content": [
        "Post 1–3x daily for first 30 days — TikTok rewards new account velocity",
        "Optimal length: 7–15s for viral reach, 30–60s for saves and shares",
        "First frame must stop the scroll — use text overlay, bold color, or unexpected image",
        "Use trending sounds from the Discover page within 48–72h of trending (early mover wins)",
        "Add 3–5 hashtags: 1 mega (#fyp), 1 niche (#gymtok), 1 trending (#WorldCup2026)",
        "Post between 6–9am, 12–3pm, 7–11pm in your audience's timezone",
        "Caption: ask a yes/no question to trigger comment algorithm boost",
        "Reply to every comment within the first hour of posting",
    ],
    "growth": [
        "Duet or stitch 2–3 viral videos per week in your niche — borrows their algorithmic momentum",
        "Use the Creator Marketplace to find collaboration opportunities at your follower level",
        "Go LIVE 2x/week minimum — TikTok heavily promotes accounts that go live regularly",
        "Cross-post your TikToks to YouTube Shorts and Instagram Reels (repurpose everything)",
        "Follow 20–30 accounts in your niche daily for reciprocal follow-backs",
        "Analyze your TikTok Analytics weekly: check Audience tab for peak hours",
    ],
    "monetization": [
        "TikTok Creator Rewards: requires 10K followers + 100K views/30 days",
        "Series (paid content): unlock at 10K followers",
        "TikTok Shop affiliate: apply at any follower count — add product links to videos",
        "Brand deals: start pitching at 5K engaged followers with a media kit",
        "Digital products: sell via link-in-bio (courses, templates, e-books)",
    ],
}

YOUTUBE_OPTIMIZATION = {
    "channel": [
        "Channel name: keyword-rich + brandable (e.g. 'Daily Finance Hacks' not 'JohnSmith2003')",
        "Channel art: 2560x1440px banner, clear value prop visible on mobile (safe zone: 1235x338px center)",
        "Profile pic: high-contrast, recognizable at 40px — same as TikTok for brand consistency",
        "Channel description: first 150 chars show in search — lead with your core keyword",
        "Featured channel sections: organize playlists by topic — improves session time",
        "Custom URL: claim at 100 subscribers (youtube.com/@yourhandle)",
        "Channel trailer: 60–90s, hook in 5s, explain who it's for, end with subscribe CTA",
    ],
    "shorts": [
        "Upload as Shorts (9:16, under 60s, #Shorts in title OR description)",
        "Title: include primary keyword + emotional hook. Max 60 chars",
        "Description: 2–3 sentences, 3–5 hashtags, include link to long-form video",
        "Thumbnail: auto-selected from video but can set custom — bright, bold, face if possible",
        "End screen: add 'Subscribe' button element — drives channel growth from Shorts viewers",
        "Shorts shelf placement: post 2–3/day for first 2 weeks to appear in Shorts feed",
    ],
    "content": [
        "Optimal posting: 2–3 Shorts/day + 1 long-form/week for compound growth",
        "Long-form: 8–15 mins hits YouTube ad revenue sweet spot",
        "Chapters: add timestamps to long videos — improves search ranking",
        "End screen (last 20s of long video): promote most relevant other video + subscribe",
        "Cards: add 2–3 info cards to long videos linking related content",
        "Community posts: use for polls, updates, teasers — keeps audience engaged between uploads",
    ],
    "seo": [
        "Title: primary keyword first, then hook. Use TubeBuddy/vidIQ to verify search volume",
        "Tags: 10–15 tags mixing exact match, broad, and related terms",
        "Description: 200+ words, front-load keywords, include transcript snippet",
        "Chapters with timestamps: crawled by Google, appear in search snippets",
        "Closed captions: upload SRT for better search indexing",
        "Playlists: group content into 5–10 video playlists — increases session time 40%+",
    ],
    "monetization": [
        "YPP eligibility: 1K subscribers + 4K watch hours (long-form) OR 10M Shorts views/90 days",
        "Mid-roll ads trigger at 8+ min videos — target 10–15 min for max ad revenue",
        "Super Thanks / Super Chat: enable for live streams at any size",
        "Channel memberships: unlock at 500 subscribers",
        "Merch shelf: connect Printful/Spreadshop at 10K subscribers",
    ],
}

INSTAGRAM_OPTIMIZATION = {
    "profile": [
        "Username: matches TikTok/YouTube handle exactly — cross-platform brand consistency",
        "Name field (searchable): include your main keyword here, not just your name",
        "Bio: 150 chars, 3 lines max. Line 1: who you help. Line 2: how. Line 3: CTA + link",
        "Link in bio: use link-in-bio page (not direct link) — list top 3–5 destinations",
        "Highlight covers: create branded covers in Canva (same color palette) for each Story category",
        "Story Highlights: organize as Portfolio | Tips | Reviews | FAQ | About Me",
        "Professional account: switch to Creator (not Business) for better organic reach",
    ],
    "reels": [
        "Reels: 7–15s get highest distribution; 30–60s get higher saves",
        "Audio: use Instagram's trending audio (shown with arrow icon) within 48h of trending",
        "Cover frame: set custom cover that looks good as a grid post — Reels show on profile grid",
        "Caption: first line is the hook — truncated at 125 chars so lead with value",
        "Hashtags: 3–5 niche hashtags in caption (Instagram de-prioritizes hashtag stuffing)",
        "Location tag: tag a city for local reach boost",
        "Collab post: use Collab feature with a creator in your niche — shares reach to both audiences",
    ],
    "growth": [
        "Post 1 Reel/day + 5–10 Stories/day — Stories keep you top of followers' feeds",
        "Engage genuinely: spend 15 min/day commenting on top posts in your niche (be first commenter)",
        "Go Live: 2x/week — Instagram boosts Live notifications to all followers",
        "DM new followers within 24h: personal message increases follow-back rate 3x",
        "Cross-promote: share your TikTok as Instagram Reel (remove TikTok watermark first — use SnapTik)",
    ],
    "monetization": [
        "Instagram Subscriptions: exclusive content for paying followers — unlock at any size",
        "Instagram Shopping: tag products in posts/Reels — connect Shopify or WooCommerce",
        "Affiliate badges: Instagram native affiliate program for brand partnerships",
        "Paid partnerships: use branded content tool for paid collabs (required by FTC)",
        "Digital products: promote via bio link + Story swipe-up (unlocked at any follower count now)",
    ],
}

PLATFORM_PLAYBOOKS = {
    "tiktok": TIKTOK_OPTIMIZATION,
    "youtube": YOUTUBE_OPTIMIZATION,
    "instagram": INSTAGRAM_OPTIMIZATION,
}


def get_optimization_checklist(platform: str, account: Optional[AccountProfile] = None) -> dict:
    """Return full optimization playbook for a platform."""
    platform = platform.lower().replace("-", "").replace(" ", "")
    if "tiktok" in platform:
        key = "tiktok"
    elif "youtube" in platform or "yt" in platform:
        key = "youtube"
    elif "instagram" in platform or "ig" in platform:
        key = "instagram"
    else:
        return {"error": f"Unknown platform '{platform}'. Supported: tiktok, youtube, instagram"}

    playbook = PLATFORM_PLAYBOOKS[key]
    result = {
        "platform": key,
        "checklist": playbook,
        "total_items": sum(len(v) for v in playbook.values()),
    }

    if account:
        result["audit"] = _audit_account(account, playbook)

    return result


def _audit_account(account: AccountProfile, playbook: dict) -> dict:
    """Score an account against the playbook and surface quick wins."""
    quick_wins = []
    score = 0
    total = 4

    if account.profile_pic_set:
        score += 1
    else:
        quick_wins.append("Set a high-contrast profile photo")

    if account.bio_set:
        score += 1
    else:
        quick_wins.append("Write a niche-specific bio with CTA")

    if account.link_in_bio:
        score += 1
    else:
        quick_wins.append("Add a link-in-bio page (Beacons / Linktree)")

    if account.pinned_post:
        score += 1
    else:
        quick_wins.append("Pin your 3 best-performing posts")

    return {
        "profile_score": f"{score}/{total}",
        "quick_wins": quick_wins,
        "follower_tier": _follower_tier(account.follower_count),
        "recommendation": _tier_recommendation(account),
    }


def _follower_tier(count: int) -> str:
    if count < 1_000:
        return "nano (0–1K) — focus on consistency + niche authority"
    if count < 10_000:
        return "micro (1K–10K) — start pitching brands + enable monetization"
    if count < 100_000:
        return "mid-tier (10K–100K) — diversify revenue streams"
    if count < 1_000_000:
        return "macro (100K–1M) — negotiate 4-figure brand deals"
    return "mega (1M+) — agency representation recommended"


def _tier_recommendation(account: AccountProfile) -> str:
    if account.follower_count < 1_000:
        return "Post 2–3x/day. Use trending audio within 24h. Prioritize consistency over perfection."
    if account.follower_count < 10_000:
        return "Add TikTok Shop affiliate + link-in-bio digital product. Start a weekly Live."
    if account.follower_count < 100_000:
        return "Build email list via lead magnet. Create a paid community or Substack."
    return "Hire an editor. Systematize content pipeline. Pursue 5-figure brand deals."
