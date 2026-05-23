"""Account optimizer — audit and optimize social media profiles.

Analyzes account metrics and generates an optimization plan covering:
- Bio / profile optimization
- Content mix strategy
- Posting schedule
- Hashtag audit
- Engagement tactics
- Growth levers
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict


# ── Profile audit models ───────────────────────────────────────────────

@dataclass
class ProfileMetrics:
    """Current state of an account."""
    handle: str
    platform: str            # tiktok | youtube | instagram | all
    followers: int = 0
    following: int = 0
    total_videos: int = 0
    avg_views: int = 0
    avg_likes: int = 0
    avg_comments: int = 0
    avg_shares: int = 0
    engagement_rate: float = 0.0   # (likes+comments+shares) / views * 100
    niche: str = ""
    bio: str = ""
    has_link_in_bio: bool = False
    has_profile_photo: bool = True
    posting_frequency_per_week: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OptimizationReport:
    """Full account optimization report."""
    handle: str
    platform: str
    grade: str = "N/A"             # A+, A, B, C, D, F
    score: int = 0                 # 0-100
    critical_fixes: list[str] = field(default_factory=list)
    profile_optimizations: list[str] = field(default_factory=list)
    content_strategy: list[str] = field(default_factory=list)
    hashtag_strategy: list[str] = field(default_factory=list)
    growth_tactics: list[str] = field(default_factory=list)
    monetization_opportunities: list[str] = field(default_factory=list)
    estimated_growth: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# ── Optimizer ─────────────────────────────────────────────────────────

class AccountOptimizer:
    """Generate an optimization plan for a social media account."""

    # Benchmarks by follower tier
    _ER_BENCHMARKS = {
        "nano":   (1_000,     10_000,  6.0),   # <10k: ER% floor
        "micro":  (10_000,   100_000,  3.0),
        "mid":    (100_000,  500_000,  2.0),
        "macro":  (500_000, 1_000_000, 1.5),
        "mega":   (1_000_000, 999_999_999, 1.0),
    }

    def _get_tier(self, followers: int) -> tuple[str, float]:
        for tier, (low, high, er_min) in self._ER_BENCHMARKS.items():
            if low <= followers < high:
                return tier, er_min
        return "nano", 6.0

    def analyze(self, metrics: ProfileMetrics, trending_hashtags: list[str] | None = None) -> OptimizationReport:
        """Run a full account audit and produce an optimization report."""
        score = 0
        critical = []
        profile_opts = []
        content_strategy = []
        hashtag_strategy = []
        growth_tactics = []
        monetization = []

        tier, er_benchmark = self._get_tier(metrics.followers)

        # ── Profile completeness ───────────────────────────────────────
        if not metrics.bio:
            critical.append("❌ CRITICAL: Add a bio immediately — accounts without bios lose 40% of profile visitors")
        elif len(metrics.bio) < 50:
            profile_opts.append("⚠️  Bio is too short. Use all available characters: niche + value prop + CTA + location emoji")
            score += 3
        else:
            score += 8

        if not metrics.has_link_in_bio:
            critical.append("❌ CRITICAL: No link in bio — add Linktree/Stan Store/Beacons to capture leads NOW")
        else:
            score += 7

        if not metrics.has_profile_photo:
            critical.append("❌ CRITICAL: Add a professional profile photo — stick to a recognizable face or brand logo")
        else:
            score += 5

        # ── Bio optimization tips ──────────────────────────────────────
        profile_opts += [
            "✏️  Bio formula: [What you do] + [Who you help] + [Result/value] + [CTA with emoji arrow ↓]",
            "✏️  Use 1-2 relevant emojis in bio to increase visual scannability",
            "✏️  Add niche keywords to bio for discoverability (TikTok/IG search)",
            "✏️  Pin your 3 best-performing videos to profile grid for new visitors",
        ]

        # ── Engagement rate audit ──────────────────────────────────────
        if metrics.avg_views > 0 and metrics.engagement_rate == 0:
            calculated_er = (
                (metrics.avg_likes + metrics.avg_comments + metrics.avg_shares)
                / metrics.avg_views * 100
            )
            metrics.engagement_rate = round(calculated_er, 2)

        if metrics.engagement_rate > 0:
            if metrics.engagement_rate >= er_benchmark * 1.5:
                score += 20
                content_strategy.append(f"🌟 Excellent engagement rate {metrics.engagement_rate:.1f}% — well above {tier} benchmark {er_benchmark}%")
            elif metrics.engagement_rate >= er_benchmark:
                score += 15
                content_strategy.append(f"✅ Good engagement rate {metrics.engagement_rate:.1f}% — at {tier} benchmark {er_benchmark}%")
            elif metrics.engagement_rate >= er_benchmark * 0.5:
                score += 8
                content_strategy.append(f"⚠️  Below-benchmark engagement {metrics.engagement_rate:.1f}% (benchmark: {er_benchmark}%) — content relevance issue")
                critical.append("⚠️  Engagement below benchmark — shift to trending formats: POV, reaction, storytime")
            else:
                score += 2
                critical.append(f"❌ Very low engagement {metrics.engagement_rate:.1f}% — likely posting for wrong audience or at wrong times")
        else:
            content_strategy.append("📊 Provide avg_views + avg_likes to get engagement rate analysis")

        # ── Posting frequency ──────────────────────────────────────────
        if metrics.posting_frequency_per_week >= 7:
            score += 15
            content_strategy.append("✅ Daily posting — maintain this; algorithm rewards consistency")
        elif metrics.posting_frequency_per_week >= 3:
            score += 10
            content_strategy.append("📅 3-6x/week — good. Push to daily for 30 days to test algorithm response")
        elif metrics.posting_frequency_per_week >= 1:
            score += 5
            critical.append("⚠️  Posting under 3x/week — you need minimum 3-7x/week to stay in algorithm rotation")
        elif metrics.posting_frequency_per_week > 0:
            critical.append("❌ Posting less than once/week — account is effectively invisible to algorithm")
        else:
            content_strategy.append("📅 Set your posting frequency target: recommend 1-2x/day for growth phase")

        # ── Content strategy ───────────────────────────────────────────
        content_strategy += self._platform_content_strategy(metrics.platform, tier, metrics.niche)

        # ── Hashtag strategy ───────────────────────────────────────────
        hashtag_strategy += self._hashtag_strategy(metrics.platform, trending_hashtags or [])

        # ── Growth tactics ─────────────────────────────────────────────
        growth_tactics += self._growth_tactics(tier, metrics.platform)

        # ── Monetization ───────────────────────────────────────────────
        monetization += self._monetization_plan(tier, metrics.followers, metrics.niche, metrics.platform)

        # ── Score → grade ──────────────────────────────────────────────
        score = min(score, 100)
        if score >= 85:
            grade = "A+"
        elif score >= 75:
            grade = "A"
        elif score >= 65:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 35:
            grade = "D"
        else:
            grade = "F"

        growth_estimate = self._estimate_growth(tier, metrics.posting_frequency_per_week, score)

        return OptimizationReport(
            handle=metrics.handle,
            platform=metrics.platform,
            grade=grade,
            score=score,
            critical_fixes=critical,
            profile_optimizations=profile_opts,
            content_strategy=content_strategy,
            hashtag_strategy=hashtag_strategy,
            growth_tactics=growth_tactics,
            monetization_opportunities=monetization,
            estimated_growth=growth_estimate,
        )

    def _platform_content_strategy(self, platform: str, tier: str, niche: str) -> list[str]:
        base = [
            "CONTENT MIX: 70% trending formats + 20% educational/value + 10% promotional",
            "HOOK: First 0-3 seconds must stop the scroll — use a bold statement, question, or visual shock",
            "LOOP: Design videos to loop seamlessly — TikTok/Reels counts replays as re-views",
        ]
        if platform in ("tiktok", "all"):
            base += [
                "TIKTOK: Use trending sounds within 48h of peak for 2-3x algorithmic boost",
                "TIKTOK: Duet/Stitch viral creators — borrows their audience for free",
                "TIKTOK: Series content (Part 1, 2, 3) keeps viewers returning and boosts saves",
                "TIKTOK: 7-15s videos get highest completion; 21-34s for storytelling/education",
            ]
        if platform in ("youtube", "all"):
            base += [
                "YOUTUBE SHORTS: 60s max, vertical 9:16, hook in first 3 frames",
                "YOUTUBE SHORTS: Add to a Shorts playlist — boosts shelf visibility",
                "YOUTUBE LONG-FORM: 8-15 min sweet spot for ad revenue + watch time",
                "YOUTUBE: Upload custom thumbnails — 90% of top videos use them",
            ]
        return base

    def _hashtag_strategy(self, platform: str, trending: list[str]) -> list[str]:
        strat = []
        if platform in ("tiktok", "all"):
            strat.append("TIKTOK HASHTAGS: Use 3-5 total. Formula: 1-2 mega + 1-2 niche + 1 branded")
            strat.append("TIKTOK: #fyp and #viral are worth including but not sole driver — niche tags matter more")
        if platform in ("youtube", "all"):
            strat.append("YOUTUBE: Use 3-5 hashtags in description — first 3 appear as clickable tags under title")
            strat.append("YOUTUBE SHORTS: Include #Shorts as mandatory hashtag for Shorts shelf discovery")

        if trending:
            strat.append("CURRENT TRENDING (add to next 3 posts): " + " ".join(trending[:8]))

        strat += [
            "MID-TAIL STRATEGY: Mix 100M+ view hashtags with 1M-10M niche tags",
            "AVOID: Banned hashtags (check each quarterly) — they shadow-ban your content",
            "ROTATE: Change hashtag combinations every week — avoid algorithmic repetition flags",
        ]
        return strat

    def _growth_tactics(self, tier: str, platform: str) -> list[str]:
        tactics = [
            "ENGAGEMENT PODS: Join 5-10 person pods in your niche — comment on each other within 30min of posting",
            "REPLY FAST: Respond to every comment within 1h of posting — TikTok/IG rank comment speed",
            "COLLAB: Message 3 accounts your size/niche per week for duets/collabs",
            "CROSS-POST: Same video on TikTok → Instagram Reels → YouTube Shorts (3x reach, 1x effort)",
            "PINNED COMMENT: Pin a comment on your posts asking a follow-up question to drive more comments",
            "TREND JACK: Jump on trending audio/hashtags within 6h of them breaking — first-mover advantage",
        ]
        if tier in ("nano", "micro"):
            tactics += [
                "FOLLOW/ENGAGE: Engage with 30-50 accounts in your niche daily — comment genuinely (not 'nice post')",
                "NICHE COMMUNITIES: Participate in Reddit, Discord, and Facebook groups in your niche — drive traffic",
            ]
        if tier in ("mid", "macro", "mega"):
            tactics += [
                "BRAND COLLABS: Reach out to 5 brands/week in your niche for paid partnerships",
                "UGC (User Generated Content): Encourage reposts/duets — free distribution via followers",
            ]
        return tactics

    def _monetization_plan(self, tier: str, followers: int, niche: str, platform: str) -> list[str]:
        plans = []
        if followers >= 1_000:
            plans += [
                "AFFILIATE MARKETING: Sign up for Amazon Associates, ShareASale, Impact — add links to bio/captions",
                "DIGITAL PRODUCTS: Sell a $7-27 PDF guide, template, or preset pack via Gumroad/Stan",
            ]
        if followers >= 5_000:
            plans.append("SHOUTOUTS: Charge $50-200/post for smaller accounts in your niche (post in creator marketplace groups)")
        if followers >= 10_000:
            plans += [
                "BRAND DEALS: Minimum $100-500/post at this level. Use Creator.co or AspireIQ to connect with brands",
                "TIKTOK CREATOR FUND / YOUTUBE PARTNER: Apply for platform monetization programs",
            ]
        if followers >= 50_000:
            plans += [
                "BRAND DEALS: Command $500-2,000+/post. Pitch brands directly via email with media kit",
                "MEMBERSHIPS: Launch Patreon or YouTube Memberships for $5-20/month tier",
                "CONSULTING: Offer 1:1 coaching calls in your niche — $100-300/hr",
            ]
        if followers >= 100_000:
            plans += [
                "SPEAKING/EVENTS: Conference speaking, podcasts, brand ambassador roles",
                "OWN PRODUCT LINE: Launch merch, course ($297-997), or SaaS tool in your niche",
            ]

        if not plans:
            plans = [
                "BUILD TO 1,000 FOLLOWERS FIRST: Focus on content quality and consistency before monetizing",
                "DOCUMENT JOURNEY: 'Growing to X followers' series builds audience and trust simultaneously",
            ]
        return plans

    def _estimate_growth(self, tier: str, freq: float, score: int) -> str:
        multiplier = {
            "nano": 0.15,    # 15% monthly growth realistic
            "micro": 0.08,
            "mid": 0.05,
            "macro": 0.03,
            "mega": 0.01,
        }.get(tier, 0.1)

        freq_factor = min(freq / 7.0, 1.0) if freq > 0 else 0.3
        score_factor = score / 100.0
        monthly_growth = multiplier * freq_factor * score_factor * 100

        return (
            f"Estimated monthly follower growth: {monthly_growth:.0f}% "
            f"(based on {tier} tier, {freq:.1f}x/week posting, optimization score {score}/100). "
            "Improve score + post daily to 2x this estimate."
        )
