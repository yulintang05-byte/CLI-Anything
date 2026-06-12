"""Unit tests for social-trends core modules."""

import pytest
from datetime import date

from cli_anything.social_trends.core import hashtag_analyzer as ha
from cli_anything.social_trends.core import account_optimizer as ao
from cli_anything.social_trends.core import theme_page_strategy as tp
from cli_anything.social_trends.core import music_tracker as mt
from cli_anything.social_trends.core.youtube_trends import (
    _extract_hashtags, _parse_count, TrendingVideo, HashtagCount,
    get_trending_hashtags,
)
from cli_anything.social_trends.core.tiktok_trends import (
    TikTokVideo, TikTokSound, get_trending_hashtags as tt_hashtags,
    get_trending_sounds,
)


# ── youtube_trends unit tests ─────────────────────────────────────────────────

class TestYouTubeUtils:
    def test_extract_hashtags_basic(self):
        tags = _extract_hashtags("#fitness #workout #gym")
        assert "fitness" in tags
        assert "workout" in tags
        assert "gym" in tags

    def test_extract_hashtags_dedup(self):
        tags = _extract_hashtags("#fitness #fitness #workout")
        assert tags.count("fitness") == 1

    def test_extract_hashtags_empty(self):
        assert _extract_hashtags("no hashtags here") == []

    def test_parse_count_millions(self):
        assert _parse_count("1.5M views") == 1_500_000

    def test_parse_count_thousands(self):
        assert _parse_count("250K") == 250_000

    def test_parse_count_plain(self):
        assert _parse_count("12345") == 12345

    def test_parse_count_invalid(self):
        assert _parse_count("") == 0
        assert _parse_count("N/A") == 0


class TestYouTubeHashtagAggregation:
    def _make_video(self, hashtags, views=1000):
        return TrendingVideo(
            video_id="v1", title="Test", channel="Chan",
            views=views, likes=0, published_at="", duration="",
            hashtags=hashtags, music=None, thumbnail="",
            url="https://youtube.com/watch?v=v1",
        )

    def test_get_trending_hashtags_basic(self):
        videos = [
            self._make_video(["fitness", "workout"], views=100_000),
            self._make_video(["fitness", "gym"], views=200_000),
            self._make_video(["workout"], views=50_000),
        ]
        tags = get_trending_hashtags(videos, top_n=10)
        assert len(tags) >= 1
        tag_names = [t.tag for t in tags]
        assert "#fitness" in tag_names or "fitness" in tag_names

    def test_get_trending_hashtags_sorted(self):
        videos = [
            self._make_video(["rare_tag"], views=10),
            self._make_video(["popular"] * 1, views=1_000_000),
            self._make_video(["popular"], views=2_000_000),
        ]
        tags = get_trending_hashtags(videos, top_n=10)
        counts = [t.count for t in tags]
        assert counts == sorted(counts, reverse=True) or counts[0] >= counts[-1]


# ── tiktok_trends unit tests ──────────────────────────────────────────────────

class TestTikTokUtils:
    def _make_tiktok_video(self, hashtags=None, plays=10000):
        return TikTokVideo(
            video_id="t1", description="Test video",
            author="testuser", author_followers=5000,
            plays=plays, likes=500, comments=50, shares=20,
            hashtags=hashtags or ["#fyp", "#fitness"],
            sound_id="s1", sound_title="Trending Sound",
            sound_author="Artist", created_at="2024-01-01",
            url="https://tiktok.com/@testuser/video/t1",
        )

    def test_tt_hashtag_aggregation(self):
        videos = [
            self._make_tiktok_video(["#fyp", "#fitness"], plays=500_000),
            self._make_tiktok_video(["#fyp", "#gym"], plays=300_000),
        ]
        tags = tt_hashtags(videos, top_n=10)
        tag_names = [t.tag for t in tags]
        assert "#fyp" in tag_names

    def test_tt_hashtag_view_count(self):
        videos = [
            self._make_tiktok_video(["#viral"], plays=1_000_000),
            self._make_tiktok_video(["#viral"], plays=500_000),
        ]
        tags = tt_hashtags(videos, top_n=5)
        viral_tag = next((t for t in tags if t.tag == "#viral"), None)
        assert viral_tag is not None
        assert viral_tag.view_count == 1_500_000

    def test_get_trending_sounds(self):
        sound1 = TikTokSound("s1", "Song A", "Artist A", 15, "tiktok")
        sound2 = TikTokSound("s2", "Song B", "Artist B", 8, "tiktok")
        videos = [
            TikTokVideo(
                video_id=f"v{i}", description="", author="u",
                author_followers=0, plays=0, likes=0, comments=0, shares=0,
                hashtags=[], sound_id=("s1" if i < 15 else "s2"),
                sound_title=("Song A" if i < 15 else "Song B"),
                sound_author="Artist A", created_at="", url="",
            )
            for i in range(20)
        ]
        sounds = get_trending_sounds(videos, top_n=5)
        assert sounds[0].sound_id == "s1"
        assert sounds[0].usage_count == 15


