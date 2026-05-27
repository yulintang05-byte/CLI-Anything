"""End-to-end CLI tests — all network calls are mocked.

Tests the Click CLI commands through the full call stack.
"""

import json
import pytest
from click.testing import CliRunner

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_tiktok_hashtags(monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.tiktok_trends.get_trending_hashtags",
        lambda *a, **kw: [
            {"hashtag": "#fyp", "views": 900_000_000_000, "source": "mock"},
            {"hashtag": "#fitness", "views": 30_000_000_000, "source": "mock"},
            {"hashtag": "#workout", "views": 28_000_000_000, "source": "mock"},
        ],
    )


@pytest.fixture
def mock_tiktok_sounds(monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.tiktok_trends.get_trending_sounds",
        lambda *a, **kw: [
            {"title": "As It Was", "author": "Harry Styles", "usage_count": 5_000_000, "source": "mock"},
            {"title": "Flowers", "author": "Miley Cyrus", "usage_count": 3_000_000, "source": "mock"},
        ],
    )


@pytest.fixture
def mock_tiktok_videos(monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.tiktok_trends.get_trending_videos",
        lambda *a, **kw: [
            {"video_id": "1", "title": "Viral fitness clip", "author": "creator1",
             "like_count": 500_000, "hashtags": ["#fitness"], "source": "mock"},
        ],
    )


@pytest.fixture
def mock_youtube_videos(monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.youtube_trends.get_trending_videos",
        lambda *a, **kw: [
            {"id": "abc123", "title": "Top workout 2024", "channel": "FitChannel",
             "view_count": 1_000_000, "tags": ["fitness", "workout"], "hashtags": [],
             "source": "mock"},
        ],
    )


@pytest.fixture
def mock_youtube_hashtags(monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.youtube_trends.get_trending_hashtags",
        lambda *a, **kw: [
            {"hashtag": "#workout", "frequency": 3},
            {"hashtag": "#fitness", "frequency": 2},
        ],
    )


# ── Config commands ───────────────────────────────────────────────────────────

