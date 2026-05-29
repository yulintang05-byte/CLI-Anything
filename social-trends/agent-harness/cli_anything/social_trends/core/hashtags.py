"""Hashtag research, ranking, and suggestion engine."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from cli_anything.social_trends.core.store import Store

# ── Niche hashtag seed data ───────────────────────────────────────────────────

_NICHE_HASHTAGS: Dict[str, List[Dict[str, Any]]] = {
    "fitness": [
        {"tag": "#fitness",          "posts": "500M", "avg_views": "25K", "competition": "high",   "engagement_rate": 4.2},
        {"tag": "#workout",          "posts": "380M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.5},
        {"tag": "#gym",              "posts": "320M", "avg_views": "18K", "competition": "high",   "engagement_rate": 3.9},
        {"tag": "#health",           "posts": "290M", "avg_views": "20K", "competition": "high",   "engagement_rate": 4.1},
        {"tag": "#fitspo",           "posts": "120M", "avg_views": "15K", "competition": "medium", "engagement_rate": 5.2},
        {"tag": "#calisthenics",     "posts": "45M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.8},
        {"tag": "#homeworkout",      "posts": "38M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 6.1},
        {"tag": "#weightloss",       "posts": "95M",  "avg_views": "19K", "competition": "high",   "engagement_rate": 4.8},
        {"tag": "#bodybuilding",     "posts": "55M",  "avg_views": "16K", "competition": "medium", "engagement_rate": 5.0},
        {"tag": "#fitnessjourney",   "posts": "28M",  "avg_views": "32K", "competition": "low",    "engagement_rate": 7.4},
        {"tag": "#30daychallenge",   "posts": "12M",  "avg_views": "40K", "competition": "low",    "engagement_rate": 8.2},
        {"tag": "#noequipmentworkout","posts": "8M",  "avg_views": "48K", "competition": "low",    "engagement_rate": 9.1},
    ],
    "finance": [
        {"tag": "#finance",          "posts": "210M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.0},
        {"tag": "#money",            "posts": "480M", "avg_views": "20K", "competition": "high",   "engagement_rate": 3.8},
        {"tag": "#investing",        "posts": "95M",  "avg_views": "28K", "competition": "high",   "engagement_rate": 5.2},
        {"tag": "#personalfinance",  "posts": "68M",  "avg_views": "35K", "competition": "medium", "engagement_rate": 6.4},
        {"tag": "#stockmarket",      "posts": "75M",  "avg_views": "24K", "competition": "medium", "engagement_rate": 5.6},
        {"tag": "#passiveincome",    "posts": "55M",  "avg_views": "38K", "competition": "medium", "engagement_rate": 7.1},
        {"tag": "#financialliteracy","posts": "32M",  "avg_views": "42K", "competition": "low",    "engagement_rate": 8.3},
        {"tag": "#budgeting",        "posts": "28M",  "avg_views": "36K", "competition": "low",    "engagement_rate": 7.8},
        {"tag": "#wealthbuilding",   "posts": "15M",  "avg_views": "50K", "competition": "low",    "engagement_rate": 9.2},
        {"tag": "#sidehustle",       "posts": "42M",  "avg_views": "31K", "competition": "medium", "engagement_rate": 6.7},
        {"tag": "#debtfree",         "posts": "18M",  "avg_views": "44K", "competition": "low",    "engagement_rate": 8.6},
        {"tag": "#financefreedom",   "posts": "22M",  "avg_views": "40K", "competition": "low",    "engagement_rate": 8.1},
    ],
    "luxury": [
        {"tag": "#luxury",           "posts": "280M", "avg_views": "18K", "competition": "high",   "engagement_rate": 3.6},
        {"tag": "#luxurylifestyle",  "posts": "150M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.2},
        {"tag": "#luxurycar",        "posts": "90M",  "avg_views": "25K", "competition": "medium", "engagement_rate": 5.1},
        {"tag": "#millionaire",      "posts": "65M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 5.8},
        {"tag": "#richlife",         "posts": "45M",  "avg_views": "35K", "competition": "medium", "engagement_rate": 6.3},
        {"tag": "#luxuryfashion",    "posts": "38M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.5},
        {"tag": "#penthouse",        "posts": "12M",  "avg_views": "52K", "competition": "low",    "engagement_rate": 9.4},
        {"tag": "#privatejet",       "posts": "18M",  "avg_views": "48K", "competition": "low",    "engagement_rate": 8.9},
        {"tag": "#supercars",        "posts": "55M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.1},
        {"tag": "#luxurywatch",      "posts": "25M",  "avg_views": "38K", "competition": "low",    "engagement_rate": 7.6},
        {"tag": "#lavishlife",       "posts": "8M",   "avg_views": "60K", "competition": "low",    "engagement_rate": 10.2},
        {"tag": "#highend",          "posts": "14M",  "avg_views": "44K", "competition": "low",    "engagement_rate": 8.3},
    ],
    "travel": [
        {"tag": "#travel",           "posts": "620M", "avg_views": "16K", "competition": "high",   "engagement_rate": 3.4},
        {"tag": "#wanderlust",       "posts": "310M", "avg_views": "19K", "competition": "high",   "engagement_rate": 4.0},
        {"tag": "#travelphotography","posts": "185M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.5},
        {"tag": "#backpacking",      "posts": "55M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.2},
        {"tag": "#solotravel",       "posts": "42M",  "avg_views": "34K", "competition": "medium", "engagement_rate": 6.8},
        {"tag": "#budgettravel",     "posts": "28M",  "avg_views": "38K", "competition": "medium", "engagement_rate": 7.3},
        {"tag": "#digitalnomadd",    "posts": "15M",  "avg_views": "50K", "competition": "low",    "engagement_rate": 9.1},
        {"tag": "#hiddengems",       "posts": "12M",  "avg_views": "54K", "competition": "low",    "engagement_rate": 9.6},
        {"tag": "#traveltips",       "posts": "38M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.5},
        {"tag": "#offthebeatenpath", "posts": "8M",   "avg_views": "62K", "competition": "low",    "engagement_rate": 10.8},
        {"tag": "#luxurytravel",     "posts": "48M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.9},
        {"tag": "#familytravel",     "posts": "22M",  "avg_views": "36K", "competition": "low",    "engagement_rate": 7.7},
    ],
    "food": [
        {"tag": "#food",             "posts": "780M", "avg_views": "14K", "competition": "high",   "engagement_rate": 3.2},
        {"tag": "#foodie",           "posts": "420M", "avg_views": "17K", "competition": "high",   "engagement_rate": 3.8},
        {"tag": "#recipe",           "posts": "195M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.4},
        {"tag": "#homecooking",      "posts": "88M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.8},
        {"tag": "#healthyfood",      "posts": "115M", "avg_views": "25K", "competition": "high",   "engagement_rate": 5.1},
        {"tag": "#mealprep",         "posts": "52M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.4},
        {"tag": "#veganrecipes",     "posts": "38M",  "avg_views": "36K", "competition": "medium", "engagement_rate": 7.0},
        {"tag": "#foodasmr",         "posts": "22M",  "avg_views": "44K", "competition": "low",    "engagement_rate": 8.5},
        {"tag": "#whatieatinaday",   "posts": "18M",  "avg_views": "48K", "competition": "low",    "engagement_rate": 8.9},
        {"tag": "#cheatmeal",        "posts": "12M",  "avg_views": "55K", "competition": "low",    "engagement_rate": 9.7},
        {"tag": "#streetfood",       "posts": "65M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.1},
        {"tag": "#cookingvideo",     "posts": "8M",   "avg_views": "60K", "competition": "low",    "engagement_rate": 10.3},
    ],
    "gaming": [
        {"tag": "#gaming",           "posts": "340M", "avg_views": "20K", "competition": "high",   "engagement_rate": 4.1},
        {"tag": "#gamer",            "posts": "280M", "avg_views": "18K", "competition": "high",   "engagement_rate": 3.9},
        {"tag": "#gameplay",         "posts": "175M", "avg_views": "22K", "competition": "high",   "engagement_rate": 4.4},
        {"tag": "#streamer",         "posts": "95M",  "avg_views": "26K", "competition": "medium", "engagement_rate": 5.3},
        {"tag": "#gamingsetup",      "posts": "48M",  "avg_views": "34K", "competition": "medium", "engagement_rate": 6.7},
        {"tag": "#fps",              "posts": "38M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.1},
        {"tag": "#speedrun",         "posts": "15M",  "avg_views": "50K", "competition": "low",    "engagement_rate": 9.2},
        {"tag": "#pcgaming",         "posts": "55M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.8},
        {"tag": "#consolegaming",    "posts": "32M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.4},
        {"tag": "#gamingclips",      "posts": "22M",  "avg_views": "40K", "competition": "low",    "engagement_rate": 7.9},
        {"tag": "#esports",          "posts": "42M",  "avg_views": "35K", "competition": "medium", "engagement_rate": 7.0},
        {"tag": "#retrogaming",      "posts": "12M",  "avg_views": "54K", "competition": "low",    "engagement_rate": 9.8},
    ],
    "crypto": [
        {"tag": "#crypto",           "posts": "125M", "avg_views": "28K", "competition": "high",   "engagement_rate": 5.6},
        {"tag": "#bitcoin",          "posts": "185M", "avg_views": "25K", "competition": "high",   "engagement_rate": 5.1},
        {"tag": "#ethereum",         "posts": "75M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.0},
        {"tag": "#altcoins",         "posts": "42M",  "avg_views": "38K", "competition": "medium", "engagement_rate": 7.4},
        {"tag": "#defi",             "posts": "28M",  "avg_views": "44K", "competition": "medium", "engagement_rate": 8.2},
        {"tag": "#nft",              "posts": "95M",  "avg_views": "22K", "competition": "high",   "engagement_rate": 4.5},
        {"tag": "#web3",             "posts": "38M",  "avg_views": "36K", "competition": "medium", "engagement_rate": 7.0},
        {"tag": "#cryptoinvesting",  "posts": "18M",  "avg_views": "52K", "competition": "low",    "engagement_rate": 9.5},
        {"tag": "#blockchain",       "posts": "55M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.7},
        {"tag": "#cryptotrading",    "posts": "22M",  "avg_views": "46K", "competition": "low",    "engagement_rate": 8.8},
        {"tag": "#bitcoinprice",     "posts": "12M",  "avg_views": "55K", "competition": "low",    "engagement_rate": 9.9},
        {"tag": "#cryptonews",       "posts": "15M",  "avg_views": "48K", "competition": "low",    "engagement_rate": 9.1},
    ],
    "fashion": [
        {"tag": "#fashion",          "posts": "580M", "avg_views": "15K", "competition": "high",   "engagement_rate": 3.3},
        {"tag": "#style",            "posts": "380M", "avg_views": "18K", "competition": "high",   "engagement_rate": 3.9},
        {"tag": "#ootd",             "posts": "295M", "avg_views": "20K", "competition": "high",   "engagement_rate": 4.2},
        {"tag": "#fashionblogger",   "posts": "125M", "avg_views": "24K", "competition": "medium", "engagement_rate": 5.0},
        {"tag": "#streetwear",       "posts": "78M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.7},
        {"tag": "#outfitinspo",      "posts": "55M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.3},
        {"tag": "#thriftflip",       "posts": "18M",  "avg_views": "50K", "competition": "low",    "engagement_rate": 9.3},
        {"tag": "#aestheticoutfit",  "posts": "22M",  "avg_views": "44K", "competition": "low",    "engagement_rate": 8.6},
        {"tag": "#capsulewardrobe",  "posts": "12M",  "avg_views": "55K", "competition": "low",    "engagement_rate": 9.8},
        {"tag": "#fashionweek",      "posts": "35M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.0},
        {"tag": "#sustainablefashion","posts": "25M", "avg_views": "38K", "competition": "low",    "engagement_rate": 7.6},
        {"tag": "#luxuryfashion",    "posts": "42M",  "avg_views": "26K", "competition": "medium", "engagement_rate": 5.4},
    ],
    "motivational": [
        {"tag": "#motivation",       "posts": "420M", "avg_views": "18K", "competition": "high",   "engagement_rate": 4.0},
        {"tag": "#success",          "posts": "285M", "avg_views": "21K", "competition": "high",   "engagement_rate": 4.6},
        {"tag": "#mindset",          "posts": "165M", "avg_views": "26K", "competition": "medium", "engagement_rate": 5.6},
        {"tag": "#hustle",           "posts": "95M",  "avg_views": "30K", "competition": "medium", "engagement_rate": 6.2},
        {"tag": "#growthmindset",    "posts": "42M",  "avg_views": "38K", "competition": "medium", "engagement_rate": 7.5},
        {"tag": "#selfimprovement",  "posts": "68M",  "avg_views": "34K", "competition": "medium", "engagement_rate": 6.9},
        {"tag": "#dailymotivation",  "posts": "55M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.5},
        {"tag": "#positivemindset",  "posts": "35M",  "avg_views": "40K", "competition": "low",    "engagement_rate": 7.9},
        {"tag": "#entrepreneurmindset","posts":"22M", "avg_views": "46K", "competition": "low",    "engagement_rate": 8.7},
        {"tag": "#levelup",          "posts": "18M",  "avg_views": "50K", "competition": "low",    "engagement_rate": 9.2},
        {"tag": "#mentalhealth",     "posts": "88M",  "avg_views": "28K", "competition": "medium", "engagement_rate": 5.9},
        {"tag": "#disciplineequals","posts": "8M",   "avg_views": "65K", "competition": "low",    "engagement_rate": 11.0},
    ],
    "sports": [
        {"tag": "#sports",           "posts": "395M", "avg_views": "16K", "competition": "high",   "engagement_rate": 3.7},
        {"tag": "#football",         "posts": "460M", "avg_views": "18K", "competition": "high",   "engagement_rate": 4.0},
        {"tag": "#basketball",       "posts": "220M", "avg_views": "20K", "competition": "high",   "engagement_rate": 4.4},
        {"tag": "#soccer",           "posts": "310M", "avg_views": "17K", "competition": "high",   "engagement_rate": 3.8},
        {"tag": "#nba",              "posts": "135M", "avg_views": "26K", "competition": "medium", "engagement_rate": 5.5},
        {"tag": "#nfl",              "posts": "112M", "avg_views": "24K", "competition": "medium", "engagement_rate": 5.1},
        {"tag": "#sportsedits",      "posts": "28M",  "avg_views": "44K", "competition": "low",    "engagement_rate": 8.6},
        {"tag": "#athletelife",      "posts": "22M",  "avg_views": "40K", "competition": "low",    "engagement_rate": 8.0},
        {"tag": "#trainingday",      "posts": "18M",  "avg_views": "46K", "competition": "low",    "engagement_rate": 8.9},
        {"tag": "#highlights",       "posts": "55M",  "avg_views": "32K", "competition": "medium", "engagement_rate": 6.4},
        {"tag": "#sportsclips",      "posts": "15M",  "avg_views": "52K", "competition": "low",    "engagement_rate": 9.5},
        {"tag": "#athletic",         "posts": "12M",  "avg_views": "56K", "competition": "low",    "engagement_rate": 10.0},
    ],
}

_SORT_KEYS = {
    "views":      lambda h: int(h["avg_views"].replace("K", "000").replace("M", "000000")),
    "posts":      lambda h: int(h["posts"].replace("M", "000000").replace("K", "000")),
    "engagement": lambda h: h["engagement_rate"],
}


def research_hashtags(
    store: Store,
    niche: str,
    platform: str = "both",
    limit: int = 12,
) -> List[Dict[str, Any]]:
    key = niche.lower().replace(" ", "_").replace("-", "_")
    # fuzzy match
    if key not in _NICHE_HASHTAGS:
        for k in _NICHE_HASHTAGS:
            if k in key or key in k:
                key = k
                break
        else:
            key = "motivational"  # safe fallback

    tags = [dict(t, niche=key, platform=platform) for t in _NICHE_HASHTAGS[key][:limit]]
    store.hashtags = tags
    store.save()
    return tags


def rank_hashtags(store: Store, by: str = "engagement") -> List[Dict[str, Any]]:
    if not store.hashtags:
        return []
    sort_fn = _SORT_KEYS.get(by, _SORT_KEYS["engagement"])
    try:
        return sorted(store.hashtags, key=sort_fn, reverse=True)
    except Exception:
        return store.hashtags


def suggest_hashtags(store: Store, niche: str, count: int = 30) -> Dict[str, Any]:
    """Suggest optimal hashtag mix: 30% high, 40% medium, 30% low competition."""
    all_tags = research_hashtags(store, niche, limit=12)
    high   = [t for t in all_tags if t["competition"] == "high"]
    medium = [t for t in all_tags if t["competition"] == "medium"]
    low    = [t for t in all_tags if t["competition"] == "low"]

    n_high   = max(1, count * 30 // 100)
    n_medium = max(1, count * 40 // 100)
    n_low    = count - n_high - n_medium

    suggested = {
        "high_competition":   [t["tag"] for t in high[:n_high]],
        "medium_competition": [t["tag"] for t in medium[:n_medium]],
        "low_competition":    [t["tag"] for t in low[:n_low]],
        "combined":           (
            [t["tag"] for t in high[:n_high]]
            + [t["tag"] for t in medium[:n_medium]]
            + [t["tag"] for t in low[:n_low]]
        ),
        "niche": niche,
        "total": n_high + n_medium + n_low,
        "strategy": (
            "Mix high-competition tags for discovery, medium for niche reach, "
            "and low for fast ranking. Rotate sets every 2 weeks."
        ),
    }
    return suggested


def export_hashtags(store: Store, path: str) -> Dict[str, Any]:
    data = {"hashtags": store.hashtags, "exported_at": datetime.now().isoformat()}
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return {"success": True, "path": path, "count": len(store.hashtags)}
