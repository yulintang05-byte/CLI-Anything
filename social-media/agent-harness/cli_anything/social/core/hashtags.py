"""
Hashtag research and strategy engine.

Strategy rules based on publicly available creator best-practices:
  - Mix of high (>1M posts), mid (100K-1M), and micro (<100K) tags
  - Platform limits: TikTok 3-5 relevant tags; Instagram 5-15; YouTube 3-8
  - Always include 1-2 brand/niche-specific tags
"""
from typing import Dict, List, Optional

# Curated seed hashtag banks by niche — updated from creator economy research (2024-2025)
NICHE_HASHTAG_BANKS: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "mega":  ["#fitness", "#workout", "#gym", "#health", "#motivation"],
        "mid":   ["#fitlife", "#gymlife", "#workoutmotivation", "#fitnessmotivation", "#bodybuilding", "#personaltrainer", "#fitfam"],
        "micro": ["#homeworkout", "#calisthenics", "#functionaltraining", "#strengthcoach", "#macros", "#preworkout"],
        "viral": ["#75hard", "#gymtok", "#workouttok", "#fitnesstok", "#trainwithme"],
    },
    "food": {
        "mega":  ["#food", "#foodie", "#cooking", "#recipe", "#foodphotography"],
        "mid":   ["#foodlover", "#homecooking", "#easyrecipes", "#mealprep", "#foodblogger", "#tasty", "#yummy"],
        "micro": ["#whatieatinaday", "#cookingathome", "#quickrecipes", "#budgetmeals", "#plantbased"],
        "viral": ["#foodtok", "#cookingtok", "#recipetok", "#mukbang", "#asmrfood"],
    },
    "fashion": {
        "mega":  ["#fashion", "#style", "#ootd", "#clothing", "#streetwear"],
        "mid":   ["#fashionista", "#styleinspiration", "#fashionblogger", "#outfitinspo", "#streetstyle"],
        "micro": ["#thrifted", "#sustainablefashion", "#capsulewardrobe", "#vintagefit", "#outfitcheck"],
        "viral": ["#fashiontok", "#ootdtok", "#styletok", "#grwm", "#outfitoftheday"],
    },
    "beauty": {
        "mega":  ["#beauty", "#makeup", "#skincare", "#nails", "#hair"],
        "mid":   ["#beautytips", "#makeupartist", "#makeuptutorial", "#skincareroutine", "#glam"],
        "micro": ["#skincareobsessed", "#cleanbeauty", "#minimialistmakeup", "#slugging", "#skinbarrier"],
        "viral": ["#beautytok", "#makeuptok", "#grwm", "#glowup", "#nofilter"],
    },
    "finance": {
        "mega":  ["#money", "#investing", "#finance", "#crypto", "#realestate"],
        "mid":   ["#personalfinance", "#financetips", "#stockmarket", "#wealthbuilding", "#passiveincome"],
        "micro": ["#debtfree", "#financialfreedom", "#budgeting101", "#sidehustle", "#frugalliving"],
        "viral": ["#moneytok", "#financetok", "#stocktok", "#richtok", "#howtogetrich"],
    },
    "travel": {
        "mega":  ["#travel", "#wanderlust", "#explore", "#adventure", "#vacation"],
        "mid":   ["#travelblogger", "#travelgram", "#travellife", "#travelphotography", "#roadtrip"],
        "micro": ["#solotravel", "#budgettravel", "#digitalnomaad", "#hiddengems", "#vanlife"],
        "viral": ["#traveltok", "#exploretok", "#travelhacks", "#placestovisit", "#travelcheck"],
    },
    "gaming": {
        "mega":  ["#gaming", "#gamer", "#videogames", "#twitch", "#esports"],
        "mid":   ["#gamingtok", "#gamingcommunity", "#pcgaming", "#consolegaming", "#streamer"],
        "micro": ["#indiegames", "#gamingsetup", "#gamingroom", "#fps", "#rpg"],
        "viral": ["#gamingtok", "#gamertok", "#twitchstreamer", "#fyp", "#trending"],
    },
    "motivation": {
        "mega":  ["#motivation", "#success", "#mindset", "#goals", "#hustle"],
        "mid":   ["#motivationalquotes", "#entrepreneurship", "#grindset", "#selfimprovement", "#personaldevelopment"],
        "micro": ["#mindsetshift", "#morningroutine", "#dailydiscipline", "#highperformance", "#growthmindset"],
        "viral": ["#motivationtok", "#successtok", "#entrepreneur", "#ceolife", "#buildingmyempire"],
    },
    "pets": {
        "mega":  ["#pets", "#dogs", "#cats", "#animals", "#dogsofinstagram"],
        "mid":   ["#puppy", "#kitten", "#petlover", "#doglife", "#catlover"],
        "micro": ["#adoptdontshop", "#rescuedog", "#dogtraining", "#catmom", "#petcare"],
        "viral": ["#pettok", "#dogtok", "#cattok", "#animaltok", "#petsoftiktok"],
    },
    "business": {
        "mega":  ["#business", "#entrepreneur", "#startup", "#marketing", "#ecommerce"],
        "mid":   ["#smallbusiness", "#businesstips", "#onlinebusiness", "#dropshipping", "#digitalmarketing"],
        "micro": ["#businessowner", "#ecomtips", "#shopify", "#agencylife", "#contentcreator"],
        "viral": ["#businesstok", "#entrepreneurtok", "#dropshippingtips", "#makemoneyonline", "#sidehustleideas"],
    },
}

