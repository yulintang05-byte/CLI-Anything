"""Content calendar generator: 30-day schedule with trending hooks and themes."""

from datetime import datetime, timedelta
from typing import Any


CONTENT_PILLARS: dict[str, list[str]] = {
    "motivation": ["Quote post", "Success story", "Mindset tip", "Failure lesson", "Daily challenge"],
    "fitness": ["Workout demo", "Nutrition tip", "Before/after", "Form check", "Q&A session"],
    "finance": ["Market update", "Investing tip", "Case study", "Tool review", "Mistake to avoid"],
    "cars": ["Car spot", "Spec breakdown", "Mod reveal", "Driving footage", "History fact"],
    "food": ["Recipe video", "Restaurant review", "Cooking hack", "Ingredient tip", "Meal prep"],
    "beauty": ["Tutorial", "Product review", "Skincare routine", "GRWM", "Product dupe"],
    "gaming": ["Gameplay highlight", "Tips & tricks", "Game review", "Challenge run", "News reaction"],
    "anime": ["Episode edit", "Character analysis", "Recommendation list", "Manga vs anime", "Top 10"],
    "luxury": ["Item showcase", "Brand story", "How to afford", "Investment piece", "Haul"],
}

WEEKLY_THEMES = [
    "Value Week — pure educational content, no selling",
    "Engagement Week — question-based posts, polls, duets",
    "Trending Week — ride all viral trends in your niche",
    "Personal Week — behind-the-scenes, your story, journey",
]

CAPTION_HOOKS = [
    "Nobody talks about this, but...",
    "I tested this for 30 days and here's what happened:",
    "Stop doing this if you want [result]:",
    "The secret that [niche] pros don't tell you:",
    "This changed everything for me:",
    "POV: you finally figured out [topic]",
    "The #1 mistake most [niche] beginners make:",
    "What I wish I knew before starting [niche]:",
    "Day [X] of [challenge] — here's my progress:",
    "How I went from 0 to [result] in [timeframe]:",
]


class ContentCalendar:
    """Generate structured content calendars with hooks, themes, and hashtags."""

    def generate(
        self,
        niche: str,
        platform: str,
        days: int = 30,
        posts_per_day: int = 1,
        trending_hashtags: list[str] | None = None,
    ) -> dict:
        """Generate a full content calendar."""
        pillars = CONTENT_PILLARS.get(niche.lower(), ["Tips", "Story", "Tutorial", "Reaction", "Update"])
        start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        calendar: list[dict] = []
        for day_offset in range(days):
            date = start + timedelta(days=day_offset)
            week_num = day_offset // 7
            theme = WEEKLY_THEMES[week_num % len(WEEKLY_THEMES)]
            pillar = pillars[day_offset % len(pillars)]
            hook = CAPTION_HOOKS[day_offset % len(CAPTION_HOOKS)]
            hashtags = self._pick_hashtags(trending_hashtags or [], day_offset)

            posts = []
            for post_num in range(posts_per_day):
                posts.append({
                    "post_number": post_num + 1,
                    "format": self._format_for_platform(platform, pillar),
                    "content_pillar": pillar,
                    "hook": hook,
                    "caption_template": self._caption_template(hook, niche, pillar),
                    "hashtags": hashtags,
                    "cta": self._pick_cta(day_offset),
                })

            calendar.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_of_week": date.strftime("%A"),
                "week_theme": theme,
                "posts": posts,
            })

        stats = self._calendar_stats(calendar, days, posts_per_day)

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "niche": niche,
            "platform": platform,
            "total_days": days,
            "posts_per_day": posts_per_day,
            "total_posts": days * posts_per_day,
            "calendar": calendar,
            "stats": stats,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _format_for_platform(platform: str, pillar: str) -> str:
        format_map = {
            "tiktok": "Short-form video (15–60s)",
            "youtube": "Long-form video (8–20min)" if pillar in ["Tutorial", "Review", "Case study"] else "YouTube Short (60s)",
            "instagram": "Reel (15–30s)" if "video" in pillar.lower() or "reel" in pillar.lower() else "Carousel (5–10 slides)",
        }
        return format_map.get(platform.lower(), "Video")

    @staticmethod
    def _pick_hashtags(trending: list[str], day_offset: int) -> list[str]:
        base = ["#fyp", "#viral", "#foryou", "#trending"]
        if trending:
            batch_start = (day_offset * 5) % max(len(trending), 1)
            rotated = trending[batch_start:batch_start + 5]
            return list(dict.fromkeys(rotated + base))[:9]
        return base

    @staticmethod
    def _caption_template(hook: str, niche: str, pillar: str) -> str:
        return f"{hook}\n\n[Write your {niche} {pillar.lower()} content here]\n\n[3–5 sentence body]\n\n[CTA line]"

    @staticmethod
    def _pick_cta(day_offset: int) -> str:
        ctas = [
            "Follow for daily [niche] content!",
            "Save this for later! 🔖",
            "Tag someone who needs to see this",
            "What do you think? Comment below!",
            "Share this with a friend!",
            "DM me '[keyword]' for the full guide",
            "Turn on post notifications so you don't miss our next video!",
        ]
        return ctas[day_offset % len(ctas)]

    @staticmethod
    def _calendar_stats(calendar: list[dict], days: int, ppd: int) -> dict:
        pillar_counts: dict[str, int] = {}
        for day in calendar:
            for post in day["posts"]:
                p = post["content_pillar"]
                pillar_counts[p] = pillar_counts.get(p, 0) + 1
        return {
            "total_posts": days * ppd,
            "content_pillar_distribution": pillar_counts,
            "unique_hooks_used": min(days * ppd, len(CAPTION_HOOKS)),
            "weekly_themes_covered": WEEKLY_THEMES,
        }

    # ------------------------------------------------------------------
    # Weekly sprint (7-day focused view)
    # ------------------------------------------------------------------

    def weekly_sprint(self, niche: str, platform: str, trending_hashtags: list[str] | None = None) -> dict:
        full = self.generate(niche, platform, days=7, posts_per_day=2, trending_hashtags=trending_hashtags)
        return {
            "week_sprint": full["calendar"],
            "total_posts": full["total_posts"],
            "niche": niche,
            "platform": platform,
            "tip": "Batch-create all 14 pieces on Sunday, schedule with Buffer or Later",
        }

    # ------------------------------------------------------------------
    # Export to CSV-friendly format
    # ------------------------------------------------------------------

    def to_rows(self, calendar: dict) -> list[list[str]]:
        """Flatten calendar to list of rows for CSV export."""
        rows = [["Date", "Day", "Week Theme", "Post #", "Format", "Pillar", "Hook", "CTA", "Hashtags"]]
        for day in calendar.get("calendar", []):
            for post in day["posts"]:
                rows.append([
                    day["date"],
                    day["day_of_week"],
                    day["week_theme"],
                    str(post["post_number"]),
                    post["format"],
                    post["content_pillar"],
                    post["hook"][:60],
                    post["cta"],
                    " ".join(post["hashtags"]),
                ])
        return rows
