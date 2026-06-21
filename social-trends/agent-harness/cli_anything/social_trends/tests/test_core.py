"""Unit tests for social-trends core modules — run without API keys."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_trends.core import config as cfg_mod
from cli_anything.social_trends.core import account_optimizer as opt
from cli_anything.social_trends.core import theme_page as tp
from cli_anything.social_trends.core.youtube_trends import _extract_hashtags


# ── Config ────────────────────────────────────────────────────────────

class TestConfig:
    def test_load_returns_dict(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        assert cfg_mod.load() == {}

    def test_set_and_get(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        cfg_mod.set_key("test_key", "test_value")
        assert cfg_mod.get("test_key") == "test_value"

    def test_get_default(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        assert cfg_mod.get("missing", "default") == "default"

    def test_require_raises_without_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.delenv("TEST_ENV_VAR", raising=False)
        with pytest.raises(ValueError, match="Missing config key"):
            cfg_mod.require("missing_key", env_var="TEST_ENV_VAR")

    def test_require_uses_env_var(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setenv("TEST_ENV_VAR", "env_value")
        assert cfg_mod.require("missing_key", env_var="TEST_ENV_VAR") == "env_value"


# ── YouTube utilities ─────────────────────────────────────────────────

class TestYouTubeUtils:
    def test_extract_hashtags_basic(self):
        text = "Check out #fitness and #motivation content"
        tags = _extract_hashtags(text)
        assert "fitness" in tags
        assert "motivation" in tags

    def test_extract_hashtags_empty(self):
        assert _extract_hashtags("no hashtags here") == []

    def test_extract_hashtags_numbers(self):
        tags = _extract_hashtags("#top10 videos #2025trends")
        assert "top10" in tags
        assert "2025trends" in tags


# ── Account Optimizer ─────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_analyze_returns_required_keys(self):
        result = opt.analyze_account(followers=5000, platform="tiktok", niche="fitness")
        assert "tier" in result
        assert "posting_schedule" in result
        assert "hashtag_strategy" in result
        assert "growth_tactics" in result
        assert "content_pillars" in result

    def test_tier_nano(self):
        result = opt.analyze_account(followers=500, platform="tiktok")
        assert result["tier"] == "nano"

    def test_tier_micro(self):
        result = opt.analyze_account(followers=50_000, platform="tiktok")
        assert result["tier"] == "micro"

    def test_tier_mid(self):
        result = opt.analyze_account(followers=500_000, platform="youtube")
        assert result["tier"] == "mid"

    def test_tier_macro(self):
        result = opt.analyze_account(followers=2_000_000, platform="youtube")
        assert result["tier"] == "macro"

    def test_engagement_rate_calculated(self):
        result = opt.analyze_account(
            followers=10_000, platform="tiktok",
            avg_views=5000, avg_likes=600
        )
        er = result["engagement_rate"]
        assert er["current"] == pytest.approx(12.0, 0.1)

    def test_engagement_rate_excellent(self):
        result = opt.analyze_account(
            followers=5000, platform="tiktok",
            avg_views=1000, avg_likes=200
        )
        assert result["engagement_rate"]["rating"] == "EXCELLENT"

    def test_engagement_rate_below_avg(self):
        result = opt.analyze_account(
            followers=5000, platform="tiktok",
            avg_views=10000, avg_likes=50
        )
        assert "BELOW AVERAGE" in result["engagement_rate"]["rating"]

    def test_hashtag_strategy_has_niche_tags(self):
        result = opt.analyze_account(followers=1000, platform="tiktok", niche="finance")
        tags = result["hashtag_strategy"]["evergreen"]
        assert any("finance" in t or "money" in t or "invest" in t for t in tags)

    def test_content_pillars_4_items(self):
        result = opt.analyze_account(followers=1000, platform="tiktok")
        assert len(result["content_pillars"]) == 4

    def test_posting_frequency_tiktok_nano(self):
        result = opt.analyze_account(followers=500, platform="tiktok")
        freq = result["posting_schedule"]["recommended_frequency"]
        assert freq["target_per_week"] == 3

    def test_posting_frequency_youtube_macro(self):
        result = opt.analyze_account(followers=5_000_000, platform="youtube")
        freq = result["posting_schedule"]["recommended_frequency"]
        assert freq["target_per_week"] == 2

    def test_growth_tactics_non_empty(self):
        result = opt.analyze_account(followers=1000, platform="tiktok", niche="fitness")
        assert len(result["growth_tactics"]) > 0

    def test_bio_optimization_non_empty(self):
        result = opt.analyze_account(followers=1000, platform="youtube")
        assert len(result["bio_optimization"]) > 0

    def test_score_video_idea_high(self):
        result = opt.score_video_idea(
            "5 Money Mistakes Everyone Makes", "finance",
            ["#personalfinance", "#money"]
        )
        assert result["score"] >= 60
        assert result["rating"] in ("FIRE", "GOOD")

    def test_score_video_idea_returns_dict(self):
        result = opt.score_video_idea("test title", "fitness", [])
        assert "score" in result
        assert "rating" in result
        assert "signals" in result
        assert "suggestion" in result

    def test_score_range_0_to_100(self):
        result = opt.score_video_idea(
            "SECRET Shocking Never Before Seen Ultimate Best Proven Free",
            "motivation",
            ["#motivation", "#success", "#hustle"]
        )
        assert 0 <= result["score"] <= 100


# ── Theme Page ────────────────────────────────────────────────────────

class TestThemePage:
    def test_get_all_niches_non_empty(self):
        niches = tp.get_all_niches_ranked()
        assert len(niches) >= 5

    def test_all_niches_have_required_fields(self):
        for niche in tp.get_all_niches_ranked():
            assert "niche" in niche
            assert "monetization" in niche
            assert "growth_speed" in niche
            assert "overall_score" in niche

    def test_niches_sorted_descending(self):
        niches = tp.get_all_niches_ranked()
        scores = [n["overall_score"] for n in niches]
        assert scores == sorted(scores, reverse=True)

    def test_get_niche_score_finance(self):
        result = tp.get_niche_score("finance")
        assert result is not None
        assert result["monetization"] >= 8

    def test_get_niche_score_missing(self):
        result = tp.get_niche_score("nonexistent_niche_xyz")
        assert result is None

    def test_get_niche_score_case_insensitive(self):
        assert tp.get_niche_score("FITNESS") is not None
        assert tp.get_niche_score("FINANCE") is not None

    def test_launch_playbook_has_4_phases(self):
        playbook = tp.get_launch_playbook("fitness")
        assert len(playbook["phases"]) == 4

    def test_launch_playbook_phases_have_tasks(self):
        playbook = tp.get_launch_playbook("finance")
        for phase in playbook["phases"]:
            assert len(phase["tasks"]) >= 3
            assert "goal" in phase

    def test_monetization_blueprint_5_milestones(self):
        blueprint = tp.get_monetization_blueprint()
        assert len(blueprint) == 5

    def test_monetization_blueprint_structure(self):
        for stage in tp.get_monetization_blueprint():
            assert "milestone" in stage
            assert "strategy" in stage
            assert "actions" in stage
            assert "realistic_revenue" in stage

    def test_content_sourcing_guide_structure(self):
        guide = tp.get_content_sourcing_guide()
        assert "always_do" in guide
        assert "content_sources" in guide
        assert "avoid" in guide

    def test_niche_overall_scores_in_range(self):
        for niche in tp.get_all_niches_ranked():
            assert 0 <= niche["overall_score"] <= 10

    def test_finance_monetization_highest(self):
        finance = tp.get_niche_score("finance")
        assert finance["monetization"] == 10


# ── CLI smoke tests ───────────────────────────────────────────────────

class TestCLISmoke:
    def test_cli_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trending" in result.output.lower()

    def test_info_command(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["info"])
        assert result.exit_code == 0
        assert "youtube" in result.output.lower()

    def test_theme_page_guide(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "guide"])
        assert result.exit_code == 0
        assert "converting" in result.output.lower()

    def test_theme_page_niches(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "finance" in result.output.lower()

    def test_theme_page_playbook(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "playbook", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "week" in result.output.lower()

    def test_theme_page_monetize(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "monetize"])
        assert result.exit_code == 0
        assert "follower" in result.output.lower()

    def test_optimize_command(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "optimize", "--platform", "tiktok",
            "--followers", "5000", "--niche", "fitness",
            "--avg-views", "3000", "--avg-likes", "200"
        ])
        assert result.exit_code == 0
        assert "hashtag" in result.output.lower()

    def test_score_command(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "score", "5 Money Mistakes That Keep You Broke",
            "--niche", "finance"
        ])
        assert result.exit_code == 0
        assert "score" in result.output.lower()

    def test_json_output(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        import json
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "monetize"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 5

    def test_config_set_and_get(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        monkeypatch.setattr(cfg_mod, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "config.json")
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "test_key", "test_value"])
        assert result.exit_code == 0
        assert "Set test_key" in result.output

    def test_niche_detail(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "niche-detail", "finance"])
        assert result.exit_code == 0
        assert "affiliate" in result.output.lower()

    def test_trending_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trending", "--help"])
        assert result.exit_code == 0
        assert "youtube" in result.output.lower()
        assert "tiktok" in result.output.lower()
