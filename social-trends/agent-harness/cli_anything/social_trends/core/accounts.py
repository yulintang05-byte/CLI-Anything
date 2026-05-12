"""Account optimization — scoring, audits, and platform-specific advice."""

from dataclasses import dataclass, field
from typing import Optional


# ── Scoring weights ───────────────────────────────────────────────────────────

PLATFORM_TIPS: dict[str, dict] = {
    "tiktok": {
        "posting_frequency": "1-3 videos/day minimum for growth phase; 3-5/day for aggressive growth",
        "best_times": ["7-9 AM EST", "12-3 PM EST", "7-11 PM EST"],
        "video_length": "7-15 seconds for viral reach; 30-60s for storytelling/edu content",
        "hook": "First 1-3 seconds MUST hook viewer — use pattern interrupt, bold text, or question",
        "caption": "Keep captions short (1-2 lines). CTA: 'Follow for more [niche]'",
        "sounds": "Use trending sounds from the TikTok Discover page — adds 2-5x reach boost",
        "hashtags": "3-5 niche tags + 2-3 viral boosters (fyp, trending). Don't over-tag.",
        "engagement": "Reply to ALL comments in first hour — TikTok rewards creator engagement",
        "profile": "Niche bio with clear value prop. Link Linktree/Stan Store in bio.",
        "growth_hack": "Stitch/Duet trending videos in your niche — borrows their reach",
        "analytics_kpis": ["watch_time_percent", "shares_per_view", "profile_visits", "follower_conversion_rate"],
    },
    "youtube": {
        "posting_frequency": "2-3 Shorts/day + 1-2 long-form/week for maximum algorithm favor",
        "best_times": ["2-4 PM EST", "7-9 PM EST (weekdays)", "Saturdays 9-11 AM EST"],
        "video_length": "Shorts: 15-60s | Long-form: 8-15 min (sweet spot for ad revenue)",
        "hook": "First 30 seconds must deliver on thumbnail/title promise — no slow intros",
        "caption": "Keyword-rich descriptions (500+ words). Include timestamps.",
        "sounds": "Use royalty-free music (YouTube Audio Library, Epidemic Sound) to avoid strikes",
        "hashtags": "3-5 hashtags in description or title for Shorts",
        "engagement": "Pin a comment to direct viewers. Reply within 24 hours.",
        "profile": "Channel banner with upload schedule. Trailer video for new visitors.",
        "growth_hack": "Optimize thumbnails (high contrast, face + emotion + text). A/B test titles.",
        "analytics_kpis": ["CTR", "avg_view_duration", "subscriber_conversion", "impressions"],
    },
    "instagram": {
        "posting_frequency": "1 Reel/day + 2-3 Stories/day. Feed posts: 4-5/week",
        "best_times": ["6-9 AM EST", "12-2 PM EST", "5-7 PM EST"],
        "video_length": "Reels: 7-15s for max reach; 30-60s for engagement. Stories: 15s each",
        "hook": "Bright colors and movement in the first frame to stop scroll",
        "caption": "Lead with hook sentence, then expand. CTA at end. Use line breaks.",
        "sounds": "Use trending audio from Reels library — check the trending arrow icon",
        "hashtags": "5-10 hashtags, mix of large (1M+), medium (100k-1M), small (<100k)",
        "engagement": "Engage with 20-30 accounts in your niche BEFORE posting — primes algorithm",
        "profile": "Clear niche in name field (e.g., 'John | Fitness Tips'). Highlights organized.",
        "growth_hack": "Collab posts and Remix features double your reach with zero extra effort",
        "analytics_kpis": ["reach", "saves", "shares", "profile_visits", "website_clicks"],
    },
    "twitter_x": {
        "posting_frequency": "3-10 tweets/day + engage in threads",
        "best_times": ["8-10 AM EST", "12-1 PM EST", "5-6 PM EST"],
        "video_length": "Clips: 30-60s. Twitter favors text but video drives 10x more engagement",
        "hook": "Open with bold/contrarian statement or surprising statistic",
        "caption": "No caption needed — tweet IS the copy. Keep under 280 chars or thread it",
        "sounds": "N/A for text. Video: add captions for silent autoplay",
        "hashtags": "1-2 relevant hashtags max — more looks spammy",
        "engagement": "Quote-tweet viral posts with your hot take for massive exposure",
        "profile": "Bio: what you do + who you help. Pin your best tweet.",
        "growth_hack": "Post in threads (10+ tweets) — algorithm rewards time-on-thread",
        "analytics_kpis": ["impressions", "engagements", "link_clicks", "new_followers"],
    },
}

PROFILE_CHECKLIST: list[dict] = [
    {"item": "Profile picture", "tip": "High-res, face visible, consistent across platforms"},
    {"item": "Username/handle", "tip": "Same handle everywhere for brand consistency"},
    {"item": "Bio", "tip": "Clear niche + value prop in first line. Emoji optional but eye-catching"},
    {"item": "Link in bio", "tip": "Use Linktree, Stan Store, or Beacons to house all links"},
    {"item": "Highlight covers", "tip": "(Instagram) Branded highlight covers with consistent color palette"},
    {"item": "Content pillars", "tip": "Define 3-5 content pillars so your niche is unmistakable"},
    {"item": "Pinned post/video", "tip": "Pin your best-performing or most representative content"},
    {"item": "Business account", "tip": "Switch to Creator/Business for analytics and monetization tools"},
    {"item": "Niche keywords in name", "tip": "Include your niche keyword in your display name for SEO"},
    {"item": "Story highlights", "tip": "(Instagram/TikTok) Create highlight categories: About, Work With Me, Results"},
]

