"""Account optimization engine.

Takes live trend data and produces a concrete optimization plan for each
platform: content pillars, hashtag sets, caption templates, bio upgrades,
posting schedule, and engagement tactics.
"""

from __future__ import annotations

from typing import Any


def optimize_account(
    platform: str,
    niche: str,
    trending_hashtags: list[dict],
    trending_music: list[dict],
    opportunities: list[dict],
    current_followers: int = 0,
) -> dict[str, Any]:
    """Generate a comprehensive optimization plan for a single platform account."""
    platform = platform.lower()

    if platform == "tiktok":
        return _optimize_tiktok(niche, trending_hashtags, trending_music, opportunities, current_followers)
    elif platform == "youtube":
        return _optimize_youtube(niche, trending_hashtags, opportunities, current_followers)
    elif platform == "instagram":
        return _optimize_instagram(niche, trending_hashtags, opportunities, current_followers)
    else:
        raise ValueError(f"Unknown platform '{platform}'. Choose: tiktok, youtube, instagram")


def _optimize_tiktok(niche, hashtags, music, opportunities, followers) -> dict:
    top_tags = [h["hashtag"] for h in hashtags[:5]]
    niche_tags = [f"#{niche.lower().replace(' ', '')}", f"#{niche.lower()}tips", f"#{niche.lower()}viral"]
    sound_of_week = music[0]["title"] if music else "use trending audio from Discover tab"

    return {
        "platform": "TikTok",
        "niche": niche,
        "current_followers": followers,
        "bio_formula": f"[Hook about {niche}] | [Proof/credibility] | [CTA: Follow for daily {niche} content]",
        "bio_example": f"🔥 {niche} hacks that actually work | 1M+ views | New tip daily ↓",
        "content_pillars": [
            f"Education: Quick '{niche} explained in 60s' videos",
            f"Entertainment: Trends + {niche} twist (use trending audio)",
            f"Social proof: 'Watch me {niche} challenge' or before/afters",
            f"Controversy: 'Unpopular opinion about {niche}'",
            f"Trending format: Duet/Stitch top creators in {niche}",
        ],
        "hashtag_strategy": {
            "formula": "3 niche + 3 trending + 2 broad + 1 custom branded",
            "niche_tags": niche_tags,
            "trending_tags": top_tags,
            "broad_tags": ["#viral", "#fyp", "#foryoupage"],
            "branded_tag": f"#{niche.lower().replace(' ', '')}with[YourName]",
            "caption_template": f"[Hook question or bold statement]\n\n{' '.join(niche_tags[:2])} {' '.join(top_tags[:3])} #fyp #viral",
        },
        "sound_strategy": {
            "this_week": sound_of_week,
            "rule": "Use audio trending < 72hrs old for max boost. Check Discover > Sounds daily.",
            "original_audio_tip": "Create a custom sound/jingle — if it goes viral, your account gets featured each time someone uses it",
        },
        "posting_schedule": {
            "frequency": "1–3 videos/day during growth phase, 1/day for maintenance",
            "best_times": ["7–9 AM local", "12–3 PM local", "7–10 PM local"],
            "consistency": "Post at same times daily to train the algorithm on your audience",
        },
        "engagement_tactics": [
            "Reply to every comment in first 30 minutes of posting",
            "Pin a comment with a CTA: 'Follow for part 2'",
            "Use 'stitch this' CTAs to generate response content",
            "Go Live 2–3x/week after reaching 1K followers",
            "Duet top creators in your niche to borrow their audience",
        ],
        "growth_milestones": {
            "0_to_1k": "Post 3x/day with trending audio. Focus on hooks. Ignore vanity metrics.",
            "1k_to_10k": "Niche down harder. Collaborate with similar-sized accounts.",
            "10k_to_100k": "Series content, consistent character/format. Start email list.",
            "100k_plus": "Brand deals, TikTok Creator Fund, live stream monetization.",
        },
    }


def _optimize_youtube(niche, hashtags, opportunities, followers) -> dict:
    top_tags = [h["hashtag"] for h in hashtags[:8]]

    return {
        "platform": "YouTube",
        "niche": niche,
        "current_subscribers": followers,
        "channel_art": f"Banner should clearly state: What you post | How often | [Your unique angle on {niche}]",
        "about_section": f"[Keyword-rich description of {niche} channel]. New video every [day]. Subscribe for [benefit].",
        "content_pillars": [
            f"How-to tutorials: 'How to [achieve {niche} goal] in [timeframe]'",
            f"Reviews & rankings: 'Best [tools/methods] for {niche} in 2026'",
            f"Case studies: 'I tried [popular {niche} method] for 30 days — here's what happened'",
            f"Reaction/commentary: React to trending {niche} content",
            f"Shorts: Clip your long-form into 30-60s Shorts for discovery",
        ],
        "title_formula": [
            f"I [did something bold related to {niche}] for 30 days (SHOCKING results)",
            f"Why everyone is WRONG about {niche} in 2026",
            f"The ONLY {niche} strategy you need (backed by data)",
            f"[Number] {niche} mistakes KILLING your results",
            f"How I [achieved result] with {niche} (step by step)",
        ],
        "seo_strategy": {
            "title": "Front-load keyword in title. Keep under 60 chars. Add power word + number.",
            "description": "First 150 chars must include main keyword — this shows in search. Add timestamps, links, hashtags.",
            "tags": top_tags + [niche, f"{niche} tutorial", f"{niche} 2026"],
            "hashtags_in_desc": top_tags[:3],
            "thumbnail": "60% face reaction + bold 3-word text + high contrast. A/B test thumbnails.",
        },
        "posting_schedule": {
            "frequency": "2x/week minimum during growth. 1x/week for established channels.",
            "best_times": ["2–4 PM ET Thursday", "10 AM–12 PM ET Saturday"],
            "shorts": "Post 1 Short/day separately — Shorts algorithm is independent",
        },
        "monetization_path": [
            "1K subs + 4K watch hours → YouTube Partner Program (ads)",
            "Affiliate links in description from day 1",
            "Channel memberships at 30K subs",
            "Sponsored segments with brands at 50K+ subs",
            "Super Thanks + Super Chat during lives at any subscriber count",
        ],
    }


