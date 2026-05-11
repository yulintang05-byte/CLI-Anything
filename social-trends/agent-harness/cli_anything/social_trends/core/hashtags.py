"""Cross-platform hashtag analysis and recommendation engine.

Merges signals from YouTube and TikTok to produce ranked, deduplicated
hashtag recommendations with context about reach and best-fit platforms.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Niche → seed hashtag catalogue
# ──────────────────────────────────────────────────────────────────────────────

NICHE_HASHTAGS: Dict[str, Dict[str, Any]] = {
    "fitness": {
        "core": ["#fitness", "#gym", "#workout", "#fitnessmotivation", "#bodybuilding",
                 "#gains", "#personaltrainer", "#cardio", "#weightloss", "#health"],
        "tiktok": ["#fitnessmotivation", "#gymmotivation", "#fitcheck", "#gymtok", "#sweatyselfie"],
        "youtube": ["#fitness", "#workout", "#gym", "#homeworkout", "#fitnesstips"],
        "niche": ["#calisthenics", "#hiit", "#strengthtraining", "#crossfit", "#pilates"],
    },
    "food": {
        "core": ["#food", "#foodie", "#foodporn", "#recipe", "#cooking", "#homecooking",
                 "#foodlover", "#delicious", "#tasty", "#yummy"],
        "tiktok": ["#foodtok", "#cookingtiktok", "#easyrecipe", "#whatieatinaday", "#mukbang"],
        "youtube": ["#cooking", "#recipe", "#foodie", "#easyrecipes", "#healthyfood"],
        "niche": ["#veganrecipes", "#mealprep", "#airfryer", "#quickrecipes", "#dessert"],
    },
    "fashion": {
        "core": ["#fashion", "#style", "#ootd", "#outfitoftheday", "#streetstyle",
                 "#fashionista", "#fashionblogger", "#outfit", "#aesthetic", "#lookbook"],
        "tiktok": ["#fashiontok", "#outfitinspo", "#ootd", "#styletips", "#fashioncheck"],
        "youtube": ["#fashion", "#style", "#haul", "#lookbook", "#fashionadvice"],
        "niche": ["#thrifted", "#vintagefashion", "#minimalstyle", "#streetwear", "#luxury"],
    },
    "beauty": {
        "core": ["#beauty", "#makeup", "#skincare", "#beautytips", "#makeuptutorial",
                 "#glam", "#selfcare", "#skincareroutine", "#glow", "#mua"],
        "tiktok": ["#beautytok", "#makeuphacks", "#skincaretok", "#grwm", "#makeupcheck"],
        "youtube": ["#makeup", "#beauty", "#skincare", "#grwm", "#makeuptutorial"],
        "niche": ["#cleanbeauty", "#kbeauty", "#drugstoremakeup", "#acneskin", "#antiaging"],
    },
    "gaming": {
        "core": ["#gaming", "#gamer", "#games", "#videogames", "#gamingcommunity",
                 "#gameplay", "#esports", "#pc", "#console", "#twitch"],
        "tiktok": ["#gamingtiktok", "#gamertok", "#gamingnews", "#fps", "#mobilegaming"],
        "youtube": ["#gaming", "#gameplay", "#gamingchannel", "#letsplay", "#gamereviews"],
        "niche": ["#minecraft", "#fortnite", "#roblox", "#valorant", "#codmobile"],
    },
    "finance": {
        "core": ["#money", "#finance", "#investing", "#wealth", "#financetips",
                 "#personalfinance", "#passiveincome", "#stockmarket", "#crypto", "#budget"],
        "tiktok": ["#financetok", "#moneytok", "#stocktok", "#investingtips", "#fintok"],
        "youtube": ["#personalfinance", "#investing", "#stocks", "#crypto", "#passiveincome"],
        "niche": ["#dividends", "#realestateinvesting", "#sidehustle", "#frugal", "#debtfree"],
    },
    "travel": {
        "core": ["#travel", "#travelphotography", "#wanderlust", "#travelgram", "#explore",
                 "#adventure", "#vacation", "#traveling", "#worldtravel", "#tourism"],
        "tiktok": ["#traveltok", "#travelwithme", "#travelcheck", "#budgettravel", "#solo"],
        "youtube": ["#travel", "#vlog", "#travelguide", "#budgettravel", "#travelwithme"],
        "niche": ["#digitalnomad", "#backpacking", "#luxurytravel", "#roadtrip", "#solotravel"],
    },
    "motivation": {
        "core": ["#motivation", "#success", "#mindset", "#inspiration", "#hustle",
                 "#entrepreneur", "#selfimprovement", "#growth", "#goals", "#grindset"],
        "tiktok": ["#motivationtok", "#mindsetcheck", "#growthmindset", "#successquotes", "#dailymotivation"],
        "youtube": ["#motivation", "#success", "#entrepreneur", "#selfhelp", "#mindset"],
        "niche": ["#stoicism", "#discipline", "#morningroutine", "#productivity", "#manifestation"],
    },
    "pets": {
        "core": ["#pets", "#dog", "#cat", "#animals", "#cute", "#petsofinstagram",
                 "#dogsoftiktok", "#catsoftiktok", "#petlover", "#animallover"],
        "tiktok": ["#dogtok", "#cattok", "#pettok", "#funnypets", "#petcheck"],
        "youtube": ["#pets", "#dogs", "#cats", "#animals", "#petcare"],
        "niche": ["#puppytraining", "#rescuedog", "#catbehavior", "#exoticpets", "#aquarium"],
    },
    "tech": {
        "core": ["#tech", "#technology", "#ai", "#coding", "#programming",
                 "#gadgets", "#software", "#developer", "#innovation", "#startup"],
        "tiktok": ["#techtok", "#codingtok", "#techreview", "#ai", "#programming"],
        "youtube": ["#tech", "#technology", "#review", "#unboxing", "#coding"],
        "niche": ["#machinelearning", "#cybersecurity", "#webdev", "#python", "#openai"],
    },
}

# Universal high-reach tags to append to any niche strategy
_UNIVERSAL_TAGS = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]

# ──────────────────────────────────────────────────────────────────────────────
# Merge & rank
# ──────────────────────────────────────────────────────────────────────────────

def _normalise(tag: str) -> str:
    """Lowercase, strip surrounding whitespace and leading #, re-add #."""
    return "#" + tag.strip().lstrip("#").lower().strip()