CONTENT_PILLARS: dict[str, list[str]] = {
    "education": ["How-to tutorials", "Myth busting", "Tips & tricks", "Explainers", "Data breakdowns"],
    "entertainment": ["Behind the scenes", "Relatable moments", "Challenges/trends", "Humor/skits"],
    "inspiration": ["Success stories", "Transformation reveals", "Motivational quotes with proof"],
    "promotion": ["Product features", "Testimonials", "Soft-sell content", "Limited time offers"],
    "engagement": ["Questions/polls", "Controversial opinions", "This or that", "Ask me anything"],
}


@dataclass
class AccountAudit:
    platform: str
    username: str
    followers: int = 0
    following: int = 0
    posts: int = 0
    avg_likes: float = 0
    avg_comments: float = 0
    avg_views: float = 0
    bio_complete: bool = False
    has_link: bool = False
    has_profile_pic: bool = True
    posting_consistency: str = "unknown"  # daily/weekly/sporadic/unknown
    notes: list[str] = field(default_factory=list)

    @property
    def engagement_rate(self) -> float:
        if self.followers == 0:
            return 0.0
        return round(((self.avg_likes + self.avg_comments) / self.followers) * 100, 2)

    @property
    def ff_ratio(self) -> float:
        if self.following == 0:
            return 0.0
        return round(self.followers / self.following, 2)

    def score(self) -> dict:
        points = 0
        feedback = []

        # Engagement rate scoring
        er = self.engagement_rate
        if er >= 5:
            points += 25
            feedback.append("[+] Excellent engagement rate (>5%)")
        elif er >= 2:
            points += 15
            feedback.append("[~] Decent engagement rate (2-5%) — aim for 5%+")
        elif er > 0:
            points += 5
            feedback.append("[-] Low engagement rate (<2%) — focus on reply/comment strategy")
        else:
            feedback.append("[-] No engagement data provided")

        # Profile completeness
        if self.bio_complete:
            points += 10
        else:
            feedback.append("[-] Bio incomplete — add niche keyword + value prop")
        if self.has_link:
            points += 10
        else:
            feedback.append("[-] No link in bio — add Linktree or landing page")
        if self.has_profile_pic:
            points += 5

        # Follower/following ratio
        if self.ff_ratio > 5:
            points += 15
            feedback.append("[+] Great follower/following ratio")
        elif self.ff_ratio > 1:
            points += 8
        elif self.ff_ratio > 0:
            feedback.append("[-] Following too many accounts — unfollow non-followers")

        # Posting consistency
        if self.posting_consistency == "daily":
            points += 20
            feedback.append("[+] Daily posting — keep it up!")
        elif self.posting_consistency == "weekly":
            points += 10
            feedback.append("[~] Weekly posting — increase to daily for faster growth")
        elif self.posting_consistency == "sporadic":
            feedback.append("[-] Sporadic posting kills algorithm reach — batch and schedule content")

        # Posts count
        if self.posts >= 100:
            points += 15
        elif self.posts >= 30:
            points += 8
            feedback.append("[~] Build up post count to 100+ for authority")
        else:
            feedback.append("[-] Too few posts — post more to build credibility")

        return {
            "username": self.username,
            "platform": self.platform,
            "score": min(points, 100),
            "engagement_rate": f"{er}%",
            "ff_ratio": self.ff_ratio,
            "feedback": feedback,
            "platform_tips": PLATFORM_TIPS.get(self.platform.lower(), {}),
        }

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "platform": self.platform,
            "followers": self.followers,
            "following": self.following,
            "posts": self.posts,
            "avg_likes": self.avg_likes,
            "avg_comments": self.avg_comments,
            "avg_views": self.avg_views,
            "engagement_rate": f"{self.engagement_rate}%",
            "ff_ratio": self.ff_ratio,
            "bio_complete": self.bio_complete,
            "has_link": self.has_link,
            "posting_consistency": self.posting_consistency,
            "notes": self.notes,
        }


def get_platform_tips(platform: str) -> dict:
    return PLATFORM_TIPS.get(platform.lower(), {
        "error": f"Unknown platform '{platform}'",
        "available": list(PLATFORM_TIPS.keys()),
    })


def get_profile_checklist() -> list[dict]:
    return PROFILE_CHECKLIST


def get_content_pillars() -> dict:
    return CONTENT_PILLARS


def get_posting_schedule(platform: str, goal: str = "growth") -> dict:
    tips = PLATFORM_TIPS.get(platform.lower(), {})
    return {
        "platform": platform,
        "goal": goal,
        "frequency": tips.get("posting_frequency", "N/A"),
        "best_times": tips.get("best_times", []),
        "kpis": tips.get("analytics_kpis", []),
        "hook_tip": tips.get("hook", ""),
    }
