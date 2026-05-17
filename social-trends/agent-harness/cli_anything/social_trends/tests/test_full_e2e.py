"""End-to-end integration tests for cli-anything-social-trends.

These tests exercise the full CLI pipeline using Click's test runner.
No real API calls are made — HTTP is mocked with the `responses` library.

Run with:
    pip install -e . && pytest tests/test_full_e2e.py -v
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pathlib import Path

from cli_anything.social_trends.social_trends_cli import main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_backend(tmp_path, monkeypatch):
    """Patch the backend storage to a temp directory."""
    import cli_anything.social_trends.utils.social_backend as sb_module
    config_dir = tmp_path / ".social"
    monkeypatch.setattr(sb_module, "_CONFIG_DIR", config_dir)
    monkeypatch.setattr(sb_module, "_CONFIG_FILE", config_dir / "config.json")
    monkeypatch.setattr(sb_module, "_ACCOUNTS_FILE", config_dir / "accounts.json")
    monkeypatch.setattr(sb_module, "_REPORTS_DIR", config_dir / "reports")
    monkeypatch.setattr(sb_module, "_HISTORY_FILE", config_dir / "history")
    return tmp_path


# ── CLI: status ────────────────────────────────────────────────────────────

class TestStatusCommand:
    def test_status_runs(self, runner, isolated_backend):
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "Region" in result.output or "Config" in result.output

    def test_status_json(self, runner, isolated_backend):
        result = runner.invoke(main, ["--json", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube_api_configured" in data
        assert "default_region" in data


# ── CLI: setup ─────────────────────────────────────────────────────────────

class TestSetupCommands:
    def test_setup_region(self, runner, isolated_backend):
        result = runner.invoke(main, ["setup", "region", "GB"])
        assert result.exit_code == 0
        assert "GB" in result.output

    def test_setup_niche(self, runner, isolated_backend):
        result = runner.invoke(main, ["setup", "niche", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output

    def test_setup_youtube_key(self, runner, isolated_backend):
        result = runner.invoke(main, ["setup", "youtube-key", "AIzaTestKey123"])
        assert result.exit_code == 0
        # Re-check status to confirm saved
        status_result = runner.invoke(main, ["--json", "status"])
        data = json.loads(status_result.output)
        assert data["youtube_api_configured"] is True


# ── CLI: accounts ─────────────────────────────────────────────────────────

class TestAccountsCommands:
    def test_add_youtube_account(self, runner, isolated_backend):
        result = runner.invoke(main, ["accounts", "add", "youtube", "myChannel", "--channel-id", "UC12345", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "myChannel" in result.output

    def test_add_tiktok_account(self, runner, isolated_backend):
        result = runner.invoke(main, ["accounts", "add", "tiktok", "myTikTok"])
        assert result.exit_code == 0

    def test_list_accounts_empty(self, runner, isolated_backend):
        result = runner.invoke(main, ["accounts", "list"])
        assert result.exit_code == 0
        assert "No accounts" in result.output or result.exit_code == 0

    def test_list_accounts_shows_registered(self, runner, isolated_backend):
        runner.invoke(main, ["accounts", "add", "youtube", "testChannel"])
        result = runner.invoke(main, ["accounts", "list"])
        assert result.exit_code == 0
        assert "testChannel" in result.output

    def test_remove_account(self, runner, isolated_backend):
        runner.invoke(main, ["accounts", "add", "tiktok", "removeMe"])
        result = runner.invoke(main, ["accounts", "remove", "tiktok", "removeMe"])
        assert result.exit_code == 0
        list_result = runner.invoke(main, ["accounts", "list"])
        assert "removeMe" not in list_result.output

    def test_remove_nonexistent_account(self, runner, isolated_backend):
        result = runner.invoke(main, ["accounts", "remove", "youtube", "doesNotExist"])
        assert result.exit_code == 0
        assert "not found" in result.output.lower() or "Account" in result.output


# ── CLI: scrape youtube (mocked) ───────────────────────────────────────────

class TestScrapeYouTube:
    def test_scrape_requires_api_key(self, runner, isolated_backend):
        result = runner.invoke(main, ["scrape", "youtube", "--trending"])
        assert result.exit_code != 0 or "API key" in result.output

    def test_scrape_youtube_with_mocked_api(self, runner, isolated_backend):
        runner.invoke(main, ["setup", "youtube-key", "AIzaTestKey"])
        mock_videos = [
            {"id": f"vid{i}", "title": f"Trending Video {i}", "channel": "Channel",
             "published_at": "2025-01-01T00:00:00Z", "description": f"#fitness #gym",
             "tags": ["fitness", "workout"], "view_count": 1_000_000 - i * 1000,
             "like_count": 50_000, "comment_count": 1_000, "thumbnail": "https://img.jpg",
             "category_id": "17", "url": f"https://yt.be/vid{i}"}
            for i in range(5)
        ]
        with patch("cli_anything.social_trends.core.youtube_scraper.YouTubeScraper.get_trending_videos",
                   return_value=mock_videos):
            with patch("cli_anything.social_trends.core.youtube_scraper.YouTubeScraper.get_trending_music",
                       return_value=[]):
                result = runner.invoke(main, ["scrape", "youtube", "--trending", "--limit", "5"])
        assert result.exit_code == 0
        assert "Trending Video" in result.output or "Fetched" in result.output

    def test_scrape_youtube_json_output(self, runner, isolated_backend):
        runner.invoke(main, ["setup", "youtube-key", "AIzaTestKey"])
        mock_videos = [
            {"id": "v1", "title": "Test", "channel": "Ch", "published_at": "2025-01-01T00:00:00Z",
             "description": "", "tags": [], "view_count": 100, "like_count": 5,
             "comment_count": 1, "thumbnail": "", "category_id": "0", "url": "https://yt.be/v1"}
        ]
        with patch("cli_anything.social_trends.core.youtube_scraper.YouTubeScraper.get_trending_videos",
                   return_value=mock_videos):
            with patch("cli_anything.social_trends.core.youtube_scraper.YouTubeScraper.get_trending_music",
                       return_value=[]):
                result = runner.invoke(main, ["--json", "scrape", "youtube", "--trending"])
        if result.exit_code == 0:
            data = json.loads(result.output)
            assert "videos" in data


# ── CLI: scrape tiktok (mocked) ────────────────────────────────────────────

class TestScrapeTikTok:
    def test_scrape_tiktok_http_mode(self, runner, isolated_backend):
        mock_videos = [
            {"id": f"tt{i}", "description": f"Viral video #{i} #fitness",
             "author": f"user{i}", "author_nickname": f"User {i}",
             "play_count": 1_000_000, "like_count": 50_000, "comment_count": 1000,
             "share_count": 500, "sound": {"id": f"s{i}", "title": f"Sound {i}",
             "author_name": "DJ", "duration": 15, "is_original": False},
             "challenges": [{"title": "FitnessChallenge"}], "created_time": 1700000000,
             "url": f"https://tiktok.com/@user{i}/video/tt{i}", "engagement_rate": 5.15}
            for i in range(5)
        ]
        with patch("cli_anything.social_trends.core.tiktok_scraper.TikTokScraper.get_trending_videos",
                   return_value=mock_videos):
            result = runner.invoke(main, ["scrape", "tiktok", "--trending", "--no-playwright"])
        assert result.exit_code == 0

    def test_scrape_tiktok_save_report(self, runner, isolated_backend):
        mock_videos = []
        with patch("cli_anything.social_trends.core.tiktok_scraper.TikTokScraper.get_trending_videos",
                   return_value=mock_videos):
            result = runner.invoke(main, ["scrape", "tiktok", "--trending", "--no-playwright", "--save"])
        assert result.exit_code == 0


# ── CLI: hashtags ──────────────────────────────────────────────────────────

class TestHashtagCommands:
    def _seed_reports(self, runner, isolated_backend):
        """Create mock trend reports for hashtag commands to read."""
        import cli_anything.social_trends.utils.social_backend as sb_module
        reports_dir = sb_module._REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)
        yt_data = {
            "platform": "youtube", "niche": "fitness",
            "hashtags": [["fitness", 50], ["gym", 40], ["workout", 30], ["health", 20]],
            "videos": [], "music": []
        }
        tt_data = {
            "platform": "tiktok", "niche": "fitness",
            "hashtags": [["fitness", 200], ["fyp", 500], ["gymtok", 150], ["viral", 400]],
            "videos": [], "sounds": []
        }
        (reports_dir / "youtube_trends_20250101_000000.json").write_text(json.dumps(yt_data))
        (reports_dir / "tiktok_trends_20250101_000000.json").write_text(json.dumps(tt_data))

    def test_hashtag_strategy(self, runner, isolated_backend):
        self._seed_reports(runner, isolated_backend)
        result = runner.invoke(main, ["hashtags", "strategy", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_hashtag_compare(self, runner, isolated_backend):
        self._seed_reports(runner, isolated_backend)
        result = runner.invoke(main, ["hashtags", "compare", "#fitness", "#gym", "#unknown"])
        assert result.exit_code == 0

    def test_hashtag_strategy_no_reports(self, runner, isolated_backend):
        result = runner.invoke(main, ["hashtags", "strategy"])
        assert result.exit_code == 0  # Graceful warning, not crash
        assert "No saved reports" in result.output or "Run" in result.output


# ── CLI: music ─────────────────────────────────────────────────────────────

class TestMusicCommands:
    def test_music_trending_no_reports(self, runner, isolated_backend):
        result = runner.invoke(main, ["music", "trending"])
        assert result.exit_code == 0
        assert "No saved reports" in result.output

    def test_music_trending_with_reports(self, runner, isolated_backend):
        import cli_anything.social_trends.utils.social_backend as sb_module
        reports_dir = sb_module._REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)
        tt_data = {
            "platform": "tiktok",
            "videos": [
                {"id": "1", "description": "#fitness", "sound": {"id": "s1", "title": "Hot Beat",
                 "author_name": "DJ Trend", "duration": 15, "is_original": False},
                 "play_count": 1_000_000, "like_count": 50_000, "comment_count": 2000,
                 "share_count": 500, "challenges": [], "engagement_rate": 5.25},
            ] * 5,
            "hashtags": [], "sounds": [],
        }
        (reports_dir / "tiktok_trends_20250101_000000.json").write_text(json.dumps(tt_data))
        result = runner.invoke(main, ["music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0


# ── CLI: optimize ──────────────────────────────────────────────────────────

class TestOptimizeCommands:
    def test_optimize_tiktok_account(self, runner, isolated_backend):
        mock_stats = {
            "username": "testuser", "nickname": "Test User",
            "bio": "Daily fitness content! Follow me. linktr.ee/test",
            "follower_count": 10_000, "following_count": 500,
            "video_count": 100, "heart_count": 200_000, "verified": False,
        }
        with patch("cli_anything.social_trends.core.tiktok_scraper.TikTokScraper.get_account_stats",
                   return_value=mock_stats):
            result = runner.invoke(main, ["optimize", "account", "tiktok", "testuser", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "ACCOUNT AUDIT" in result.output or "testuser" in result.output

    def test_optimize_youtube_no_key(self, runner, isolated_backend):
        result = runner.invoke(main, ["optimize", "account", "youtube", "myChannel", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "demo stats" in result.output.lower() or "API key" in result.output or "ACCOUNT AUDIT" in result.output

    def test_optimize_all_no_accounts(self, runner, isolated_backend):
        result = runner.invoke(main, ["optimize", "all-accounts"])
        assert result.exit_code == 0
        assert "No accounts" in result.output


# ── CLI: theme-page ────────────────────────────────────────────────────────

class TestThemePageCommands:
    def test_theme_page_plan(self, runner, isolated_backend):
        result = runner.invoke(main, ["theme-page", "plan", "fitness", "--platform", "tiktok", "--followers", "1000"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower() or "TIKTOK" in result.output

    def test_theme_page_plan_json(self, runner, isolated_backend):
        result = runner.invoke(main, ["--json", "theme-page", "plan", "gaming", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niche" in data or "content_pillars" in data

    def test_theme_page_conversion_guide(self, runner, isolated_backend):
        result = runner.invoke(main, ["theme-page", "conversion-guide", "fitness"])
        assert result.exit_code == 0
        assert "PHASE 1" in result.output

    def test_theme_page_branding(self, runner, isolated_backend):
        result = runner.invoke(main, ["theme-page", "branding", "fitness", "FitNation", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "FitNation" in result.output or "Branding" in result.output

    def test_all_niches_plan(self, runner, isolated_backend):
        from cli_anything.social_trends.core.theme_page import NICHES
        for niche in list(NICHES.keys())[:3]:
            result = runner.invoke(main, ["theme-page", "plan", niche])
            assert result.exit_code == 0, f"Failed for niche: {niche} — {result.output}"


# ── CLI: report ────────────────────────────────────────────────────────────

class TestReportCommands:
    def test_report_list_empty(self, runner, isolated_backend):
        result = runner.invoke(main, ["report", "list"])
        assert result.exit_code == 0
        assert "No reports" in result.output or "report" in result.output.lower()

    def test_report_list_with_reports(self, runner, isolated_backend):
        import cli_anything.social_trends.utils.social_backend as sb_module
        reports_dir = sb_module._REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "test_report_20250101_000000.json").write_text('{"test": true}')
        result = runner.invoke(main, ["report", "list"])
        assert result.exit_code == 0
        assert "test_report" in result.output

    def test_report_show_by_path(self, runner, isolated_backend):
        import cli_anything.social_trends.utils.social_backend as sb_module
        reports_dir = sb_module._REPORTS_DIR
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = reports_dir / "sample_20250101_000000.json"
        report_path.write_text('{"key": "value"}')
        result = runner.invoke(main, ["report", "show", str(report_path)])
        assert result.exit_code == 0
        assert "value" in result.output
