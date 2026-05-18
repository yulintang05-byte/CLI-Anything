"""Unit tests for social-trends core modules (no network required)."""

import pytest
from datetime import date

from cli_anything.social_trends.core import tiktok_scraper as tt
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import account_optimizer as acct
from cli_anything.social_trends.core import theme_page as theme_mod
from cli_anything.social_trends.core.session import Session


# ── tiktok_scraper mock data ──────────────────────────────────────────

class TestTikTokMockData:
    def test_mock_hashtags_returns_list(self):
        data = tt._mock_trending_hashtags(10)
        assert isinstance(data, list)
        assert len(data) == 10

    def test_mock_hashtags_schema(self):
        data = tt._mock_trending_hashtags(1)
        item = data[0]
        assert "hashtag" in item
        assert item["hashtag"].startswith("#")
        assert "view_count" in item
        assert "video_count" in item

    def test_mock_music_returns_list(self):
        data = tt._mock_trending_music(5)
        assert isinstance(data, list)
        assert len(data) == 5

    def test_mock_music_schema(self):
        item = tt._mock_trending_music(1)[0]
        assert "title" in item
        assert "author" in item
        assert "use_count" in item
        assert isinstance(item["is_original"], bool)

    def test_parse_video_item_handles_empty(self):
        result = tt._parse_video_item({})
        assert "id" in result
        assert "hashtags" in result
        assert isinstance(result["hashtags"], list)

    def test_safe_int(self):
        assert tt._safe_int(123) == 123
        assert tt._safe_int("456") == 456
        assert tt._safe_int(None) is None
        assert tt._safe_int("abc") is None


# ── trends module ─────────────────────────────────────────────────────

class TestTrends:
    def test_niche_keywords_populated(self):
        assert "fitness" in trends_mod.NICHE_KEYWORDS
        assert len(trends_mod.NICHE_KEYWORDS["fitness"]) > 3

    def test_get_hashtag_suggestions_tiktok(self):
        tags = trends_mod.get_hashtag_suggestions("fitness", "tiktok", 20)
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert all(isinstance(t, str) for t in tags)
        # Should contain at least one broad tag
        assert any("fyp" in t or "viral" in t or "tiktok" in t for t in tags)

    def test_get_hashtag_suggestions_youtube(self):
        tags = trends_mod.get_hashtag_suggestions("beauty", "youtube", 15)
        assert len(tags) > 0
        assert any("shorts" in t.lower() or "youtube" in t.lower() for t in tags)

    def test_get_hashtag_suggestions_dedup(self):
        tags = trends_mod.get_hashtag_suggestions("gaming", "both", 30)
        lower = [t.lower() for t in tags]
        assert len(lower) == len(set(lower)), "Duplicates found in hashtags"

    def test_hashtag_prefix(self):
        tags = trends_mod.get_hashtag_suggestions("food", "both", 10)
        for t in tags:
            assert t.startswith("#"), f"Tag missing #: {t}"

    def test_analyze_trend_velocity_empty(self):
        result = trends_mod.analyze_trend_velocity([])
        assert "hot_trends" in result
        assert "rising_trends" in result
        assert "fading_trends" in result
        assert all(isinstance(v, list) for v in result.values())

    def test_analyze_trend_velocity_categorizes(self):
        videos = [
            {"title": "Fresh hot", "views": 500_000, "upload_date": "20260515"},
            {"title": "Rising", "views": 200_000, "upload_date": "20260512"},
            {"title": "Old", "views": 50_000, "upload_date": "20260401"},
        ]
        result = trends_mod.analyze_trend_velocity(videos)
        all_videos = (
            result["hot_trends"] + result["rising_trends"] + result["fading_trends"]
        )
        assert len(all_videos) == 3


# ── account_optimizer ─────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_audit_returns_dict(self):
        result = acct.audit_account(
            platform="tiktok",
            handle="testpage",
            niche="fitness",
            followers=10000,
            avg_views=5000,
            avg_likes=500,
        )
        assert isinstance(result, dict)
        assert "score" in result
        assert "grade" in result
        assert "issues" in result
        assert "action_items" in result
        assert "wins" in result

    def test_audit_score_range(self):
        result = acct.audit_account("tiktok", "test", "fitness", 50000, 20000, 3000)
        assert 0 <= result["score"] <= 100

    def test_audit_grade_mapping(self):
        assert acct._score_to_grade(90) == "A"
        assert acct._score_to_grade(75) == "B"
        assert acct._score_to_grade(60) == "C"
        assert acct._score_to_grade(45) == "D"
        assert acct._score_to_grade(30) == "F"

    def test_get_best_posting_times(self):
        times = acct.get_best_posting_times("tiktok", "fitness")
        assert isinstance(times, list)
        assert len(times) > 0
        entry = times[0]
        assert "day" in entry
        assert "utc_start" in entry
        assert "label" in entry
        assert "priority" in entry

    def test_get_best_posting_times_unknown_niche(self):
        times = acct.get_best_posting_times("tiktok", "unknownniche")
        assert isinstance(times, list)

    def test_suggest_bio_tiktok(self):
        result = acct.suggest_bio("fitness", "tiktok", "fitpage")
        assert "bio_template" in result
        assert "char_limit" in result
        assert "tips" in result
        assert len(result["bio_template"]) <= result["char_limit"]

    def test_suggest_bio_youtube(self):
        result = acct.suggest_bio("finance", "youtube", "wealthpage")
        assert len(result["bio_template"]) > 0

    def test_engagement_rate_calculation(self):
        result = acct.get_engagement_rate(views=10000, likes=1000, comments=100)
        assert result["likes_rate"] == 10.0
        assert result["engagement_rate_by_views"] == 11.0
        assert result["rating"] == "excellent"

    def test_engagement_rate_poor(self):
        result = acct.get_engagement_rate(views=100000, likes=100)
        assert result["rating"] in ("poor", "average")

    def test_engagement_rate_zero_views(self):
        result = acct.get_engagement_rate(views=0, likes=100)
        assert "error" in result

    def test_follower_tier_tiktok(self):
        assert "nano" in acct._get_follower_tier("tiktok", 5000)
        assert "micro" in acct._get_follower_tier("tiktok", 50000)
        assert "mid" in acct._get_follower_tier("tiktok", 500000)
        assert "macro" in acct._get_follower_tier("tiktok", 5000000)


