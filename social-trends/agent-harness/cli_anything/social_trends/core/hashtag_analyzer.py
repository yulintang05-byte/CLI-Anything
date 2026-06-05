"""Hashtag analysis and optimization recommendations.

Combines YouTube + TikTok trend data to produce optimized hashtag sets
for maximum reach on each platform.
"""

from collections import Counter
from typing import Optional
import re


# Evergreen hashtags that perform well regardless of trends
_EVERGREEN_YT = [
    "trending", "viral", "fyp", "explore", "subscribe", "foryou",
    "new", "watch", "video", "content",
]
_EVERGREEN_TT = [
    "fyp", "foryoupage", "viral", "trending", "tiktok", "foryou",
    "trend", "explore", "xyzbca", "4u",
]

_NICHE_TEMPLATES = {
    "fitness": ["fitness", "workout", "gym", "health", "motivation", "fitcheck", "gains", "cardio"],
    "food": ["food", "recipe", "cooking", "foodie", "yummy", "delicious", "easyrecipe", "homecooking"],
    "fashion": ["fashion", "ootd", "style", "outfit", "aesthetic", "streetwear", "clothes", "lookbook"],
    "gaming": ["gaming", "gamer", "game", "gameplay", "twitch", "streamer", "esports", "videogames"],
    "finance": ["finance", "money", "investing", "crypto", "wealth", "financetips", "stockmarket", "passive income"],
    "beauty": ["beauty", "makeup", "skincare", "glow", "tutorial", "beautytips", "grwm", "selfcare"],
    "travel": ["travel", "wanderlust", "adventure", "explore", "travelgram", "vacation", "trip", "traveltiktok"],
    "motivation": ["motivation", "mindset", "success", "hustle", "grind", "inspiration", "goals", "lifestyle"],
    "tech": ["tech", "technology", "coding", "programming", "ai", "gadgets", "softwaredev", "innovation"],
}


class HashtagAnalyzer:
    """Analyze and optimize hashtag strategies across YouTube and TikTok."""

    def analyze_hashtags(self, hashtags: list[str]) -> dict:
        """Score a list of hashtags and return analysis."""
        cleaned = [h.lstrip("#").lower().strip() for h in hashtags if h.strip()]
        if not cleaned:
            return {"error": "No hashtags provided"}

        counter = Counter(cleaned)
        scores = {}
        for tag, count in counter.items():
            score = self._score_tag(tag, count)
            scores[tag] = score

        ranked = sorted(scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
        return {
            "total_unique": len(cleaned),
            "analysis": [
                {
                    "hashtag": f"#{tag}",
                    "frequency": count,
                    **scores[tag],
                }
                for tag, count in ranked[:50]
            ],
            "recommendations": self._generate_recommendations(cleaned),
        }

    def _score_tag(self, tag: str, freq: int) -> dict:
        length_score = 10 if 4 <= len(tag) <= 15 else (5 if len(tag) <= 20 else 2)
        specificity_score = 8 if len(tag) > 8 else 5
        evergreen_bonus = 3 if tag in _EVERGREEN_TT or tag in _EVERGREEN_YT else 0
        frequency_score = min(freq * 2, 10)
        total = length_score + specificity_score + evergreen_bonus + frequency_score
        return {
            "length_score": length_score,
            "specificity_score": specificity_score,
            "evergreen_bonus": evergreen_bonus,
            "frequency_score": frequency_score,
            "total_score": total,
        }

    def _generate_recommendations(self, tags: list[str]) -> list[str]:
        recs = []
        if len(tags) < 5:
            recs.append("Add more hashtags — aim for 5-10 on TikTok, 3-5 on YouTube.")
        if len(tags) > 30:
            recs.append("Too many hashtags can look spammy. Curate to 10-15 best-fit ones.")
        short = [t for t in tags if len(t) < 4]
        if len(short) > 3:
            recs.append(f"Remove overly short tags: {short[:5]}. Too generic to drive discovery.")
        if not any(t in tags for t in _EVERGREEN_TT):
            recs.append("Include at least one evergreen TikTok tag like #fyp or #foryoupage.")
        return recs

    def build_optimal_set(
        self,
        platform: str,
        niche: str,
        trending_tags: list[str],
        count: int = 15,
    ) -> dict:
        """Build an optimized hashtag set for a platform + niche combo."""
        platform = platform.lower()
        niche = niche.lower()

        niche_tags = _NICHE_TEMPLATES.get(niche, [])
        evergreen = _EVERGREEN_TT if platform == "tiktok" else _EVERGREEN_YT

        # Deduplicate: trending first, then niche, then evergreen
        seen = set()
        result = []
        for source in [trending_tags, niche_tags, evergreen]:
            for tag in source:
                tag_clean = tag.lstrip("#").lower().strip()
                if tag_clean not in seen:
                    seen.add(tag_clean)
                    result.append(f"#{tag_clean}")
                if len(result) >= count:
                    break
            if len(result) >= count:
                break

        # Platform-specific packaging
        if platform == "tiktok":
            max_count = 5
            copy_string = " ".join(result[:max_count])
            tip = "TikTok: Use 3-5 hashtags in the caption, not 30. Quality > quantity."
        else:
            max_count = 5
            copy_string = " ".join(result[:max_count])
            tip = "YouTube: Put 3-5 hashtags at the very end of description for best SEO lift."

        return {
            "platform": platform,
            "niche": niche,
            "optimal_set": result[:count],
            "copy_ready": copy_string,
            "tip": tip,
            "breakdown": {
                "trending": [t for t in result if t.lstrip("#") in [x.lstrip("#") for x in trending_tags]],
                "niche_specific": [t for t in result if t.lstrip("#") in niche_tags],
                "evergreen": [t for t in result if t.lstrip("#") in evergreen],
            },
        }

    def get_niche_tags(self, niche: str) -> list[str]:
        """Return curated hashtags for a known niche."""
        return [f"#{t}" for t in _NICHE_TEMPLATES.get(niche.lower(), [])]

    def list_niches(self) -> list[str]:
        return list(_NICHE_TEMPLATES.keys())