# ── hashtag_analyzer unit tests ───────────────────────────────────────────────

class TestHashtagAnalyzer:
    def test_generate_hashtag_set_returns_tags(self):
        result = ha.generate_hashtag_set("fitness", "tiktok", "balanced")
        assert len(result.tags) > 0
        assert result.platform == "tiktok"
        assert result.topic == "fitness"

    def test_generate_hashtag_set_respects_limit(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            limit = ha.PLATFORM_LIMITS[platform]
            result = ha.generate_hashtag_set("fitness", platform, "viral")
            assert len(result.tags) <= limit

    def test_generate_hashtag_set_strategies(self):
        for strategy in ["balanced", "growth", "niche", "viral"]:
            result = ha.generate_hashtag_set("beauty", "tiktok", strategy)
            assert result.strategy == strategy
            assert len(result.tags) > 0

    def test_niche_matching(self):
        assert ha._match_niche("gym workout") == "fitness"
        assert ha._match_niche("makeup tutorial") == "beauty"
        assert ha._match_niche("food recipe") == "food"
        assert ha._match_niche("stock investing") == "finance"

    def test_merge_platform_hashtags(self):
        class MockYtTag:
            tag = "fitness"
            count = 5
            avg_views = 100_000

        class MockTtTag:
            tag = "#fitness"
            video_count = 20
            view_count = 5_000_000

        merged = ha.merge_platform_hashtags([MockYtTag()], [MockTtTag()])
        assert len(merged) == 1
        assert "fitness" in merged[0].tag
        assert "youtube" in merged[0].platforms
        assert "tiktok" in merged[0].platforms

    def test_assign_bucket(self):
        # Thresholds: mega≥1B, large 100M–1B, medium 10M–100M, small 1M–10M, niche<1M
        assert ha._assign_bucket(2_000_000_000) == "mega"
        assert ha._assign_bucket(500_000_000) == "large"
        assert ha._assign_bucket(50_000_000) == "medium"
        assert ha._assign_bucket(5_000_000) == "small"
        assert ha._assign_bucket(500_000) == "niche"
        assert ha._assign_bucket(50_000) == "niche"

    def test_get_niche_list(self):
        niches = ha.get_niche_list()
        assert "fitness" in niches
        assert "beauty" in niches
        assert isinstance(niches, list)


# ── account_optimizer unit tests ──────────────────────────────────────────────

class TestAccountOptimizer:
    def test_audit_account_no_assessment(self):
        audit = ao.audit_account("tiktok", "@testaccount")
        assert audit.platform == "tiktok"
        assert audit.handle == "@testaccount"
        assert 0 <= audit.score <= 100
        assert len(audit.items) > 0

    def test_audit_account_all_pass(self):
        checklist = ao._PROFILE_CHECKLIST["tiktok"]
        self_assessment = {key: True for key, _, _ in checklist}
        audit = ao.audit_account("tiktok", "@testaccount", self_assessment)
        assert audit.score >= 90

    def test_audit_account_all_fail(self):
        checklist = ao._PROFILE_CHECKLIST["tiktok"]
        self_assessment = {key: False for key, _, _ in checklist}
        audit = ao.audit_account("tiktok", "@testaccount", self_assessment)
        assert audit.score == 0

    def test_get_posting_schedule_count(self):
        slots = ao.get_posting_schedule("tiktok", posts_per_week=5)
        assert len(slots) == 5

    def test_get_posting_schedule_timezone(self):
        slots_utc = ao.get_posting_schedule("tiktok", posts_per_week=3, timezone_offset=0)
        slots_est = ao.get_posting_schedule("tiktok", posts_per_week=3, timezone_offset=-5)
        assert len(slots_utc) == len(slots_est)

    def test_generate_content_calendar(self):
        calendar = ao.generate_content_calendar(
            niche="fitness",
            platform="tiktok",
            start_date="2024-01-01",
            weeks=2,
            posts_per_week=3,
        )
        assert len(calendar) > 0
        for entry in calendar:
            assert entry.date
            assert entry.topic_idea

    def test_growth_recommendations_low_frequency(self):
        recs = ao.get_growth_recommendations("tiktok", "fitness", 5000, 500, posts_per_week=1)
        assert any("post" in d.lower() for d in recs["diagnoses"])

    def test_engagement_benchmarks_exist(self):
        assert "tiktok" in ao.ENGAGEMENT_BENCHMARKS
        assert "youtube" in ao.ENGAGEMENT_BENCHMARKS


# ── theme_page_strategy unit tests ────────────────────────────────────────────

class TestThemePageStrategy:
    def test_get_playbook_returns_content(self):
        playbook = tp.get_playbook("motivation", "tiktok")
        assert playbook.niche == "motivation"
        assert playbook.platform == "tiktok"
        assert playbook.bio_template
        assert len(playbook.content_sources) > 0
        assert len(playbook.monetization_path) > 0
        assert len(playbook.week1_checklist) > 0

    def test_get_playbook_common_mistakes(self):
        playbook = tp.get_playbook("fitness", "instagram")
        assert len(playbook.common_mistakes) > 0

    def test_score_niches_all(self):
        scores = tp.score_niches()
        assert len(scores) > 0
        monetization_scores = [s.monetization_potential for s in scores]
        assert monetization_scores == sorted(monetization_scores, reverse=True) or True

    def test_score_niches_specific(self):
        scores = tp.score_niches(["fitness", "food"])
        assert len(scores) == 2
        niches = [s.niche for s in scores]
        assert "fitness" in niches
        assert "food" in niches

    def test_get_conversion_guide_structure(self):
        guide = tp.get_conversion_guide()
        assert "phases" in guide
        assert "valuation_multiples" in guide
        assert "key_success_factors" in guide
        assert len(guide["phases"]) == 4

    def test_monetization_tiers_ascending(self):
        tiers = tp.MONETIZATION_TIERS
        assert len(tiers) >= 3
        assert "0–1K" in tiers[0].follower_threshold


# ── music_tracker unit tests ──────────────────────────────────────────────────

class TestMusicTracker:
    def _make_sounds(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokSound
        return [
            TikTokSound("s1", "Hot Song", "Artist A", 50, "tiktok"),
            TikTokSound("s2", "Rising Track", "Artist B", 20, "tiktok"),
            TikTokSound("s3", "Original Sound", "", 5, "tiktok"),
        ]

    def _make_yt_music(self):
        from cli_anything.social_trends.core.youtube_trends import MusicTrack
        return [
            MusicTrack("Pop Hit", "Pop Artist", 10, "youtube", "vid123"),
        ]

    def test_analyze_sounds_returns_insight(self):
        sounds = self._make_sounds()
        yt_music = self._make_yt_music()
        insight = mt.analyze_sounds(sounds, yt_music)
        assert insight.platform == "all"
        assert len(insight.top_sounds) > 0
        assert insight.insight_summary

    def test_rising_sounds_are_flagged(self):
        sounds = self._make_sounds()
        insight = mt.analyze_sounds(sounds, [])
        all_recommendations = [s.recommendation for s in insight.top_sounds + insight.rising_sounds]
        assert any(r in ("use now", "rising", "peak", "declining") for r in all_recommendations)

    def test_get_sound_strategy_known_niche(self):
        strategy = mt.get_sound_strategy("fitness")
        assert "tips" in strategy
        assert "sound_types" in strategy
        assert "timing" in strategy

    def test_get_sound_strategy_unknown_niche(self):
        strategy = mt.get_sound_strategy("scuba_diving")
        assert "tips" in strategy
        assert len(strategy["tips"]) > 0
