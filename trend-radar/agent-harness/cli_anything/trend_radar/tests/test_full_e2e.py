"""End-to-end tests for CLI-Anything Trend Radar.

Tests the CLI as a subprocess and validates output structure.
API-dependent tests are skipped when no credentials are available.

Run with: pytest -v
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# ── CLI resolver ──────────────────────────────────────────────────────

def _resolve_cli() -> list[str]:
    """Return the command prefix to invoke the CLI."""
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
        return ["cli-anything-trend-radar"]
    # Try installed command first
    import shutil
    if shutil.which("cli-anything-trend-radar"):
        return ["cli-anything-trend-radar"]
    # Fall back to python -m for dev/CI
    return [sys.executable, "-m", "cli_anything.trend_radar"]


CLI = _resolve_cli()


def _run(*args, env_extra=None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        CLI + list(args),
        capture_output=True, text=True, env=env,
    )


# ════════════════════════════════════════════════════════════════════
# CLI smoke tests
# ════════════════════════════════════════════════════════════════════

class TestCLISmoke:
    def test_version(self):
        result = _run("--version")
        assert result.returncode == 0
        assert "0.1.0" in result.stdout or "0.1.0" in result.stderr

    def test_help_shows_commands(self):
        result = _run("--help")
        assert result.returncode == 0
        output = result.stdout
        assert "youtube" in output
        assert "tiktok" in output
        assert "optimize" in output
        assert "calendar" in output
        assert "theme" in output

    def test_youtube_help(self):
        result = _run("youtube", "--help")
        assert result.returncode == 0
        assert "trending" in result.stdout
        assert "hashtags" in result.stdout
        assert "music" in result.stdout

    def test_tiktok_help(self):
        result = _run("tiktok", "--help")
        assert result.returncode == 0
        assert "trending" in result.stdout
        assert "hashtags" in result.stdout
        assert "sounds" in result.stdout

    def test_optimize_help(self):
        result = _run("optimize", "--help")
        assert result.returncode == 0
        assert "hashtags" in result.stdout
        assert "schedule" in result.stdout
        assert "account" in result.stdout

    def test_calendar_help(self):
        result = _run("calendar", "--help")
        assert result.returncode == 0
        assert "generate" in result.stdout
        assert "export" in result.stdout

    def test_theme_help(self):
        result = _run("theme", "--help")
        assert result.returncode == 0
        assert "guide" in result.stdout
        assert "niches" in result.stdout
        assert "convert" in result.stdout
        assert "setup" in result.stdout


# ════════════════════════════════════════════════════════════════════
# TikTok commands (no API key needed — uses fallback data)
# ════════════════════════════════════════════════════════════════════

class TestTikTokCLI:
    def test_hashtags_human_output(self):
        result = _run("tiktok", "hashtags", "--region", "US", "--limit", "5")
        assert result.returncode == 0
        assert "#" in result.stdout

    def test_hashtags_json_output(self):
        result = _run("tiktok", "hashtags", "--json", "--limit", "5")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) <= 5
        assert "hashtag_name" in data[0]

    def test_sounds_human_output(self):
        result = _run("tiktok", "sounds", "--limit", "5")
        assert result.returncode == 0

    def test_sounds_json_output(self):
        result = _run("tiktok", "sounds", "--json", "--limit", "5")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert "title" in data[0]
        assert "author" in data[0]

    def test_trending_json_output(self):
        result = _run("tiktok", "trending", "--json", "--limit", "5")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert "play_count" in data[0]

    def test_hashtags_rise_sort(self):
        result = _run("tiktok", "hashtags", "--sort", "rise", "--limit", "5", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_hashtags_30day_period(self):
        result = _run("tiktok", "hashtags", "--period", "30", "--limit", "5", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)


# ════════════════════════════════════════════════════════════════════
# Optimize commands
# ════════════════════════════════════════════════════════════════════

class TestOptimizeCLI:
    def test_hashtags_human_output(self):
        result = _run("optimize", "hashtags", "--niche", "fitness")
        assert result.returncode == 0
        assert "#" in result.stdout

    def test_hashtags_json_output(self):
        result = _run("optimize", "hashtags", "--niche", "fitness", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "niche" in data
        assert "tiers" in data
        assert "all_tags" in data
        assert "copy_ready" in data

    def test_hashtags_platform_tiktok(self):
        result = _run("optimize", "hashtags", "--niche", "food", "--platform", "tiktok", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["platform"] == "tiktok"
        assert data["total"] <= 10

    def test_hashtags_platform_youtube(self):
        result = _run("optimize", "hashtags", "--niche", "tech", "--platform", "youtube", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] <= 15

    def test_hashtags_platform_twitter(self):
        result = _run("optimize", "hashtags", "--niche", "finance", "--platform", "twitter", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] <= 3

    def test_schedule_human_output(self):
        result = _run("optimize", "schedule", "--platform", "instagram")
        assert result.returncode == 0
        assert "Monday" in result.stdout or "monday" in result.stdout.lower()

    def test_schedule_json_output(self):
        result = _run("optimize", "schedule", "--platform", "tiktok", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "schedule" in data
        assert len(data["schedule"]) == 7

    def test_schedule_all_platforms(self):
        result = _run("optimize", "schedule", "--platform", "all", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "instagram" in data
        assert "tiktok" in data
        assert "youtube" in data

    def test_account_audit_human_output(self):
        result = _run("optimize", "account", "--platform", "instagram", "--niche", "fitness")
        assert result.returncode == 0
        assert len(result.stdout) > 100

    def test_account_audit_json_output(self):
        result = _run("optimize", "account", "--platform", "tiktok", "--niche", "food", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_account_audit_with_username(self):
        result = _run("optimize", "account", "--platform", "instagram",
                      "--niche", "travel", "--username", "mytravelpage")
        assert result.returncode == 0
        assert "@mytravelpage" in result.stdout


# ════════════════════════════════════════════════════════════════════
# Calendar commands
# ════════════════════════════════════════════════════════════════════

class TestCalendarCLI:
    def test_generate_human_output(self):
        result = _run("calendar", "generate", "--niche", "fitness", "--weeks", "1")
        assert result.returncode == 0
        assert "Week 1" in result.stdout

    def test_generate_json_output(self):
        result = _run("calendar", "generate", "--niche", "food", "--weeks", "2", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["niche"] == "food"
        assert len(data["weeks"]) == 2
        assert data["total_posts"] > 0

    def test_generate_export_json(self, tmp_path):
        out = str(tmp_path / "cal.json")
        result = _run("calendar", "generate", "--niche", "travel",
                      "--weeks", "1", "--output", out)
        assert result.returncode == 0
        assert Path(out).exists()
        with open(out) as f:
            data = json.load(f)
        assert data["niche"] == "travel"

    def test_generate_export_csv(self, tmp_path):
        out = str(tmp_path / "cal.csv")
        result = _run("calendar", "generate", "--niche", "finance",
                      "--weeks", "1", "--output", out)
        assert result.returncode == 0
        assert Path(out).exists()
        content = Path(out).read_text()
        assert "week" in content
        assert "topic" in content

    def test_export_command_json(self, tmp_path):
        out = str(tmp_path / "exported.json")
        result = _run("calendar", "export", out, "--niche", "fashion", "--weeks", "1")
        assert result.returncode == 0
        assert Path(out).exists()

    def test_export_command_csv(self, tmp_path):
        out = str(tmp_path / "exported.csv")
        result = _run("calendar", "export", out, "--niche", "beauty", "--weeks", "1")
        assert result.returncode == 0
        assert Path(out).exists()

    def test_posts_per_week_respected(self):
        result = _run("calendar", "generate", "--niche", "gaming",
                      "--weeks", "1", "--posts-per-week", "3", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["weeks"][0]["posts"] is not None
        assert len(data["weeks"][0]["posts"]) <= 3


# ════════════════════════════════════════════════════════════════════
# Theme page commands
# ════════════════════════════════════════════════════════════════════

class TestThemeCLI:
    def test_guide_overview(self):
        result = _run("theme", "guide")
        assert result.returncode == 0
        assert len(result.stdout) > 200

    def test_guide_json_output(self):
        result = _run("theme", "guide", "--topic", "monetize", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_guide_all_topics(self):
        result = _run("theme", "guide", "--topic", "all", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) > 5

    def test_niches_all_json(self):
        result = _run("theme", "niches", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 10
        assert "niche" in data[0]
        assert "growth_potential" in data[0]

    def test_niches_by_category(self):
        result = _run("theme", "niches", "--category", "fitness", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert all(r["category"] == "fitness" for r in data)

    def test_convert_personal_to_theme(self):
        result = _run("theme", "convert", "--from-type", "personal", "--to-type", "theme")
        assert result.returncode == 0
        assert len(result.stdout) > 100

    def test_convert_json_output(self):
        result = _run("theme", "convert", "--from-type", "meme", "--to-type", "theme", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_setup_checklist_output(self):
        result = _run("theme", "setup", "--niche", "fitness")
        assert result.returncode == 0
        assert "fitness" in result.stdout.lower()
        assert "☐" in result.stdout

    def test_setup_checklist_json(self):
        result = _run("theme", "setup", "--niche", "travel", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert len(data) > 0


# ════════════════════════════════════════════════════════════════════
# YouTube commands (skipped without API key)
# ════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(
    not os.environ.get("YOUTUBE_API_KEY"),
    reason="YOUTUBE_API_KEY not set — skipping YouTube live API tests",
)
class TestYouTubeCLILive:
    def test_trending_us(self):
        result = _run("youtube", "trending", "--region", "US", "--limit", "5", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "title" in data[0]
        assert "views" in data[0]

    def test_trending_music_category(self):
        result = _run("youtube", "music", "--region", "US", "--limit", "5", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)

    def test_hashtags_niche(self):
        result = _run("youtube", "hashtags", "--niche", "fitness", "--limit", "10", "--json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        for item in data:
            assert "tag" in item
            assert "video_count" in item


# ════════════════════════════════════════════════════════════════════
# Error handling
# ════════════════════════════════════════════════════════════════════

class TestErrorHandling:
    def test_youtube_no_api_key_exits_nonzero(self):
        env = {k: v for k, v in os.environ.items() if k != "YOUTUBE_API_KEY"}
        result = subprocess.run(
            CLI + ["youtube", "trending"],
            capture_output=True, text=True,
            env=env,
        )
        assert result.returncode != 0

    def test_optimize_hashtags_missing_niche(self):
        result = _run("optimize", "hashtags")  # missing required --niche
        assert result.returncode != 0

    def test_calendar_generate_missing_niche(self):
        result = _run("calendar", "generate")  # missing required --niche
        assert result.returncode != 0

    def test_theme_setup_missing_niche(self):
        result = _run("theme", "setup")  # missing required --niche
        assert result.returncode != 0
