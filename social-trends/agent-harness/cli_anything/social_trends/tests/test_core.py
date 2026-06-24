#!/usr/bin/env python3
"""Unit tests for social-trends CLI core modules.

Run with: pytest cli_anything/social_trends/tests/test_core.py -v
"""

import pytest
from cli_anything.social_trends.core import tiktok_trends as tt
from cli_anything.social_trends.core import account_optimizer as ao
from cli_anything.social_trends.core import theme_pages as tp
from cli_anything.social_trends.utils.formatters import fmt_number, fmt_duration
from cli_anything.social_trends.utils.config import load_config, save_config, load_accounts, save_accounts


# ---------------------------------------------------------------------------
# Formatter tests
# ---------------------------------------------------------------------------
class TestFormatters:
    def test_fmt_number_millions(self):
        assert fmt_number(1_500_000) == "1.5M"

    def test_fmt_number_thousands(self):
        assert fmt_number(25_000) == "25.0K"

    def test_fmt_number_small(self):
        assert fmt_number(999) == "999"

    def test_fmt_duration_seconds(self):
        assert fmt_duration(90) == "1:30"

    def test_fmt_duration_hours(self):
        assert fmt_duration(3661) == "1:01:01"

    def test_fmt_duration_zero(self):
        assert fmt_duration(0) == "0:00"


