"""Unit tests for social-media CLI core modules."""

import pytest
from cli_anything.social_media.core import account_optimizer, theme_pages
from cli_anything.social_media.core.youtube_trends import (
    extract_trending_hashtags,
    fetch_trending_music_from_videos,
    _parse_view_count,
)
from cli_anything.social_media.core.tiktok_trends import (
    extract_niche_hashtags,
    _parse_video,
    _parse_sound,
)


# ─── YouTube ────────────────────────────────────────────────────────────────

class TestParseViewCount:
    def test_plain_number(self):
        assert _parse_view_count("1234567") == 1234567

    def test_k_suffix(self):
        assert _parse_view_count("234K") == 234_000

    def test_m_suffix(self):
        assert _parse_view_count("1.5M") == 1_500_000

    def test_b_suffix(self):
        assert _parse_view_count("2B") == 2_000_000_000

    def test_with_views_text(self):
        assert _parse_view_count("5.2M views") == 5_200_000

    def test_empty(self):
        assert _parse_view_count("") == 0

    def test_invalid(self):
        assert _parse_view_count("no views") == 0


class TestExtractTrendingHashtags:
    def test_extracts_from_tags(self):
        videos = [
            {"title": "Test", "tags": ["fitness", "workout", "gym"]},
            {"title": "Test2", "tags": ["fitness", "nutrition"]},
        ]
        result = extract_trending_hashtags(videos, top_n=10)
        assert result[0]["hashtag"] == "#fitness"
        assert result[0]["count"] == 2

    def test_extracts_from_title_hashtags(self):
        videos = [{"title": "Great #workout tips #fitness", "tags": []}]
        result = extract_trending_hashtags(videos)
        tags = {r["hashtag"] for r in result}
        assert "#workout" in tags or "#fitness" in tags

    def test_empty_videos(self):
        assert extract_trending_hashtags([]) == []


class TestFetchTrendingMusic:
    def test_extracts_music_videos(self):
        videos = [
            {"title": "Taylor Swift - Shake It Off (Official Music Video)", "channel": "Taylor Swift", "views": 1_000_000, "url": "https://yt.com/1"},
            {"title": "How to cook pasta", "channel": "Chef John", "views": 50_000, "url": "https://yt.com/2"},
        ]
        music = fetch_trending_music_from_videos(videos)
        assert len(music) == 1
        assert music[0]["artist"] == "Taylor Swift"

    def test_official_keyword(self):
        videos = [{"title": "Official Lyric Video", "channel": "Artist", "views": 500_000, "url": "x"}]
        music = fetch_trending_music_from_videos(videos)
        assert len(music) == 1


# ─── TikTok ──────────────────────────────────────────────────────────────────

class TestParseTikTokVideo:
    def test_parses_basic_fields(self):
        item = {
            "id": "123456",
            "desc": "Check this out #fitness #gym workout tips",
            "author": {"uniqueId": "creator123", "nickname": "Creator Name"},
            "stats": {
                "playCount": 500_000,
                "diggCount": 25_000,
                "shareCount": 1_200,
                "commentCount": 890,
            },
            "music": {"title": "Trending Song", "authorName": "DJ X", "id": "m123"},
        }
        result = _parse_video(item)
        assert result["id"] == "123456"
        assert result["author"] == "creator123"
        assert result["play_count"] == 500_000
        assert "fitness" in result["hashtags"]
        assert "gym" in result["hashtags"]
        assert result["music_title"] == "Trending Song"

    def test_extracts_hashtags_from_description(self):
        item = {
            "id": "1",
            "desc": "#viral #fyp #trending new dance challenge",
            "author": {}, "stats": {}, "music": {},
        }
        result = _parse_video(item)
        assert "viral" in result["hashtags"]
        assert "fyp" in result["hashtags"]
        assert "trending" in result["hashtags"]


class TestExtractNicheHashtags:
    def test_counts_hashtag_frequency(self):
        videos = [
            {"hashtags": ["fitness", "gym", "workout"]},
            {"hashtags": ["fitness", "nutrition"]},
            {"hashtags": ["gym", "fitness"]},
        ]
        result = extract_niche_hashtags(videos)
        top = result[0]
        assert top["hashtag"] == "#fitness"
        assert top["frequency"] == 3

    def test_handles_empty(self):
        assert extract_niche_hashtags([]) == []


# ─── Account Optimizer ───────────────────────────────────────────────────────

