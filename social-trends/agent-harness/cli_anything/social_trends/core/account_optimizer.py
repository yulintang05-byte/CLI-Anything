"""Account optimization engine for YouTube and TikTok accounts.

Covers:
  - Profile audit (bio, avatar, link-in-bio, CTA)
  - Posting schedule optimization by platform + timezone
  - Content calendar generation
  - Engagement rate benchmarks
  - Growth lever recommendations
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class AuditItem:
    category: str
    item: str
    status: str        # "pass", "warn", "fail"
    recommendation: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ProfileAudit:
    platform: str
    handle: str
    score: int          # 0–100
    items: List[AuditItem]
    top_actions: List[str]

    def to_dict(self) -> Dict:
        return {
            "platform": self.platform,
            "handle": self.handle,
            "score": self.score,
            "items": [i.to_dict() for i in self.items],
            "top_actions": self.top_actions,
        }


@dataclass
class PostSlot:
    day: str
    time_local: str
    priority: str   # "best", "good", "ok"
    reason: str

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContentCalendarEntry:
    date: str
    day_of_week: str
    post_time: str
    content_type: str
    topic_idea: str
    hashtag_set: List[str]
    notes: str

    def to_dict(self) -> Dict:
        return asdict(self)


# ── Engagement benchmarks ─────────────────────────────────────────────────────

ENGAGEMENT_BENCHMARKS = {
    "tiktok": {
        "nano":   {"followers": (1_000, 10_000),   "eng_rate": 9.38},
        "micro":  {"followers": (10_000, 100_000), "eng_rate": 7.20},
        "mid":    {"followers": (100_000, 500_000), "eng_rate": 5.30},
        "macro":  {"followers": (500_000, 1_000_000), "eng_rate": 4.10},
        "mega":   {"followers": (1_000_000, float("inf")), "eng_rate": 3.50},
    },
    "youtube": {
        "small":  {"subscribers": (1_000, 10_000),    "eng_rate": 3.5},
        "medium": {"subscribers": (10_000, 100_000),  "eng_rate": 2.0},
        "large":  {"subscribers": (100_000, 1_000_000), "eng_rate": 1.5},
        "mega":   {"subscribers": (1_000_000, float("inf")), "eng_rate": 0.8},
    },
}


# ── Posting schedules (researched optimal times) ──────────────────────────────

OPTIMAL_POSTING_TIMES = {
    "tiktok": [
        PostSlot("Tuesday",   "09:00", "best", "Highest FYP push window"),
        PostSlot("Thursday",  "12:00", "best", "Lunch scroll peak"),
        PostSlot("Friday",    "17:00", "best", "End-of-week momentum"),
        PostSlot("Monday",    "07:00", "good", "Morning routine scroll"),
        PostSlot("Wednesday", "11:00", "good", "Mid-week engagement"),
        PostSlot("Saturday",  "11:00", "good", "Weekend leisure scroll"),
        PostSlot("Sunday",    "20:00", "ok",   "Evening browse before work week"),
    ],
    "youtube": [
        PostSlot("Thursday", "14:00", "best", "Algorithm indexes before weekend peak"),
        PostSlot("Friday",   "12:00", "best", "Friday lunch + weekend boost"),
        PostSlot("Saturday", "10:00", "best", "Weekend morning watch session"),
        PostSlot("Tuesday",  "15:00", "good", "Post-school/work browse"),
        PostSlot("Wednesday","14:00", "good", "Mid-week viewing"),
        PostSlot("Sunday",   "14:00", "good", "Sunday afternoon viewing"),
        PostSlot("Monday",   "12:00", "ok",   "Week start content"),
    ],
    "instagram": [
        PostSlot("Monday",    "11:00", "best", "Week start motivation content"),
        PostSlot("Wednesday", "11:00", "best", "Mid-week engagement peak"),
        PostSlot("Friday",    "10:00", "best", "TGIF shareability"),
        PostSlot("Tuesday",   "14:00", "good", "Afternoon browse"),
        PostSlot("Thursday",  "12:00", "good", "Lunch engagement"),
        PostSlot("Saturday",  "09:00", "good", "Morning inspiration scroll"),
    ],
}


# ── Profile audit ─────────────────────────────────────────────────────────────

_PROFILE_CHECKLIST = {
    "tiktok": [
        ("bio",        "Bio is 80 chars max, includes niche keyword + CTA",
         "Add your niche + 'Follow for [value prop]' or link CTA"),
        ("username",   "Username matches content niche and is < 20 chars",
         "Shorter, niche-relevant usernames rank better in search"),
        ("avatar",     "Profile photo is high-res, face visible or clear logo",
         "Faces outperform logos for personal accounts by 38%"),
        ("link",       "Link in bio points to a funnel (Linktree, Beacons, or landing page)",
         "Every profile needs a destination — link to your top resource"),
        ("pinned",     "Top 3 pinned videos showcase your best/most viral content",
         "First impressions: pin your 3 highest-performing videos"),
        ("consistency","Posts at least 3–5x per week in a consistent niche",
         "TikTok rewards consistent daily posting — aim for 1–3/day"),
        ("niche",      "All content is within 1–2 related topics",
         "Niche clarity = faster audience growth + algorithm categorization"),
    ],
    "youtube": [
        ("channel_art",   "Banner is 2560x1440px, mobile-safe zone has clear brand",
         "Upload a professional banner — free templates at Canva"),
        ("channel_icon",  "Channel icon is 800x800px, clear at small sizes",
         "Face or logo should be recognizable at 32px"),
        ("about",         "About section has keywords, upload schedule, and links",
         "First 150 chars shown in search — lead with your value prop"),
        ("trailer",       "Channel trailer is < 60 seconds and hooks in first 5s",
         "Unsubscribed visitors see your trailer — make it compelling"),
        ("playlists",     "Videos organized into topic playlists",
         "Playlists increase session time by keeping viewers on your channel"),
        ("end_screens",   "All videos have end screens pointing to next video or subscribe",
         "End screens are free retention tools — use them on every video"),
        ("cards",         "Cards used at key moments to link to related content",
         "Add cards at 20% and 80% marks in each video"),
        ("thumbnails",    "Thumbnails use high contrast, readable text, and emotion",
         "A/B test thumbnails — YouTube Studio shows click-through rate"),
        ("upload_cadence","Uploads consistently (1–3x/week minimum)",
         "Consistency signals to algorithm — set a schedule and keep it"),
    ],
}


def audit_account(
    platform: str,
    handle: str,
    self_assessment: Optional[Dict[str, bool]] = None,
) -> ProfileAudit:
    """Audit a social media account against optimization best practices.

    Args:
        platform: "tiktok" | "youtube" | "instagram"
        handle: Account handle (e.g., @username)
        self_assessment: Optional dict mapping checklist item names to True/False.
                        If None, all items flagged as "needs review".

    Returns:
        ProfileAudit with score and prioritized action items.
    """
    checklist = _PROFILE_CHECKLIST.get(platform, _PROFILE_CHECKLIST["tiktok"])
    items: List[AuditItem] = []
    score = 0
    per_item = 100 // len(checklist)

    for key, description, recommendation in checklist:
        if self_assessment is None:
            status = "warn"
            score += per_item // 2
        elif self_assessment.get(key, False):
            status = "pass"
            score += per_item
        else:
            status = "fail"

        items.append(AuditItem(
            category=key,
            item=description,
            status=status,
            recommendation=recommendation,
        ))

    fails = [i for i in items if i.status == "fail"]
    warns = [i for i in items if i.status == "warn"]
    top_actions = [i.recommendation for i in (fails + warns)[:5]]

    return ProfileAudit(
        platform=platform,
        handle=handle,
        score=min(score, 100),
        items=items,
        top_actions=top_actions,
    )


# ── Posting schedule ──────────────────────────────────────────────────────────

def get_posting_schedule(
    platform: str,
    posts_per_week: int = 5,
    timezone_offset: int = 0,
) -> List[PostSlot]:
    """Return an optimized posting schedule.

    Args:
        platform: "tiktok" | "youtube" | "instagram"
        posts_per_week: How many posts per week (1–14 for TikTok, 1–5 for YouTube)
        timezone_offset: Hours offset from UTC (e.g., -5 for EST, +1 for CET)

    Returns:
        List of PostSlot objects for the week, sorted by priority.
    """
    all_slots = OPTIMAL_POSTING_TIMES.get(platform, OPTIMAL_POSTING_TIMES["tiktok"])
    best_first = sorted(all_slots, key=lambda s: {"best": 0, "good": 1, "ok": 2}[s.priority])

    selected = best_first[:posts_per_week]

    if timezone_offset != 0:
        adjusted = []
        for slot in selected:
            h, m = map(int, slot.time_local.split(":"))
            h = (h + timezone_offset) % 24
            adjusted.append(PostSlot(
                day=slot.day,
                time_local=f"{h:02d}:{m:02d}",
                priority=slot.priority,
                reason=slot.reason + f" (adjusted UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset})",
            ))
        return adjusted

    return selected


# ── Content calendar ──────────────────────────────────────────────────────────

_CONTENT_TYPE_ROTATION = {
    "tiktok": [
        "Hook + Value Drop",
        "Trend/Sound Stitch",
        "Tutorial (POV style)",
        "Behind The Scenes",
        "Story + CTA",
        "Duet or Collaboration",
        "Trending Hashtag Challenge",
    ],
    "youtube": [
        "Evergreen Tutorial",
        "Trending Topic Reaction",
        "List / Top 10",
        "Case Study / Deep Dive",
        "Shorts (cross-post)",
        "Collab / Interview",
        "Q&A / Community",
    ],
}

_TOPIC_IDEAS = {
    "fitness": [
        "5-min home workout for beginners",
        "What I eat in a day (cutting)",
        "The truth about [popular supplement]",
        "My 30-day transformation challenge",
        "Best exercises for [body part]",
        "Why you're not seeing results",
        "Morning routine of a fit person",
    ],
    "beauty": [
        "5-minute everyday makeup",
        "Skincare routine for [skin type]",
        "Testing viral [product] — worth it?",
        "Drugstore dupe for [luxury product]",
        "My honest review of [brand]",
        "Grwm for [occasion]",
        "Skincare mistakes you're making",
    ],
    "food": [
        "3 meals under $10",
        "5-ingredient [cuisine] dinner",
        "Restaurant dupe at home",
        "Meal prep for the week",
        "Viral recipe — does it work?",
        "Gordon Ramsay's secret technique",
        "What I eat to lose weight",
    ],
    "finance": [
        "How I saved $10K in 6 months",
        "5 money mistakes in your 20s",
        "Investing $100/month for 10 years",
        "Side hustles that actually work",
        "My passive income breakdown",
        "Credit card hacks nobody talks about",
        "Emergency fund — how much?",
    ],
    "motivation": [
        "The 5-second rule (Mel Robbins)",
        "Why discipline beats motivation",
        "Morning routine that changed my life",
        "Lessons from reading 50 books",
        "The mindset of top 1% earners",
        "Stop waiting to feel ready",
        "One habit that changed everything",
    ],
}


def generate_content_calendar(
    niche: str,
    platform: str,
    start_date: str,
    weeks: int = 4,
    posts_per_week: int = 5,
    hashtags: Optional[List[str]] = None,
) -> List[ContentCalendarEntry]:
    """Generate a content calendar for the specified period.

    Args:
        niche: Content niche (fitness, beauty, food, finance, motivation, etc.)
        platform: Target platform
        start_date: ISO date string (YYYY-MM-DD) for calendar start
        weeks: Number of weeks to plan
        posts_per_week: Posts per week
        hashtags: Hashtag list to rotate across posts

    Returns:
        List of ContentCalendarEntry objects for the full period.
    """
    schedule = get_posting_schedule(platform, posts_per_week)
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    content_types = _CONTENT_TYPE_ROTATION.get(platform, _CONTENT_TYPE_ROTATION["tiktok"])
    topics = _TOPIC_IDEAS.get(niche.lower(), _TOPIC_IDEAS.get("motivation", []))

    start = datetime.strptime(start_date, "%Y-%m-%d")
    entries: List[ContentCalendarEntry] = []

    hashtag_pool = hashtags or [f"#{niche}", "#viral", "#fyp", "#trending"]
    tag_chunk_size = min(7, len(hashtag_pool))

    type_idx = 0
    topic_idx = 0
    entry_num = 0

    for week in range(weeks):
        for slot in schedule:
            target_weekday = day_order.index(slot.day)
            days_ahead = (target_weekday - start.weekday() + week * 7) % 7 + week * 7
            post_date = start + timedelta(days=days_ahead)

            tags_start = (entry_num * 3) % max(1, len(hashtag_pool) - tag_chunk_size)
            entry_tags = hashtag_pool[tags_start: tags_start + tag_chunk_size]

            entries.append(ContentCalendarEntry(
                date=post_date.strftime("%Y-%m-%d"),
                day_of_week=slot.day,
                post_time=slot.time_local,
                content_type=content_types[type_idx % len(content_types)],
                topic_idea=topics[topic_idx % len(topics)] if topics else f"{niche} content #{entry_num + 1}",
                hashtag_set=entry_tags,
                notes=f"Priority: {slot.priority}. {slot.reason}",
            ))

            type_idx += 1
            topic_idx += 1
            entry_num += 1

    entries.sort(key=lambda e: (e.date, e.post_time))
    return entries


# ── Growth lever recommendations ──────────────────────────────────────────────

def get_growth_recommendations(
    platform: str,
    niche: str,
    followers: int,
    avg_views: int,
    posts_per_week: int,
) -> Dict:
    """Generate personalized growth recommendations.

    Args:
        platform: "tiktok" | "youtube"
        niche: Content niche
        followers: Current follower/subscriber count
        avg_views: Average views per post
        posts_per_week: Current posting frequency

    Returns:
        Dict with diagnoses, quick wins, and 30-day action plan.
    """
    benchmarks = ENGAGEMENT_BENCHMARKS.get(platform, ENGAGEMENT_BENCHMARKS["tiktok"])

    tier = "nano"
    for t, data in benchmarks.items():
        lo, hi = data.get("followers", data.get("subscribers", (0, float("inf"))))
        if lo <= followers < hi:
            tier = t
            break

    eng_benchmark = benchmarks.get(tier, {}).get("eng_rate", 5.0)
    actual_eng = (avg_views / max(followers, 1)) * 100

    diagnoses = []
    quick_wins = []
    action_plan = []

    if posts_per_week < 3:
        diagnoses.append(f"Posting only {posts_per_week}x/week — algorithm deprioritizes inconsistent accounts")
        quick_wins.append("Increase to 5–7 posts/week for TikTok or 2–3/week for YouTube")
        action_plan.append("Week 1: Batch-record 10 videos and schedule them out")

    if actual_eng < eng_benchmark * 0.7:
        diagnoses.append(f"Engagement rate ({actual_eng:.1f}%) is below {tier} benchmark ({eng_benchmark}%)")
        quick_wins.append("Add a strong CTA in the first 3 seconds and last 5 seconds")
        action_plan.append("Week 2: A/B test hooks — record same content with 3 different opening lines")

    if platform == "tiktok" and followers < 1000:
        diagnoses.append("Under 1K followers — focus on hook quality, not hashtag volume")
        quick_wins.append("Study your FYP for 30 min/day and remix top-performing formats in your niche")
        action_plan.append("Week 1: Post 3 videos using trending sounds + hooks from viral videos")

    if platform == "youtube" and followers < 1000:
        diagnoses.append("Under 1K subscribers — focus on searchable evergreen content")
        quick_wins.append("Target keywords with < 50K competing videos for first-page ranking")
        action_plan.append("Week 1: Use VidIQ or TubeBuddy to find low-competition keywords")

    if not diagnoses:
        diagnoses.append(f"Account metrics look healthy for {tier} tier")

    action_plan.extend([
        "Week 3: Collaborate with 2–3 accounts in your niche (duets/stitches for TikTok)",
        f"Week 4: Review analytics — double down on top 3 performing content types",
    ])

    return {
        "platform": platform,
        "tier": tier,
        "followers": followers,
        "avg_views": avg_views,
        "engagement_rate": round(actual_eng, 2),
        "benchmark_engagement_rate": eng_benchmark,
        "diagnoses": diagnoses,
        "quick_wins": quick_wins,
        "thirty_day_action_plan": action_plan,
    }
