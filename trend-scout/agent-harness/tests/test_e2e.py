"""E2E tests for trend-scout CLI (subprocess invocation)."""

import json
import subprocess
import sys
import os
import tempfile
import pytest

_PKG_DIR = os.path.join(os.path.dirname(__file__), "..")
_PYTHON = sys.executable


def _run(*args, expect_ok: bool = True) -> subprocess.CompletedProcess:
    cmd = [_PYTHON, "-m", "cli_anything.trend_scout", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=_PKG_DIR, timeout=30)
    if expect_ok:
        assert result.returncode == 0, f"Command failed:\n{result.stdout}\n{result.stderr}"
    return result


def _run_json(*args) -> dict:
    result = _run("--json", *args)
    return json.loads(result.stdout)


# ── version / help ────────────────────────────────────────────────────────────

class TestCLIHelp:
    def test_version(self):
        r = _run("--version")
        assert "1.0.0" in r.stdout

    def test_root_help(self):
        r = _run("--help")
        assert "youtube" in r.stdout
        assert "tiktok" in r.stdout
        assert "optimize" in r.stdout
        assert "theme-pages" in r.stdout
        assert "compare" in r.stdout

    def test_youtube_help(self):
        r = _run("youtube", "--help")
        assert "trends" in r.stdout
        assert "hashtag" in r.stdout

    def test_tiktok_help(self):
        r = _run("tiktok", "--help")
        assert "trends" in r.stdout
        assert "sounds" in r.stdout
        assert "hashtag" in r.stdout

    def test_optimize_help(self):
        r = _run("optimize", "--help")
        assert "--platform" in r.stdout
        assert "--niche" in r.stdout
        assert "--followers" in r.stdout

    def test_theme_pages_help(self):
        r = _run("theme-pages", "--help")
        assert "niches" in r.stdout
        assert "guide" in r.stdout
        assert "playbook" in r.stdout


# ── youtube ───────────────────────────────────────────────────────────────────

class TestYoutubeCLI:
    def test_categories_json(self):
        data = _run_json("youtube", "categories")
        assert isinstance(data, list)
        assert "default" in data
        assert "music" in data

    def test_categories_text(self):
        r = _run("youtube", "categories")
        assert "default" in r.stdout
        assert "music" in r.stdout

    @pytest.mark.skip(reason="requires network + yt-dlp")
    def test_trends_live(self):
        data = _run_json("youtube", "trends")
        assert data["source"] == "youtube"

    def test_trends_json_structure_with_mock(self):
        # Progress goes to stderr in --json mode, stdout is clean JSON
        r = subprocess.run(
            [_PYTHON, "-m", "cli_anything.trend_scout", "--json", "youtube", "trends", "--limit", "1"],
            capture_output=True, text=True, cwd=_PKG_DIR, timeout=30
        )
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["source"] == "youtube"
        assert "videos" in data
        assert "top_hashtags" in data


# ── tiktok ────────────────────────────────────────────────────────────────────

class TestTiktokCLI:
    def test_regions_json(self):
        data = _run_json("tiktok", "regions")
        assert isinstance(data, list)
        assert "us" in data
        assert "uk" in data

    def test_regions_text(self):
        r = _run("tiktok", "regions")
        assert "us" in r.stdout

    def test_sounds_json(self):
        data = _run_json("tiktok", "sounds")
        assert data["source"] == "tiktok"
        assert "sounds" in data
        assert data["sound_count"] > 0  # fallback data always present

    def test_sounds_text(self):
        r = _run("tiktok", "sounds")
        assert "Trending Sounds" in r.stdout

    def test_trends_json(self):
        data = _run_json("tiktok", "trends")
        assert data["source"] == "tiktok"
        assert "top_hashtags" in data
        assert len(data["top_hashtags"]) > 0  # fallback ensures data

    def test_trends_region(self):
        data = _run_json("tiktok", "trends", "--region", "uk")
        assert data["region"] == "uk"

    def test_hashtag_json(self):
        data = _run_json("tiktok", "hashtag", "fitness")
        assert "name" in data
        assert data["source"] == "tiktok"
        assert "url" in data


# ── optimize ──────────────────────────────────────────────────────────────────

