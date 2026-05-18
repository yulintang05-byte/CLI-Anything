"""End-to-end CLI tests using Click's test runner (no network required)."""

import json
import pytest
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, args, json_mode=True):
    """Helper: invoke CLI and return (exit_code, parsed_json_or_output)."""
    full_args = (["--json"] if json_mode else []) + args
    result = runner.invoke(cli, full_args, catch_exceptions=False)
    if json_mode and result.output.strip():
        try:
            return result.exit_code, json.loads(result.output.strip())
        except json.JSONDecodeError:
            return result.exit_code, result.output
    return result.exit_code, result.output


# ── trends commands ───────────────────────────────────────────────────

class TestTrendsTikTokMock:
    def test_tiktok_hashtags_only(self, runner):
        code, data = invoke(runner, ["--mock", "trends", "tiktok", "--hashtags-only", "--limit", "5"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) == 5
        assert data[0]["hashtag"].startswith("#")

    def test_tiktok_music_only(self, runner):
        code, data = invoke(runner, ["--mock", "trends", "tiktok", "--music-only", "--limit", "3"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) == 3

    def test_trends_hashtags_niche(self, runner):
        code, data = invoke(runner, ["trends", "hashtags", "--niche", "fitness", "--platform", "both", "--limit", "15"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) > 0


class TestTrendsMusicCommands:
    def test_music_tiktok_mock(self, runner):
        code, data = invoke(runner, ["--mock", "trends", "music", "--platform", "tiktok", "--limit", "5"])
        assert code == 0
        assert isinstance(data, list)


class TestHashtagSuggestions:
    def test_hashtag_suggestions_all_niches(self, runner):
        for niche in ["fitness", "beauty", "finance", "food", "gaming"]:
            code, data = invoke(runner, ["trends", "hashtags", "--niche", niche, "--platform", "tiktok"])
            assert code == 0, f"Failed for niche: {niche}"
            assert isinstance(data, list)
            assert len(data) > 0


# ── account commands ──────────────────────────────────────────────────

class TestAccountCommands:
    def test_add_and_list(self, runner):
        runner.invoke(cli, ["account", "add", "tiktok", "@testpage", "--niche", "fitness"])
        code, data = invoke(runner, ["account", "list"])
        assert code == 0

    def test_account_audit(self, runner):
        code, data = invoke(runner, [
            "account", "audit", "tiktok", "@mypage",
            "--niche", "fitness",
            "--followers", "12000",
            "--avg-views", "8000",
            "--avg-likes", "640",
            "--posts-per-week", "7",
        ])
        assert code == 0
        assert isinstance(data, dict)
        assert "score" in data
        assert "grade" in data
        assert 0 <= data["score"] <= 100
        assert data["grade"] in ("A", "B", "C", "D", "F")

    def test_account_audit_with_bio(self, runner):
        code, data = invoke(runner, [
            "account", "audit", "tiktok", "@beautypage",
            "--niche", "beauty",
            "--followers", "50000",
            "--avg-views", "15000",
            "--avg-likes", "1200",
            "--bio", "Beauty tips daily | skincare routine | Follow for glow ups",
        ])
        assert code == 0
        assert "wins" in data

    def test_posting_times(self, runner):
        code, data = invoke(runner, ["account", "posting-times", "tiktok", "--niche", "fitness"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) > 0
        assert "day" in data[0]
        assert "label" in data[0]

    def test_bio_suggest(self, runner):
        code, data = invoke(runner, [
            "account", "bio-suggest", "tiktok",
            "--niche", "fitness",
            "--handle", "fitdaily",
        ])
        assert code == 0
        assert "bio_template" in data
        assert "tips" in data

    def test_engagement_rate(self, runner):
        code, data = invoke(runner, [
            "account", "engagement-rate",
            "--views", "10000",
            "--likes", "1000",
            "--comments", "100",
        ])
        assert code == 0
        assert "likes_rate" in data
        assert data["likes_rate"] == 10.0
        assert data["rating"] == "excellent"

    def test_account_hashtags(self, runner):
        code, data = invoke(runner, [
            "account", "hashtags", "finance",
            "--platform", "tiktok",
            "--count", "20",
        ])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) == 20


# ── theme commands ────────────────────────────────────────────────────

class TestThemeCommands:
    def test_niche_guide_fitness(self, runner):
        code, data = invoke(runner, ["theme", "niche-guide", "fitness"])
        assert code == 0
        assert data["niche"] == "fitness"
        assert "content_pillars" in data
        assert "viral_formats" in data
        assert "monetization_paths" in data
        assert len(data["quick_start_steps"]) > 0

    def test_niche_guide_finance(self, runner):
        code, data = invoke(runner, ["theme", "niche-guide", "finance"])
        assert code == 0
        assert data["niche"] == "finance"

    def test_niche_guide_unknown(self, runner):
        code, data = invoke(runner, ["theme", "niche-guide", "unicornstuff"])
        assert code == 0
        assert "monetization_paths" in data

    def test_conversion_guide(self, runner):
        code, data = invoke(runner, ["theme", "conversion-guide"])
        assert code == 0
        assert len(data["phases"]) == 4
        assert "common_mistakes" in data
        assert "tools_needed" in data

    def test_content_calendar(self, runner):
        code, data = invoke(runner, [
            "theme", "calendar", "fitness",
            "--platform", "tiktok",
            "--days", "7",
            "--posts-per-day", "2",
            "--start-date", "2026-01-01",
        ])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) == 14
        assert data[0]["date"] == "2026-01-01"
        assert data[0]["status"] == "planned"

    def test_content_calendar_hashtags_present(self, runner):
        code, data = invoke(runner, [
            "theme", "calendar", "beauty",
            "--days", "3",
        ])
        assert code == 0
        for entry in data:
            assert len(entry["hashtags"]) > 0

    def test_monetization(self, runner):
        code, data = invoke(runner, ["theme", "monetization", "finance"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) >= 3
        assert data[0]["rank"] == 1

    def test_list_niches(self, runner):
        code, data = invoke(runner, ["theme", "list-niches"])
        assert code == 0
        assert isinstance(data, list)
        assert len(data) >= 5
        niche_names = [n["niche"] for n in data]
        assert "fitness" in niche_names
        assert "finance" in niche_names

    def test_faceless_formats(self, runner):
        code, data = invoke(runner, ["theme", "faceless-formats"])
        assert code == 0
        assert "formats" in data
        assert len(data["formats"]) >= 5


# ── session commands ──────────────────────────────────────────────────

class TestSessionCommands:
    def test_session_status(self, runner):
        code, data = invoke(runner, ["session", "status"])
        assert code == 0
        assert "session_id" in data
        assert "accounts" in data

    def test_set_niche(self, runner):
        code, out = invoke(runner, ["session", "set-niche", "fitness"], json_mode=False)
        assert code == 0
        assert "fitness" in out

    def test_set_platform(self, runner):
        code, out = invoke(runner, ["session", "set-platform", "tiktok"], json_mode=False)
        assert code == 0
        assert "tiktok" in out


# ── JSON output correctness ───────────────────────────────────────────

class TestJsonOutput:
    def test_all_trend_commands_return_valid_json(self, runner):
        commands = [
            ["--mock", "trends", "tiktok", "--hashtags-only"],
            ["--mock", "trends", "tiktok", "--music-only"],
            ["trends", "hashtags", "--niche", "fitness"],
            ["theme", "list-niches"],
            ["theme", "conversion-guide"],
            ["session", "status"],
        ]
        for cmd in commands:
            result = runner.invoke(cli, ["--json"] + cmd, catch_exceptions=False)
            assert result.exit_code == 0, f"Failed: {cmd} — {result.output}"
            if result.output.strip():
                try:
                    json.loads(result.output.strip())
                except json.JSONDecodeError:
                    pytest.fail(f"Invalid JSON for: {cmd}\nOutput: {result.output[:200]}")
