"""Unit tests for social-trends core modules — no external API calls."""

import json
import pytest
from datetime import datetime

from cli_anything.social_trends.core import youtube_trends as yt
from cli_anything.social_trends.core import tiktok_trends as tt
from cli_anything.social_trends.core import account_optimizer as opt
from cli_anything.social_trends.core import theme_pages as theme
from cli_anything.social_trends.core import session as sess


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_yt_videos():
    return [
        {
            "id": "abc123",
            "title": "Top 10 #fitness tips #workout",
            "channel": "FitLife",
            "published_at": "2024-01-01T12:00:00Z",
            "category_id": "26",
            "category": "Howto & Style",
            "view_count": 1_000_000,
            "like_count": 50_000,
            "comment_count": 2_000,
            "duration_seconds": 480,
            "hashtags": ["fitness", "workout"],
            "thumbnail": "https://example.com/thumb.jpg",
            "url": "https://www.youtube.com/watch?v=abc123",
            "tags": ["#fitness", "health"],
            "description_snippet": "Top fitness tips",
        },
        {
            "id": "def456",
            "title": "Easy Cooking #food #recipe",
            "channel": "CookMaster",
            "published_at": "2024-01-02T10:00:00Z",
            "category_id": "26",
            "category": "Howto & Style",
            "view_count": 500_000,
            "like_count": 25_000,
            "comment_count": 800,
            "duration_seconds": 720,
            "hashtags": ["food", "recipe"],
            "thumbnail": "https://example.com/thumb2.jpg",
            "url": "https://www.youtube.com/watch?v=def456",
            "tags": ["#food", "cooking"],
            "description_snippet": "Easy recipes",
        },
        {
            "id": "ghi789",
            "title": "#gaming highlights",
            "channel": "GamerPro",
            "published_at": "2024-01-03T08:00:00Z",
            "category_id": "20",
            "category": "Gaming",
            "view_count": 2_000_000,
            "like_count": 100_000,
            "comment_count": 5_000,
            "duration_seconds": 900,
            "hashtags": ["gaming"],
            "thumbnail": "https://example.com/thumb3.jpg",
            "url": "https://www.youtube.com/watch?v=ghi789",
            "tags": [],
            "description_snippet": "Gaming highlights",
        },
    ]


@pytest.fixture
def sample_tt_videos():
    return [
        {
            "id": "tt1",
            "username": "creator1",
            "description": "This is a fitness tip #fitness #workout #gym",
            "hashtags": ["#fitness", "#workout", "#gym"],
            "music_id": "sound1",
            "music_title": "Trending Song 1",
            "music_author": "Artist 1",
            "music_original": False,
            "duration_seconds": 30,
            "view_count": 500_000,
            "like_count": 25_000,
            "comment_count": 1_000,
            "share_count": 500,
            "engagement_rate_pct": 5.3,
            "created_at": "2024-01-01T14:00:00",
            "url": "https://www.tiktok.com/@creator1/video/tt1",
            "source": "web_scrape",
        },
        {
            "id": "tt2",
            "username": "creator2",
            "description": "Food recipe #food #cooking #recipe",
            "hashtags": ["#food", "#cooking", "#recipe"],
            "music_id": "sound2",
            "music_title": "Trending Song 2",
            "music_author": "Artist 2",
            "music_original": True,
            "duration_seconds": 15,
            "view_count": 2_000_000,
            "like_count": 200_000,
            "comment_count": 5_000,
            "share_count": 10_000,
            "engagement_rate_pct": 10.75,
            "created_at": "2024-01-02T20:00:00",
            "url": "https://www.tiktok.com/@creator2/video/tt2",
            "source": "web_scrape",
        },
        {
            "id": "tt3",
            "username": "creator3",
            "description": "Dance challenge #dance #viral #trending",
            "hashtags": ["#dance", "#viral", "#trending"],
            "music_id": "sound1",
            "music_title": "Trending Song 1",
            "music_author": "Artist 1",
            "music_original": False,
            "duration_seconds": 20,
            "view_count": 10_000_000,
            "like_count": 800_000,
            "comment_count": 20_000,
            "share_count": 50_000,
            "engagement_rate_pct": 8.7,
            "created_at": "2024-01-03T18:00:00",
            "url": "https://www.tiktok.com/@creator3/video/tt3",
            "source": "web_scrape",
        },
    ]


@pytest.fixture
def sample_account():
    return {
        "platform": "tiktok",
        "username": "testcreator",
        "follower_count": 15_000,
        "avg_views": 5_000,
        "avg_likes": 500,
        "avg_comments": 50,
        "posting_frequency_per_week": 5,
        "niche": "fitness",
        "bio": "Fitness tips daily | Follow for workouts",
    }


