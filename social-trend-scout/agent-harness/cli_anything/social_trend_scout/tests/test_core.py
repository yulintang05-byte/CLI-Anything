"""Unit tests for social-trend-scout core modules (no external API calls)."""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from cli_anything.social_trend_scout.core.youtube_trends import YouTubeTrends, YOUTUBE_CATEGORIES
from cli_anything.social_trend_scout.core.tiktok_trends import TikTokTrends, NICHE_SEEDS
from cli_anything.social_trend_scout.core.trend_analyzer import TrendAnalyzer
from cli_anything.social_trend_scout.core.account_optimizer import AccountOptimizer
from cli_anything.social_trend_scout.core.theme_pages import ThemePageStrategy, NICHE_DATABASE
from cli_anything.social_trend_scout.core.content_calendar import ContentCalendar
from cli_anything.social_trend_scout.core.session import Session
from cli_anything.social_trend_scout.utils.output import (
    format_number, format_viral_score, format_hashtag_table, format_video_table
)


# ======================================================================
# YouTubeTrends
# ======================================================================

class TestYouTubeTrendsHashtagExtraction:
    def test_extracts_hashtags_from_title(self):
        tags = YouTubeTrends._extract_hashtags("Going viral with #fitness and #gym today")
        assert "#fitness" in tags
        assert "#gym" in tags

    def test_extracts_hashtags_from_description(self):
        tags = YouTubeTrends._extract_hashtags("Daily #motivation #mindset #success content")
        assert len(tags) == 3

    def test_no_duplicates(self):
        tags = YouTubeTrends._extract_hashtags("#fitness #fitness #gym #fitness")
        assert tags.count("#fitness") == 1

    def test_empty_text(self):
        assert YouTubeTrends._extract_hashtags("") == []

    def test_no_hashtags(self):
        assert YouTubeTrends._extract_hashtags("plain text no tags") == []

    def test_mixed_case_normalized(self):
        tags = YouTubeTrends._extract_hashtags("#Fitness #GYM")
        assert "#fitness" in tags
        assert "#gym" in tags

    def test_parse_video_item(self):
        yt = YouTubeTrends("fake_key")
        item = {
            "id": "abc123",
            "snippet": {
                "title": "My #fitness workout",
                "channelTitle": "FitChannel",
                "categoryId": "17",
                "publishedAt": "2024-01-01T00:00:00Z",
                "description": "#gym #workout tips",
                "tags": ["fitness", "gym"],
                "thumbnails": {"high": {"url": "http://img.example.com"}},
            },
            "statistics": {"viewCount": "1000000", "likeCount": "50000", "commentCount": "2000"},
            "contentDetails": {"duration": "PT10M30S"},
        }
        parsed = yt._parse_video(item)
        assert parsed["id"] == "abc123"
        assert parsed["views"] == 1000000
        assert parsed["likes"] == 50000
        assert parsed["engagement_pct"] == round(52000 / 1000000 * 100, 2)
        assert "#fitness" in parsed["hashtags"]
        assert len(parsed["tags"]) <= 15

    def test_rank_by_viral_score_sorts_descending(self):
        yt = YouTubeTrends("fake")
        videos = [
            {"views": 100, "engagement_pct": 1.0},
            {"views": 1000000, "engagement_pct": 8.0},
            {"views": 50000, "engagement_pct": 3.0},
        ]
        ranked = yt.rank_by_viral_score(videos)
        assert ranked[0]["views"] == 1000000
        assert all("viral_score" in v for v in ranked)
        assert ranked[0]["viral_score"] >= ranked[1]["viral_score"]

    def test_rank_by_viral_score_empty(self):
        yt = YouTubeTrends("fake")
        assert yt.rank_by_viral_score([]) == []

    def test_viral_score_bounded_0_100(self):
        yt = YouTubeTrends("fake")
        videos = [
            {"views": i * 10000, "engagement_pct": float(i)} for i in range(1, 11)
        ]
        ranked = yt.rank_by_viral_score(videos)
        for v in ranked:
            assert 0 <= v["viral_score"] <= 100

    def test_youtube_categories_completeness(self):
        assert "0" in YOUTUBE_CATEGORIES
        assert "10" in YOUTUBE_CATEGORIES  # Music
        assert "20" in YOUTUBE_CATEGORIES  # Gaming

    def test_avg_duration_parsing(self):
        videos = [
            {"duration": "PT10M30S", "engagement_pct": 5.0, "views": 1000, "viral_score": 70},
            {"duration": "PT5M", "engagement_pct": 4.0, "views": 900, "viral_score": 65},
        ]
        result = TrendAnalyzer._avg_duration(videos)
        assert "m" in result or result == "unknown"


