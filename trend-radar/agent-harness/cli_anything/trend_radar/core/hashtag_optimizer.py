"""Hashtag Optimizer — Generate optimized hashtag sets for any niche and platform.

Hashtag tiers (by approximate post count):
  mega   >100M  posts — broad discovery, very competitive
  large  10M-100M posts — good reach, moderate competition
  medium 1M-10M  posts — sweet spot for growth
  niche  <1M     posts — targeted, high-signal audience
"""

from __future__ import annotations

import random

# ── Built-in hashtag database by niche and tier ───────────────────────

HASHTAG_DATABASE: dict[str, dict[str, list[str]]] = {
    "fitness": {
        "mega":   ["fitness", "gym", "workout", "fit", "health", "motivation", "exercise", "training"],
        "large":  ["fitnessmotivation", "fitnessjourney", "bodybuilding", "weightloss", "cardio", "strengthtraining", "crossfit", "personaltrainer"],
        "medium": ["fitfam", "gymlife", "fitgirl", "homeworkout", "weightlifting", "legday", "chestday", "gainz"],
        "niche":  ["powerlifting", "calisthenics", "hiitworkout", "kettlebell", "resistancetraining", "naturalbodybuilder", "fitnessblogger", "gymcoach"],
    },
    "food": {
        "mega":   ["food", "foodie", "cooking", "recipe", "delicious", "yummy", "eat", "homecooking"],
        "large":  ["foodphotography", "foodblogger", "foodstagram", "instafood", "foodlover", "healthyfood", "mealprep", "breakfast"],
        "medium": ["foodblog", "veganfood", "glutenfree", "homemade", "recipevideo", "easyrecipe", "dinnerideas", "quickrecipes"],
        "niche":  ["plantbased", "whole30", "ketorecipes", "airfryer", "slowcooker", "batchcooking", "foodstyling", "culinaryarts"],
    },
    "travel": {
        "mega":   ["travel", "wanderlust", "photography", "explore", "adventure", "vacation", "travelgram", "instatravel"],
        "large":  ["travelphotography", "traveling", "travelblogger", "travellife", "worldtravel", "backpacking", "solotravel", "luxurytravel"],
        "medium": ["travelcouple", "traveltips", "travelinspiration", "bucketlist", "digitalnomad", "travelwithkids", "roadtrip", "hotellife"],
        "niche":  ["offthebeatenpath", "slowtravel", "budgettravel", "travelplanning", "vanlife", "workandtravel", "travelhacks", "sustainabletravel"],
    },
    "fashion": {
        "mega":   ["fashion", "style", "ootd", "outfit", "clothes", "shopping", "beauty", "lifestyle"],
        "large":  ["fashionblogger", "fashionista", "outfitoftheday", "streetstyle", "fashionphotography", "lookbook", "fashionstyle", "wiwt"],
        "medium": ["outfitinspo", "styleinspo", "outfitgoals", "casualstyle", "minimalistfashion", "sustainablefashion", "vintageoutfit", "mensfashion"],
        "niche":  ["slowfashion", "thriftedfashion", "capsulewardrobe", "ethicalfashion", "upcycled", "fashionrevolution", "indiestylist", "personalstyle"],
    },
    "tech": {
        "mega":   ["tech", "technology", "coding", "programming", "developer", "software", "ai", "innovation"],
        "large":  ["techblogger", "javascript", "python", "webdevelopment", "machinelearning", "startup", "entrepreneur", "cybersecurity"],
        "medium": ["techtips", "devlife", "fullstackdeveloper", "reactjs", "nodejs", "uxdesign", "productdesign", "swe"],
        "niche":  ["opensource", "devops", "cloudcomputing", "codenewbie", "100daysofcode", "techethics", "aitools", "buildinpublic"],
    },
    "finance": {
        "mega":   ["money", "finance", "investing", "wealth", "success", "business", "entrepreneur", "rich"],
        "large":  ["personalfinance", "financialfreedom", "invest", "stockmarket", "cryptocurrency", "realestate", "passiveincome", "sidehustle"],
        "medium": ["moneytips", "financialliteracy", "moneymanagement", "debtfree", "frugalliving", "retirementplanning", "indexfunds", "dividends"],
        "niche":  ["firemovement", "leanfire", "moneymindset", "wealthbuilding", "financialcoach", "generationalwealth", "budgetbabe", "investingforbeginners"],
    },
    "gaming": {
        "mega":   ["gaming", "gamer", "twitch", "youtube", "games", "videogames", "playstation", "xbox"],
        "large":  ["gamingcommunity", "pcgaming", "gaminglifestyle", "esports", "fortnite", "minecraft", "cod", "leagueoflegends"],
        "medium": ["gamingnews", "indiegames", "gamingmemes", "retrogaming", "mobilegaming", "gamingsetup", "consolegaming", "speedrun"],
        "niche":  ["gamedesign", "gamedevelopment", "boardgames", "tabletopgaming", "ttrpg", "dungeonsanddragons", "soloboardgames", "gamedev"],
    },
    "beauty": {
        "mega":   ["beauty", "makeup", "skincare", "glam", "cosmetics", "beautytips", "makeupartist", "lipstick"],
        "large":  ["makeuptutorial", "beautyblogger", "makeuplover", "skincareroutine", "eyeshadow", "glowup", "makeuplook", "naturalmakeup"],
        "medium": ["makeupinspo", "skincareobsessed", "beautyreview", "cleanbeauty", "crueltyfreemakeup", "drugstoremakeup", "makeuplife", "glowyskin"],
        "niche":  ["kbeauty", "jbeauty", "skinminimalism", "skintok", "sluggingmethod", "glasskin", "beautyunboxing", "makeupdupes"],
    },
    "lifestyle": {
        "mega":   ["lifestyle", "life", "happy", "positivity", "motivation", "inspiration", "mindset", "growth"],
        "large":  ["lifestyleblogger", "selfcare", "wellness", "mentalhealth", "mindfulness", "selflove", "gratitude", "personaldevelopment"],
        "medium": ["selfimprovement", "morningroutine", "productivitytips", "worklifebalance", "slowliving", "intentionalliving", "minimalism", "hygge"],
        "niche":  ["stoicism", "journaling", "habittracking", "lifebydesign", "consciousliving", "deepwork", "morningpages", "soberlife"],
    },
    "general": {
        "mega":   ["viral", "fyp", "foryou", "trending", "explore", "instagood", "follow", "like"],
        "large":  ["reels", "instareels", "content", "contentcreator", "creativeentrepreneur", "creatoreconomy", "socialmedia", "influencer"],
        "medium": ["contentcreation", "socialmediatips", "growyouraccount", "instagramtips", "tiktoktips", "videocontent", "shortformcontent", "ugc"],
        "niche":  ["contentmarketing", "ugccreator", "brandcollaboration", "paidpartnership", "creatorlife", "influencermarketing", "digitalcreator", "nanoinfluencer"],
    },
}