# ---------------------------------------------------------------------------
# YouTube trends tests
# ---------------------------------------------------------------------------

class TestYouTubeTrends:
    def test_parse_duration_seconds(self):
        assert yt._parse_duration("PT30S") == 30

    def test_parse_duration_minutes(self):
        assert yt._parse_duration("PT5M30S") == 330

    def test_parse_duration_hours(self):
        assert yt._parse_duration("PT1H2M3S") == 3723

    def test_parse_duration_empty(self):
        assert yt._parse_duration("PT0S") == 0

    def test_parse_duration_invalid(self):
        assert yt._parse_duration("") == 0

    def test_engagement_rate_calculation(self, sample_yt_videos):
        rate = yt.get_video_engagement_rate(sample_yt_videos[0])
        assert rate > 0
        expected = (50_000 + 2_000) / 1_000_000 * 100
        assert abs(rate - expected) < 0.01

    def test_engagement_rate_zero_views(self):
        rate = yt.get_video_engagement_rate({"view_count": 0, "like_count": 100, "comment_count": 10})
        assert rate == 0.0

    def test_extract_trending_hashtags(self, sample_yt_videos):
        hashtags = yt.extract_trending_hashtags(sample_yt_videos, top_n=10)
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0
        for h in hashtags:
            assert "hashtag" in h
            assert h["hashtag"].startswith("#")
            assert "video_count" in h
            assert "total_views" in h

    def test_extract_hashtags_deduplication(self, sample_yt_videos):
        hashtags = yt.extract_trending_hashtags(sample_yt_videos, top_n=5)
        tags = [h["hashtag"] for h in hashtags]
        assert len(tags) == len(set(tags))

    def test_analyze_trending_patterns_empty(self):
        result = yt.analyze_trending_patterns([])
        assert result == {}

    def test_analyze_trending_patterns(self, sample_yt_videos):
        result = yt.analyze_trending_patterns(sample_yt_videos)
        assert "total_videos_analyzed" in result
        assert result["total_videos_analyzed"] == 3
        assert "avg_views" in result
        assert "avg_engagement_rate_pct" in result
        assert "duration_breakdown" in result
        assert "top_tags" in result
        assert "best_duration_range" in result

    def test_analyze_patterns_calculates_avg_views(self, sample_yt_videos):
        result = yt.analyze_trending_patterns(sample_yt_videos)
        expected_avg = (1_000_000 + 500_000 + 2_000_000) // 3
        assert abs(result["avg_views"] - expected_avg) <= 1

    def test_region_codes_exist(self):
        assert "US" in yt.REGION_CODES
        assert "GB" in yt.REGION_CODES
        assert "IN" in yt.REGION_CODES

    def test_category_ids_exist(self):
        assert "10" in yt.CATEGORY_IDS
        assert yt.CATEGORY_IDS["10"] == "Music"
        assert "20" in yt.CATEGORY_IDS


# ---------------------------------------------------------------------------
# TikTok trends tests
# ---------------------------------------------------------------------------

