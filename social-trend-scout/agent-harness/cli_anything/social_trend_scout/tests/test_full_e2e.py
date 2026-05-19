"""E2E tests for social-trend-scout CLI commands (no external API calls required)."""

import json
import csv
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from cli_anything.social_trend_scout.social_trend_scout_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_session(tmp_path, monkeypatch):
    """Redirect session storage to a temp directory and patch CLI-level singleton."""
    monkeypatch.setattr("cli_anything.social_trend_scout.core.session.CONFIG_DIR", tmp_path)
    from cli_anything.social_trend_scout.core.session import Session
    fresh = Session()
    monkeypatch.setattr("cli_anything.social_trend_scout.social_trend_scout_cli.SESSION", fresh)
    yield tmp_path


# ======================================================================
# Config commands
# ======================================================================

class TestConfigCommands:
    def test_config_show(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0
        assert "API keys" in result.output

    def test_config_show_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "show", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "api_keys" in data

    def test_config_set_key(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "set-key", "youtube", "MY_FAKE_KEY"])
        assert result.exit_code == 0
        assert "saved" in result.output

    def test_config_add_account(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "add-account", "tiktok", "myhandle", "fitness"])
        assert result.exit_code == 0
        assert "myhandle" in result.output

    def test_config_list_accounts_empty(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "list-accounts"])
        assert result.exit_code == 0

    def test_config_list_accounts_after_add(self, runner, isolated_session):
        runner.invoke(cli, ["config", "add-account", "tiktok", "fitpro", "fitness"])
        result = runner.invoke(cli, ["config", "list-accounts"])
        assert result.exit_code == 0
        assert "fitpro" in result.output

    def test_config_list_accounts_json(self, runner, isolated_session):
        runner.invoke(cli, ["config", "add-account", "youtube", "mychannel", "finance"])
        result = runner.invoke(cli, ["config", "list-accounts", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube" in data

    def test_config_list_accounts_filter_by_platform(self, runner, isolated_session):
        runner.invoke(cli, ["config", "add-account", "tiktok", "user1", "fitness"])
        runner.invoke(cli, ["config", "add-account", "youtube", "user2", "gaming"])
        result = runner.invoke(cli, ["config", "list-accounts", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "user1" in result.output

    def test_config_clear_cache(self, runner, isolated_session):
        result = runner.invoke(cli, ["config", "clear-cache"])
        assert result.exit_code == 0
        assert "cleared" in result.output


# ======================================================================
# Status command
# ======================================================================

class TestStatusCommand:
    def test_status_table(self, runner, isolated_session):
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "API keys" in result.output or "api" in result.output.lower()

    def test_status_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["status", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "api_keys" in data
        assert "accounts" in data


# ======================================================================
# Optimize commands (no external APIs needed)
# ======================================================================

class TestOptimizeCommands:
    def test_optimize_profile_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "profile", "tiktok"])
        assert result.exit_code == 0
        assert "Profile Optimization" in result.output

    def test_optimize_profile_with_niche(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "profile", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_optimize_profile_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "profile", "youtube", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "checklist" in data

    def test_optimize_posting_times_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "posting-times", "tiktok", "--timezone", "UTC"])
        assert result.exit_code == 0
        assert "Monday" in result.output

    def test_optimize_posting_times_youtube(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "posting-times", "youtube"])
        assert result.exit_code == 0

    def test_optimize_posting_times_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "posting-times", "instagram", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "schedule" in data

    def test_optimize_hashtags_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "hashtags", "tiktok", "fitness"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_optimize_bio_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "bio", "tiktok", "fitness", "fitguru"])
        assert result.exit_code == 0
        assert "Bio" in result.output

    def test_optimize_bio_with_cta(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "bio", "tiktok", "finance", "financeking",
                                    "--cta", "DM me for my free guide"])
        assert result.exit_code == 0

    def test_optimize_bio_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "bio", "instagram", "beauty", "beautypage", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bio" in data

    def test_optimize_engagement_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "engagement", "tiktok"])
        assert result.exit_code == 0
        assert "hook" in result.output.lower() or "algorithm" in result.output.lower()

    def test_optimize_engagement_youtube(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "engagement", "youtube"])
        assert result.exit_code == 0

    def test_optimize_audit_tiktok(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "audit", "tiktok", "fitness", "myhandle"])
        assert result.exit_code == 0
        assert "Audit" in result.output

    def test_optimize_audit_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["optimize", "audit", "youtube", "gaming", "gamechannel", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "profile_checklist" in data


# ======================================================================
# Theme-page commands (no external APIs needed)
# ======================================================================

class TestThemePageCommands:
    def test_theme_page_niches(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output
        assert "motivation" in result.output

    def test_theme_page_niches_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "niches", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "fitness" in data

    def test_theme_page_guide_fitness(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "guide", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()
        assert "checklist" in result.output.lower() or "Checklist" in result.output

    def test_theme_page_guide_motivation(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "guide", "motivation"])
        assert result.exit_code == 0

    def test_theme_page_guide_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "guide", "finance", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "monetization" in data

    def test_theme_page_content_sourcing_zero(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "content-sourcing", "--budget", "zero"])
        assert result.exit_code == 0
        assert "Repost" in result.output or "repost" in result.output

    def test_theme_page_content_sourcing_low(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "content-sourcing", "--budget", "low"])
        assert result.exit_code == 0

    def test_theme_page_content_sourcing_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "content-sourcing", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "methods" in data

    def test_theme_page_monetization_small(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "monetization", "fitness", "500"])
        assert result.exit_code == 0
        assert "Stage" in result.output or "pre-monetization" in result.output.lower()

    def test_theme_page_monetization_large(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "monetization", "finance", "200000"])
        assert result.exit_code == 0
        assert "established" in result.output.lower()

    def test_theme_page_monetization_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "monetization", "cars", "50000", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "stage" in data
        assert "estimated_monthly_revenue" in data

    def test_theme_page_platforms_fitness(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "platforms", "fitness"])
        assert result.exit_code == 0
        assert "tiktok" in result.output.lower() or "TIKTOK" in result.output

    def test_theme_page_platforms_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "platforms", "anime", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommended_order" in data

    def test_theme_page_playbook_table(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "playbook", "motivation"])
        assert result.exit_code == 0
        assert "Playbook" in result.output

    def test_theme_page_playbook_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["theme-page", "playbook", "gaming", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tools" in data

    def test_theme_page_playbook_saves_to_file(self, runner, isolated_session):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["theme-page", "playbook", "food", "--output", "playbook.json"])
            assert result.exit_code == 0
            assert Path("playbook.json").exists()
            data = json.loads(Path("playbook.json").read_text())
            assert "niche_guide" in data


