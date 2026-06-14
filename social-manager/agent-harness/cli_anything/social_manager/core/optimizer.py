"""Account optimizer — hashtag strategy, posting schedule, bio/profile recommendations."""
from datetime import datetime
from typing import Optional


# Best posting times by platform (EST, based on 2026 engagement research)
POSTING_WINDOWS = {
    "tiktok": [
        {"day": "Monday",    "times": ["6AM", "10AM", "10PM"]},
        {"day": "Tuesday",   "times": ["2AM", "4AM", "9AM"]},
        {"day": "Wednesday", "times": ["7AM", "8AM", "11PM"]},
        {"day": "Thursday",  "times": ["9AM", "12PM", "7PM"]},
        {"day": "Friday",    "times": ["5AM", "1PM", "3PM"]},
        {"day": "Saturday",  "times": ["11AM", "7PM", "8PM"]},
        {"day": "Sunday",    "times": ["7AM", "8AM", "4PM"]},
    ],
    "youtube": [
        {"day": "Monday",    "times": ["2PM", "4PM"]},
        {"day": "Tuesday",   "times": ["2PM", "4PM"]},
        {"day": "Wednesday", "times": ["2PM", "4PM"]},
        {"day": "Thursday",  "times": ["12PM", "3PM"]},
        {"day": "Friday",    "times": ["12PM", "3PM"]},
        {"day": "Saturday",  "times": ["9AM", "11AM"]},
        {"day": "Sunday",    "times": ["9AM", "11AM"]},
    ],
    "instagram": [
        {"day": "Monday",    "times": ["6AM", "10AM", "6PM"]},
        {"day": "Tuesday",   "times": ["8AM", "2PM", "9PM"]},
        {"day": "Wednesday", "times": ["9AM", "11AM", "3PM"]},
        {"day": "Thursday",  "times": ["7AM", "11AM", "5PM"]},
        {"day": "Friday",    "times": ["5AM", "1PM", "3PM"]},
        {"day": "Saturday",  "times": ["11AM", "12PM", "7PM"]},
        {"day": "Sunday",    "times": ["9AM", "3PM", "5PM"]},
    ],
}

# Hashtag strategy by niche
HASHTAG_SETS = {
    "finance": {
        "mega": ["#money", "#investing", "#wealth", "#financialfreedom"],
        "niche": ["#personalfinance", "#stockmarket", "#budgeting", "#passiveincome", "#sidehustle"],
        "micro": ["#moneyminset", "#financetips", "#financialliteracy", "#genzmoney"],
        "trending": ["#worldcup2026", "#summer2026", "#fyp", "#viral"],
    },
    "fitness": {
        "mega": ["#fitness", "#workout", "#gym", "#health"],
        "niche": ["#weightloss", "#bodybuilding", "#homeworkout", "#fitnessmotivation"],
        "micro": ["#gymtok", "#fitcheck", "#sweatyselfie", "#gymlife"],
        "trending": ["#fyp", "#summer2026", "#viral", "#trending"],
    },
    "travel": {
        "mega": ["#travel", "#wanderlust", "#vacation", "#adventure"],
        "niche": ["#travelgram", "#digitalnomad", "#solotravel", "#budgettravel"],
        "micro": ["#hiddengems", "#traveltok", "#travelhacks", "#travelinspo"],
        "trending": ["#worldcup2026", "#summer2026", "#fyp", "#viral"],
    },
    "motivation": {
        "mega": ["#motivation", "#mindset", "#success", "#hustle"],
        "niche": ["#entrepreneur", "#selfimprovement", "#discipline", "#growthmindset"],
        "micro": ["#dailymotivation", "#motivationalquotes", "#mindsetshift"],
        "trending": ["#fyp", "#foryou", "#viral", "#trending"],
    },
    "entertainment": {
        "mega": ["#funny", "#comedy", "#viral", "#trending"],
        "niche": ["#storytime", "#prank", "#reaction", "#challenge"],
        "micro": ["#fyp", "#foryou", "#lol", "#relatable"],
        "trending": ["#worldcup2026", "#lovelsland", "#summer2026"],
    },
    "beauty": {
        "mega": ["#beauty", "#makeup", "#skincare", "#fashion"],
        "niche": ["#grwm", "#makeuptutorial", "#skincareroutine", "#ootd"],
        "micro": ["#beautytok", "#cleanbeauty", "#glowup", "#y2k"],
        "trending": ["#fyp", "#tiktokmademebuyit", "#summer2026", "#viral"],
    },
    "food": {
        "mega": ["#food", "#foodie", "#cooking", "#recipe"],
        "niche": ["#mealprep", "#healthyeating", "#foodtok", "#homecooking"],
        "micro": ["#easyrecipes", "#whatieatinaday", "#foodasmr", "#tasty"],
        "trending": ["#fyp", "#summer2026", "#viral", "#trending"],
    },
    "tech": {
        "mega": ["#tech", "#technology", "#ai", "#innovation"],
        "niche": ["#aitools", "#automation", "#coding", "#startup"],
        "micro": ["#techtok", "#aiart", "#chatgpt", "#productivity"],
        "trending": ["#fyp", "#viral", "#trending", "#summer2026"],
    },
}


