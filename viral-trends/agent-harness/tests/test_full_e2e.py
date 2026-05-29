"""Viral Trends CLI - Full E2E tests (network-optional).

Network tests require yt-dlp and are skipped automatically if not installed.
All other tests run fully offline using mock data and Click test runner.

Run: cd viral-trends/agent-harness && pytest tests/test_full_e2e.py -v
"""

import json
import os
import subprocess
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from click.testing import CliRunner
from cli_anything.viral_trends.viral_trends_cli import cli
from cli_anything.viral_trends.core.session import Session
from cli_anything.viral_trends.core import workspace as ws_mod
from cli_anything.viral_trends.core import trends as trends_mod
from cli_anything.viral_trends.core import scheduler as sched_mod


# ─────────────────────────────────────────────────────────────────────────────
# Availability checks
# ─────────────────────────────────────────────────────────────────────────────

def _check_ytdlp() -> bool:
    try:
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=10)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


YTDLP_AVAILABLE = _check_ytdlp()

requires_ytdlp = pytest.mark.skipif(
    not YTDLP_AVAILABLE,
    reason="Requires yt-dlp to be installed (pip install yt-dlp)"
)


# ─────────────────────────────────────────────────────────────────────────────
# Full workflow (offline)
# ─────────────────────────────────────────────────────────────────────────────

