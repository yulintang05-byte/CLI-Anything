"""Hashtag strategy engine — generate, analyse, and optimise hashtag sets.

Strategy follows the 3-tier system used by top creators:
  - Mega tags  (1B+ views): broad reach, very high competition
  - Large tags (100M–1B):   good reach, medium competition
  - Niche tags (<100M):     targeted, best chance of appearing in results

Optimal mix varies by platform:
  - TikTok:    5–10 tags; 1 mega + 3 large + 3–5 niche
  - Instagram: 20–30 tags; 3 mega + 10 large + 10+ niche (use all 30)
  - YouTube:   3–5 tags in title/description (SEO keyword style)
  - Reels:     Same as Instagram, 15–25 tags
"""

from typing import Any

# Comprehensive niche hashtag database
_HASHTAG_DB: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "mega":  ["#fitness", "#gym", "#workout", "#motivation", "#health"],
        "large": ["#fitspo", "#bodybuilding", "#gains", "#fitnessmotivation", "#exercise",
                  "#healthylifestyle", "#cardio", "#weightloss", "#personaltrainer", "#fit"],
        "niche": ["#homeworkout", "#legday", "#chestday", "#backday", "#gymmotivation",
                  "#resistancetraining", "#hiit", "#strengthtraining", "#musclebuilding",
                  "#fitnessjourney", "#calisthenics", "#crossfit", "#natty", "#nattyorbottle"],
    },
    "food": {
        "mega":  ["#food", "#foodie", "#recipe", "#cooking", "#yummy"],
        "large": ["#foodporn", "#foodphotography", "#instafood", "#delicious", "#homecooking",
                  "#healthyfood", "#easyrecipe", "#mealprep", "#foodlover", "#chef"],
        "niche": ["#foodtok", "#dinnerideas", "#lunchideas", "#breakfastideas", "#veganrecipe",
                  "#ketorecipe", "#airfryer", "#onepanmeal", "#30minutemeals", "#budgetcooking",
                  "#mealplan", "#weeknightdinners", "#comfortfood", "#saucyrecipe"],
    },
    "fashion": {
        "mega":  ["#fashion", "#style", "#ootd", "#outfit", "#clothes"],
        "large": ["#fashionblogger", "#streetstyle", "#fashionista", "#outfitinspo", "#aesthetic",
                  "#streetwear", "#vintage", "#thrift", "#fashiontok", "#wiwt"],
        "niche": ["#outfitcheck", "#thrifted", "#sustainablefashion", "#capsulewardrobe",
                  "#slowfashion", "#mensoutfit", "#womensfashion", "#y2k", "#90sfashion",
                  "#minimalfashion", "#colorfuloutfit", "#preppy", "#academia"],
    },
    "beauty": {
        "mega":  ["#beauty", "#makeup", "#skincare", "#selfcare", "#glam"],
        "large": ["#makeuptutorial", "#makeuplook", "#skincareroutine", "#glowup", "#grwm",
                  "#foundation", "#eyeshadow", "#lipstick", "#nails", "#haircare"],
        "niche": ["#cleanbeauty", "#skintok", "#acneskin", "#dryskin", "#oilyskin",
                  "#naturalmakeup", "#fullglam", "#softglam", "#drugstorebeauty",
                  "#affordablebeauty", "#skincareingredients", "#retinol", "#vitaminc"],
    },
    "finance": {
        "mega":  ["#money", "#finance", "#investing", "#wealth", "#success"],
        "large": ["#personalfinance", "#budgeting", "#savings", "#financetips", "#entrepreneur",
                  "#sidehustle", "#passiveincome", "#stockmarket", "#crypto", "#realestate"],
        "niche": ["#financetok", "#moneytok", "#debtfree", "#financialindependence", "#fire",
                  "#dividends", "#indexfunds", "#etf", "#frugalliving", "#budgettips",
                  "#moneymanagement", "#incomestreams", "#wealthbuilding", "#financialliteracy"],
    },
    "travel": {
        "mega":  ["#travel", "#adventure", "#wanderlust", "#vacation", "#explore"],
        "large": ["#travelblogger", "#travelgram", "#instatravel", "#travelphotography",
                  "#backpacking", "#travelvlog", "#solo travel", "#roadtrip", "#travellife"],
        "niche": ["#traveltok", "#budgettravel", "#luxurytravel", "#digitalNomad",
                  "#remotework", "#travel2025", "#hiddengems", "#offthebeatenpath",
                  "#solo travel tips", "#travelcouple", "#familytravel", "#traveleurope"],
    },
    "gaming": {
        "mega":  ["#gaming", "#gamer", "#games", "#videogames", "#twitch"],
        "large": ["#gamingsetup", "#streamer", "#fortnite", "#minecraft", "#fps",
                  "#pcgaming", "#consolegaming", "#esports", "#gamingclips", "#gameplay"],
        "niche": ["#gamingmemes", "#twitchclips", "#warzone", "#apex", "#valorant",
                  "#lol", "#overwatch", "#roblox", "#indiegames", "#retrogaming",
                  "#gamingcommunity", "#newgames", "#gamereview", "#walkthrough"],
    },
    "motivation": {
        "mega":  ["#motivation", "#mindset", "#success", "#inspiration", "#goals"],
        "large": ["#hustle", "#grindset", "#discipline", "#entrepreneur", "#selfimprovement",
                  "#positivity", "#growth", "#mentalhealth", "#mindfulness", "#dailymotivation"],
        "niche": ["#motivationtok", "#selfdev", "#personaldevelopment", "#productivity",
                  "#morningroutine", "#habitbuilding", "#atomic habits", "#stoicism",
                  "#manifestation", "#lawofattraction", "#wealthmindset", "#successmindset"],
    },
    "education": {
        "mega":  ["#education", "#learning", "#school", "#study", "#knowledge"],
        "large": ["#tutorial", "#howto", "#learnontiktok", "#edutok", "#facts",
                  "#science", "#history", "#psychology", "#lifehacks", "#tips"],
        "niche": ["#studytok", "#studymotivation", "#studywithme", "#studyaesthetic",
                  "#didyouknow", "#funfacts", "#sciencefacts", "#psychologyfacts",
                  "#historyfacts", "#learnsomenthing", "#mindblow", "#explainit"],
    },
    "pets": {
        "mega":  ["#pets", "#dogs", "#cats", "#animals", "#cute"],
        "large": ["#dogsoftiktok", "#catsoftiktok", "#puppy", "#kitten", "#petlover",
                  "#funnypets", "#cuteanimals", "#doglife", "#catlife", "#petcare"],
        "niche": ["#dogtraining", "#puppylife", "#rescuedog", "#adoptdontshop",
                  "#goldenretriever", "#frenchbulldog", "#husky", "#siamese", "#mainecoon",
                  "#petfood", "#vettips", "#petadvice", "#exoticpets"],
    },
    "diy": {
        "mega":  ["#diy", "#craft", "#creative", "#art", "#handmade"],
        "large": ["#homedecor", "#interiordesign", "#crafting", "#makingwith", "#upcycle",
                  "#satisfying", "#transformation", "#diyhome", "#homeimprovement"],
        "niche": ["#diytok", "#crafttok", "#thriftflip", "#furnituremakeover", "#woodworking",
                  "#crochet", "#knitting", "#resin", "#candle making", "#sublimation",
                  "#printables", "#sewing", "#embroidery", "#diyjewelry"],
    },
    "music": {
        "mega":  ["#music", "#song", "#musician", "#artist", "#singing"],
        "large": ["#newmusic", "#rap", "#rnb", "#pop", "#hiphop",
                  "#producer", "#beat", "#singersoftiktok", "#originalmusic", "#cover"],
        "niche": ["#musicproducer", "#indieartist", "#unsignedartist", "#flstudio", "#ableton",
                  "#beatmaker", "#songwriter", "#loopkit", "#samplepacks", "#musictheory",
                  "#vocalcover", "#acousticcover", "#pianotok", "#guitarcover"],
    },
    "general": {
        "mega":  ["#fyp", "#foryou", "#viral", "#trending", "#explore"],
        "large": ["#foryoupage", "#tiktok", "#content", "#creator", "#contentcreator",
                  "#instagram", "#reels", "#shorts", "#youtube", "#socialmedia"],
        "niche": ["#smallcreator", "#newcreator", "#growingcreator", "#contentcreation",
                  "#creatortips", "#socialmediatips", "#algorithm", "#growthhack"],
    },
}