def _optimize_instagram(niche, hashtags, opportunities, followers) -> dict:
    top_tags = [h["hashtag"] for h in hashtags[:10]]
    niche_tags = [f"#{niche.lower().replace(' ', '')}", f"#{niche.lower()}gram", f"#{niche.lower()}community"]

    return {
        "platform": "Instagram",
        "niche": niche,
        "current_followers": followers,
        "bio_formula": "[What you do] for [who] | [Proof] | [CTA with link]",
        "bio_example": f"{niche.title()} content that converts | 📩 DM 'FREE' for our guide | 👇 Get the resource",
        "content_mix": {
            "reels": "40% — highest reach, prioritized by algorithm",
            "carousels": "35% — highest saves and shares, best for theme page growth",
            "static_posts": "15% — community posts, testimonials",
            "stories": "10% — daily engagement, polls, link stickers",
        },
        "content_pillars": [
            f"Value carousels: '10 {niche} tips most people ignore' (save-bait)",
            f"Reels: Trend audio + {niche} twist for reach",
            f"Social proof: Screenshots, before/afters, testimonials",
            f"Behind-the-scenes: How you create {niche} content",
            f"CTA posts: Drive to link in bio (freebie, product, email list)",
        ],
        "hashtag_strategy": {
            "total": "20–30 hashtags max",
            "mix": "5 mega (1M+) + 10 medium (100K–1M) + 10 small (10K–100K) + 3 branded",
            "niche_tags": niche_tags,
            "trending_tags": top_tags,
            "placement": "Put hashtags in first comment or at end of caption after dots",
        },
        "growth_tactics": [
            "Collab posts with accounts of similar size (shares both audiences)",
            "Comment on top accounts in niche within 30 min of their post",
            "Respond to every DM and comment in first hour",
            "Use 'Save this post' CTA — saves signal quality to algorithm",
            "Create a series (e.g., 'Monday motivation') for repeat visitors",
        ],
        "monetization_path": [
            "Affiliate links via link-in-bio tool (Linktree, Stan Store)",
            "Paid shoutouts/promotions to brands at 10K+ followers",
            "Digital products (guides, templates) via gumroad or Stan Store",
            "Instagram subscriptions for exclusive content",
            "Agency/coaching offers once niche authority established",
        ],
    }


def optimize_all_accounts(
    niches: dict[str, str],
    trending_hashtags: list[dict],
    trending_music: list[dict],
    opportunities: list[dict],
) -> dict[str, Any]:
    """
    Generate optimization plans for all your accounts at once.

    niches format: {"tiktok": "fitness", "youtube": "finance", "instagram": "fitness"}
    """
    plans = {}
    for platform, niche in niches.items():
        try:
            plans[platform] = optimize_account(
                platform=platform,
                niche=niche,
                trending_hashtags=trending_hashtags,
                trending_music=trending_music,
                opportunities=opportunities,
            )
        except ValueError as e:
            plans[platform] = {"error": str(e)}

    return {
        "accounts_optimized": list(plans.keys()),
        "plans": plans,
        "cross_platform_tip": (
            "Repurpose content across platforms: "
            "1) Record TikTok → 2) Upload to YouTube Shorts → 3) Post to Instagram Reels. "
            "Adjust aspect ratio and remove TikTok watermark before cross-posting."
        ),
        "weekly_content_calendar": _build_calendar(niches, trending_hashtags, trending_music),
    }


def _build_calendar(niches, hashtags, music) -> list[dict]:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    niche = next(iter(niches.values()), "your niche")
    top_sound = music[0]["title"] if music else "trending audio"
    top_tags = " ".join(h["hashtag"] for h in hashtags[:3])

    content_types = [
        f"Educational: '3 {niche} secrets no one talks about' — Carousel on IG, Reel on TikTok",
        f"Entertainment: Use '{top_sound}' audio + {niche} hook — TikTok + Reels",
        f"Tutorial: 'How to [specific {niche} goal] in 60 seconds' — Short + TikTok",
        f"Community: Poll or question about {niche} — Stories + TikTok comment bait",
        f"Social proof: Results post with before/after — IG carousel + TikTok duet",
        f"Trending take: Hot topic in {niche} this week — YouTube video + TikTok opinion",
        f"Repurpose: Clip best moment from week's content → Short/Reel/TikTok {top_tags}",
    ]

    return [{"day": day, "content": content} for day, content in zip(days, content_types)]
