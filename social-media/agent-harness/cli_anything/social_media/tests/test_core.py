"""Unit tests for cli-anything-social-media core modules.

Tests run entirely on synthetic data — no network calls, no yt-dlp required.
"""

from __future__ import annotations

import pytest
from datetime import datetime

from cli_anything.social_media.core.youtube_scraper import (
    YouTubeTrend, extract_hashtags, _compute_engagement,
    _aggregate_hashtags, _aggregate_music, _detect_viral_patterns,
    TrendingMusic,
)
from cli_anything.social_media.core.tiktok_scraper import (
    TikTokTrend, _extract_hashtags as tt_extract_hashtags,
    _compute_engagement as tt_compute_engagement,
    _compute_virality, _aggregate_hashtags as tt_aggregate_hashtags,
    _aggregate_music as tt_aggregate_music,
    _detect_viral_patterns as tt_detect_viral_patterns,
    _generate_content_strategy,
    TikTokTrendsResult,
)
from cli_anything.social_media.core.account_optimizer import (
    AccountProfile, OptimizationScore,
    _compute_score, _score_profile_completeness, _score_hashtag_quality,
    _score_posting_consistency, _score_engagement_health,
    _critical_fixes, _quick_wins, _strategic_recs,
    _build_hashtag_overhaul, _build_content_calendar,
    _monetization_opportunities,
    optimize_account,
    register_account, get_account, remove_account, list_accounts,
)
from cli_anything.social_media.core.theme_pages import (
    get_niche_analysis, list_niches, get_playbook, get_conversion_strategies,
    compare_niches, NicheAnalysis, ThemePagePlaybook, ConversionStrategy,
)
from cli_anything.social_media.core.trends_aggregator import (
    _merge_hashtags, _merge_sounds, _build_unified_trends,
    _build_proactive_actions,
    YouTubeTrendsResult, TikTokTrendsResult as TT_TrendsResult,
)


# ── Fixtures ──────────────────────────────────────────────────────────

def _make_yt_trend(**kwargs) -> YouTubeTrend:
    defaults = dict(
        title="How to Get Viral on YouTube in 2025",
        video_id="abc123",
        channel="TestChannel",
        view_count=1_000_000,
        like_count=50_000,
        comment_count=5_000,
        upload_date="20250101",
        duration=480,
        hashtags=["youtube", "viral", "howto"],
        music_track="",
        description_snippet="Test video description",
        thumbnail_url="https://img.youtube.com/vi/abc123/default.jpg",
        tags=["youtube", "viral"],
        category="Education",
        engagement_rate=5.5,
    )
    defaults.update(kwargs)
    return YouTubeTrend(**defaults)


def _make_tt_trend(**kwargs) -> TikTokTrend:
    defaults = dict(
        title="POV: You're trying to get fit #fitness #gym",
        video_id="tt001",
        author="fitnessguru",
        author_followers=100_000,
        play_count=5_000_000,
        like_count=500_000,
        comment_count=10_000,
        share_count=50_000,
        duration=30,
        hashtags=["fitness", "gym", "workout"],
        music_title="Motivational Beat",
        music_author="SoundPro",
        music_is_original=False,
        upload_date="20250201",
        thumbnail_url="",
        video_url="https://www.tiktok.com/video/tt001",
        engagement_rate=11.2,
        virality_score=3.5,
    )
    defaults.update(kwargs)
    return TikTokTrend(**defaults)


def _make_account(**kwargs) -> AccountProfile:
    defaults = dict(
        platform="tiktok",
        username="testaccount",
        display_name="Test Account",
        bio="This is a test bio with enough characters to pass the minimum length check for tiktok requirements",
        follower_count=5_000,
        following_count=500,
        post_count=120,
        avg_views=15_000,
        avg_likes=1_200,
        avg_comments=80,
        niche="fitness",
        posting_frequency="daily",
        content_types=["shorts", "tutorials"],
        current_hashtags=["fitness", "gym", "workout"],
        profile_url="https://www.tiktok.com/@testaccount",
        notes="",
    )
    defaults.update(kwargs)
    return AccountProfile(**defaults)


# ══════════════════════════════════════════════════════════════════════
# YouTube scraper unit tests
# ══════════════════════════════════════════════════════════════════════

