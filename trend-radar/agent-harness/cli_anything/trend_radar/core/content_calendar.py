"""Content Calendar — Generate structured posting schedules from trend data."""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

CONTENT_FORMATS: dict[str, list[str]] = {
    "instagram": ["reel", "carousel", "photo", "story", "live"],
    "tiktok":    ["video", "duet", "stitch", "live", "photo_mode"],
    "youtube":   ["short", "tutorial", "vlog", "review", "live"],
    "all":       ["reel", "carousel", "video", "story", "photo"],
}

TOPIC_TEMPLATES: dict[str, list[str]] = {
    "fitness": [
        "5-minute morning workout to start your day right",
        "What I eat in a day (tracking macros for my goals)",
        "My biggest fitness mistake and how to fix it",
        "Progress check: weeks of consistency results",
        "Best exercises for building strength at home",
        "Morning routine that transformed my physique",
        "Rest day activities that actually support recovery",
        "One exercise that changed my body in 30 days",
    ],
    "food": [
        "5-ingredient recipe ready in 20 minutes",
        "Meal prep Sunday: 5 days of food in 1 hour",
        "Restaurant-quality meal made at home for under $10",
        "Viral recipe — does it actually taste good?",
        "Budget meal: feeding 4 people for $15",
        "The cooking hack that changed everything for me",
        "Honest taste test: store-bought vs. homemade",
        "The one recipe I make every single week",
    ],
    "travel": [
        "Budget guide: everything you need for this destination",
        "Things nobody tells you before you visit this place",
        "My top hidden gems most tourists miss",
        "7-day itinerary under $1,500 total",
        "How I afford to travel every month on a normal salary",
        "Packing light: everything I bring in a carry-on",
        "Travel mistakes I'll never make again",
        "Solo trip experience: what I learned",
    ],
    "finance": [
        "How I saved $10,000 in 12 months on a normal income",
        "Beginner's guide to starting investing with $100",
        "Passive income stream: how I built it and what it pays",
        "The budgeting method that finally worked for me",
        "Month-by-month breakdown of my financial journey",
        "How I negotiated a $15,000 raise (exact script)",
        "Emergency fund: how much you actually need",
        "The financial mistake 90% of people in their 20s make",
    ],
    "general": [
        "This one thing changed how I approach everything",
        "5 things I wish I knew before starting",
        "My honest opinion on the trend everyone's talking about",
        "Day in my life (unfiltered)",
        "Why I quit this habit and what happened next",
        "Algorithm update: what's actually working right now",
        "Honest review after using this for 90 days",
        "The question everyone keeps asking me, answered",
    ],
}

BEST_TIMES: dict[str, dict[str, list[str]]] = {
    "instagram": {
        "monday":    ["9:00 AM", "12:00 PM", "7:00 PM"],
        "tuesday":   ["8:00 AM",  "1:00 PM", "7:00 PM"],
        "wednesday": ["11:00 AM", "1:00 PM", "8:00 PM"],
        "thursday":  ["12:00 PM", "7:00 PM", "9:00 PM"],
        "friday":    ["10:00 AM", "1:00 PM", "8:00 PM"],
        "saturday":  ["9:00 AM", "11:00 AM", "7:00 PM"],
        "sunday":    ["10:00 AM", "2:00 PM",  "5:00 PM"],
    },
    "tiktok": {
        "monday":    ["6:00 AM", "10:00 AM", "10:00 PM"],
        "tuesday":   ["9:00 AM",  "2:00 PM",  "9:00 PM"],
        "wednesday": ["7:00 AM", "11:00 AM",  "9:00 PM"],
        "thursday":  ["9:00 AM", "12:00 PM",  "8:00 PM"],
        "friday":    ["5:00 AM",  "1:00 PM",  "3:00 PM"],
        "saturday":  ["11:00 AM", "7:00 PM",  "8:00 PM"],
        "sunday":    ["7:00 AM",  "8:00 AM",  "4:00 PM"],
    },
    "youtube": {
        "monday":    ["2:00 PM", "4:00 PM",  "9:00 PM"],
        "tuesday":   ["3:00 PM", "7:00 PM",  "9:00 PM"],
        "wednesday": ["3:00 PM", "7:00 PM",  "9:00 PM"],
        "thursday":  ["12:00 PM", "3:00 PM", "7:00 PM"],
        "friday":    ["12:00 PM", "3:00 PM", "4:00 PM"],
        "saturday":  ["9:00 AM", "11:00 AM", "1:00 PM"],
        "sunday":    ["9:00 AM", "11:00 AM", "12:00 PM"],
    },
}

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


class ContentCalendar:
    """Generate and export structured content calendars."""

    def generate(
        self,
        niche: str,
        platform: str = "instagram",
        weeks: int = 4,
        posts_per_week: int = 5,
    ) -> dict:
        """Generate a content calendar.

        Returns dict with niche, platform, total_posts, and a weeks list where
        each week has a date_range and list of post dicts.
        """
        from cli_anything.trend_radar.core.hashtag_optimizer import HashtagOptimizer
        hashtag_pool = HashtagOptimizer().generate_set(
            niche=niche, platform=platform, count=20
        )["all_tags"]

        templates = TOPIC_TEMPLATES.get(niche.lower(), TOPIC_TEMPLATES["general"])
        formats   = CONTENT_FORMATS.get(platform, CONTENT_FORMATS["all"])
        times_db  = BEST_TIMES.get(platform, BEST_TIMES["instagram"])

        today = date.today()
        days_to_monday = (7 - today.weekday()) % 7 or 7
        start = today + timedelta(days=days_to_monday)

        calendar_weeks = []
        post_counter = 0
        for week_num in range(1, weeks + 1):
            week_start = start + timedelta(weeks=week_num - 1)
            week_end   = week_start + timedelta(days=6)
            selected_days = sorted(random.sample(DAYS, min(posts_per_week, 7)))

            posts = []
            for i, day_name in enumerate(selected_days):
                post_counter += 1
                day_date = week_start + timedelta(days=DAYS.index(day_name))
                topic    = random.choice(templates)
                fmt      = random.choice(formats)
                times    = times_db.get(day_name, ["12:00 PM"])
                tags     = random.sample(hashtag_pool, min(6, len(hashtag_pool)))

                posts.append({
                    "day":         day_name.title(),
                    "date":        str(day_date),
                    "format":      fmt,
                    "topic":       topic,
                    "hashtags":    tags,
                    "best_time":   times[0],
                    "week_number": week_num,
                    "post_number": post_counter,
                })

            calendar_weeks.append({
                "week_number": week_num,
                "date_range":  f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d, %Y')}",
                "start_date":  str(week_start),
                "end_date":    str(week_end),
                "posts":       posts,
            })

        return {
            "niche":          niche,
            "platform":       platform,
            "weeks":          weeks,
            "posts_per_week": posts_per_week,
            "total_posts":    post_counter,
            "generated_date": str(today),
            "weeks":          calendar_weeks,
        }

    def export_csv(self, calendar: dict, path: str):
        """Export calendar to a CSV file."""
        rows = []
        for week in calendar.get("weeks", []):
            for post in week.get("posts", []):
                rows.append({
                    "week":      week["week_number"],
                    "day":       post["day"],
                    "date":      post["date"],
                    "format":    post["format"],
                    "topic":     post["topic"],
                    "hashtags":  " ".join(f"#{h}" for h in post.get("hashtags", [])),
                    "best_time": post.get("best_time", ""),
                })
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

    def export_json(self, calendar: dict, path: str):
        """Export calendar to a JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(calendar, f, indent=2, ensure_ascii=False)