class TestOptimizeCLI:
    def test_optimize_tiktok_json(self):
        data = _run_json("optimize", "-p", "tiktok", "-n", "fitness", "-f", "5000")
        assert data["platform"] == "tiktok"
        assert data["niche"] == "fitness"
        assert data["tier"] == "micro"
        assert "posting_times" in data
        assert "hashtag_strategy" in data
        assert "growth_tactics" in data
        assert "monetization_milestones" in data

    def test_optimize_youtube_json(self):
        data = _run_json("optimize", "-p", "youtube", "-n", "gaming", "-f", "100000")
        assert data["platform"] == "youtube"
        assert data["tier"] == "macro"  # 100k hits macro threshold (not < 100k)

    def test_optimize_instagram_json(self):
        data = _run_json("optimize", "-p", "instagram", "-n", "fashion", "-f", "1000000")
        assert data["platform"] == "instagram"
        assert data["tier"] == "mega"  # 1M hits mega threshold

    def test_optimize_text_output(self):
        r = _run("optimize", "-p", "tiktok", "-n", "travel", "-f", "500")
        assert "Optimization Report" in r.stdout or "optimization" in r.stdout.lower()
        assert "Hashtag Strategy" in r.stdout
        assert "Monetization" in r.stdout

    def test_optimize_all_niches(self):
        niches = ["motivation", "fashion", "food", "fitness", "travel", "comedy", "finance"]
        for niche in niches:
            data = _run_json("optimize", "-p", "tiktok", "-n", niche, "-f", "1000")
            assert data["niche"] == niche


# ── compare ───────────────────────────────────────────────────────────────────

class TestCompareCLI:
    def test_compare_json(self):
        data = _run_json("compare", "--limit", "5")
        assert "cross_platform_hashtags" in data
        assert "youtube_only_tags" in data
        assert "tiktok_only_tags" in data
        assert "recommendation" in data
        assert "action_items" in data

    def test_compare_text(self):
        r = _run("compare", "--limit", "5")
        assert "Cross-Platform" in r.stdout or "platform" in r.stdout.lower()


# ── theme-pages ───────────────────────────────────────────────────────────────

class TestThemePagesCLI:
    def test_niches_json(self):
        data = _run_json("theme-pages", "niches")
        assert isinstance(data, list)
        assert len(data) >= 8
        assert any(n["niche"] == "fitness" for n in data)

    def test_niches_text(self):
        r = _run("theme-pages", "niches")
        assert "fitness" in r.stdout
        assert "fashion" in r.stdout
        assert "finance" in r.stdout

    def test_guide_json(self):
        data = _run_json("theme-pages", "guide", "fitness")
        assert data["niche"] == "fitness"
        assert "content_sources" in data
        assert "monetization" in data
        assert "quick_start_checklist" in data
        assert len(data["quick_start_checklist"]) == 7

    def test_guide_all_niches(self):
        niches = ["motivation", "luxury", "animals", "finance", "fitness",
                  "food", "travel", "tech", "fashion", "gaming"]
        for niche in niches:
            data = _run_json("theme-pages", "guide", niche)
            assert data["niche"] == niche

    def test_guide_invalid_niche(self):
        r = _run("theme-pages", "guide", "notrealniche", expect_ok=False)
        assert r.returncode != 0 or "error" in r.stderr.lower() or "Error" in r.stderr

    def test_playbook_json_all(self):
        data = _run_json("theme-pages", "playbook")
        assert "phases" in data
        assert len(data["phases"]) == 4

    def test_playbook_specific_phase(self):
        for phase in ("1", "2", "3", "4"):
            data = _run_json("theme-pages", "playbook", "--phase", phase)
            assert "actions" in data
            assert len(data["actions"]) >= 3

    def test_playbook_text(self):
        r = _run("theme-pages", "playbook")
        assert "Phase" in r.stdout

    def test_tools_json(self):
        data = _run_json("theme-pages", "tools")
        assert isinstance(data, list)
        assert len(data) >= 5
        assert any(t["name"] == "CapCut" for t in data)

    def test_tools_text(self):
        r = _run("theme-pages", "tools")
        assert "CapCut" in r.stdout
        assert "Canva" in r.stdout

    def test_sell_json(self):
        data = _run_json("theme-pages", "sell")
        assert isinstance(data, list)
        assert any(p["name"] == "Flippa" for p in data)

    def test_sell_text(self):
        r = _run("theme-pages", "sell")
        assert "Flippa" in r.stdout


# ── export ────────────────────────────────────────────────────────────────────

class TestExportCLI:
    def test_export_tiktok_only(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            _run("export", "-o", path, "--source", "tiktok")
            with open(path) as f:
                data = json.load(f)
            assert "tiktok" in data
            assert "exported_at" in data
        finally:
            os.unlink(path)

    def test_export_youtube_only(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            _run("export", "-o", path, "--source", "youtube")
            with open(path) as f:
                data = json.load(f)
            assert "youtube" in data
            assert "tiktok" not in data
        finally:
            os.unlink(path)

    def test_export_both(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            _run("export", "-o", path, "--source", "both")
            with open(path) as f:
                data = json.load(f)
            assert "tiktok" in data
            assert "youtube" in data
            assert "cross_platform" in data
        finally:
            os.unlink(path)
