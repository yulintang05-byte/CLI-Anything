"""Tests for TikTok harness core modules."""

import pytest
from unittest.mock import patch, MagicMock


# ── Backend unit tests ────────────────────────────────────────────────────

class TestTikTokBackend:
    def test_get_niche_hashtags_fitness(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
        tags = get_niche_hashtags("fitness")
        assert len(tags) > 0
        assert "fitness" in tags

    def test_get_niche_hashtags_food(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
        tags = get_niche_hashtags("food")
        assert "food" in tags or "foodie" in tags

    def test_get_niche_hashtags_limit(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
        tags = get_niche_hashtags("fitness", limit=5)
        assert len(tags) <= 5

    def test_list_niches(self):
        from cli_anything.tiktok.utils.tiktok_backend import list_niches
        niches = list_niches()
        assert len(niches) >= 8
        assert "fitness" in niches
        assert "food" in niches

    def test_get_posting_schedule_tiktok(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_posting_schedule
        schedule = get_posting_schedule("tiktok")
        assert "monday" in schedule
        assert "saturday" in schedule
        for day, slots in schedule.items():
            assert isinstance(slots, list)
            assert len(slots) >= 1

    def test_get_posting_schedule_youtube(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_posting_schedule
        schedule = get_posting_schedule("youtube_shorts")
        assert "friday" in schedule

    def test_get_posting_schedule_fallback(self):
        from cli_anything.tiktok.utils.tiktok_backend import get_posting_schedule
        schedule = get_posting_schedule("unknown_platform")
        assert "monday" in schedule  # falls back to tiktok

    def test_account_audit_tips_structure(self):
        from cli_anything.tiktok.utils.tiktok_backend import account_audit_tips
        result = account_audit_tips(handle="@test", niche="fitness")
        assert "tips" in result
        assert "profile" in result["tips"]
        assert "content" in result["tips"]
        assert "growth" in result["tips"]
        assert "algorithm" in result["tips"]
        assert "hashtags" in result["tips"]  # niche-specific

    def test_account_audit_tips_no_niche(self):
        from cli_anything.tiktok.utils.tiktok_backend import account_audit_tips
        result = account_audit_tips()
        assert "tips" in result
        assert len(result["tips"]["content"]) > 0

    def test_parse_tiktok_video(self):
        from cli_anything.tiktok.utils.tiktok_backend import _parse_tiktok_video
        raw = {
            "id": "123",
            "description": "Check out my workout #fitness #gym",
            "uploader": "testuser",
            "view_count": 50000,
            "like_count": 2000,
            "track": "Original Sound",
            "artist": "testuser",
        }
        parsed = _parse_tiktok_video(raw)
        assert parsed["id"] == "123"
        assert "fitness" in parsed["hashtags"]
        assert "gym" in parsed["hashtags"]
        assert parsed["view_count"] == 50000
        assert parsed["sound"]["title"] == "Original Sound"

    def test_extract_trends_from_videos(self):
        from cli_anything.tiktok.utils.tiktok_backend import extract_trends_from_videos
        videos = [
            {"hashtags": ["fitness", "gym"], "sound": {"title": "Song A", "artist": "Artist A"}},
            {"hashtags": ["fitness", "workout"], "sound": {"title": "Song A", "artist": "Artist A"}},
            {"hashtags": ["food"], "sound": {"title": "Song B", "artist": "Artist B"}},
        ]
        result = extract_trends_from_videos(videos)
        assert "trending_hashtags" in result
        assert "trending_sounds" in result
        # fitness should be most frequent
        assert result["trending_hashtags"][0]["hashtag"] == "fitness"
        assert result["trending_hashtags"][0]["appearances"] == 2
        # Song A should be top sound
        assert result["trending_sounds"][0]["title"] == "Song A"

    def test_load_save_config(self, tmp_path, monkeypatch):
        from cli_anything.tiktok.utils import tiktok_backend
        monkeypatch.setattr(tiktok_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(tiktok_backend, "CONFIG_DIR", tmp_path)

        tiktok_backend.save_config({"default_region": "GB"})
        cfg = tiktok_backend.load_config()
        assert cfg["default_region"] == "GB"

    def test_load_config_missing(self, tmp_path, monkeypatch):
        from cli_anything.tiktok.utils import tiktok_backend
        monkeypatch.setattr(tiktok_backend, "CONFIG_FILE", tmp_path / "nonexistent.json")
        cfg = tiktok_backend.load_config()
        assert cfg == {}


# ── Core hashtag tests ────────────────────────────────────────────────────

class TestHashtagCore:
    def test_get_top_hashtags_with_niche(self):
        from cli_anything.tiktok.core.hashtags import get_top_hashtags
        result = get_top_hashtags(niche="fitness", limit=10)
        assert result["niche"] == "fitness"
        assert len(result["hashtags"]) <= 10
        assert all(h.startswith("#") for h in result["hashtags"])

    def test_get_top_hashtags_all(self):
        from cli_anything.tiktok.core.hashtags import get_top_hashtags
        result = get_top_hashtags(limit=20)
        assert result["niche"] == "all"
        assert len(result["hashtags"]) <= 20

    def test_suggest_hashtags_returns_tiers(self):
        from cli_anything.tiktok.core.hashtags import suggest_hashtags
        result = suggest_hashtags("food", limit=20)
        assert "strategy" in result
        s = result["strategy"]
        assert "mega_tags" in s
        assert "large_tags" in s
        assert "niche_tags" in s
        assert "micro_tags" in s
        assert "recommended_mix" in result

    def test_available_niches(self):
        from cli_anything.tiktok.core.hashtags import available_niches
        niches = available_niches()
        assert "fitness" in niches
        assert "beauty" in niches
        assert "gaming" in niches

    def test_build_caption(self):
        from cli_anything.tiktok.core.hashtags import build_caption
        caption = build_caption("fitness", num_tags=5)
        assert "#" in caption
        tag_count = caption.count("#")
        assert tag_count == 5


# ── Trends core tests ─────────────────────────────────────────────────────

class TestTrendsCore:
    @patch("cli_anything.tiktok.core.trends.get_trending_videos")
    @patch("cli_anything.tiktok.core.trends.extract_trends_from_videos")
    def test_fetch_trending(self, mock_extract, mock_get):
        mock_get.return_value = [{"id": "1", "hashtags": ["fitness"]}]
        mock_extract.return_value = {
            "trending_hashtags": [{"hashtag": "fitness", "appearances": 1}],
            "trending_sounds": [],
        }

        from cli_anything.tiktok.core.trends import fetch_trending
        result = fetch_trending(region="US", limit=5)
        assert result["region"] == "US"
        assert result["video_count"] == 1
        assert len(result["trending_hashtags"]) == 1

    @patch("cli_anything.tiktok.core.trends.get_trending_videos")
    @patch("cli_anything.tiktok.core.trends.extract_trends_from_videos")
    def test_build_trend_report(self, mock_extract, mock_get):
        mock_get.return_value = [
            {"id": "1", "view_count": 100000, "hashtags": ["fitness"]},
            {"id": "2", "view_count": 50000, "hashtags": ["gym"]},
        ]
        mock_extract.return_value = {
            "trending_hashtags": [{"hashtag": "fitness", "appearances": 1}],
            "trending_sounds": [{"title": "Song A", "artist": "X", "count": 2}],
        }

        from cli_anything.tiktok.core.trends import build_trend_report
        report = build_trend_report(region="US", limit=10)
        assert "date" in report
        assert "top_hashtags" in report
        assert "top_sounds" in report
        assert "top_videos" in report
        assert "insights" in report


# ── Sounds core tests ─────────────────────────────────────────────────────

class TestSoundsCore:
    @patch("cli_anything.tiktok.core.sounds.get_trending_videos")
    @patch("cli_anything.tiktok.core.sounds.extract_trends_from_videos")
    def test_get_trending_sounds(self, mock_extract, mock_get):
        mock_get.return_value = [{"id": "1", "hashtags": []}]
        mock_extract.return_value = {
            "trending_hashtags": [],
            "trending_sounds": [{"title": "Viral Song", "artist": "DJ X", "count": 15}],
        }

        from cli_anything.tiktok.core.sounds import get_trending_sounds
        result = get_trending_sounds(region="US", limit=10)
        assert result["region"] == "US"
        assert result["count"] == 1
        assert result["sounds"][0]["title"] == "Viral Song"
        assert "tips" in result

    def test_sound_tips_not_empty(self):
        from cli_anything.tiktok.core.sounds import _sound_tips
        tips = _sound_tips()
        assert len(tips) >= 4
        assert all(isinstance(t, str) for t in tips)


# ── CLI integration tests ─────────────────────────────────────────────────

class TestCLI:
    def test_cli_help(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "TikTok" in result.output

    def test_niches_list(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["niches", "list"])
        assert result.exit_code == 0
        assert "fitness" in result.output

    def test_niches_list_json(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        import json
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "niches", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "niches" in data
        assert "fitness" in data["niches"]

    def test_hashtags_top(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "top", "--niche", "fitness", "--limit", "10"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_hashtags_suggest(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "suggest", "food"])
        assert result.exit_code == 0

    def test_hashtags_caption(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "caption", "fitness", "--tags", "5"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_account_audit(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["account", "audit", "--handle", "@testuser", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_account_schedule(self):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["account", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "monday" in result.output.lower()

    def test_config_set_get(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        from cli_anything.tiktok.utils import tiktok_backend
        monkeypatch.setattr(tiktok_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(tiktok_backend, "CONFIG_DIR", tmp_path)

        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "default_region", "GB"])
        assert result.exit_code == 0

        result = runner.invoke(cli, ["config", "get", "default_region"])
        assert result.exit_code == 0
        assert "GB" in result.output

    @patch("cli_anything.tiktok.core.trends.get_trending_videos")
    @patch("cli_anything.tiktok.core.trends.extract_trends_from_videos")
    def test_trends_fetch_json(self, mock_extract, mock_get):
        mock_get.return_value = [{"id": "1", "hashtags": ["fitness"], "view_count": 10000}]
        mock_extract.return_value = {
            "trending_hashtags": [{"hashtag": "fitness", "appearances": 1}],
            "trending_sounds": [],
        }
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        import json
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "trends", "fetch", "--limit", "1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "videos" in data
        assert "trending_hashtags" in data

    @patch("cli_anything.tiktok.core.sounds.get_trending_videos")
    @patch("cli_anything.tiktok.core.sounds.extract_trends_from_videos")
    def test_sounds_trending(self, mock_extract, mock_get):
        mock_get.return_value = []
        mock_extract.return_value = {"trending_hashtags": [], "trending_sounds": []}
        from click.testing import CliRunner
        from cli_anything.tiktok.tiktok_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["sounds", "trending"])
        assert result.exit_code == 0
