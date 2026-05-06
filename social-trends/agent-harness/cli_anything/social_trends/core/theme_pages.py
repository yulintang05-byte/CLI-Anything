"""Theme page strategy — converting, growing, and monetizing niche theme pages."""

import re
from typing import Optional


# ── Theme page overview ───────────────────────────────────────────


DEFINITION = """
A THEME PAGE is a social media account built around a topic/niche rather than a personal brand.
The creator stays anonymous and reposts/curates content from others (with credit) or creates
original content within the theme. Examples: @motivationmafia, @luxury.lifestyle, @sciencefacts.

Why theme pages work:
  • No face required — post anonymously at scale
  • Easily outsourceable — train VAs to handle posting
  • Multiple pages = multiple revenue streams
  • Sellable asset once established (3–5x monthly revenue)
"""


# ── Niche selection framework ─────────────────────────────────────


NICHE_SCORES: dict[str, dict] = {
    "motivation": {
        "demand": 10,
        "competition": 8,
        "monetization": 8,
        "content_availability": 10,
        "recommended": True,
        "why": "Evergreen demand, infinite repostable content, strong sponsorship market",
    },
    "luxury": {
        "demand": 9,
        "competition": 9,
        "monetization": 9,
        "content_availability": 9,
        "recommended": True,
        "why": "High CPM, strong affiliate opportunities (cars, watches, real estate)",
    },
    "finance": {
        "demand": 9,
        "competition": 7,
        "monetization": 10,
        "content_availability": 8,
        "recommended": True,
        "why": "Highest CPM niche, financial products pay premium affiliate commissions",
    },
    "fitness": {
        "demand": 9,
        "competition": 9,
        "monetization": 8,
        "content_availability": 9,
        "recommended": True,
        "why": "Supplement/apparel affiliates, coaching programs, strong community",
    },
    "animals": {
        "demand": 10,
        "competition": 8,
        "monetization": 6,
        "content_availability": 10,
        "recommended": True,
        "why": "Viral-friendly, massive audience, lower CPM but easy growth",
    },
    "quotes": {
        "demand": 8,
        "competition": 10,
        "monetization": 6,
        "content_availability": 10,
        "recommended": False,
        "why": "Over-saturated — needs a unique angle (e.g. niche-specific quotes)",
    },
    "beauty": {
        "demand": 9,
        "competition": 9,
        "monetization": 9,
        "content_availability": 9,
        "recommended": True,
        "why": "Strong affiliate market (Amazon, Sephora), high female CPM",
    },
    "cooking_food": {
        "demand": 10,
        "competition": 7,
        "monetization": 7,
        "content_availability": 10,
        "recommended": True,
        "why": "Massive audience, recipe eBooks, meal kit affiliates",
    },
    "tech": {
        "demand": 8,
        "competition": 7,
        "monetization": 9,
        "content_availability": 8,
        "recommended": True,
        "why": "High-ticket affiliate products (laptops, software), strong B2B sponsorships",
    },
    "travel": {
        "demand": 9,
        "competition": 8,
        "monetization": 8,
        "content_availability": 10,
        "recommended": True,
        "why": "Hotel/airline affiliates, travel gear, tourism brand deals",
    },
}


def evaluate_niche(niche: str) -> dict:
    """Score a niche across key theme page metrics."""
    data = NICHE_SCORES.get(niche.lower())
    if not data:
        return {
            "niche": niche,
            "note": f"No preset data for '{niche}'. Evaluate manually against: demand, competition, monetization.",
            "available_niches": sorted(NICHE_SCORES.keys()),
        }
    total = data["demand"] + (10 - data["competition"]) + data["monetization"] + data["content_availability"]
    return {
        "niche": niche,
        **data,
        "total_score": total,
        "grade": "A" if total >= 35 else "B" if total >= 28 else "C",
    }


