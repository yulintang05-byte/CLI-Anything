"""Account optimization — profile audit, content strategy, and growth playbook."""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ProfileAudit:
    platform: str
    username: str
    score: int  # 0-100
    passed: list[str]
    warnings: list[str]
    fixes: list[str]
    priority_fixes: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GrowthPlaybook:
    platform: str
    current_phase: str
    daily_actions: list[str]
    weekly_actions: list[str]
    monthly_goals: list[str]
    kpis: dict
    monetization_unlocks: list[dict]

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContentCalendar:
    platform: str
    week: list[dict]
    hashtag_sets: list[dict]
    hook_templates: list[str]
    cta_templates: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Profile audit rules
# ---------------------------------------------------------------------------

_TIKTOK_AUDIT_RULES = [
    ("profile_pic", "Has clear, high-quality profile picture", "Add a bright, face-forward profile photo — accounts with faces get 35% more follows"),
    ("bio_niche", "Bio clearly states niche in first line", "Add your niche to bio (e.g. 'Daily finance tips | Making $10K/mo online')"),
    ("bio_cta", "Bio has a clear CTA or link", "Add CTA to bio: 'Follow for [X] every day' or a link-in-bio tool"),
    ("username_clean", "Username is short and memorable (<20 chars)", "Shorten username — under 15 characters sticks better in search"),
    ("pinned_videos", "Has 3 pinned videos showing best content", "Pin your top 3 videos. First impression = retained followers"),
    ("consistent_posting", "Posts at minimum 1x/day", "Increase post frequency — TikTok rewards accounts posting 3-5x/day"),
    ("sound_trending", "Uses trending sounds in recent posts", "Incorporate trending sounds — adds +40% reach from sound page discovery"),
    ("hook_quality", "Videos start with a hook in first 2 seconds", "Recut videos: open with a question, stat, or visual surprise"),
    ("reply_engagement", "Replies to comments within 1 hour", "Set 30-min reply windows after posting — comment velocity boosts distribution"),
    ("hashtag_mix", "Uses mixed hashtag strategy (big + niche)", "Use 1 mega-tag (#fyp), 2 niche tags, 1-2 trending tags per post"),
]

_YOUTUBE_AUDIT_RULES = [
    ("channel_art", "Has branded channel art (2560x1440px)", "Design channel art with Canva — brand consistency lifts subscribe rate"),
    ("channel_description", "Channel description has keywords in first 200 chars", "Add your top 3 keywords in first sentence of channel description"),
    ("upload_schedule", "Posts on consistent schedule (weekly minimum)", "Publish on same day/time weekly — subscribers get notified and expect it"),
    ("thumbnails", "Custom thumbnails on all videos", "Create custom thumbnails: bold text + face reaction + contrast colors = +38% CTR"),
    ("titles_seo", "Video titles include searchable keywords", "Add 1-2 high-volume keywords in every title (use Google Trends to find them)"),
    ("end_screens", "Uses end screens on all videos", "Add end screens to final 20s — drives 30%+ more views to next video"),
    ("playlists", "Content organized into playlists", "Create 3-5 playlists — playlists auto-play and double average watch time"),
    ("community_tab", "Uses Community tab for engagement", "Post in Community tab 3x/week (polls, behind-scenes) — keeps subscribers warm"),
    ("shorts_strategy", "Publishes YouTube Shorts regularly", "Add 2-3 Shorts/week — Shorts have separate viral potential and feed new subs to long-form"),
    ("description_links", "Video descriptions have chapters and links", "Add chapters (00:00 format) and links in every description — boosts SEO and retention"),
]

_INSTAGRAM_AUDIT_RULES = [
    ("business_account", "Using Business/Creator account", "Switch to Creator account for analytics and monetization tools"),
    ("highlights", "Story highlights organized and branded", "Create 5-7 branded highlight covers — first impression for profile visitors"),
    ("bio_hook", "Bio explains who you help and how", "Rewrite bio: '[Who you are] helping [target audience] [achieve outcome]'"),
    ("reels_strategy", "Posts Reels minimum 3x/week", "Reels get 22% more reach than static posts — make them your primary content"),
    ("carousel_engagement", "Uses carousel posts for educational content", "Carousels get up to 3x more saves — saves are Instagram's #1 ranking signal"),
    ("story_daily", "Posts Stories daily", "Daily Stories keep you top-of-feed for followers — use polls/questions for engagement"),
    ("hashtags_optimized", "Uses 3-10 niche hashtags (not 30)", "Use 5-8 targeted hashtags — algorithm penalizes hashtag stuffing since 2023"),
    ("collab_posts", "Uses Instagram Collabs feature", "Use Collab feature with niche creators — your content shows on both audiences"),
]

_PHASE_CRITERIA = {
    "launch": (0, 1000),
    "growth": (1000, 10000),
    "scale": (10000, 100000),
    "authority": (100000, 10**9),
}

