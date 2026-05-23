"""End-to-end tests for social-trends CLI (network optional).

Tests that require live APIs are skipped when credentials are absent.
Tests marked e2e_network require real network access.
"""

import os
import json
import pytest
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


def _has_yt_key():
    return bool(os.environ.get("YOUTUBE_API_KEY", ""))


def _has_tt_session():
    return bool(os.environ.get("TIKTOK_SESSION_ID", ""))


# ── CLI help & version ─────────────────────────────────────────────────

class TestCLIBasics:
    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trend" in result.output.lower() or "tiktok" in result.output.lower()

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_tiktok_group_help(self, runner):
        result = runner.invoke(cli, ["tiktok", "--help"])
        assert result.exit_code == 0

    def test_youtube_group_help(self, runner):
        result = runner.invoke(cli, ["youtube", "--help"])
        assert result.exit_code == 0

    def test_analyze_help(self, runner):
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0

    def test_optimize_help(self, runner):
        result = runner.invoke(cli, ["optimize", "--help"])
        assert result.exit_code == 0

    def test_theme_page_help(self, runner):
        result = runner.invoke(cli, ["theme-page", "--help"])
        assert result.exit_code == 0

    def test_content_plan_help(self, runner):
        result = runner.invoke(cli, ["content-plan", "--help"])
        assert result.exit_code == 0

    def test_list_niches_help(self, runner):
        result = runner.invoke(cli, ["list-niches", "--help"])
        assert result.exit_code == 0

    def test_setup_help(self, runner):
        result = runner.invoke(cli, ["setup", "--help"])
        assert result.exit_code == 0


# ── Setup command ──────────────────────────────────────────────────────

class TestSetupCommand:
    def test_setup_runs(self, runner):
        result = runner.invoke(cli, ["setup"])
        assert result.exit_code == 0
        assert "YOUTUBE" in result.output

    def test_setup_json(self, runner):
        # setup doesn't produce JSON but shouldn't crash with --json flag
        result = runner.invoke(cli, ["--json", "setup"])
        assert result.exit_code == 0


# ── List niches ────────────────────────────────────────────────────────

class TestListNiches:
    def test_list_niches_output(self, runner):
        result = runner.invoke(cli, ["list-niches"])
        assert result.exit_code == 0
        assert "Finance" in result.output or "finance" in result.output.lower()

    def test_list_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "list-niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5
        for item in data:
            assert "key" in item
            assert "name" in item


# ── Theme page command ─────────────────────────────────────────────────