def rank_niches() -> list[dict]:
    """Rank all known niches by total score."""
    ranked = []
    for niche in NICHE_SCORES:
        result = evaluate_niche(niche)
        ranked.append(result)
    return sorted(ranked, key=lambda x: x.get("total_score", 0), reverse=True)


# ── Theme page setup checklist ────────────────────────────────────


SETUP_CHECKLIST = [
    {
        "phase": "1. Niche Selection",
        "steps": [
            "Research 3–5 potential niches using rank_niches()",
            "Check top 10 accounts in each niche — can you match their quality?",
            "Verify content supply: search niche on TikTok/IG, are there 500+ recent videos?",
            "Choose niche with score >= 30 and recommended=True",
        ],
    },
    {
        "phase": "2. Account Creation",
        "steps": [
            "Create accounts on TikTok, Instagram, and YouTube simultaneously",
            "Use consistent username across all platforms",
            "Set up Linktree/Beacons for bio link before first post",
            "Enable Creator/Business account on all platforms",
            "Set up email for brand inquiries",
        ],
    },
    {
        "phase": "3. Content Pipeline",
        "steps": [
            "Find 5 top performing accounts in your niche to monitor",
            "Set up a content folder (Google Drive/Notion) for saved clips",
            "Collect 30 pieces of content before launching (content bank)",
            "Use CapCut or InShot for editing — keep templates consistent",
            "Add watermark/branding overlay to all content",
        ],
    },
    {
        "phase": "4. Posting Strategy",
        "steps": [
            "Post 3–5 times/day on TikTok for first 30 days",
            "Post 1–2 Reels/day on Instagram + 10 Stories",
            "Repurpose each TikTok to YouTube Shorts and Instagram Reels",
            "Use trending sounds on each platform (check Discover weekly)",
            "Engage with comments for first 30 minutes after posting",
        ],
    },
    {
        "phase": "5. Growth (0–10K)",
        "steps": [
            "Follow/unfollow method (controversial — use sparingly)",
            "Comment on viral posts in your niche with value-add responses",
            "Collaborate with 3–5 similar-size pages for shoutouts",
            "Run 'Tag a friend' content to boost organic reach",
            "Post consistently every day for minimum 60 days",
        ],
    },
    {
        "phase": "6. Monetization (10K+)",
        "steps": [
            "Apply to TikTok Creator Marketplace for brand deals",
            "Join Amazon Associates and relevant affiliate programs",
            "Offer shoutout packages ($50–$500 depending on niche/size)",
            "Create/sell a digital product (eBook, template, course)",
            "Apply for TikTok Creator Fund / YouTube Partner Program",
        ],
    },
]


def get_setup_checklist(phase: Optional[str] = None) -> list[dict]:
    """Return setup checklist, optionally filtered by phase name."""
    if phase:
        return [s for s in SETUP_CHECKLIST if phase.lower() in s["phase"].lower()]
    return SETUP_CHECKLIST



# ── Content reposting framework ───────────────────────────────────


REPOST_GUIDE = {
    "tiktok": {
        "process": [
            "Find viral video (500K+ views, <7 days old)",
            "Download with watermark removal tool (SnapTik, SSSTikTok)",
            "Add your watermark/text overlay",
            "Re-upload with your own caption and different hashtags",
            "Credit original creator in comments (reduces copyright risk)",
        ],
        "legal_note": (
            "TikTok's Terms of Service permit sharing content. However, always credit "
            "original creators and respond promptly to any takedown requests. "
            "Original content always outperforms reposts long-term."
        ),
        "best_content_age": "Repost content 3–7 days after original upload peak",
    },
    "instagram": {
        "process": [
            "Find viral Reel using Reels tab or search",
            "Use Inflact or Reposit app to repost with attribution",
            "Or: screen-record + re-edit with your branding",
            "Tag original creator in caption: 'Credit: @originalcreator'",
            "Add your own caption and hashtags on top",
        ],
        "legal_note": (
            "Instagram requires credit to original creators. Use 'Add Credit' feature "
            "in Instagram Stories. For Reels, tag in caption."
        ),
        "best_content_age": "Repost within 3 days of original going viral for maximum reach",
    },
    "youtube_shorts": {
        "process": [
            "Source viral clips from TikTok, Instagram, or Reddit",
            "Edit in CapCut: add captions, music, transitions",
            "Add intro/outro branding (2 seconds each)",
            "Optimize title with keyword + hook ('This will change your life...')",
            "Add chapters for longer Shorts (60+ seconds)",
        ],
        "legal_note": (
            "YouTube is stricter on copyright. Always transform content (edit, add commentary). "
            "Pure reposts get removed. Add commentary, captions, or educational value."
        ),
        "best_content_age": "YouTube Shorts has less time-sensitivity — good content works any time",
    },
}