_PHASE_ACTIONS = {
    "launch": {
        "daily": [
            "Post 3-5 TikToks or 1 YouTube video",
            "Engage 30 min: comment on 20 posts in your niche",
            "Follow 50 niche creators (follow-back strategy)",
            "Reply to every comment within 1 hour",
            "DM 5 creators for potential collabs",
        ],
        "weekly": [
            "Analyze your top-performing post and make 3 variations",
            "Research 5 new trending sounds/hashtags",
            "Review competitors' top videos for content ideas",
            "Test one new content format you haven't tried",
            "Check analytics: drop content types under 10% avg completion",
        ],
        "monthly": [
            "Reach 1,000 followers on primary platform",
            "Identify your top 3 viral video formats",
            "Build an email list (link-in-bio to free lead magnet)",
            "Establish posting schedule and batch-record 1 week of content",
        ],
    },
    "growth": {
        "daily": [
            "Post 2-3 times across platforms",
            "Engage 20 min on comments/DMs",
            "Check analytics dashboard — cut what's not working",
            "Reply to top comments to boost distribution",
        ],
        "weekly": [
            "Collab or duet with 1 creator in your niche",
            "Create one long-form piece (YouTube video / blog) repurposed to 5 short-form clips",
            "Test one new monetization format (affiliate, TikTok Shop, digital product)",
            "Review and update your top 3 pinned posts / pinned videos",
        ],
        "monthly": [
            "Hit platform monetization threshold (TikTok 10K, YouTube 1K subs + 4K hours)",
            "Launch first product/service offer to warm audience",
            "Guest appear on 1 podcast or collab channel",
            "Analyze and double down on your #1 traffic-driving content type",
        ],
    },
    "scale": {
        "daily": [
            "Delegate posting to VA — you focus on content creation only",
            "Record content in batches (3-4 hours, 2x/week)",
            "Check revenue metrics: CPM, affiliate conversions, product sales",
        ],
        "weekly": [
            "Brand deal outreach to 5-10 relevant companies",
            "Review content performance with team",
            "Launch or optimize lead funnel (email + offers)",
            "Repurpose top content to additional platforms",
        ],
        "monthly": [
            "Negotiate 2+ brand deal contracts",
            "Launch or iterate digital product/course",
            "Expand to second platform with repurposed content",
            "Hire or outsource: editor, thumbnail designer, community manager",
        ],
    },
}

_MONETIZATION_MILESTONES = [
    {"threshold": "1K TikTok followers", "unlock": "TikTok LIVE (can receive gifts)"},
    {"threshold": "1K YouTube + 4K watch hours", "unlock": "YouTube Partner Program (ads revenue)"},
    {"threshold": "10K TikTok followers", "unlock": "TikTok Creator Marketplace (brand deals)"},
    {"threshold": "10K Instagram followers", "unlock": "Instagram subscription / paid partnership badge"},
    {"threshold": "1K email subscribers", "unlock": "Email marketing revenue (avg $1-5/subscriber/month)"},
    {"threshold": "First digital product", "unlock": "Gumroad / Stan Store / Teachable passive income"},
    {"threshold": "50K multi-platform followers", "unlock": "Brand deal rates of $500-5K per sponsored post"},
    {"threshold": "100K+ any platform", "unlock": "Agent/manager representation, $5K-50K brand deals"},
]

_HOOK_TEMPLATES = [
    "I gained [X] followers in [Y] days doing this one thing…",
    "Nobody talks about how [controversial truth in your niche]",
    "POV: You discover [desirable outcome] exists…",
    "Stop doing [common mistake] if you want [goal]",
    "This is why 99% of people never [achieve outcome] — watch till the end",
    "[Number] things I wish I knew before [starting/doing X]",
    "Rate my [X] (comment bait for engagement)",
    "I tested [popular thing] for 30 days — here's what happened",
    "The [platform] algorithm hates when you know this…",
    "Day [X] of [challenge]: [update that shows progress]",
]

_CTA_TEMPLATES = [
    "Follow for daily [niche] tips — I post every day",
    "Save this for later — you'll need it",
    "Comment '[keyword]' and I'll DM you [free resource]",
    "Share this with someone who needs to hear it",
    "Like if you agree — drop a disagree if you don't",
    "What should I cover next? Comment below",
    "Part 2 coming if this hits [X] likes",
    "Tag a friend who's doing [mistake mentioned in video]",
]


def audit_profile(
    platform: str,
    username: str,
    follower_count: int = 0,
    checks: Optional[dict] = None,
) -> ProfileAudit:
    """Run a profile optimization audit for a given platform."""
    platform = platform.lower()

    rule_set = {
        "tiktok": _TIKTOK_AUDIT_RULES,
        "youtube": _YOUTUBE_AUDIT_RULES,
        "instagram": _INSTAGRAM_AUDIT_RULES,
    }.get(platform, _TIKTOK_AUDIT_RULES)

    if checks is None:
        checks = {}

    passed = []
    warnings = []
    fixes = []
    priority_fixes = []

    for key, description, fix in rule_set:
        if checks.get(key, False):
            passed.append(description)
        else:
            warnings.append(description)
            if key in ("profile_pic", "bio_niche", "hook_quality", "thumbnails", "bio_hook"):
                priority_fixes.append(fix)
            else:
                fixes.append(fix)

    total = len(rule_set)
    score = int((len(passed) / total) * 100) if total > 0 else 0

    return ProfileAudit(
        platform=platform,
        username=username,
        score=score,
        passed=passed,
        warnings=warnings,
        fixes=fixes,
        priority_fixes=priority_fixes,
    )


