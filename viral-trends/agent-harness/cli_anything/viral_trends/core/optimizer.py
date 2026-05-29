"""Viral Trends CLI - Account optimization (hashtags, posting times, caption hooks)."""

from typing import Dict, Any, List, Optional


# ── Hashtag sets ──────────────────────────────────────────────────────────────

HASHTAG_SETS: Dict[str, Dict[str, Any]] = {
    # Gaming
    "gaming_viral": {
        "niche": "gaming",
        "tags": ["#gaming", "#gamer", "#gameplay", "#gamingcommunity", "#pcgaming",
                 "#videogames", "#twitch", "#streamer", "#esports", "#gaminglife"],
        "reach_tier": "high",
        "avg_posts_per_tag": 5_000_000,
        "platform": "tiktok",
    },
    "gaming_youtube": {
        "niche": "gaming",
        "tags": ["#gaming", "#letsplay", "#walkthrough", "#gamereview", "#ps5",
                 "#xbox", "#nintendoswitch", "#pcgaming", "#indiegame", "#newgame"],
        "reach_tier": "high",
        "avg_posts_per_tag": 3_000_000,
        "platform": "youtube",
    },
    "gaming_niche": {
        "niche": "gaming",
        "tags": ["#soloranked", "#gamingsetup", "#gamingpc", "#streamhighlights",
                 "#clutchplays", "#gamingmemes", "#gamingtips", "#fps", "#moba", "#rts"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 800_000,
        "platform": "tiktok",
    },
    # Finance
    "finance_growth": {
        "niche": "finance",
        "tags": ["#investing", "#stockmarket", "#personalfinance", "#money", "#wealth",
                 "#crypto", "#financialfreedom", "#trading", "#realestate", "#sidehustle"],
        "reach_tier": "high",
        "avg_posts_per_tag": 2_000_000,
        "platform": "tiktok",
    },
    "finance_youtube": {
        "niche": "finance",
        "tags": ["#investing", "#passiveincome", "#budgeting", "#debtfree", "#fire",
                 "#dividends", "#etf", "#indexfunds", "#moneytips", "#frugal"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 1_500_000,
        "platform": "youtube",
    },
    "finance_crypto": {
        "niche": "finance",
        "tags": ["#bitcoin", "#ethereum", "#altcoin", "#defi", "#nft",
                 "#cryptonews", "#blockchain", "#web3", "#cryptotrading", "#hodl"],
        "reach_tier": "high",
        "avg_posts_per_tag": 1_800_000,
        "platform": "tiktok",
    },
    # Fitness
    "fitness_viral": {
        "niche": "fitness",
        "tags": ["#workout", "#gym", "#fitness", "#fitnessmotivation", "#bodybuilding",
                 "#weightloss", "#healthylifestyle", "#exercise", "#gains", "#fitfam"],
        "reach_tier": "high",
        "avg_posts_per_tag": 4_000_000,
        "platform": "tiktok",
    },
    "fitness_youtube": {
        "niche": "fitness",
        "tags": ["#workout", "#homeworkout", "#noequipment", "#calisthenics",
                 "#weighttraining", "#cardio", "#yoga", "#pilates", "#hiit", "#abs"],
        "reach_tier": "high",
        "avg_posts_per_tag": 2_500_000,
        "platform": "youtube",
    },
    "fitness_nutrition": {
        "niche": "fitness",
        "tags": ["#mealprep", "#cleaneating", "#protein", "#macros", "#veganfitness",
                 "#keto", "#intermittentfasting", "#nutritioncoach", "#healthyfood", "#diet"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 1_200_000,
        "platform": "tiktok",
    },
    # Cooking
    "cooking_viral": {
        "niche": "cooking",
        "tags": ["#food", "#recipe", "#cooking", "#foodie", "#homecooking",
                 "#easyrecipes", "#foodtok", "#yummy", "#delicious", "#mealprep"],
        "reach_tier": "high",
        "avg_posts_per_tag": 6_000_000,
        "platform": "tiktok",
    },
    "cooking_youtube": {
        "niche": "cooking",
        "tags": ["#recipe", "#cooking", "#baking", "#foodreview", "#mukbang",
                 "#streetfood", "#restaurantreview", "#cheflife", "#cookingvlog", "#foodblog"],
        "reach_tier": "high",
        "avg_posts_per_tag": 3_500_000,
        "platform": "youtube",
    },
    "cooking_quick": {
        "niche": "cooking",
        "tags": ["#5minutemeals", "#quickrecipes", "#budgetmeals", "#onepanmeal",
                 "#airfryer", "#instantpot", "#noodles", "#pasta", "#rice", "#soup"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 900_000,
        "platform": "tiktok",
    },
    # Tech
    "tech_viral": {
        "niche": "tech",
        "tags": ["#technology", "#tech", "#ai", "#artificialintelligence", "#gadgets",
                 "#techtok", "#programming", "#coding", "#software", "#innovation"],
        "reach_tier": "high",
        "avg_posts_per_tag": 3_000_000,
        "platform": "tiktok",
    },
    "tech_youtube": {
        "niche": "tech",
        "tags": ["#techreview", "#unboxing", "#smartphone", "#laptop", "#apple",
                 "#samsung", "#pc", "#cybersecurity", "#datascience", "#machinelearning"],
        "reach_tier": "high",
        "avg_posts_per_tag": 2_000_000,
        "platform": "youtube",
    },
    "tech_ai": {
        "niche": "tech",
        "tags": ["#chatgpt", "#openai", "#midjourney", "#aitools", "#aiart",
                 "#promptengineering", "#llm", "#automation", "#aifuture", "#techdemo"],
        "reach_tier": "high",
        "avg_posts_per_tag": 2_800_000,
        "platform": "tiktok",
    },
    # Beauty
    "beauty_viral": {
        "niche": "beauty",
        "tags": ["#makeup", "#skincare", "#beauty", "#beautytok", "#makeupartist",
                 "#glowup", "#skincareroutine", "#makeuptutorial", "#selfcare", "#skintok"],
        "reach_tier": "high",
        "avg_posts_per_tag": 5_500_000,
        "platform": "tiktok",
    },
    "beauty_youtube": {
        "niche": "beauty",
        "tags": ["#makeuptutorial", "#grwm", "#gettingreadywithme", "#drugstorebeauty",
                 "#luxurybeauty", "#cleanbeauty", "#hairtutorial", "#nailart", "#ootd", "#fashion"],
        "reach_tier": "high",
        "avg_posts_per_tag": 3_000_000,
        "platform": "youtube",
    },
    "beauty_skincare": {
        "niche": "beauty",
        "tags": ["#acneskin", "#antiaging", "#serum", "#moisturizer", "#spf",
                 "#retinol", "#hyaluronicacid", "#skinbarrier", "#clearskin", "#glowingskin"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 1_400_000,
        "platform": "tiktok",
    },
    # Motivation
    "motivation_viral": {
        "niche": "motivation",
        "tags": ["#motivation", "#mindset", "#success", "#selfimprovement", "#discipline",
                 "#growthmindset", "#hustle", "#inspiration", "#goalsetting", "#positivity"],
        "reach_tier": "high",
        "avg_posts_per_tag": 3_500_000,
        "platform": "tiktok",
    },
    "motivation_youtube": {
        "niche": "motivation",
        "tags": ["#selfhelp", "#personaldevelopment", "#productivity", "#habits",
                 "#mindfulness", "#success", "#entrepreneur", "#leadership", "#stoicism", "#journaling"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 2_000_000,
        "platform": "youtube",
    },
    "motivation_quotes": {
        "niche": "motivation",
        "tags": ["#dailymotivation", "#quotesoftheday", "#mondaymotivation",
                 "#successquotes", "#mindsetquotes", "#lifequotes", "#grindmindset",
                 "#nevergiveup", "#believeinyourself", "#levelup"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 1_100_000,
        "platform": "tiktok",
    },
    # Entertainment
    "entertainment_viral": {
        "niche": "entertainment",
        "tags": ["#viral", "#funny", "#trending", "#comedy", "#meme",
                 "#foryou", "#fyp", "#trending", "#relatable", "#humor"],
        "reach_tier": "high",
        "avg_posts_per_tag": 10_000_000,
        "platform": "tiktok",
    },
    "entertainment_youtube": {
        "niche": "entertainment",
        "tags": ["#viral", "#funny", "#compilation", "#reactionvideo", "#challenge",
                 "#prank", "#vlog", "#dayinmylife", "#storytime", "#exposed"],
        "reach_tier": "high",
        "avg_posts_per_tag": 5_000_000,
        "platform": "youtube",
    },
    "entertainment_commentary": {
        "niche": "entertainment",
        "tags": ["#commentary", "#drama", "#tea", "#exposed", "#opinions",
                 "#celebrity", "#trending", "#scandal", "#controversial", "#reacts"],
        "reach_tier": "medium",
        "avg_posts_per_tag": 2_200_000,
        "platform": "tiktok",
    },
}


# ── Posting windows ───────────────────────────────────────────────────────────

POSTING_WINDOWS: Dict[str, List[Dict[str, Any]]] = {
    "tiktok": [
        {"day": "monday",    "windows": [{"start": "06:00", "end": "10:00", "score": 78}, {"start": "19:00", "end": "23:00", "score": 92}]},
        {"day": "tuesday",   "windows": [{"start": "06:00", "end": "09:00", "score": 75}, {"start": "20:00", "end": "23:00", "score": 88}]},
        {"day": "wednesday", "windows": [{"start": "07:00", "end": "09:00", "score": 80}, {"start": "19:00", "end": "22:00", "score": 90}, {"start": "22:00", "end": "00:00", "score": 85}]},
        {"day": "thursday",  "windows": [{"start": "06:00", "end": "09:00", "score": 76}, {"start": "20:00", "end": "22:00", "score": 87}]},
        {"day": "friday",    "windows": [{"start": "07:00", "end": "09:00", "score": 82}, {"start": "20:00", "end": "23:00", "score": 95}]},
        {"day": "saturday",  "windows": [{"start": "09:00", "end": "11:00", "score": 89}, {"start": "19:00", "end": "23:00", "score": 94}]},
        {"day": "sunday",    "windows": [{"start": "08:00", "end": "11:00", "score": 91}, {"start": "19:00", "end": "22:00", "score": 93}]},
    ],
    "youtube": [
        {"day": "monday",    "windows": [{"start": "12:00", "end": "16:00", "score": 78}, {"start": "18:00", "end": "22:00", "score": 85}]},
        {"day": "tuesday",   "windows": [{"start": "12:00", "end": "16:00", "score": 76}, {"start": "18:00", "end": "21:00", "score": 83}]},
        {"day": "wednesday", "windows": [{"start": "14:00", "end": "18:00", "score": 82}, {"start": "19:00", "end": "22:00", "score": 88}]},
        {"day": "thursday",  "windows": [{"start": "12:00", "end": "16:00", "score": 79}, {"start": "18:00", "end": "22:00", "score": 86}]},
        {"day": "friday",    "windows": [{"start": "12:00", "end": "16:00", "score": 84}, {"start": "17:00", "end": "21:00", "score": 90}]},
        {"day": "saturday",  "windows": [{"start": "09:00", "end": "13:00", "score": 87}, {"start": "15:00", "end": "19:00", "score": 91}]},
        {"day": "sunday",    "windows": [{"start": "09:00", "end": "13:00", "score": 89}, {"start": "14:00", "end": "18:00", "score": 88}]},
    ],
    "instagram": [
        {"day": "monday",    "windows": [{"start": "06:00", "end": "09:00", "score": 80}, {"start": "17:00", "end": "20:00", "score": 87}]},
        {"day": "tuesday",   "windows": [{"start": "06:00", "end": "09:00", "score": 78}, {"start": "17:00", "end": "20:00", "score": 85}]},
        {"day": "wednesday", "windows": [{"start": "08:00", "end": "11:00", "score": 83}, {"start": "17:00", "end": "20:00", "score": 89}]},
        {"day": "thursday",  "windows": [{"start": "06:00", "end": "09:00", "score": 76}, {"start": "17:00", "end": "20:00", "score": 84}]},
        {"day": "friday",    "windows": [{"start": "08:00", "end": "11:00", "score": 85}, {"start": "16:00", "end": "20:00", "score": 92}]},
        {"day": "saturday",  "windows": [{"start": "08:00", "end": "12:00", "score": 90}, {"start": "17:00", "end": "21:00", "score": 91}]},
        {"day": "sunday",    "windows": [{"start": "09:00", "end": "12:00", "score": 88}, {"start": "17:00", "end": "20:00", "score": 86}]},
    ],
}


# ── Caption hooks ─────────────────────────────────────────────────────────────

CAPTION_HOOKS: Dict[str, List[str]] = {
    "curiosity": [
        "You won't believe what happened when...",
        "Nobody talks about this, but...",
        "The secret that {niche} experts don't want you to know",
        "I discovered something that changed my {niche} game forever",
        "This one thing separates beginners from experts in {niche}",
    ],
    "urgency": [
        "Do this NOW before it's too late",
        "This {niche} trend is exploding RIGHT NOW",
        "Only {timeframe} left to take advantage of this",
        "Everyone is jumping on this — don't miss out",
        "This is the moment you'll look back on",
    ],
    "authority": [
        "After {count} hours of research in {niche}...",
        "As someone who has done this for {years} years...",
        "I tested {count} {items} so you don't have to",
        "Here's what {count} successful {niche} creators all have in common",
        "The framework I used to go from 0 to {count} followers",
    ],
    "relatability": [
        "POV: You finally figured out {topic}",
        "Me at 2am realizing {niche} is actually this simple",
        "That feeling when your {niche} content actually works",
        "Things nobody tells you about starting in {niche}",
        "Every {niche} beginner needs to hear this",
    ],
    "controversy": [
        "Hot take: {opinion}",
        "Unpopular opinion about {topic}...",
        "Everyone is wrong about {niche} except...",
        "I'm going to say what no one in {niche} wants to admit",
        "The {niche} advice everyone gives that's actually terrible",
    ],
}


# ── Functions ─────────────────────────────────────────────────────────────────

def get_hashtags(
    niche: str,
    platform: str = "tiktok",
    set_name: Optional[str] = None,
    count: int = 10,
) -> Dict[str, Any]:
    """Get hashtags for a niche.

    Args:
        niche: Content niche (gaming, finance, etc.)
        platform: Target platform.
        set_name: Specific hashtag set name (optional).
        count: Max number of tags to return.

    Returns:
        Dict with tags, set_name, reach_tier, niche, platform.
    """
    from cli_anything.viral_trends.core.workspace import NICHES
    if niche not in NICHES:
        raise ValueError(f"Unknown niche '{niche}'. Available: {list(NICHES.keys())}")

    if set_name:
        if set_name not in HASHTAG_SETS:
            raise ValueError(f"Unknown hashtag set '{set_name}'. Run 'optimize hashtags --list' to see options.")
        hset = HASHTAG_SETS[set_name]
        return {
            "success": True,
            "set_name": set_name,
            "niche": niche,
            "platform": platform,
            "reach_tier": hset["reach_tier"],
            "tags": hset["tags"][:count],
            "avg_posts_per_tag": hset["avg_posts_per_tag"],
        }

    # Find best matching set
    candidates = [
        (k, v) for k, v in HASHTAG_SETS.items()
        if v["niche"] == niche and (platform == "any" or v.get("platform") == platform)
    ]

    if not candidates:
        # Fallback: any set for this niche
        candidates = [(k, v) for k, v in HASHTAG_SETS.items() if v["niche"] == niche]

    if not candidates:
        raise ValueError(f"No hashtag sets found for niche '{niche}'")

    best_name, best_set = max(candidates, key=lambda x: x[1]["avg_posts_per_tag"])

    return {
        "success": True,
        "set_name": best_name,
        "niche": niche,
        "platform": platform,
        "reach_tier": best_set["reach_tier"],
        "tags": best_set["tags"][:count],
        "avg_posts_per_tag": best_set["avg_posts_per_tag"],
    }


def get_posting_times(
    platform: str = "tiktok",
    day: Optional[str] = None,
) -> Dict[str, Any]:
    """Get optimal posting windows for a platform.

    Args:
        platform: "tiktok", "youtube", or "instagram".
        day: Specific day ("monday"..."sunday"), or None for top windows across all days.

    Returns:
        Dict with windows list, platform, and day.
    """
    if platform not in POSTING_WINDOWS:
        raise ValueError(f"Unknown platform '{platform}'. Available: {list(POSTING_WINDOWS.keys())}")

    platform_data = POSTING_WINDOWS[platform]

    if day:
        day = day.lower()
        day_data = next((d for d in platform_data if d["day"] == day), None)
        if not day_data:
            raise ValueError(f"Unknown day '{day}'. Use: monday, tuesday, ... sunday")
        return {
            "success": True,
            "platform": platform,
            "day": day,
            "windows": day_data["windows"],
        }

    # Return top 3 windows across all days sorted by score
    all_windows = []
    for day_data in platform_data:
        for win in day_data["windows"]:
            all_windows.append({
                "day": day_data["day"],
                "start": win["start"],
                "end": win["end"],
                "score": win["score"],
            })

    top_windows = sorted(all_windows, key=lambda w: w["score"], reverse=True)[:3]

    return {
        "success": True,
        "platform": platform,
        "day": "all",
        "windows": top_windows,
    }


def get_caption_hook(
    hook_type: str = "curiosity",
    niche: str = "general",
    fill: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Get caption hook templates.

    Args:
        hook_type: Hook style (curiosity, urgency, authority, relatability, controversy).
        niche: Content niche (used for template substitution).
        fill: Dict of template variable values to substitute.

    Returns:
        Dict with hooks list, hook_type, niche.
    """
    if hook_type not in CAPTION_HOOKS:
        raise ValueError(f"Unknown hook type '{hook_type}'. Available: {list(CAPTION_HOOKS.keys())}")

    hooks = CAPTION_HOOKS[hook_type][:3]

    if fill:
        resolved = []
        for h in hooks:
            for k, v in fill.items():
                h = h.replace(f"{{{k}}}", v)
            h = h.replace("{niche}", niche)
            resolved.append(h)
        hooks = resolved
    else:
        hooks = [h.replace("{niche}", niche) for h in hooks]

    return {
        "success": True,
        "hook_type": hook_type,
        "niche": niche,
        "hooks": hooks,
    }


def list_hashtag_sets(niche: Optional[str] = None) -> List[Dict[str, Any]]:
    """List available hashtag sets, optionally filtered by niche."""
    result = []
    for name, data in HASHTAG_SETS.items():
        if niche and data["niche"] != niche:
            continue
        result.append({
            "set_name": name,
            "niche": data["niche"],
            "platform": data.get("platform", "any"),
            "reach_tier": data["reach_tier"],
            "tag_count": len(data["tags"]),
            "preview": data["tags"][:3],
        })
    return result


def list_hook_types() -> List[Dict[str, Any]]:
    """List available caption hook types."""
    descriptions = {
        "curiosity":    "Sparks interest, makes audience want to keep watching",
        "urgency":      "Creates FOMO and drives immediate action",
        "authority":    "Establishes credibility and trust",
        "relatability": "Builds emotional connection with the audience",
        "controversy":  "Generates discussion and debate",
    }
    return [
        {
            "hook_type": k,
            "description": descriptions.get(k, ""),
            "example": CAPTION_HOOKS[k][0] if CAPTION_HOOKS[k] else "",
        }
        for k in CAPTION_HOOKS
    ]


def optimize_profile(
    niche: str,
    platform: str = "tiktok",
) -> Dict[str, Any]:
    """Generate a consolidated account optimization report.

    Args:
        niche: Content niche.
        platform: Target platform.

    Returns:
        Full optimization report with hashtags, timing, hooks, and action plan.
    """
    from cli_anything.viral_trends.core.workspace import NICHES
    if niche not in NICHES:
        raise ValueError(f"Unknown niche '{niche}'. Available: {list(NICHES.keys())}")

    hashtags = get_hashtags(niche=niche, platform=platform)
    times = get_posting_times(platform=platform)
    hooks = {ht: get_caption_hook(hook_type=ht, niche=niche)["hooks"][:1][0]
             for ht in CAPTION_HOOKS}

    niche_info = NICHES[niche]
    peak_hour = niche_info["peak_hour"]

    top_window = times["windows"][0] if times["windows"] else {}
    best_day = top_window.get("day", "friday")
    best_time = top_window.get("start", f"{peak_hour:02d}:00")

    action_plan = (
        f"1. Post daily at {best_time} on {best_day.title()} for maximum reach\n"
        f"2. Always include {hashtags['tags'][0]}, {hashtags['tags'][1]} in every post\n"
        f"3. Start every caption with a {list(CAPTION_HOOKS.keys())[0]} hook\n"
        f"4. Batch-create 7 posts in one session, schedule throughout the week\n"
        f"5. Engage with top {niche} creators' content within 30min of posting\n"
        f"6. Repost your best-performing content every 30 days with new captions"
    )

    return {
        "success": True,
        "niche": niche,
        "platform": platform,
        "hashtag_set": hashtags["set_name"],
        "top_hashtags": hashtags["tags"][:10],
        "best_posting_day": best_day,
        "best_posting_time": best_time,
        "top_posting_windows": times["windows"],
        "caption_hooks": hooks,
        "action_plan": action_plan,
    }
