"""End-to-end CLI tests for social-trends (subprocess invocation)."""

import json
import subprocess
import sys
import typing
from typing import Any
import pytest


def run(args: list[str], expect_exit_0: bool = True) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, "-m", "cli_anything.social_trends"] + args,
        capture_output=True,
        text=True,
    )
    if expect_exit_0:
        assert result.returncode == 0, (
            f"Command {args} exited {result.returncode}\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result.returncode, result.stdout, result.stderr


def run_json(args: list[str]) -> tuple[int, Any]:
    code, stdout, stderr = run(["--json"] + args)
    parsed = json.loads(stdout)
    return code, parsed


# ── trends ────────────────────────────────────────────────────────────────────

class TestTrendsE2E:
    def test_trends_fetch_all(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        code, out, _ = run(["trends", "fetch", "--platform", "all"])
        assert code == 0

    def test_trends_list_tiktok_text(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        run(["trends", "fetch", "--platform", "tiktok"])
        code, out, _ = run(["trends", "list", "--platform", "tiktok"])
        assert code == 0
        assert "tiktok" in out.lower() or "tt_" in out.lower()

    def test_trends_list_json(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        run(["trends", "fetch", "--platform", "all"])
        code, data = run_json(["trends", "list", "--platform", "all"])
        assert isinstance(data, list)
        assert len(data) > 0

    def test_trends_show_json(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        run(["trends", "fetch", "--platform", "tiktok"])
        _, all_data = run_json(["trends", "list", "--platform", "tiktok"])
        first_id = all_data[0]["id"]
        code, detail = run_json(["trends", "show", first_id])
        assert detail["id"] == first_id

    def test_trends_show_unknown_exits_1(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        run(["trends", "fetch", "--platform", "tiktok"])
        code, _, _ = run(["trends", "show", "does_not_exist"], expect_exit_0=False)
        assert code != 0

    def test_trends_cache_info(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        run(["trends", "fetch", "--platform", "all"])
        code, data = run_json(["trends", "cache-info"])
        assert "platforms" in data


# ── hashtags ──────────────────────────────────────────────────────────────────

class TestHashtagsE2E:
    def test_suggest_text(self):
        code, out, _ = run(["hashtags", "suggest", "--niche", "fitness", "--platform", "tiktok"])
        assert code == 0
        assert "#" in out

    def test_suggest_json(self):
        code, data = run_json(["hashtags", "suggest", "--niche", "finance", "--platform", "youtube"])
        assert "primary_set" in data
        assert len(data["primary_set"]) > 0

    def test_all_platforms_json(self):
        code, data = run_json(["hashtags", "all-platforms", "--niche", "tech"])
        assert "tiktok" in data
        assert "youtube" in data
        assert "instagram" in data

    def test_trending_json(self):
        code, data = run_json(["hashtags", "trending", "--platform", "instagram"])
        assert isinstance(data, list)
        assert len(data) > 0

    def test_niches_lists_output(self):
        code, out, _ = run(["hashtags", "niches"])
        assert code == 0
        assert "fitness" in out

    def test_invalid_niche_exits_1(self):
        code, _, _ = run(
            ["hashtags", "suggest", "--niche", "aliens", "--platform", "tiktok"],
            expect_exit_0=False,
        )
        assert code != 0


# ── music ─────────────────────────────────────────────────────────────────────

class TestMusicE2E:
    def test_trending_text(self):
        code, out, _ = run(["music", "trending", "--platform", "tiktok"])
        assert code == 0

    def test_trending_json(self):
        code, data = run_json(["music", "trending", "--platform", "youtube"])
        assert isinstance(data, list)
        assert len(data) > 0

    def test_search_json(self):
        code, data = run_json(["music", "search", "phonk"])
        assert isinstance(data, list)

    def test_genres_json(self):
        code, data = run_json(["music", "genres"])
        assert isinstance(data, list)
        assert len(data) > 0

    def test_by_use_case_json(self):
        code, data = run_json(["music", "by-use-case", "gym"])
        assert isinstance(data, list)


# ── account ───────────────────────────────────────────────────────────────────

class TestAccountE2E:
    def test_optimize_text(self):
        code, out, _ = run(["account", "optimize", "--platform", "tiktok"])
        assert code == 0
        assert "CRITICAL" in out

    def test_optimize_json(self):
        code, data = run_json(["account", "optimize", "--platform", "youtube"])
        assert "checklist" in data
        assert "critical_items" in data

    def test_schedule_json(self):
        code, data = run_json(["account", "schedule", "--platform", "instagram"])
        assert "best_days" in data
        assert "frequency" in data

    def test_analyze_json(self):
        code, data = run_json(["account", "analyze", "--platform", "tiktok", "--niche", "fitness"])
        assert "score" in data
        assert "grade" in data

    def test_roadmap_json(self):
        code, data = run_json(["account", "roadmap", "--platform", "youtube", "--followers", "500"])
        assert data["current_phase"] == "seed"
        assert data["current_followers"] == 500


# ── theme-page ────────────────────────────────────────────────────────────────

class TestThemePageE2E:
    def test_niches_text(self):
        code, out, _ = run(["theme-page", "niches"])
        assert code == 0
        assert "finance" in out

    def test_niches_json(self):
        code, data = run_json(["theme-page", "niches"])
        assert isinstance(data, list)
        assert any(n["niche"] == "ai_tools" for n in data)

    def test_create_text(self):
        code, out, _ = run(["theme-page", "create", "--niche", "ai_tools"])
        assert code == 0
        assert "BLUEPRINT" in out
        assert "First 30 Days" in out

    def test_create_json(self):
        code, data = run_json(["theme-page", "create", "--niche", "finance"])
        assert "first_30_days" in data
        assert "monetization_stack" in data

    def test_compare_json(self):
        code, data = run_json(["theme-page", "compare", "finance", "fitness", "ai_tools"])
        assert len(data) == 3

    def test_monetize_json(self):
        code, data = run_json(["theme-page", "monetize", "--niche", "fitness"])
        assert "all_methods" in data
        assert len(data["all_methods"]) > 0

    def test_content_calendar_json(self):
        code, data = run_json(["theme-page", "content-calendar", "--niche", "motivation", "--days", "7"])
        assert len(data) == 7
        assert all("hook_idea" in d for d in data)

    def test_invalid_niche_exits_1(self):
        code, _, _ = run(
            ["theme-page", "create", "--niche", "knitting"],
            expect_exit_0=False,
        )
        assert code != 0

    def test_help_flag(self):
        code, out, _ = run(["--help"])
        assert code == 0
        assert "social-trends" in out.lower() or "Social Trends" in out