class TestYouTubeHashtagExtraction:
    def test_basic_hashtag_extraction(self):
        result = extract_hashtags("#fitness #gym #workout")
        assert "fitness" in result
        assert "gym" in result
        assert "workout" in result

    def test_hashtag_in_sentence(self):
        result = extract_hashtags("Check out my #viral video #2025tips")
        assert "viral" in result
        assert "2025tips" in result

    def test_no_hashtags(self):
        result = extract_hashtags("No hashtags here at all")
        assert result == []

    def test_duplicate_hashtags_preserved(self):
        # extract_hashtags does not deduplicate — that's done downstream
        result = extract_hashtags("#fitness #fitness #gym")
        assert result.count("fitness") == 2

    def test_hashtags_are_lowercase(self):
        result = extract_hashtags("#Fitness #GYM #WorkOut")
        assert all(t == t.lower() for t in result)


class TestYouTubeEngagement:
    def test_zero_views(self):
        assert _compute_engagement(0, 100, 10) == 0.0

    def test_normal_engagement(self):
        rate = _compute_engagement(1_000_000, 50_000, 5_000)
        assert rate == pytest.approx(5.5, abs=0.01)

    def test_high_engagement(self):
        rate = _compute_engagement(100_000, 20_000, 3_000)
        assert rate > 20.0


class TestYouTubeAggregation:
    def test_aggregate_hashtags_empty(self):
        result = _aggregate_hashtags([])
        assert result == []

    def test_aggregate_hashtags_counts(self):
        trends = [
            _make_yt_trend(hashtags=["fitness", "viral"], view_count=500_000),
            _make_yt_trend(hashtags=["fitness", "gym"], view_count=1_000_000),
            _make_yt_trend(hashtags=["fitness"], view_count=2_000_000),
        ]
        result = _aggregate_hashtags(trends)
        fitness = next((h for h in result if h["tag"] == "fitness"), None)
        assert fitness is not None
        assert fitness["count"] == 3
        assert fitness["avg_views"] == pytest.approx(1_166_666, abs=10)

    def test_aggregate_hashtags_sorted_by_score(self):
        trends = [
            _make_yt_trend(hashtags=["popular"] * 5, view_count=10_000_000),
            _make_yt_trend(hashtags=["rare"], view_count=100),
        ]
        result = _aggregate_hashtags(trends)
        assert result[0]["tag"] == "popular"

    def test_aggregate_music(self):
        trends = [
            _make_yt_trend(music_track="Hit Song - Artist A"),
            _make_yt_trend(music_track="Hit Song - Artist A"),
            _make_yt_trend(music_track="Other Song"),
        ]
        result = _aggregate_music(trends)
        assert len(result) == 2
        top = result[0]
        assert top.title == "Hit Song - Artist A"
        assert top.use_count == 2

    def test_aggregate_music_empty(self):
        trends = [_make_yt_trend(music_track="")]
        result = _aggregate_music(trends)
        assert result == []

    def test_detect_viral_patterns_shorts(self):
        trends = [_make_yt_trend(duration=30) for _ in range(10)]
        patterns = _detect_viral_patterns(trends)
        assert any("Short" in p or "short" in p for p in patterns)

    def test_detect_viral_patterns_numbers_in_title(self):
        trends = [
            _make_yt_trend(title="10 Ways to Go Viral"),
            _make_yt_trend(title="5 Secrets of YouTube"),
            _make_yt_trend(title="3 Tips for Growth"),
            _make_yt_trend(title="Top 7 Hacks"),
            _make_yt_trend(title="Normal title here"),
        ]
        patterns = _detect_viral_patterns(trends)
        assert any("Number" in p or "number" in p.lower() for p in patterns)


# ══════════════════════════════════════════════════════════════════════
# TikTok scraper unit tests
# ══════════════════════════════════════════════════════════════════════

class TestTikTokHashtagExtraction:
    def test_basic(self):
        result = tt_extract_hashtags("#fitness #gym #fyp")
        assert "fitness" in result
        assert "gym" in result
        assert "fyp" in result

    def test_embedded(self):
        result = tt_extract_hashtags("My daily workout routine #workout #fitnessmotivation")
        assert "workout" in result


class TestTikTokEngagement:
    def test_zero_plays(self):
        assert tt_compute_engagement(0, 100, 10, 5) == 0.0

    def test_typical_tiktok_engagement(self):
        rate = tt_compute_engagement(1_000_000, 80_000, 5_000, 15_000)
        assert rate == pytest.approx(10.0, abs=0.01)