def get_repost_guide(platform: str) -> dict:
    guide = REPOST_GUIDE.get(platform.lower())
    if not guide:
        return {"error": f"Unknown platform '{platform}'"}
    return {"platform": platform, **guide}


# ── Monetization roadmap ──────────────────────────────────────────


MONETIZATION_TIERS = [
    {
        "milestone": "0–1K followers",
        "revenue_potential": "$0–$50/month",
        "strategies": [
            "Build content bank and establish posting consistency",
            "Focus on niche clarity and profile optimization",
            "Join affiliate programs early (Amazon, ShareASale)",
        ],
    },
    {
        "milestone": "1K–10K followers",
        "revenue_potential": "$50–$500/month",
        "strategies": [
            "Sell shoutouts to smaller accounts ($25–$100 each)",
            "Promote affiliate links (aim for 1–3% conversion)",
            "Sell digital products (presets, templates, guides) for $7–$27",
        ],
    },
    {
        "milestone": "10K–50K followers",
        "revenue_potential": "$500–$2,000/month",
        "strategies": [
            "Brand deals ($200–$1,000 per post)",
            "TikTok Creator Fund / YouTube Partner Program",
            "Sell higher-ticket digital products ($47–$197)",
            "Launch a paid community (Patreon, Discord, Telegram)",
        ],
    },
    {
        "milestone": "50K–100K followers",
        "revenue_potential": "$2,000–$5,000/month",
        "strategies": [
            "Brand deal packages ($1,000–$5,000 per post)",
            "Sell the page (5–10x monthly revenue = $10K–$50K)",
            "Launch a course or coaching program ($297–$997)",
            "Licensing your content strategy to other creators",
        ],
    },
    {
        "milestone": "100K+ followers",
        "revenue_potential": "$5,000–$30,000+/month",
        "strategies": [
            "Premium brand deals ($5,000–$50,000 per campaign)",
            "Build a portfolio of 5–10 pages in same or adjacent niches",
            "Launch a media company — hire VAs, scale to $50K+/month",
            "Sell pages as package deals to investors/brands",
        ],
    },
]


def get_monetization_roadmap(current_followers: Optional[int] = None) -> list[dict]:
    if current_followers is None:
        return MONETIZATION_TIERS
    for tier in MONETIZATION_TIERS:
        low, high = _parse_milestone(tier["milestone"])
        if low <= current_followers <= high:
            return [tier]
    return [MONETIZATION_TIERS[-1]]  # 100K+


def _parse_milestone(milestone: str) -> tuple[int, int]:
    """Parse '10K–50K followers' into (10000, 50000)."""
    nums = re.findall(r"[\d.]+[KM]?", milestone)
    def parse_num(s):
        s = s.strip()
        if s.endswith("K"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        try:
            return int(s)
        except ValueError:
            return 0
    if len(nums) >= 2:
        return parse_num(nums[0]), parse_num(nums[1])
    if len(nums) == 1:
        return parse_num(nums[0]), 10_000_000
    return 0, 10_000_000
