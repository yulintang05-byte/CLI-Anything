"""Unit tests for cli-anything-social core modules.

Tests cover all pure-logic functions (no network calls).
Functions that require live API calls are tested in test_full_e2e.py.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── trends.py ────────────────────────────────────────────────────────────────

class TestTrendsHelpers:
    def test_safe_int_normal(self):
        from cli_anything.social.core.trends import _safe_int
        assert _safe_int("12345") == 12345
        assert _safe_int(999) == 999

    def test_safe_int_bad_values(self):
        from cli_anything.social.core.trends import _safe_int
        assert _safe_int(None) == 0
        assert _safe_int("") == 0
        assert _safe_int("abc") == 0
        assert _safe_int("1.5") == 0

    def test_engagement_rate_normal(self):
        from cli_anything.social.core.trends import _engagement_rate
        rate = _engagement_rate(10000, 500, 100)
        assert rate == 6.0

    def test_engagement_rate_zero_views(self):
        from cli_anything.social.core.trends import _engagement_rate
        assert _engagement_rate(0, 100, 50) == 0.0

    def test_now_iso_format(self):
        from cli_anything.social.core.trends import _now_iso
        ts = _now_iso()
        assert ts.endswith("Z")
        assert "T" in ts
        assert len(ts) == 20

    def test_extract_hashtags_basic(self):
        from cli_anything.social.core.trends import extract_hashtags
        tags = extract_hashtags("Check out #fitness and #gym tips")
        assert "#fitness" in tags
        assert "#gym" in tags

    def test_extract_hashtags_empty(self):
        from cli_anything.social.core.trends import extract_hashtags
        assert extract_hashtags("No hashtags here") == []

    def test_extract_hashtags_mixed_case(self):
        from cli_anything.social.core.trends import extract_hashtags
        tags = extract_hashtags("#FitnessMotivation is great")
        assert "#fitnessmotivation" in tags

    def test_filter_hashtags_by_min_count(self):
        from cli_anything.social.core.trends import filter_hashtags_by_volume
        data = [
            {"hashtag": "#a", "count": 5},
            {"hashtag": "#b", "count": 15},
            {"hashtag": "#c", "count": 2},
        ]
        result = filter_hashtags_by_volume(data, min_count=5)
        assert len(result) == 2
        assert result[0]["hashtag"] == "#b"

    def test_filter_hashtags_by_max_count(self):
        from cli_anything.social.core.trends import filter_hashtags_by_volume
        data = [
            {"hashtag": "#a", "count": 5},
            {"hashtag": "#b", "count": 100},
        ]
        result = filter_hashtags_by_volume(data, max_count=50)
        assert len(result) == 1
        assert result[0]["hashtag"] == "#a"

    def test_build_recommendations_no_data(self):
        from cli_anything.social.core.trends import _build_recommendations
        recs = _build_recommendations({
            "youtube": None,
            "tiktok_feed": None,
            "tiktok_music": None,
            "cross_platform_hashtags": [],
        })
        assert isinstance(recs, list)
        assert len(recs) >= 1

    def test_build_recommendations_with_data(self):
        from cli_anything.social.core.trends import _build_recommendations
        recs = _build_recommendations({
            "youtube": {
                "trending_hashtags": [{"hashtag": "#fitness", "count": 3}],
                "trending_topics": [{"topic": "workout", "count": 5}],
            },
            "tiktok_feed": {
                "trending_hashtags": [{"hashtag": "#gym", "count": 2}],
            },
            "tiktok_music": {
                "trending_music": [{"title": "Song A", "author": "Artist B"}],
            },
            "cross_platform_hashtags": ["#fitness"],
        })
        assert any("PRIORITY" in r for r in recs)


# ── accounts.py ──────────────────────────────────────────────────────────────

class TestAccountsHelpers:
    def test_score_bio_empty(self):
        from cli_anything.social.core.accounts import _score_bio
        score = _score_bio("", "tiktok")
        assert score["overall"] == 0 or score["breakdown"]["length"] == 0

    def test_score_bio_short(self):
        from cli_anything.social.core.accounts import _score_bio
        score = _score_bio("Fitness tips", "tiktok")
        assert score["overall"] < 80

    def test_score_bio_with_cta(self):
        from cli_anything.social.core.accounts import _score_bio
        score = _score_bio("Daily fitness tips 💪 link in bio for guide", "tiktok")
        assert score["breakdown"]["has_cta"] == 100

    def test_score_bio_no_cta(self):
        from cli_anything.social.core.accounts import _score_bio
        score = _score_bio("Daily fitness tips and motivation every day here", "tiktok")
        assert score["breakdown"]["has_cta"] == 0

    def test_score_bio_youtube(self):
        from cli_anything.social.core.accounts import _score_bio
        bio = "Welcome to my channel! I post finance tips every week. Subscribe for daily updates. Click the link to join my community."
        score = _score_bio(bio, "youtube")
        assert score["overall"] > 50

    def test_optimize_bio_returns_templates(self):
        from cli_anything.social.core.accounts import optimize_bio
        result = optimize_bio("tiktok", "fitness", "followers")
        assert "templates" in result
        assert len(result["templates"]) >= 1
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"

    def test_optimize_bio_with_current(self):
        from cli_anything.social.core.accounts import optimize_bio
        result = optimize_bio("tiktok", "fitness", current_bio="Old bio text")
        assert "current_score" in result
        assert "optimised_score" in result
        assert "improvement" in result

    def test_optimize_bio_all_platforms(self):
        from cli_anything.social.core.accounts import optimize_bio
        for platform in ("tiktok", "youtube", "instagram"):
            result = optimize_bio(platform, "fitness")
            assert result["platform"] == platform
            assert len(result["templates"]) >= 1

    def test_get_hashtag_strategy_tiktok_small(self):
        from cli_anything.social.core.accounts import get_hashtag_strategy
        result = get_hashtag_strategy("tiktok", "fitness", "small")
        assert "tiers" in result
        assert "niche_specific" in result["tiers"]
        assert "medium_competition" in result["tiers"]
        assert "broad_reach" in result["tiers"]
        total = sum(t["count"] for t in result["tiers"].values())
        assert total == result["recommended_total"]

    def test_get_hashtag_strategy_instagram_large(self):
        from cli_anything.social.core.accounts import get_hashtag_strategy
        result = get_hashtag_strategy("instagram", "beauty", "large")
        assert result["recommended_total"] >= 20

    def test_get_optimal_posting_times(self):
        from cli_anything.social.core.accounts import get_optimal_posting_times
        result = get_optimal_posting_times("tiktok", "US", "fitness")
        assert "best_times" in result
        assert "best_days" in result
        assert len(result["best_times"]) > 0
        assert len(result["best_days"]) > 0

    def test_get_optimal_posting_times_all_platforms(self):
        from cli_anything.social.core.accounts import get_optimal_posting_times
        for platform in ("tiktok", "youtube", "instagram"):
            result = get_optimal_posting_times(platform, "US")
            assert result["platform"] == platform

    def test_generate_tiktok_tips_new_account(self):
        from cli_anything.social.core.accounts import _generate_tiktok_tips
        tips = _generate_tiktok_tips(
            bio="", followers=100, following=50, hearts=500,
            video_count=5, avg_hearts=100, verified=False,
        )
        assert isinstance(tips, list)
        assert len(tips) >= 2

    def test_generate_youtube_tips_new_channel(self):
        from cli_anything.social.core.accounts import _generate_youtube_tips
        tips = _generate_youtube_tips(
            bio="", subscribers=50, avg_views=10,
            video_count=3, branding={},
        )
        assert isinstance(tips, list)
        assert len(tips) >= 2


# ── theme_pages.py ────────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_available_niches(self):
        from cli_anything.social.core.theme_pages import list_available_niches
        niches = list_available_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 5
        keys = {n["niche"] for n in niches}
        assert "fitness" in keys
        assert "finance" in keys

    def test_get_niche_analysis_fitness(self):
        from cli_anything.social.core.theme_pages import get_niche_analysis
        result = get_niche_analysis("fitness")
        assert result["niche"] == "fitness"
        assert "competition" in result
        assert "viral_formula" in result
        assert "opportunity_score" in result
        assert 0 <= result["opportunity_score"] <= 100

    def test_get_niche_analysis_unknown(self):
        from cli_anything.social.core.theme_pages import get_niche_analysis
        result = get_niche_analysis("nonexistent_niche_xyz")
        assert "error" in result
        assert "available_niches" in result

    def test_get_niche_analysis_all_known(self):
        from cli_anything.social.core.theme_pages import (
            get_niche_analysis, list_available_niches,
        )
        for niche_entry in list_available_niches():
            result = get_niche_analysis(niche_entry["niche"])
            assert "error" not in result
            assert result["niche"] == niche_entry["niche"]

    def test_estimate_revenue_zero_followers(self):
        from cli_anything.social.core.theme_pages import estimate_revenue
        result = estimate_revenue("fitness", 0, "tiktok")
        assert result["total_estimate"]["low"] == 0.0
        assert result["total_estimate"]["mid"] == 0.0

    def test_estimate_revenue_10k_fitness(self):
        from cli_anything.social.core.theme_pages import estimate_revenue
        result = estimate_revenue("fitness", 10000, "tiktok")
        assert "estimated_monthly_revenue" in result
        chans = result["estimated_monthly_revenue"]
        for key in ("platform_ads", "brand_deals", "affiliate_marketing", "digital_products"):
            assert key in chans
            assert chans[key]["low"] <= chans[key]["mid"] <= chans[key]["high"]

    def test_estimate_revenue_high_niche_cpm(self):
        from cli_anything.social.core.theme_pages import estimate_revenue
        crypto = estimate_revenue("crypto", 10000, "tiktok")
        finance = estimate_revenue("finance", 10000, "tiktok")
        fitness = estimate_revenue("fitness", 10000, "tiktok")
        assert crypto["total_estimate"]["mid"] > fitness["total_estimate"]["mid"]

    def test_get_conversion_strategies_no_followers(self):
        from cli_anything.social.core.theme_pages import get_conversion_strategies
        result = get_conversion_strategies("fitness", "tiktok", 0)
        assert "viable_strategies" in result
        # UGC (min 0 followers) should be available
        keys = {s["strategy"] for s in result["viable_strategies"]}
        assert "ugc_content" in keys

    def test_get_conversion_strategies_with_followers(self):
        from cli_anything.social.core.theme_pages import get_conversion_strategies
        result = get_conversion_strategies("fitness", "tiktok", 10000)
        keys = {s["strategy"] for s in result["viable_strategies"]}
        assert "brand_deals" in keys
        assert "account_flipping" in keys

    def test_get_theme_page_playbook_structure(self):
        from cli_anything.social.core.theme_pages import get_theme_page_playbook
        result = get_theme_page_playbook("fitness", "tiktok", 10000)
        assert "phases" in result
        assert len(result["phases"]) == 4
        assert "daily_tasks" in result
        assert "milestones" in result
        assert "tools_needed" in result
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"

    def test_get_theme_page_playbook_unknown_niche(self):
        from cli_anything.social.core.theme_pages import get_theme_page_playbook
        result = get_theme_page_playbook("not_a_real_niche", "tiktok", 1000)
        assert "error" in result

    def test_get_account_flip_valuation_low_engagement(self):
        from cli_anything.social.core.theme_pages import get_account_flip_valuation
        result = get_account_flip_valuation("fitness", "instagram", 10000, 0, 1.0)
        assert result["estimated_value"]["low"] < result["estimated_value"]["mid"]
        assert result["estimated_value"]["mid"] < result["estimated_value"]["high"]

    def test_get_account_flip_valuation_high_engagement(self):
        from cli_anything.social.core.theme_pages import get_account_flip_valuation
        low_eng = get_account_flip_valuation("fitness", "instagram", 10000, 0, 1.0)
        high_eng = get_account_flip_valuation("fitness", "instagram", 10000, 0, 9.0)
        assert high_eng["estimated_value"]["mid"] > low_eng["estimated_value"]["mid"]

    def test_get_account_flip_valuation_with_revenue(self):
        from cli_anything.social.core.theme_pages import get_account_flip_valuation
        no_rev = get_account_flip_valuation("finance", "tiktok", 50000, 0, 4.0)
        with_rev = get_account_flip_valuation("finance", "tiktok", 50000, 1000, 4.0)
        assert with_rev["estimated_value"]["mid"] >= no_rev["estimated_value"]["mid"]

    def test_estimate_growth_time(self):
        from cli_anything.social.core.theme_pages import _estimate_growth_time
        assert "days" in _estimate_growth_time("tiktok", 500) or "week" in _estimate_growth_time("tiktok", 500)
        assert "month" in _estimate_growth_time("tiktok", 100000)


# ── scheduler.py ─────────────────────────────────────────────────────────────

class TestScheduler:
    def test_create_content_calendar_structure(self):
        from cli_anything.social.core.scheduler import create_content_calendar
        result = create_content_calendar("tiktok", "fitness", weeks=2)
        assert "weeks" in result
        assert len(result["weeks"]) == 2
        assert result["total_posts"] > 0
        assert "hashtag_sets" in result
        assert result["platform"] == "tiktok"

    def test_create_content_calendar_all_platforms(self):
        from cli_anything.social.core.scheduler import create_content_calendar
        for platform in ("tiktok", "youtube", "instagram"):
            result = create_content_calendar(platform, "finance", weeks=1)
            assert result["platform"] == platform
            assert result["total_weeks"] == 1

    def test_create_content_calendar_all_niches(self):
        from cli_anything.social.core.scheduler import create_content_calendar
        from cli_anything.social.core.theme_pages import list_available_niches
        for n in list_available_niches():
            result = create_content_calendar("tiktok", n["niche"], weeks=1)
            assert result["total_posts"] > 0

    def test_create_content_calendar_custom_date(self):
        from cli_anything.social.core.scheduler import create_content_calendar
        result = create_content_calendar(
            "tiktok", "fitness", weeks=1, start_date="2025-01-06"
        )
        assert result["start_date"] == "2025-01-06"

    def test_create_content_calendar_max_weeks(self):
        from cli_anything.social.core.scheduler import create_content_calendar
        result = create_content_calendar("tiktok", "fitness", weeks=12)
        assert len(result["weeks"]) == 12

    def test_get_posting_frequency_all_stages(self):
        from cli_anything.social.core.scheduler import get_posting_frequency
        for stage in ("starter", "growing", "established"):
            result = get_posting_frequency("tiktok", stage)
            assert result["account_stage"] == stage
            assert "recommendation" in result
            assert "rationale" in result

    def test_get_posting_frequency_all_platforms(self):
        from cli_anything.social.core.scheduler import get_posting_frequency
        for platform in ("tiktok", "youtube", "instagram"):
            result = get_posting_frequency(platform, "starter")
            assert result["platform"] == platform

    def test_get_content_hooks_all_types(self):
        from cli_anything.social.core.scheduler import get_content_hooks
        for htype in ("curiosity", "value", "social_proof", "controversy"):
            result = get_content_hooks("fitness", htype, 5)
            assert "hooks" in result
            assert len(result["hooks"]) <= 5
            for hook in result["hooks"]:
                assert "type" in hook
                assert "hook" in hook

    def test_get_content_hooks_all_type(self):
        from cli_anything.social.core.scheduler import get_content_hooks
        result = get_content_hooks("finance", "all", 10)
        assert len(result["hooks"]) <= 10

    def test_get_content_hooks_niche_personalisation(self):
        from cli_anything.social.core.scheduler import get_content_hooks
        result = get_content_hooks("fitness", "value", 5)
        for hook in result["hooks"]:
            assert "fitness" in hook["hook"].lower() or len(hook["hook"]) > 10

    def test_get_content_repurposing_plan(self):
        from cli_anything.social.core.scheduler import get_content_repurposing_plan
        result = get_content_repurposing_plan("tiktok", ["instagram", "youtube"], "fitness")
        assert "repurposing_plans" in result
        assert len(result["repurposing_plans"]) == 2
        targets = {p["target"] for p in result["repurposing_plans"]}
        assert "instagram" in targets
        assert "youtube" in targets

    def test_get_content_repurposing_excludes_source(self):
        from cli_anything.social.core.scheduler import get_content_repurposing_plan
        result = get_content_repurposing_plan("youtube", ["tiktok", "instagram"], "food")
        targets = {p["target"] for p in result["repurposing_plans"]}
        assert "youtube" not in targets

    def test_generate_hashtag_sets(self):
        from cli_anything.social.core.scheduler import _generate_hashtag_sets
        sets = _generate_hashtag_sets("fitness", "tiktok", count=3)
        assert len(sets) == 3
        for tag_set in sets:
            assert isinstance(tag_set, list)
            assert len(tag_set) > 0

    def test_week_themes_cycle(self):
        from cli_anything.social.core.scheduler import _week_theme
        themes = [_week_theme(i, "fitness") for i in range(1, 8)]
        assert len(set(themes)) > 1  # not all the same


# ── CLI smoke tests ───────────────────────────────────────────────────────────

class TestCLIInvocation:
    """Test that Click commands are wired correctly without making network calls."""

    def test_cli_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output

    def test_trends_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "--help"])
        assert result.exit_code == 0
        assert "youtube" in result.output

    def test_account_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["account", "--help"])
        assert result.exit_code == 0

    def test_theme_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme", "--help"])
        assert result.exit_code == 0

    def test_schedule_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["schedule", "--help"])
        assert result.exit_code == 0

    def test_theme_niches_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_theme_analyse_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme", "analyse", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_theme_monetise_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "theme", "monetise", "--niche", "fitness",
            "--platform", "tiktok", "--followers", "5000",
        ])
        assert result.exit_code == 0

    def test_theme_revenue_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "theme", "revenue", "--niche", "finance",
            "--followers", "10000", "--platform", "tiktok",
        ])
        assert result.exit_code == 0

    def test_theme_playbook_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "theme", "playbook", "--niche", "fitness",
            "--platform", "tiktok", "--goal", "10000",
        ])
        assert result.exit_code == 0

    def test_theme_valuation_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "theme", "valuation", "--niche", "fitness",
            "--followers", "20000", "--engagement", "5.0",
        ])
        assert result.exit_code == 0

    def test_account_bio_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "account", "bio", "--platform", "tiktok", "--niche", "fitness",
        ])
        assert result.exit_code == 0

    def test_account_hashtags_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "account", "hashtags", "--platform", "tiktok",
            "--niche", "fitness", "--size", "small",
        ])
        assert result.exit_code == 0

    def test_account_post_times_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "account", "post-times", "--platform", "tiktok", "--region", "US",
        ])
        assert result.exit_code == 0

    def test_schedule_calendar_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "schedule", "calendar", "--platform", "tiktok",
            "--niche", "fitness", "--weeks", "1",
        ])
        assert result.exit_code == 0

    def test_schedule_frequency_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "schedule", "frequency", "--platform", "tiktok", "--stage", "starter",
        ])
        assert result.exit_code == 0

    def test_schedule_hooks_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "schedule", "hooks", "--niche", "fitness",
        ])
        assert result.exit_code == 0

    def test_schedule_repurpose_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "schedule", "repurpose",
            "--from", "tiktok", "--to", "instagram",
        ])
        assert result.exit_code == 0

    def test_trends_extract_hashtags_command(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "trends", "extract-hashtags", "#fitness #gym",
        ])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_json_output_flag(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        import json as json_mod
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "theme", "niches",
        ])
        assert result.exit_code == 0
        data = json_mod.loads(result.output)
        assert "available_niches" in data

    def test_trends_all_requires_at_least_one_key(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "all"])
        assert result.exit_code != 0 or "error" in result.output.lower() or "Provide" in result.output