class TestTikTokVirality:
    def test_high_plays_low_followers(self):
        score = _compute_virality(10_000_000, 500_000, 200_000, 1_000)
        assert score > 5.0  # should be very high virality

    def test_zero_plays(self):
        score = _compute_virality(0, 0, 0, 1_000)
        assert score == 0.0


class TestTikTokAggregation:
    def test_aggregate_hashtags(self):
        trends = [
            _make_tt_trend(hashtags=["fyp", "fitness"], play_count=1_000_000),
            _make_tt_trend(hashtags=["fyp", "gym"], play_count=2_000_000),
        ]
        result = tt_aggregate_hashtags(trends)
        fyp = next((h for h in result if h["tag"] == "fyp"), None)
        assert fyp is not None
        assert fyp["count"] == 2

    def test_aggregate_music(self):
        trends = [
            _make_tt_trend(music_title="Song A", music_author="Artist X", play_count=5_000_000),
            _make_tt_trend(music_title="Song A", music_author="Artist X", play_count=3_000_000),
        ]
        result = tt_aggregate_music(trends)
        assert len(result) == 1
        assert result[0].title == "Song A"
        assert result[0].video_count == 2

    def test_detect_viral_patterns_short_clips(self):
        trends = [_make_tt_trend(duration=10) for _ in range(10)]
        patterns = tt_detect_viral_patterns(trends)
        assert any("Ultra-short" in p or "15s" in p for p in patterns)

    def test_generate_content_strategy_with_hashtags(self):
        hashtags = [{"tag": "fitness", "count": 5, "avg_plays": 2_000_000, "trend_score": 10}]
        music = []
        strategy = _generate_content_strategy([], hashtags, music)
        assert any("fitness" in s for s in strategy)


# ══════════════════════════════════════════════════════════════════════
# Account optimizer unit tests
# ══════════════════════════════════════════════════════════════════════

class TestAccountScoring:
    def test_score_completeness_full_profile(self):
        account = _make_account()
        score = _score_profile_completeness(account)
        assert score >= 70

    def test_score_completeness_empty_bio(self):
        account = _make_account(bio="")
        score = _score_profile_completeness(account)
        assert score < 80

    def test_score_hashtag_quality_ideal_range(self):
        account = _make_account(
            platform="tiktok",
            current_hashtags=["fitness", "gym", "workout", "fyp", "viral", "foryou"]
        )
        score = _score_hashtag_quality(account)
        assert score >= 80

    def test_score_hashtag_quality_no_hashtags(self):
        account = _make_account(current_hashtags=[])
        score = _score_hashtag_quality(account)
        assert score <= 15

    def test_score_posting_consistency_daily(self):
        account = _make_account(platform="tiktok", posting_frequency="daily")
        score = _score_posting_consistency(account)
        assert score >= 90

    def test_score_posting_consistency_weekly(self):
        account = _make_account(posting_frequency="weekly")
        score = _score_posting_consistency(account)
        assert score <= 55

    def test_score_engagement_above_benchmark(self):
        # 12% engagement rate on TikTok is great
        account = _make_account(avg_views=100_000, avg_likes=12_000, avg_comments=500)
        score = _score_engagement_health(account)
        assert score >= 75

    def test_compute_overall_score_range(self):
        account = _make_account()
        score = _compute_score(account)
        assert 0 <= score.overall <= 100
        assert 0 <= score.profile_completeness <= 100
        assert 0 <= score.hashtag_quality <= 100

    def test_engagement_rate_calculation(self):
        account = _make_account(avg_views=100_000, avg_likes=5_000, avg_comments=500)
        rate = account.engagement_rate()
        assert rate == pytest.approx(5.5, abs=0.01)

    def test_engagement_rate_zero_views(self):
        account = _make_account(avg_views=0)
        assert account.engagement_rate() == 0.0


