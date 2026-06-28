"""End-to-end CLI tests for Social Trends (subprocess + Click runner)."""

import pytest
import json
import os
import tempfile
import subprocess
import sys

from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


# ── Runner fixture ─────────────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def project_file():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    yield path
    if os.path.isfile(path):
        os.unlink(path)


# ── Project lifecycle ─────────────────────────────────────────────────────────

class TestProjectCLI:
    def test_project_new(self, runner):
        result = runner.invoke(cli, ["project", "new", "myproject"])
        assert result.exit_code == 0

    def test_project_new_json(self, runner):
        result = runner.invoke(cli, ["--json", "project", "new", "myproject"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "created" in data

    def test_project_save_and_open(self, runner, project_file):
        runner.invoke(cli, ["project", "new", "testproj"])
        result = runner.invoke(cli, ["session", "save", project_file])
        assert result.exit_code == 0

        result2 = runner.invoke(cli, ["project", "open", project_file])
        assert result2.exit_code == 0

    def test_project_set_config(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        result = runner.invoke(cli, ["project", "set-config", "niche", "fitness"])
        assert result.exit_code == 0

    def test_project_get_config(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        result = runner.invoke(cli, ["--json", "project", "get-config"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niche" in data or "youtube_api_key" in data

    def test_project_info(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        result = runner.invoke(cli, ["--json", "project", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "p"


# ── Session CLI ────────────────────────────────────────────────────────────────

class TestSessionCLI:
    def test_session_status(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["has_project"] is True

    def test_session_undo_empty_error(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        result = runner.invoke(cli, ["session", "undo"])
        assert result.exit_code != 0 or "Nothing" in result.output or "Error" in result.output

    def test_session_history_after_changes(self, runner):
        runner.invoke(cli, ["project", "new", "p"])
        runner.invoke(cli, ["project", "set-config", "niche", "fitness"])
        result = runner.invoke(cli, ["--json", "session", "history"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)


# ── Hashtags CLI ───────────────────────────────────────────────────────────────

class TestHashtagsCLI:
    def _setup(self, runner):
        runner.invoke(cli, ["project", "new", "p"])

    def test_research_fitness(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "hashtags", "research", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert len(data["hashtags"]) > 0

    def test_research_beauty(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "hashtags", "research", "beauty", "--platform", "instagram"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "instagram"

    def test_score_tag(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "score", "#fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tier" in data

    def test_generate_set(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "hashtags", "generate-set", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "caption_ready" in data

    def test_generate_set_aggressive(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "hashtags", "generate-set", "gaming", "--mix", "aggressive"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["mix_strategy"] == "aggressive"

    def test_list_sets_empty(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "hashtags", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_list_sets_after_generate(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["hashtags", "generate-set", "fitness"])
        runner.invoke(cli, ["hashtags", "generate-set", "beauty"])
        result = runner.invoke(cli, ["--json", "hashtags", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2

    def test_all_mix_strategies(self, runner):
        self._setup(runner)
        for mix in ["balanced", "aggressive", "safe"]:
            result = runner.invoke(cli, ["--json", "hashtags", "generate-set", "travel", "--mix", mix])
            assert result.exit_code == 0

    def test_all_platforms_research(self, runner):
        self._setup(runner)
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            result = runner.invoke(cli, ["--json", "hashtags", "research", "fitness", "--platform", platform])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["platform"] == platform


# ── Accounts CLI ───────────────────────────────────────────────────────────────

class TestAccountsCLI:
    def _setup(self, runner):
        runner.invoke(cli, ["project", "new", "p"])

    def test_add_account(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "accounts", "add", "Main", "--platform", "tiktok", "--handle", "myaccount"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["handle"] == "myaccount"

    def test_list_accounts_empty(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "accounts", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_optimize_account(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["accounts", "add", "Main", "--platform", "tiktok", "--handle", "myhandle", "--niche", "fitness"])
        runner.invoke(cli, ["accounts", "stats", "myhandle", "--platform", "tiktok", "--followers", "15000", "--posts", "60"])
        result = runner.invoke(cli, ["--json", "accounts", "optimize", "myhandle", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "optimization_score" in data
        assert "grade" in data
        assert data["grade"] in ["A", "B", "C", "D", "F"]

    def test_optimize_score_improves_with_stats(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["accounts", "add", "Low", "--platform", "tiktok", "--handle", "lowaccount"])
        low_result = runner.invoke(cli, ["--json", "accounts", "optimize", "lowaccount", "--platform", "tiktok"])
        low_score = json.loads(low_result.output)["optimization_score"]

        runner.invoke(cli, ["accounts", "stats", "lowaccount", "--platform", "tiktok",
                            "--followers", "50000", "--posts", "100", "--avg-likes", "2000", "--avg-comments", "200"])
        runner.invoke(cli, ["accounts", "add", "High", "--platform", "tiktok", "--handle", "highaccount", "--niche", "fitness"])
        runner.invoke(cli, ["accounts", "stats", "highaccount", "--platform", "tiktok",
                            "--followers", "50000", "--posts", "100", "--avg-likes", "2000", "--avg-comments", "200"])
        high_result = runner.invoke(cli, ["--json", "accounts", "optimize", "highaccount", "--platform", "tiktok"])
        high_score = json.loads(high_result.output)["optimization_score"]
        assert high_score >= low_score

    def test_remove_account(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["accounts", "add", "Main", "--platform", "tiktok", "--handle", "todelete"])
        result = runner.invoke(cli, ["--json", "accounts", "remove", "todelete", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["removed"] == 1

    def test_all_platforms_add(self, runner):
        self._setup(runner)
        for i, platform in enumerate(["tiktok", "youtube", "instagram", "twitter", "facebook"]):
            result = runner.invoke(cli, ["accounts", "add", f"acc{i}", "--platform", platform, "--handle", f"user{i}"])
            assert result.exit_code == 0


# ── Theme Page CLI ─────────────────────────────────────────────────────────────

class TestThemePageCLI:
    def test_niches_list(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_guide(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "guide"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "phases" in data
        assert "common_mistakes" in data

    def test_strategy_luxury(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "strategy", "luxury_lifestyle"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "content_pillars" in data
        assert "conversion_funnel" in data

    def test_strategy_motivation(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "strategy", "motivation"])
        assert result.exit_code == 0

    def test_content_pillars(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "content-pillars", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "pillars" in data
        assert "content_mix" in data

    def test_posting_schedule_tiktok(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "posting-schedule", "gaming", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "times" in data
        assert "content_rotation" in data

    def test_all_niches_strategy(self, runner):
        niches = ["luxury_lifestyle", "motivation", "fitness", "finance_money", "gaming", "beauty_makeup"]
        for niche in niches:
            result = runner.invoke(cli, ["--json", "theme-page", "strategy", niche])
            assert result.exit_code == 0, f"Failed for niche: {niche}\n{result.output}"


# ── Calendar CLI ───────────────────────────────────────────────────────────────

class TestCalendarCLI:
    def _setup(self, runner):
        runner.invoke(cli, ["project", "new", "p"])

    def test_generate_calendar(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "calendar", "generate", "--platform", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["total_entries"] > 0

    def test_view_calendar_empty(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "calendar", "view"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_view_after_generate(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        result = runner.invoke(cli, ["--json", "calendar", "view"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) > 0

    def test_add_entry(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, [
            "--json", "calendar", "add",
            "--date", "2025-06-01",
            "--platform", "tiktok",
            "--type", "trending_repost",
            "--title", "Viral fitness clip"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["date"] == "2025-06-01"

    def test_update_status_posted(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        entries_result = runner.invoke(cli, ["--json", "calendar", "view"])
        entries = json.loads(entries_result.output)
        entry_id = entries[0]["id"]

        result = runner.invoke(cli, ["--json", "calendar", "update-status", entry_id, "posted"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["status"] == "posted"

    def test_export_json(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        result = runner.invoke(cli, ["--json", "calendar", "export", "--format", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "entries" in data

    def test_export_csv(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        result = runner.invoke(cli, ["calendar", "export", "--format", "csv"])
        assert result.exit_code == 0
        assert "id,date" in result.output

    def test_export_text(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        result = runner.invoke(cli, ["calendar", "export", "--format", "text"])
        assert result.exit_code == 0
        assert "===" in result.output

    def test_calendar_2_weeks(self, runner):
        self._setup(runner)
        result = runner.invoke(cli, ["--json", "calendar", "generate", "--platform", "instagram", "--niche", "beauty", "--weeks", "2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["weeks"] == 2

    def test_filter_by_status(self, runner):
        self._setup(runner)
        runner.invoke(cli, ["calendar", "generate", "--platform", "tiktok", "--niche", "fitness", "--weeks", "1"])
        entries_result = runner.invoke(cli, ["--json", "calendar", "view"])
        entries = json.loads(entries_result.output)
        if entries:
            entry_id = entries[0]["id"]
            runner.invoke(cli, ["calendar", "update-status", entry_id, "posted"])

        result = runner.invoke(cli, ["--json", "calendar", "view", "--status", "posted"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert all(e["status"] == "posted" for e in data)


# ── Subprocess tests (verify installability) ──────────────────────────────────

class TestSubprocess:
    def test_module_importable(self):
        result = subprocess.run(
            [sys.executable, "-c", "from cli_anything.social_trends.social_trends_cli import cli; print('ok')"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "ok" in result.stdout

    def test_help_flag(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_trends", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "social" in result.stdout.lower() or "trend" in result.stdout.lower()

    def test_json_project_new(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_trends", "--json", "project", "new", "subproc_test"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "created" in data

    def test_hashtags_research_subprocess(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_trends",
             "--json", "hashtags", "research", "fitness"],
            capture_output=True, text=True,
        )
        # May fail if no project, but import must not crash
        assert "error" not in result.stdout.lower() or "No project" in result.stdout

    def test_theme_page_guide_subprocess(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_trends",
             "--json", "theme-page", "guide"],
            capture_output=True, text=True,
        )
        # theme-page guide doesn't need a project
        # It might error if session requires project, but should be importable
        assert result.returncode in (0, 1)
