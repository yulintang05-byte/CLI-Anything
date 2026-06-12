"""Cross-platform hashtag analysis and strategy generator.

Provides:
  - Unified ranking across YouTube + TikTok
  - Niche-specific hashtag sets (small/medium/large buckets)
  - Hashtag set generation optimized per platform
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class RankedHashtag:
    tag: str
    score: float
    platforms: List[str]
    youtube_count: int
    tiktok_count: int
    total_reach: int
    bucket: str  # "mega", "large", "medium", "small", "niche"

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class HashtagSet:
    topic: str
    platform: str
    strategy: str
    tags: List[str]
    rationale: str

    def to_dict(self) -> Dict:
        return asdict(self)


# ── Niche hashtag dictionaries ────────────────────────────────────────────────
# Curated seed hashtags per niche — supplement with live scraped data.

NICHE_SEEDS: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "mega":   ["#fitness", "#workout", "#gym", "#health", "#fit"],
        "large":  ["#weightloss", "#bodybuilding", "#exercise", "#motivation", "#fitlife"],
        "medium": ["#homeworkout", "#strengthtraining", "#cardio", "#fitnessmotivation", "#gains"],
        "small":  ["#noexcuses", "#trainhard", "#sweateveryday", "#fitfam", "#personaltrainer"],
        "niche":  ["#calisthenics", "#hiitworkout", "#flexibilityday", "#plyometrics"],
    },
    "beauty": {
        "mega":   ["#beauty", "#makeup", "#skincare", "#fashion", "#style"],
        "large":  ["#glam", "#makeupartist", "#skincareroutine", "#ootd", "#cosmetics"],
        "medium": ["#makeuptutorial", "#grwm", "#glowup", "#naturalmakeup", "#skintok"],
        "small":  ["#drugstoremakeup", "#antiaging", "#acneskincare", "#glassskin"],
        "niche":  ["#skincareobsessed", "#k-beauty", "#minimalistmakeup", "#slugging"],
    },
    "food": {
        "mega":   ["#food", "#foodie", "#cooking", "#recipe", "#foodphotography"],
        "large":  ["#homecooking", "#foodlover", "#delicious", "#yummy", "#instafood"],
        "medium": ["#mealprep", "#easyrecipes", "#healthyeating", "#foodtok", "#whatieatinaday"],
        "small":  ["#veganrecipes", "#airfryer", "#onepotmeal", "#budgetmeals"],
        "niche":  ["#fermentation", "#cottagecore", "#darkfoodphotography", "#umami"],
    },
    "travel": {
        "mega":   ["#travel", "#wanderlust", "#explore", "#vacation", "#trip"],
        "large":  ["#travelgram", "#adventure", "#travelblogger", "#backpacking", "#travelphotography"],
        "medium": ["#solotravel", "#budgettravel", "#digitalnomad", "#travelcouple", "#roadtrip"],
        "small":  ["#hiddengem", "#offthebeatenpath", "#travelreels", "#vanlife"],
        "niche":  ["#slowtravel", "#workandtravel", "#traveltok", "#hotellife"],
    },
    "finance": {
        "mega":   ["#money", "#investing", "#finance", "#wealth", "#business"],
        "large":  ["#personalfinance", "#sidehustle", "#passiveincome", "#stockmarket", "#entrepreneur"],
        "medium": ["#financialliteracy", "#financetok", "#budgeting", "#frugal", "#crypto"],
        "small":  ["#debtfree", "#dividendinvesting", "#realestateinvesting", "#frugalliving"],
        "niche":  ["#coastfire", "#leanfire", "#creditcardhacks", "#valuesinvesting"],
    },
    "gaming": {
        "mega":   ["#gaming", "#gamer", "#game", "#videogames", "#twitch"],
        "large":  ["#gamingcommunity", "#pcgaming", "#xbox", "#playstation", "#nintendo"],
        "medium": ["#gamingmemes", "#gamingsetup", "#fps", "#rpg", "#esports"],
        "small":  ["#indiegames", "#retrogaming", "#gaminghighlights", "#gamedev"],
        "niche":  ["#soulslike", "#speedrun", "#leagueoflegends", "#valorant"],
    },
    "motivation": {
        "mega":   ["#motivation", "#mindset", "#success", "#hustle", "#inspiration"],
        "large":  ["#selfimprovement", "#growthmindset", "#positivevibes", "#goals", "#discipline"],
        "medium": ["#dailymotivation", "#mentalhealth", "#personaldevelopment", "#selflove", "#mindfulness"],
        "small":  ["#stoicism", "#morningroutine", "#atomichabits", "#journaling"],
        "niche":  ["#75hard", "#wakeupchallenge", "#coldshower", "#dopaminedetox"],
    },
    "fashion": {
        "mega":   ["#fashion", "#style", "#ootd", "#outfitoftheday", "#streetwear"],
        "large":  ["#fashionista", "#styletips", "#aesthetic", "#vintage", "#thrift"],
        "medium": ["#capsulewardrobe", "#fashiontok", "#outfitinspo", "#mensfashion", "#womensfashion"],
        "small":  ["#thriftflip", "#slowfashion", "#sustainablefashion", "#fashionhacks"],
        "niche":  ["#darkacademia", "#cottagecore", "#y2kfashion", "#coquette"],
    },
    "pets": {
        "mega":   ["#pets", "#dogs", "#cats", "#doglovers", "#catlover"],
        "large":  ["#dogsofinstagram", "#catsofinstagram", "#puppy", "#kitten", "#animallovers"],
        "medium": ["#dogtraining", "#rescuedog", "#adoptdontshop", "#pettok", "#petparents"],
        "small":  ["#goldenretriever", "#frenchbulldog", "#mainecoon", "#dogsofTikTok"],
        "niche":  ["#rawfeeding", "#dogagility", "#cattricks", "#exoticpets"],
    },
    "entrepreneurship": {
        "mega":   ["#entrepreneur", "#business", "#startup", "#success", "#money"],
        "large":  ["#businessowner", "#smallbusiness", "#marketing", "#ecommerce", "#dropshipping"],
        "medium": ["#shopify", "#amazonFBA", "#businesstips", "#branding", "#socialmediamarketing"],
        "small":  ["#solopreneur", "#bootstrapped", "#agencylife", "#saas", "#contentcreator"],
        "niche":  ["#ugccreator", "#facelessmarketing", "#printOnDemand", "#digitalproducts"],
    },
}

PLATFORM_LIMITS = {
    "youtube": 15,
    "tiktok": 30,
    "instagram": 30,
    "all": 30,
}

BUCKET_SIZES = {
    "mega":   (1_000_000_000, float("inf")),   # 1B+
    "large":  (100_000_000, 1_000_000_000),     # 100M–1B
    "medium": (10_000_000, 100_000_000),         # 10M–100M
    "small":  (1_000_000, 10_000_000),           # 1M–10M
    "niche":  (0, 1_000_000),                   # < 1M
}


def _assign_bucket(reach: int) -> str:
    for bucket, (lo, hi) in BUCKET_SIZES.items():
        if lo <= reach < hi:
            return bucket
    return "niche"


def merge_platform_hashtags(
    youtube_tags: List,
    tiktok_tags: List,
) -> List[RankedHashtag]:
    """Merge and rank hashtags from both platforms into a unified list."""
    yt_map: Dict[str, Dict] = {}
    for h in youtube_tags:
        clean = h.tag.lstrip("#").lower()
        yt_map[clean] = {"count": h.count, "reach": h.avg_views * h.count}

    tt_map: Dict[str, Dict] = {}
    for h in tiktok_tags:
        clean = h.tag.lstrip("#").lower()
        tt_map[clean] = {"count": h.video_count, "reach": h.view_count}

    all_tags = set(yt_map) | set(tt_map)
    ranked = []

    for tag in all_tags:
        yt = yt_map.get(tag, {"count": 0, "reach": 0})
        tt = tt_map.get(tag, {"count": 0, "reach": 0})

        platforms = []
        if tag in yt_map:
            platforms.append("youtube")
        if tag in tt_map:
            platforms.append("tiktok")

        total_reach = yt["reach"] + tt["reach"]
        score = total_reach / 1_000_000

        ranked.append(RankedHashtag(
            tag=f"#{tag}",
            score=round(score, 2),
            platforms=platforms,
            youtube_count=yt["count"],
            tiktok_count=tt["count"],
            total_reach=total_reach,
            bucket=_assign_bucket(total_reach),
        ))

    ranked.sort(key=lambda h: h.total_reach, reverse=True)
    return ranked


def generate_hashtag_set(
    topic: str,
    platform: str = "tiktok",
    strategy: str = "balanced",
    live_tags: Optional[List[RankedHashtag]] = None,
) -> HashtagSet:
    """Generate an optimized hashtag set for a given topic and platform.

    Args:
        topic: Niche/topic (e.g., "fitness", "beauty", "food", or any keyword)
        platform: Target platform — "youtube", "tiktok", "instagram", "all"
        strategy: "balanced" | "growth" | "niche" | "viral"
          balanced — mix of all bucket sizes (recommended)
          growth   — heavy on medium + small (avoid mega competition)
          niche    — prioritize niche + small (community building)
          viral    — heavy on mega + large (max reach, high competition)
        live_tags: Optional live-scraped tags to blend in

    Returns:
        HashtagSet with platform-optimized tag list and rationale.
    """
    limit = PLATFORM_LIMITS.get(platform, 30)
    niche_key = _match_niche(topic)
    seeds = NICHE_SEEDS.get(niche_key, _generic_seeds(topic))

    strategy_mix: Dict[str, int] = {
        "balanced": {"mega": 2, "large": 4, "medium": 5, "small": 5, "niche": 4},
        "growth":   {"mega": 1, "large": 2, "medium": 6, "small": 8, "niche": 3},
        "niche":    {"mega": 0, "large": 2, "medium": 4, "small": 8, "niche": 8},
        "viral":    {"mega": 5, "large": 8, "medium": 6, "small": 4, "niche": 2},
    }.get(strategy, {"mega": 2, "large": 4, "medium": 5, "small": 5, "niche": 4})

    selected: List[str] = []

    live_by_bucket: Dict[str, List[str]] = {}
    if live_tags:
        for lt in live_tags:
            live_by_bucket.setdefault(lt.bucket, []).append(lt.tag)

    for bucket, count in strategy_mix.items():
        live_pool = live_by_bucket.get(bucket, [])
        seed_pool = seeds.get(bucket, [])

        combined = list(dict.fromkeys(live_pool + seed_pool))
        selected.extend(combined[:count])
        if len(selected) >= limit:
            break

    selected = list(dict.fromkeys(selected))[:limit]

    rationale = (
        f"{strategy.title()} strategy for {platform}: "
        f"{strategy_mix.get('mega', 0)} mega + {strategy_mix.get('large', 0)} large + "
        f"{strategy_mix.get('medium', 0)} medium + {strategy_mix.get('small', 0)} small + "
        f"{strategy_mix.get('niche', 0)} niche hashtags. "
        f"Total: {len(selected)}/{limit} (platform max)."
    )

    return HashtagSet(
        topic=topic,
        platform=platform,
        strategy=strategy,
        tags=selected,
        rationale=rationale,
    )


def _match_niche(topic: str) -> str:
    """Fuzzy-match a topic string to a known niche key."""
    topic_lower = topic.lower()
    for key in NICHE_SEEDS:
        if key in topic_lower or topic_lower in key:
            return key
    keyword_map = {
        "gym": "fitness", "sport": "fitness", "exercise": "fitness",
        "makeup": "beauty", "skincare": "beauty", "glow": "beauty",
        "cook": "food", "recipe": "food", "eat": "food",
        "trip": "travel", "vacation": "travel", "explore": "travel",
        "invest": "finance", "stock": "finance", "crypto": "finance",
        "game": "gaming", "play": "gaming", "twitch": "gaming",
        "inspire": "motivation", "mindset": "motivation",
        "outfit": "fashion", "clothes": "fashion", "style": "fashion",
        "dog": "pets", "cat": "pets", "animal": "pets",
        "business": "entrepreneurship", "startup": "entrepreneurship",
    }
    for keyword, niche in keyword_map.items():
        if keyword in topic_lower:
            return niche
    return "__generic__"


def _generic_seeds(topic: str) -> Dict[str, List[str]]:
    """Generate generic hashtags when topic doesn't match a known niche."""
    base = re.sub(r"\W+", "", topic.lower())
    return {
        "mega":   ["#viral", "#trending", "#fyp", "#foryou"],
        "large":  [f"#{base}", f"#{base}tok", f"#{base}life", f"#{base}community"],
        "medium": [f"#{base}tips", f"#{base}content", f"#{base}creator"],
        "small":  [f"#{base}daily", f"#{base}journey", f"#{base}motivation"],
        "niche":  [f"#{base}niche", f"#{base}obsessed"],
    }


def get_niche_list() -> List[str]:
    """Return all supported niche keywords."""
    return sorted(NICHE_SEEDS.keys())
