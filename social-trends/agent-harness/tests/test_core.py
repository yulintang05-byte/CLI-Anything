"""Unit tests for social-trends core modules.

Tests run entirely in demo mode (no API keys required).
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_trends.utils import youtube_backend as yt
from cli_anything.social_trends.utils import tiktok_backend as tt
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import optimizer as opt
from cli_anything.social_trends.core import theme_pages as theme


# ── YouTube backend ───────────────────────────────────────────────────────────

class TestYouTubeBackend:

    def test_fetch_trending_videos_demo_mode(self):
        result = yt.fetch_trending_videos(limit=5)
        assert result["platform"] == "youtube"
        assert result["mode"] == "demo"
        assert result["total"] == 5
        assert len(result["items"]) == 5

    def test_fetch_trending_videos_item_schema(self):
        result = yt.fetch_trending_videos(limit=1)
        item = result["items"][0]
        assert "rank" in item
        assert "title" in item
        assert "channel" in item
        assert "views" in item
        assert "likes" in item
        assert isinstance(item["views"], int)
        assert isinstance(item["likes"], int)

    def test_fetch_trending_videos_limit_respected(self):
        for n in [1, 5, 10]:
            result = yt.fetch_trending_videos(limit=n)
            assert result["total"] == n
            assert len(result["items"]) == n

    def test_fetch_trending_videos_has_hashtags(self):
        result = yt.fetch_trending_videos(limit=3)
        for item in result["items"]:
            assert "hashtags" in item
            assert isinstance(item["hashtags"], list)

    def test_fetch_trending_music_demo_mode(self):
        result = yt.fetch_trending_music(limit=5)
        assert result["platform"] == "youtube"
        assert result["type"] == "music"
        assert result["mode"] == "demo"
        assert result["total"] == 5

    def test_fetch_trending_music_item_schema(self):
        result = yt.fetch_trending_music(limit=1)
        item = result["items"][0]
        assert "rank" in item
        assert "title" in item
        assert "artist" in item
        assert "trend" in item

    def test_fetch_hashtags_demo_mode(self):
        result = yt.fetch_trending_hashtags(limit=5)
        assert result["platform"] == "youtube"
        assert result["type"] == "hashtags"
        assert result["total"] == 5

    def test_fetch_hashtags_with_niche_fitness(self):
        result = yt.fetch_trending_hashtags(niche="fitness", limit=10)
        assert result["niche"] == "fitness"
        tags = [item["tag"] for item in result["items"]]
        assert any("fitness" in t or "workout" in t or "gym" in t for t in tags)

    def test_fetch_hashtags_with_niche_finance(self):
        result = yt.fetch_trending_hashtags(niche="finance", limit=10)
        tags = [item["tag"] for item in result["items"]]
        assert any("finance" in t or "invest" in t or "money" in t for t in tags)

    def test_is_demo_mode_no_key(self):
        assert yt.is_demo_mode(None) is True
        assert yt.is_demo_mode("") is True

    def test_is_demo_mode_with_key(self):
        assert yt.is_demo_mode("fake_key_12345") is False

    def test_demo_video_ranks_are_sequential(self):
        result = yt.fetch_trending_videos(limit=5)
        ranks = [item["rank"] for item in result["items"]]
        assert ranks == list(range(1, 6))


# ── TikTok backend ────────────────────────────────────────────────────────────

class TestTikTokBackend:

    def test_fetch_trending_videos_demo_mode(self):
        result = tt.fetch_trending_videos(limit=5)
        assert result["platform"] == "tiktok"
        assert result["mode"] == "demo"
        assert result["total"] == 5
        assert len(result["items"]) == 5

    def test_fetch_trending_videos_item_schema(self):
        result = tt.fetch_trending_videos(limit=1)
        item = result["items"][0]
        assert "rank" in item
        assert "desc" in item
        assert "author" in item
        assert "plays" in item
        assert "likes" in item
        assert "music" in item
        assert "hashtags" in item
        assert isinstance(item["plays"], int)

    def test_fetch_trending_videos_limit_respected(self):
        for n in [1, 3, 8]:
            result = tt.fetch_trending_videos(limit=n)
            assert result["total"] == n

    def test_fetch_trending_sounds_demo_mode(self):
        result = tt.fetch_trending_sounds(limit=5)
        assert result["platform"] == "tiktok"
        assert result["type"] == "sounds"
        assert result["mode"] == "demo"
        assert result["total"] == 5

    def test_fetch_trending_sounds_item_schema(self):
        result = tt.fetch_trending_sounds(limit=1)
        item = result["items"][0]
        assert "rank" in item
        assert "title" in item
        assert "author" in item
        assert "uses" in item
        assert "trend" in item
        assert "mood" in item
        assert "recommended_content" in item
        assert isinstance(item["recommended_content"], list)

    def test_fetch_hashtags_demo_mode(self):
        result = tt.fetch_trending_hashtags(limit=5)
        assert result["platform"] == "tiktok"
        assert result["type"] == "hashtags"
        assert result["total"] == 5

    def test_fetch_hashtags_with_niche_fitness(self):
        result = tt.fetch_trending_hashtags(niche="fitness", limit=10)
        assert result["niche"] == "fitness"
        tags = [item["tag"] for item in result["items"]]
        assert any("fitness" in t or "workout" in t or "gym" in t for t in tags)

    def test_fetch_hashtags_have_advice(self):
        result = tt.fetch_trending_hashtags(limit=5)
        for item in result["items"]:
            assert "advice" in item
            assert len(item["advice"]) > 5

    def test_fetch_hashtags_have_competition_field(self):
        result = tt.fetch_trending_hashtags(limit=5)
        for item in result["items"]:
            assert "competition" in item
            assert item["competition"] in ("low", "medium", "high", "very_high", "extreme")

    def test_is_demo_mode(self):
        assert tt.is_demo_mode(None) is True
        assert tt.is_demo_mode("any_key") is False


# ── Core trends aggregator ────────────────────────────────────────────────────

class TestTrendsCore:

    def test_fetch_all_trends_structure(self):
        result = trends_mod.fetch_all_trends(region="US", limit=3)
        assert "youtube" in result
        assert "tiktok" in result
        assert "cross_platform" in result
        assert "insights" in result
        assert "fetched_at" in result

    def test_fetch_all_trends_youtube_section(self):
        result = trends_mod.fetch_all_trends(limit=3)
        yt_section = result["youtube"]
        assert "trending_videos" in yt_section
        assert "trending_music" in yt_section
        assert len(yt_section["trending_videos"]) == 3

    def test_fetch_all_trends_tiktok_section(self):
        result = trends_mod.fetch_all_trends(limit=3)
        tt_section = result["tiktok"]
        assert "trending_videos" in tt_section
        assert "trending_sounds" in tt_section
        assert len(tt_section["trending_videos"]) == 3

    def test_fetch_all_trends_insights_not_empty(self):
        result = trends_mod.fetch_all_trends(limit=3)
        assert len(result["insights"]) >= 2

    def test_fetch_all_trends_insight_schema(self):
        result = trends_mod.fetch_all_trends(limit=3)
        for insight in result["insights"]:
            assert "type" in insight
            assert "message" in insight
            assert "action" in insight


# ── Optimizer ─────────────────────────────────────────────────────────────────

class TestOptimizer:

    def test_get_posting_schedule_tiktok(self):
        result = opt.get_posting_schedule("tiktok")
        assert result["platform"] == "tiktok"
        assert "frequency" in result
        assert "best_days" in result
        assert "recommended_slots" in result
        assert len(result["recommended_slots"]) > 0

    def test_get_posting_schedule_youtube(self):
        result = opt.get_posting_schedule("youtube")
        assert result["platform"] == "youtube"
        assert "Shorts" in result["frequency"] or "long" in result["frequency"].lower()

    def test_get_posting_schedule_instagram(self):
        result = opt.get_posting_schedule("instagram")
        assert result["platform"] == "instagram"
        assert len(result["best_days"]) > 0

    def test_get_bio_templates_tiktok_fitness(self):
        result = opt.get_bio_templates("tiktok", "fitness")
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"
        assert len(result["templates"]) > 0
        assert "placeholders" in result
        assert "bio_rules" in result

    def test_get_bio_templates_general_fallback(self):
        result = opt.get_bio_templates("tiktok", "knitting")
        assert len(result["templates"]) > 0

    def test_get_bio_templates_has_rules(self):
        result = opt.get_bio_templates("youtube", "finance")
        assert len(result["bio_rules"]) >= 3

    def test_get_hashtag_recommendations_tiktok(self):
        result = opt.get_hashtag_recommendations("fitness", "tiktok", count=10)
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"
        assert "strategy" in result
        assert "recommended_mix" in result["strategy"]
        assert "rules" in result

    def test_get_content_plan_7_days(self):
        result = opt.get_content_plan("fitness", "all", days=7)
        assert result["niche"] == "fitness"
        assert len(result["content_plan"]) <= 7
        assert "viral_hooks" in result
        assert len(result["viral_hooks"]) > 0

    def test_get_content_plan_finance(self):
        result = opt.get_content_plan("finance", "all", days=7)
        assert len(result["content_plan"]) > 0
        for day in result["content_plan"]:
            assert "day" in day
            assert "format" in day
            assert "hook" in day
            assert "platform" in day

    def test_get_content_plan_platform_filter_tiktok(self):
        result = opt.get_content_plan("general", "tiktok", days=7)
        for day in result["content_plan"]:
            assert day["platform"] in ("tiktok", "both")

    def test_get_content_plan_platform_filter_youtube(self):
        result = opt.get_content_plan("general", "youtube", days=7)
        for day in result["content_plan"]:
            assert day["platform"] in ("youtube", "both")

    def test_get_profile_checklist_tiktok(self):
        result = opt.get_profile_checklist("tiktok")
        assert result["platform"] == "tiktok"
        assert len(result["checklist"]) >= 8
        for item in result["checklist"]:
            assert "item" in item
            assert "tip" in item
            assert len(item["tip"]) > 10

    def test_get_profile_checklist_youtube(self):
        result = opt.get_profile_checklist("youtube")
        assert result["platform"] == "youtube"
        assert len(result["checklist"]) >= 8


# ── Theme pages ───────────────────────────────────────────────────────────────

class TestThemePages:

    def test_list_niches_all(self):
        result = theme.list_niches("all")
        assert result["filter"] == "all"
        assert result["total"] >= 5
        for n in result["niches"]:
            assert "name" in n
            assert "difficulty" in n
            assert "growth_speed" in n
            assert "monetization_potential" in n
            assert "avg_monthly_revenue" in n

    def test_list_niches_filter_easy(self):
        result = theme.list_niches("easy")
        for n in result["niches"]:
            assert n["difficulty"] == "easy"

    def test_list_niches_filter_growing(self):
        result = theme.list_niches("growing")
        for n in result["niches"]:
            assert n["growth_speed"] in ("fast", "very_fast")

    def test_list_niches_filter_high_income(self):
        result = theme.list_niches("high_income")
        for n in result["niches"]:
            assert n["monetization_potential"] in ("very_high", "extreme")

    def test_get_niche_strategy_luxury(self):
        result = theme.get_niche_strategy("luxury")
        assert "error" not in result
        assert "niche" in result
        assert "overview" in result
        assert "quick_start" in result
        assert "monetization_roadmap" in result
        assert len(result["quick_start"]) >= 3

    def test_get_niche_strategy_fitness(self):
        result = theme.get_niche_strategy("fitness")
        assert "error" not in result
        assert "Fitness" in result["niche"]

    def test_get_niche_strategy_finance(self):
        result = theme.get_niche_strategy("finance")
        assert "error" not in result

    def test_get_niche_strategy_unknown_niche(self):
        result = theme.get_niche_strategy("quantum_physics_memes")
        assert "error" in result
        assert "available_niches" in result

    def test_get_niche_strategy_with_platform(self):
        result = theme.get_niche_strategy("luxury", platform="tiktok")
        assert "platform_specific" in result
        assert "is_best_platform" in result["platform_specific"]

    def test_get_conversion_guide_general(self):
        result = theme.get_conversion_guide()
        assert result["type"] == "general_conversion_guide"
        assert "guide" in result
        guide = result["guide"]
        assert "steps" in guide
        assert "timeline" in guide
        assert "reality_check" in guide
        assert len(guide["steps"]) >= 5

    def test_get_conversion_guide_steps_schema(self):
        result = theme.get_conversion_guide()
        for step in result["guide"]["steps"]:
            assert "step" in step
            assert "title" in step
            assert "actions" in step
            assert len(step["actions"]) > 0

    def test_get_conversion_guide_specific(self):
        result = theme.get_conversion_guide("luxury", "finance")
        assert result["type"] == "specific_conversion"
        assert "steps" in result
        assert "transition_time" in result
        assert "audience_retention" in result

    def test_get_monetization_strategy_fitness(self):
        result = theme.get_monetization_strategy("fitness")
        assert "error" not in result
        assert "revenue_streams" in result
        assert "follower_milestones" in result
        assert "platform_revenue" in result
        assert len(result["revenue_streams"]) > 0

    def test_get_monetization_strategy_follower_milestones(self):
        result = theme.get_monetization_strategy("finance")
        milestones = result["follower_milestones"]
        assert "1k_followers" in milestones
        assert "100k_followers" in milestones

    def test_get_monetization_strategy_unknown(self):
        result = theme.get_monetization_strategy("definitely_not_a_niche_xyz")
        assert "error" in result
