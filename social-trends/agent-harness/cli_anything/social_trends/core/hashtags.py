"""Hashtag strategy engine.

Provides:
- Curated niche hashtag sets for 30+ content niches
- Mix strategy: broad + mid + niche + trending (optimal 3-5 per post)
- Hashtag scoring based on estimated competition vs reach
- Caption template generation with hashtag blocks
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


# ── Niche hashtag library ─────────────────────────────────────────────────────
# Each niche has 3 tiers: broad (high competition), mid, niche (low competition/high conversion)

NICHE_HASHTAGS: Dict[str, Dict[str, List[str]]] = {
    "fitness": {
        "broad":  ["fitness", "gym", "workout", "motivation", "health", "fitfam"],
        "mid":    ["strengthtraining", "homeworkout", "gymmotivation", "fitnessmotivation", "bodybuilding"],
        "niche":  ["glutes", "calisthenicdiet", "nattyorbottle", "legdayeveryday", "progresspics"],
    },
    "fashion": {
        "broad":  ["fashion", "style", "ootd", "outfit", "clothing"],
        "mid":    ["streetwear", "aestheticfashion", "vintagefit", "thriftedfit", "fashioninspo"],
        "niche":  ["darkacademia", "cottagecore", "menshighfashion", "effortlesschic", "parisianchic"],
    },
    "food": {
        "broad":  ["food", "foodie", "recipe", "cooking", "eat"],
        "mid":    ["homecooking", "mealprep", "healthyrecipes", "easyrecipes", "foodphotography"],
        "niche":  ["proteinfood", "highproteinmeals", "airfryerrecipes", "veganrecipes", "dairyfree"],
    },
    "travel": {
        "broad":  ["travel", "wanderlust", "explore", "adventure", "vacation"],
        "mid":    ["solotravel", "budgettravel", "traveltok", "travelgram", "travelreels"],
        "niche":  ["vanlife", "digitalnomad", "luxurytravel", "hiddengemtravel", "offthebeatenpath"],
    },
    "beauty": {
        "broad":  ["beauty", "makeup", "skincare", "glam", "cosmetics"],
        "mid":    ["skincareRoutine", "makeuptutorial", "drugstorebeauty", "cleanbeauty", "antiaging"],
        "niche":  ["glassskin", "slugging", "koreanbeauty", "oilyskin", "acneskincare"],
    },
    "finance": {
        "broad":  ["money", "finance", "investing", "wealth", "rich"],
        "mid":    ["personalfinance", "stockmarket", "sidehustle", "passiveincome", "budgeting"],
        "niche":  ["debtfreejourney", "frugalliving", "dividendinvesting", "indexfunds", "fireretirement"],
    },
    "gaming": {
        "broad":  ["gaming", "gamer", "games", "videogames", "twitch"],
        "mid":    ["fps", "rpg", "gamingcommunity", "gameclips", "streamclips"],
        "niche":  ["leagueoflegends", "valorantclips", "eldenpringtips", "speedrunning", "retrogaming"],
    },
    "motivation": {
        "broad":  ["motivation", "mindset", "success", "inspiration", "grind"],
        "mid":    ["selfimprovement", "dailymotivation", "entrepreneurmindset", "growthmindset", "hustle"],
        "niche":  ["stoicism", "discipline", "morningroutine", "highperformance", "mentalfitness"],
    },
    "pets": {
        "broad":  ["pets", "dog", "cat", "cute", "animals"],
        "mid":    ["dogsofinstagram", "catsoftiktok", "puppylove", "dogmom", "petlife"],
        "niche":  ["frenchbulldog", "bengalcat", "dogtraining", "rescuedog", "cottagedog"],
    },
    "crypto": {
        "broad":  ["crypto", "bitcoin", "nft", "blockchain", "web3"],
        "mid":    ["altcoins", "defi", "cryptotrading", "cryptonews", "ethereum"],
        "niche":  ["solana", "airdrop", "cryptogains", "onchain", "L2crypto"],
    },
    "business": {
        "broad":  ["business", "entrepreneur", "startup", "marketing", "brand"],
        "mid":    ["smallbusiness", "onlinebusiness", "digitalmarketing", "ecommerce", "dropshipping"],
        "niche":  ["amazonFBA", "etsy", "agencylife", "bizmodel", "scalingbusiness"],
    },
    "music": {
        "broad":  ["music", "artist", "song", "rap", "hiphop"],
        "mid":    ["newmusic", "indieartist", "unsigned", "producer", "musicproducer"],
        "niche":  ["lofi", "beatmaker", "soundcloud", "vocalcoach", "musictheory"],
    },
    "lifestyle": {
        "broad":  ["lifestyle", "life", "daily", "vlog", "dayinmylife"],
        "mid":    ["luxurylifestyle", "minimalism", "slowliving", "aestheticlifestyle", "contentcreator"],
        "niche":  ["softlife", "quietluxury", "darkfeminine", "richmom", "aestheticcore"],
    },
    "comedy": {
        "broad":  ["funny", "comedy", "lol", "humor", "meme"],
        "mid":    ["funnyvideos", "standup", "skits", "relatable", "comedytok"],
        "niche":  ["dryhumor", "darkcomedy", "adulthumor", "roast", "satirical"],
    },
    "art": {
        "broad":  ["art", "artist", "drawing", "painting", "creative"],
        "mid":    ["digitalart", "illustration", "procreate", "sketching", "artprocess"],
        "niche":  ["characterdesign", "conceptart", "abstractart", "handlettering", "pixelart"],
    },
    "education": {
        "broad":  ["education", "learn", "knowledge", "tips", "howto"],
        "mid":    ["learnontiktok", "didyouknow", "funfacts", "explainer", "edutok"],
        "niche":  ["science", "psychology", "history", "economics", "philosophy"],
    },
}

# Universal platform boosters
_PLATFORM_TAGS = {
    "tiktok":   ["fyp", "foryou", "foryoupage", "viral", "trending"],
    "instagram": ["reels", "explore", "instareels", "instadaily", "igtrend"],
    "youtube":  ["shorts", "youtubeshorts", "viral", "trending", "subscribe"],
    "all":      ["fyp", "viral", "trending", "explore"],
}


def get_hashtag_mix(
    niche: str,
    platform: str = "tiktok",
    count: int = 5,
    include_platform_boosters: bool = True,
) -> List[str]:
    """Return an optimized hashtag mix for a niche and platform.

    Strategy (per research): 3-5 hashtags, mix of broad/mid/niche.
    Platform boosters (fyp, viral) added if requested.
    """
    niche_lower = niche.lower()
    tags = NICHE_HASHTAGS.get(niche_lower, {})
    if not tags:
        # Best-effort fuzzy match
        for key in NICHE_HASHTAGS:
            if niche_lower in key or key in niche_lower:
                tags = NICHE_HASHTAGS[key]
                break

    broad = tags.get("broad", [])
    mid = tags.get("mid", [])
    niche_tags = tags.get("niche", [])
    boosters = _PLATFORM_TAGS.get(platform.lower(), _PLATFORM_TAGS["all"]) if include_platform_boosters else []

    # Build mix: broad + mid + niche, then inject boosters (replace tail if needed)
    mix: List[str] = []
    if broad:
        mix.append(broad[0])
    mix.extend(mid[:2])
    mix.extend(niche_tags[:2])

    # Deduplicate preserving order
    seen: set = set()
    result = []
    for tag in mix:
        if tag and tag not in seen:
            seen.add(tag)
            result.append(tag)

    if include_platform_boosters and boosters:
        # Ensure at least one booster is present; swap out the last niche tag if full
        booster = next((b for b in boosters if b not in seen), None)
        if booster:
            if len(result) >= count:
                result[-1] = booster
            else:
                result.append(booster)
                seen.add(booster)

    return result[:count]


def score_hashtag(tag: str) -> Dict[str, Any]:
    """Score a hashtag on competition and estimated reach (heuristic model).

    Returns a dict with competition (low/med/high), reach (low/med/high), score (1-10).
    """
    tag = tag.lstrip("#").lower()

    # Simple heuristic based on length and known patterns
    # Shorter, generic tags = high competition; specific = low competition
    length_score = min(len(tag) / 20, 1.0)  # longer = more specific

    generic_words = {"fyp", "viral", "trending", "food", "fitness", "love", "life", "motivation",
                     "fashion", "travel", "funny", "art", "music", "style", "beauty"}
    is_generic = tag in generic_words

    competition = "high" if is_generic or len(tag) <= 6 else ("med" if len(tag) <= 12 else "low")
    reach = "high" if is_generic else ("med" if len(tag) <= 12 else "low")

    # Ideal: low competition + med-high reach
    score_map = {
        ("high", "high"): 5, ("high", "med"): 4, ("high", "low"): 2,
        ("med", "high"): 8, ("med", "med"): 7, ("med", "low"): 5,
        ("low", "high"): 10, ("low", "med"): 8, ("low", "low"): 6,
    }
    score = score_map.get((competition, reach), 6)

    return {
        "tag": tag,
        "competition": competition,
        "reach": reach,
        "score": score,
        "recommendation": "use" if score >= 6 else "skip",
    }


def audit_hashtags(tags: List[str]) -> Dict[str, Any]:
    """Audit a list of hashtags and return recommendations."""
    scored = [score_hashtag(t) for t in tags]
    avg_score = sum(s["score"] for s in scored) / len(scored) if scored else 0

    issues = []
    if len(tags) > 5:
        issues.append("Too many hashtags (>5) — TikTok/IG algorithms may penalize spam")
    if len(tags) < 3:
        issues.append("Too few hashtags (<3) — add niche-specific tags to improve discovery")
    if all(score_hashtag(t)["competition"] == "high" for t in tags):
        issues.append("All hashtags are high-competition — mix in niche-specific tags for better reach")

    return {
        "tags": scored,
        "count": len(tags),
        "avg_score": round(avg_score, 1),
        "issues": issues,
        "overall": "good" if avg_score >= 6 and not issues else "needs improvement",
    }


def get_trending_hashtags_from_trends(trend_items: List[Dict]) -> List[str]:
    """Extract and rank hashtags from a list of TrendItem dicts."""
    from collections import Counter
    all_tags = [tag for item in trend_items for tag in item.get("hashtags", [])]
    return [tag for tag, _ in Counter(all_tags).most_common(20) if tag]


def list_niches() -> List[str]:
    return sorted(NICHE_HASHTAGS.keys())


def build_caption(text: str, hashtags: List[str], platform: str = "tiktok") -> str:
    """Build an optimized caption with hashtag block."""
    tag_str = " ".join(f"#{t.lstrip('#')}" for t in hashtags)
    if platform.lower() == "tiktok":
        # TikTok: hashtags inline at end
        return f"{text}\n\n{tag_str}"
    elif platform.lower() == "instagram":
        # IG Reels: hashtags in comment block style (trailing dot separator)
        return f"{text}\n.\n.\n.\n{tag_str}"
    else:
        return f"{text}\n\n{tag_str}"