class TestTikTokTrends:
    def test_normalize_web_video_structure(self):
        raw_item = {
            "id": "123",
            "desc": "Test video #viral",
            "challenges": [{"hashtagName": "viral"}],
            "stats": {"playCount": 1000, "diggCount": 100, "commentCount": 20, "shareCount": 5},
            "author": {"uniqueId": "testuser", "nickname": "Test User"},
            "music": {"id": "m1", "title": "Song", "authorName": "Artist", "original": False},
            "video": {"duration": 30},
            "createTime": 1704067200,
        }
        result = tt._normalize_web_video(raw_item)
        assert result["id"] == "123"
        assert result["username"] == "testuser"
        assert "#viral" in result["hashtags"]
        assert result["view_count"] == 1000
        assert result["like_count"] == 100
        assert result["engagement_rate_pct"] > 0
        assert "tiktok.com" in result["url"]

    def test_engagement_rate_calculation(self):
        raw_item = {
            "id": "1",
            "desc": "",
            "challenges": [],
            "stats": {"playCount": 1000, "diggCount": 100, "commentCount": 10, "shareCount": 5},
            "author": {"uniqueId": "u", "nickname": "U"},
            "music": {},
            "video": {},
            "createTime": 0,
        }
        result = tt._normalize_web_video(raw_item)
        expected = (100 + 10 + 5) / 1000 * 100
        assert abs(result["engagement_rate_pct"] - expected) < 0.01

    def test_extract_trending_hashtags(self, sample_tt_videos):
        hashtags = tt.extract_trending_hashtags(sample_tt_videos, top_n=10)
        assert isinstance(hashtags, list)
        assert len(hashtags) > 0
        for h in hashtags:
            assert "hashtag" in h
            assert h["hashtag"].startswith("#")
            assert "trend_score" in h

    def test_extract_trending_hashtags_ranking(self, sample_tt_videos):
        hashtags = tt.extract_trending_hashtags(sample_tt_videos, top_n=10)
        # Should be sorted by some score
        assert len(hashtags) > 0

    def test_extract_trending_sounds(self, sample_tt_videos):
        sounds = tt.extract_trending_sounds(sample_tt_videos, top_n=10)
        assert isinstance(sounds, list)
        assert len(sounds) > 0
        assert sounds[0]["music_id"] == "sound1"  # sound1 appears twice
        assert sounds[0]["usage_count"] == 2
        for s in sounds:
            assert "music_id" in s
            assert "usage_count" in s
            assert "total_views" in s

    def test_extract_sounds_sorted_by_usage(self, sample_tt_videos):
        sounds = tt.extract_trending_sounds(sample_tt_videos, top_n=5)
        counts = [s["usage_count"] for s in sounds]
        assert counts == sorted(counts, reverse=True)

    def test_analyze_tiktok_patterns_empty(self):
        result = tt.analyze_tiktok_patterns([])
        assert result == {}

    def test_analyze_tiktok_patterns(self, sample_tt_videos):
        result = tt.analyze_tiktok_patterns(sample_tt_videos)
        assert "total_videos_analyzed" in result
        assert result["total_videos_analyzed"] == 3
        assert "avg_views" in result
        assert "avg_engagement_rate_pct" in result
        assert "duration_breakdown" in result
        assert "best_duration" in result
        assert "top_hashtags" in result
        assert "top_sounds" in result

    def test_duration_breakdown_correct(self, sample_tt_videos):
        result = tt.analyze_tiktok_patterns(sample_tt_videos)
        breakdown = result["duration_breakdown"]
        # durations: 30, 15, 20 — all under 30s
        assert breakdown["under_15s"] == 1   # 15s
        assert breakdown["15_30s"] == 2      # 30s, 20s

    def test_normalize_research_video(self):
        raw = {
            "id": 999,
            "username": "researchuser",
            "video_description": "Research video #trending",
            "hashtag_names": ["trending", "viral"],
            "music_id": 42,
            "view_count": "50000",
            "like_count": "5000",
            "comment_count": "200",
            "share_count": "100",
            "region_code": "US",
            "create_time": 1704067200,
        }
        result = tt._normalize_research_video(raw)
        assert result["username"] == "researchuser"
        assert "#trending" in result["hashtags"]
        assert "#viral" in result["hashtags"]
        assert result["view_count"] == 50_000
        assert result["source"] == "research_api"


# ---------------------------------------------------------------------------
# Account optimizer tests
# ---------------------------------------------------------------------------

