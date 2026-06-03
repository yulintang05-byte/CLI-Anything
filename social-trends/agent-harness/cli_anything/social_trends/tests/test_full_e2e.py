"""End-to-end tests for social-trends CLI — CLI subprocess + integration tests."""

import json
import subprocess
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

HARNESS_DIR = Path(__file__).parent.parent.parent.parent


def run_cli(*args, env=None):
    """Run the CLI as a subprocess and return (returncode, stdout, stderr)."""
    base_env = os.environ.copy()
    base_env["PYTHONPATH"] = str(HARNESS_DIR)
    if env:
        base_env.update(env)
    result = subprocess.run(
        [sys.executable, "-m", "cli_anything.social_trends.social_trends_cli", *args],
        capture_output=True, text=True, cwd=str(HARNESS_DIR), env=base_env,
        timeout=30,
    )
    return result.returncode, result.stdout, result.stderr


# ── CLI Smoke Tests ────────────────────────────────────────────────────

class TestCLISmoke:
    def test_help(self):
        rc, out, _ = run_cli("--help")
        assert rc == 0
        assert "Social Trends CLI" in out or "viral trends" in out.lower()

    def test_trends_help(self):
        rc, out, _ = run_cli("trends", "--help")
        assert rc == 0
        assert "scrape" in out.lower() or "hashtags" in out.lower()

    def test_account_help(self):
        rc, out, _ = run_cli("account", "--help")
        assert rc == 0

    def test_theme_page_help(self):
        rc, out, _ = run_cli("theme-page", "--help")
        assert rc == 0

    def test_config_help(self):
        rc, out, _ = run_cli("config", "--help")
        assert rc == 0

    def test_invalid_command(self):
        rc, _, err = run_cli("nonexistent-command")
        assert rc != 0


# ── Theme Page E2E (no network) ────────────────────────────────────────

class TestThemePageE2E:
    def test_niches_list(self):
        rc, out, _ = run_cli("theme-page", "niches")
        assert rc == 0
        assert "fitness" in out.lower()
        assert "finance" in out.lower()

    def test_niches_list_json(self):
        rc, out, _ = run_cli("--json", "theme-page", "niches")
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert "fitness" in data

    def test_guide_fitness(self):
        rc, out, _ = run_cli("theme-page", "guide", "--niche", "fitness")
        assert rc == 0
        assert "FITNESS" in out
        assert "monetization" in out.lower() or "Monetization" in out

    def test_guide_finance(self):
        rc, out, _ = run_cli("theme-page", "guide", "--niche", "finance")
        assert rc == 0
        assert "FINANCE" in out

    def test_guide_json(self):
        rc, out, _ = run_cli("--json", "theme-page", "guide", "--niche", "fitness")
        assert rc == 0
        data = json.loads(out)
        assert data["niche"] == "fitness"
        assert "bio_formula" in data
        assert "growth_playbook" in data

    def test_guide_unknown_niche(self):
        rc, out, _ = run_cli("theme-page", "guide", "--niche", "xyz_unknown_niche")
        assert rc == 0  # falls back to generic guide, doesn't error

    def test_convert_command(self):
        rc, out, _ = run_cli("theme-page", "convert", "--niche", "fitness", "--platform", "tiktok")
        assert rc == 0
        assert "BIO" in out.upper() or "CONVERT" in out.upper() or "tip" in out.lower()

    def test_convert_json(self):
        rc, out, _ = run_cli("--json", "theme-page", "convert", "--niche", "fitness", "--platform", "tiktok")
        assert rc == 0
        data = json.loads(out)
        assert "tips" in data
        assert "funnel" in data

    def test_calendar_command(self):
        rc, out, _ = run_cli("theme-page", "calendar", "--niche", "fitness")
        assert rc == 0
        assert "MONDAY" in out.upper() or "monday" in out.lower()

    def test_calendar_json(self):
        rc, out, _ = run_cli("--json", "theme-page", "calendar", "--niche", "finance")
        assert rc == 0
        data = json.loads(out)
        assert "calendar" in data
        assert "monday" in data["calendar"]


# ── Account E2E (no network) ───────────────────────────────────────────

class TestAccountE2E:
    def test_account_list_empty(self, tmp_path, monkeypatch):
        env = {"XDG_CONFIG_HOME": str(tmp_path)}
        rc, out, _ = run_cli("account", "list")
        assert rc == 0

    def test_config_set_get(self, tmp_path):
        rc, out, err = run_cli("config", "set", "default_country", "US")
        assert rc == 0
        assert "US" in out or "default_country" in out

    def test_config_get(self):
        rc, out, err = run_cli("config", "get")
        assert rc == 0  # returns even if empty

    def test_config_path(self):
        rc, out, _ = run_cli("config", "path")
        assert rc == 0
        assert "social-trends" in out.lower() or "config" in out.lower()

    def test_config_set_json(self):
        rc, out, _ = run_cli("--json", "config", "set", "default_country", "UK")
        assert rc == 0
        data = json.loads(out)
        assert data.get("key") == "default_country"

    def test_session_history_empty(self):
        rc, out, _ = run_cli("session", "history")
        assert rc == 0

    def test_session_status(self):
        rc, out, _ = run_cli("session", "status")
        assert rc == 0


