"""Tests for Social Optimizer harness."""

import pytest
import json
from unittest.mock import patch, MagicMock


# ── Backend unit tests ────────────────────────────────────────────────────

class TestOptimizerBackend:
    def test_add_account(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        result = optimizer_backend.add_account("tiktok", "@fituser", niche="fitness")
        assert result["platform"] == "tiktok"
        assert result["handle"] == "fituser"  # @ stripped
        assert result["niche"] == "fitness"

    def test_add_account_invalid_platform(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        with pytest.raises(ValueError, match="Unsupported platform"):
            optimizer_backend.add_account("snapchat", "user", niche="fitness")

    def test_list_accounts_empty(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "missing.json")
        accounts = optimizer_backend.list_accounts()
        assert accounts == []

    def test_add_and_list_accounts(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        optimizer_backend.add_account("tiktok", "user1", niche="fitness")
        optimizer_backend.add_account("youtube", "user2", niche="cooking")
        accounts = optimizer_backend.list_accounts()
        assert len(accounts) == 2

    def test_remove_account(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        optimizer_backend.add_account("tiktok", "removeuser", niche="fitness")
        removed = optimizer_backend.remove_account("removeuser", "tiktok")
        assert removed is True
        accounts = optimizer_backend.list_accounts()
        assert len(accounts) == 0

    def test_remove_nonexistent_account(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        removed = optimizer_backend.remove_account("nonexistent", "tiktok")
        assert removed is False

    def test_get_account(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        optimizer_backend.add_account("tiktok", "findme", niche="fitness")
        acct = optimizer_backend.get_account("findme", "tiktok")
        assert acct is not None
        assert acct["handle"] == "findme"

    def test_theme_page_playbook_structure(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import THEME_PAGE_PLAYBOOK
        assert "what_is_a_theme_page" in THEME_PAGE_PLAYBOOK
        assert "phase_1_setup" in THEME_PAGE_PLAYBOOK
        assert "phase_2_content_strategy" in THEME_PAGE_PLAYBOOK
        assert "phase_3_growth" in THEME_PAGE_PLAYBOOK
        assert "phase_4_monetization" in THEME_PAGE_PLAYBOOK
        assert "niches_with_highest_roi" in THEME_PAGE_PLAYBOOK
        assert "mistakes_to_avoid" in THEME_PAGE_PLAYBOOK
        assert "conversion_from_personal_brand" in THEME_PAGE_PLAYBOOK

    def test_theme_page_playbook_monetization(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import THEME_PAGE_PLAYBOOK
        mon = THEME_PAGE_PLAYBOOK["phase_4_monetization"]
        assert "milestones" in mon
        assert "1K followers" in mon["milestones"]
        assert "100K followers" in mon["milestones"]

    def test_generate_content_calendar_tiktok(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import generate_content_calendar
        cal = generate_content_calendar(platform="tiktok", niche="fitness", days=7, posts_per_day=2)
        assert len(cal) == 14  # 7 days * 2 posts
        assert all(c["platform"] == "tiktok" for c in cal)
        assert all(c["niche"] == "fitness" for c in cal)
        assert all(c["status"] == "planned" for c in cal)
        assert all(c["date"] for c in cal)

    def test_generate_content_calendar_youtube(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import generate_content_calendar
        cal = generate_content_calendar(platform="youtube", niche="gaming", days=7, posts_per_day=1)
        assert len(cal) == 7
        assert all("content_type" in c for c in cal)

    def test_generate_content_calendar_variety(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import generate_content_calendar
        cal = generate_content_calendar(platform="tiktok", niche="food", days=14, posts_per_day=1)
        types = [c["content_type"] for c in cal]
        # Should have variety, not all the same type
        assert len(set(types)) > 1

    def test_get_hashtag_rules_tiktok(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import get_hashtag_rules
        rules = get_hashtag_rules("tiktok")
        assert "optimal_count" in rules
        assert "placement" in rules
        assert "rules" in rules
        assert len(rules["rules"]) > 0

    def test_get_hashtag_rules_youtube(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import get_hashtag_rules
        rules = get_hashtag_rules("youtube")
        assert "optimal_count" in rules
        assert "15" in rules["optimal_count"] or "3" in rules["optimal_count"]

    def test_get_hashtag_rules_instagram(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import get_hashtag_rules
        rules = get_hashtag_rules("instagram")
        assert "rules" in rules

    def test_get_hashtag_rules_fallback(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import get_hashtag_rules
        rules = get_hashtag_rules("unknown_platform")
        # Falls back to tiktok rules
        assert "optimal_count" in rules

    def test_build_combined_report_empty(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import build_combined_report
        report = build_combined_report()
        assert "date" in report
        assert "cross_platform_tags" in report
        assert "action_items" in report
        assert len(report["action_items"]) > 0

    def test_build_combined_report_with_data(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import build_combined_report
        tt_data = {
            "trending_hashtags": [
                {"hashtag": "fitness", "appearances": 5},
                {"hashtag": "gym", "appearances": 3},
            ],
            "trending_sounds": [{"title": "Viral Song", "artist": "DJ X", "count": 10}],
        }
        yt_data = {
            "trending_tags": [
                {"tag": "fitness", "appearances": 4},
                {"tag": "workout", "appearances": 2},
            ],
            "trending_keywords": ["workout", "routine", "beginner"],
        }
        report = build_combined_report(tiktok_data=tt_data, youtube_data=yt_data, niche="fitness")
        assert "fitness" in report["cross_platform_tags"]  # shared across both
        assert report["niche"] == "fitness"
        assert len(report["action_items"]) > 0

    def test_load_save_config(self, tmp_path, monkeypatch):
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        optimizer_backend.save_config({"default_platform": "tiktok"})
        cfg = optimizer_backend.load_config()
        assert cfg["default_platform"] == "tiktok"

    def test_niches_with_highest_roi(self):
        from cli_anything.social_optimizer.utils.optimizer_backend import THEME_PAGE_PLAYBOOK
        niches = THEME_PAGE_PLAYBOOK["niches_with_highest_roi"]
        assert len(niches) >= 5
        assert any("Finance" in n or "Crypto" in n for n in niches)


# ── CLI integration tests ─────────────────────────────────────────────────

class TestCLI:
    def test_help(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Social Optimizer" in result.output

    def test_account_add(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["account", "add", "tiktok", "@testuser", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "testuser" in result.output

    def test_account_list_empty(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "empty.json")

        runner = CliRunner()
        result = runner.invoke(cli, ["account", "list"])
        assert result.exit_code == 0
        assert "No accounts" in result.output

    def test_account_list_json(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        runner = CliRunner()
        runner.invoke(cli, ["account", "add", "youtube", "mychannel", "--niche", "gaming"])
        result = runner.invoke(cli, ["--json", "account", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["handle"] == "mychannel"

    def test_theme_page_niches(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "Finance" in result.output or "Crypto" in result.output

    def test_theme_page_niches_json(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "niches", "--top", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niches" in data
        assert len(data["niches"]) == 5

    def test_theme_page_convert(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "convert"])
        assert result.exit_code == 0
        assert "Step" in result.output

    def test_theme_page_mistakes(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "mistakes"])
        assert result.exit_code == 0

    def test_content_calendar(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "content", "calendar",
            "--platform", "tiktok", "--niche", "fitness", "--days", "7"
        ])
        assert result.exit_code == 0

    def test_content_calendar_json(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "content", "calendar",
            "--platform", "tiktok", "--niche", "food", "--days", "3"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "calendar" in data
        assert data["total_posts"] == 6  # 3 days * 2 posts default for tiktok

    def test_hashtag_rules_tiktok(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtag", "rules", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_hashtag_strategy(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtag", "strategy", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_schedule_best_times(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["schedule", "best-times", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "monday" in result.output.lower()

    def test_schedule_cadence(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["schedule", "cadence", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_report_accounts_empty(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "ACCOUNTS_FILE", tmp_path / "empty.json")

        runner = CliRunner()
        result = runner.invoke(cli, ["report", "accounts"])
        assert result.exit_code == 0
        assert "No accounts" in result.output

    def test_theme_page_guide_json(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "guide"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "phase_1_setup" in data
        assert "phase_4_monetization" in data

    def test_theme_page_guide_with_niche(self):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "guide", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niche_hashtags" in data
        assert data["niche_hashtags"]["niche"] == "fitness"

    def test_config_set_get(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        from cli_anything.social_optimizer.utils import optimizer_backend
        monkeypatch.setattr(optimizer_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(optimizer_backend, "CONFIG_DIR", tmp_path)

        runner = CliRunner()
        runner.invoke(cli, ["config", "set", "default_niche", "gaming"])
        result = runner.invoke(cli, ["--json", "config", "get", "default_niche"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["value"] == "gaming"

    def test_content_calendar_to_file(self, tmp_path):
        from click.testing import CliRunner
        from cli_anything.social_optimizer.social_optimizer_cli import cli
        output_file = str(tmp_path / "calendar.json")
        runner = CliRunner()
        result = runner.invoke(cli, [
            "content", "calendar",
            "--platform", "instagram", "--niche", "beauty",
            "--days", "7", "--output", output_file,
        ])
        assert result.exit_code == 0
        assert "saved" in result.output.lower()
        with open(output_file) as f:
            data = json.load(f)
        assert "calendar" in data
        assert len(data["calendar"]) == 7