def get_hashtag_strategy(niche: str, platform: str = "tiktok") -> dict:
    niche_lower = niche.lower()
    matched = None
    for key in HASHTAG_SETS:
        if key in niche_lower or niche_lower in key:
            matched = key
            break

    if not matched:
        # Generic fallback
        base = {
            "mega": ["#viral", "#trending", "#fyp", "#foryou"],
            "niche": [f"#{niche_lower}", f"#{niche_lower}tok", f"#{niche_lower}tips"],
            "micro": [f"#{niche_lower}community", f"#{niche_lower}life"],
            "trending": ["#worldcup2026", "#summer2026", "#lovelsland"],
        }
    else:
        base = HASHTAG_SETS[matched]

    all_tags = base["mega"][:2] + base["niche"][:4] + base["micro"][:2] + base["trending"][:2]

    return {
        "niche": niche,
        "platform": platform,
        "strategy": "Mix 1-2 mega + 3-4 niche + 1-2 micro + 1-2 trending (max 8-10 total)",
        "tag_groups": base,
        "recommended_set": all_tags,
        "tips": [
            "Add hashtags in caption, not just comments",
            "Rotate trending tags weekly to stay fresh",
            "Use niche tags to reach your target audience, not just big tags",
            "Save your best-performing hashtag combo and reuse it",
            f"On {platform.title()}: 5-8 hashtags is the sweet spot in 2026",
        ],
    }


def get_posting_schedule(platform: str, frequency: str = "daily") -> dict:
    platform_lower = platform.lower()
    windows = POSTING_WINDOWS.get(platform_lower, POSTING_WINDOWS["tiktok"])

    freq_map = {
        "daily": "Post once per day — pick your top 1 slot",
        "2x": "Post twice daily — morning + evening slots",
        "3x": "Post 3x/day — morning, midday, evening (max algo push)",
        "weekly": "Pick Tue/Wed/Thu — highest engagement days",
    }

    return {
        "platform": platform,
        "recommended_frequency": "1-3x/day for TikTok, 1x/day for YouTube, 1-2x/day for Instagram",
        "posting_windows_est": windows,
        "best_days": ["Tuesday", "Wednesday", "Thursday"],
        "worst_days": ["Saturday afternoon", "Sunday evening"],
        "frequency_note": freq_map.get(frequency, freq_map["daily"]),
        "pro_tips": [
            "Batch-create content in one session, schedule across the week",
            "Post Reels/Shorts within 1 hour of when your audience is most active",
            "Reply to ALL comments in the first 30 minutes — boosts reach 40%+",
            "Use TikTok/YouTube/Instagram native scheduling (not third-party) for better reach",
            "Go LIVE 1-2x/week to push your recent posts in the algorithm",
        ],
    }


def generate_profile_audit(platform: str, handle: str, niche: str) -> dict:
    return {
        "platform": platform,
        "handle": handle,
        "niche": niche,
        "profile_checklist": [
            {"item": "Profile photo",         "tip": "High-contrast face or bold logo — recognizable at 50px"},
            {"item": "Username",               "tip": "Keep it short, memorable, niche-relevant — no numbers if possible"},
            {"item": "Display name",           "tip": f"Include 1-2 keywords: e.g. '@{handle} | {niche.title()} Tips'"},
            {"item": "Bio (TikTok/IG)",        "tip": "Hook → Value prop → CTA (link in bio). Max 150 chars, emoji ok"},
            {"item": "Link in bio",            "tip": "Use a link-in-bio tool (Linktree, Stan Store) with lead magnet"},
            {"item": "Pinned posts",           "tip": "Pin your 3 best-performing / most viral posts"},
            {"item": "Content consistency",    "tip": "Stick to 1-3 content formats. Niche down first, then expand"},
            {"item": "Brand colors/fonts",     "tip": "Pick 2-3 colors + 1 font and use them in every video thumbnail"},
            {"item": "Posting rhythm",         "tip": "Never go silent >3 days — algo punishes gaps"},
            {"item": "Keywords in captions",   "tip": "TikTok is a search engine in 2026 — use spoken + on-screen keywords"},
        ],
        "quick_wins": [
            "Update profile photo today",
            "Add a keyword to your display name",
            "Pin your top 3 videos",
            "Add a link-in-bio with lead magnet",
            "Reply to every comment on your last 5 posts",
        ],
    }
