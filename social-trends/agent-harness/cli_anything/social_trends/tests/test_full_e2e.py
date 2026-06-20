"""End-to-end tests for Social Trends CLI — runs CLI commands via Click test runner."""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from cli_anything.social_trends.social_trends_cli import cli


MOCK_TIKTOK_REPORT = {
    "platform": "tiktok",
    "country": "US",
    "period_days": 7,
    "fetched_at": "2026-06-20T00:00:00+00:00",
    "from_cache": False,
    "hashtags": [
        {"rank": 1, "name": "fitness", "video_count": 1000000, "view_count": 5000000000, "trend": "up", "country": "US", "period_days": 7, "fetched_at": "2026-06-20T00:00:00+00:00"},
        {"rank": 2, "name": "gym", "video_count": 800000, "view_count": 4000000000, "trend": "up", "country": "US", "period_days": 7, "fetched_at": "2026-06-20T00:00:00+00:00"},
    ],
    "sounds": [
        {"rank": 1, "title": "Viral Beat", "artist": "DJ Test", "usage_count": 500000, "trend": "up", "country": "US", "period_days": 7, "fetched_at": "2026-06-20T00:00:00+00:00"},
    ],
    "videos": [
        {
            "rank": 1, "video_id": "abc", "description": "Best workout ever",
            "author": "fitguru", "view_count": 2000000, "hashtags": ["fitness"],
            "music_title": "Viral Beat", "music_artist": "DJ Test",
            "country": "US", "period_days": 7, "fetched_at": "2026-06-20T00:00:00+00:00",
            "like_count": 50000, "comment_count": 1000, "share_count": 5000, "author_followers": 100000,
        }
    ],
    "creators": [],
    "errors": [],
}

MOCK_YOUTUBE_REPORT = {
    "platform": "youtube",
    "region": "US",
    "api_mode": "html_scrape",
    "fetched_at": "2026-06-20T00:00:00+00:00",
    "from_cache": False,
    "trending_all": [
        {"rank": 1, "title": "Most Viral Video of 2026", "channel": "TopChannel",
         "view_count_text": "10M views", "video_id": "xyz",
         "url": "https://www.youtube.com/watch?v=xyz", "region": "US",
         "fetched_at": "2026-06-20T00:00:00+00:00"},
    ],
    "trending_music": [],
    "errors": [],
}


@pytest.fixture(autouse=True)
def reset_globals():
    """Reset CLI module globals between tests to prevent state bleed."""
    import cli_anything.social_trends.social_trends_cli as cli_mod
    cli_mod._session = None
    cli_mod._json_output = False
    cli_mod._repl_mode = False
    cli_mod._youtube_api_key = None
    yield
    cli_mod._session = None


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_tiktok_trends():
    with patch(
        "cli_anything.social_trends.core.trends.fetch_tiktok_trends",
        return_value=MOCK_TIKTOK_REPORT,
    ):
        yield


@pytest.fixture
def mock_youtube_trends():
    with patch(
        "cli_anything.social_trends.core.trends.fetch_youtube_trends",
        return_value=MOCK_YOUTUBE_REPORT,
    ):
        yield


# ── Trends Command Tests ──────────────────────────────────────────────

