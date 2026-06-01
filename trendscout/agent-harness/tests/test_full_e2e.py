"""TrendScout – CLI end-to-end tests (Click test runner, no network).

Exercises the CLI commands via Click's test runner.
Run: cd trendscout/agent-harness && pytest tests/test_full_e2e.py -v
"""

import os
import sys
import json
import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.trendscout.trendscout_cli import cli
import cli_anything.trendscout.trendscout_cli as cli_module


@pytest.fixture(autouse=True)
def reset_session():
    """Reset the global session before every test."""
    cli_module._session = None
    cli_module._json_output = False
    cli_module._repl_mode = False
    yield
    cli_module._session = None


@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, *args, json_mode=True):
    extra = ["--json"] if json_mode else []
    return runner.invoke(cli, extra + list(args), catch_exceptions=False)


# ── Smoke tests ───────────────────────────────────────────────────────────────

class TestCLISmoke:
    def test_version(self, runner):
        r = runner.invoke(cli, ["--version"])
        assert r.exit_code == 0
        assert "1.0.0" in r.output

    def test_help(self, runner):
        r = runner.invoke(cli, ["--help"])
        assert r.exit_code == 0
        assert "trends" in r.output
        assert "account" in r.output
        assert "theme-page" in r.output


# ── Account commands ──────────────────────────────────────────────────────────