PLATFORM_LIMITS: dict[str, int] = {
    "instagram": 30,
    "tiktok": 10,
    "youtube": 15,
    "twitter": 3,
}

PLATFORM_STRATEGIES: dict[str, dict] = {
    "instagram": {
        "mega_pct": 0.20, "large_pct": 0.30, "medium_pct": 0.35, "niche_pct": 0.15,
        "description": "Mix broad discovery with niche targeting. Avoid only mega-tags for better chance of ranking.",
    },
    "tiktok": {
        "mega_pct": 0.30, "large_pct": 0.30, "medium_pct": 0.25, "niche_pct": 0.15,
        "description": "Trend-forward hashtags dominate. Include fyp/foryou sparingly — algorithm matters more than tags.",
    },
    "youtube": {
        "mega_pct": 0.15, "large_pct": 0.35, "medium_pct": 0.35, "niche_pct": 0.15,
        "description": "Place in description and title. Focus on searchable, keyword-rich terms over pure trend tags.",
    },
    "twitter": {
        "mega_pct": 0.50, "large_pct": 0.50, "medium_pct": 0.00, "niche_pct": 0.00,
        "description": "Use 1-3 highly relevant trending hashtags only. Less is more on Twitter/X.",
    },
}


class HashtagOptimizer:
    """Generate and analyze optimized hashtag sets for social media niches."""

    def generate_set(
        self,
        niche: str,
        platform: str = "instagram",
        count: int = 30,
    ) -> dict:
        """Generate a tiered, optimized hashtag set for a niche.

        Returns dict: niche, platform, total, strategy, tiers, all_tags, copy_ready
        """
        db = HASHTAG_DATABASE.get(niche.lower().strip(), HASHTAG_DATABASE["general"])
        strategy = PLATFORM_STRATEGIES.get(platform, PLATFORM_STRATEGIES["instagram"])
        limit = min(count, PLATFORM_LIMITS.get(platform, 30))

        mega_n   = max(1, int(limit * strategy["mega_pct"]))
        large_n  = max(1, int(limit * strategy["large_pct"]))
        medium_n = max(1, int(limit * strategy.get("medium_pct", 0.35)))
        niche_n  = max(0, limit - mega_n - large_n - medium_n)

        def _pick(pool: list[str], n: int) -> list[str]:
            shuffled = pool.copy()
            random.shuffle(shuffled)
            return shuffled[:n]

        mega_tags   = _pick(db["mega"], mega_n)
        large_tags  = _pick(db["large"], large_n)
        medium_tags = _pick(db["medium"], medium_n)
        niche_tags  = _pick(db["niche"], niche_n)

        all_tags = mega_tags + large_tags + medium_tags + niche_tags
        random.shuffle(all_tags)

        return {
            "niche":    niche,
            "platform": platform,
            "total":    len(all_tags),
            "strategy": strategy["description"],
            "tiers": {
                "mega (100M+ posts)":    mega_tags,
                "large (10M-100M)":      large_tags,
                "medium (1M-10M)":       medium_tags,
                "niche (<1M)":           niche_tags,
            },
            "all_tags":   all_tags,
            "copy_ready": " ".join(f"#{t}" for t in all_tags),
        }

    def analyze_hashtags(self, hashtags: list[str]) -> dict:
        """Analyze a list of hashtags for tier balance and give recommendations.

        Returns dict: total, tier_counts, classification, recommendations
        """
        # Build lookup sets from all niches
        mega_set, large_set, medium_set, niche_set = set(), set(), set(), set()
        for niche_data in HASHTAG_DATABASE.values():
            mega_set.update(niche_data.get("mega", []))
            large_set.update(niche_data.get("large", []))
            medium_set.update(niche_data.get("medium", []))
            niche_set.update(niche_data.get("niche", []))

        classification: dict[str, str] = {}
        for tag in hashtags:
            clean = tag.lstrip("#").lower()
            if clean in mega_set:
                classification[tag] = "mega"
            elif clean in large_set:
                classification[tag] = "large"
            elif clean in medium_set:
                classification[tag] = "medium"
            elif clean in niche_set:
                classification[tag] = "niche"
            else:
                classification[tag] = "unknown"

        counts: dict[str, int] = {t: 0 for t in ["mega", "large", "medium", "niche", "unknown"]}
        for tier in classification.values():
            counts[tier] += 1

        total = len(hashtags)
        recommendations: list[str] = []
        if total > 0:
            if counts["mega"] / total > 0.5:
                recommendations.append("Too many mega-hashtags — your content will be buried. Add more medium/niche tags.")
            if counts["niche"] / total > 0.6:
                recommendations.append("Good niche targeting, but add some large-tier tags for discoverability.")
            if counts["mega"] == 0:
                recommendations.append("Add 2-5 mega-hashtags for broad reach.")
        if not recommendations:
            recommendations.append("Good balance! Hashtag mix looks well-optimized.")

        return {
            "total":           total,
            "tier_counts":     counts,
            "classification":  classification,
            "recommendations": recommendations,
        }