# Platform-specific tag strategies
_PLATFORM_STRATEGY: dict[str, dict[str, Any]] = {
    "tiktok": {
        "recommended_count": 5,
        "max_count": 10,
        "distribution": {"mega": 1, "large": 2, "niche": 2},
        "placement": "Caption (not comments)",
        "character_limit": 2200,
        "notes": [
            "TikTok's algorithm primarily uses video content signals, not tags",
            "5–7 relevant tags outperform 30 irrelevant ones",
            "Include 1–2 niche-specific tags the algorithm can categorise you by",
            "Never use banned/restricted hashtags — check TikTok's list regularly",
        ],
    },
    "instagram": {
        "recommended_count": 25,
        "max_count": 30,
        "distribution": {"mega": 3, "large": 10, "niche": 12},
        "placement": "Caption or first comment",
        "character_limit": 2200,
        "notes": [
            "Use the full 30 tags; Instagram penalises hashtag stuffing far less than TikTok",
            "Rotate hashtag sets every 3–5 posts to avoid shadow ban",
            "Save 3–5 hashtag sets for different content pillars",
            "Mix hashtags by size: some 10K–100K for reach, some 1M+ for discovery",
        ],
    },
    "youtube": {
        "recommended_count": 5,
        "max_count": 15,
        "distribution": {"mega": 1, "large": 2, "niche": 2},
        "placement": "Video description (first 3 show as clickable tags)",
        "character_limit": 500,
        "notes": [
            "YouTube tags are secondary to title and description for SEO",
            "First 3 tags appear as clickable blue tags under the video",
            "Use exact keyword phrases, not just single words",
            "Include your channel name as a tag to help group your content",
        ],
    },
    "reels": {
        "recommended_count": 20,
        "max_count": 30,
        "distribution": {"mega": 3, "large": 8, "niche": 9},
        "placement": "Caption",
        "character_limit": 2200,
        "notes": [
            "Instagram Reels get broader distribution than regular feed posts",
            "Mix trending audio hashtags with niche tags for best reach",
            "Audio hashtags (e.g. #trendingsound) can significantly boost Reels views",
        ],
    },
}


