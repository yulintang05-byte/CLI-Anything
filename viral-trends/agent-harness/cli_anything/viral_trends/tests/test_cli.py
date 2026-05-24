"""CLI integration tests using Click's test runner (no network)."""

import json
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_anything.viral_trends.viral_trends_cli import cli


# Shared mock data
_MOCK_YT = {
    "platform": "youtube",
    "category": "now",
    "region": "US",
    "fetched_at": "2025-01-01T00:00:00+00:00",
    "videos": [
        {
            "video_id": "abc123",
            "url": "https://www.youtube.com/watch?v=abc123",
            "title": "Test Video #finance #viral",
            "channel": "TestChannel",
            "views": "1M views",
            "published": "1 day ago",
            "duration": "3:45",
            "hashtags": ["#finance", "#viral"],
        }
    ],
    "hashtags": [{"tag": "#finance", "count": 2}, {"tag": "#viral", "count": 1}],
    "music_tracks": [],
    "total": 1,
}

_MOCK_YT_MUSIC = {
    "platform": "youtube",
    "category": "music",
    "region": "US",
    "fetched_at": "2025-01-01T00:00:00+00:00",
    "videos": [],
    "hashtags": [],
    "music_tracks": [{"artist": "Test Artist", "track": "Test Song", "video_url": "https://yt.com/v"}],
    "total": 0,
}

_MOCK_TT = {
    "platform": "tiktok",
    "region": "US",
    "fetched_at": "2025-01-01T00:00:00+00:00",
    "videos": [
        {
            "video_id": "tt123",
            "url": "https://www.tiktok.com/@test/video/tt123",
            "description": "#finance tips #fyp",
            "author": {"username": "testuser", "nickname": "Test User", "followers": 5000},
            "stats": {"plays": 100000, "likes": 5000, "comments": 200, "shares": 100},
            "music": {"id": "m1", "title": "Trending Song", "author": "Artist", "original": False},
            "hashtags": ["#finance", "#fyp"],
            "duration": 30,
        }
    ],
    "hashtags": [{"tag": "#finance", "count": 3}, {"tag": "#fyp", "count": 5}],
    "trending_music": [{"id": "m1", "title": "Trending Song", "author": "Artist", "original": False, "video_count": 1}],
    "total": 1,
}


def _mk_runner():
    return CliRunner()


# ── YouTube commands ───────────────────────────────────────────────────────────

class TestYouTubeCommands:
    def test_youtube_trending_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT):
            result = runner.invoke(cli, ["--json", "youtube-trending", "--region", "us"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"

    def test_youtube_trending_human(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT):
            result = runner.invoke(cli, ["youtube-trending"])
        assert result.exit_code == 0
        assert "youtube" in result.output.lower()

    def test_youtube_music_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC):
            result = runner.invoke(cli, ["--json", "youtube-music"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"

    def test_youtube_hashtag_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.search_hashtag", return_value={
            "platform": "youtube", "hashtag": "#finance", "videos": [], "total": 0, "fetched_at": ""
        }):
            result = runner.invoke(cli, ["--json", "youtube-hashtag", "#finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["hashtag"] == "#finance"


# ── TikTok commands ────────────────────────────────────────────────────────────

class TestTikTokCommands:
    def test_tiktok_trending_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "tiktok-trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"

    def test_tiktok_sounds_json(self):
        runner = _mk_runner()
        mock = {"platform": "tiktok", "region": "US", "fetched_at": "", "trending_sounds": [], "total": 0}
        with patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending_sounds", return_value=mock):
            result = runner.invoke(cli, ["--json", "tiktok-sounds"])
        assert result.exit_code == 0

    def test_tiktok_hashtag_json(self):
        runner = _mk_runner()
        mock = {"platform": "tiktok", "hashtag": "#fitness", "videos": [], "total": 0, "fetched_at": ""}
        with patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_hashtag_trends", return_value=mock):
            result = runner.invoke(cli, ["--json", "tiktok-hashtag", "#fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["hashtag"] == "#fitness"

    def test_tiktok_creators_json(self):
        runner = _mk_runner()
        mock = {"platform": "tiktok", "region": "US", "fetched_at": "", "trending_creators": [], "total": 0}
        with patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_creator_trends", return_value=mock):
            result = runner.invoke(cli, ["--json", "tiktok-creators"])
        assert result.exit_code == 0


# ── Cross-platform commands ────────────────────────────────────────────────────

class TestCrossPlatformCommands:
    def _patch_both(self):
        return {
            "cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending": _MOCK_YT,
            "cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends": _MOCK_YT_MUSIC,
            "cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending": _MOCK_TT,
        }

    def test_all_trends_json(self):
        runner = _mk_runner()
        patches = self._patch_both()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "all-trends"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_hashtags" in data
        assert "top_music" in data
        assert "content_opportunities" in data

    def test_hashtags_no_niche(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "hashtags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_hashtags" in data

    def test_hashtags_with_niche(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "hashtags", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "finance"

    def test_sounds_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending_sounds", return_value={
                 "platform": "tiktok", "region": "US", "fetched_at": "", "trending_sounds": [], "total": 0
             }):
            result = runner.invoke(cli, ["--json", "sounds"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_sounds" in data


# ── Account optimization commands ──────────────────────────────────────────────

class TestAccountCommands:
    def test_optimize_account_json(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "optimize-account", "--platform", "tiktok",
                                     "--type", "theme_page", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "posting_schedule" in data
        assert "hashtag_strategy" in data

    def test_content_calendar_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "content-calendar", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "week_calendar" in data
        assert len(data["week_calendar"]) == 7

    def test_growth_hacks_json(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "growth-hacks", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "growth_hacks" in data

    def test_theme_page_roadmap(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "theme-page", "--action", "roadmap",
                                     "--niche", "finance", "--followers", "0"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["current_phase"] == 1
        assert len(data["phases"]) == 4

    def test_theme_page_niches(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "theme-page", "--action", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_niches" in data

    def test_theme_page_conversion(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "theme-page", "--action", "conversion"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "conversion_tactics" in data

    def test_theme_page_tools(self):
        runner = _mk_runner()
        result = runner.invoke(cli, ["--json", "theme-page", "--action", "tools"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tools_stack" in data


# ── Daily brief ────────────────────────────────────────────────────────────────

class TestDailyBrief:
    def test_daily_brief_json(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "daily-brief", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_5_hashtags" in data
        assert "top_3_sounds" in data
        assert "todays_posting_plan" in data
        assert "quick_tip" in data

    def test_daily_brief_no_niche(self):
        runner = _mk_runner()
        with patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_trending", return_value=_MOCK_YT), \
             patch("cli_anything.viral_trends.viral_trends_cli.youtube_scraper.fetch_music_trends", return_value=_MOCK_YT_MUSIC), \
             patch("cli_anything.viral_trends.viral_trends_cli.tiktok_scraper.fetch_trending", return_value=_MOCK_TT):
            result = runner.invoke(cli, ["--json", "daily-brief"])
        assert result.exit_code == 0