UNIVERSAL_VIRAL_TAGS = ["#fyp", "#foryou", "#foryoupage", "#trending", "#viral"]

PLATFORM_LIMITS = {
    "tiktok":    {"max": 5,  "ideal": "3-5",  "note": "Use 3-5 highly relevant tags; avoid hashtag stuffing"},
    "instagram": {"max": 30, "ideal": "5-15", "note": "Mix mega, mid, and micro; 5-15 performs best post-2022"},
    "youtube":   {"max": 15, "ideal": "3-8",  "note": "YouTube tags are less visible but help recommendation"},
    "twitter":   {"max": 2,  "ideal": "1-2",  "note": "1-2 trending tags maximum; overuse hurts reach"},
}


def research_hashtags(
    niche: str,
    platform: str = "tiktok",
    include_viral: bool = True,
    limit: int = 30,
) -> Dict:
    """Return a structured hashtag strategy for a niche and platform."""
    niche_key = niche.lower().strip()
    bank = NICHE_HASHTAG_BANKS.get(niche_key)

    if bank:
        mega  = bank.get("mega", [])
        mid   = bank.get("mid", [])
        micro = bank.get("micro", [])
        viral = bank.get("viral", [])
    else:
        # Unknown niche — generate generic strategy
        mega  = [f"#{niche_key}", f"#{niche_key}tips", f"#{niche_key}life"]
        mid   = [f"#{niche_key}community", f"#{niche_key}lover", f"#{niche_key}content"]
        micro = [f"#{niche_key}creator", f"#{niche_key}tok", f"#{niche_key}daily"]
        viral = [f"#{niche_key}tok", f"#{niche_key}tiktok"]

    plat_cfg = PLATFORM_LIMITS.get(platform.lower(), PLATFORM_LIMITS["tiktok"])
    max_tags = plat_cfg["max"]

    # Build recommended set respecting platform limits
    recommended: List[str] = []
    # 1 mega + 2 mid + 1 micro + 1 viral for TikTok (3-5 total)
    # 3 mega + 5 mid + 4 micro + 3 viral for Instagram (15 total)
    if platform.lower() == "tiktok":
        mix = (mega[:1] + mid[:2] + micro[:1] + viral[:1])[:max_tags]
    elif platform.lower() == "instagram":
        mix = (mega[:3] + mid[:5] + micro[:4] + viral[:3])[:max_tags]
    elif platform.lower() == "youtube":
        mix = (mega[:2] + mid[:3] + micro[:2] + viral[:1])[:max_tags]
    else:
        mix = (mega[:1] + mid[:2] + micro[:1])[:max_tags]

    recommended = mix
    if include_viral and platform.lower() == "tiktok":
        # Append #fyp separately as a universal booster
        recommended = list(dict.fromkeys(recommended + ["#fyp"]))[:max_tags + 1]

    all_tags = mega + mid + micro + viral
    if include_viral:
        all_tags += UNIVERSAL_VIRAL_TAGS

    return {
        "niche":        niche,
        "platform":     platform,
        "strategy": {
            "mega_tags":  mega,
            "mid_tags":   mid,
            "micro_tags": micro,
            "viral_tags": viral,
        },
        "recommended":  recommended,
        "all_tags":     list(dict.fromkeys(all_tags))[:limit],
        "platform_rules": plat_cfg,
        "tips": _hashtag_tips(platform.lower()),
    }


def _hashtag_tips(platform: str) -> List[str]:
    shared = [
        "Research competitors in your niche and note which hashtags they use on viral posts.",
        "Rotate hashtag sets every 2-3 weeks to reach new audiences and avoid shadowbans.",
        "Use niche-specific tags to reach engaged communities, not just mass audiences.",
    ]
    specific = {
        "tiktok": [
            "TikTok's algorithm prioritizes video quality and watch time over hashtags.",
            "Using #fyp or #foryou does NOT guarantee FYP placement — TikTok has confirmed this.",
            "Focus on 3 highly relevant hashtags rather than stuffing 10+ irrelevant ones.",
            "Check TikTok Creative Center (ads.tiktok.com) for real-time trending hashtags.",
        ],
        "instagram": [
            "Instagram recommends 3-5 tags in Reels captions, but 10-15 still works for feed posts.",
            "Avoid banned hashtags — they can suppress your entire post's reach.",
            "Story hashtags reach a different audience than feed post hashtags.",
            "Use 'Recent' tab to verify hashtags are active, not dead/shadowbanned.",
        ],
        "youtube": [
            "YouTube shows only the first 3 tags publicly under video titles.",
            "Tags matter less than title, thumbnail, and description for YouTube SEO.",
            "Use TubeBuddy or VidIQ to find high-traffic, low-competition tags.",
            "Include your niche keyword as the first tag.",
        ],
    }
    return shared + specific.get(platform, [])


def score_hashtag(tag: str) -> Dict:
    """Estimate a hashtag's strategic value (heuristic scoring)."""
    tag = tag.lstrip("#").lower()
    length_score = 10 - min(len(tag), 10)
    specificity = "broad" if len(tag) <= 6 else ("mid" if len(tag) <= 12 else "niche")
    return {
        "hashtag":     f"#{tag}",
        "length":      len(tag),
        "specificity": specificity,
        "length_score": length_score,
        "recommendation": (
            "Too generic — high competition, low conversion" if len(tag) <= 4
            else "Good balance of reach and targeting" if len(tag) <= 12
            else "Very niche — low volume but high engagement rate"
        ),
    }


def available_niches() -> List[str]:
    return sorted(NICHE_HASHTAG_BANKS.keys())