# ======================================================================
# TikTokTrends
# ======================================================================

class TestTikTokTrends:
    def test_fallback_hashtags_returned_on_error(self):
        tt = TikTokTrends()
        result = tt._fallback_trending_hashtags("connection refused")
        assert any(h["hashtag"] == "#fyp" for h in result)
        assert any(h["hashtag"] == "#viral" for h in result)
        assert all("fallback" in h.get("note", "") for h in result)

    def test_niche_seeds_contains_fitness(self):
        assert "fitness" in NICHE_SEEDS
        assert all(h.startswith("#") for h in NICHE_SEEDS["fitness"])

    def test_get_niche_hashtags_includes_universal(self):
        tt = TikTokTrends()
        tags = tt.get_niche_hashtags("fitness")
        assert "#fyp" in tags
        assert "#viral" in tags

    def test_get_niche_hashtags_unknown_niche(self):
        tt = TikTokTrends()
        tags = tt.get_niche_hashtags("underwater_basket_weaving")
        assert "#fyp" in tags
        assert "#underwater_basket_weaving" in tags

    def test_research_api_no_token(self):
        tt = TikTokTrends()
        result = tt.get_research_api_trends("fitness")
        assert "error" in result
        assert "research_api_token" in result["error"].lower()

    def test_niche_seeds_all_have_hashtag_prefix(self):
        for niche, tags in NICHE_SEEDS.items():
            for tag in tags:
                assert tag.startswith("#"), f"Tag {tag} in niche {niche} missing #"

    def test_days_ago_format(self):
        result = TikTokTrends._days_ago(7)
        assert len(result) == 8
        assert result.isdigit()

    def test_today_format(self):
        result = TikTokTrends._today()
        assert len(result) == 8
        assert result.isdigit()


# ======================================================================
# TrendAnalyzer
# ======================================================================

