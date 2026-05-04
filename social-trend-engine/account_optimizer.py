"""
Account optimization engine.
Audits YouTube + TikTok accounts and generates actionable improvement plans.
Covers: bio, posting cadence, content gaps, SEO, engagement tactics.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


# ─── Account audit checklist ─────────────────────────────────────────────────

YOUTUBE_CHECKLIST = {
    "profile": [
        "Channel name includes primary keyword",
        "Channel art (banner) is 2560x1440 px, brand-consistent",
        "Profile picture is clear, 800x800 px minimum",
        "Channel description has primary keyword in first 2 sentences",
        "Custom URL claimed (@handle)",
        "Links section filled (social, website)",
        "Channel trailer set for non-subscribers",
        "Featured section populated with playlists",
    ],
    "content": [
        "Custom thumbnail on every video (CTR lifts 25-40%)",
        "Titles follow: [Hook] + [Keyword] + [Value] format",
        "First 24 hours engagement = reply to every comment",
        "End screens on every video (last 20 seconds)",
        "Cards added mid-video to related content",
        "Chapters (timestamps) in description for watch-time boost",
        "Pinned comment with CTA or question",
        "Video description has 3-5 keyword-rich sentences",
        "Tags: 5 highly relevant (not 30 random ones)",
        "Subtitles/captions enabled (accessibility + SEO)",
    ],
    "seo": [
        "Keyword research done before filming (TubeBuddy/VidIQ)",
        "Title starts with exact keyword phrase",
        "Description keyword appears in first 125 characters",
        "Playlist names are keyword-optimized",
        "Upload schedule is consistent (same days/time)",
    ],
    "growth": [
        "Posting 1-3x per week minimum",
        "Shorts (60s) cross-posted from TikTok — free reach",
        "Community posts active (unlocked at 500 subs)",
        "Collab with 2-3 channels in same niche per month",
        "Reply to comments within 1 hour of posting",
    ],
}

TIKTOK_CHECKLIST = {
    "profile": [
        "Username is memorable and keyword-adjacent",
        "Display name includes primary niche keyword",
        "Bio: who you help + what you post + CTA (max 80 chars)",
        "Link in bio active (use Linktree if multiple links)",
        "Profile video set (loops silently — make it compelling)",
        "TikTok Business Account enabled for analytics",
        "Creator Marketplace enrollment if 10K+ followers",
    ],
    "content": [
        "First 1-3 seconds = strong hook (text, action, question)",
        "Captions/text overlay on every video (80% watch on mute)",
        "Trending audio used when relevant to content",
        "Video length 21-34 seconds for max completion rate",
        "Post 1-4 times per day during growth phase",
        "Duet/Stitch viral content in your niche for borrowed reach",
        "Reply to comments with video replies for extra distribution",
        "Use TikTok's native effects/templates — algorithm rewards it",
    ],
    "hashtags": [
        "5-8 targeted hashtags (not 30)",
        "Mix: 1 mega + 3 medium + 2 niche + 2 boosters",
        "#fyp and #foryoupage used sparingly (not every post)",
        "Niche hashtag rotation tracked weekly",
    ],
    "growth": [
        "Post at peak times: 6-9AM, 12-3PM, 7-9PM local",
        "Engage with top creators in niche (first 30 mins after their post)",
        "Run a 7-day challenge or series for retention",
        "Cross-promote to YouTube Shorts + Instagram Reels",
        "Pin 3 best-performing videos to profile",
    ],
    "analytics": [
        "Check analytics every 48 hours post-upload",
        "Track: completion rate >50%, shares, saves (weighted heavily)",
        "Double down on video styles with >60% completion rate",
        "Identify best posting times from your own analytics",
        "A/B test thumbnails (TikTok auto-selects after ~24h)",
    ],
}


@dataclass
class AccountAudit:
    platform: str
    handle: str
    followers: int = 0
    avg_views: int = 0
    niche: str = ""
    completed_checks: list[str] = field(default_factory=list)
    missing_checks: list[str] = field(default_factory=list)
    score: int = 0
    tier: str = ""
    action_plan: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            f"ACCOUNT AUDIT — @{self.handle} ({self.platform.upper()})",
            "=" * 60,
            f"Followers : {self.followers:,}",
            f"Avg Views : {self.avg_views:,}",
            f"Niche     : {self.niche}",
            f"Score     : {self.score}/100  [{self.tier}]",
            "",
            f"COMPLETED ({len(self.completed_checks)}):",
        ]
        for c in self.completed_checks:
            lines.append(f"  [x] {c}")
        lines += [
            "",
            f"MISSING ({len(self.missing_checks)}) — fix these first:",
        ]
        for i, m in enumerate(self.missing_checks, 1):
            lines.append(f"  [{i:02d}] {m}")
        lines += [
            "",
            "TOP 5 ACTION ITEMS:",
        ]
        for i, a in enumerate(self.action_plan[:5], 1):
            lines.append(f"  {i}. {a}")
        return "\n".join(lines)


def audit_account(
    platform: str,
    handle: str,
    followers: int = 0,
    avg_views: int = 0,
    niche: str = "lifestyle",
    completed_checks: Optional[list[str]] = None,
) -> AccountAudit:
    """
    Run an account audit. Pass completed_checks as list of check names already done.
    All checks not in completed_checks are flagged as missing.
    """
    checklist = YOUTUBE_CHECKLIST if platform == "youtube" else TIKTOK_CHECKLIST
    all_checks = [c for section in checklist.values() for c in section]

    done = set(completed_checks or [])
    completed = [c for c in all_checks if c in done]
    missing = [c for c in all_checks if c not in done]

    score = int(len(completed) / max(len(all_checks), 1) * 100)

    if score >= 80:
        tier = "OPTIMIZED"
    elif score >= 60:
        tier = "GROWING"
    elif score >= 40:
        tier = "DEVELOPING"
    else:
        tier = "NEEDS WORK"

    # Priority action plan — first 5 missing items most likely to move the needle
    priority_order = (
        checklist.get("profile", [])
        + checklist.get("seo", [])
        + checklist.get("hashtags", [])
        + checklist.get("content", [])
        + checklist.get("growth", [])
        + checklist.get("analytics", [])
    )
    action_plan = [c for c in priority_order if c in set(missing)][:10]

    return AccountAudit(
        platform=platform,
        handle=handle,
        followers=followers,
        avg_views=avg_views,
        niche=niche,
        completed_checks=completed,
        missing_checks=missing,
        score=score,
        tier=tier,
        action_plan=action_plan,
    )


def generate_content_calendar(
    platform: str,
    niche: str,
    posts_per_week: int = 5,
    trending_topics: Optional[list[str]] = None,
) -> str:
    """Generate a weekly content calendar with content types and hooks."""

    content_types = {
        "youtube": [
            "Tutorial / How-To",
            "Reaction / Commentary",
            "Listicle (Top 5/10)",
            "Story Time / Vlog",
            "Challenge / Experiment",
            "Collab / Interview",
            "Shorts (60s highlight)",
        ],
        "tiktok": [
            "Hook + Value (talking head)",
            "Text-over-video story",
            "Duet / Stitch trending",
            "Day-in-my-life / DITL",
            "Tutorial in under 30s",
            "Trend audio + your niche",
            "Comment reply video",
        ],
    }

    hooks = [
        "POV: you discovered [X] and your life changed...",
        "Stop doing this if you want [result]",
        "Nobody talks about this [niche] hack",
        "I tried [trend] for 30 days — here's what happened",
        "The reason 99% of [niche] people fail",
        "What [niche experts] don't want you to know",
        "How I [achieved result] with [low effort/cost]",
    ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    types_cycle = content_types.get(platform, content_types["tiktok"])
    topics = (trending_topics or [niche, f"{niche} tips", f"{niche} transformation"])

    lines = [
        f"WEEKLY CONTENT CALENDAR — {platform.upper()} / #{niche}",
        f"Posts per week: {posts_per_week}",
        "=" * 60,
    ]

    post_days = days[:posts_per_week]
    for i, day in enumerate(post_days):
        ctype = types_cycle[i % len(types_cycle)]
        hook = hooks[i % len(hooks)]
        topic = topics[i % len(topics)]
        lines += [
            f"\n{day.upper()}",
            f"  Format : {ctype}",
            f"  Topic  : {topic}",
            f"  Hook   : {hook.replace('[niche]', niche).replace('[X]', topic)}",
        ]
        if i == 0:
            lines.append("  NOTE   : Best day for new content — algorithm push highest")

    lines += [
        "",
        "ENGAGEMENT WINDOWS (respond to comments in these slots):",
        "  30 min after posting — critical for early push",
        "  2-4 hours after posting — sustain momentum",
        "  24 hours after posting — second-day retention boost",
    ]

    return "\n".join(lines)


def viral_engagement_tactics(platform: str) -> str:
    """Return platform-specific engagement tactics to boost algorithmic reach."""

    yt_tactics = """
