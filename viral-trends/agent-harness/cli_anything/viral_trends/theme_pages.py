"""Theme page creation and monetization guide — structured knowledge base."""
from __future__ import annotations
from typing import Any


THEME_PAGE_GUIDE: dict[str, Any] = {
    "what_is_a_theme_page": (
        "A theme page curates and reposts content around a single topic (e.g. 'Luxury Lifestyle', "
        "'Mindset Quotes', 'Nature Cinematography'). You don't need to appear on camera. "
        "The account IS the brand — not you."
    ),
    "step_by_step": [
        {
            "step": 1,
            "title": "Pick a Profitable Niche",
            "actions": [
                "Choose niches with high CPM ads or affiliate products: finance, fitness, tech, luxury, mindset",
                "Validate: search the niche on TikTok/Reels, look for 100k+ view videos in the last 30 days",
                "Avoid: saturated niches with no monetization angle (memes only, generic humor)",
            ],
            "tool": "viral-trends hashtags tiktok --niche <your-niche>",
        },
        {
            "step": 2,
            "title": "Set Up Accounts Across All Platforms",
            "actions": [
                "Create accounts on: TikTok, Instagram (Reels), YouTube (Shorts)",
                "Use same handle across platforms for brand recognition",
                "Profile pic: high-contrast logo or aesthetic image — no selfies",
                "Optimize bio: niche keyword + value prop + one CTA",
            ],
            "tool": "viral-trends optimize --platform tiktok --niche <niche>",
        },
        {
            "step": 3,
            "title": "Source Content (3 Legal Methods)",
            "actions": [
                "Method A — Curate with credit: repost viral videos, always tag original creator",
                "Method B — UGC compilations: stitch/duet top videos with your commentary",
                "Method C — Faceless original: screen recordings, B-roll + voiceover AI, stock footage + music",
            ],
            "free_tools": [
                "CapCut (mobile editing, trending templates)",
                "ElevenLabs (AI voiceover)",
                "Pexels / Pixabay (royalty-free B-roll)",
                "clipper (this toolkit — clip and export for each platform preset)",
            ],
        },
        {
            "step": 4,
            "title": "Post With Trending Audio + Hashtags",
            "actions": [
                "TikTok: always use a trending sound from the Creative Center — boosts algorithmic reach",
                "Reels: use trending audio (same rule as TikTok)",
                "Shorts: original audio or licensed music via YouTube Audio Library",
                "Attach 3-5 hashtags: 1 niche, 1 trending, 1 broad (e.g. #fyp, #viral)",
            ],
            "tool": "viral-trends hashtags cross-platform --limit 20",
        },
        {
            "step": 5,
            "title": "Consistency Schedule",
            "actions": [
                "Post 2-3x/day on TikTok for first 30 days (algorithm rewards volume early)",
                "1x/day on Reels and Shorts (repurpose TikTok content same day)",
                "Batch-create 1 week of content in one session, schedule via Later or Buffer",
                "Reply to every comment in first 30 minutes after posting (boosts reach)",
            ],
        },
        {
            "step": 6,
            "title": "Monetization Stack (in order)",
            "actions": [
                "Phase 1 (0-10k): Build audience, no selling. Focus on follows/saves rate.",
                "Phase 2 (10k+): TikTok Creator Fund / YouTube Shorts Fund + affiliate links",
                "Phase 3 (50k+): Sponsorships ($50-$500/post) + sell digital products (Gumroad/Stan.store)",
                "Phase 4 (100k+): Launch paid newsletter, community (Discord/Whop), or course",
            ],
            "affiliate_programs": [
                "Amazon Associates (general products)",
                "Impact / ShareASale (brand deals)",
                "ClickBank / Digistore24 (digital products, high commission)",
                "Whop (digital communities and tools)",
            ],
        },
        {
            "step": 7,
            "title": "Converting Theme Page (Driving Traffic)",
            "actions": [
                "Link in bio → Linktree or Beacons page with: affiliate links, email opt-in, product",
                "Pin a 'start here' video that explains the value of following",
                "Use 'save this for later' CTA — saves signal to algorithm that content is valuable",
                "Stories / Stickers: polls and Q&As boost profile visits and link clicks",
                "Run a giveaway at 1k, 5k, 10k milestones to spike follower growth",
            ],
        },
    ],
    "conversion_metrics_to_track": {
        "save_rate":           "Saves ÷ Views × 100 — target >3%",
        "follow_rate":         "New follows ÷ Views × 100 — target >1%",
        "link_click_rate":     "Link clicks ÷ Profile visits × 100 — target >10%",
        "watch_time_percent":  "Avg watch % — target >50% for TikTok, >40% for Reels",
    },
    "common_mistakes": [
        "Posting without a trending sound on TikTok/Reels",
        "Using too many broad hashtags (#fyp, #viral only) — algorithm can't categorize you",
        "Inconsistent posting — algorithm deprioritizes accounts that disappear for 3+ days",
        "Monetizing too early — sending people to links before they trust the account",
        "Ignoring analytics — check weekly, kill what's not working in 72h",
    ],
}


def get_guide() -> dict[str, Any]:
    """Return the full theme page guide."""
    return THEME_PAGE_GUIDE


def get_step(step_number: int) -> dict[str, Any]:
    """Return a specific step from the guide."""
    steps = THEME_PAGE_GUIDE.get("step_by_step", [])
    for s in steps:
        if s.get("step") == step_number:
            return s
    raise ValueError(f"Step {step_number} not found. Valid steps: 1-{len(steps)}")


def get_monetization_timeline() -> list[dict]:
    """Return just the monetization phases."""
    for s in THEME_PAGE_GUIDE["step_by_step"]:
        if s.get("step") == 6:
            return [{"phase": a} for a in s["actions"]]
    return []