class TestTrendAnalyzer:
    def setup_method(self):
        self.analyzer = TrendAnalyzer()

    def test_merge_hashtags_cross_platform(self):
        yt = [{"hashtag": "#fitness", "frequency": 5}, {"hashtag": "#gym", "frequency": 3}]
        tt = [{"hashtag": "#fitness", "frequency": 10}, {"hashtag": "#viral", "frequency": 8}]
        merged = self.analyzer.merge_hashtags(yt, tt)
        fitness = next(h for h in merged if h["hashtag"] == "#fitness")
        assert fitness["cross_platform"] is True
        assert fitness["combined_score"] > 0

    def test_merge_hashtags_yt_only(self):
        yt = [{"hashtag": "#gym", "frequency": 3}]
        tt = [{"hashtag": "#fitness", "frequency": 5}]
        merged = self.analyzer.merge_hashtags(yt, tt)
        gym = next(h for h in merged if h["hashtag"] == "#gym")
        assert gym["cross_platform"] is False

    def test_merge_hashtags_sorted_by_score(self):
        yt = [{"hashtag": "#a", "frequency": 1}]
        tt = [{"hashtag": "#b", "frequency": 100}]
        merged = self.analyzer.merge_hashtags(yt, tt)
        assert merged[0]["hashtag"] == "#b"

    def test_extract_viral_patterns_empty(self):
        result = self.analyzer.extract_viral_patterns([])
        assert result == {}

    def test_extract_viral_patterns_hook_detection(self):
        videos = [
            {"title": "How to build muscle fast", "engagement_pct": 5.0, "viral_score": 70, "duration": "PT10M"},
            {"title": "Top 10 exercises for beginners", "engagement_pct": 4.5, "viral_score": 65, "duration": "PT8M"},
        ]
        patterns = self.analyzer.extract_viral_patterns(videos)
        assert "question_hook" in patterns.get("hook_patterns", [])
        assert "list_format" in patterns.get("hook_patterns", [])

    def test_extract_viral_patterns_content_angles(self):
        videos = [
            {"title": "My fitness story - how I lost 50lbs", "engagement_pct": 6.0, "viral_score": 80, "duration": "PT12M"},
            {"title": "Honest review: Pre-workout worth it?", "engagement_pct": 4.0, "viral_score": 62, "duration": "PT8M"},
        ]
        patterns = self.analyzer.extract_viral_patterns(videos)
        angles = patterns.get("content_angles", [])
        assert "personal_story" in angles or "review" in angles

    def test_classify_trend_velocity_rising(self):
        videos = [{"published_at": datetime.utcnow().isoformat() + "Z", "viral_score": 85, "engagement_pct": 8.0}]
        result = self.analyzer.classify_trend_velocity(videos)
        assert result[0]["velocity"] == "RISING"

    def test_classify_trend_velocity_declining(self):
        old_date = "2020-01-01T00:00:00Z"
        videos = [{"published_at": old_date, "viral_score": 20, "engagement_pct": 1.0}]
        result = self.analyzer.classify_trend_velocity(videos)
        assert result[0]["velocity"] == "DECLINING"

    def test_generate_action_plan_structure(self):
        hashtags = [
            {"hashtag": "#fitness", "cross_platform": True, "combined_score": 10},
            {"hashtag": "#gym", "cross_platform": False, "combined_score": 5},
        ]
        patterns = {"hook_patterns": ["question_hook"], "content_angles": ["educational"],
                    "top_title_words": [("workout", 5), ("tips", 3)], "avg_viral_duration": "8m 30s"}
        plan = self.analyzer.generate_action_plan(hashtags, patterns, "fitness")
        assert "immediate_actions" in plan
        assert "content_strategy" in plan
        assert "hashtag_strategy" in plan
        assert plan["niche"] == "fitness"

    def test_hashtag_recommendation_high_priority(self):
        tag_data = {"cross_platform": True, "youtube_frequency": 5, "tiktok_frequency": 8}
        rec = TrendAnalyzer._hashtag_recommendation(tag_data)
        assert "HIGH PRIORITY" in rec


# ======================================================================
# AccountOptimizer
# ======================================================================