YOUTUBE VIRAL ENGAGEMENT TACTICS
=================================
1. FIRST HOUR SURGE
   • Share video in 3 relevant Discord/Reddit communities immediately on publish
   • Pin a comment asking a question (drives comment velocity)
   • Send to email list within 30 min of going live

2. WATCH TIME (king metric for YouTube)
   • Pattern interrupt every 60-90 seconds (cut, graphic, music change)
   • Open loops: "I'll show you X at the end but first..."
   • Chapters make people rewind = double watch time count

3. CLICK-THROUGH RATE (CTR) — target 8-12%
   • A/B test thumbnails with TubeBuddy
   • Thumbnail must show emotion + contrast + 3 words max
   • Change title in first 24h if CTR below 5%

4. SUBSCRIBER CONVERSION
   • Ask to subscribe at the 30% mark (not beginning)
   • Offer reason: "Subscribe for [specific weekly value]"
   • End screen subscription button over a still frame

5. SHORTS STRATEGY (free traffic machine)
   • Repurpose best TikToks as Shorts for free reach
   • Shorts push Longs — add card linking to long-form
   • Post Shorts at different times than long-form
"""

    tt_tactics = """
TIKTOK VIRAL ENGAGEMENT TACTICS
=================================
1. THE FIRST 3 SECONDS (everything)
   • Visual hook: unexpected image/action
   • Text hook: bold statement or question on screen
   • Audio hook: trending sound from first beat
   • Never start with "Hey guys" — start MID-sentence

