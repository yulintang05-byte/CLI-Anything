"""End-to-end CLI integration tests for Social Trends CLI."""

import json
import pytest
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ── hashtags commands ─────────────────────────────────────────────────────────

class TestHashtagsCLI:
    def test_recommend_plain(self, runner):
        result = runner.invoke(cli, ["hashtags", "recommend", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower() or "primary" in result.output.lower()

    def test_recommend_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "recommend", "food", "--platform", "instagram"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "food"
        assert "primary" in data
        assert "caption_ready" in data

    def test_caption_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "caption", "travel"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "caption" in data
        assert "#" in data["caption"]

    def test_score_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "score", "fitness", "gym", "fyp", "viral"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "score" in data
        assert "total" in data
        assert data["total"] == 4

    def test_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert "fitness" in data

    def test_score_no_args_error(self, runner):
        result = runner.invoke(cli, ["hashtags", "score"])
        assert result.exit_code != 0 or "Provide hashtags" in result.output


# ── music commands ────────────────────────────────────────────────────────────

class TestMusicCLI:
    def test_catalog_json(self, runner):
        result = runner.invoke(cli, ["--json", "music", "catalog"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_catalog_category_filter(self, runner):
        result = runner.invoke(cli, ["--json", "music", "catalog", "--category", "hype"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert all(d["category"] == "hype" for d in data)

    def test_recommend_json(self, runner):
        result = runner.invoke(cli, ["--json", "music", "recommend", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_categories_json(self, runner):
        result = runner.invoke(cli, ["--json", "music", "categories"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trendy_2025" in data

    def test_trending_no_key_returns_catalog(self, runner, monkeypatch):
        monkeypatch.delenv("TIKTOK_RAPIDAPI_KEY", raising=False)
        result = runner.invoke(cli, ["--json", "music", "trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ── account commands ──────────────────────────────────────────────────────────

class TestAccountCLI:
    def test_tips_tiktok_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "tips", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "posting_frequency" in data
        assert "growth_hack" in data

    def test_schedule_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "schedule", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert "best_times" in data

    def test_checklist_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "checklist"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert all("item" in c for c in data)

    def test_pillars_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "pillars"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "education" in data
        assert "entertainment" in data

    def test_audit_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "account", "audit",
            "--platform", "tiktok",
            "--username", "testpage",
            "--followers", "10000",
            "--following", "300",
            "--posts", "120",
            "--avg-likes", "500",
            "--avg-comments", "40",
            "--posting", "daily",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "score" in data
        assert data["score"] >= 0
        assert "feedback" in data

    def test_optimize_all_json(self, runner):
        result = runner.invoke(cli, ["--json", "account", "optimize-all"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "platform_guides" in data
        assert "tiktok" in data["platform_guides"]
        assert "youtube" in data["platform_guides"]
        assert "profile_checklist" in data


# ── theme commands ────────────────────────────────────────────────────────────

class TestThemeCLI:
    def test_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "fitness" in data

    def test_niches_filter_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)

    def test_playbook_plain(self, runner):
        result = runner.invoke(cli, ["theme", "playbook"])
        assert result.exit_code == 0
        assert "Phase" in result.output
        assert "Niche" in result.output

    def test_playbook_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "playbook"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 7

    def test_convert_plain(self, runner):
        result = runner.invoke(cli, ["theme", "convert"])
        assert result.exit_code == 0
        assert "Link in Bio" in result.output or "Funnel" in result.output

    def test_convert_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "convert"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert all("strategy" in s for s in data)

    def test_plan_json(self, runner):
        result = runner.invoke(cli, [
            "--json", "theme", "plan",
            "--niche", "fitness",
            "--platform", "tiktok",
            "--target", "25000",
            "--goal", "affiliate",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "fitness"
        assert len(data["phases"]) == 7

    def test_list_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "list-niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ── trends commands (no API keys) ────────────────────────────────────────────

class TestTrendsCLI:
    def test_tiktok_no_key_returns_something(self, runner, monkeypatch):
        monkeypatch.delenv("TIKTOK_RAPIDAPI_KEY", raising=False)
        result = runner.invoke(cli, ["--json", "trends", "tiktok", "--count", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_youtube_no_key_returns_something(self, runner, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--count", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_all_no_keys(self, runner, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        monkeypatch.delenv("TIKTOK_RAPIDAPI_KEY", raising=False)
        result = runner.invoke(cli, ["--json", "trends", "all", "--count", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube_trending" in data
        assert "tiktok_trending" in data


# ── session commands ──────────────────────────────────────────────────────────

class TestSessionCLI:
    def test_status_json(self, runner):
        result = runner.invoke(cli, ["--json", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "history_count" in data
        assert "api_keys" in data

    def test_history_json(self, runner):
        result = runner.invoke(cli, ["--json", "history"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_undo_empty(self, runner):
        result = runner.invoke(cli, ["undo"])
        assert result.exit_code == 0
        assert "Nothing" in result.output

    def test_redo_empty(self, runner):
        result = runner.invoke(cli, ["redo"])
        assert result.exit_code == 0
        assert "Nothing" in result.output
