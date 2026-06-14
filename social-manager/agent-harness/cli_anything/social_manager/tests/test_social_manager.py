"""Test suite for CLI-Anything Social Manager."""
import json
import pytest
from click.testing import CliRunner

from cli_anything.social_manager.social_manager_cli import cli
from cli_anything.social_manager.core import trends, optimizer, theme_pages
from cli_anything.social_manager.utils import tiktok_client, config


# ─── Trends ───────────────────────────────────────────────────────────────────

class TestTikTokTrends:
    def test_fallback_hashtags_structure(self):
        data = tiktok_client._fallback_trending_hashtags()
        assert len(data) > 0
        for h in data:
            assert "hashtag" in h
            assert h["hashtag"].startswith("#")
            assert "view_count" in h
            assert isinstance(h["view_count"], int)

    def test_fallback_sounds_structure(self):
        data = tiktok_client._fallback_trending_sounds()
        assert len(data) > 0
        for s in data:
            assert "title" in s
            assert "artist" in s
            assert "usage_count" in s

    def test_get_tiktok_trends_shape(self):
        data = trends.get_tiktok_trends(region="US", period=7, limit=10)
        assert data["platform"] == "TikTok"
        assert "trending_hashtags" in data
        assert "trending_sounds" in data
        assert len(data["trending_hashtags"]) > 0

    def test_tiktok_trends_region(self):
        data = trends.get_tiktok_trends(region="UK")
        assert data["region"] == "UK"


class TestYouTubeTrends:
    def test_fallback_when_no_api_key(self):
        data = trends.get_youtube_trends(region="US", api_key=None)
        assert data["platform"] == "YouTube"
        assert "top_hashtags" in data
        assert len(data["top_hashtags"]) > 0

    def test_fallback_hashtags_are_tuples(self):
        data = trends.get_youtube_trends(region="US", api_key=None)
        for tag, count in data["top_hashtags"]:
            assert tag.startswith("#")
            assert isinstance(count, int)

    def test_trend_report_combines_platforms(self):
        data = trends.generate_trend_report(region="US")
        assert "tiktok" in data
        assert "youtube" in data
        assert "cross_platform_trends" in data
        assert len(data["cross_platform_trends"]) > 0
        assert "report_date" in data


# ─── Optimizer ────────────────────────────────────────────────────────────────

class TestOptimizer:
    def test_hashtag_strategy_known_niche(self):
        data = optimizer.get_hashtag_strategy("finance", "tiktok")
        assert data["niche"] == "finance"
        assert "tag_groups" in data
        assert "recommended_set" in data
        assert len(data["recommended_set"]) >= 4
        for tag in data["recommended_set"]:
            assert tag.startswith("#")

    def test_hashtag_strategy_unknown_niche(self):
        data = optimizer.get_hashtag_strategy("cooking", "tiktok")
        assert "recommended_set" in data
        assert len(data["recommended_set"]) > 0

    def test_posting_schedule_tiktok(self):
        data = optimizer.get_posting_schedule("tiktok")
        assert data["platform"] == "tiktok"
        assert "posting_windows_est" in data
        assert len(data["posting_windows_est"]) == 7

    def test_posting_schedule_youtube(self):
        data = optimizer.get_posting_schedule("youtube")
        assert len(data["posting_windows_est"]) == 7

    def test_profile_audit_structure(self):
        data = optimizer.generate_profile_audit("tiktok", "@testpage", "finance")
        assert "profile_checklist" in data
        assert "quick_wins" in data
        assert len(data["profile_checklist"]) >= 5
        assert len(data["quick_wins"]) >= 3


# ─── Theme Pages ──────────────────────────────────────────────────────────────

class TestThemePages:
    def test_niche_recommendations(self):
        niches = theme_pages.get_niche_recommendations()
        assert len(niches) >= 5
        for n in niches:
            assert "niche" in n
            assert "monetization" in n
            assert "platforms" in n

    def test_setup_guide_has_all_steps(self):
        guide = theme_pages.get_setup_guide()
        assert "steps" in guide
        assert len(guide["steps"]) >= 6
        assert "monetization" in guide
        assert "tools" in guide

    def test_monetization_methods(self):
        methods = theme_pages.get_monetization_breakdown()
        assert len(methods) >= 5
        for m in methods:
            assert "method" in m
            assert "income_potential" in m
            assert "timeline" in m

    def test_tools_stack_categories(self):
        tools = theme_pages.get_tools_stack()
        assert "content_discovery" in tools
        assert "content_creation" in tools
        assert "scheduling" in tools
        assert "analytics" in tools
        assert "monetization" in tools


# ─── Config ───────────────────────────────────────────────────────────────────

class TestConfig:
    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(config, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        config.save_config({"test_key": "test_value"})
        assert config.get("test_key") == "test_value"

    def test_add_and_load_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(config, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        config.add_account("tiktok", "@testpage", "finance", "test")
        accounts = config.load_accounts()
        assert len(accounts) == 1
        assert accounts[0]["handle"] == "@testpage"

    def test_duplicate_account_replaced(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(config, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        config.add_account("tiktok", "@testpage", "finance")
        config.add_account("tiktok", "@testpage", "fitness")
        accounts = config.load_accounts()
        assert len(accounts) == 1
        assert accounts[0]["niche"] == "fitness"


# ─── CLI Integration ──────────────────────────────────────────────────────────

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Social Manager" in result.output

    def test_trends_tiktok_json(self):
        result = self.runner.invoke(cli, ["--json", "trends", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "TikTok"
        assert "trending_hashtags" in data

    def test_trends_youtube_json(self):
        result = self.runner.invoke(cli, ["--json", "trends", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "YouTube"

    def test_trends_report_json(self):
        result = self.runner.invoke(cli, ["--json", "trends", "report"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok" in data
        assert "youtube" in data

    def test_optimize_hashtags_json(self):
        result = self.runner.invoke(cli, ["--json", "optimize", "hashtags", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommended_set" in data
        assert len(data["recommended_set"]) > 0

    def test_optimize_schedule_json(self):
        result = self.runner.invoke(cli, ["--json", "optimize", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "posting_windows_est" in data

    def test_optimize_profile_json(self):
        result = self.runner.invoke(cli, ["--json", "optimize", "profile",
                                          "--platform", "tiktok",
                                          "--handle", "@mypage",
                                          "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "profile_checklist" in data

    def test_theme_niches_json(self):
        result = self.runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_theme_monetize_json(self):
        result = self.runner.invoke(cli, ["--json", "theme", "monetize"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert any(m["method"] == "Affiliate Marketing" for m in data)

    def test_theme_tools_json(self):
        result = self.runner.invoke(cli, ["--json", "theme", "tools"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "content_discovery" in data

    def test_accounts_add_and_list(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                "accounts", "add",
                "--platform", "tiktok",
                "--handle", "@testpage",
                "--niche", "finance",
            ])
            assert result.exit_code == 0

    def test_config_set_and_show(self):
        result = self.runner.invoke(cli, ["config", "set", "test_key", "test_val"])
        assert result.exit_code == 0
