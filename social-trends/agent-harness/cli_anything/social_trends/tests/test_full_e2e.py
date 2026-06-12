"""End-to-end workflow tests for social-trends CLI.

These tests exercise the full CLI pipeline using the Click test runner.
Network calls are not mocked — tests that require live data are marked
with pytest.mark.integration and skipped by default.
"""

import pytest
import json
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ── Hashtag commands ──────────────────────────────────────────────────────────

class TestHashtagCommands:
    def test_generate_default(self, runner):
        result = runner.invoke(cli, ["hashtags", "generate", "--topic", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower() or "hashtag" in result.output.lower()

    def test_generate_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "generate",
                                     "--topic", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tags" in data
        assert isinstance(data["tags"], list)
        assert len(data["tags"]) > 0

    def test_generate_all_strategies(self, runner):
        for strategy in ["balanced", "growth", "niche", "viral"]:
            result = runner.invoke(cli, [
                "--json", "hashtags", "generate",
                "--topic", "fitness",
                "--strategy", strategy,
            ])
            assert result.exit_code == 0, f"Strategy {strategy} failed: {result.output}"
            data = json.loads(result.output)
            assert data["strategy"] == strategy

    def test_generate_all_platforms(self, runner):
        for platform in ["tiktok", "youtube", "instagram"]:
            result = runner.invoke(cli, [
                "--json", "hashtags", "generate",
                "--topic", "beauty",
                "--platform", platform,
            ])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["platform"] == platform

    def test_niches_command(self, runner):
        result = runner.invoke(cli, ["hashtags", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output

    def test_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert "fitness" in data


# ── Account commands ──────────────────────────────────────────────────────────

class TestAccountCommands:
    def test_schedule_tiktok(self, runner):
        result = runner.invoke(cli, [
            "account", "schedule",
            "--platform", "tiktok",
            "--posts-per-week", "5",
        ])
        assert result.exit_code == 0

    def test_schedule_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "account", "schedule",
            "--platform", "youtube",
            "--posts-per-week", "3",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3
        assert all("day" in s for s in data)

    def test_calendar_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "account", "calendar",
            "--niche", "fitness",
            "--platform", "tiktok",
            "--start", "2024-01-01",
            "--weeks", "2",
            "--posts-per-week", "3",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert all("date" in entry for entry in data)
        assert all("topic_idea" in entry for entry in data)

    def test_grow_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "account", "grow",
            "--platform", "tiktok",
            "--niche", "fitness",
            "--followers", "5000",
            "--avg-views", "200",
            "--posts-per-week", "2",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "diagnoses" in data
        assert "quick_wins" in data
        assert "thirty_day_action_plan" in data

    def test_grow_engagement_calculation(self, runner):
        result = runner.invoke(cli, [
            "--json", "account", "grow",
            "--platform", "tiktok",
            "--niche", "fitness",
            "--followers", "10000",
            "--avg-views", "1000",
            "--posts-per-week", "5",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["engagement_rate"] == pytest.approx(10.0, abs=0.1)


# ── Theme page commands ───────────────────────────────────────────────────────

class TestThemePageCommands:
    def test_playbook_motivation_tiktok(self, runner):
        result = runner.invoke(cli, [
            "--json", "theme", "playbook",
            "--niche", "motivation",
            "--platform", "tiktok",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "motivation"
        assert data["platform"] == "tiktok"
        assert "bio_template" in data
        assert "week1_checklist" in data
        assert len(data["monetization_path"]) > 0

    def test_playbook_human_readable(self, runner):
        result = runner.invoke(cli, [
            "theme", "playbook",
            "--niche", "fitness",
            "--platform", "instagram",
        ])
        assert result.exit_code == 0
        assert "Week 1" in result.output or "checklist" in result.output.lower()

    def test_niches_scoring(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert all("monetization_potential" in n for n in data)

    def test_convert_guide(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "convert"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "phases" in data
        assert len(data["phases"]) == 4

    def test_convert_human_readable(self, runner):
        result = runner.invoke(cli, ["theme", "convert"])
        assert result.exit_code == 0
        assert "Build the Asset" in result.output or "monetiz" in result.output.lower()
        assert "monetiz" in result.output.lower()


# ── Music commands ────────────────────────────────────────────────────────────

class TestMusicCommands:
    @pytest.mark.integration
    def test_music_analyze_integration(self, runner):
        """Requires network — marked integration, skip by default."""
        result = runner.invoke(cli, ["music", "analyze", "--niche", "fitness"])
        assert result.exit_code == 0


# ── Integration tests (skipped by default) ───────────────────────────────────

class TestYouTubeIntegration:
    @pytest.mark.integration
    def test_youtube_trending_live(self, runner):
        result = runner.invoke(cli, [
            "--json", "youtube", "trending",
            "--category", "all",
            "--region", "US",
            "--limit", "5",
        ])
        assert result.exit_code == 0

    @pytest.mark.integration
    def test_youtube_hashtags_live(self, runner):
        result = runner.invoke(cli, ["--json", "youtube", "hashtags", "--limit", "10"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


class TestTikTokIntegration:
    @pytest.mark.integration
    def test_tiktok_trending_live(self, runner):
        result = runner.invoke(cli, [
            "--json", "tiktok", "trending",
            "--limit", "10",
        ])
        assert result.exit_code == 0