class TestAccountOptimizer:
    def test_generate_posting_schedule_returns_list(self):
        schedule = opt.generate_posting_schedule("tiktok", posts_per_week=5)
        assert isinstance(schedule, list)
        assert len(schedule) == 5

    def test_posting_schedule_structure(self):
        schedule = opt.generate_posting_schedule("tiktok", posts_per_week=7)
        for slot in schedule:
            assert "date" in slot
            assert "day" in slot
            assert "hour_utc" in slot
            assert "platform" in slot
            assert "slot_quality" in slot

    def test_posting_schedule_respects_platform(self):
        yt_sched = opt.generate_posting_schedule("youtube", posts_per_week=5)
        tt_sched = opt.generate_posting_schedule("tiktok", posts_per_week=5)
        # Both should be valid lists
        assert len(yt_sched) == 5
        assert len(tt_sched) == 5

    def test_unknown_platform_defaults(self):
        schedule = opt.generate_posting_schedule("mastodon", posts_per_week=3)
        assert len(schedule) == 3

    def test_utc_to_tz_conversion(self):
        result = opt._utc_to_tz(0, "EST")
        assert "EST" in result
        assert "PM" in result or "AM" in result

    def test_build_hashtag_strategy_structure(self):
        strategy = opt.build_hashtag_strategy("fitness", platform="tiktok")
        assert "niche" in strategy
        assert "recommended_combo" in strategy
        assert "tiers" in strategy
        assert "pro_tips" in strategy
        assert isinstance(strategy["recommended_combo"], list)

    def test_build_hashtag_strategy_respects_limits(self):
        strategy = opt.build_hashtag_strategy("fitness", platform="tiktok")
        limit = strategy["platform_limit"]
        assert len(strategy["recommended_combo"]) <= limit

    def test_build_hashtag_strategy_blends_trending(self):
        trending = [{"hashtag": "#newtrend"}, {"hashtag": "#viral2024"}]
        strategy = opt.build_hashtag_strategy("fitness", platform="tiktok", trending_hashtags=trending)
        all_tags = (
            strategy["tiers"]["mega"]["tags"]
            + strategy["tiers"]["large"]["tags"]
            + strategy["tiers"]["medium"]["tags"]
            + strategy["tiers"]["small"]["tags"]
            + strategy["tiers"]["micro"]["tags"]
        )
        # At least some trending tags should be blended in
        assert len(all_tags) > 0

    def test_generate_content_calendar_structure(self):
        calendar = opt.generate_content_calendar("fitness", platform="tiktok", weeks=2, posts_per_week=7)
        assert len(calendar) == 14
        for post in calendar:
            assert "date" in post
            assert "content_type" in post
            assert "hook" in post
            assert "cta" in post
            assert "status" in post

    def test_content_calendar_post_numbering(self):
        calendar = opt.generate_content_calendar("food", platform="instagram", weeks=1, posts_per_week=5)
        numbers = [p["post_number"] for p in calendar]
        assert numbers == list(range(1, 6))

    def test_audit_account_structure(self, sample_account):
        result = opt.audit_account(sample_account)
        assert "engagement_rate_pct" in result
        assert "engagement_grade" in result
        assert "recommendations" in result
        assert "score" in result
        assert isinstance(result["recommendations"], list)

    def test_audit_high_engagement_grade(self):
        data = {
            "platform": "tiktok",
            "username": "superstar",
            "follower_count": 100_000,
            "avg_views": 500_000,
            "avg_likes": 100_000,
            "avg_comments": 5_000,
            "posting_frequency_per_week": 7,
            "niche": "fitness",
            "bio": "Elite fitness creator helping you transform your body in 90 days",
        }
        result = opt.audit_account(data)
        assert result["engagement_grade"] in ("good", "viral")

    def test_audit_low_posting_frequency_recommendation(self):
        data = {
            "platform": "tiktok",
            "username": "lazy",
            "follower_count": 1_000,
            "avg_views": 200,
            "avg_likes": 10,
            "avg_comments": 2,
            "posting_frequency_per_week": 1,
            "niche": "lifestyle",
            "bio": "Just a creator",
        }
        result = opt.audit_account(data)
        rec_categories = [r["category"] for r in result["recommendations"]]
        assert "consistency" in rec_categories

    def test_audit_score_grade_boundaries(self):
        data = {
            "platform": "tiktok",
            "username": "avg",
            "follower_count": 50_000,
            "avg_views": 10_000,
            "avg_likes": 500,
            "avg_comments": 50,
            "posting_frequency_per_week": 7,
            "niche": "fitness",
            "bio": "A solid bio that has more than fifty characters total right here",
        }
        result = opt.audit_account(data)
        score = result["score"]
        assert score["grade"] in ("A", "B", "C", "D", "F")
        assert 0 <= score["total"] <= 100

    def test_optimize_bio_returns_templates(self):
        result = opt.optimize_bio("fitness", "tiktok")
        assert "templates" in result
        assert "tips" in result
        assert isinstance(result["templates"], list)
        assert len(result["templates"]) > 0

    def test_platform_best_times_coverage(self):
        for platform in ["tiktok", "youtube", "instagram", "twitter", "facebook"]:
            assert platform in opt.PLATFORM_BEST_TIMES

    def test_niche_hashtag_sets_coverage(self):
        for niche in ["fitness", "food", "fashion", "finance", "beauty", "travel"]:
            assert niche in opt.NICHE_HASHTAG_SETS
            assert len(opt.NICHE_HASHTAG_SETS[niche]) >= 10


# ---------------------------------------------------------------------------
# Theme pages tests
# ---------------------------------------------------------------------------