class TestConfigCommands:
    def test_config_set_api_key(self, runner, tmp_path, monkeypatch):
        cfg_file = tmp_path / "config.json"
        monkeypatch.setattr("cli_anything.social_trends.utils.scraper_backend.CONFIG_FILE", cfg_file)
        monkeypatch.setattr("cli_anything.social_trends.utils.scraper_backend.CONFIG_DIR", tmp_path)

        result = runner.invoke(cli, ["config", "set", "--youtube-api-key", "AIzaFAKEKEY"])
        assert result.exit_code == 0
        assert "YouTube API key saved" in result.output or "Configuration updated" in result.output

    def test_config_show(self, runner, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.scraper_backend.CONFIG_FILE",
            tmp_path / "config.json"
        )
        result = runner.invoke(cli, ["config", "show"])
        assert result.exit_code == 0

    def test_config_cache_clear(self, runner, tmp_path, monkeypatch):
        monkeypatch.setattr("cli_anything.social_trends.utils.scraper_backend.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("cli_anything.social_trends.utils.scraper_backend.CACHE_DIR", tmp_path)
        result = runner.invoke(cli, ["config", "cache-clear"])
        assert result.exit_code == 0


# ── TikTok commands ───────────────────────────────────────────────────────────

class TestTikTokCommands:
    def test_hashtags_default(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["tiktok", "hashtags"])
        assert result.exit_code == 0
        assert "#fyp" in result.output

    def test_hashtags_json(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["--json", "tiktok", "hashtags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["hashtag"] == "#fyp"

    def test_hashtags_region_flag(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["tiktok", "hashtags", "--region", "UK"])
        assert result.exit_code == 0

    def test_hashtags_limit(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["--json", "tiktok", "hashtags", "--limit", "2"])
        data = json.loads(result.output)
        assert len(data) <= 2

    def test_sounds(self, runner, mock_tiktok_sounds):
        result = runner.invoke(cli, ["tiktok", "sounds"])
        assert result.exit_code == 0
        assert "Harry Styles" in result.output or "As It Was" in result.output

    def test_sounds_json(self, runner, mock_tiktok_sounds):
        result = runner.invoke(cli, ["--json", "tiktok", "sounds"])
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_videos(self, runner, mock_tiktok_videos):
        result = runner.invoke(cli, ["tiktok", "videos"])
        assert result.exit_code == 0


# ── YouTube commands ──────────────────────────────────────────────────────────

class TestYouTubeCommands:
    def test_videos_default(self, runner, mock_youtube_videos):
        result = runner.invoke(cli, ["youtube", "videos"])
        assert result.exit_code == 0

    def test_videos_json(self, runner, mock_youtube_videos):
        result = runner.invoke(cli, ["--json", "youtube", "videos"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_videos_category(self, runner, mock_youtube_videos):
        result = runner.invoke(cli, ["youtube", "videos", "--category", "music"])
        assert result.exit_code == 0

    def test_hashtags(self, runner, mock_youtube_hashtags):
        result = runner.invoke(cli, ["youtube", "hashtags"])
        assert result.exit_code == 0
        assert "#workout" in result.output or "#fitness" in result.output

    def test_music(self, runner, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.youtube_trends.get_trending_music",
            lambda *a, **kw: [
                {"id": "xyz", "title": "Trending Song 2024", "channel": "MusicChannel",
                 "view_count": 5_000_000, "tags": [], "hashtags": [], "source": "mock"},
            ],
        )
        result = runner.invoke(cli, ["youtube", "music"])
        assert result.exit_code == 0


# ── Trends commands ───────────────────────────────────────────────────────────

class TestTrendsCommands:
    def test_report(self, runner, mock_youtube_videos, mock_youtube_hashtags,
                    mock_tiktok_videos, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["trends", "report"])
        assert result.exit_code == 0

    def test_report_json(self, runner, mock_youtube_videos, mock_youtube_hashtags,
                         mock_tiktok_videos, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["--json", "trends", "report"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_cross_platform_hashtags" in data
        assert "top_themes" in data

    def test_hashtag_score(self, runner):
        result = runner.invoke(cli, ["trends", "hashtag-score", "#fyp", "#fitness", "#workout"])
        assert result.exit_code == 0
        assert "mix_score" in result.output or "Hashtag Analysis" in result.output

    def test_hashtag_score_json(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "hashtag-score", "#fyp", "#fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "mix_score" in data


# ── Plan commands ─────────────────────────────────────────────────────────────

class TestPlanCommands:
    def test_weekly_plan(self, runner, mock_tiktok_hashtags, mock_tiktok_sounds):
        result = runner.invoke(cli, ["plan", "weekly", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "week" in result.output.lower() or "day" in result.output.lower()

    def test_weekly_plan_json(self, runner, mock_tiktok_hashtags, mock_tiktok_sounds):
        result = runner.invoke(cli, ["--json", "plan", "weekly", "--niche", "motivation"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "days" in data
        assert len(data["days"]) == 7

    def test_weekly_plan_youtube(self, runner, mock_youtube_hashtags):
        result = runner.invoke(cli, ["plan", "weekly", "--platform", "youtube", "--niche", "gaming"])
        assert result.exit_code == 0

    def test_hashtag_set(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["plan", "hashtags", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_hashtag_set_json(self, runner, mock_tiktok_hashtags):
        result = runner.invoke(cli, ["--json", "plan", "hashtags", "--niche", "fitness"])
        data = json.loads(result.output)
        assert "hashtag_set" in data
        assert "copy_paste" in data

    def test_content_ideas(self, runner, mock_youtube_videos, mock_tiktok_videos):
        result = runner.invoke(cli, ["plan", "ideas", "--niche", "fitness", "--count", "5"])
        assert result.exit_code == 0


# ── Optimise commands ─────────────────────────────────────────────────────────

class TestOptimiseCommands:
    def test_optimise_tiktok(self, runner):
        result = runner.invoke(cli, ["optimise", "tiktok", "--niche", "fitness",
                                     "--followers", "5000", "--avg-views", "2000"])
        assert result.exit_code == 0
        assert "tiktok" in result.output.lower()

    def test_optimise_tiktok_json(self, runner):
        result = runner.invoke(cli, ["--json", "optimise", "tiktok", "--niche", "fitness",
                                     "--followers", "5000"])
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert "profile_checklist" in data
        assert "growth_tactics" in data

    def test_optimise_youtube(self, runner):
        result = runner.invoke(cli, ["--json", "optimise", "youtube", "--niche", "gaming",
                                     "--subscribers", "10000", "--avg-views", "5000"])
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert "channel_checklist" in data

    def test_optimise_instagram(self, runner):
        result = runner.invoke(cli, ["--json", "optimise", "instagram", "--niche", "fashion",
                                     "--followers", "3000"])
        data = json.loads(result.output)
        assert data["platform"] == "instagram"
        assert "reels_strategy" in data

    def test_add_list_accounts(self, runner, tmp_path, monkeypatch):
        import cli_anything.social_trends.core.account_optimizer as ao
        monkeypatch.setattr(ao, "PROFILES_FILE", tmp_path / "accounts.json")

        result = runner.invoke(cli, ["optimise", "add-account",
                                     "--platform", "tiktok",
                                     "--username", "fitnessguru",
                                     "--niche", "fitness",
                                     "--followers", "10000"])
        assert result.exit_code == 0

        result2 = runner.invoke(cli, ["optimise", "list-accounts"])
        assert result2.exit_code == 0
        assert "fitnessguru" in result2.output


# ── Theme commands ────────────────────────────────────────────────────────────

class TestThemeCommands:
    def test_guide(self, runner):
        result = runner.invoke(cli, ["theme", "guide"])
        assert result.exit_code == 0
        assert "Step 1" in result.output or "step" in result.output.lower()

    def test_guide_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "guide"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 6

    def test_niches_list(self, runner):
        result = runner.invoke(cli, ["theme", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output
        assert "motivation" in result.output

    def test_niches_sorted_cpm(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches", "--sort-by", "avg_cpm"])
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_niche_info_valid(self, runner):
        result = runner.invoke(cli, ["theme", "niche-info", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_niche_info_invalid(self, runner):
        result = runner.invoke(cli, ["theme", "niche-info", "unknownniche12345"])
        assert result.exit_code != 0 or "Error" in result.output or "not found" in result.output

    def test_monetise(self, runner):
        result = runner.invoke(cli, ["theme", "monetise", "--followers", "10000"])
        assert result.exit_code == 0

    def test_monetise_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "monetise", "--followers", "10000"])
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_funnel(self, runner):
        result = runner.invoke(cli, ["theme", "funnel", "--niche", "fitness",
                                     "--followers", "5000"])
        assert result.exit_code == 0
        assert "Awareness" in result.output or "funnel" in result.output.lower()

    def test_funnel_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "funnel",
                                     "--niche", "fitness", "--followers", "5000"])
        data = json.loads(result.output)
        assert "funnel_stages" in data
        assert len(data["funnel_stages"]) == 5

    def test_sourcing(self, runner):
        result = runner.invoke(cli, ["theme", "sourcing"])
        assert result.exit_code == 0

    def test_sourcing_specific(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "sourcing",
                                     "--strategy", "repost_with_credit"])
        data = json.loads(result.output)
        assert "steps" in data


# ── JSON global flag ──────────────────────────────────────────────────────────

class TestJsonFlag:
    def test_json_flag_position(self, runner):
        """--json must come before subcommand."""
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
