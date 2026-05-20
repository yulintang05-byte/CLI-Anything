"""Tests for trendscraper core modules."""
import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.trendscraper.core import optimizer as opt_mod
from cli_anything.trendscraper.core import theme_pages as theme_mod
from cli_anything.trendscraper.core import trends as trends_mod


# ─── Optimizer tests ─────────────────────────────────────────────────────────

class TestOptimizeCaption:
    def test_basic_caption_tiktok(self):
        result = opt_mod.optimize_caption(
            text="My workout routine",
            platform="tiktok",
            niche="fitness",
            trending_hashtags=["gymlife", "fitnessmotivation"],
        )
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"
        assert "#" in result["caption"]
        assert len(result["hashtags_used"]) <= 5

    def test_instagram_hashtag_limit(self):
        result = opt_mod.optimize_caption(platform="instagram", niche="luxury")
        assert len(result["hashtags_used"]) <= 15

    def test_twitter_hashtag_limit(self):
        result = opt_mod.optimize_caption(platform="twitter", niche="finance")
        assert len(result["hashtags_used"]) <= 2

    def test_has_cta(self):
        result = opt_mod.optimize_caption(platform="tiktok", niche="motivation")
        assert result["call_to_action"]

    def test_has_hook(self):
        result = opt_mod.optimize_caption(platform="instagram", niche="travel")
        assert result["suggested_hook"]

    def test_empty_text_uses_template(self):
        result = opt_mod.optimize_caption(text="", platform="tiktok", niche="motivation")
        assert result["caption"]


class TestAnalyzeAccount:
    def test_engagement_rate_calculation(self):
        result = opt_mod.analyze_account(
            platform="tiktok",
            followers=10_000,
            avg_views=5_000,
            avg_likes=500,
            niche="fitness",
        )
        assert result["engagement_rate"] == pytest.approx(10.0)

    def test_grade_excellent(self):
        result = opt_mod.analyze_account(
            platform="tiktok",
            followers=50_000,
            avg_views=100_000,
            avg_likes=20_000,
            niche="luxury",
        )
        assert "A" in result["account_grade"]

    def test_grade_needs_work(self):
        result = opt_mod.analyze_account(
            platform="tiktok",
            followers=10_000,
            avg_views=100,
            avg_likes=1,
            niche="generic",
        )
        assert "D" in result["account_grade"]

    def test_recommendations_not_empty(self):
        result = opt_mod.analyze_account(platform="instagram", followers=5_000, avg_views=500, niche="beauty")
        assert len(result["recommendations"]) > 0

    def test_monetization_threshold_tiktok(self):
        result = opt_mod.analyze_account(platform="tiktok", followers=15_000, avg_views=3_000)
        thresholds = result["monetization_threshold"]
        assert thresholds["creator_fund"]["unlocked"] is True
        assert thresholds["creator_fund"]["required_followers"] == 10_000

    def test_zero_views_no_division_error(self):
        result = opt_mod.analyze_account(platform="tiktok", followers=0, avg_views=0, avg_likes=0)
        assert result["engagement_rate"] == 0.0


class TestContentCalendar:
    def test_returns_correct_days(self):
        cal = opt_mod.generate_content_calendar(niche="motivation", platform="tiktok", days=7)
        assert len(cal["posts"]) == 7

    def test_all_posts_have_hashtags(self):
        cal = opt_mod.generate_content_calendar(niche="fitness", platform="instagram", days=3)
        for post in cal["posts"]:
            assert len(post["hashtags"]) > 0

    def test_posting_times_exist(self):
        cal = opt_mod.generate_content_calendar(niche="luxury", platform="tiktok", days=7)
        for post in cal["posts"]:
            assert isinstance(post["suggested_times_utc"], list)


# ─── Theme page tests ─────────────────────────────────────────────────────────

class TestNicheAnalysis:
    def test_known_niche_returns_data(self):
        result = theme_mod.get_niche_analysis("luxury")
        assert result["niche"] == "luxury"
        assert "analysis" in result
        assert result["analysis"]["avg_cpm_usd"] > 0

    def test_unknown_niche_returns_error(self):
        result = theme_mod.get_niche_analysis("xyzunknown")
        assert "error" in result
        assert "available_niches" in result

    def test_all_niches_have_monetization(self):
        for niche in theme_mod.NICHES:
            result = theme_mod.get_niche_analysis(niche)
            assert "monetization_breakdown" in result

    def test_niche_comparison_returns_ranked(self):
        result = theme_mod.compare_niches()
        comparison = result["comparison"]
        assert len(comparison) > 0
        # Verify sorted descending by score
        scores = [n["score"] for n in comparison]
        assert scores == sorted(scores, reverse=True)

    def test_compare_specific_niches(self):
        result = theme_mod.compare_niches(["luxury", "cars", "fitness"])
        assert len(result["comparison"]) == 3