class TestAccountOptimizer:
    def setup_method(self):
        self.optimizer = AccountOptimizer()

    def test_posting_times_tiktok(self):
        result = self.optimizer.get_best_posting_times("tiktok", "UTC")
        assert "schedule" in result
        assert "Monday" in result["schedule"]
        assert len(result["schedule"]["Monday"]) >= 2

    def test_posting_times_unknown_platform(self):
        result = self.optimizer.get_best_posting_times("snapchat")
        assert "error" in result

    def test_profile_checklist_tiktok(self):
        result = self.optimizer.get_profile_checklist("tiktok")
        assert "checklist" in result
        assert len(result["checklist"]) > 3

    def test_profile_checklist_with_niche(self):
        result = self.optimizer.get_profile_checklist("tiktok", "fitness")
        assert "niche_specific_tips" in result
        assert len(result["niche_specific_tips"]) > 0

    def test_profile_checklist_unknown_platform(self):
        result = self.optimizer.get_profile_checklist("pinterest")
        assert "error" in result

    def test_optimize_hashtags_count_respected(self):
        trending = [{"hashtag": f"#tag{i}", "frequency": 10 - i} for i in range(20)]
        niche_tags = ["#fitness", "#gym"]
        result = self.optimizer.optimize_hashtags("tiktok", "fitness", trending, niche_tags)
        assert "recommended_hashtags" in result
        assert len(result["recommended_hashtags"]) <= 5  # TikTok limit

    def test_bio_generation_tiktok(self):
        result = self.optimizer.generate_bio("tiktok", "fitness", "fitnessguru")
        assert "bio" in result
        assert "fitness" in result["bio"].lower() or "Fitness" in result["bio"]
        assert result["char_count"] > 0

    def test_bio_generation_all_platforms(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            result = self.optimizer.generate_bio(platform, "cars", "carpage")
            assert "bio" in result
            assert len(result["bio"]) > 10

    def test_engagement_tactics_all_platforms(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            result = self.optimizer.get_engagement_tactics(platform)
            assert "tactics" in result
            assert len(result["tactics"]) >= 5

    def test_engagement_tactics_unknown_platform(self):
        result = self.optimizer.get_engagement_tactics("myspace")
        assert result["tactics"] == []

    def test_full_audit_structure(self):
        result = self.optimizer.full_audit("tiktok", "fitness", "myhandle")
        assert "account" in result
        assert "profile_checklist" in result
        assert "best_posting_times" in result
        assert "engagement_tactics" in result
        assert "bio_suggestion" in result

    def test_niche_specific_tips_fitness(self):
        tips = AccountOptimizer._niche_specific_tips("tiktok", "fitness")
        assert len(tips) > 0
        assert any("transform" in t.lower() or "before" in t.lower() for t in tips)

    def test_niche_specific_tips_unknown(self):
        tips = AccountOptimizer._niche_specific_tips("tiktok", "unknown_niche")
        assert len(tips) > 0


# ======================================================================
# ThemePageStrategy
# ======================================================================

class TestThemePageStrategy:
    def setup_method(self):
        self.strategy = ThemePageStrategy()

    def test_get_niche_guide_fitness(self):
        result = self.strategy.get_niche_guide("fitness")
        assert "description" in result
        assert "monetization" in result
        assert "launch_checklist" in result
        assert "first_30_days" in result

    def test_get_niche_guide_all_niches(self):
        for niche in NICHE_DATABASE:
            result = self.strategy.get_niche_guide(niche)
            assert "error" not in result, f"Niche {niche} returned error"

    def test_get_niche_guide_unknown(self):
        result = self.strategy.get_niche_guide("quilting")
        assert "error" in result
        assert "Available" in result["error"]

    def test_launch_checklist_contains_platform(self):
        data = NICHE_DATABASE["fitness"]
        checklist = ThemePageStrategy._launch_checklist("fitness", data)
        assert any("platform" in item.lower() for item in checklist)

    def test_first_30_days_plan_covers_all_weeks(self):
        data = NICHE_DATABASE["motivation"]
        plan = ThemePageStrategy._first_30_days_plan("motivation", data)
        assert len(plan) == 4
        all_days = [p["days"] for p in plan]
        assert "1–7" in all_days

    def test_content_sourcing_zero_budget(self):
        result = self.strategy.get_content_sourcing_guide("zero")
        assert "methods" in result
        assert "repost_with_credit" in result["methods"]
        assert "ai_generated" in result["methods"]

    def test_content_sourcing_workflow(self):
        result = self.strategy.get_content_sourcing_guide("zero")
        assert len(result["recommended_workflow"]) >= 4

    def test_conversion_plan_pre_monetization(self):
        result = self.strategy.get_conversion_plan("fitness", 500)
        assert result["stage"] == "pre-monetization"

    def test_conversion_plan_established(self):
        result = self.strategy.get_conversion_plan("finance", 200000)
        assert result["stage"] == "established"
        assert len(result["recommended_strategies"]) > 3

    def test_estimate_revenue_brackets(self):
        assert "grow first" in ThemePageStrategy._estimate_revenue(500, "$5")
        assert "affiliate" in ThemePageStrategy._estimate_revenue(5000, "$5").lower()
        assert "brand" in ThemePageStrategy._estimate_revenue(100001, "$25").lower()

    def test_platform_comparison_fitness(self):
        result = self.strategy.platform_comparison("fitness")
        assert "recommended_order" in result
        assert "multi_platform_tip" in result

    def test_platform_comparison_all_niches(self):
        for niche in NICHE_DATABASE:
            result = self.strategy.platform_comparison(niche)
            assert "recommended_order" in result

    def test_full_playbook_structure(self):
        result = self.strategy.full_playbook("motivation")
        assert "niche_guide" in result
        assert "content_sourcing" in result
        assert "conversion_plan_10k" in result
        assert "platform_comparison" in result
        assert "tools" in result

    def test_recommended_tools_categories(self):
        tools = ThemePageStrategy._recommended_tools()
        assert "content_creation" in tools
        assert "scheduling" in tools
        assert "monetization" in tools
        assert "analytics" in tools


# ======================================================================
# ContentCalendar
# ======================================================================

class TestContentCalendar:
    def setup_method(self):
        self.cal = ContentCalendar()

    def test_generate_correct_day_count(self):
        result = self.cal.generate("fitness", "tiktok", days=7)
        assert len(result["calendar"]) == 7

    def test_generate_correct_post_count(self):
        result = self.cal.generate("fitness", "tiktok", days=7, posts_per_day=2)
        assert result["total_posts"] == 14
        for day in result["calendar"]:
            assert len(day["posts"]) == 2

    def test_generate_contains_required_fields(self):
        result = self.cal.generate("motivation", "instagram", days=3)
        for day in result["calendar"]:
            assert "date" in day
            assert "day_of_week" in day
            assert "week_theme" in day
            assert "posts" in day
            for post in day["posts"]:
                assert "format" in post
                assert "hook" in post
                assert "hashtags" in post
                assert "cta" in post

    def test_generate_all_niches(self):
        from cli_anything.social_trend_scout.core.content_calendar import CONTENT_PILLARS
        for niche in CONTENT_PILLARS:
            result = self.cal.generate(niche, "tiktok", days=3)
            assert len(result["calendar"]) == 3

    def test_generate_with_trending_hashtags(self):
        tags = ["#fitness", "#gym", "#workout"]
        result = self.cal.generate("fitness", "tiktok", days=3, trending_hashtags=tags)
        first_post_tags = result["calendar"][0]["posts"][0]["hashtags"]
        assert len(first_post_tags) > 0

    def test_weekly_themes_rotate(self):
        result = self.cal.generate("finance", "youtube", days=28)
        weeks = [day["week_theme"] for day in result["calendar"][::7]]
        assert len(set(weeks)) > 1  # Multiple themes used

    def test_to_rows_format(self):
        result = self.cal.generate("fitness", "tiktok", days=3)
        rows = self.cal.to_rows(result)
        assert rows[0] == ["Date", "Day", "Week Theme", "Post #", "Format", "Pillar", "Hook", "CTA", "Hashtags"]
        assert len(rows) == 4  # header + 3 days * 1 post

    def test_weekly_sprint_structure(self):
        result = self.cal.weekly_sprint("cars", "instagram")
        assert len(result["week_sprint"]) == 7
        assert result["total_posts"] == 14
        assert "tip" in result

    def test_pick_hashtags_rotation(self):
        tags = [f"#tag{i}" for i in range(20)]
        set1 = self.cal._pick_hashtags(tags, 0)
        set2 = self.cal._pick_hashtags(tags, 5)
        assert set1 != set2

    def test_caption_template_contains_hook(self):
        template = self.cal._caption_template("Nobody talks about this", "fitness", "Workout demo")
        assert "Nobody talks about this" in template
        assert "fitness" in template.lower()

    def test_calendar_stats_pillar_distribution(self):
        result = self.cal.generate("motivation", "tiktok", days=10)
        stats = result["stats"]
        assert "content_pillar_distribution" in stats
        total = sum(stats["content_pillar_distribution"].values())
        assert total == 10


# ======================================================================
# Session
# ======================================================================

class TestSession:
    def setup_method(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()

    def test_set_and_get_api_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path
        )
        s = Session()
        s.set_api_key("youtube", "MY_KEY_123")
        assert s.get_api_key("youtube") == "MY_KEY_123"

    def test_get_missing_key_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        assert s.get_api_key("nonexistent") is None

    def test_register_and_list_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.register_account("tiktok", "fitnessguru", "fitness")
        accounts = s.list_accounts("tiktok")
        assert len(accounts["tiktok"]) == 1
        assert accounts["tiktok"][0]["handle"] == "fitnessguru"

    def test_register_duplicate_account_not_added(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.register_account("tiktok", "user1", "fitness")
        s.register_account("tiktok", "user1", "fitness")
        accounts = s.list_accounts("tiktok")
        assert len(accounts["tiktok"]) == 1

    def test_cache_and_retrieve(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        data = {"hashtags": ["#fitness", "#gym"]}
        s.cache_trends("youtube", data, ttl_seconds=3600)
        cached = s.get_cached_trends("youtube")
        assert cached == data

    def test_cache_miss_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        assert s.get_cached_trends("tiktok") is None

    def test_clear_cache_specific(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.cache_trends("youtube", {"data": 1})
        s.clear_cache("youtube")
        assert s.get_cached_trends("youtube") is None

    def test_clear_cache_all(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.cache_trends("youtube", {"data": 1})
        s.cache_trends("tiktok", {"data": 2})
        s.clear_cache()
        assert s.get_cached_trends("youtube") is None
        assert s.get_cached_trends("tiktok") is None

    def test_status_structure(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.set_api_key("youtube", "key1")
        s.register_account("tiktok", "user1", "fitness")
        status = s.status()
        assert "api_keys" in status
        assert "accounts" in status
        assert "cached_platforms" in status

    def test_set_and_get_preference(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        s.set_preference("default_region", "GB")
        assert s.get_preference("default_region") == "GB"

    def test_get_missing_preference_returns_default(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
        s = Session()
        assert s.get_preference("nonexistent", "fallback") == "fallback"


# ======================================================================
# Output utilities
# ======================================================================

class TestOutputUtils:
    def test_format_number_millions(self):
        assert format_number(1_500_000) == "1.5M"

    def test_format_number_thousands(self):
        assert format_number(25_000) == "25.0K"

    def test_format_number_small(self):
        assert format_number(999) == "999"

    def test_format_viral_score_fire(self):
        assert "🔥" in format_viral_score(85)

    def test_format_viral_score_rising(self):
        assert "📈" in format_viral_score(65)

    def test_format_viral_score_declining(self):
        assert "📉" in format_viral_score(20)

    def test_format_hashtag_table_structure(self):
        hashtags = [
            {"hashtag": "#fitness", "frequency": 10, "combined_score": 8.0, "cross_platform": True, "recommendation": "HIGH PRIORITY"},
        ]
        rows = format_hashtag_table(hashtags)
        assert rows[0] == ["Rank", "Hashtag", "Frequency", "Cross-Platform", "Recommendation"]
        assert rows[1][1] == "#fitness"
        assert rows[1][3] == "✅"

    def test_format_video_table_structure(self):
        videos = [
            {"title": "Test Video", "channel": "TestChannel", "views": 1000000,
             "engagement_pct": 5.0, "viral_score": 75, "velocity": "RISING"},
        ]
        rows = format_video_table(videos)
        assert rows[0][1] == "Title"
        assert "1.0M" in str(rows[1])

    def test_format_video_table_truncates_long_title(self):
        videos = [
            {"title": "A" * 60, "channel": "Ch", "views": 1000, "engagement_pct": 1.0, "viral_score": 30, "velocity": "DECLINING"},
        ]
        rows = format_video_table(videos)
        assert len(rows[1][1]) <= 47  # 45 chars + "…"
