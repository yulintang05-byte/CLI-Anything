"""End-to-end CLI integration tests.

These tests invoke the Click CLI via CliRunner (no network required) and
verify that all command groups, sub-commands, and --json flags work correctly.
"""

import json
import pytest
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ── tiktok group ──────────────────────────────────────────────────────────────

class TestTikTokCLI:
    def test_tiktok_hashtags_default(self, runner):
        result = runner.invoke(cli, ["tiktok", "hashtags"])
        # Command should exit 0 even when network scrape falls back to seeds
        assert result.exit_code == 0

    def test_tiktok_hashtags_json(self, runner):
        result = runner.invoke(cli, ["--json", "tiktok", "hashtags", "--limit", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert data["count"] <= 5

    def test_tiktok_sounds_json(self, runner):
        result = runner.invoke(cli, ["--json", "tiktok", "sounds", "--limit", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "sounds" in data

    def test_tiktok_all_json(self, runner):
        result = runner.invoke(cli, ["--json", "tiktok", "all"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "sounds" in data


# ── hashtags group ────────────────────────────────────────────────────────────

class TestHashtagsCLI:
    def test_recommend_fitness(self, runner):
        result = runner.invoke(cli, ["hashtags", "recommend", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "#fitness" in result.output or "fitness" in result.output.lower()

    def test_recommend_json_structure(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "recommend", "--niche", "food", "--limit", "10"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "copy_paste" in data
        assert data["count"] <= 10

    def test_recommend_tiktok_platform(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "recommend",
                                     "--niche", "gaming", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"

    def test_recommend_no_universal(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "recommend",
                                     "--niche", "travel", "--no-universal"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        copy = data.get("copy_paste", "")
        assert "#fyp" not in copy

    def test_recommend_unknown_niche_exits_1(self, runner):
        result = runner.invoke(cli, ["hashtags", "recommend", "--niche", "knitting_for_cats"])
        assert result.exit_code == 1

    def test_audit_command(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "audit",
                                     "#fitness #gym #fyp #workout"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtag_count" in data
        assert data["hashtag_count"] == 4

    def test_niches_command(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niches" in data
        assert "fitness" in data["niches"]

    def test_merge_command_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "merge"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "merged_hashtags" in data


# ── music group ───────────────────────────────────────────────────────────────

class TestMusicCLI:
    def test_trending_default(self, runner):
        result = runner.invoke(cli, ["music", "trending"])
        assert result.exit_code == 0

    def test_trending_json(self, runner):
        result = runner.invoke(cli, ["--json", "music", "trending", "--limit", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tracks" in data
        assert data["count"] <= 5

    def test_trending_genre_filter(self, runner):
        result = runner.invoke(cli, ["--json", "music", "trending", "--genre", "pop"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        for t in data["tracks"]:
            assert t["genre"] == "pop"

    def test_for_content_dance(self, runner):
        result = runner.invoke(cli, ["--json", "music", "for-content", "dance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] > 0

    def test_platform_guide_tiktok(self, runner):
        result = runner.invoke(cli, ["--json", "music", "platform-guide", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "guidance" in data

    def test_genres_command(self, runner):
        result = runner.invoke(cli, ["--json", "music", "genres"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "genres" in data
        assert "pop" in data["genres"]


# ── account group ─────────────────────────────────────────────────────────────

class TestAccountCLI:
    def test_optimize_tiktok(self, runner):
        result = runner.invoke(cli, ["account", "optimize", "tiktok"])
        assert result.exit_code == 0
        assert "tiktok" in result.output.lower() or "algorithm" in result.output.lower()

    def test_optimize_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "optimize", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "algorithm_signals" in data
        assert "profile_checklist" in data

    def test_audit_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "audit", "tiktok",
                                     "--followers", "5000",
                                     "--avg-views", "250",
                                     "--posts-per-week", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "health_score" in data
        assert 0 <= data["health_score"] <= 100
        assert len(data["action_items"]) > 0

    def test_audit_invalid_platform(self, runner):
        result = runner.invoke(cli, ["account", "audit", "snapchat"])
        assert result.exit_code == 1

    def test_calendar_default(self, runner):
        result = runner.invoke(cli, ["account", "calendar"])
        assert result.exit_code == 0
        assert "Monday" in result.output

    def test_calendar_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "calendar",
                                     "--platforms", "tiktok,youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "calendar" in data
        assert len(data["calendar"]) == 7

    def test_hooks_tiktok(self, runner):
        result = runner.invoke(cli, ["account", "hooks", "tiktok"])
        assert result.exit_code == 0

    def test_platforms_command(self, runner):
        result = runner.invoke(cli, ["--json", "account", "platforms"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok" in data["platforms"]


# ── theme-page group ──────────────────────────────────────────────────────────

class TestThemePageCLI:
    def test_niches_default(self, runner):
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0

    def test_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niches" in data
        assert data["count"] > 0

    def test_niches_filter_monetisation(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "niches",
                                     "--min-monetisation", "very_high"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        for n in data["niches"]:
            assert n["monetisation_ceiling"] in ("high", "very_high")

    def test_niche_detail_finance(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "niche-detail",
                                     "finance_investing"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "viral_hooks" in data
        assert "shoutout_rate_card" in data

    def test_niche_detail_invalid(self, runner):
        result = runner.invoke(cli, ["theme-page", "niche-detail", "madeupniche"])
        assert result.exit_code == 1

    def test_playbook_command(self, runner):
        result = runner.invoke(cli, ["theme-page", "playbook"])
        assert result.exit_code == 0
        assert "Phase" in result.output or "phase" in result.output.lower()

    def test_funnel_affiliate(self, runner):
        result = runner.invoke(cli, ["theme-page", "funnel", "affiliate"])
        assert result.exit_code == 0

    def test_funnel_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "funnel", "digital_product"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "stages" in data
        assert len(data["stages"]) >= 4

    def test_sourcing_command(self, runner):
        result = runner.invoke(cli, ["theme-page", "sourcing"])
        assert result.exit_code == 0

    def test_funnels_list(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "funnels"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "affiliate" in data["funnels"]


# ── report group ──────────────────────────────────────────────────────────────

class TestReportCLI:
    def test_snapshot_json(self, runner, tmp_path):
        out_file = str(tmp_path / "snapshot.json")
        result = runner.invoke(cli, ["--json", "report", "snapshot",
                                     "--region", "US",
                                     "--niche", "fitness",
                                     "-o", out_file])
        assert result.exit_code == 0
        import os
        assert os.path.isfile(out_file)
        with open(out_file) as f:
            data = json.load(f)
        assert "tiktok" in data
        assert "youtube" in data
        assert "merged_hashtags" in data

    def test_snapshot_no_file(self, runner):
        result = runner.invoke(cli, ["--json", "report", "snapshot"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "report_type" in data


# ── global flags ──────────────────────────────────────────────────────────────

class TestGlobalFlags:
    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "social-trends" in result.output.lower() or "Social Trends" in result.output

    def test_json_flag_produces_valid_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "niches"])
        assert result.exit_code == 0
        # Must be parseable
        json.loads(result.output)
