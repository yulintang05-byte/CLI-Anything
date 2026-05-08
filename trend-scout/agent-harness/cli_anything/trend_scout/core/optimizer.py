"""Account optimizer: generates platform-specific optimization plans based on trend data."""

import json
from datetime import datetime
from typing import Any

from .analyzer import TrendAnalyzer


PLATFORM_ALGORITHMS = {
    "tiktok": {
        "ranking_factors": [
            "Watch time / completion rate (most important)",
            "Shares (highest weight of all engagement)",
            "Comments (shows active discussion)",
            "Likes (engagement signal)",
            "Video information (sounds, captions, hashtags)",
            "Device and account settings (region, language)",
        ],
        "profile_factors": [
            "Consistent posting schedule",
            "Niche clarity (don't post random topics)",
            "Profile photo quality",
            "Bio with clear value prop + link",
            "TikTok LIVE engagement (boosts account reach)",
        ],
    },
    "youtube": {
        "ranking_factors": [
            "Click-through rate (CTR) on thumbnail",
            "Average view duration (AVD)",
            "Total watch time",
            "Likes and comments",
            "Subscriber conversions",
            "Video recency",
        ],
        "profile_factors": [
            "Channel art and banner consistency",
            "About section with keywords",
            "Playlist organization",
            "Community posts (drives engagement between uploads)",
            "End screens and cards usage",
        ],
    },
    "instagram": {
        "ranking_factors": [
            "Relationship (do followers interact with you?)",
            "Interest (does content match past behavior?)",
            "Recency (new content prioritized)",
            "Saves (highest weight on Reels)",
            "Shares via DM",
            "Time spent watching Reel",
        ],
        "profile_factors": [
            "Keyword in username and name field",
            "Clear niche in bio",
            "Link in bio (use Linktree or Beacons)",
            "Story highlights organized by topic",
            "Consistent visual aesthetic",
        ],
    },
}

ACCOUNT_AUDIT_CHECKS = [
    "profile_photo", "bio_keyword", "bio_cta", "link_in_bio",
    "posting_consistency", "niche_clarity", "engagement_rate",
    "hashtag_strategy", "content_mix", "cross_promotion",
]


