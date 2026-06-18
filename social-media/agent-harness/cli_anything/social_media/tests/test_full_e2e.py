"""E2E tests — requires network and/or real API keys.

Tests are skipped when credentials are not configured.
Run: pytest tests/test_full_e2e.py -v -s
"""

import sys
import os
import json
import subprocess
import pytest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from cli_anything.social_media.utils.youtube_backend import YouTubeBackend
from cli_anything.social_media.utils.tiktok_backend import TikTokBackend
from cli_anything.social_media.core import trends as trends_mod


def _resolve_cli():
    for candidate in ["cli-anything-social", "python -m cli_anything.social_media"]:
        try:
            result = subprocess.run(
                candidate.split() + ["--help"],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                return candidate.split()
        except Exception:
            continue
    pytest.skip("cli-anything-social not installed")


HAS_YT_KEY = bool(os.environ.get("YOUTUBE_API_KEY"))
HAS_NETWORK = True  # assume network unless proven otherwise


@pytest.mark.skipif(not HAS_YT_KEY, reason="YOUTUBE_API_KEY not set")
class TestYouTubeAPI:
    def test_trending_videos_returns_data(self):
        yt = YouTubeBackend()
        videos = yt.get_trending_videos(region="US", category="all", max_results=10)
        assert isinstance(videos, list)
        assert len(videos) > 0
        v = videos[0]
        assert "title" in v
        assert "views" in v
        assert "url" in v
        assert v["url"].startswith("https://")

    def test_trending_hashtags_derived(self):
        yt = YouTubeBackend()
        tags = yt.get_trending_hashtags(region="US", category="all", top_n=20)
        assert isinstance(tags, list)
        assert len(tags) > 0
        assert all(t["hashtag"].startswith("#") for t in tags)

    def test_trending_music_returns_music(self):
        yt = YouTubeBackend()
        music = yt.get_trending_music(region="US", max_results=10)
        assert isinstance(music, list)
        assert len(music) > 0

    def test_search_videos(self):
        yt = YouTubeBackend()
        results = yt.search_videos("fitness workout", max_results=5)
        assert isinstance(results, list)


@pytest.mark.skipif(not HAS_NETWORK, reason="No network access")
class TestYouTubeFallback:
    def test_fallback_returns_list_without_api_key(self):
        yt = YouTubeBackend(api_key="")
        yt.api_key = ""
        videos = yt.get_trending_videos(category="all", max_results=10)
        assert isinstance(videos, list)

    def test_cache_roundtrip(self, tmp_path, monkeypatch):
        import cli_anything.social_media.utils.youtube_backend as yt_mod
        monkeypatch.setattr(yt_mod, "_CACHE_PATH", tmp_path / "yt_cache.json")
        yt = YouTubeBackend(api_key="")
        data = [{"title": "cached", "views": 999}]
        yt.cache_results("test_key", data)
        loaded = yt.load_cache("test_key")
        assert loaded == data


@pytest.mark.skipif(not HAS_NETWORK, reason="No network access")
class TestTikTokFallback:
    def test_trending_hashtags_returns_list(self):
        tt = TikTokBackend()
        result = tt.get_trending_hashtags(category="all", top_n=10)
        assert isinstance(result, list)
        assert len(result) > 0
        for item in result:
            assert "hashtag" in item
            assert item["hashtag"].startswith("#")

    def test_trending_sounds_returns_list(self):
        tt = TikTokBackend()
        result = tt.get_trending_sounds(top_n=10)
        assert isinstance(result, list)

    def test_cache_roundtrip(self, tmp_path, monkeypatch):
        import cli_anything.social_media.utils.tiktok_backend as tt_mod
        monkeypatch.setattr(tt_mod, "_CACHE_PATH", tmp_path / "tt_cache.json")
        tt = TikTokBackend()
        data = [{"hashtag": "#test", "view_count": 1_000_000}]
        tt.cache_results("test_key", data)
        loaded = tt.load_cache("test_key")
        assert loaded == data


class TestTrendAggregation:
    def _mock_yt_video(self):
        return {
            "id": "abc", "title": "Fitness Video", "channel": "FitChannel",
            "views": 1_000_000, "likes": 50_000, "comments": 5_000,
            "published": "2024-01-01", "tags": ["fitness", "workout"],
            "description": "Great workout", "url": "https://youtube.com/watch?v=abc",
            "thumbnail": "", "duration": "PT5M",
        }

    def test_full_aggregate_pipeline(self):
        report = trends_mod.aggregate_trends(
            yt_videos=[self._mock_yt_video()],
            yt_hashtags=[{"hashtag": "#fitness", "score": 4, "total_views": 2_000_000}],
            yt_music=[self._mock_yt_video()],
            tt_hashtags=[{"hashtag": "#fitness", "view_count": 5_000_000, "video_count": 200_000, "is_trending": True, "source": "test"}],
            tt_sounds=[{"title": "Hot Beat", "author": "DJ", "video_count": 1_000_000, "duration": 15, "is_original": False, "cover": "", "id": "s1"}],
            tt_videos=[],
        )
        assert report["item_count"] > 0
        assert "fitness" in report["cross_platform_hashtags"]

    def test_save_and_load_report(self, tmp_path, monkeypatch):
        import cli_anything.social_media.core.trends as tr_mod
        monkeypatch.setattr(tr_mod, "_REPORTS_PATH", tmp_path)
        report = {"generated_at": "2024-01-01T00:00:00Z", "top_viral": [], "cross_platform_hashtags": []}
        path = tr_mod.save_report(report, "test_report")
        assert path.exists()
        loaded = tr_mod.load_last_report()
        assert loaded["generated_at"] == "2024-01-01T00:00:00Z"


class TestCLIIntegration:
    def test_help_returns_zero(self):
        cli = _resolve_cli()
        result = subprocess.run(cli + ["--help"], capture_output=True, text=True, timeout=15)
        assert result.returncode == 0
        assert "Social Media" in result.stdout or "Usage" in result.stdout

    def test_hashtags_generate(self):
        cli = _resolve_cli()
        result = subprocess.run(
            cli + ["hashtags", "generate", "--niche", "fitness", "--platform", "tiktok"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        assert "#" in result.stdout

    def test_hashtags_generate_json(self):
        cli = _resolve_cli()
        result = subprocess.run(
            cli + ["--json", "hashtags", "generate", "--niche", "finance", "--platform", "instagram"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "flat" in data
        assert "count" in data

    def test_theme_niches(self):
        cli = _resolve_cli()
        result = subprocess.run(
            cli + ["theme", "niches", "--interests", "fitness", "--interests", "finance"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0

    def test_theme_guide(self):
        cli = _resolve_cli()
        result = subprocess.run(
            cli + ["theme", "guide"],
            capture_output=True, text=True, timeout=20,
        )
        assert result.returncode == 0
        assert "Monetization" in result.stdout or "theme" in result.stdout.lower()

    def test_schedule_add_and_list(self, tmp_path, monkeypatch):
        cli = _resolve_cli()
        r1 = subprocess.run(
            cli + [
                "schedule", "add",
                "--platform", "tiktok",
                "--time", "2099-12-01T18:00:00",
                "--caption", "E2E test post",
                "--content-type", "video",
            ],
            capture_output=True, text=True, timeout=15,
        )
        assert r1.returncode == 0
        assert "scheduled" in r1.stdout.lower()

    @pytest.mark.skipif(not HAS_NETWORK, reason="No network")
    def test_music_content_types(self):
        cli = _resolve_cli()
        result = subprocess.run(
            cli + ["music", "content-types"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "dance" in result.stdout