# ── theme_page ────────────────────────────────────────────────────────

class TestThemePage:
    def test_niche_guide_known_niche(self):
        guide = theme_mod.get_niche_guide("fitness")
        assert guide["niche"] == "fitness"
        assert "content_pillars" in guide
        assert "viral_formats" in guide
        assert "monetization_paths" in guide
        assert "hashtags" in guide
        assert "quick_start_steps" in guide

    def test_niche_guide_unknown_niche(self):
        guide = theme_mod.get_niche_guide("underwater_basket_weaving")
        assert "niche" in guide
        assert "monetization_paths" in guide

    def test_conversion_guide_has_phases(self):
        guide = theme_mod.get_conversion_guide()
        assert "phases" in guide
        assert len(guide["phases"]) == 4
        assert "common_mistakes" in guide
        assert "tools_needed" in guide

    def test_conversion_guide_phase_structure(self):
        guide = theme_mod.get_conversion_guide()
        for phase in guide["phases"]:
            assert "phase" in phase
            assert "name" in phase
            assert "tasks" in phase
            assert len(phase["tasks"]) > 0

    def test_monetization_strategies(self):
        strats = theme_mod.get_monetization_strategies("finance")
        assert isinstance(strats, list)
        assert len(strats) >= 2
        for s in strats:
            assert "rank" in s
            assert "path" in s

    def test_generate_content_calendar(self):
        cal = theme_mod.generate_content_calendar(
            niche="fitness",
            platform="tiktok",
            start_date=date(2026, 1, 1),
            days=7,
            posts_per_day=2,
        )
        assert len(cal) == 14  # 7 days × 2 posts/day
        entry = cal[0]
        assert "date" in entry
        assert "content_pillar" in entry
        assert "format_idea" in entry
        assert "hashtags" in entry
        assert entry["status"] == "planned"

    def test_list_niches(self):
        niches = theme_mod.list_niches()
        assert len(niches) >= 5
        for n in niches:
            assert "niche" in n
            assert "difficulty" in n

    def test_faceless_content_types_populated(self):
        assert len(theme_mod.FACELESS_CONTENT_TYPES) >= 5


# ── Session ───────────────────────────────────────────────────────────

class TestSession:
    def test_add_account(self):
        s = Session("test_add")
        a = s.add_account("tiktok", "@fitpage", niche="fitness")
        assert a["handle"] == "fitpage"
        assert a["platform"] == "tiktok"

    def test_add_account_dedup(self):
        s = Session("test_dedup")
        s.add_account("tiktok", "page1", niche="fitness")
        s.add_account("tiktok", "page1", niche="beauty")
        assert len(s.list_accounts()) == 1
        assert s.list_accounts()[0]["niche"] == "beauty"

    def test_remove_account(self):
        s = Session("test_remove")
        s.add_account("tiktok", "page2")
        ok = s.remove_account("tiktok", "page2")
        assert ok
        assert len(s.list_accounts()) == 0

    def test_remove_nonexistent(self):
        s = Session("test_nonexist")
        ok = s.remove_account("tiktok", "nobody")
        assert not ok

    def test_cache_and_retrieve(self):
        s = Session("test_cache")
        data = [{"id": 1, "title": "Test"}]
        s.cache_trends("test_key", data)
        retrieved = s.get_cached_trends("test_key")
        assert retrieved == data

    def test_cache_miss(self):
        s = Session("test_miss")
        assert s.get_cached_trends("nonexistent") is None

    def test_clear_cache(self):
        s = Session("test_clear")
        s.cache_trends("k1", [])
        s.cache_trends("k2", [])
        n = s.clear_cache()
        assert n == 2
        assert s.get_cached_trends("k1") is None

    def test_set_niche(self):
        s = Session("test_niche")
        s.set_niche("Fitness")
        assert s.active_niche == "fitness"

    def test_set_platform_valid(self):
        s = Session("test_platform")
        s.set_platform("tiktok")
        assert s.active_platform == "tiktok"

    def test_set_platform_invalid(self):
        s = Session("test_invalid_platform")
        with pytest.raises(ValueError):
            s.set_platform("twitter")

    def test_status(self):
        s = Session("test_status")
        st = s.status()
        assert "session_id" in st
        assert "accounts" in st
        assert "active_niche" in st
