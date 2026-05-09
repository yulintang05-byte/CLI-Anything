"""End-to-end CLI tests for social-trends.

Tests the full command pipeline via click's CliRunner.
All tests run without real API calls (no YOUTUBE_API_KEY, no TikTok creds).
"""

import json
import pytest
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def isolated_runner(tmp_path):
    """Runner that uses a temp config so tests don't pollute ~/.social_trends_config.json"""
    return CliRunner(env={"HOME": str(tmp_path)})


# ── trends ────────────────────────────────────────────────────────────────────

class TestTrendsCommands:
    def test_trends_fetch_tiktok(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["trends", "fetch", "--platform", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "tiktok" in result.output.lower() or "fitness" in result.output.lower()

    def test_trends_fetch_youtube_json(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "trends", "fetch", "--platform", "youtube", "--niche", "food"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert "niche" in data

    def test_trends_fetch_all(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "trends", "fetch", "--platform", "all", "--niche", "general"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" in data

    def test_trends_search_youtube(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "trends", "search", "gym workout", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "results" in data
        assert data["query"] == "gym workout"

    def test_trends_compare(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "trends", "compare", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommendation" in data

    def test_trends_saved_no_snapshot(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["trends", "saved", "--platform", "tiktok", "--niche", "fitness"])
        assert result.exit_code != 0 or "No saved snapshot" in result.output

    def test_trends_fetch_with_save(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["trends", "fetch", "--platform", "tiktok", "--niche", "food", "--save"])
        assert result.exit_code == 0

    def test_trends_fetch_with_region(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "trends", "fetch", "--platform", "tiktok", "--region", "GB"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["region"] == "GB"


# ── hashtags ──────────────────────────────────────────────────────────────────

class TestHashtagsCommands:
    def test_hashtags_generate_tiktok(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["hashtags", "generate", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_hashtags_generate_instagram_json(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "generate", "--niche", "food", "--platform", "instagram"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "instagram"
        assert len(data["hashtags"]) > 0
        for tag in data["hashtags"]:
            assert tag.startswith("#")

    def test_hashtags_generate_custom_count(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "generate", "--niche", "fitness", "--count", "10"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] == 10

    def test_hashtags_generate_with_custom_tags(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "generate", "--niche", "fitness", "--tags", "mygym,mytown"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert any("mygym" in t or "mytown" in t for t in data["hashtags"])

    def test_hashtags_analyse_known(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "hashtags", "analyse", "#fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["tier"] in ("mega", "large", "niche")

    def test_hashtags_analyse_without_hash(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "hashtags", "analyse", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["hashtag"] == "#fitness"

    def test_hashtags_sets(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "sets", "--niche", "beauty", "--num-sets", "3"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3

    def test_hashtags_calendar(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "calendar", "--niche", "food", "--days", "7"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 7
        assert all("date" in day for day in data)

    @pytest.mark.parametrize("platform", ["tiktok", "instagram", "youtube", "reels"])
    def test_hashtags_all_platforms(self, isolated_runner, platform):
        result = isolated_runner.invoke(
            cli, ["--json", "hashtags", "generate", "--niche", "fitness", "--platform", platform]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["count"] > 0


# ── music ─────────────────────────────────────────────────────────────────────

class TestMusicCommands:
    def test_music_trending_tiktok(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "music", "trending", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert "royalty_free_sources" in data

    def test_music_trending_youtube(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "music", "trending", "--niche", "food", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"

    def test_music_strategy(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "music", "strategy", "tutorial"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "strategy" in data
        assert "bpm_range" in data["strategy"]

    def test_music_sources(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "music", "sources"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) >= 5

    def test_music_archetypes(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "music", "archetypes", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) > 0


# ── account ───────────────────────────────────────────────────────────────────

class TestAccountCommands:
    def test_account_add(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["account", "add", "tiktok", "testcreator", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "testcreator" in result.output or "ok" in result.output.lower()

    def test_account_list_empty(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["account", "list"])
        assert result.exit_code == 0
        assert "No accounts" in result.output

    def test_account_add_then_list(self, isolated_runner):
        isolated_runner.invoke(cli, ["account", "add", "instagram", "foodlover", "--niche", "food"])
        result = isolated_runner.invoke(cli, ["--json", "account", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["platform"] == "instagram"

    def test_account_remove(self, isolated_runner):
        isolated_runner.invoke(cli, ["account", "add", "tiktok", "toremove", "--niche", "fitness"])
        result = isolated_runner.invoke(cli, ["account", "remove", "tiktok", "toremove"])
        assert result.exit_code == 0

    def test_account_optimise(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "account", "optimise", "tiktok", "--niche", "fitness", "--followers", "5000"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bio_template" in data
        assert "content_pillars" in data
        assert "posting_schedule" in data

    def test_account_optimise_all_empty(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["account", "optimise-all"])
        assert result.exit_code == 0
        assert "No accounts" in result.output

    def test_account_diagnose(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "account", "diagnose", "high views but low followers"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) > 0
        assert "fix" in data[0]

    def test_account_benchmarks(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "account", "benchmarks", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "nano (1K–10K)" in data

    def test_account_engagement_rate(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "account", "engagement-rate",
                  "--likes", "500", "--comments", "25", "--views", "10000", "--followers", "2000"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "engagement_rate_by_views" in data
        assert data["total_engagements"] == 525


# ── theme-page ────────────────────────────────────────────────────────────────

class TestThemePageCommands:
    def test_theme_niches_default(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) > 0
        for n in data:
            assert n["growth_speed"] >= 7
            assert n["monetisation"] >= 7

    def test_theme_niches_high_threshold(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "theme-page", "niches", "--min-growth", "9", "--min-monetisation", "9"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        for n in data:
            assert n["growth_speed"] >= 9

    def test_theme_score_fitness(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "score", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "overall_score" in data
        assert "verdict" in data

    def test_theme_score_unknown(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "score", "unknownniche999"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "error" in data

    def test_theme_niche_details(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "monetisation_methods" in data

    def test_theme_playbook(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "playbook"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 6

    def test_theme_convert(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "convert"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) >= 5

    def test_theme_ethics(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "theme-page", "ethics"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) >= 5
        assert all(isinstance(g, str) for g in data)

    def test_theme_content_plan(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "theme-page", "content-plan", "fitness", "--days", "7"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 7

    def test_theme_content_plan_unknown_niche(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "theme-page", "content-plan", "unknownniche999", "--days", "3"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "error" in data[0]


# ── schedule ──────────────────────────────────────────────────────────────────

class TestScheduleCommands:
    def test_schedule_generate_tiktok(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "schedule", "generate", "--platform", "tiktok", "--niche", "fitness", "--days", "7"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 7
        for day in data:
            assert "date" in day
            assert "content_pillar" in day
            assert "hashtags" in day

    def test_schedule_generate_instagram(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "schedule", "generate", "--platform", "instagram", "--niche", "food", "--days", "14"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 14

    def test_schedule_generate_youtube(self, isolated_runner):
        result = isolated_runner.invoke(
            cli, ["--json", "schedule", "generate", "--platform", "youtube", "--niche", "gaming", "--days", "7"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 7


# ── config ─────────────────────────────────────────────────────────────────────

class TestConfigCommands:
    def test_config_set_and_get(self, isolated_runner):
        isolated_runner.invoke(cli, ["config", "set", "default_niche", "fitness"])
        result = isolated_runner.invoke(cli, ["config", "get", "default_niche"])
        assert result.exit_code == 0
        assert "fitness" in result.output

    def test_config_get_missing(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["config", "get", "nonexistent_key"])
        assert result.exit_code != 0 or "not set" in result.output

    def test_config_show(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "config", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "api_keys" in data
        assert "YOUTUBE_API_KEY" in data["api_keys"]

    def test_config_show_has_setup_guide(self, isolated_runner):
        result = isolated_runner.invoke(cli, ["--json", "config", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "setup_guide" in data


# ── JSON output global flag ───────────────────────────────────────────────────

class TestJsonOutput:
    def test_json_flag_produces_valid_json(self, isolated_runner):
        """Every command with --json must produce parseable JSON."""
        commands = [
            ["--json", "trends", "fetch", "--platform", "tiktok"],
            ["--json", "hashtags", "generate", "--niche", "fitness"],
            ["--json", "music", "sources"],
            ["--json", "account", "benchmarks", "tiktok"],
            ["--json", "theme-page", "playbook"],
            ["--json", "schedule", "generate", "--days", "3"],
            ["--json", "config", "show"],
        ]
        for cmd in commands:
            result = isolated_runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Command {cmd} failed: {result.output}"
            try:
                json.loads(result.output)
            except json.JSONDecodeError as e:
                pytest.fail(f"Command {cmd} produced invalid JSON: {e}\nOutput: {result.output[:200]}")