# ---------------------------------------------------------------------------
# TikTok trends tests
# ---------------------------------------------------------------------------
class TestTikTokTrends:
    def test_list_niches(self):
        niches = tt.list_available_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 10
        assert "motivation" in niches
        assert "fitness" in niches
        assert "finance" in niches

    def test_fetch_hashtags_valid_niche(self):
        tags = tt.fetch_trending_hashtags_by_niche("fitness", top_n=10)
        assert isinstance(tags, list)
        assert len(tags) == 10
        for tag in tags:
            assert "hashtag" in tag
            assert tag["hashtag"].startswith("#")
            assert "virality_rank" in tag
            assert "estimated_posts" in tag

    def test_fetch_hashtags_invalid_niche(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            tt.fetch_trending_hashtags_by_niche("nonexistent_niche_xyz")

    def test_fetch_hashtags_recommended_flag(self):
        tags = tt.fetch_trending_hashtags_by_niche("motivation", top_n=10)
        recommended = [t for t in tags if t["recommended"]]
        assert len(recommended) >= 3  # At least first 5 should be recommended

    def test_optimal_hashtag_mix(self):
        mix = tt.get_optimal_hashtag_mix("fitness")
        assert "hashtags" in mix
        assert "primary_niche_tags" in mix
        assert "broad_reach_tags" in mix
        assert len(mix["hashtags"]) >= 5
        for tag in mix["hashtags"]:
            assert tag.startswith("#")

    def test_optimal_hashtag_mix_no_broad(self):
        mix = tt.get_optimal_hashtag_mix("motivation", include_broad=False)
        assert len(mix["broad_reach_tags"]) == 0

    def test_fetch_trending_sounds(self):
        sounds = tt.fetch_trending_sounds(top_n=10)
        assert isinstance(sounds, list)
        assert len(sounds) >= 5
        for s in sounds:
            assert "title" in s
            assert "artist" in s
            assert "viral_score" in s
            assert isinstance(s["viral_score"], int)

    def test_fetch_trending_sounds_by_category(self):
        sounds = tt.fetch_trending_sounds(category="pop", top_n=5)
        assert all(s["category"] == "pop" for s in sounds)

    def test_trend_report_structure(self):
        report = tt.get_tiktok_trend_report("finance")
        assert "niche" in report
        assert "trending_hashtags" in report
        assert "optimal_hashtag_mix" in report
        assert "trending_sounds" in report
        assert "content_ideas" in report
        assert "best_posting_times" in report
        assert "algorithm_tips" in report
        assert report["niche"] == "finance"
        assert len(report["algorithm_tips"]) >= 5

    def test_all_niches_hashtags(self):
        all_niches = tt.fetch_all_niches_hashtags()
        assert isinstance(all_niches, dict)
        assert len(all_niches) >= 10
        for niche, tags in all_niches.items():
            assert isinstance(tags, list)
            assert len(tags) >= 5
            for tag in tags:
                assert tag.startswith("#")


# ---------------------------------------------------------------------------
# Account optimizer tests
# ---------------------------------------------------------------------------
class TestAccountOptimizer:
    def test_score_bio_empty(self):
        result = ao.score_bio("", "instagram")
        assert result["score"] < 50
        assert result["bio_length"] == 0
        assert len(result["improvements"]) > 0

    def test_score_bio_good(self):
        bio = "🎯 Fitness coach | Helping 10K+ clients get fit in 90 days 💪 👇 Free workout guide"
        result = ao.score_bio(bio, "instagram")
        assert result["score"] >= 60
        assert result["grade"] in ["A+", "A", "B", "C"]

    def test_score_bio_too_long(self):
        bio = "x" * 200
        result = ao.score_bio(bio, "instagram")
        assert result["bio_length"] == 200
        assert any("Trim bio" in imp for imp in result["improvements"])

    def test_score_to_grade(self):
        assert ao._score_to_grade(95) == "A+"
        assert ao._score_to_grade(85) == "A"
        assert ao._score_to_grade(75) == "B"
        assert ao._score_to_grade(30) == "F"

    def test_posting_schedule_tiktok(self):
        sched = ao.get_posting_schedule("tiktok", "motivation")
        assert sched["platform"] == "tiktok"
        assert "weekly_schedule" in sched
        assert len(sched["weekly_schedule"]) == 7
        for day_data in sched["weekly_schedule"]:
            assert "day" in day_data
            assert "posts" in day_data

    def test_posting_schedule_instagram(self):
        sched = ao.get_posting_schedule("instagram", "fashion")
        assert sched["platform"] == "instagram"
        assert len(sched["weekly_schedule"]) == 7

    def test_posting_schedule_youtube(self):
        sched = ao.get_posting_schedule("youtube", "gaming")
        assert sched["platform"] == "youtube"
        assert len(sched["weekly_schedule"]) == 7

    def test_posting_schedule_invalid_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            ao.get_posting_schedule("snapchat", "motivation")

    def test_growth_stage_zero(self):
        stage = ao._get_growth_stage(0)
        assert stage["stage"] == "Pre-launch"

    def test_growth_stage_nano(self):
        stage = ao._get_growth_stage(500)
        assert "Nano" in stage["stage"]

    def test_growth_stage_mega(self):
        stage = ao._get_growth_stage(5_000_000)
        assert "Mega" in stage["stage"]

    def test_optimize_account_full(self):
        result = ao.optimize_account(
            platform="tiktok",
            handle="testpage",
            niche="motivation",
            bio="Daily motivation 🔥 | Tips for success 👇 Free guide below",
            follower_count=2500,
            goal="growth",
        )
        assert "account" in result
        assert "posting_schedule" in result
        assert "30_day_action_plan" in result
        assert "bio_analysis" in result
        assert result["account"]["handle"] == "@testpage"

    def test_optimize_account_no_bio(self):
        result = ao.optimize_account("instagram", "mypage", "fashion")
        assert result["bio_analysis"] is None

    def test_action_plan_has_4_weeks(self):
        plan = ao._get_action_plan("tiktok", "fitness", 0, "growth")
        assert len(plan) == 4
        for week in plan:
            assert "week" in week
            assert "tasks" in week
            assert len(week["tasks"]) >= 3


# ---------------------------------------------------------------------------
# Theme pages tests
# ---------------------------------------------------------------------------
class TestThemePages:
    def test_list_niches(self):
        niches = tp.list_available_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 6
        assert "motivation" in niches
        assert "finance_wealth" in niches

    def test_blueprint_valid_niche(self):
        blueprint = tp.get_theme_page_blueprint("motivation")
        assert "niche" in blueprint
        assert "setup_checklist" in blueprint
        assert "90_day_plan" in blueprint
        assert "monetization_roadmap" in blueprint
        assert "conversion_funnel" in blueprint
        assert blueprint["niche"] == "motivation"

    def test_blueprint_invalid_niche(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            tp.get_theme_page_blueprint("not_a_real_niche")

    def test_setup_checklist_10_steps(self):
        blueprint = tp.get_theme_page_blueprint("fitness_transformation")
        checklist = blueprint["setup_checklist"]
        assert len(checklist) == 10
        for item in checklist:
            assert "step" in item
            assert "task" in item
            assert "detail" in item

    def test_90_day_plan_4_phases(self):
        blueprint = tp.get_theme_page_blueprint("luxury_lifestyle")
        plan = blueprint["90_day_plan"]
        assert len(plan) == 4
        for phase in plan:
            assert "days" in phase
            assert "focus" in phase
            assert "kpi" in phase
            assert "goals" in phase

    def test_monetization_strategy_valid(self):
        result = tp.get_monetization_strategy("affiliate_marketing")
        assert "description" in result
        assert "steps" in result
        assert "pro_tips" in result
        assert len(result["steps"]) >= 5

    def test_monetization_strategy_invalid(self):
        with pytest.raises(ValueError, match="Unknown method"):
            tp.get_monetization_strategy("not_a_method")

    def test_all_monetization_methods(self):
        methods = tp.get_all_monetization_methods()
        assert len(methods) >= 5
        for m in methods:
            assert "method" in m
            assert "difficulty" in m
            assert "income_ceiling" in m

    def test_conversion_funnel_5_stages(self):
        funnel = tp.get_conversion_funnel()
        assert "stages" in funnel
        assert len(funnel["stages"]) == 5
        stages = [s["name"] for s in funnel["stages"]]
        assert "Awareness" in stages
        assert "Conversion" in stages

    def test_multi_page_system(self):
        plan = tp.get_multi_page_scaling_plan()
        assert "concept" in plan
        assert "phases" in plan
        assert "tools" in plan
        assert len(plan["phases"]) == 3

    def test_content_strategy_has_repurposing(self):
        blueprint = tp.get_theme_page_blueprint("finance_wealth")
        strategy = blueprint["content_strategy"]
        assert "repurposing_workflow" in strategy
        assert len(strategy["repurposing_workflow"]) >= 4


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------
class TestConfig:
    def test_load_empty_config(self, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trends.utils.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("cli_anything.social_trends.utils.config.CONFIG_FILE", tmp_path / "config.json")
        cfg = load_config()
        assert cfg == {}

    def test_save_and_load_config(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.json"
        monkeypatch.setattr("cli_anything.social_trends.utils.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("cli_anything.social_trends.utils.config.CONFIG_FILE", config_file)
        save_config({"youtube_api_key": "test_key_123"})
        cfg = load_config()
        assert cfg["youtube_api_key"] == "test_key_123"

    def test_add_and_list_accounts(self, tmp_path, monkeypatch):
        accounts_file = tmp_path / "accounts.json"
        monkeypatch.setattr("cli_anything.social_trends.utils.config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("cli_anything.social_trends.utils.config.ACCOUNTS_FILE", accounts_file)
        from cli_anything.social_trends.utils.config import add_account, remove_account
        acc = add_account("tiktok", "testpage", "motivation", "growth")
        assert acc["handle"] == "testpage"
        accounts = load_accounts()
        assert len(accounts) == 1
        removed = remove_account("tiktok", "testpage")
        assert removed
        assert len(load_accounts()) == 0