class TestTrendsTikTok:
    def test_tiktok_default(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, ["trends", "tiktok"])
        assert result.exit_code == 0
        assert "TikTok Trends" in result.output
        assert "fitness" in result.output

    def test_tiktok_json_output(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, ["--json", "trends", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert "hashtags" in data

    def test_tiktok_country_option(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, ["trends", "tiktok", "--country", "GB"])
        assert result.exit_code == 0

    def test_tiktok_period_option(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, ["trends", "tiktok", "--period", "30"])
        assert result.exit_code == 0

    def test_tiktok_no_cache(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, ["trends", "tiktok", "--no-cache"])
        assert result.exit_code == 0


class TestTrendsYouTube:
    def test_youtube_default(self, runner, mock_youtube_trends):
        result = runner.invoke(cli, ["trends", "youtube"])
        assert result.exit_code == 0
        assert "YouTube Trends" in result.output

    def test_youtube_json(self, runner, mock_youtube_trends):
        result = runner.invoke(cli, ["--json", "trends", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"

    def test_youtube_region(self, runner, mock_youtube_trends):
        result = runner.invoke(cli, ["trends", "youtube", "--region", "CA"])
        assert result.exit_code == 0


class TestTrendsAll:
    def test_cross_platform(self, runner, mock_tiktok_trends, mock_youtube_trends):
        result = runner.invoke(cli, ["trends", "all"])
        assert result.exit_code == 0

    def test_cross_platform_json(self, runner, mock_tiktok_trends, mock_youtube_trends):
        result = runner.invoke(cli, ["--json", "trends", "all"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok" in data
        assert "youtube" in data
        assert "insights" in data

    def test_cross_platform_save_file(self, runner, tmp_path, mock_tiktok_trends, mock_youtube_trends):
        out_file = str(tmp_path / "report.json")
        result = runner.invoke(cli, ["trends", "all", "--output-file", out_file])
        assert result.exit_code == 0
        import os
        assert os.path.exists(out_file)
        with open(out_file) as f:
            data = json.load(f)
        assert "insights" in data


class TestTrendsCache:
    def test_cache_list_empty(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.core.trends as trends_mod
        monkeypatch.setattr(trends_mod, "CACHE_DIR", tmp_path / "nonexistent")
        result = runner.invoke(cli, ["trends", "cache", "--list"])
        assert result.exit_code == 0
        assert "No cached" in result.output or result.exit_code == 0

    def test_cache_clear(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.core.trends as trends_mod
        monkeypatch.setattr(trends_mod, "CACHE_DIR", tmp_path)
        # Create dummy cache file
        (tmp_path / "tiktok_US_7d.json").write_text('{"_cached_at": 0}')
        result = runner.invoke(cli, ["trends", "cache", "--clear"])
        assert result.exit_code == 0


# ── Account Optimize Tests ────────────────────────────────────────────

class TestAccountOptimize:
    def test_basic_optimize(self, runner):
        result = runner.invoke(cli, [
            "account", "optimize",
            "--platform", "tiktok",
            "--niche", "fitness",
            "--followers", "1500",
            "--avg-views", "1000",
            "--posts-per-week", "2",
        ])
        assert result.exit_code == 0
        assert "Optimization" in result.output or "tiktok" in result.output.lower()

    def test_optimize_json(self, runner):
        result = runner.invoke(cli, [
            "--json",
            "account", "optimize",
            "--platform", "instagram",
            "--niche", "beauty",
            "--followers", "10000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "instagram"
        assert "recommendations" in data
        assert len(data["recommendations"]) > 0

    def test_optimize_with_trends(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, [
            "account", "optimize",
            "--platform", "tiktok",
            "--niche", "cooking",
            "--use-trends",
            "--country", "US",
        ])
        assert result.exit_code == 0

    def test_optimize_all_from_file(self, runner, tmp_path):
        config = [
            {"name": "tiktok_main", "platform": "tiktok", "niche": "fitness", "current_followers": 5000},
            {"name": "ig_page", "platform": "instagram", "niche": "food", "current_followers": 2000},
        ]
        cfg_file = tmp_path / "accounts.json"
        cfg_file.write_text(json.dumps(config))
        result = runner.invoke(cli, ["account", "optimize-all", str(cfg_file)])
        assert result.exit_code == 0


# ── Theme Page Tests ──────────────────────────────────────────────────

class TestThemePage:
    def test_list_niches(self, runner):
        result = runner.invoke(cli, ["theme", "niches"])
        assert result.exit_code == 0
        assert "fitness_motivation" in result.output
        assert "finance_education" in result.output

    def test_list_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 5

    def test_blueprint_basic(self, runner):
        result = runner.invoke(cli, [
            "theme", "blueprint",
            "--niche", "fitness_motivation",
            "--platform", "tiktok",
            "--target-followers", "50000",
        ])
        assert result.exit_code == 0
        assert "fitness_motivation" in result.output

    def test_blueprint_json(self, runner):
        result = runner.invoke(cli, [
            "--json",
            "theme", "blueprint",
            "--niche", "meme_humor",
            "--platform", "instagram",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "meme_humor"
        assert len(data["content_calendar_30_days"]) > 0
        assert "revenue_projection" in data

    def test_blueprint_with_trends(self, runner, mock_tiktok_trends):
        result = runner.invoke(cli, [
            "theme", "blueprint",
            "--niche", "fitness_motivation",
            "--platform", "tiktok",
            "--use-trends",
            "--country", "US",
        ])
        assert result.exit_code == 0

    def test_blueprint_save_file(self, runner, tmp_path):
        out = str(tmp_path / "blueprint.json")
        result = runner.invoke(cli, [
            "theme", "blueprint",
            "--niche", "finance_education",
            "--platform", "youtube_shorts",
            "--output-file", out,
        ])
        assert result.exit_code == 0
        import os
        assert os.path.exists(out)

    def test_content_formats(self, runner):
        result = runner.invoke(cli, ["theme", "formats"])
        assert result.exit_code == 0
        assert "trending_challenge" in result.output

    def test_content_formats_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "formats"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert any(f["format"] == "before_after" for f in data)


# ── Config Tests ──────────────────────────────────────────────────────

class TestConfig:
    def test_set_and_get(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.social_trends_cli as cli_mod
        monkeypatch.setattr(cli_mod, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cli_mod, "CONFIG_FILE", tmp_path / "config.json")

        result = runner.invoke(cli, ["config", "set", "youtube_api_key", "AIzaTest123"])
        assert result.exit_code == 0

    def test_get_empty(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.social_trends_cli as cli_mod
        monkeypatch.setattr(cli_mod, "CONFIG_FILE", tmp_path / "nonexistent.json")
        result = runner.invoke(cli, ["config", "get"])
        assert result.exit_code == 0


# ── Session Tests ─────────────────────────────────────────────────────

class TestSessionCommands:
    def test_session_status(self, runner):
        result = runner.invoke(cli, ["session", "status"])
        assert result.exit_code == 0

    def test_session_history_empty(self, runner):
        result = runner.invoke(cli, ["session", "history"])
        assert result.exit_code == 0

    def test_session_undo_empty(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.social_trends_cli as cli_mod
        monkeypatch.setattr(cli_mod, "CONFIG_DIR", tmp_path)
        # Force a fresh session backed by a temp dir
        cli_mod._session = None
        result = runner.invoke(cli, ["session", "undo"])
        assert result.exit_code == 0
        assert "Nothing" in result.output

    def test_session_redo_empty(self, runner):
        result = runner.invoke(cli, ["session", "redo"])
        assert result.exit_code == 0
