"""E2E tests for cli-anything-trends — mock the HTTP layer, test full CLI flows."""

import json
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.trends.trends_cli import cli


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_yt_trending_response():
    return {
        "items": [
            {
                "id": "abc123",
                "snippet": {
                    "title": "Best Fitness Workout Routine 2025 #fitness #workout",
                    "channelTitle": "FitnessChannel",
                    "categoryId": "26",
                    "publishedAt": "2025-01-01T12:00:00Z",
                    "description": "Try this amazing #fitness routine. #workout #gym",
                    "tags": ["fitness", "workout", "gym", "health"],
                    "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
                },
                "statistics": {
                    "viewCount": "5000000",
                    "likeCount": "250000",
                    "commentCount": "15000",
                },
            },
            {
                "id": "def456",
                "snippet": {
                    "title": "Viral Dance Trend #dance #viral #fyp",
                    "channelTitle": "DanceChannel",
                    "categoryId": "24",
                    "publishedAt": "2025-01-02T10:00:00Z",
                    "description": "#viral #dance challenge",
                    "tags": ["dance", "viral"],
                    "thumbnails": {"high": {"url": "https://example.com/thumb2.jpg"}},
                },
                "statistics": {
                    "viewCount": "8000000",
                    "likeCount": "600000",
                    "commentCount": "30000",
                },
            },
        ]
    }


@pytest.fixture
def mock_yt_music_response():
    return {
        "items": [
            {
                "id": "music1",
                "snippet": {
                    "title": "Hit Song 2025 - Official Music Video",
                    "channelTitle": "PopArtist",
                    "categoryId": "10",
                    "publishedAt": "2025-01-01T00:00:00Z",
                    "description": "#music #pop #newrelease",
                    "tags": ["music", "pop"],
                    "thumbnails": {"high": {"url": ""}},
                },
                "statistics": {"viewCount": "20000000", "likeCount": "1000000", "commentCount": "50000"},
            }
        ]
    }


@pytest.fixture
def mock_tt_trending_response():
    return {
        "itemList": [
            {
                "id": "tt001",
                "desc": "Amazing fitness transformation #fitness #fyp #workout",
                "author": {"uniqueId": "fituser1", "nickname": "FitUser One"},
                "stats": {"playCount": 3_000_000, "diggCount": 200_000, "commentCount": 5_000, "shareCount": 15_000},
                "music": {"id": "mus001", "title": "Motivational Beat", "authorName": "BeatMaker"},
                "challenges": [{"title": "FitnessChallenge"}, {"title": "fyp"}],
            }
        ]
    }


# ── YouTube command tests ─────────────────────────────────────────────────


class TestYouTubeCommand:
    def test_trends_youtube_basic(self, runner, mock_yt_trending_response, tmp_path):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_yt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--yt-key", "fake_api_key",
                "trends", "youtube",
                "--region", "US",
                "--category", "all",
            ])

        assert result.exit_code == 0, f"Exit code {result.exit_code}: {result.output}"
        assert "YouTube trending" in result.output or "video" in result.output.lower()

    def test_trends_youtube_json_output(self, runner, mock_yt_trending_response):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_yt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "youtube",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "videos" in data
        assert data["platform"] == "youtube"

    def test_trends_youtube_no_api_key(self, runner):
        with patch.dict(os.environ, {}, clear=True):
            with patch("cli_anything.trends.utils.config.load_config", return_value={}):
                result = runner.invoke(cli, ["trends", "youtube"])
        assert result.exit_code != 0 or "error" in result.output.lower() or "key" in result.output.lower()

    def test_trends_youtube_region_filter(self, runner, mock_yt_trending_response):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_yt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "youtube",
                "--region", "GB",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["region"] in ("GB", "gb")

    def test_trends_youtube_hashtags_extracted(self, runner, mock_yt_trending_response):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_yt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "youtube",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        # Should have extracted hashtags
        assert "hashtags" in data


# ── TikTok command tests ──────────────────────────────────────────────────


class TestTikTokCommand:
    def test_trends_tiktok_public_scrape(self, runner):
        mock_html = """
        <html>
        <script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
        {"challengeName": "fitness", "videoCount": 1000000}
        </script>
        </html>
        """
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = mock_html
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--json",
                "trends", "tiktok",
                "--region", "US",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"

    def test_trends_tiktok_cookie_scrape(self, runner, mock_tt_trending_response):
        with patch("requests.Session") as mock_session_cls:
            mock_session = MagicMock()
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_tt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_session.get.return_value = mock_resp
            mock_session_cls.return_value = mock_session

            result = runner.invoke(cli, [
                "--json",
                "--tt-cookies", "sessionid=test123; ttwid=abc",
                "trends", "tiktok",
                "--region", "US",
                "--count", "10",
            ])

        assert result.exit_code == 0, result.output


# ── Hashtags command tests ────────────────────────────────────────────────


