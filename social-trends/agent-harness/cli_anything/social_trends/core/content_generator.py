"""Content generator — create optimized captions, hashtag stacks, and post schedules.

Takes trend data and generates ready-to-post content packages:
- Captions with hooks and CTAs
- Hashtag stacks (mega + niche + branded)
- Posting schedule
- Sound recommendations
- Cross-platform content repurposing plan
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone


# ── Models ─────────────────────────────────────────────────────────────

@dataclass
class ContentPost:
    """A single ready-to-post content package."""
    platform: str
    post_number: int
    scheduled_time: str
    caption: str
    hashtags: list[str] = field(default_factory=list)
    recommended_sound: str = ""
    content_type: str = ""       # hook | value | trend | entertainment | promo
    hook: str = ""
    cta: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def formatted(self) -> str:
        """Human-readable post card."""
        lines = [
            f"── Post #{self.post_number} ─────────────────────────",
            f"Platform     : {self.platform}",
            f"Schedule     : {self.scheduled_time}",
            f"Type         : {self.content_type}",
            f"Sound        : {self.recommended_sound or 'any trending'}",
            f"",
            f"CAPTION:",
            f"  {self.caption}",
            f"",
            f"HASHTAGS:",
            f"  {' '.join(self.hashtags)}",
        ]
        if self.notes:
            lines += ["", f"NOTES: {self.notes}"]
        return "\n".join(lines)


@dataclass
class ContentPlan:
    """A multi-day content schedule."""
    niche: str
    platform: str
    days: int
    generated_at: str = ""
    posts: list[ContentPost] = field(default_factory=list)
    repurpose_strategy: list[str] = field(default_factory=list)
    weekly_tips: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "niche": self.niche,
            "platform": self.platform,
            "days": self.days,
            "generated_at": self.generated_at,
            "posts": [p.to_dict() for p in self.posts],
            "repurpose_strategy": self.repurpose_strategy,
            "weekly_tips": self.weekly_tips,
        }


# ── Posting time windows ───────────────────────────────────────────────

_BEST_TIMES = {
    "tiktok": [
        (6, 10), (7, 0), (8, 0),   # morning
        (12, 0), (13, 0),           # lunch
        (19, 0), (20, 0), (21, 0),  # evening
    ],
    "youtube": [
        (12, 0), (13, 0), (14, 0),  # lunch
        (15, 0), (16, 0),           # afternoon
        (19, 0), (20, 0),           # evening
    ],
    "instagram": [
        (8, 0), (9, 0),             # morning commute
        (11, 0), (12, 0),           # late morning
        (17, 0), (18, 0), (19, 0),  # after work
    ],
}

_CONTENT_TYPES = [
    "hook",        # pattern interrupt / question / bold claim
    "value",       # educational tip
    "trend",       # trending audio or format
    "entertainment",
    "promo",       # subtle promotion / CTA to bio
]


# ── Hook templates ─────────────────────────────────────────────────────

_HOOKS = {
    "finance": [
        "99% of people don't know this money trick 💸",
        "I made $X in 30 days doing this 👇",
        "The REAL reason you're broke (it's not what you think)",
        "This one habit changed my financial life forever",
        "Millionaires never say this about money…",
    ],
    "luxury": [
        "Wait until you see inside this $X,000,000 home 😱",
        "This is what $X million actually buys you in [city]",
        "Rich people do THIS differently every morning",
        "The most expensive [item] I've ever seen 👀",
    ],
    "fitness": [
        "I tried [challenge] for 30 days — here's what happened",
        "Stop doing [exercise] wrong ❌ Do THIS instead",
        "The workout that changed my body in 8 weeks",
        "No one talks about this fitness mistake 💪",
    ],
    "motivation": [
        "Read this if you feel like giving up 🙏",
        "Your competition isn't sleeping — are you?",
        "One year from now you'll wish you started today",
        "This mindset shift will change your life forever",
    ],
    "default": [
        "Wait for it… 👀",
        "Nobody is talking about this 🤫",
        "I can't believe this actually worked",
        "POV: You finally figure out [niche] 🤯",
        "The secret [niche] experts don't want you to know",
        "If you're not doing this, you're leaving money on the table",
    ],
}

_CTAS = [
    "Follow for more 🔔",
    "Save this for later! 📌",
    "Link in bio for the full guide ↑",
    "Comment 'YES' if this helped you 👇",
    "Share this with someone who needs to see it",
    "Follow + save for part 2 coming tomorrow!",
    "DM me 'INFO' for the full breakdown",
    "Drop a 🔥 if you agree",
    "Which one are you? Comment below 👇",
]


# ── Generator ──────────────────────────────────────────────────────────

class ContentGenerator:
    """Generate ready-to-post content plans from trend data."""

    def generate_plan(
        self,
        niche: str,
        platform: str = "tiktok",
        days: int = 7,
        posts_per_day: int = 2,
        trending_hashtags: list[str] | None = None,
        trending_sounds: list[str] | None = None,
        start_date: datetime | None = None,
    ) -> ContentPlan:
        """Generate a full content posting schedule.

        Args:
            niche: Content niche (finance, fitness, luxury, etc.).
            platform: Target platform (tiktok, youtube, instagram, all).
            days: Number of days to plan.
            posts_per_day: Posts per day (1-3 recommended).
            trending_hashtags: Trending hashtag list to include.
            trending_sounds: Trending sounds to recommend.
            start_date: Start date (defaults to today UTC).
        """
        trending_hashtags = trending_hashtags or []
        trending_sounds = trending_sounds or []
        start_date = start_date or datetime.now(timezone.utc)

        platforms = [platform] if platform != "all" else ["tiktok", "instagram", "youtube"]
        posts = []
        post_number = 1

        for day in range(days):
            date = start_date + timedelta(days=day)
            day_type_index = day % len(_CONTENT_TYPES)

            for p_idx, plat in enumerate(platforms):
                posts_today = posts_per_day if plat != "youtube" else max(1, posts_per_day - 1)
                times = _BEST_TIMES.get(plat, _BEST_TIMES["tiktok"])

                for t_idx in range(posts_today):
                    content_type = _CONTENT_TYPES[(day_type_index + t_idx) % len(_CONTENT_TYPES)]
                    time_tuple = times[t_idx % len(times)]
                    scheduled = date.replace(hour=time_tuple[0], minute=time_tuple[1] if len(time_tuple) > 1 else 0, second=0, microsecond=0)

                    hook = self._pick_hook(niche)
                    cta = random.choice(_CTAS)
                    caption = self._build_caption(niche, content_type, hook, cta)
                    hashtags = self._build_hashtag_stack(niche, plat, trending_hashtags)
                    sound = (trending_sounds[post_number % len(trending_sounds)]
                             if trending_sounds else "")

                    posts.append(ContentPost(
                        platform=plat,
                        post_number=post_number,
                        scheduled_time=scheduled.strftime("%Y-%m-%d %H:%M UTC"),
                        caption=caption,
                        hashtags=hashtags,
                        recommended_sound=sound,
                        content_type=content_type,
                        hook=hook,
                        cta=cta,
                        notes=self._content_notes(content_type, plat),
                    ))
                    post_number += 1

        repurpose = self._repurpose_strategy(platforms)
        tips = self._weekly_tips(niche, platform)

        return ContentPlan(
            niche=niche,
            platform=platform,
            days=days,
            generated_at=datetime.now(timezone.utc).isoformat(),
            posts=posts,
            repurpose_strategy=repurpose,
            weekly_tips=tips,
        )

    def _pick_hook(self, niche: str) -> str:
        hooks = _HOOKS.get(niche.lower(), _HOOKS["default"])
        return random.choice(hooks)

    def _build_caption(self, niche: str, content_type: str, hook: str, cta: str) -> str:
        if content_type == "hook":
            return f"{hook}\n\n{cta}"
        elif content_type == "value":
            return (
                f"{hook}\n\n"
                f"Here's exactly what you need to know about {niche}:\n"
                f"→ Tip 1: [Add your specific value here]\n"
                f"→ Tip 2: [Add your specific value here]\n"
                f"→ Tip 3: [Add your specific value here]\n\n"
                f"{cta}"
            )
        elif content_type == "trend":
            return f"{hook}\n\n[Use trending audio and format for maximum reach]\n\n{cta}"
        elif content_type == "entertainment":
            return f"{hook}\n\n[Add entertaining/relatable content here]\n\n{cta}"
        elif content_type == "promo":
            return (
                f"{hook}\n\n"
                f"I put everything in the link in my bio 🔗\n"
                f"Check it out → link in bio\n\n"
                f"{cta}"
            )
        return f"{hook}\n\n{cta}"

    def _build_hashtag_stack(self, niche: str, platform: str, trending: list[str]) -> list[str]:
        """Build optimized hashtag stack: mega + niche + trending."""
        # Mega hashtags (always high reach)
        mega = ["#fyp", "#foryou", "#viral", "#trending"]

        # Niche-specific hashtags
        niche_ht = {
            "finance": ["#personalfinance", "#moneytips", "#investing", "#financetok", "#richhabits"],
            "luxury": ["#luxury", "#luxurylifestyle", "#rich", "#millionaire", "#luxuryhomes"],
            "fitness": ["#fitness", "#gym", "#workout", "#fitnesstok", "#bodybuilding", "#gains"],
            "motivation": ["#motivation", "#mindset", "#success", "#hustle", "#motivational"],
            "crypto": ["#crypto", "#bitcoin", "#ethereum", "#web3", "#nft"],
            "cars": ["#cars", "#supercar", "#automotive", "#carporn", "#carsoftiktok"],
            "food": ["#food", "#foodtok", "#recipe", "#cooking", "#foodie"],
            "fashion": ["#fashion", "#ootd", "#style", "#outfitinspo", "#fashiontok"],
        }.get(niche.lower(), [f"#{niche.lower()}", f"#{niche.lower()}tok"])

        if platform == "youtube":
            mega = ["#Shorts", "#YouTubeShorts", f"#{niche}shorts"]
        elif platform == "instagram":
            mega = ["#reels", "#reelsinstagram", "#explore", "#viral"]

        # Build stack: 2 mega + 3-4 niche + 1-2 trending
        stack = mega[:2] + niche_ht[:3]
        for ht in trending[:3]:
            cleaned = ht.lstrip("#")
            if f"#{cleaned}" not in stack:
                stack.append(f"#{cleaned}")

        return stack[:10]

    def _content_notes(self, content_type: str, platform: str) -> str:
        notes = {
            "hook": "Open with bold visual or text overlay matching the hook. No intro needed.",
            "value": "Use text overlays for each tip. Save-bait format → high saves = algorithm boost.",
            "trend": "Find #1 trending sound, use it with your niche content. Post within 24h of sound trending.",
            "entertainment": "Higher share rate = more reach. Make it relatable or surprising.",
            "promo": "Keep promo subtle — 80% value, 20% CTA. Hard sells get skipped.",
        }
        base = notes.get(content_type, "")
        if platform == "youtube":
            base += " For Shorts: hook in first frame, loop seamlessly."
        return base

    def _repurpose_strategy(self, platforms: list[str]) -> list[str]:
        return [
            "REPURPOSE WORKFLOW (1 video → 3-5 pieces of content):",
            "1. Film 60s vertical video (9:16, 1080x1920)",
            "2. Post full version on TikTok with trending sound",
            "3. Trim to 30s → post on Instagram Reels",
            "4. Upload to YouTube Shorts (add #Shorts to description)",
            "5. Extract audio → post as Twitter/X voice clip or podcast episode",
            "6. Screenshot best frame → post as Instagram/Twitter image with key quote",
            "TOOLS: CapCut (free), InShot, Canva for thumbnails",
            "BATCH FILM: Record 5-7 videos in one session to stay consistent",
        ]

    def _weekly_tips(self, niche: str, platform: str) -> list[str]:
        return [
            f"WEEKLY {niche.upper()} CONTENT TIPS:",
            "Monday: Educational — '3 things about [niche] most people get wrong'",
            "Tuesday: Trending format — use #1 sound in your niche category",
            "Wednesday: Repurpose a top-performing post with a new angle",
            "Thursday: Behind-the-scenes — builds trust and authenticity",
            "Friday: Entertainment/comedy — gets shares, peaks before weekend",
            "Saturday: Aspirational — aspirational content saves drive reach",
            "Sunday: Community — 'Which do you prefer?' or Q&A drives comments",
            "",
            "ANALYTICS CHECK (every Sunday):",
            "  → What was your highest-reach post this week? Why?",
            "  → What was your lowest? Cut that format.",
            "  → Which hashtags are driving impressions? Double down.",
            "  → Best posting time this week? Optimize schedule next week.",
        ]