class TestOptimizationRecommendations:
    def test_critical_fixes_low_engagement(self):
        account = _make_account(avg_views=100_000, avg_likes=100, avg_comments=10)
        score = _compute_score(account)
        fixes = _critical_fixes(account, score)
        # low engagement should trigger a fix
        assert any("engagement" in f.lower() for f in fixes)

    def test_quick_wins_bio_no_cta(self):
        account = _make_account(bio="Just a generic bio")
        wins = _quick_wins(account)
        assert any("CTA" in w or "call-to-action" in w.lower() or "bio" in w.lower() for w in wins)

    def test_strategic_recs_not_empty(self):
        account = _make_account()
        recs = _strategic_recs(account)
        assert len(recs) >= 4

    def test_hashtag_overhaul_fitness(self):
        account = _make_account(niche="fitness", current_hashtags=["old1", "old2"])
        plan = _build_hashtag_overhaul(account)
        assert "remove" in plan
        assert "add_niche" in plan
        assert len(plan["add_niche"]) > 0

    def test_content_calendar_7_days(self):
        account = _make_account()
        calendar = _build_content_calendar(account)
        assert len(calendar) == 7
        days = [c["day"] for c in calendar]
        assert "Monday" in days and "Sunday" in days

    def test_monetization_opportunities_small_account(self):
        account = _make_account(follower_count=500)
        opps = _monetization_opportunities(account)
        assert any("AFFILIATE" in o or "DIGITAL" in o for o in opps)

    def test_monetization_opportunities_large_account(self):
        account = _make_account(follower_count=50_000)
        opps = _monetization_opportunities(account)
        assert any("BRAND DEAL" in o or "brand" in o.lower() for o in opps)

    def test_optimize_account_returns_report(self):
        account = _make_account()
        report = optimize_account(account)
        assert report.account == account
        assert 0 <= report.score.overall <= 100
        assert isinstance(report.critical_fixes, list)
        assert isinstance(report.quick_wins, list)
        assert isinstance(report.content_calendar, list)


class TestAccountRegistry:
    """Tests for the local account registry (file-based storage)."""

    def setup_method(self):
        """Register a fresh test account before each test."""
        self.test_profile = _make_account(username="pytest_test_user_001")
        register_account(self.test_profile)

    def teardown_method(self):
        """Remove test account after each test."""
        remove_account("tiktok", "pytest_test_user_001")

    def test_register_and_retrieve(self):
        profile = get_account("tiktok", "pytest_test_user_001")
        assert profile is not None
        assert profile.username == "pytest_test_user_001"
        assert profile.platform == "tiktok"

    def test_list_accounts_contains_registered(self):
        accounts = list_accounts()
        usernames = [a.username for a in accounts]
        assert "pytest_test_user_001" in usernames

    def test_remove_account(self):
        removed = remove_account("tiktok", "pytest_test_user_001")
        assert removed is True
        profile = get_account("tiktok", "pytest_test_user_001")
        assert profile is None

    def test_remove_nonexistent(self):
        removed = remove_account("tiktok", "nonexistent_account_xyz")
        assert removed is False

    def test_get_nonexistent(self):
        profile = get_account("youtube", "nonexistent_xyz_99")
        assert profile is None


# ══════════════════════════════════════════════════════════════════════
# Theme pages unit tests
# ══════════════════════════════════════════════════════════════════════

class TestNicheAnalysis:
    def test_get_fitness_niche(self):
        niche = get_niche_analysis("fitness")
        assert niche is not None
        assert niche.niche == "fitness"
        assert niche.monetization_potential in ("low", "medium", "high", "very high")
        assert len(niche.top_hashtags) > 0
        assert len(niche.monetization_paths) > 0

    def test_get_personal_finance_niche(self):
        niche = get_niche_analysis("personal_finance")
        assert niche is not None
        assert niche.avg_cpm > 10  # finance has high CPM

    def test_get_unknown_niche(self):
        niche = get_niche_analysis("nonexistent_niche_xyz")
        assert niche is None

    def test_list_niches_not_empty(self):
        niches = list_niches()
        assert len(niches) >= 5
        niche_names = [n.niche for n in niches]
        assert "fitness" in niche_names
        assert "travel" in niche_names

    def test_compare_niches(self):
        results = compare_niches(["fitness", "personal_finance", "travel"])
        assert len(results) == 3

    def test_compare_niches_partial_match(self):
        results = compare_niches(["fitness", "unknown_niche"])
        assert len(results) == 1
        assert results[0].niche == "fitness"

    def test_compare_niches_empty(self):
        results = compare_niches([])
        assert results == []