# ── Scraper E2E (mocked network) ──────────────────────────────────────

class TestScraperMocked:
    """Tests that mock network calls to verify scraper logic."""

    def _mock_videos(self):
        return [
            {
                "platform": "tiktok",
                "title": "Best Fitness Tips #fitness #gym",
                "channel": "fitnessguru",
                "views": 1000000,
                "likes": 50000,
                "shares": 5000,
                "comments": 2000,
                "tags": ["FitnessChallenge"],
                "hashtags": ["#fitness", "#gym", "#workout"],
                "description": "Amazing workout tips #fitness",
                "url": "https://www.tiktok.com/@fitnessguru/video/1",
                "thumbnail": "",
                "duration": 60,
                "upload_date": "1700000000",
                "categories": ["fitness"],
                "music_used": {"title": "Power Song", "artist": "DJ Energy", "id": "1", "duration": 30},
            },
            {
                "platform": "youtube",
                "title": "10 Best Exercises for Beginners",
                "channel": "FitnessChannel",
                "views": 5000000,
                "likes": 100000,
                "shares": 0,
                "comments": 8000,
                "tags": ["fitness", "workout", "beginner"],
                "hashtags": ["#fitness", "#beginner", "#workout"],
                "description": "Great workout #fitness #beginner",
                "url": "https://youtube.com/watch?v=abc123",
                "thumbnail": "",
                "duration": 600,
                "upload_date": "20241101",
                "categories": ["Sports"],
                "music_used": None,
            },
        ]

    def test_analyze_trends_on_mocked_data(self):
        from cli_anything.social_trends.core.trends import analyze_trends
        report = analyze_trends(self._mock_videos())
        assert report["platform_breakdown"]["total"] == 2
        assert len(report["top_hashtags"]) > 0
        assert report["engagement_stats"]["avg_views"] == 3000000

    def test_get_hashtags_on_mocked_data(self):
        from cli_anything.social_trends.core.scraper import get_all_hashtags
        tags = get_all_hashtags(self._mock_videos())
        names = [t["hashtag"] for t in tags]
        assert "#fitness" in names

    def test_get_sounds_on_mocked_data(self):
        from cli_anything.social_trends.core.scraper import get_all_sounds
        sounds = get_all_sounds(self._mock_videos())
        assert len(sounds) == 1
        assert sounds[0]["title"] == "Power Song"

    @patch("cli_anything.social_trends.core.scraper.scrape_youtube_trending")
    def test_scrape_platform_youtube(self, mock_scrape):
        mock_scrape.return_value = [self._mock_videos()[1]]
        from cli_anything.social_trends.core.scraper import scrape_platform
        videos = scrape_platform("youtube", limit=1)
        assert len(videos) == 1
        assert videos[0]["platform"] == "youtube"

    @patch("cli_anything.social_trends.core.scraper.scrape_tiktok_trending")
    def test_scrape_platform_tiktok(self, mock_scrape):
        mock_scrape.return_value = [self._mock_videos()[0]]
        from cli_anything.social_trends.core.scraper import scrape_platform
        videos = scrape_platform("tiktok", limit=1)
        assert len(videos) == 1
        assert videos[0]["platform"] == "tiktok"

    def test_optimize_account_with_mocked_trends(self):
        from cli_anything.social_trends.core.trends import analyze_trends
        from cli_anything.social_trends.core.optimizer import optimize_account
        trend_data = analyze_trends(self._mock_videos())
        plan = optimize_account("tiktok", "fitness", trend_data, followers=1500)
        assert plan["optimization_score"]["score"] > 0
        assert len(plan["content_ideas"]) >= 5
        assert plan["posting_schedule"]["7_day_calendar"]

    def test_optimize_all_with_no_accounts(self):
        from cli_anything.social_trends.core.optimizer import optimize_all_accounts
        from cli_anything.social_trends.core.trends import analyze_trends
        from unittest.mock import patch as mp
        trend_data = analyze_trends(self._mock_videos())
        with mp("cli_anything.social_trends.core.optimizer.load_accounts", return_value=[]):
            result = optimize_all_accounts(trend_data)
            assert result == []


# ── JSON Output Format ─────────────────────────────────────────────────

class TestJSONOutput:
    def test_theme_guide_json_structure(self):
        rc, out, _ = run_cli("--json", "theme-page", "guide", "--niche", "pets")
        assert rc == 0
        data = json.loads(out)
        assert "niche" in data
        assert "overview" in data
        assert "conversion_funnel" in data
        for stage in ("awareness", "interest", "desire", "action"):
            assert stage in data["conversion_funnel"]

    def test_theme_niches_json_is_list(self):
        rc, out, _ = run_cli("--json", "theme-page", "niches")
        assert rc == 0
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) >= 8

    def test_session_status_json(self):
        rc, out, _ = run_cli("--json", "session", "status")
        assert rc == 0
        data = json.loads(out)
        assert "history_count" in data
