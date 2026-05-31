"""Account optimization analysis and scoring."""

from typing import Any, Dict, List, Optional


# Platform-specific optimization checklists
OPTIMIZATION_CHECKLIST: Dict[str, List[Dict[str, str]]] = {
    "tiktok": [
        {"item": "Profile picture", "detail": "Clear, high-res, on-brand (400×400 min)", "priority": "high"},
        {"item": "Display name", "detail": "Contains niche keyword + memorable brand word", "priority": "high"},
        {"item": "Bio", "detail": "80 chars max: who you are + value prop + CTA (link in bio)", "priority": "high"},
        {"item": "Link in bio", "detail": "Landing page, Linktree, or storefront URL set", "priority": "high"},
        {"item": "Email in bio", "detail": "Business email for brand deal inquiries", "priority": "medium"},
        {"item": "Pinned videos", "detail": "3 best-performing or on-brand videos pinned", "priority": "medium"},
        {"item": "Consistent posting", "detail": "Post 1-3× daily during peak hours", "priority": "high"},
        {"item": "Niche focus", "detail": "Every video stays within 1-2 core niches", "priority": "high"},
        {"item": "Hook in first 2s", "detail": "Open with a scroll-stopping statement or visual", "priority": "high"},
        {"item": "Captions/subtitles", "detail": "Auto-caption all videos for accessibility + reach", "priority": "medium"},
        {"item": "Sound strategy", "detail": "Use trending sounds (<7 days old) or viral originals", "priority": "high"},
        {"item": "Hashtag mix", "detail": "3-5 niche + 2-3 broad + 1-2 trending per post", "priority": "medium"},
        {"item": "Duet/Stitch enabled", "detail": "Allow Duet & Stitch to boost organic reach", "priority": "low"},
        {"item": "Creator account", "detail": "Switch to Creator account for analytics + tools", "priority": "high"},
        {"item": "TikTok LIVE", "detail": "Go live 2-3× per week to boost algorithmic push", "priority": "medium"},
    ],
    "youtube": [
        {"item": "Channel art", "detail": "2560×1440px banner with channel value prop", "priority": "high"},
        {"item": "Profile picture", "detail": "800×800px, visible at small sizes", "priority": "high"},
        {"item": "Channel description", "detail": "First 100 chars appear in search — niche + keywords", "priority": "high"},
        {"item": "Channel trailer", "detail": "60-90s trailer targeting non-subscribers", "priority": "high"},
        {"item": "Featured channels", "detail": "Add 5-10 relevant channels for social proof", "priority": "low"},
        {"item": "Sections / playlists", "detail": "Organize content into 3-5 thematic playlists", "priority": "medium"},
        {"item": "Custom URL", "detail": "Claim youtube.com/@yourchannel handle", "priority": "high"},
        {"item": "Custom thumbnails", "detail": "Bold text + contrasting colors + face (30% CTR lift)", "priority": "high"},
        {"item": "Title SEO", "detail": "Include primary keyword in first 40 chars of title", "priority": "high"},
        {"item": "Description SEO", "detail": "500+ word description with keywords + timestamps", "priority": "medium"},
        {"item": "Tags", "detail": "15-20 tags: exact match, broad, long-tail, channel name", "priority": "medium"},
        {"item": "End screens", "detail": "Add subscribe button + suggested video in last 20s", "priority": "medium"},
        {"item": "Cards", "detail": "Add 2-5 cards linking to related content mid-video", "priority": "low"},
        {"item": "Community posts", "detail": "Post 2-3× weekly to keep subscribers engaged", "priority": "medium"},
        {"item": "Chapters", "detail": "Add timestamp chapters for watchtime + SEO", "priority": "medium"},
    ],
    "instagram": [
        {"item": "Profile picture", "detail": "110px circle — logo or face, no text", "priority": "high"},
        {"item": "Bio", "detail": "150 chars: niche + hook + CTA. Use line breaks.", "priority": "high"},
        {"item": "Name field", "detail": "Include searchable keyword (e.g., 'Fitness Coach')", "priority": "high"},
        {"item": "Link in bio", "detail": "Use Linktree or direct link to landing page", "priority": "high"},
        {"item": "Story Highlights", "detail": "5-7 branded Highlights with custom covers", "priority": "high"},
        {"item": "Content grid", "detail": "Cohesive visual theme / color palette across posts", "priority": "high"},
        {"item": "Reels strategy", "detail": "Post 4-7 Reels per week for primary reach", "priority": "high"},
        {"item": "Hashtag strategy", "detail": "5-10 niche hashtags (avoid banned/oversaturated)", "priority": "medium"},
        {"item": "Alt text", "detail": "Add alt text to posts for accessibility + SEO", "priority": "low"},
        {"item": "Creator Studio", "detail": "Use Creator/Professional account for analytics", "priority": "medium"},
    ],
    "twitter": [
        {"item": "Header image", "detail": "1500×500px — show what you do / brand tagline", "priority": "high"},
        {"item": "Profile picture", "detail": "400×400px face or logo", "priority": "high"},
        {"item": "Bio", "detail": "160 chars — keywords + personality + link signal", "priority": "high"},
        {"item": "Pinned tweet", "detail": "Pin your best thread or offer for new visitors", "priority": "high"},
        {"item": "Posting cadence", "detail": "5-10 tweets + 1-3 threads per week", "priority": "high"},
        {"item": "Thread strategy", "detail": "Long-form threads drive follows more than single tweets", "priority": "high"},
        {"item": "Reply strategy", "detail": "Reply to 10+ accounts in niche daily for visibility", "priority": "medium"},
    ],
    "facebook": [
        {"item": "Page cover photo", "detail": "820×312px with value prop visible on mobile", "priority": "high"},
        {"item": "Page username", "detail": "Custom @username matching your brand handle", "priority": "high"},
        {"item": "About section", "detail": "Fill all fields — hours, website, category, story", "priority": "medium"},
        {"item": "CTA button", "detail": "Set 'Follow', 'Shop Now', or 'Sign Up' button", "priority": "high"},
        {"item": "Reels on Facebook", "detail": "Cross-post Instagram/TikTok Reels to FB Reels", "priority": "high"},
        {"item": "Facebook Groups", "detail": "Create or join 2-3 niche groups for community", "priority": "medium"},
    ],
}