class TestFullWorkflow:
    def test_new_workspace_fetch_optimize_schedule_save_reload(self, tmp_path):
        """End-to-end: create workspace → fetch trends → optimize → schedule → save → reload."""
        path = str(tmp_path / "page.json")

        s = Session()
        ws_mod.new_workspace(s, name="my_page", niche="gaming")

        # Fetch trends (mock)
        snap_result = trends_mod.get_trend_snapshot(s, platform="both", live=False)
        assert snap_result["success"]
        assert len(s.project["trend_snapshots"]) == 1

        # Generate schedule
        sched_result = sched_mod.generate_week(
            s, niche="gaming", platforms=["tiktok"], posts_per_day=1
        )
        assert sched_result["entries_created"] == 7

        # Save workspace
        ws_mod.save_workspace(s, path)
        assert os.path.isfile(path)

        # Reload workspace in fresh session
        s2 = Session()
        reload_result = ws_mod.open_workspace(s2, path)
        assert reload_result["success"]
        assert s2.project["name"] == "my_page"
        assert len(s2.project["trend_snapshots"]) == 1
        assert len(s2.project["schedule"]) == 7

    def test_undo_redo_across_operations(self):
        s = Session()
        ws_mod.new_workspace(s, name="test", niche="finance")

        trends_mod.get_trend_snapshot(s, platform="youtube", live=False)
        assert len(s.project["trend_snapshots"]) == 1

        s.undo()
        assert len(s.project["trend_snapshots"]) == 0

        s.redo()
        assert len(s.project["trend_snapshots"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# CLI commands via CliRunner (offline)
# ─────────────────────────────────────────────────────────────────────────────

class TestCLICommands:
    def setup_method(self):
        """Reset global session state between tests."""
        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None
        cli_module._json_output = False
        cli_module._repl_mode = False

    def test_workspace_new(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "workspace", "new",
                                     "--name", "test", "--niche", "gaming"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert data["name"] == "test"

    def test_workspace_new_invalid_niche(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["workspace", "new", "--niche", "invalid_niche"])
        assert result.exit_code != 0

    def test_workspace_niches(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "workspace", "niches"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 8

    def test_workspace_save_and_open(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")

        result = runner.invoke(cli, ["--json", "workspace", "new",
                                     "--name", "test", "--niche", "fitness",
                                     "-o", path])
        assert result.exit_code == 0, result.output

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        result2 = runner.invoke(cli, ["--json", "workspace", "open", path])
        assert result2.exit_code == 0, result2.output
        data = json.loads(result2.output)
        assert data["success"]
        assert data["name"] == "test"

    def test_trends_fetch_requires_workspace(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "fetch", "--platform", "youtube"])
        assert result.exit_code != 0

    def test_trends_fetch_with_workspace(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        result = runner.invoke(cli, ["--json", "--workspace", path,
                                     "trends", "fetch", "--platform", "youtube"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]

    def test_trends_list(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        runner.invoke(cli, ["--workspace", path, "trends", "fetch",
                            "--platform", "youtube"])
        result = runner.invoke(cli, ["--json", "--workspace", path, "trends", "list"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_optimize_profile(self):
        runner = CliRunner()
        runner.invoke(cli, ["workspace", "new", "--name", "test", "--niche", "gaming"])
        result = runner.invoke(cli, ["--json", "optimize", "profile", "--niche", "gaming"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert "top_hashtags" in data
        assert "action_plan" in data

    def test_optimize_hashtags(self):
        runner = CliRunner()
        runner.invoke(cli, ["workspace", "new", "--name", "test", "--niche", "finance"])
        result = runner.invoke(cli, ["--json", "optimize", "hashtags", "--niche", "finance"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert len(data["tags"]) > 0

    def test_optimize_times(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "optimize", "times", "--platform", "tiktok"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert len(data["windows"]) > 0

    def test_optimize_hooks(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "optimize", "hooks",
                                     "--type", "curiosity", "--niche", "gaming"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert len(data["hooks"]) == 3

    def test_schedule_generate(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        result = runner.invoke(cli, ["--json", "--workspace", path,
                                     "schedule", "generate",
                                     "--niche", "gaming", "--platforms", "tiktok"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]
        assert data["entries_created"] > 0

    def test_schedule_list(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        runner.invoke(cli, ["--workspace", path, "schedule", "generate",
                            "--niche", "gaming", "--platforms", "tiktok"])
        result = runner.invoke(cli, ["--json", "--workspace", path, "schedule", "list"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_schedule_add_and_mark(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        runner.invoke(cli, ["--workspace", path, "schedule", "add",
                            "--day", "monday", "--time", "19:00", "--platform", "tiktok"])
        result = runner.invoke(cli, ["--json", "--workspace", path,
                                     "schedule", "mark", "sched0", "--status", "published"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["entry"]["status"] == "published"

    def test_guide_theme_page(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "guide", "theme-page"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "title" in data
        assert "sections" in data

    def test_guide_converting(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "guide", "converting"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "sections" in data

    def test_guide_list(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "guide", "list"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 8

    def test_session_status(self):
        runner = CliRunner()
        runner.invoke(cli, ["workspace", "new", "--name", "test", "--niche", "gaming"])
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["has_project"]

    def test_session_undo_redo(self, tmp_path):
        runner = CliRunner()
        path = str(tmp_path / "page.json")
        runner.invoke(cli, ["workspace", "new", "--name", "test",
                            "--niche", "gaming", "-o", path])

        import cli_anything.viral_trends.viral_trends_cli as cli_module
        cli_module._session = None

        runner.invoke(cli, ["--workspace", path, "trends", "fetch",
                            "--platform", "youtube"])

        result = runner.invoke(cli, ["--json", "--workspace", path, "session", "undo"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["success"]

    def test_version_flag(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output


# ─────────────────────────────────────────────────────────────────────────────
# Live YouTube fetch (requires yt-dlp)
# ─────────────────────────────────────────────────────────────────────────────

class TestYouTubeLiveFetch:
    @requires_ytdlp
    def test_live_fetch_returns_items(self):
        result = trends_mod.fetch_youtube_trends(live=True, max_results=5)
        assert result["success"]
        # May fall back to mock — either is acceptable
        assert result["count"] > 0

    @requires_ytdlp
    def test_live_fetch_items_have_required_keys(self):
        result = trends_mod.fetch_youtube_trends(live=True, max_results=5)
        required = {"rank", "title", "channel", "views", "likes",
                    "category", "url", "duration_seconds"}
        for item in result["items"]:
            assert required.issubset(item.keys())

    @requires_ytdlp
    def test_live_fetch_does_not_raise_on_network_failure(self):
        """Even with network failure, the call should return mock data, not raise."""
        try:
            result = trends_mod.fetch_youtube_trends(
                live=True, country="XX", max_results=5
            )
            assert result["success"]
        except Exception as e:
            pytest.fail(f"fetch_youtube_trends raised unexpectedly: {e}")