class TestThemePages:
    def test_score_niche_structure(self):
        result = theme.score_niche("finance")
        assert "total_score" in result
        assert "grade" in result
        assert "breakdown" in result
        assert result["grade"] in ("A", "B", "C", "D")

    def test_score_niche_unknown(self):
        result = theme.score_niche("unknownniche999")
        assert "error" in result

    def test_score_all_niches(self):
        for key in theme.NICHES:
            result = theme.score_niche(key)
            assert "total_score" in result
            assert result["total_score"] > 0
            assert result["total_score"] <= 100

    def test_get_niche_starter_kit_structure(self):
        result = theme.get_niche_starter_kit("finance")
        assert "sub_niches" in result
        assert "content_types" in result
        assert "monetization_methods" in result
        assert "seed_keywords" in result

    def test_get_niche_starter_kit_unknown(self):
        result = theme.get_niche_starter_kit("fakenichwzz")
        assert "error" in result

    def test_get_playbook_all_phases(self):
        playbook = theme.get_playbook()
        assert isinstance(playbook, list)
        assert len(playbook) == 6
        phases = [p["phase"] for p in playbook]
        assert phases == [1, 2, 3, 4, 5, 6]

    def test_get_playbook_specific_phase(self):
        phase = theme.get_playbook(1)
        assert isinstance(phase, dict)
        assert phase["phase"] == 1
        assert "steps" in phase
        assert "deliverable" in phase

    def test_get_playbook_invalid_phase(self):
        result = theme.get_playbook(99)
        assert "error" in result

    def test_estimate_revenue_structure(self):
        result = theme.estimate_revenue(50_000, "tiktok", 10_000, "fitness")
        assert "monthly_estimates_usd" in result
        assert "total" in result["monthly_estimates_usd"]
        assert "brand_deals" in result["monthly_estimates_usd"]

    def test_estimate_revenue_increases_with_followers(self):
        low = theme.estimate_revenue(1_000, "tiktok", 500, "finance")
        high = theme.estimate_revenue(500_000, "tiktok", 100_000, "finance")
        assert high["monthly_estimates_usd"]["brand_deals"] > low["monthly_estimates_usd"]["brand_deals"]

    def test_compare_niches_sorted_by_score(self):
        results = theme.compare_niches(["finance", "pets", "fitness"])
        assert len(results) == 3
        scores = [r["total_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_compare_niches_ignores_unknowns(self):
        results = theme.compare_niches(["finance", "fakenichwzz"])
        assert len(results) == 1
        assert results[0]["niche"] == "finance"

    def test_conversion_strategies_exist(self):
        for key in ["follow_to_engagement", "engagement_to_leads", "leads_to_customers", "page_to_brand_deals"]:
            assert key in theme.CONVERSION_STRATEGIES
            strategy = theme.CONVERSION_STRATEGIES[key]
            assert "name" in strategy
            assert "tactics" in strategy
            assert "kpis" in strategy

    def test_niche_data_completeness(self):
        required_fields = ["display", "saturation", "cpm_usd", "affiliate_potential",
                           "brand_deal_avg_usd", "audience_purchase_intent", "content_types",
                           "monetization", "keywords", "sub_niches"]
        for niche_key, niche_data in theme.NICHES.items():
            for field in required_fields:
                assert field in niche_data, f"Niche '{niche_key}' missing field '{field}'"


# ---------------------------------------------------------------------------
# Session tests
# ---------------------------------------------------------------------------

class TestSession:
    def test_new_session_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        assert "accounts" in s
        assert "api_keys" in s
        assert "history" in s

    def test_save_and_load_session(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        s["test_key"] = "test_value"
        sess.save_session(s)
        s2 = sess.load_session()
        assert s2["test_key"] == "test_value"

    def test_add_and_get_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        sess.add_account(s, "tiktok", "myuser", {"niche": "fitness"})
        accounts = sess.get_accounts(s, "tiktok")
        assert "myuser" in accounts

    def test_cache_set_and_get(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        data = {"key": "value", "number": 42}
        sess.cache_set("test_cache", data, ttl_seconds=3600)
        result = sess.cache_get("test_cache")
        assert result == data

    def test_cache_miss_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        result = sess.cache_get("nonexistent_cache_key_xyz")
        assert result is None

    def test_cache_expired_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        sess.cache_set("expired_key", {"data": "old"}, ttl_seconds=-1)
        result = sess.cache_get("expired_key")
        assert result is None

    def test_cache_clear_all(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        sess.cache_set("key1", "val1")
        sess.cache_set("key2", "val2")
        count = sess.cache_clear()
        assert count == 2

    def test_get_api_key_from_env(self, monkeypatch, tmp_path):
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_key_from_env")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        key = sess.get_api_key(s, "YOUTUBE_API_KEY")
        assert key == "test_key_from_env"

    def test_log_history_appends(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        sess.log_history(s, "yt trends", "50 videos")
        assert len(s["history"]) == 1
        assert s["history"][0]["command"] == "yt trends"

    def test_log_history_capped_at_100(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
        monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
        s = sess.load_session()
        for i in range(150):
            sess.log_history(s, f"command {i}", "result")
        assert len(s["history"]) == 100
