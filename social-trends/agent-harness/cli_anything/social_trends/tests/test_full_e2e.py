"""End-to-end CLI tests using Click test runner."""

import json
import pytest
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def runner_with_json():
    return CliRunner()


def invoke(runner, *args, expect_exit_code=0):
    result = runner.invoke(cli, list(args))
    assert result.exit_code == expect_exit_code, (
        f"Exit code {result.exit_code} != {expect_exit_code}\nOutput: {result.output}\nException: {result.exception}"
    )
    return result


def invoke_json(runner, *args):
    result = runner.invoke(cli, ["--json"] + list(args))
    assert result.exit_code == 0, f"CLI error: {result.output}"
    return json.loads(result.output)


# ===========================================================================
# Root CLI
# ===========================================================================

class TestRootCLI:
    def test_help(self, runner):
        result = invoke(runner, "--help")
        assert "social" in result.output.lower() or "trends" in result.output.lower()

    def test_version_or_no_error(self, runner):
        result = runner.invoke(cli, [])
        assert result.exit_code in (0, 2)


# ===========================================================================
# trends commands
# ===========================================================================

class TestTrendsCommands:
    def test_trends_tiktok(self, runner):
        result = invoke(runner, "trends", "tiktok", "--limit", "3")
        assert "tiktok" in result.output.lower()

    def test_trends_youtube(self, runner):
        result = invoke(runner, "trends", "youtube", "--limit", "3")
        assert "youtube" in result.output.lower()

    def test_trends_all(self, runner):
        result = invoke(runner, "trends", "all", "--limit", "3")
        assert len(result.output) > 0

    def test_trends_tiktok_json(self, runner):
        data = invoke_json(runner, "trends", "tiktok", "--limit", "3")
        assert data["platform"] == "tiktok"
        assert "videos" in data
        assert "top_hashtags" in data

    def test_trends_youtube_json(self, runner):
        data = invoke_json(runner, "trends", "youtube", "--limit", "3")
        assert data["platform"] == "youtube"
        assert "videos" in data

    def test_trends_youtube_category(self, runner):
        result = invoke(runner, "trends", "youtube", "--category", "music", "--limit", "3")
        assert result.exit_code == 0

    def test_trends_search(self, runner):
        result = invoke(runner, "trends", "search", "fitness tips")
        assert "fitness" in result.output.lower() or "results" in result.output.lower()

    def test_trends_hashtag(self, runner):
        result = invoke(runner, "trends", "hashtag", "#fitness")
        assert result.exit_code == 0

    def test_trends_tiktok_region(self, runner):
        data = invoke_json(runner, "trends", "tiktok", "--region", "GB", "--limit", "3")
        assert data["region"] == "GB"


# ===========================================================================
# hashtags commands
# ===========================================================================

class TestHashtagsCommands:
    def test_hashtags_niche_fitness(self, runner):
        result = invoke(runner, "hashtags", "niche", "fitness")
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_hashtags_niche_json(self, runner):
        data = invoke_json(runner, "hashtags", "niche", "fitness")
        assert "hashtags" in data
        assert len(data["hashtags"]) > 0

    def test_hashtags_niche_luxury(self, runner):
        data = invoke_json(runner, "hashtags", "niche", "luxury")
        assert "hashtags" in data

    def test_hashtags_recommend(self, runner):
        result = invoke(runner, "hashtags", "recommend", "morning workout routine")
        assert result.exit_code == 0

    def test_hashtags_recommend_json(self, runner):
        data = invoke_json(runner, "hashtags", "recommend", "morning workout routine")
        assert "recommended_hashtags" in data
        assert "copy_paste" in data

    def test_hashtags_analyze(self, runner):
        result = invoke(runner, "hashtags", "analyze", "#fyp", "#fitness", "#gymtok")
        assert result.exit_code == 0

    def test_hashtags_analyze_json(self, runner):
        data = invoke_json(runner, "hashtags", "analyze", "#fyp", "#fitness", "#fyp", "--niche", "fitness")
        assert "ranked_hashtags" in data
        assert "optimal_set" in data
        top = data["ranked_hashtags"][0]
        assert top["hashtag"] == "#fyp"
        assert top["frequency"] == 2


# ===========================================================================
# music commands
# ===========================================================================

class TestMusicCommands:
    def test_music_trending(self, runner):
        result = invoke(runner, "music", "trending")
        assert result.exit_code == 0

    def test_music_trending_json(self, runner):
        data = invoke_json(runner, "music", "trending", "--limit", "5")
        assert "tracks" in data
        assert "usage_tips" in data
        assert len(data["tracks"]) <= 5

    def test_music_trending_genre_filter(self, runner):
        data = invoke_json(runner, "music", "trending", "--genre", "pop")
        for track in data["tracks"]:
            assert "pop" in track["genre"].lower()

    def test_music_for_niche(self, runner):
        result = invoke(runner, "music", "for-niche", "fitness")
        assert result.exit_code == 0

    def test_music_for_niche_json(self, runner):
        data = invoke_json(runner, "music", "for-niche", "luxury")
        assert "recommended_tracks" in data
        assert "pro_tip" in data

    def test_music_trending_all_platforms(self, runner):
        data = invoke_json(runner, "music", "trending", "--platform", "all")
        assert "tracks" in data


# ===========================================================================
# optimize commands
# ===========================================================================