class TestAccountOptimizer:
    def _make_profile(self, **kwargs):
        base = {
            "handle": "@testaccount",
            "platform": "tiktok",
            "bio": "Daily fitness content | Free workout plan in bio 💪",
            "follower_count": 10_000,
            "following_count": 500,
            "avg_views": 15_000,
            "avg_likes": 800,
            "avg_comments": 60,
            "posting_frequency_per_week": 7,
            "niche": "fitness",
            "last_posts": [],
        }
        base.update(kwargs)
        return base

    def test_returns_score(self):
        result = account_optimizer.analyze_account(self._make_profile())
        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_returns_grade(self):
        result = account_optimizer.analyze_account(self._make_profile())
        assert result["grade"] in ["A+", "A", "B+", "B", "C+", "C", "D"]

    def test_low_engagement_flagged(self):
        result = account_optimizer.analyze_account(
            self._make_profile(avg_likes=10, avg_comments=1)
        )
        all_recs = " ".join(result["recommendations"]).lower()
        assert "engagement" in all_recs or "hook" in all_recs or "cta" in all_recs

    def test_no_bio_flagged(self):
        result = account_optimizer.analyze_account(self._make_profile(bio=""))
        all_recs = " ".join(result["recommendations"]).lower()
        assert "bio" in all_recs

    def test_low_posting_freq_flagged(self):
        result = account_optimizer.analyze_account(
            self._make_profile(posting_frequency_per_week=0.5)
        )
        all_recs = " ".join(result["recommendations"]).lower()
        assert "post" in all_recs

    def test_posting_times_returned(self):
        result = account_optimizer.analyze_account(self._make_profile())
        assert len(result["best_posting_times_utc"]) > 0
        assert "UTC" in result["best_posting_times_utc"][0]

    def test_growth_hacks_returned(self):
        result = account_optimizer.analyze_account(self._make_profile())
        assert len(result["growth_hacks"]) > 0

    def test_engagement_rate_calc(self):
        result = account_optimizer.analyze_account(
            self._make_profile(follower_count=10000, avg_likes=500, avg_comments=50)
        )
        assert result["engagement_rate"] == pytest.approx(5.5)

    def test_zero_followers(self):
        result = account_optimizer.analyze_account(self._make_profile(follower_count=0))
        assert result["score"] >= 0

    def test_batch_analyze_sorted(self):
        profiles = [
            self._make_profile(handle="@a", avg_likes=10),
            self._make_profile(handle="@b", avg_likes=5000),
        ]
        results = account_optimizer.batch_analyze_accounts(profiles)
        assert results[0]["score"] >= results[1]["score"]

    def test_score_grade_mapping(self):
        assert account_optimizer._score_to_grade(95) == "A+"
        assert account_optimizer._score_to_grade(80) == "A"
        assert account_optimizer._score_to_grade(70) == "B+"
        assert account_optimizer._score_to_grade(30) == "D"


# ─── Theme Pages ─────────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches(self):
        niches = theme_pages.list_all_niches()
        assert len(niches) >= 8
        assert all("niche" in n for n in niches)
        assert all("monetization" in n for n in niches)

    def test_get_niche_analysis_valid(self):
        result = theme_pages.get_niche_analysis("luxury_lifestyle")
        assert result["niche"] == "luxury_lifestyle"
        assert "90_day_roadmap" in result
        assert "content_calendar" in result
        assert len(result["90_day_roadmap"]) >= 5

    def test_get_niche_analysis_invalid(self):
        result = theme_pages.get_niche_analysis("nonexistent_niche_xyz")
        assert "error" in result
        assert "available_niches" in result

    def test_get_niche_fuzzy_match(self):
        result = theme_pages.get_niche_analysis("fitness")
        assert "error" not in result

    def test_get_platform_strategy_tiktok(self):
        result = theme_pages.get_platform_strategy("tiktok")
        assert result["platform"] == "tiktok"
        assert "growth_strategy" in result
        assert "monetization_milestones" in result
        assert len(result["content_repurposing_workflow"]) >= 5

    def test_get_platform_strategy_invalid(self):
        result = theme_pages.get_platform_strategy("myspace")
        assert "error" in result

    def test_conversion_optimization_sales(self):
        result = theme_pages.get_conversion_optimization("tiktok", goal="sales")
        assert len(result["conversion_tactics"]) >= 4
        assert "funnel_stages" in result

    def test_conversion_optimization_with_rate(self):
        result = theme_pages.get_conversion_optimization(
            "tiktok", current_conversion_rate=0.3, goal="sales"
        )
        assert "diagnosis" in result
        assert "low" in result["diagnosis"].lower()

    def test_conversion_optimization_good_rate(self):
        result = theme_pages.get_conversion_optimization(
            "tiktok", current_conversion_rate=7.5, goal="follows"
        )
        assert "Good" in result.get("diagnosis", "")

    def test_content_calendar_has_all_days(self):
        result = theme_pages.get_niche_analysis("pets")
        calendar = result["content_calendar"]
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            assert day in calendar