def build_growth_playbook(
    platform: str,
    follower_count: int,
    niche: str = "general",
) -> GrowthPlaybook:
    """Generate a phase-specific growth playbook."""
    platform = platform.lower()

    phase = "launch"
    for p, (lo, hi) in _PHASE_CRITERIA.items():
        if lo <= follower_count < hi:
            phase = p
            break

    actions = _PHASE_ACTIONS.get(phase, _PHASE_ACTIONS["launch"])

    kpis = {
        "follower_growth_rate": "10-20% month-over-month minimum",
        "avg_completion_rate": ">50% for viral potential",
        "engagement_rate": ">5% (likes+comments / views)",
        "posting_frequency": "Daily minimum for launch/growth phases",
        "profile_visits_to_follows": ">15% conversion target",
    }

    return GrowthPlaybook(
        platform=platform,
        current_phase=phase,
        daily_actions=actions["daily"],
        weekly_actions=actions["weekly"],
        monthly_goals=actions["monthly"],
        kpis=kpis,
        monetization_unlocks=_MONETIZATION_MILESTONES,
    )


def build_content_calendar(
    platform: str,
    niche: str = "general",
    posts_per_day: int = 3,
) -> ContentCalendar:
    """Generate a 7-day content calendar with hooks, CTAs, and hashtag sets."""
    from datetime import datetime, timedelta

    today = datetime.today()
    formats = [
        ("Hook + value delivery", "Educational tip in under 30 seconds"),
        ("POV storytelling", "First-person narrative about a relatable experience"),
        ("Trending sound lip-sync + text overlay", "Ride viral audio with on-screen text value"),
        ("Tutorial / how-to", "Step-by-step process with clear outcome"),
        ("Before/After", "Transformation reveal — before state then after state"),
        ("Hot take / unpopular opinion", "Controversial angle to bait comments"),
        ("Day in my life", "Authentic look at your daily routine in niche context"),
    ]

    week = []
    for i in range(7):
        day = today + timedelta(days=i)
        day_posts = []
        for j in range(posts_per_day):
            fmt = formats[(i * posts_per_day + j) % len(formats)]
            day_posts.append({
                "time": ["6:30 AM", "12:00 PM", "8:00 PM"][j % 3],
                "format": fmt[0],
                "description": fmt[1],
                "hook": _HOOK_TEMPLATES[(i + j) % len(_HOOK_TEMPLATES)],
                "cta": _CTA_TEMPLATES[(i + j) % len(_CTA_TEMPLATES)],
            })
        week.append({
            "date": day.strftime("%Y-%m-%d (%A)"),
            "posts": day_posts,
        })

    hashtag_sets = [
        {
            "name": "Max Reach",
            "hashtags": ["#fyp", "#foryoupage", "#viral", "#trending", f"#{niche}"],
            "use_when": "For content with broad mass appeal",
        },
        {
            "name": "Niche Authority",
            "hashtags": [f"#{niche}tok", f"#{niche}tips", f"#{niche}101", "#learnontiktok", "#smallcreator"],
            "use_when": "For educational / authority-building content",
        },
        {
            "name": "Engagement Bait",
            "hashtags": ["#comment", "#duet", "#stitch", "#reaction", "#debate"],
            "use_when": "For opinion pieces and comment-bait videos",
        },
    ]

    return ContentCalendar(
        platform=platform,
        week=week,
        hashtag_sets=hashtag_sets,
        hook_templates=_HOOK_TEMPLATES,
        cta_templates=_CTA_TEMPLATES,
    )


def optimize_all_accounts(accounts: list[dict]) -> list[dict]:
    """Run optimization audit across multiple accounts and return prioritized action plans."""
    results = []
    for acc in accounts:
        platform = acc.get("platform", "tiktok")
        username = acc.get("username", "unknown")
        followers = acc.get("followers", 0)
        niche = acc.get("niche", "general")
        checks = acc.get("checks", {})

        audit = audit_profile(platform, username, followers, checks)
        playbook = build_growth_playbook(platform, followers, niche)
        calendar = build_content_calendar(platform, niche)

        results.append({
            "account": f"@{username} ({platform})",
            "audit": audit.to_dict(),
            "growth_playbook": playbook.to_dict(),
            "content_calendar_preview": {
                "next_3_days": calendar.week[:3],
                "hashtag_sets": calendar.hashtag_sets,
            },
            "top_priority": audit.priority_fixes[:3] if audit.priority_fixes else ["Profile looks optimized — focus on consistency"],
        })

    return results
