"""Unit tests for social-trends core modules (no network required)."""

import pytest
from datetime import datetime, timezone


# ── TikTok scraper tests ───────────────────────────────────────────────

class TestTikTokScraper:
    def test_fallback_hashtags_returns_list(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        s = TikTokScraper()
        hashtags = s._fallback_trending_hashtags()
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0
        assert all(isinstance(h.name, str) and h.name for h in hashtags)

    def test_fallback_sounds_returns_list(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        s = TikTokScraper()
        sounds = s._fallback_trending_sounds()
        assert isinstance(sounds, list)
        assert len(sounds) > 0
        assert all(isinstance(s_.title, str) and s_.title for s_ in sounds)

    def test_parse_video_item_valid(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        s = TikTokScraper()
        item = {
            "id": "123456",
            "desc": "Check out #fyp #viral this is cool",
            "author": {"uniqueId": "testuser", "followerCount": 10000},
            "stats": {"diggCount": 500, "commentCount": 20, "shareCount": 10, "playCount": 5000},
            "music": {"title": "Test Song", "authorName": "Test Artist"},
            "video": {"duration": 15},
            "challenges": [{"title": "fyp"}, {"title": "viral"}],
        }
        video = s._parse_video_item(item)
        assert video is not None
        assert video.id == "123456"
        assert video.author == "testuser"
        assert "fyp" in video.hashtags
        assert video.like_count == 500
        assert video.play_count == 5000

    def test_parse_video_item_invalid(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        s = TikTokScraper()
        assert s._parse_video_item({}) is None

    def test_trending_hashtag_to_dict(self):
        from cli_anything.social_trends.core.tiktok_scraper import TrendingHashtag
        ht = TrendingHashtag(name="fyp", id="123", view_count=1000000)
        d = ht.to_dict()
        assert d["name"] == "fyp"
        assert d["view_count"] == 1000000

    def test_trending_sound_to_dict(self):
        from cli_anything.social_trends.core.tiktok_scraper import TrendingSound
        s = TrendingSound(title="Test", artist="Artist", video_count=50000)
        d = s.to_dict()
        assert d["title"] == "Test"
        assert d["video_count"] == 50000

    def test_trending_video_to_dict(self):
        from cli_anything.social_trends.core.tiktok_scraper import TrendingVideo
        v = TrendingVideo(id="abc", description="test #fyp", author="testuser",
                          hashtags=["fyp", "viral"])
        d = v.to_dict()
        assert d["id"] == "abc"
        assert "fyp" in d["hashtags"]

    def test_report_to_dict_structure(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokTrendReport, TrendingHashtag
        r = TikTokTrendReport(
            scraped_at="2025-01-01T00:00:00Z",
            region="US",
            trending_hashtags=[TrendingHashtag(name="fyp", view_count=1000)],
        )
        d = r.to_dict()
        assert "trending_hashtags" in d
        assert d["region"] == "US"
        assert len(d["trending_hashtags"]) == 1


# ── YouTube scraper tests ──────────────────────────────────────────────

class TestYouTubeScraper:
    def test_parse_video_item_valid(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
        s = YouTubeScraper()
        item = {
            "id": "yt_001",
            "snippet": {
                "title": "Artist - Song Title #music #trending",
                "channelTitle": "Music Channel",
                "channelId": "UC123",
                "description": "Check #pop music video",
                "categoryId": "10",
                "publishedAt": "2025-01-01T00:00:00Z",
                "tags": ["music", "pop", "2025"],
                "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
            },
            "statistics": {"viewCount": "1000000", "likeCount": "50000", "commentCount": "2000"},
            "contentDetails": {"duration": "PT3M45S"},
        }
        v = s._parse_video_item(item)
        assert v is not None
        assert v.id == "yt_001"
        assert v.view_count == 1000000
        assert v.category_name == "Music"
        assert "music" in v.hashtags or "trending" in v.hashtags

    def test_parse_video_item_empty(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
        s = YouTubeScraper()
        assert s._parse_video_item({}) is None

    def test_get_top_hashtags(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper, YouTubeTrendingVideo
        s = YouTubeScraper()
        videos = [
            YouTubeTrendingVideo("1", "Test", "Ch", hashtags=["viral", "trending"]),
            YouTubeTrendingVideo("2", "Test2", "Ch2", hashtags=["viral", "music"]),
            YouTubeTrendingVideo("3", "Test3", "Ch3", hashtags=["music", "trending"]),
        ]
        top = s.get_top_hashtags(videos)
        assert "viral" in top[:3] or "music" in top[:3]

    def test_get_trending_categories(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper, YouTubeTrendingVideo
        s = YouTubeScraper()
        videos = [
            YouTubeTrendingVideo("1", "A", "C", category_name="Music"),
            YouTubeTrendingVideo("2", "B", "C", category_name="Music"),
            YouTubeTrendingVideo("3", "C", "C", category_name="Gaming"),
        ]
        cats = s.get_trending_categories(videos)
        assert cats[0] == "Music"

    def test_mock_trending_videos(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
        s = YouTubeScraper()
        videos = s._mock_trending_videos()
        assert isinstance(videos, list)
        assert len(videos) > 0

    def test_report_to_dict_structure(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeTrendReport
        r = YouTubeTrendReport(scraped_at="2025-01-01T00:00:00Z", region="US")
        d = r.to_dict()
        assert "trending_videos" in d
        assert "trending_music" in d
        assert d["region"] == "US"


# ── Trend analyzer tests ───────────────────────────────────────────────

class TestTrendAnalyzer:
    def _make_tt_report(self):
        from cli_anything.social_trends.core.tiktok_scraper import (
            TikTokTrendReport, TrendingHashtag, TrendingSound, TrendingVideo
        )
        return TikTokTrendReport(
            scraped_at="2025-01-01T00:00:00Z",
            region="US",
            trending_hashtags=[
                TrendingHashtag("fyp", view_count=40_000_000_000),
                TrendingHashtag("viral", view_count=30_000_000_000),
                TrendingHashtag("music", view_count=10_000_000_000),
            ],
            trending_sounds=[
                TrendingSound("Song A", "Artist X", video_count=5_000_000),
                TrendingSound("Song B", "Artist Y", video_count=3_000_000),
            ],
            trending_videos=[],
        )

    def _make_yt_report(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeTrendReport, YouTubeTrendingMusic
        return YouTubeTrendReport(
            scraped_at="2025-01-01T00:00:00Z",
            region="US",
            top_hashtags=["music", "trending", "viral"],
            trending_music=[
                YouTubeTrendingMusic("Song A", "Artist X", view_count=50_000_000),
            ],
        )

    def test_analyze_both_platforms(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(self._make_tt_report(), self._make_yt_report())
        assert len(analysis.top_trends) > 0
        assert analysis.analyzed_at != ""

    def test_cross_platform_boost(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(self._make_tt_report(), self._make_yt_report())
        cross = [t for t in analysis.top_trends if "viral" in t.keyword.lower() and len(t.platforms) > 1]
        if cross:
            assert cross[0].cross_platform_score > 0

    def test_analyze_tiktok_only(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(self._make_tt_report(), None)
        assert len(analysis.top_trends) > 0

    def test_analyze_youtube_only(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(None, self._make_yt_report())
        assert len(analysis.top_trends) > 0

    def test_best_hashtags_format(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(self._make_tt_report(), None)
        for ht in analysis.best_hashtags:
            assert ht.startswith("#")

    def test_to_dict_structure(self):
        from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer
        analysis = TrendAnalyzer().analyze(self._make_tt_report(), self._make_yt_report())
        d = analysis.to_dict()
        assert "top_trends" in d
        assert "best_hashtags" in d
        assert "posting_strategy" in d
        assert "content_ideas" in d


# ── Account optimizer tests ────────────────────────────────────────────

class TestAccountOptimizer:
    def _base_metrics(self, **overrides):
        from cli_anything.social_trends.core.account_optimizer import ProfileMetrics
        defaults = dict(
            handle="@testaccount",
            platform="tiktok",
            followers=5000,
            avg_views=1000,
            avg_likes=50,
            avg_comments=10,
            avg_shares=5,
            posting_frequency_per_week=5.0,
            niche="fitness",
            has_link_in_bio=True,
            bio="Fitness tips & transformations 💪 | Daily workouts | Link below ↓",
        )
        defaults.update(overrides)
        return ProfileMetrics(**defaults)

    def test_grade_high_score(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer
        metrics = self._base_metrics(
            followers=10000, avg_views=5000, avg_likes=500,
            avg_comments=50, avg_shares=25, posting_frequency_per_week=7.0,
            has_link_in_bio=True,
            bio="Daily fitness tips and transformations 💪 | Building champions | Results guaranteed | ↓ Free guide",
        )
        report = AccountOptimizer().analyze(metrics)
        assert report.grade in ("A+", "A", "B", "C")
        assert report.score >= 40

    def test_grade_low_score(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, ProfileMetrics
        metrics = ProfileMetrics(
            handle="@ghost",
            platform="tiktok",
            followers=100,
            posting_frequency_per_week=0.0,
            has_link_in_bio=False,
        )
        report = AccountOptimizer().analyze(metrics)
        assert len(report.critical_fixes) > 0

    def test_no_bio_is_critical(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, ProfileMetrics
        metrics = ProfileMetrics(handle="@x", platform="tiktok", bio="")
        report = AccountOptimizer().analyze(metrics)
        assert any("bio" in f.lower() for f in report.critical_fixes)

    def test_no_link_is_critical(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, ProfileMetrics
        metrics = ProfileMetrics(handle="@x", platform="tiktok", bio="my bio", has_link_in_bio=False)
        report = AccountOptimizer().analyze(metrics)
        assert any("link" in f.lower() for f in report.critical_fixes)

    def test_monetization_tiers(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer
        for followers, min_length in [(500, 1), (5000, 2), (50000, 3)]:
            metrics = self._base_metrics(followers=followers)
            report = AccountOptimizer().analyze(metrics)
            assert len(report.monetization_opportunities) >= min_length

    def test_report_to_dict(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer
        metrics = self._base_metrics()
        report = AccountOptimizer().analyze(metrics)
        d = report.to_dict()
        assert "grade" in d
        assert "score" in d
        assert "critical_fixes" in d

    def test_engagement_rate_calculation(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer
        metrics = self._base_metrics(
            avg_views=1000, avg_likes=60, avg_comments=10, avg_shares=5
        )
        report = AccountOptimizer().analyze(metrics)
        assert report.score > 0

    def test_posting_frequency_daily(self):
        from cli_anything.social_trends.core.account_optimizer import AccountOptimizer
        metrics = self._base_metrics(posting_frequency_per_week=7.0)
        report = AccountOptimizer().analyze(metrics)
        assert any("daily" in s.lower() or "daily" in s.lower() for s in report.content_strategy)


# ── Theme page guide tests ─────────────────────────────────────────────

class TestThemePageGuide:
    def test_generate_known_niche(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        guide = ThemePageGuide()
        plan = guide.generate_plan("finance")
        assert plan.niche == "finance"
        assert len(plan.phase_1_setup) > 0
        assert len(plan.phase_2_growth) > 0
        assert len(plan.phase_3_monetization) > 0

    def test_generate_custom_niche(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        guide = ThemePageGuide()
        plan = guide.generate_plan("gaming")
        assert plan.niche == "gaming"
        assert len(plan.phase_1_setup) > 0

    def test_dm_scripts_present(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        plan = ThemePageGuide().generate_plan("fitness")
        assert len(plan.dm_scripts) > 3

    def test_red_flags_present(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        plan = ThemePageGuide().generate_plan("luxury")
        assert len(plan.red_flags_to_avoid) > 5

    def test_list_niches(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        niches = ThemePageGuide().list_niches()
        assert len(niches) >= 5
        for n in niches:
            assert "key" in n and "name" in n and "monetization_potential" in n

    def test_valuation_with_followers(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        plan = ThemePageGuide().generate_plan("finance", current_followers=10000)
        assert "10,000" in plan.account_valuation

    def test_plan_to_dict(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        plan = ThemePageGuide().generate_plan("fitness")
        d = plan.to_dict()
        assert "phase_1_setup" in d
        assert "dm_scripts" in d
        assert "account_valuation" in d

    def test_content_calendar_days(self):
        from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
        plan = ThemePageGuide().generate_plan("motivation")
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        calendar_lower = " ".join(plan.content_calendar).lower()
        for day in days:
            assert day in calendar_lower


# ── Content generator tests ────────────────────────────────────────────

class TestContentGenerator:
    def test_generate_basic_plan(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="fitness", platform="tiktok", days=3, posts_per_day=2)
        assert plan.niche == "fitness"
        assert len(plan.posts) == 6  # 3 days * 2 posts/day

    def test_posts_have_required_fields(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="finance", platform="tiktok", days=1, posts_per_day=1)
        post = plan.posts[0]
        assert post.caption
        assert post.hashtags
        assert post.scheduled_time
        assert post.platform == "tiktok"
        assert post.content_type in ("hook", "value", "trend", "entertainment", "promo")

    def test_all_platform_generates_multiple(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="luxury", platform="all", days=1, posts_per_day=1)
        platforms = {p.platform for p in plan.posts}
        assert len(platforms) > 1

    def test_hashtag_stack_includes_niche(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="finance", platform="tiktok", days=1, posts_per_day=1)
        all_hashtags = " ".join(plan.posts[0].hashtags).lower()
        assert "finance" in all_hashtags or "fyp" in all_hashtags

    def test_youtube_hashtag_includes_shorts(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="fitness", platform="youtube", days=1, posts_per_day=1)
        all_hashtags = " ".join(plan.posts[0].hashtags)
        assert "Shorts" in all_hashtags or "shorts" in all_hashtags.lower()

    def test_trending_hashtags_injected(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(
            niche="fitness", platform="tiktok", days=1, posts_per_day=1,
            trending_hashtags=["supertrendinghashtag123"]
        )
        all_hashtags = " ".join(plan.posts[0].hashtags).lower()
        assert "supertrendinghashtag123" in all_hashtags

    def test_repurpose_strategy_present(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        plan = ContentGenerator().generate_plan("luxury", days=1, posts_per_day=1)
        assert len(plan.repurpose_strategy) > 3

    def test_post_formatted_output(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="cars", platform="tiktok", days=1, posts_per_day=1)
        formatted = plan.posts[0].formatted()
        assert "Post #1" in formatted
        assert "CAPTION" in formatted
        assert "HASHTAGS" in formatted

    def test_post_to_dict(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        gen = ContentGenerator()
        plan = gen.generate_plan(niche="food", platform="instagram", days=1, posts_per_day=1)
        d = plan.posts[0].to_dict()
        assert "caption" in d
        assert "hashtags" in d
        assert "scheduled_time" in d

    def test_plan_to_dict(self):
        from cli_anything.social_trends.core.content_generator import ContentGenerator
        plan = ContentGenerator().generate_plan("motivation", days=2, posts_per_day=1)
        d = plan.to_dict()
        assert "posts" in d
        assert "repurpose_strategy" in d
        assert "weekly_tips" in d


# ── Helpers tests ──────────────────────────────────────────────────────

class TestHelpers:
    def test_format_number(self):
        from cli_anything.social_trends.utils.helpers import format_number
        assert format_number(1_000_000) == "1.0M"
        assert format_number(1_500_000) == "1.5M"
        assert format_number(45_000) == "45.0K"
        assert format_number(500) == "500"
        assert format_number(2_000_000_000) == "2.0B"

    def test_timestamp_filename(self):
        from cli_anything.social_trends.utils.helpers import timestamp_filename
        name = timestamp_filename("report")
        assert name.startswith("report_")
        assert name.endswith(".json")
        assert len(name) > 15

    def test_timestamp_filename_custom_ext(self):
        from cli_anything.social_trends.utils.helpers import timestamp_filename
        name = timestamp_filename("export", ext="csv")
        assert name.endswith(".csv")

    def test_load_env_missing_file(self):
        from cli_anything.social_trends.utils.helpers import load_env
        env = load_env("/nonexistent/path/.env")
        assert env == {}