class TestAccountCLI:
    def test_add_account(self, runner):
        r = invoke(runner, "account", "add", "--handle", "testpage", "--platform", "tiktok", "--niche", "fitness")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"]
        assert data["handle"] == "testpage"

    def test_list_empty(self, runner):
        r = invoke(runner, "account", "list")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data == []

    def test_list_after_add(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "list")
        data = json.loads(r.output)
        assert len(data) == 1
        assert data[0]["handle"] == "p1"

    def test_remove_account(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "remove", "acc0")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"]

    def test_update_account(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "update", "acc0", "--followers", "50000")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["followers"] == 50000

    def test_audit_account(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "audit", "acc0")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "score" in data
        assert "grade" in data
        assert "top_priority_actions" in data

    def test_audit_with_completed(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "audit", "acc0", "--completed", "bio_keywords,profile_pic")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["score"] > 0

    def test_checklist_tiktok(self, runner):
        r = invoke(runner, "account", "checklist", "tiktok")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_optimize_all_empty(self, runner):
        r = invoke(runner, "account", "optimize-all")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["total_accounts"] == 0

    def test_optimize_all_with_accounts(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        invoke(runner, "account", "add", "--handle", "p2", "--platform", "youtube")
        r = invoke(runner, "account", "optimize-all")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["total_accounts"] == 2

    def test_growth_plan(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "account", "plan", "acc0", "--goal", "10000", "--weeks", "12")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["goal_followers"] == 10000
        assert len(data["phases"]) == 3


# ── Trends commands ───────────────────────────────────────────────────────────

class TestTrendsCLI:
    def test_trends_times_both(self, runner):
        r = invoke(runner, "trends", "times", "--platform", "both")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "platforms" in data
        assert "tiktok" in data["platforms"]

    def test_trends_times_tiktok(self, runner):
        r = invoke(runner, "trends", "times", "--platform", "tiktok")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "best_days" in data

    def test_trends_times_invalid(self, runner):
        r = runner.invoke(cli, ["trends", "times", "--platform", "snapchat"])
        assert r.exit_code != 0 or "error" in r.output.lower() or "Error" in r.output

    def test_trends_fetch_tiktok_returns_hashtags(self, runner):
        r = invoke(runner, "trends", "fetch", "tiktok", "--limit", "10")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "hashtags" in data
        assert len(data["hashtags"]) > 0

    def test_trends_fetch_youtube_returns_videos(self, runner):
        r = invoke(runner, "trends", "fetch", "youtube", "--limit", "5")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "videos" in data
        assert len(data["videos"]) > 0

    def test_trends_fetch_music(self, runner):
        r = invoke(runner, "trends", "fetch", "music", "--limit", "5")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "youtube_music" in data or "tracks" in data or "tiktok_sounds" in data

    def test_trends_cross_returns_hashtags(self, runner):
        r = invoke(runner, "trends", "cross", "--category", "all", "--limit", "10")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "cross_platform_hashtags" in data
        assert len(data["cross_platform_hashtags"]) > 0

    def test_trends_hashtags_fitness(self, runner):
        r = invoke(runner, "trends", "hashtags", "--niche", "fitness")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "recommended_hashtags" in data
        assert len(data["recommended_hashtags"]) > 0
        assert "strategy_tip" in data

    def test_trends_hashtags_unknown_niche_works(self, runner):
        r = invoke(runner, "trends", "hashtags", "--niche", "beekeeping")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "recommended_hashtags" in data

    def test_trends_fyp_returns_videos(self, runner):
        r = invoke(runner, "trends", "fyp", "--limit", "5")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "videos" in data


# ── Theme page commands ───────────────────────────────────────────────────────

class TestThemePageCLI:
    def test_playbook_full(self, runner):
        r = invoke(runner, "theme-page", "playbook")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "steps" in data
        assert data["total_steps"] == 7

    def test_playbook_step(self, runner):
        r = invoke(runner, "theme-page", "playbook", "--step", "1")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["step"] == 1
        assert "action_items" in data

    def test_playbook_all_steps(self, runner):
        for step in range(1, 8):
            r = invoke(runner, "theme-page", "playbook", "--step", str(step))
            assert r.exit_code == 0

    def test_niches_cpm_sort(self, runner):
        r = invoke(runner, "theme-page", "niches", "--sort", "cpm")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["count"] >= 10

    def test_niches_opportunity_sort(self, runner):
        r = invoke(runner, "theme-page", "niches", "--sort", "opportunity")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["sort_by"] == "opportunity"

    def test_formats_tiktok(self, runner):
        r = invoke(runner, "theme-page", "formats", "--platform", "tiktok")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["platform"] == "tiktok"
        assert data["count"] >= 5

    def test_formats_youtube(self, runner):
        r = invoke(runner, "theme-page", "formats", "--platform", "youtube")
        assert r.exit_code == 0

    def test_monetize_all(self, runner):
        r = invoke(runner, "theme-page", "monetize", "--niche", "all")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["count"] >= 8

    def test_monetize_fitness(self, runner):
        r = invoke(runner, "theme-page", "monetize", "--niche", "fitness")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["count"] >= 2

    def test_quickstart_gaming(self, runner):
        r = invoke(runner, "theme-page", "quickstart", "--niche", "gaming", "--platform", "tiktok")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["niche"] == "gaming"
        assert "week_1_actions" in data
        assert "recommended_monetization" in data

    def test_quickstart_youtube(self, runner):
        r = invoke(runner, "theme-page", "quickstart", "--niche", "finance", "--platform", "youtube")
        assert r.exit_code == 0


# ── Session commands ──────────────────────────────────────────────────────────

class TestSessionCLI:
    def test_session_status(self, runner):
        r = invoke(runner, "session", "status")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "accounts" in data

    def test_session_undo_nothing(self, runner):
        r = runner.invoke(cli, ["session", "undo"])
        assert "Nothing to undo" in r.output or r.exit_code != 0

    def test_session_undo_after_add(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "session", "undo")
        assert r.exit_code == 0
        # Account should be gone
        list_r = invoke(runner, "account", "list")
        data = json.loads(list_r.output)
        assert len(data) == 0

    def test_session_redo(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        invoke(runner, "session", "undo")
        r = invoke(runner, "session", "redo")
        assert r.exit_code == 0

    def test_session_history(self, runner):
        invoke(runner, "account", "add", "--handle", "p1", "--platform", "tiktok")
        r = invoke(runner, "session", "history")
        assert r.exit_code == 0
