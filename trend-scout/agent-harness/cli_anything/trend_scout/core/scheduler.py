"""Content calendar and auto-scheduler: generates posting schedules based on trend data."""

import json
from datetime import datetime, timedelta
from typing import Any


PLATFORM_POST_TIMES = {
    "tiktok": {
        "US": [
            {"day": "Monday", "times": ["6:00 AM", "10:00 AM", "7:00 PM"]},
            {"day": "Tuesday", "times": ["9:00 AM", "12:00 PM", "7:00 PM"]},
            {"day": "Wednesday", "times": ["7:00 AM", "11:00 AM", "8:00 PM"]},
            {"day": "Thursday", "times": ["9:00 AM", "12:00 PM", "7:00 PM"]},
            {"day": "Friday", "times": ["5:00 AM", "1:00 PM", "3:00 PM"]},
            {"day": "Saturday", "times": ["11:00 AM", "7:00 PM", "8:00 PM"]},
            {"day": "Sunday", "times": ["7:00 AM", "8:00 AM", "4:00 PM"]},
        ],
        "GB": [
            {"day": "Monday", "times": ["7:00 AM", "12:00 PM", "8:00 PM"]},
            {"day": "Tuesday", "times": ["7:00 AM", "2:00 PM", "9:00 PM"]},
            {"day": "Thursday", "times": ["9:00 AM", "7:00 PM", "9:00 PM"]},
            {"day": "Friday", "times": ["5:00 AM", "1:00 PM", "3:00 PM"]},
        ],
    },
    "youtube": {
        "US": [
            {"day": "Thursday", "times": ["2:00 PM", "3:00 PM", "4:00 PM"]},
            {"day": "Friday", "times": ["12:00 PM", "3:00 PM", "4:00 PM"]},
            {"day": "Saturday", "times": ["9:00 AM", "11:00 AM"]},
            {"day": "Sunday", "times": ["9:00 AM", "11:00 AM"]},
        ],
    },
    "instagram": {
        "US": [
            {"day": "Monday", "times": ["6:00 AM", "10:00 AM", "10:00 PM"]},
            {"day": "Tuesday", "times": ["2:00 AM", "4:00 AM", "9:00 AM"]},
            {"day": "Wednesday", "times": ["7:00 AM", "8:00 AM", "11:00 PM"]},
            {"day": "Thursday", "times": ["9:00 AM", "12:00 PM", "7:00 PM"]},
            {"day": "Friday", "times": ["5:00 AM", "1:00 PM", "3:00 PM"]},
        ],
    },
}

CONTENT_TYPES = {
    "tiktok": ["Hook video", "Tutorial", "POV", "Storytime", "Day in my life", "Duet/Stitch", "Trending sound"],
    "youtube": ["Long-form explainer", "YouTube Short", "Tutorial", "Vlog", "Review", "Compilation"],
    "instagram": ["Reel", "Carousel post", "Story", "Static post", "Collab Reel"],
}


