"""Cross-platform hashtag strategy analyzer — generates optimized hashtag sets."""
import re
from typing import List, Dict, Any, Optional

# Curated hashtag pools by niche (research-backed, high engagement)
NICHE_HASHTAGS: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "mega":   ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#health"],
        "large":  ["#bodybuilding", "#cardio", "#weightloss", "#fitfam", "#gymlife"],
        "medium": ["#homeworkout", "#fitnessjourney", "#gains", "#fitnesstips", "#personaltrainer"],
        "niche":  ["#calisthenics", "#hiit", "#strengthtraining", "#fatloss", "#musclebuilding"],
    },
    "fashion": {
        "mega":   ["#fashion", "#style", "#ootd", "#outfit", "#streetwear"],
        "large":  ["#fashionista", "#styleinspo", "#aesthetic", "#wearit", "#lookbook"],
        "medium": ["#outfitoftheday", "#fashionblogger", "#trending", "#vibes", "#drip"],
        "niche":  ["#thriftflip", "#sustainable", "#minimalistfashion", "#grwm", "#fashionhacks"],
    },
    "business": {
        "mega":   ["#business", "#entrepreneur", "#money", "#success", "#motivation"],
        "large":  ["#hustleculture", "#mindset", "#marketing", "#smallbusiness", "#sidehustle"],
        "medium": ["#passiveincome", "#investing", "#startup", "#businesstips", "#grind"],
        "niche":  ["#dropshipping", "#ecommerce", "#digitalmarketing", "#smma", "#agencylife"],
    },
    "lifestyle": {
        "mega":   ["#lifestyle", "#life", "#happy", "#love", "#instagood"],
        "large":  ["#dailyvlog", "#livingmybest", "#selfcare", "#mindfulness", "#wellness"],
        "medium": ["#morningroutine", "#aesthetic", "#luxurylifestyle", "#travel", "#explore"],
        "niche":  ["#slowliving", "#digitalnomad", "#minimallife", "#contentcreator", "#influencer"],
    },
    "food": {
        "mega":   ["#food", "#foodie", "#cooking", "#recipe", "#yummy"],
        "large":  ["#homecooking", "#foodphotography", "#delicious", "#tasty", "#foodblogger"],
        "medium": ["#mealprep", "#healthyeating", "#dinner", "#lunch", "#breakfast"],
        "niche":  ["#plantbased", "#veganrecipes", "#keto", "#macros", "#cleaneating"],
    },
    "tech": {
        "mega":   ["#tech", "#technology", "#ai", "#software", "#coding"],
        "large":  ["#programming", "#developer", "#startup", "#innovation", "#gadgets"],
        "medium": ["#cybersecurity", "#machinelearning", "#webdev", "#python", "#javascript"],
        "niche":  ["#buildinpublic", "#saas", "#nocode", "#devlife", "#techbro"],
    },
    "themepage": {
        "mega":   ["#fyp", "#foryou", "#viral", "#trending", "#explore"],
        "large":  ["#contentcreator", "#themepage", "#niche", "#pagegrowth", "#organicgrowth"],
        "medium": ["#themepages", "#repost", "#curated", "#aestheticpage", "#nichecontent"],
        "niche":  ["#themepageowner", "#pagemonetization", "#growthstrategy", "#paidshoutout", "#spons"],
    },
    "general": {
        "mega":   ["#fyp", "#foryou", "#viral", "#trending", "#explore"],
        "large":  ["#reels", "#tiktok", "#instagram", "#youtube", "#content"],
        "medium": ["#contentcreator", "#creator", "#influencer", "#socialmedia", "#growth"],
        "niche":  ["#organicgrowth", "#engagement", "#community", "#collab", "#shoutout"],
    },
}

# Optimal hashtag counts per platform
PLATFORM_HASHTAG_RULES = {
    "tiktok":    {"optimal": 5,  "max": 7,  "min": 3,  "strategy": "mix 2 mega + 2 medium + 1 niche"},
    "instagram": {"optimal": 15, "max": 30, "min": 8,  "strategy": "mix 3 mega + 6 large + 4 medium + 2 niche"},
    "youtube":   {"optimal": 3,  "max": 5,  "min": 1,  "strategy": "1 broad + 1 niche + 1 trending in description"},
    "twitter":   {"optimal": 2,  "max": 3,  "min": 1,  "strategy": "1 trending + 1 niche"},
    "threads":   {"optimal": 3,  "max": 5,  "min": 1,  "strategy": "mix trending + niche"},
}


