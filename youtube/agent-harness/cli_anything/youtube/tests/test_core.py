"""Tests for YouTube harness core modules."""

import pytest
from unittest.mock import patch, MagicMock


# ── Backend unit tests ────────────────────────────────────────────────────

class TestYouTubeBackend:
    def test_get_niche_keywords_fitness(self):
        from cli_anything.youtube.utils.yt_backend import get_niche_keywords
        kws = get_niche_keywords("fitness")
        assert len(kws) > 0
        assert any("workout" in k for k in kws)

    def test_get_niche_keywords_limit(self):
        from cli_anything.youtube.utils.yt_backend import get_niche_keywords
        kws = get_niche_keywords("cooking", limit=5)
        assert len(kws) <= 5

    def test_get_niche_keywords_fallback(self):
        from cli_anything.youtube.utils.yt_backend import get_niche_keywords
        kws = get_niche_keywords("unknown_niche_xyz")
        assert len(kws) > 0  # falls back to education

    def test_channel_audit_tips_structure(self):
        from cli_anything.youtube.utils.yt_backend import channel_audit_tips
        result = channel_audit_tips(niche="fitness")
        assert "tips" in result
        assert "channel_setup" in result["tips"]
        assert "video_optimization" in result["tips"]
        assert "algorithm" in result["tips"]
        assert "growth" in result["tips"]
        assert "monetization" in result["tips"]
        assert "seo_keywords" in result["tips"]  # niche-specific

    def test_channel_audit_tips_no_niche(self):
        from cli_anything.youtube.utils.yt_backend import channel_audit_tips
        result = channel_audit_tips()
        assert "tips" in result
        assert "quick_wins" in result

    def test_category_ids_coverage(self):
        from cli_anything.youtube.utils.yt_backend import CATEGORY_IDS
        assert "all" in CATEGORY_IDS
        assert "music" in CATEGORY_IDS
        assert "gaming" in CATEGORY_IDS
        assert len(CATEGORY_IDS) >= 8

    def test_regions_list(self):
        from cli_anything.youtube.utils.yt_backend import REGIONS
        assert "US" in REGIONS
        assert "GB" in REGIONS
        assert len(REGIONS) >= 10

    def test_parse_yt_video(self):
        from cli_anything.youtube.utils.yt_backend import _parse_yt_video
        raw = {
            "id": "abc123",
            "title": "Best Workout 2024 #fitness #gym",
            "description": "Full workout guide #health",
            "uploader": "FitChannel",
            "view_count": 100000,
            "like_count": 5000,
        }
        parsed = _parse_yt_video(raw)
        assert parsed["id"] == "abc123"
        assert "fitness" in parsed["hashtags"]
        assert "gym" in parsed["hashtags"]
        assert "health" in parsed["hashtags"]
        assert parsed["view_count"] == 100000
        assert parsed["channel"] == "FitChannel"

    def test_load_save_config(self, tmp_path, monkeypatch):
        from cli_anything.youtube.utils import yt_backend
        monkeypatch.setattr(yt_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(yt_backend, "CONFIG_DIR", tmp_path)

        yt_backend.save_config({"default_region": "GB"})
        cfg = yt_backend.load_config()
        assert cfg["default_region"] == "GB"

    def test_load_config_missing(self, tmp_path, monkeypatch):
        from cli_anything.youtube.utils import yt_backend
        monkeypatch.setattr(yt_backend, "CONFIG_FILE", tmp_path / "missing.json")
        cfg = yt_backend.load_config()
        assert cfg == {}

    def test_get_api_key_from_env(self, monkeypatch):
        from cli_anything.youtube.utils import yt_backend
        monkeypatch.setenv("YT_API_KEY", "test_key_123")
        key = yt_backend.get_api_key()
        assert key == "test_key_123"

    def test_get_api_key_cli_overrides_env(self, monkeypatch):
        from cli_anything.youtube.utils import yt_backend
        monkeypatch.setenv("YT_API_KEY", "env_key")
        key = yt_backend.get_api_key("cli_key")
        assert key == "cli_key"


# ── Trends core tests ─────────────────────────────────────────────────────

class TestTrendsCore:
    @patch("cli_anything.youtube.core.trends.get_trending_videos_ytdlp")
    def test_fetch_trending_no_api_key(self, mock_ytdlp):
        mock_ytdlp.return_value = [
            {"id": "1", "title": "Best workout #fitness", "hashtags": ["fitness"],
             "tags": [], "view_count": 50000},
        ]
        from cli_anything.youtube.core.trends import fetch_trending
        result = fetch_trending(region="US", category="all", limit=5, api_key=None)
        assert result["source"] == "yt-dlp"
        assert result["video_count"] == 1
        assert "trending_tags" in result
        assert "trending_keywords" in result

    @patch("cli_anything.youtube.core.trends.get_trending_videos_api")
    def test_fetch_trending_with_api_key(self, mock_api):
        mock_api.return_value = [
            {"id": "2", "title": "Viral music #pop", "hashtags": ["pop"],
             "tags": ["music"], "view_count": 200000},
        ]
        from cli_anything.youtube.core.trends import fetch_trending
        result = fetch_trending(region="US", category="music", limit=10, api_key="fake_key")
        assert result["source"] == "youtube_data_api_v3"
        assert result["video_count"] == 1

    def test_extract_top_tags(self):
        from cli_anything.youtube.core.trends import _extract_top_tags
        videos = [
            {"hashtags": ["fitness", "gym"], "tags": ["workout"]},
            {"hashtags": ["fitness"], "tags": ["health", "gym"]},
            {"hashtags": ["food"], "tags": []},
        ]
        tags = _extract_top_tags(videos)
        assert tags[0]["tag"] in ("fitness", "gym")  # most frequent
        assert tags[0]["appearances"] >= 2

    def test_extract_top_keywords(self):
        from cli_anything.youtube.core.trends import _extract_top_keywords
        videos = [
            {"title": "Best workout routine ever"},
            {"title": "Best home workout 2024"},
            {"title": "Food recipe ideas"},
        ]
        kws = _extract_top_keywords(videos)
        assert "best" in kws or "workout" in kws

    def test_list_categories(self):
        from cli_anything.youtube.core.trends import list_categories
        cats = list_categories()
        assert "music" in cats
        assert "gaming" in cats
        assert "all" in cats

    def test_list_regions(self):
        from cli_anything.youtube.core.trends import list_regions
        regions = list_regions()
        assert "US" in regions
        assert len(regions) >= 10


# ── Hashtags core tests ───────────────────────────────────────────────────

class TestHashtagsCore:
    @patch("cli_anything.youtube.core.hashtags.get_video_metadata")
    def test_extract_from_video(self, mock_meta):
        mock_meta.return_value = {
            "title": "Fitness Tutorial #fitness",
            "hashtags": ["fitness", "gym"],
            "tags": ["workout", "health"],
            "channel": "FitChan",
        }
        from cli_anything.youtube.core.hashtags import extract_from_video
        result = extract_from_video("https://youtu.be/abc")
        assert "fitness" in result["hashtags"]
        assert result["total_found"] == 4  # 2 hashtags + 2 tags

    def test_suggest_for_niche(self):
        from cli_anything.youtube.core.hashtags import suggest_for_niche
        result = suggest_for_niche("fitness")
        assert "search_keywords" in result
        assert "hashtags" in result
        assert "title_formulas" in result
        assert len(result["title_formulas"]) > 0

    def test_list_niches(self):
        from cli_anything.youtube.core.hashtags import list_niches
        niches = list_niches()
        assert "fitness" in niches
        assert "tech" in niches

    def test_title_formulas_generated(self):
        from cli_anything.youtube.core.hashtags import suggest_for_niche
        result = suggest_for_niche("cooking")
        for formula in result["title_formulas"]:
            assert len(formula) > 10


# ── Channel core tests ────────────────────────────────────────────────────

class TestChannelCore:
    def test_audit_returns_tips(self):
        from cli_anything.youtube.core.channel import audit
        result = audit(niche="gaming")
        assert "tips" in result
        assert len(result["tips"]["channel_setup"]) > 0

    def test_keyword_research(self):
        from cli_anything.youtube.core.channel import keyword_research
        result = keyword_research("tech")
        assert "keywords" in result
        assert "how_to_use" in result
        assert len(result["keywords"]) > 0


# ── CLI integration tests ─────────────────────────────────────────────────

class TestCLI:
    def test_help(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "YouTube" in result.output

    def test_trends_categories(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "categories"])
        assert result.exit_code == 0
        assert "music" in result.output

    def test_trends_regions(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "regions"])
        assert result.exit_code == 0
        assert "US" in result.output

    def test_hashtags_niches(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output

    def test_hashtags_suggest(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "suggest", "fitness"])
        assert result.exit_code == 0

    def test_channel_audit(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["channel", "audit", "--niche", "gaming"])
        assert result.exit_code == 0

    def test_channel_keywords(self):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["channel", "keywords", "finance"])
        assert result.exit_code == 0

    def test_config_set_get_json(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        from cli_anything.youtube.utils import yt_backend
        import json
        monkeypatch.setattr(yt_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(yt_backend, "CONFIG_DIR", tmp_path)

        runner = CliRunner()
        runner.invoke(cli, ["config", "set", "default_region", "AU"])
        result = runner.invoke(cli, ["--json", "config", "get", "default_region"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["value"] == "AU"

    @patch("cli_anything.youtube.core.trends.get_trending_videos_ytdlp")
    def test_trends_fetch_no_key(self, mock_ytdlp):
        mock_ytdlp.return_value = [
            {"id": "x", "title": "Viral video #music", "hashtags": ["music"],
             "tags": [], "view_count": 1000000, "channel": "BigChan",
             "like_count": 50000, "comment_count": 1000, "duration": 300,
             "upload_date": "20240101", "channel_url": "", "description_snippet": "",
             "categories": []},
        ]
        from click.testing import CliRunner
        from cli_anything.youtube.youtube_cli import cli
        import json
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "trends", "fetch", "--limit", "1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["source"] == "yt-dlp"
        assert data["video_count"] == 1