class ContentScheduler:
    """Generates content calendars and posting schedules based on trend data."""

    def generate_weekly_calendar(
        self,
        platforms: list[str],
        niche: str,
        posts_per_day: int = 2,
        region: str = "US",
        content_ideas: list[dict] | None = None,
        trending_hashtags: list[dict] | None = None,
        trending_sounds: list[dict] | None = None,
    ) -> dict:
        """Generate a full 7-day content calendar."""
        start_date = datetime.utcnow()
        calendar = {}

        ideas = content_ideas or self._default_ideas(niche)
        hashtags = [h.get("hashtag", "") for h in (trending_hashtags or [])][:10]
        sounds = [s.get("title", "") for s in (trending_sounds or [])][:5]
        idea_pool = list(ideas) * 10  # repeat pool to fill week

        idea_idx = 0
        for day_offset in range(7):
            date = start_date + timedelta(days=day_offset)
            day_name = date.strftime("%A")
            date_str = date.strftime("%Y-%m-%d")
            day_posts = []

            for platform in platforms:
                platform_lower = platform.lower()
                post_times = self._get_post_times(platform_lower, region, day_name, posts_per_day)
                content_type_pool = CONTENT_TYPES.get(platform_lower, ["Video"])

                for i, post_time in enumerate(post_times):
                    idea = idea_pool[idea_idx % len(idea_pool)]
                    idea_idx += 1
                    content_type = content_type_pool[i % len(content_type_pool)]
                    sound = sounds[idea_idx % len(sounds)] if sounds else "Trending sound from TikTok Discover"
                    day_posts.append({
                        "platform": platform,
                        "post_time": post_time,
                        "content_type": content_type,
                        "title_idea": idea.get("title", f"{niche} content idea"),
                        "format": idea.get("format", "Video"),
                        "suggested_sound": sound if platform_lower in ["tiktok", "instagram"] else None,
                        "hashtags": hashtags[:5] + ["#fyp", "#viral"] if platform_lower == "tiktok" else hashtags[:3],
                        "caption_starter": self._caption_starter(idea.get("title", ""), niche),
                        "status": "scheduled",
                    })

            calendar[date_str] = {
                "day": day_name,
                "posts": sorted(day_posts, key=lambda x: x["post_time"]),
                "tip": self._daily_tip(day_name),
            }

        return {
            "week_start": start_date.strftime("%Y-%m-%d"),
            "niche": niche,
            "platforms": platforms,
            "region": region,
            "calendar": calendar,
            "total_posts_planned": sum(len(v["posts"]) for v in calendar.values()),
            "batch_recording_tip": self._batch_tip(len(platforms), posts_per_day),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def generate_monthly_plan(
        self,
        platforms: list[str],
        niche: str,
        posts_per_week: int = 14,
        region: str = "US",
    ) -> dict:
        """Generate a high-level 30-day content plan."""
        weeks = []
        for week_num in range(1, 5):
            week_theme = self._get_week_theme(week_num, niche)
            weeks.append({
                "week": week_num,
                "theme": week_theme["theme"],
                "content_focus": week_theme["focus"],
                "post_count_target": posts_per_week,
                "content_mix": {
                    "educational": f"{int(posts_per_week * 0.4)} posts",
                    "entertaining": f"{int(posts_per_week * 0.3)} posts",
                    "personal": f"{int(posts_per_week * 0.2)} posts",
                    "promotional": f"{max(1, int(posts_per_week * 0.1))} posts",
                },
                "milestones": week_theme.get("milestones", []),
            })

        return {
            "month": datetime.utcnow().strftime("%B %Y"),
            "niche": niche,
            "platforms": platforms,
            "total_posts_target": posts_per_week * 4,
            "weekly_plans": weeks,
            "month_goals": self._monthly_goals(niche),
            "tools_for_scheduling": [
                "TikTok native scheduler (free, in-app)",
                "Later — Instagram + TikTok ($16/mo)",
                "Publer — multi-platform ($12/mo)",
                "Buffer — Twitter + Instagram + Facebook (free tier)",
                "Hootsuite — enterprise ($99/mo)",
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_posting_frequency_recommendation(self, platform: str, current_followers: int, niche: str) -> dict:
        """Return posting frequency recommendation based on platform and growth stage."""
        recommendations = {
            "tiktok": {
                "0-1k": {"posts_per_day": "2-4", "rationale": "Algorithm rewards new accounts that post high volume"},
                "1k-10k": {"posts_per_day": "1-3", "rationale": "Consistency matters more than volume now"},
                "10k-100k": {"posts_per_day": "1-2", "rationale": "Focus on quality — you have enough reach"},
                "100k+": {"posts_per_day": "1", "rationale": "One great post beats three mediocre ones"},
            },
            "youtube": {
                "0-1k": {"posts_per_week": "3-5 Shorts + 1 long-form", "rationale": "Shorts build fast; long-form builds subs"},
                "1k-10k": {"posts_per_week": "2-3 Shorts + 1 long-form", "rationale": "Grow via Shorts, monetize via long-form"},
                "10k+": {"posts_per_week": "1-2 long-form + daily Shorts", "rationale": "Long-form = ad revenue; Shorts = discovery"},
            },
            "instagram": {
                "0-1k": {"posts_per_day": "1-2 Reels + 3-5 Stories", "rationale": "Reels for reach, Stories for retention"},
                "1k-10k": {"posts_per_day": "1 Reel + 3 Stories + 2 Carousels/week", "rationale": "Mix formats for algorithm diversity"},
                "10k+": {"posts_per_day": "1 Reel + Stories daily + 1 Carousel", "rationale": "Diversified content mix for peak reach"},
            },
        }
        platform_lower = platform.lower()
        tier = self._get_tier_key(current_followers)
        platform_recs = recommendations.get(platform_lower, {})
        rec = platform_recs.get(tier, {"note": "Post consistently for your platform"})

        return {
            "platform": platform,
            "niche": niche,
            "follower_count": current_followers,
            "tier": tier,
            "recommendation": rec,
            "consistency_tip": "Missing 3+ days resets your algorithm momentum — schedule posts in advance",
            "best_times": self._get_post_times_dict(platform_lower, "US"),
        }

    def export_to_notion_format(self, calendar: dict) -> str:
        """Export calendar as markdown table (paste into Notion)."""
        lines = ["# Content Calendar\n"]
        lines.append("| Date | Day | Platform | Time | Content Type | Title Idea | Hashtags |")
        lines.append("|------|-----|----------|------|--------------|------------|----------|")
        for date_str, day_data in calendar.get("calendar", {}).items():
            for post in day_data.get("posts", []):
                tags = " ".join(post.get("hashtags", [])[:3])
                lines.append(
                    f"| {date_str} | {day_data['day']} | {post['platform']} | "
                    f"{post['post_time']} | {post['content_type']} | "
                    f"{post['title_idea'][:50]} | {tags} |"
                )
        return "\n".join(lines)

    def export_to_csv(self, calendar: dict) -> str:
        """Export calendar as CSV string."""
        lines = ["date,day,platform,time,content_type,title_idea,hashtags,sound,status"]
        for date_str, day_data in calendar.get("calendar", {}).items():
            for post in day_data.get("posts", []):
                tags = "|".join(post.get("hashtags", [])[:5])
                sound = post.get("suggested_sound", "") or ""
                title = post["title_idea"].replace(",", ";")
                lines.append(
                    f"{date_str},{day_data['day']},{post['platform']},"
                    f"{post['post_time']},{post['content_type']},"
                    f"\"{title}\",\"{tags}\",\"{sound}\",{post.get('status', 'scheduled')}"
                )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_post_times(self, platform: str, region: str, day_name: str, count: int) -> list[str]:
        region_times = PLATFORM_POST_TIMES.get(platform, {}).get(region, PLATFORM_POST_TIMES.get(platform, {}).get("US", []))
        for day_data in region_times:
            if day_data["day"] == day_name:
                return day_data["times"][:count]
        # Fallback times
        fallback = {"tiktok": ["7:00 AM", "12:00 PM", "7:00 PM"], "youtube": ["2:00 PM", "4:00 PM"], "instagram": ["9:00 AM", "7:00 PM"]}
        return fallback.get(platform, ["12:00 PM"])[:count]

    def _get_post_times_dict(self, platform: str, region: str) -> dict:
        region_times = PLATFORM_POST_TIMES.get(platform, {}).get(region, [])
        return {d["day"]: d["times"] for d in region_times}

    def _caption_starter(self, title: str, niche: str) -> str:
        hooks = [
            f"Nobody talks about this 👇",
            f"This changed everything for me 🎯",
            f"Save this before you forget ✅",
            f"If you're into {niche}, you need this 💡",
            f"The truth about {niche} 👇",
        ]
        import hashlib
        idx = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(hooks)
        return hooks[idx]

    def _daily_tip(self, day_name: str) -> str:
        tips = {
            "Monday": "Monday posts get lower reach — use it to test new formats",
            "Tuesday": "Tuesday + Thursday peak engagement days — post your best content",
            "Wednesday": "Wednesday: great day for educational content",
            "Thursday": "Thursday: highest engagement day on most platforms — post your best",
            "Friday": "Friday afternoon: high views as people scroll heading into weekend",
            "Saturday": "Saturday morning performs well — people scroll during downtime",
            "Sunday": "Sunday: prep and batch content for the week, post 1 banger",
        }
        return tips.get(day_name, "Engage with your niche 30 min after posting")

    def _default_ideas(self, niche: str) -> list[dict]:
        return [
            {"title": f"Things {niche} beginners need to know", "format": "Educational"},
            {"title": f"My {niche} routine that actually works", "format": "Day-in-life"},
            {"title": f"Honest review: [top {niche} product]", "format": "Review"},
            {"title": f"The {niche} tip that changed everything", "format": "Tips"},
            {"title": f"POV: You discover {niche}", "format": "POV"},
            {"title": f"Things I wish I knew about {niche}", "format": "Educational"},
            {"title": f"Hot take: [controversial {niche} opinion]", "format": "Opinion"},
            {"title": f"I tried [{niche} trend] for 7 days", "format": "Challenge"},
            {"title": f"Rating viral {niche} hacks (honest)", "format": "Entertainment"},
            {"title": f"How I got into {niche} (storytime)", "format": "Storytime"},
            {"title": f"The {niche} products I actually use", "format": "Recommendations"},
            {"title": f"Q&A: Your {niche} questions answered", "format": "Q&A"},
            {"title": f"Biggest {niche} myths debunked", "format": "Educational"},
            {"title": f"Before vs after: {niche} transformation", "format": "Before/After"},
        ]

    def _get_week_theme(self, week_num: int, niche: str) -> dict:
        themes = [
            {
                "theme": "Foundation Week",
                "focus": f"Introduce yourself and your {niche} perspective",
                "milestones": ["First 100 followers", "Establish brand voice"],
            },
            {
                "theme": "Education Week",
                "focus": f"Deep-dive tutorials and tips for {niche}",
                "milestones": ["First viral post", "Grow email list"],
            },
            {
                "theme": "Engagement Week",
                "focus": "Interactive content: Q&As, polls, challenges",
                "milestones": ["First collab", "Hit engagement rate target"],
            },
            {
                "theme": "Monetization Week",
                "focus": "Soft promotions, affiliate content, product mentions",
                "milestones": ["First affiliate click", "First brand inquiry"],
            },
        ]
        return themes[(week_num - 1) % len(themes)]

    def _monthly_goals(self, niche: str) -> list[str]:
        return [
            "Gain 500-2,000 new followers across all platforms",
            "Post consistently without missing a day",
            "Generate first affiliate revenue (even $1 proves the model)",
            "Identify your top 3 performing content formats",
            "Build email list to 50+ subscribers",
            "Engage with 5 creators in your niche for relationship building",
        ]

    def _batch_tip(self, num_platforms: int, posts_per_day: int) -> str:
        total_weekly = num_platforms * posts_per_day * 7
        return (
            f"You're planning ~{total_weekly} posts/week across {num_platforms} platforms. "
            f"Batch record on Sunday (3-4 hours) and edit Monday morning. "
            f"Use CapCut's 'duplicate draft' feature to repurpose one video to multiple formats."
        )

    def _get_tier_key(self, followers: int) -> str:
        if followers < 1000:
            return "0-1k"
        elif followers < 10_000:
            return "1k-10k"
        elif followers < 100_000:
            return "10k-100k"
        else:
            return "100k+"