def generate_hashtag_set(niche: str, platform: str = "tiktok",
                         count: int | None = None, custom_tags: list[str] | None = None) -> dict:
    """Generate an optimised hashtag set for a niche and platform."""
    niche_key = niche.lower() if niche.lower() in _HASHTAG_DB else "general"
    platform_key = platform.lower() if platform.lower() in _PLATFORM_STRATEGY else "tiktok"

    db = _HASHTAG_DB[niche_key]
    strategy = _PLATFORM_STRATEGY[platform_key]
    dist = strategy["distribution"]

    if count is None:
        count = strategy["recommended_count"]

    mega = db["mega"][:dist["mega"]]
    large = db["large"][:dist["large"]]
    niche_tags = db["niche"][:dist["niche"]]

    # Fill remaining slots with more large/niche tags
    base = mega + large + niche_tags
    remaining = count - len(base)
    if remaining > 0:
        extra_large = db["large"][dist["large"]:dist["large"] + remaining // 2]
        extra_niche = db["niche"][dist["niche"]:dist["niche"] + remaining - len(extra_large)]
        base = base + extra_large + extra_niche

    all_tags = base[:count]

    # Append custom tags after the count slice so they are always included
    if custom_tags:
        for t in custom_tags:
            tag = t if t.startswith("#") else f"#{t}"
            if tag not in all_tags:
                all_tags.append(tag)
    return {
        "niche": niche,
        "platform": platform,
        "hashtags": all_tags,
        "count": len(all_tags),
        "caption_ready": " ".join(all_tags),
        "strategy": strategy,
        "breakdown": {
            "mega": [t for t in all_tags if t in db["mega"]],
            "large": [t for t in all_tags if t in db["large"]],
            "niche": [t for t in all_tags if t in db["niche"]],
            "custom": custom_tags or [],
        },
    }


def analyse_hashtag(tag: str) -> dict:
    """Analyse a single hashtag's tier and placement recommendations."""
    tag = tag if tag.startswith("#") else f"#{tag}"
    tag_lower = tag.lower()

    for niche_key, tiers in _HASHTAG_DB.items():
        for tier, tags in tiers.items():
            if tag_lower in [t.lower() for t in tags]:
                return {
                    "hashtag": tag,
                    "tier": tier,
                    "niche": niche_key,
                    "competition": _tier_competition(tier),
                    "recommended_platforms": _tag_platforms(tier),
                    "advice": _tag_advice(tier),
                }

    return {
        "hashtag": tag,
        "tier": "unknown",
        "note": "Tag not found in database. Research its view count on TikTok/Instagram to determine tier.",
        "advice": "Search the hashtag on target platform and check total view count",
    }


def generate_multiple_sets(niche: str, platform: str = "instagram",
                           num_sets: int = 3) -> list[dict]:
    """Generate multiple rotating hashtag sets to avoid repetitive use."""
    niche_key = niche.lower() if niche.lower() in _HASHTAG_DB else "general"
    db = _HASHTAG_DB[niche_key]
    strategy = _PLATFORM_STRATEGY.get(platform.lower(), _PLATFORM_STRATEGY["instagram"])
    count = strategy["recommended_count"]

    all_tags = db["mega"] + db["large"] + db["niche"]
    sets = []
    for i in range(num_sets):
        offset = i * (len(all_tags) // num_sets)
        selected = all_tags[offset:offset + count]
        if len(selected) < count:
            selected += all_tags[:count - len(selected)]
        sets.append({
            "set_number": i + 1,
            "label": f"Set {i + 1} — {niche} {platform}",
            "hashtags": selected,
            "caption_ready": " ".join(selected),
        })
    return sets


def hashtag_calendar(niche: str, platform: str = "instagram",
                     days: int = 7) -> list[dict]:
    """Generate a weekly hashtag rotation calendar."""
    sets = generate_multiple_sets(niche, platform, num_sets=3)
    calendar = []
    for day in range(days):
        set_idx = day % len(sets)
        from datetime import date, timedelta
        post_date = date.today() + timedelta(days=day)
        calendar.append({
            "date": post_date.isoformat(),
            "day": post_date.strftime("%A"),
            "hashtag_set": sets[set_idx]["set_number"],
            "hashtags": sets[set_idx]["hashtags"],
        })
    return calendar


def _tier_competition(tier: str) -> str:
    return {
        "mega": "Very high — use sparingly, primarily for discovery",
        "large": "Medium — good balance of reach and competition",
        "niche": "Low — best chance to appear in hashtag results",
    }.get(tier, "Unknown")


def _tag_platforms(tier: str) -> list[str]:
    if tier == "mega":
        return ["Instagram (mix)", "TikTok (limit to 1)"]
    if tier == "large":
        return ["Instagram", "TikTok", "YouTube", "Reels"]
    return ["Instagram (primary)", "TikTok (niche targeting)", "YouTube (description)"]


def _tag_advice(tier: str) -> str:
    return {
        "mega": "Mega tags boost impressions but rarely convert to followers. Always pair with niche tags.",
        "large": "Sweet spot for most creators. Use 40–50% of your set as large tags.",
        "niche": "Niche tags have the highest follow-through rate. Prioritise these for community building.",
    }.get(tier, "Research this tag's view count to determine strategy.")