class TestMonetizationStrategies:
    def test_all_methods_accessible(self):
        for method in theme_mod.MONETIZATION_METHODS:
            result = theme_mod.get_monetization_strategy(method)
            assert "how_to" in result
            assert len(result["how_to"]) > 0

    def test_unknown_method_returns_error(self):
        result = theme_mod.get_monetization_strategy("nonexistent_method")
        assert "error" in result

    def test_shoutout_has_pricing_info(self):
        result = theme_mod.get_monetization_strategy("shoutouts")
        assert "income_range_usd" in result
        assert result["income_range_usd"]["min"] >= 0

    def test_affiliate_has_top_programs(self):
        result = theme_mod.get_monetization_strategy("affiliate")
        assert "top_programs" in result


class TestGrowthPlaybooks:
    def test_playbook_for_each_platform(self):
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            result = theme_mod.get_growth_playbook(platform)
            assert len(result["steps"]) >= 5
            assert "common_mistakes" in result

    def test_unknown_platform_returns_error(self):
        result = theme_mod.get_growth_playbook("snapchat")
        assert "error" in result


class TestPageFlipRoadmap:
    def test_roadmap_has_5_phases(self):
        result = theme_mod.page_flip_roadmap(niche="luxury", platform="instagram", target_followers=50_000)
        assert len(result["phases"]) == 5

    def test_estimated_value_positive(self):
        result = theme_mod.page_flip_roadmap(niche="finance", platform="tiktok", target_followers=100_000)
        assert result["estimated_sell_value_usd"] > 0

    def test_timeline_positive(self):
        result = theme_mod.page_flip_roadmap(niche="cars", platform="tiktok", target_followers=10_000)
        assert result["estimated_timeline_months"] >= 1

    def test_all_phases_have_actions(self):
        result = theme_mod.page_flip_roadmap(niche="motivation", platform="instagram", target_followers=20_000)
        for phase in result["phases"]:
            assert len(phase["actions"]) > 0


# ─── Trend aggregation tests ──────────────────────────────────────────────────

class TestTrendMerging:
    def _make_yt_data(self, hashtags=None):
        return {
            "platform": "youtube",
            "trending_hashtags": hashtags or [{"tag": "fitness", "count": 5}, {"tag": "viral", "count": 3}],
            "trending_music": [{"title": "Shape of You", "count": 2}],
            "video_count": 10,
            "source": "mock",
        }

    def _make_tt_data(self, hashtags=None):
        return {
            "platform": "tiktok",
            "trending_hashtags": hashtags or [{"tag": "fitness", "count": 8}, {"tag": "fyp", "count": 15}],
            "trending_sounds": [{"title": "Trending Sound 1", "count": 50}],
            "video_count": 20,
            "source": "mock",
        }

    def test_cross_platform_finds_shared(self):
        yt = self._make_yt_data()
        tt = self._make_tt_data()
        cross = trends_mod._find_cross_platform_trends(yt, tt)
        tags = [h["tag"] for h in cross]
        assert "fitness" in tags

    def test_merged_hashtags_scored(self):
        yt = self._make_yt_data()
        tt = self._make_tt_data()
        merged = trends_mod._merge_hashtags(yt, tt)
        assert all("score" in h for h in merged)
        # Cross-platform should score higher
        fitness = next(h for h in merged if h["tag"] == "fitness")
        assert len(fitness["platforms"]) == 2

    def test_music_merge_deduplicates(self):
        yt = self._make_yt_data()
        tt = self._make_tt_data()
        music = trends_mod._merge_music(yt, tt)
        titles = [m.get("title", "") for m in music]
        assert len(titles) == len(set(t.lower() for t in titles if t))

    def test_top_hashtags_for_posting_format(self):
        trends = {
            "cross_platform_trends": [{"tag": "fitness"}, {"tag": "motivation"}],
            "trending_hashtags": [{"tag": "viral"}, {"tag": "trending"}],
        }
        result = trends_mod._top_hashtags_for_posting(trends)
        assert all(t.startswith("#") for t in result)


# ─── CLI tests ────────────────────────────────────────────────────────────────

class TestCLI:
    def test_main_help(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "TrendScraper" in result.output

    def test_scrape_group_help(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["scrape", "--help"])
        assert result.exit_code == 0

    def test_theme_group_help(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme", "--help"])
        assert result.exit_code == 0

    def test_optimize_caption_runs(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        # Mock the fetch so we don't hit network in tests
        with patch("cli_anything.trendscraper.core.trends.fetch_all_trends") as mock_trends:
            mock_trends.return_value = {"trending_hashtags": [{"tag": "viral", "count": 5, "platforms": ["tiktok"]}], "trending_music": [], "cross_platform_trends": [], "youtube_summary": {}, "tiktok_summary": {}}
            result = runner.invoke(main, [
                "optimize", "caption",
                "--text", "Test post",
                "--platform", "tiktok",
                "--niche", "motivation",
            ])
        assert result.exit_code == 0

    def test_theme_compare_runs(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme", "compare"])
        assert result.exit_code == 0
        assert "Niche" in result.output

    def test_theme_strategies_runs(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme", "strategies"])
        assert result.exit_code == 0

    def test_optimize_times_runs(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["optimize", "times", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_json_output_flag(self):
        from click.testing import CliRunner
        from cli_anything.trendscraper.trendscraper_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["--json", "theme", "strategies"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "available_niches" in data