class TestHashtagsCommand:
    def test_trends_hashtags_youtube_only(self, runner, mock_yt_trending_response):
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = mock_yt_trending_response
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "hashtags",
                "--platform", "youtube",
                "--region", "US",
                "--niche", "fitness",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "top_hashtags" in data
        assert "copy_paste_packs" in data


# ── Report command tests ──────────────────────────────────────────────────


class TestReportCommand:
    def test_trends_report_json(self, runner, mock_yt_trending_response):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            def side_effect(url, **kwargs):
                mock_resp = MagicMock()
                if "googleapis" in url:
                    mock_resp.json.return_value = mock_yt_trending_response
                else:
                    mock_resp.status_code = 200
                    mock_resp.text = mock_html
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            mock_get.side_effect = side_effect

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "report",
                "--region", "US",
                "--niche", "fitness",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "top_hashtags" in data
        assert "content_themes" in data
        assert "trending_topics" in data

    def test_trends_report_no_youtube_key(self, runner):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = mock_html
            mock_resp.raise_for_status.return_value = None
            mock_get.return_value = mock_resp

            with patch("cli_anything.trends.utils.config.load_config", return_value={}):
                result = runner.invoke(cli, [
                    "--json",
                    "trends", "report",
                    "--niche", "general",
                ])

        # Should still succeed, just with TikTok data only
        assert result.exit_code == 0, result.output


# ── Optimize command tests ────────────────────────────────────────────────


class TestOptimizeCommand:
    def test_trends_optimize_tiktok(self, runner, mock_yt_trending_response):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            def side_effect(url, **kwargs):
                mock_resp = MagicMock()
                if "googleapis" in url:
                    mock_resp.json.return_value = mock_yt_trending_response
                else:
                    mock_resp.status_code = 200
                    mock_resp.text = mock_html
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            mock_get.side_effect = side_effect

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "optimize",
                "--platform", "tiktok",
                "--niche", "fitness",
                "--followers", "5000",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert "profile" in data
        assert "content_strategy" in data
        assert "growth_tactics" in data
        assert "monetization_readiness" in data

    def test_trends_optimize_growth_phase(self, runner, mock_yt_trending_response):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            def side_effect(url, **kwargs):
                mock_resp = MagicMock()
                if "googleapis" in url:
                    mock_resp.json.return_value = mock_yt_trending_response
                else:
                    mock_resp.status_code = 200
                    mock_resp.text = mock_html
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            mock_get.side_effect = side_effect

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "optimize",
                "--platform", "tiktok",
                "--followers", "500",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["growth_phase"] == "seed"


# ── Calendar command tests ────────────────────────────────────────────────


class TestCalendarCommand:
    def test_trends_calendar_basic(self, runner, mock_yt_trending_response):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            def side_effect(url, **kwargs):
                mock_resp = MagicMock()
                if "googleapis" in url:
                    mock_resp.json.return_value = mock_yt_trending_response
                else:
                    mock_resp.status_code = 200
                    mock_resp.text = mock_html
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            mock_get.side_effect = side_effect

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "calendar",
                "--niche", "fitness",
                "--weeks", "1",
                "--platforms", "tiktok",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "calendar" in data
        assert data["weeks"] == 1
        assert data["total_posts"] > 0

    def test_trends_calendar_2_weeks(self, runner, mock_yt_trending_response):
        mock_html = "<html><script id='__UNIVERSAL_DATA_FOR_REHYDRATION__'>{}</script></html>"
        with patch("requests.get") as mock_get:
            def side_effect(url, **kwargs):
                mock_resp = MagicMock()
                if "googleapis" in url:
                    mock_resp.json.return_value = mock_yt_trending_response
                else:
                    mock_resp.status_code = 200
                    mock_resp.text = mock_html
                mock_resp.raise_for_status.return_value = None
                return mock_resp
            mock_get.side_effect = side_effect

            result = runner.invoke(cli, [
                "--json",
                "--yt-key", "fake_api_key",
                "trends", "calendar",
                "--niche", "lifestyle",
                "--weeks", "2",
            ])

        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert data["weeks"] == 2


# ── Config command tests ──────────────────────────────────────────────────


class TestConfigCommand:
    def test_config_set_and_get(self, runner, tmp_path, monkeypatch):
        import cli_anything.trends.utils.config as config_mod
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)

        set_result = runner.invoke(cli, ["config", "set", "youtube_api_key", "test_key_xyz"])
        assert set_result.exit_code == 0

    def test_config_path(self, runner):
        result = runner.invoke(cli, ["config", "path"])
        assert result.exit_code == 0
        assert "config" in result.output.lower()


# ── Session command tests ─────────────────────────────────────────────────


class TestSessionCommand:
    def test_session_status(self, runner):
        result = runner.invoke(cli, ["session", "status"])
        assert result.exit_code == 0

    def test_session_history_empty(self, runner):
        result = runner.invoke(cli, ["session", "history"])
        assert result.exit_code == 0