class TestThemePagePlaybook:
    def test_get_playbook_fitness_tiktok(self):
        playbook = get_playbook("fitness", "tiktok")
        assert playbook.niche == "fitness"
        assert playbook.platform == "tiktok"
        assert len(playbook.phase_1_launch) >= 5
        assert len(playbook.phase_2_growth) >= 4
        assert len(playbook.phase_3_scale) >= 4
        assert len(playbook.phase_4_monetize) >= 4
        assert len(playbook.content_sources) >= 5
        assert len(playbook.monetization_timeline) >= 4
        assert len(playbook.tools_needed) >= 4
        assert len(playbook.common_mistakes) >= 8
        assert len(playbook.bio_templates) >= 3
        assert len(playbook.hashtag_sets) >= 2

    def test_get_playbook_any_niche(self):
        # Should work for any niche, even unknown (falls back to motivation)
        playbook = get_playbook("some_custom_niche", "instagram")
        assert playbook is not None
        assert len(playbook.phase_1_launch) > 0

    def test_playbook_to_dict(self):
        playbook = get_playbook("travel", "youtube")
        data = playbook.to_dict()
        assert "phase_1_launch" in data
        assert "monetization_timeline" in data
        assert isinstance(data["tools_needed"], list)


class TestConversionStrategies:
    def test_get_all_strategies(self):
        strategies = get_conversion_strategies()
        assert len(strategies) >= 4

    def test_filter_beginner(self):
        strategies = get_conversion_strategies(difficulty="beginner")
        assert all(s.difficulty == "beginner" for s in strategies)
        assert len(strategies) >= 2

    def test_filter_intermediate(self):
        strategies = get_conversion_strategies(difficulty="intermediate")
        assert all(s.difficulty == "intermediate" for s in strategies)

    def test_strategy_structure(self):
        strategies = get_conversion_strategies()
        for s in strategies:
            assert s.strategy_name
            assert s.income_potential
            assert len(s.steps) >= 4
            assert len(s.tools) >= 1
            assert s.difficulty in ("beginner", "intermediate", "advanced")


# ══════════════════════════════════════════════════════════════════════
# Trends aggregator unit tests
# ══════════════════════════════════════════════════════════════════════

class TestTrendsAggregator:
    def _make_yt_tags(self):
        return [
            {"tag": "viral", "count": 5, "avg_views": 1_000_000, "trend_score": 5.0},
            {"tag": "trending", "count": 3, "avg_views": 500_000, "trend_score": 1.5},
            {"tag": "youtube", "count": 8, "avg_views": 800_000, "trend_score": 6.4},
        ]

    def _make_tt_tags(self):
        return [
            {"tag": "viral", "count": 10, "avg_plays": 2_000_000, "trend_score": 20.0},
            {"tag": "fyp", "count": 15, "avg_plays": 3_000_000, "trend_score": 45.0},
            {"tag": "tiktok", "count": 7, "avg_plays": 1_200_000, "trend_score": 8.4},
        ]

    def test_merge_hashtags_combines_both(self):
        yt = self._make_yt_tags()
        tt = self._make_tt_tags()
        merged = _merge_hashtags(yt, tt)
        tags = [t.lstrip("#") for t in merged]
        assert "viral" in tags  # in both — should rank high
        assert "fyp" in tags
        assert "youtube" in tags

    def test_merge_hashtags_cross_platform_bonus(self):
        yt = [{"tag": "viral", "count": 1, "avg_views": 100_000, "trend_score": 0.1}]
        tt = [{"tag": "viral", "count": 1, "avg_plays": 100_000, "trend_score": 0.1}]
        merged = _merge_hashtags(yt, tt)
        # "viral" should be first since it's the only tag
        assert merged[0].lstrip("#") == "viral"

    def test_merge_hashtags_empty_inputs(self):
        merged = _merge_hashtags([], [])
        assert merged == []

    def test_merge_sounds(self):
        from cli_anything.social_media.core.youtube_scraper import TrendingMusic
        from cli_anything.social_media.core.tiktok_scraper import TikTokMusicTrend
        yt_music = [
            TrendingMusic("Song A", "Artist 1", ["v1"], 3, 500_000, 1.5),
        ]
        tt_music = [
            TikTokMusicTrend("soundA", "Song B", "Artist 2", 5, 1_000_000, False, 5.0),
        ]
        sounds = _merge_sounds(yt_music, tt_music)
        assert len(sounds) >= 2

    def test_merge_sounds_empty(self):
        sounds = _merge_sounds([], [])
        assert sounds == []

    def test_proactive_actions_not_empty(self):
        yt_result = YouTubeTrendsResult(
            scraped_at=datetime.utcnow().isoformat() + "Z",
            region="US", category="trending",
            trends=[], top_hashtags=self._make_yt_tags(),
            trending_music=[], viral_patterns=["Pattern 1 detected"],
        )
        actions = _build_proactive_actions(yt_result, None, [], [], [])
        assert len(actions) > 0
