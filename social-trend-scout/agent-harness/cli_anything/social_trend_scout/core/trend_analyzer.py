"""Cross-platform trend analysis and actionable insight generation."""

from collections import Counter
from datetime import datetime
from typing import Any


PLATFORM_WEIGHTS = {"youtube": 0.6, "tiktok": 0.4}  # YouTube still drives discovery volume


class TrendAnalyzer:
    """Merge, score, and derive insights from multi-platform trend data."""

    # ------------------------------------------------------------------
    # Cross-platform hashtag unification
    # ------------------------------------------------------------------

    def merge_hashtags(
        self,
        youtube_hashtags: list[dict],
        tiktok_hashtags: list[dict],
    ) -> list[dict]:
        """Merge hashtag frequency from both platforms into unified ranked list."""
        merged: dict[str, dict] = {}

        for entry in youtube_hashtags:
            tag = entry["hashtag"].lower()
            merged[tag] = {
                "hashtag": tag,
                "youtube_frequency": entry.get("frequency", 0),
                "tiktok_frequency": 0,
                "cross_platform": False,
            }

        for entry in tiktok_hashtags:
            tag = entry["hashtag"].lower()
            if tag in merged:
                merged[tag]["tiktok_frequency"] = entry.get("frequency", 0)
                merged[tag]["cross_platform"] = True
            else:
                merged[tag] = {
                    "hashtag": tag,
                    "youtube_frequency": 0,
                    "tiktok_frequency": entry.get("frequency", 0),
                    "cross_platform": False,
                }

        for tag_data in merged.values():
            yt = tag_data["youtube_frequency"] * PLATFORM_WEIGHTS["youtube"]
            tt = tag_data["tiktok_frequency"] * PLATFORM_WEIGHTS["tiktok"]
            tag_data["combined_score"] = round(yt + tt, 2)
            tag_data["recommendation"] = self._hashtag_recommendation(tag_data)

        return sorted(merged.values(), key=lambda x: x["combined_score"], reverse=True)

    @staticmethod
    def _hashtag_recommendation(tag_data: dict) -> str:
        if tag_data["cross_platform"]:
            return "HIGH PRIORITY — trending on both platforms"
        if tag_data["youtube_frequency"] > 3:
            return "Use in YouTube titles and descriptions"
        if tag_data["tiktok_frequency"] > 2:
            return "Use in TikTok captions"
        return "Monitor — low frequency"

    # ------------------------------------------------------------------
    # Viral pattern extraction
    # ------------------------------------------------------------------

    def extract_viral_patterns(self, videos: list[dict]) -> dict:
        """Find patterns in high-engagement content."""
        if not videos:
            return {}

        top = [v for v in videos if v.get("engagement_pct", 0) > 3 or v.get("viral_score", 0) > 60]

        title_words = Counter()
        for v in top:
            words = v.get("title", "").lower().split()
            title_words.update([w for w in words if len(w) > 3])

        avg_duration = self._avg_duration(top)

        return {
            "top_title_words": title_words.most_common(15),
            "avg_viral_duration": avg_duration,
            "engagement_threshold": "3%+ = viral on YouTube",
            "hook_patterns": self._detect_hook_patterns(top),
            "content_angles": self._detect_content_angles(top),
        }

    @staticmethod
    def _avg_duration(videos: list[dict]) -> str:
        """Parse ISO 8601 durations and average them."""
        import re
        total = 0
        count = 0
        for v in videos:
            dur = v.get("duration", "")
            m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
            if m:
                h, mn, s = (int(m.group(i) or 0) for i in (1, 2, 3))
                total += h * 3600 + mn * 60 + s
                count += 1
        if not count:
            return "unknown"
        avg = total // count
        return f"{avg // 60}m {avg % 60}s"

    @staticmethod
    def _detect_hook_patterns(videos: list[dict]) -> list[str]:
        patterns = []
        for v in videos:
            title = v.get("title", "").lower()
            if any(w in title for w in ["how to", "why", "what", "when"]):
                patterns.append("question_hook")
            if any(w in title for w in ["vs", "versus", "vs."]):
                patterns.append("comparison")
            if any(w in title for w in ["top", "best", "worst", "most"]):
                patterns.append("list_format")
            if any(w in title for w in ["react", "reacts", "reaction"]):
                patterns.append("reaction_content")
            if any(w in title for w in ["before", "after", "transformation"]):
                patterns.append("transformation")
        return list(set(patterns))

    @staticmethod
    def _detect_content_angles(videos: list[dict]) -> list[str]:
        angles = []
        for v in videos:
            title = v.get("title", "").lower()
            if any(w in title for w in ["tutorial", "guide", "learn", "how"]):
                angles.append("educational")
            if any(w in title for w in ["funny", "lol", "fail", "roast"]):
                angles.append("comedy")
            if any(w in title for w in ["story", "my", "i"]):
                angles.append("personal_story")
            if any(w in title for w in ["review", "honest", "worth"]):
                angles.append("review")
        return list(set(angles))

    # ------------------------------------------------------------------
    # Trend velocity (is it rising or peaking?)
    # ------------------------------------------------------------------

    def classify_trend_velocity(self, videos: list[dict]) -> list[dict]:
        """Add velocity label: RISING / PEAKING / DECLINING based on pub date + engagement."""
        now = datetime.utcnow()
        for v in videos:
            published = v.get("published_at", "")
            try:
                pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00")).replace(tzinfo=None)
                age_hours = (now - pub_dt).total_seconds() / 3600
            except (ValueError, TypeError):
                age_hours = 48

            eng = v.get("engagement_pct", 0)
            score = v.get("viral_score", 0)

            if age_hours < 24 and score > 60:
                v["velocity"] = "RISING"
            elif age_hours < 72 and score > 40:
                v["velocity"] = "PEAKING"
            else:
                v["velocity"] = "DECLINING"

        return videos

    # ------------------------------------------------------------------
    # Actionable summary
    # ------------------------------------------------------------------

    def generate_action_plan(
        self,
        merged_hashtags: list[dict],
        viral_patterns: dict,
        niche: str | None = None,
    ) -> dict:
        """Generate a prioritized action plan for content creators."""
        top_tags = [h["hashtag"] for h in merged_hashtags[:5] if h.get("cross_platform")]
        if not top_tags:
            top_tags = [h["hashtag"] for h in merged_hashtags[:5]]

        hooks = viral_patterns.get("hook_patterns", [])
        angles = viral_patterns.get("content_angles", [])
        top_words = [w for w, _ in viral_patterns.get("top_title_words", [])[:5]]

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "niche": niche or "general",
            "immediate_actions": [
                f"Use cross-platform hashtags: {', '.join(top_tags)}",
                f"Optimal video duration: {viral_patterns.get('avg_viral_duration', 'unknown')}",
                f"Top performing title words: {', '.join(top_words)}",
            ],
            "content_strategy": {
                "proven_hooks": hooks,
                "content_angles": angles,
                "post_frequency": "1–2x per day on TikTok, 3–4x per week on YouTube",
            },
            "hashtag_strategy": {
                "primary": top_tags,
                "secondary": [h["hashtag"] for h in merged_hashtags[5:15]],
                "niche_specific": [h["hashtag"] for h in merged_hashtags if not h.get("cross_platform")][:5],
            },
        }