class AccountOptimizer:
    """Generates actionable account optimization plans using trend data."""

    def __init__(self, youtube_api_key: str | None = None, tiktok_ms_token: str | None = None):
        self.analyzer = TrendAnalyzer(youtube_api_key=youtube_api_key, tiktok_ms_token=tiktok_ms_token)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize_account(
        self,
        platform: str,
        niche: str,
        username: str = "",
        follower_count: int = 0,
        region: str = "US",
        current_issues: list[str] | None = None,
    ) -> dict:
        """Generate a full optimization plan for a social media account."""
        platform_lower = platform.lower()
        trend_data = self.analyzer.get_niche_deep_dive(niche=niche, region=region)
        hashtag_data = self.analyzer.get_hashtag_master_list(niche=niche, region=region, follower_count=follower_count)

        audit = self._audit_account(platform_lower, follower_count, niche, current_issues or [])
        profile_fixes = self._get_profile_fixes(platform_lower, niche)
        content_plan = self._build_content_plan(platform_lower, niche, trend_data)
        growth_roadmap = self._build_growth_roadmap(platform_lower, follower_count, niche)

        return {
            "platform": platform,
            "username": username or "your account",
            "niche": niche,
            "follower_tier": self._tier(follower_count),
            "audit": audit,
            "priority_fixes": audit.get("critical", []),
            "profile_optimization": profile_fixes,
            "content_strategy": content_plan,
            "hashtag_strategy": hashtag_data,
            "growth_roadmap": growth_roadmap,
            "algorithm_guide": PLATFORM_ALGORITHMS.get(platform_lower, {}),
            "trend_opportunities": trend_data.get("content_ideas", [])[:5],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def optimize_all_accounts(
        self,
        accounts: list[dict],
        region: str = "US",
    ) -> dict:
        """Optimize multiple accounts across platforms simultaneously."""
        results = {}
        for account in accounts:
            platform = account.get("platform", "tiktok")
            niche = account.get("niche", "general")
            key = f"{platform}_{account.get('username', 'account')}"
            results[key] = self.optimize_account(
                platform=platform,
                niche=niche,
                username=account.get("username", ""),
                follower_count=account.get("followers", 0),
                region=account.get("region", region),
                current_issues=account.get("issues", []),
            )

        unified_strategy = self._build_unified_cross_platform_strategy(accounts, region)
        return {
            "accounts": results,
            "unified_strategy": unified_strategy,
            "repurposing_workflow": self._repurposing_workflow(accounts),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_bio_optimization(self, platform: str, niche: str, goal: str = "followers") -> dict:
        """Generate optimized bio/about section for any platform."""
        templates = {
            "tiktok": {
                "structure": "[Hook/Identity] | [Value you provide] | [CTA with link]",
                "examples": [
                    f"I teach {niche} tips that actually work 💡 | New video daily | Link below 👇",
                    f"Your {niche} bestie 🎯 | Helping you [result] | Follow for daily tips",
                    f"{niche.capitalize()} creator | [City] | DM for collabs 📩",
                ],
                "character_limit": 80,
                "keywords_tip": "TikTok indexes bio for search — include your niche keyword",
            },
            "youtube": {
                "structure": "[Who you are] + [What you post] + [Upload schedule] + [Social links]",
                "examples": [
                    f"I post {niche} content every [day] | Subscribe for weekly tips on [topic]",
                    f"[Your name] | {niche.capitalize()} educator | New videos every [day]",
                ],
                "character_limit": 1000,
                "keywords_tip": "First 100 chars appear in search — front-load your niche keywords",
            },
            "instagram": {
                "structure": "[Title/Name] | [Niche + benefit] | [Social proof] | [CTA + link]",
                "examples": [
                    f"✨ {niche.capitalize()} tips & inspo\n📍 [Location]\n👇 Free [resource] below",
                    f"Helping you [result] with {niche} 🎯\n[Credibility] | [Posts/week]\nLink 👇",
                ],
                "character_limit": 150,
                "keywords_tip": "Use keyword in Name field (not just username) — it's searchable",
            },
        }
        platform_lower = platform.lower()
        template = templates.get(platform_lower, templates["tiktok"])
        return {
            "platform": platform,
            "niche": niche,
            "goal": goal,
            **template,
            "cta_options": [
                "Follow for daily tips",
                f"Save my free {niche} guide (link below)",
                "DM me 'START' to get my [resource]",
                "New post every [day] — don't miss it",
            ],
        }

    def get_thumbnail_strategy(self, platform: str, niche: str) -> dict:
        """Return thumbnail/cover optimization tips for max CTR."""
        return {
            "platform": platform,
            "niche": niche,
            "principles": [
                "Face + emotion gets 30% higher CTR (curiosity, shock, joy work best)",
                "High contrast colors — yellow, red, orange outperform muted tones",
                "Large bold text (max 4-5 words) visible at small size",
                "Consistent brand colors so viewers recognize you in feed",
                "Before/after or open loop ('you won't believe...')",
            ],
            "tools": [
                "Canva (free) — use 1280x720 for YouTube, 1080x1920 for TikTok cover",
                "Adobe Express — free templates for social",
                "Remove.bg — cut out backgrounds for clean face shots",
            ],
            "split_test_tip": "Change ONE element at a time — title, thumbnail, or posting time",
            "tiktok_cover_tip": "TikTok cover: use first 2 seconds as hook — no static thumbnail",
        }

    def get_engagement_boost_plan(self, platform: str, niche: str, follower_count: int = 0) -> dict:
        """Generate tactics to boost engagement rate."""
        return {
            "platform": platform,
            "niche": niche,
            "immediate_actions": [
                "Reply to EVERY comment within first hour of posting (algorithm boost)",
                "Ask a question at the end of every video ('Comment your answer below')",
                "Pin your best comment to start the conversation",
                "Use 'Save this' CTA — saves boost reach more than likes",
                "Duet/stitch trending creators in your niche (TikTok)",
                "Go LIVE for 30 min after posting — boosts visibility window",
            ],
            "weekly_habits": [
                "Engage with 20 accounts in your niche daily (like + comment)",
                "Follow back engaged followers to build community",
                "Post a poll or question in Stories",
                "Feature a follower's comment in your next video",
                "Collaborate with 1 creator per week in your niche",
            ],
            "content_hooks": [
                "Controversy hook: 'Unpopular opinion: ...'",
                "Completion hook: 'Watch until the end for the secret'",
                "FOMO hook: 'Everyone doing this is getting results except...'",
                "Relatability hook: 'If you've ever felt [pain point], this is for you'",
            ],
            "engagement_rate_target": self._engagement_target(follower_count),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _audit_account(self, platform: str, followers: int, niche: str, issues: list[str]) -> dict:
        tier = self._tier(followers)
        critical = []
        improvements = []
        good = []

        # Universal checks
        if "no_bio" in issues or "empty_bio" in issues:
            critical.append("CRITICAL: Bio is empty — add niche keyword + CTA immediately")
        else:
            good.append("Bio: present")

        if "no_link" in issues:
            critical.append("Add link in bio — use Beacons.ai or Linktree (free)")

        if "inconsistent" in issues or "irregular_posting" in issues:
            critical.append("Posting schedule is inconsistent — algorithm punishes gaps >3 days")

        if "no_hashtags" in issues:
            critical.append("No hashtags used — missing discovery traffic")

        if "mixed_niche" in issues or "unfocused" in issues:
            critical.append("Account posts multiple unrelated niches — algorithm can't categorize you")

        if followers < 1000 and "no_growth" in issues:
            improvements.append("Under 1K: focus on hooks + consistency before monetization")

        if not issues:
            improvements.append("Run a content audit: delete or unlist videos under 1K views if <6mo old")
            improvements.append("Check Analytics: identify top 3 performing videos and replicate format")

        return {
            "tier": tier,
            "critical": critical or ["No critical issues detected — focus on optimization"],
            "improvements": improvements or ["Analyze your top performers and double down on that format"],
            "good": good,
            "platform_algorithm": PLATFORM_ALGORITHMS.get(platform, {}).get("ranking_factors", [])[:3],
        }

    def _get_profile_fixes(self, platform: str, niche: str) -> list[dict]:
        fixes = [
            {
                "element": "Profile Photo",
                "action": "Use a clear face shot with good lighting, or a branded logo",
                "priority": "HIGH",
            },
            {
                "element": "Username",
                "action": f"Include niche keyword if possible: @{niche}tips, @{niche}daily, @the{niche}guy",
                "priority": "MEDIUM",
            },
            {
                "element": "Bio/About",
                "action": f"Format: Who you are | What value you give {niche} fans | CTA",
                "priority": "HIGH",
            },
            {
                "element": "Link in Bio",
                "action": "Add Beacons.ai or Linktree with your best content, products, or contact",
                "priority": "HIGH",
            },
        ]
        if platform == "youtube":
            fixes += [
                {"element": "Channel Art", "action": "1280x720 banner with niche + upload schedule", "priority": "MEDIUM"},
                {"element": "Channel Trailer", "action": "60-90 second video: who you are, what you post, why subscribe", "priority": "HIGH"},
                {"element": "Playlists", "action": "Organize videos into 3-5 topic playlists — boosts AVD", "priority": "MEDIUM"},
            ]
        elif platform == "instagram":
            fixes += [
                {"element": "Name Field", "action": f"Add '{niche} tips' or '{niche} creator' to Name (searchable)", "priority": "HIGH"},
                {"element": "Story Highlights", "action": "Create 4-6 highlights: About, Tips, Results, FAQ, Collab", "priority": "MEDIUM"},
            ]
        return fixes

    def _build_content_plan(self, platform: str, niche: str, trend_data: dict) -> dict:
        ideas = trend_data.get("content_ideas", [])
        strategy = trend_data.get("posting_strategy", {})
        freq = strategy.get("frequency", {})
        platform_freq = freq.get(platform.replace("youtube", "YouTube_Shorts"), "1-2/day")

        return {
            "posting_frequency": platform_freq,
            "content_mix": strategy.get("content_mix", {}),
            "this_week_ideas": ideas[:5],
            "video_structure": {
                "hook": "0-3 seconds: say or show the most interesting thing first",
                "value": "3s-60s: deliver on the hook promise",
                "cta": "Last 3s: 'Follow for more', 'Save this', 'Comment [X]'",
            },
            "repurposing": strategy.get("repurposing_workflow", []),
        }

    def _build_growth_roadmap(self, platform: str, followers: int, niche: str) -> list[dict]:
        roadmap = []
        if followers < 1000:
            roadmap.append({
                "phase": "0-1K: Foundation",
                "goal": "Get first 1,000 followers",
                "tactics": [
                    "Post 1x/day minimum for 30 days straight",
                    "Engage with 50 posts/day in your niche",
                    "Use trending sounds + hooks from top creators",
                    "Study your top performers (first 100 videos — quantity over quality)",
                ],
                "timeline": "30-90 days",
            })
        if followers < 10_000:
            roadmap.append({
                "phase": "1K-10K: Consistency",
                "goal": "Hit 10K followers",
                "tactics": [
                    "Identify your 3 best-performing video formats and repeat them",
                    "Collaborate with 2-3 creators in your niche monthly",
                    "Start a series (part 1, 2, 3...) to keep viewers coming back",
                    "Enable monetization features (TikTok Creator Rewards, YouTube Partner)",
                ],
                "timeline": "3-6 months",
            })
        if followers < 100_000:
            roadmap.append({
                "phase": "10K-100K: Scale",
                "goal": "Hit 100K followers",
                "tactics": [
                    "Invest in better lighting + microphone (production quality matters now)",
                    "Build email list as owned audience",
                    "Launch digital product or affiliate marketing",
                    "Cross-post consistently to all platforms",
                    "Hire an editor to increase posting volume",
                ],
                "timeline": "6-18 months",
            })
        if followers >= 100_000:
            roadmap.append({
                "phase": "100K+: Monetize",
                "goal": "Build sustainable revenue",
                "tactics": [
                    "Brand deals: charge $[followers/10] per sponsored post",
                    "Own product launch (course, merch, ebook)",
                    "Subscription / community (Patreon, Discord, TikTok LIVE gifts)",
                    "YouTube AdSense + TikTok Creator Rewards passive income",
                ],
                "timeline": "Ongoing",
            })
        return roadmap

    def _build_unified_cross_platform_strategy(self, accounts: list[dict], region: str) -> dict:
        platforms = [a.get("platform", "") for a in accounts]
        niches = list({a.get("niche", "general") for a in accounts})
        return {
            "platforms": platforms,
            "niches": niches,
            "unified_content_flow": [
                "Step 1: Film one core piece of content (raw footage)",
                "Step 2: Edit primary cut for TikTok (hooks-first, 7-30s)",
                "Step 3: Repurpose same content for YouTube Shorts",
                "Step 4: Add music + cover → Instagram Reels",
                "Step 5: Long-form version → YouTube main channel",
                "Step 6: Screenshots/clips → Twitter/X and LinkedIn",
            ],
            "cross_promotion": [
                "Mention your other platforms in every bio",
                "Post 'Follow me on [platform] for [exclusive content]' once/week",
                "TikTok drives best organic reach → use it to funnel to YouTube/Instagram",
            ],
            "region": region,
        }

    def _repurposing_workflow(self, accounts: list[dict]) -> list[str]:
        platforms = [a.get("platform", "").lower() for a in accounts]
        steps = ["1. Create one video idea with hook + value + CTA"]
        if "tiktok" in platforms:
            steps.append("2. Post raw vertical cut on TikTok first (fastest feedback loop)")
        if "youtube" in platforms:
            steps.append("3. Add captions + thumbnail → YouTube Shorts (same cut, add end card)")
        if "instagram" in platforms:
            steps.append("4. Add trending audio → Instagram Reels")
        steps.append("5. Best-performing video → extend to full YouTube long-form")
        steps.append("6. Text insights from video → Twitter thread / LinkedIn post")
        return steps

    def _tier(self, followers: int) -> str:
        if followers < 1000:
            return "Nano (0-1K)"
        elif followers < 10_000:
            return "Micro (1K-10K)"
        elif followers < 100_000:
            return "Mid-tier (10K-100K)"
        elif followers < 1_000_000:
            return "Macro (100K-1M)"
        else:
            return "Mega (1M+)"

    def _engagement_target(self, followers: int) -> str:
        if followers < 10_000:
            return "5-15% (nano/micro — high engagement expected)"
        elif followers < 100_000:
            return "2-5% (mid-tier)"
        elif followers < 1_000_000:
            return "1-3% (macro)"
        else:
            return "0.5-1.5% (mega — scale dilutes ER)"