def optimize_account(platform: str, niche: Optional[str] = None) -> Dict[str, Any]:
    """Generate optimization checklist and score for a platform account."""
    platform = platform.lower()
    checklist = OPTIMIZATION_CHECKLIST.get(platform)
    if not checklist:
        raise ValueError(f"No optimization data for platform '{platform}'.")

    high = [i for i in checklist if i["priority"] == "high"]
    medium = [i for i in checklist if i["priority"] == "medium"]
    low = [i for i in checklist if i["priority"] == "low"]

    niche_tips = _niche_specific_tips(platform, niche) if niche else []

    return {
        "platform": platform,
        "niche": niche or "general",
        "total_items": len(checklist),
        "high_priority": high,
        "medium_priority": medium,
        "low_priority": low,
        "niche_specific_tips": niche_tips,
        "quick_wins": [i for i in high[:5]],
    }


def _niche_specific_tips(platform: str, niche: str) -> List[Dict[str, str]]:
    tips: Dict[str, Dict[str, List]] = {
        "tiktok": {
            "fitness": [
                {"tip": "Post workout transformation content — highest engagement in niche"},
                {"tip": "Use POV format: 'POV: you started working out 30 days ago'"},
                {"tip": "Film in gym with natural lighting — avoid dark, low-quality clips"},
                {"tip": "Top sounds: upbeat EDM, hip-hop instrumentals for workout clips"},
            ],
            "food": [
                {"tip": "ASMR cooking sounds drive 3× more saves than music overlay"},
                {"tip": "Recipe videos under 60s outperform longer tutorials"},
                {"tip": "Always show the final dish in the first 1s (thumbnail moment)"},
                {"tip": "Use text overlays for ingredients — boosts completion rate"},
            ],
            "gaming": [
                {"tip": "Clip highlights under 30s — not full gameplay"},
                {"tip": "Reaction face-cam adds 40% more engagement for gaming content"},
                {"tip": "Trending game moments within 24h of release get massive reach"},
            ],
            "finance": [
                {"tip": "Hook: 'I made $X doing Y' or 'This $10 investment changed my life'"},
                {"tip": "Use split-screen: talking head + screen recording of charts"},
                {"tip": "Disclaimer in bio required by TikTok for financial content"},
            ],
        },
        "youtube": {
            "fitness": [
                {"tip": "Full workout videos (20-45 min) dominate YouTube fitness"},
                {"tip": "Thumbnail: before/after or impressive physique + bold text"},
                {"tip": "SEO: target 'X workout for beginners' long-tail keywords"},
            ],
            "gaming": [
                {"tip": "First 24h views determine YouTube Shorts viral velocity"},
                {"tip": "Reaction + commentary drives higher watch time than gameplay only"},
                {"tip": "SEO: include game name + patch version in title"},
            ],
        },
    }

    platform_tips = tips.get(platform, {})
    return platform_tips.get(niche.lower(), [{"tip": f"Create authentic {niche} content consistently"}])


def audit_all_accounts(accounts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Run optimization audit across all tracked accounts."""
    results = []
    for acc in accounts:
        try:
            audit = optimize_account(acc["platform"], acc.get("niche"))
            results.append({
                "handle": acc["handle"],
                "platform": acc["platform"],
                "niche": acc.get("niche", "general"),
                "high_priority_count": len(audit["high_priority"]),
                "quick_wins": audit["quick_wins"],
                "niche_tips_count": len(audit["niche_specific_tips"]),
            })
        except Exception as e:
            results.append({"handle": acc["handle"], "platform": acc["platform"], "error": str(e)})
    return results