def merge_hashtags(
    yt_hashtags: List[Dict],
    tt_hashtags: List[Dict],
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Merge YouTube and TikTok hashtag lists, dedup, and rank by combined signal."""
    scores: Dict[str, Dict[str, Any]] = {}

    for i, h in enumerate(yt_hashtags):
        tag = _normalise(h.get("hashtag", ""))
        if not tag or tag == "#":
            continue
        entry = scores.setdefault(tag, {"hashtag": tag, "yt_rank": None, "tt_rank": None,
                                        "yt_views": 0, "tt_views": 0, "platforms": []})
        entry["yt_rank"] = i + 1
        entry["yt_views"] = h.get("view_count", 0) or 0
        if "youtube" not in entry["platforms"]:
            entry["platforms"].append("youtube")

    for i, h in enumerate(tt_hashtags):
        tag = _normalise(h.get("hashtag", ""))
        if not tag or tag == "#":
            continue
        entry = scores.setdefault(tag, {"hashtag": tag, "yt_rank": None, "tt_rank": None,
                                        "yt_views": 0, "tt_views": 0, "platforms": []})
        entry["tt_rank"] = i + 1
        entry["tt_views"] = h.get("view_count", 0) or 0
        if "tiktok" not in entry["platforms"]:
            entry["platforms"].append("tiktok")

    def _score(e: Dict) -> float:
        s = 0.0
        if e["yt_rank"] is not None:
            s += 1.0 / e["yt_rank"]
        if e["tt_rank"] is not None:
            s += 1.5 / e["tt_rank"]  # TikTok weighted higher for virality
        s += e["tt_views"] / 1e10
        return s

    ranked = sorted(scores.values(), key=_score, reverse=True)[:limit]
    for i, entry in enumerate(ranked):
        entry["rank"] = i + 1
        entry["cross_platform"] = len(entry["platforms"]) > 1
    return ranked


def recommend_hashtags(
    niche: str,
    platform: str = "all",
    limit: int = 30,
    include_universal: bool = True,
) -> Dict[str, Any]:
    """Return a ranked hashtag recommendation pack for a niche + platform."""
    niche_key = niche.lower().strip()
    catalogue = NICHE_HASHTAGS.get(niche_key)

    if catalogue is None:
        available = list(NICHE_HASHTAGS.keys())
        raise ValueError(f"Unknown niche '{niche}'. Available: {available}")

    plat = platform.lower()
    seen: set = set()
    tags: List[Dict] = []

    def _add(tag_list: List[str], source: str, weight: int) -> None:
        for raw in tag_list:
            tag = _normalise(raw)
            if tag not in seen:
                seen.add(tag)
                tags.append({"hashtag": tag, "source": source, "weight": weight})

    # Core tags always included
    _add(catalogue["core"], "core", 10)

    if plat in ("tiktok", "all"):
        _add(catalogue.get("tiktok", []), "tiktok-specific", 9)
    if plat in ("youtube", "all"):
        _add(catalogue.get("youtube", []), "youtube-specific", 8)

    _add(catalogue.get("niche", []), "niche-deep", 7)

    if include_universal and plat in ("tiktok", "all"):
        _add(_UNIVERSAL_TAGS, "universal-viral", 6)

    tags_sorted = sorted(tags, key=lambda t: t["weight"], reverse=True)[:limit]
    for i, t in enumerate(tags_sorted):
        t["rank"] = i + 1

    return {
        "niche": niche_key,
        "platform": plat,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(tags_sorted),
        "hashtags": tags_sorted,
        "copy_paste": " ".join(t["hashtag"] for t in tags_sorted),
    }


def analyse_caption(caption: str) -> Dict[str, Any]:
    """Analyse an existing caption and return hashtag audit results."""
    existing = re.findall(r'#\w+', caption.lower())
    existing_norm = [_normalise(t) for t in existing]
    count = len(existing_norm)

    universal_present = [t for t in existing_norm if t in [_normalise(u) for u in _UNIVERSAL_TAGS]]
    unique = list(dict.fromkeys(existing_norm))
    duplicates = [t for t in existing_norm if existing_norm.count(t) > 1]

    recommendations = []
    if count < 5:
        recommendations.append("Too few hashtags — aim for 10-30 for TikTok, 5-15 for YouTube.")
    if count > 30:
        recommendations.append("Too many hashtags — TikTok caps effectiveness around 30.")
    if not universal_present:
        recommendations.append(f"Add at least one universal viral tag: {', '.join(_UNIVERSAL_TAGS[:3])}")
    if duplicates:
        recommendations.append(f"Remove duplicate hashtags: {', '.join(set(duplicates))}")

    return {
        "caption_length": len(caption),
        "hashtag_count": count,
        "unique_hashtags": unique,
        "duplicates": list(set(duplicates)),
        "universal_tags_present": universal_present,
        "score": max(0, min(100, 50 + (count - 3) * 3 - len(duplicates) * 10 + len(universal_present) * 5)),
        "recommendations": recommendations,
    }


def list_niches() -> List[str]:
    """Return all supported niches."""
    return sorted(NICHE_HASHTAGS.keys())