class TestOptimizeCommands:
    def test_optimize_schedule_tiktok(self, runner):
        result = invoke(runner, "optimize", "schedule", "--platform", "tiktok")
        assert result.exit_code == 0

    def test_optimize_schedule_json(self, runner):
        data = invoke_json(runner, "optimize", "schedule", "--platform", "tiktok")
        assert "weekly_schedule" in data
        assert len(data["weekly_schedule"]) == 7

    def test_optimize_bio(self, runner):
        result = invoke(runner, "optimize", "bio", "--platform", "tiktok", "--niche", "fitness")
        assert result.exit_code == 0

    def test_optimize_bio_json(self, runner):
        data = invoke_json(runner, "optimize", "bio", "--platform", "tiktok", "--niche", "fitness", "--followers", "5000")
        assert "bio" in data
        assert 0 <= data["optimization_score"] <= 100

    def test_optimize_playbook(self, runner):
        result = invoke(runner, "optimize", "playbook", "5000")
        assert result.exit_code == 0

    def test_optimize_playbook_json(self, runner):
        data = invoke_json(runner, "optimize", "playbook", "5000")
        assert "daily_actions" in data
        assert "Growth" in data["label"] or "1K-10K" in data["label"]

    def test_optimize_audit(self, runner):
        result = invoke(runner, "optimize", "audit",
                        "--platform", "tiktok", "--username", "@test",
                        "--followers", "5000", "--avg-views", "2000", "--avg-likes", "100")
        assert result.exit_code == 0

    def test_optimize_audit_json(self, runner):
        data = invoke_json(runner, "optimize", "audit",
                           "--platform", "tiktok", "--username", "@test",
                           "--followers", "10000", "--avg-views", "50000", "--avg-likes", "3000")
        assert "health_score" in data
        assert "metrics" in data
        assert "recommendations" in data

    def test_optimize_all_accounts_empty(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["optimize", "all-accounts"])
            assert result.exit_code == 0


# ===========================================================================
# themepage commands
# ===========================================================================

class TestThemePageCommands:
    def test_themepage_niches_list(self, runner):
        result = invoke(runner, "themepage", "niches")
        assert result.exit_code == 0

    def test_themepage_niches_json(self, runner):
        data = invoke_json(runner, "themepage", "niches")
        assert "niches" in data
        assert len(data["niches"]) > 0

    def test_themepage_niche_specific(self, runner):
        data = invoke_json(runner, "themepage", "niches", "--niche", "luxury")
        assert "monetization" in data

    def test_themepage_niche_invalid(self, runner):
        data = invoke_json(runner, "themepage", "niches", "--niche", "invalidniche12345")
        assert "error" in data

    def test_themepage_checklist(self, runner):
        result = invoke(runner, "themepage", "checklist")
        assert result.exit_code == 0

    def test_themepage_checklist_json(self, runner):
        data = invoke_json(runner, "themepage", "checklist")
        assert "checklist" in data
        assert len(data["checklist"]) >= 5

    def test_themepage_checklist_phase(self, runner):
        data = invoke_json(runner, "themepage", "checklist", "--phase", "1")
        assert "phase" in data

    def test_themepage_content_methods(self, runner):
        result = invoke(runner, "themepage", "content-methods")
        assert result.exit_code == 0

    def test_themepage_content_methods_json(self, runner):
        data = invoke_json(runner, "themepage", "content-methods")
        assert "methods" in data
        assert len(data["methods"]) > 0

    def test_themepage_pitch(self, runner):
        result = invoke(runner, "themepage", "pitch",
                        "--handle", "@testpage", "--brand", "Nike",
                        "--niche", "fitness", "--followers", "50000",
                        "--name", "Alex", "--email", "alex@test.com")
        assert result.exit_code == 0

    def test_themepage_pitch_json(self, runner):
        data = invoke_json(runner, "themepage", "pitch",
                           "--handle", "@testpage", "--brand", "Adidas",
                           "--niche", "fitness", "--followers", "50000",
                           "--name", "Alex", "--email", "alex@test.com")
        assert "pitch_email" in data
        assert "Adidas" in data["pitch_email"]
        assert "@testpage" in data["pitch_email"]


# ===========================================================================
# config commands
# ===========================================================================

class TestConfigCommands:
    def test_config_show(self, runner):
        result = invoke(runner, "config", "show")
        assert result.exit_code == 0

    def test_config_show_json(self, runner):
        data = invoke_json(runner, "config", "show")
        assert "default_region" in data

    def test_config_set_and_show(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["config", "set", "default_region", "GB"])
            assert result.exit_code == 0


# ===========================================================================
# accounts commands
# ===========================================================================

class TestAccountsCommands:
    def test_accounts_list_empty(self, runner):
        result = invoke(runner, "accounts", "list")
        assert result.exit_code == 0

    def test_accounts_list_json(self, runner):
        result = runner.invoke(cli, ["--json", "accounts", "list"])
        assert result.exit_code == 0


# ===========================================================================
# JSON output mode
# ===========================================================================

class TestJSONOutputMode:
    def test_all_trend_commands_produce_valid_json(self, runner):
        commands = [
            ["trends", "tiktok", "--limit", "2"],
            ["trends", "youtube", "--limit", "2"],
            ["hashtags", "niche", "fitness"],
            ["music", "trending", "--limit", "3"],
            ["optimize", "schedule"],
            ["optimize", "playbook", "1000"],
            ["themepage", "niches"],
            ["themepage", "checklist"],
        ]
        for cmd in commands:
            result = runner.invoke(cli, ["--json"] + cmd)
            assert result.exit_code == 0, f"Failed: {cmd} — {result.output}"
            try:
                data = json.loads(result.output)
                assert isinstance(data, dict), f"Not a dict for: {cmd}"
            except json.JSONDecodeError as e:
                pytest.fail(f"Invalid JSON for {cmd}: {e}\nOutput: {result.output[:200]}")