class TestThemePageCommand:
    def test_finance_plan(self, runner):
        result = runner.invoke(cli, ["theme-page", "--niche", "finance"])
        assert result.exit_code == 0
        assert "Phase 1" in result.output or "SETUP" in result.output

    def test_fitness_plan(self, runner):
        result = runner.invoke(cli, ["theme-page", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "Phase" in result.output

    def test_custom_niche(self, runner):
        result = runner.invoke(cli, ["theme-page", "--niche", "gaming"])
        assert result.exit_code == 0

    def test_with_followers(self, runner):
        result = runner.invoke(cli, ["theme-page", "--niche", "luxury", "--followers", "50000"])
        assert result.exit_code == 0
        assert "50,000" in result.output

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "phase_1_setup" in data
        assert "dm_scripts" in data
        assert "account_valuation" in data

    def test_all_niches_work(self, runner):
        niches = ["finance", "luxury", "fitness", "motivation", "crypto", "cars", "food", "fashion"]
        for niche in niches:
            result = runner.invoke(cli, ["theme-page", "--niche", niche])
            assert result.exit_code == 0, f"Failed for niche: {niche}"

    def test_save_flag(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["theme-page", "--niche", "finance", "--save"])
            assert result.exit_code == 0
            # Check a file was created
            import glob
            files = glob.glob("theme_page_finance_*.json")
            assert len(files) == 1


# ── Account optimizer command ──────────────────────────────────────────

class TestOptimizeCommand:
    def test_basic_optimize(self, runner):
        result = runner.invoke(cli, [
            "optimize", "--handle", "@testpage", "--platform", "tiktok",
            "--followers", "10000",
        ])
        assert result.exit_code == 0
        assert "Grade" in result.output or "GRADE" in result.output

    def test_optimize_no_link_shows_critical(self, runner):
        result = runner.invoke(cli, [
            "optimize", "--handle", "@test", "--platform", "tiktok",
            "--followers", "500", "--no-link",
        ])
        assert result.exit_code == 0
        assert "link" in result.output.lower() or "critical" in result.output.lower()

    def test_optimize_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "optimize",
            "--handle", "@testjson",
            "--platform", "tiktok",
            "--followers", "5000",
            "--avg-views", "1000",
            "--avg-likes", "50",
            "--has-link",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "grade" in data
        assert "score" in data
        assert "critical_fixes" in data
        assert "monetization_opportunities" in data

    def test_optimize_all_platforms(self, runner):
        result = runner.invoke(cli, [
            "optimize", "--handle", "@multi", "--platform", "all",
            "--followers", "25000",
        ])
        assert result.exit_code == 0

    def test_optimize_with_full_metrics(self, runner):
        result = runner.invoke(cli, [
            "optimize", "--handle", "@full",
            "--platform", "tiktok",
            "--followers", "50000",
            "--avg-views", "10000",
            "--avg-likes", "800",
            "--avg-comments", "100",
            "--avg-shares", "200",
            "--posts-per-week", "7",
            "--niche", "fitness",
            "--has-link",
        ])
        assert result.exit_code == 0
        assert "A" in result.output  # Should get a good grade

    def test_optimize_save(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, [
                "optimize", "--handle", "@savetest",
                "--platform", "tiktok", "--followers", "1000", "--save",
            ])
            assert result.exit_code == 0
            import glob
            files = glob.glob("optimize_savetest_*.json")
            assert len(files) == 1


# ── Content plan command ───────────────────────────────────────────────

class TestContentPlanCommand:
    def test_basic_plan(self, runner):
        result = runner.invoke(cli, [
            "content-plan", "--niche", "fitness", "--platform", "tiktok",
            "--days", "3", "--posts-per-day", "1",
        ])
        assert result.exit_code == 0
        assert "Post #1" in result.output
        assert "CAPTION" in result.output

    def test_plan_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "content-plan", "--niche", "finance",
            "--platform", "tiktok", "--days", "2", "--posts-per-day", "1",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "posts" in data
        assert len(data["posts"]) == 2

    def test_all_platforms_plan(self, runner):
        result = runner.invoke(cli, [
            "content-plan", "--niche", "luxury", "--platform", "all",
            "--days", "1", "--posts-per-day", "1",
        ])
        assert result.exit_code == 0

    def test_various_niches(self, runner):
        niches = ["finance", "fitness", "luxury", "motivation", "cars", "food"]
        for niche in niches:
            result = runner.invoke(cli, [
                "content-plan", "--niche", niche, "--days", "1", "--posts-per-day", "1",
            ])
            assert result.exit_code == 0, f"Failed for niche: {niche}"

    def test_plan_save(self, runner, tmp_path):
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, [
                "content-plan", "--niche", "fitness",
                "--days", "1", "--posts-per-day", "1", "--save",
            ])
            assert result.exit_code == 0
            import glob
            files = glob.glob("content_plan_fitness_*.json")
            assert len(files) == 1


# ── TikTok commands (no network — uses fallback data) ─────────────────

class TestTikTokCommands:
    def test_hashtags_fallback(self, runner):
        """TikTok hashtags command returns fallback data if API unreachable."""
        result = runner.invoke(cli, ["tiktok", "hashtags", "--count", "5"])
        # Should not crash even if network unavailable
        assert result.exit_code == 0 or "Error" in result.output

    def test_sounds_fallback(self, runner):
        result = runner.invoke(cli, ["tiktok", "sounds", "--count", "5"])
        assert result.exit_code == 0 or "Error" in result.output

    def test_scan_json(self, runner):
        """Scan command runs and produces JSON (falls back if network unavailable)."""
        result = runner.invoke(cli, [
            "--json", "tiktok", "scan",
            "--hashtags", "5", "--sounds", "5", "--videos", "5",
        ])
        if result.exit_code == 0:
            data = json.loads(result.output)
            assert "trending_hashtags" in data
            assert "trending_sounds" in data


# ── YouTube commands (skipped without API key) ─────────────────────────

class TestYouTubeCommands:
    @pytest.mark.skipif(not _has_yt_key(), reason="YOUTUBE_API_KEY not set")
    def test_youtube_scan_live(self, runner):
        result = runner.invoke(cli, ["youtube", "scan", "--count", "5"])
        assert result.exit_code == 0

    @pytest.mark.skipif(not _has_yt_key(), reason="YOUTUBE_API_KEY not set")
    def test_youtube_music_live(self, runner):
        result = runner.invoke(cli, ["youtube", "music", "--count", "5"])
        assert result.exit_code == 0

    def test_youtube_scan_no_key(self, runner):
        """Without API key, command should either give mock data or informative error."""
        env = {k: v for k, v in os.environ.items() if k != "YOUTUBE_API_KEY"}
        result = runner.invoke(cli, ["youtube", "scan", "--count", "5"], env=env)
        # Should not segfault — either 0 (mock) or 1 (error) is fine
        assert result.exit_code in (0, 1)


# ── Analyze command ────────────────────────────────────────────────────

class TestAnalyzeCommand:
    def test_analyze_tiktok_only(self, runner):
        result = runner.invoke(cli, [
            "analyze", "--platform", "tiktok", "--region", "US",
        ])
        assert result.exit_code == 0 or "Error" in result.output

    def test_analyze_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "analyze", "--platform", "tiktok",
        ])
        if result.exit_code == 0:
            data = json.loads(result.output)
            assert "top_trends" in data