def build_hashtag_set(
    niche: str = "general",
    platform: str = "tiktok",
    trending: Optional[List[str]] = None,
    count: Optional[int] = None,
) -> Dict[str, Any]:
    """Build an optimized hashtag set for a given niche and platform."""
    niche_key = niche.lower().replace(" ", "")
    pool = NICHE_HASHTAGS.get(niche_key, NICHE_HASHTAGS["general"])
    rules = PLATFORM_HASHTAG_RULES.get(platform.lower(), PLATFORM_HASHTAG_RULES["tiktok"])

    target = count or rules["optimal"]

    # Build balanced mix
    mega   = pool["mega"][:2]
    large  = pool["large"][:2]
    medium = pool["medium"][:2]
    niche_ = pool["niche"][:1]
    trending_ = (trending or [])[:2]

    combined = list(dict.fromkeys(mega + large + medium + niche_ + trending_))
    final    = combined[:target]

    return {
        "platform":     platform,
        "niche":        niche,
        "hashtags":     final,
        "count":        len(final),
        "strategy":     rules["strategy"],
        "optimal_count": rules["optimal"],
        "max_count":    rules["max"],
        "breakdown": {
            "mega":     mega,
            "large":    large,
            "medium":   medium,
            "niche":    niche_,
            "trending": trending_,
        },
    }


def analyze_competitor_hashtags(urls_or_captions: List[str]) -> Dict[str, Any]:
    """Analyze hashtag patterns from competitor post captions/text."""
    all_tags: Dict[str, int] = {}
    for text in urls_or_captions:
        for tag in re.findall(r"#\w+", text):
            tag = tag.lower()
            all_tags[tag] = all_tags.get(tag, 0) + 1

    sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
    return {
        "top_tags": [{"hashtag": t, "frequency": f} for t, f in sorted_tags[:20]],
        "unique_count": len(all_tags),
        "total_analyzed": len(urls_or_captions),
        "recommendation": _hashtag_recommendation(sorted_tags),
    }


def generate_hashtag_calendar(niche: str, platforms: List[str], days: int = 7) -> List[Dict]:
    """Generate a hashtag rotation plan to avoid shadowbanning."""
    calendar = []
    for day in range(1, days + 1):
        day_tags = {}
        for platform in platforms:
            # Rotate niche tags daily to avoid repetition penalty
            pool = NICHE_HASHTAGS.get(niche.lower(), NICHE_HASHTAGS["general"])
            offset = (day - 1) % 3
            niche_tags = pool["niche"][offset:offset+2] + pool["medium"][:2] + pool["mega"][:2]
            day_tags[platform] = list(dict.fromkeys(niche_tags))[:PLATFORM_HASHTAG_RULES.get(platform.lower(), {}).get("optimal", 5)]
        calendar.append({"day": day, "tags": day_tags})
    return calendar


def cross_platform_trend_merge(yt_hashtags: List[Dict], tt_hashtags: List[Dict]) -> List[Dict]:
    """Find hashtags trending on BOTH YouTube and TikTok — highest priority."""
    yt_set = {h["hashtag"].lower().lstrip("#") for h in yt_hashtags}
    tt_set = {h["hashtag"].lower().lstrip("#") for h in tt_hashtags}
    overlap = yt_set & tt_set

    merged = []
    for h in tt_hashtags:
        name = h["hashtag"].lower().lstrip("#")
        if name in overlap:
            merged.append({**h, "cross_platform": True, "platforms": ["youtube", "tiktok"]})

    for h in yt_hashtags:
        name = h["hashtag"].lower().lstrip("#")
        if name not in overlap:
            merged.append({**h, "cross_platform": False, "platforms": ["youtube"]})

    for h in tt_hashtags:
        name = h["hashtag"].lower().lstrip("#")
        if name not in overlap:
            merged.append({**h, "cross_platform": False, "platforms": ["tiktok"]})

    return sorted(merged, key=lambda x: (x["cross_platform"], x.get("frequency", 0)), reverse=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _hashtag_recommendation(sorted_tags: List) -> str:
    if not sorted_tags:
        return "No hashtag data to analyze."
    top = sorted_tags[:3]
    names = [t[0] for t in top]
    return (
        f"High-frequency tags detected: {', '.join(names)}. "
        "Mix these with 2-3 niche-specific tags for best reach-to-engagement ratio."
    )