2. COMPLETION RATE (TikTok's #1 signal)
   • Loop the video: end where you began
   • Cliff-hanger ending: "Wait for it..." at second 25
   • Target 21-34 second sweet spot for max loops

3. SHARES & SAVES (weighted 2x more than likes)
   • Content that makes people say "I need to share this"
   • Actionable tips people want to save for later
   • "Share this with your [friend who does X]"

4. COMMENT BAITING (algorithmically rewarded)
   • Intentional mistake people will correct
   • "Comment your result below"
   • Controversial (but safe) opinion in your niche
   • "Drop a (emoji) if you want part 2"

5. DUET / STITCH STRATEGY
   • React to viral content in your niche (borrowed audience)
   • Stitch with: "Here's what they missed..."
   • Creators love getting duetted — often reshare you

6. SOUND SELECTION
   • Check Trending Sounds tab daily
   • Use sound within 24-48h of trending spike
   • Original audio can go viral — record clean, unique hooks
"""

    if platform == "youtube":
        return yt_tactics
    elif platform == "tiktok":
        return tt_tactics
    else:
        return yt_tactics + "\n" + tt_tactics


if __name__ == "__main__":
    audit = audit_account("tiktok", "myhandle", followers=1200, avg_views=3000, niche="fitness")
    print(audit.summary())
    print()
    print(generate_content_calendar("tiktok", "fitness", posts_per_week=5))