# ======================================================================
# Calendar commands (no external APIs needed)
# ======================================================================

class TestCalendarCommands:
    def test_calendar_generate_7_days(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "generate", "fitness", "tiktok", "--days", "7"])
        assert result.exit_code == 0
        assert "calendar" in result.output.lower() or "Calendar" in result.output

    def test_calendar_generate_30_days(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "generate", "motivation", "instagram", "--days", "30"])
        assert result.exit_code == 0

    def test_calendar_generate_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "generate", "finance", "youtube", "--days", "7", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["calendar"]) == 7
        assert data["total_posts"] == 7

    def test_calendar_generate_csv(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "generate", "cars", "instagram", "--days", "7", "--csv"])
        assert result.exit_code == 0
        rows = [r for r in csv.reader(result.output.splitlines()) if r]
        assert rows[0][0] == "Date"
        assert len(rows) == 8  # header + 7 days

    def test_calendar_generate_saves_json(self, runner, isolated_session):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["calendar", "generate", "anime", "tiktok",
                                         "--days", "14", "--output", "cal.json"])
            assert result.exit_code == 0
            assert Path("cal.json").exists()
            data = json.loads(Path("cal.json").read_text())
            assert len(data["calendar"]) == 14

    def test_calendar_generate_saves_csv(self, runner, isolated_session):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["calendar", "generate", "food", "instagram",
                                         "--days", "7", "--output", "cal.csv"])
            assert result.exit_code == 0
            assert Path("cal.csv").exists()
            rows = [r for r in csv.reader(Path("cal.csv").read_text().splitlines()) if r]
            assert rows[0][0] == "Date"

    def test_calendar_generate_multiple_posts_per_day(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "generate", "fitness", "tiktok",
                                     "--days", "7", "--posts-per-day", "3", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total_posts"] == 21
        for day in data["calendar"]:
            assert len(day["posts"]) == 3

    def test_calendar_sprint(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "sprint", "motivation", "tiktok"])
        assert result.exit_code == 0
        assert "Sprint" in result.output or "sprint" in result.output.lower()

    def test_calendar_sprint_json(self, runner, isolated_session):
        result = runner.invoke(cli, ["calendar", "sprint", "gaming", "youtube", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["week_sprint"]) == 7
        assert data["total_posts"] == 14


# ======================================================================
# Trends commands — fail gracefully without API key
# ======================================================================

class TestTrendsGracefulFailure:
    def test_trends_youtube_no_key_exits_with_error(self, runner, isolated_session):
        result = runner.invoke(cli, ["trends", "youtube"])
        assert result.exit_code != 0 or "API key" in result.output

    def test_trends_tiktok_hashtags_fallback(self, runner, isolated_session):
        # Should return fallback data or helpful error without crashing
        result = runner.invoke(cli, ["trends", "tiktok", "--type", "hashtags"])
        # Either succeeds with fallback data or exits cleanly with an install hint
        assert result.exit_code in (0, 1)

    def test_trends_cross_platform_no_key(self, runner, isolated_session):
        result = runner.invoke(cli, ["trends", "cross-platform"])
        assert "API key" in result.output or result.exit_code != 0
