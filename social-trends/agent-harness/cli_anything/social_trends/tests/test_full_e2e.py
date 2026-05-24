"""End-to-end tests for social-trends CLI — requires network access.

These tests make real HTTP requests to TikTok Creative Center and YouTube RSS.
Run with: pytest -v -m e2e --no-header
Skip in CI with: pytest -v -m "not e2e"
"""

import json
import pytest

pytestmark = pytest.mark.e2e


@pytest.fixture(autouse=True)
def skip_without_network(request):
    """Mark all tests in this module as e2e."""
    pass


class TestTikTokHashtagsE2E:
    def test_trending_hashtags_us(self):
        from cli_anything.social_trends.core.trends import get_tiktok_trending_hashtags
        result = get_tiktok_trending_hashtags(region="US", period=7, limit=10, bypass_cache=True)
        assert "hashtags" in result
        assert "source" in result
        # Either got data or got a graceful error with empty list
        assert isinstance(result["hashtags"], list)

    def test_trending_hashtags_gb(self):
        from cli_anything.social_trends.core.trends import get_tiktok_trending_hashtags
        result = get_tiktok_trending_hashtags(region="GB", period=7, limit=5, bypass_cache=True)
        assert isinstance(result.get("hashtags", []), list)

    def test_tiktok_trending_videos(self):
        from cli_anything.social_trends.core.trends import get_tiktok_trending_videos
        result = get_tiktok_trending_videos(region="US", period=7, limit=5, bypass_cache=True)
        assert isinstance(result.get("videos", []), list)


class TestTikTokMusicE2E:
    def test_trending_sounds_us(self):
        from cli_anything.social_trends.core.music import get_tiktok_trending_sounds
        result = get_tiktok_trending_sounds(region="US", period=7, limit=10, bypass_cache=True)
        assert "sounds" in result
        assert isinstance(result["sounds"], list)

    def test_search_sounds(self):
        from cli_anything.social_trends.core.music import search_tiktok_sounds
        result = search_tiktok_sounds("pop", region="US", limit=10, bypass_cache=True)
        assert "query" in result
        assert result["query"] == "pop"
        assert isinstance(result.get("sounds", []), list)


class TestYouTubeRSSE2E:
    def test_youtube_trending_rss_fallback(self):
        from cli_anything.social_trends.core.trends import get_youtube_trending
        from unittest.mock import patch
        with patch("cli_anything.social_trends.core.trends.load_config", return_value={}):
            result = get_youtube_trending(region_code="US", bypass_cache=True)
        assert result["source"] == "youtube_rss"
        assert isinstance(result["videos"], list)


class TestHashtagResearchE2E:
    def test_research_fitness_hashtags(self):
        from cli_anything.social_trends.core.hashtags import research_hashtags
        result = research_hashtags("fitness", platform="tiktok", region="US", limit=20,
                                   bypass_cache=True)
        assert result["topic"] == "fitness"
        assert isinstance(result["hashtags"], list)
        assert len(result["hashtags"]) > 0
        for h in result["hashtags"]:
            assert h["hashtag"].startswith("#")

    def test_generate_fitness_set(self):
        from cli_anything.social_trends.core.hashtags import generate_hashtag_set
        result = generate_hashtag_set("fitness", post_count=3, bypass_cache=True)
        assert len(result["sets"]) == 3
        for s in result["sets"]:
            assert len(s["full_set"]) >= 3
            assert s["copy_paste"].startswith("#")


class TestCLIE2E:
    def test_cli_tiktok_trends(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["trends", "tiktok", "--region", "US", "--limit", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "videos" in data

    def test_cli_youtube_trends_rss(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        from unittest.mock import patch
        runner = CliRunner()
        with patch("cli_anything.social_trends.core.trends.load_config", return_value={}):
            result = runner.invoke(main, ["trends", "youtube", "--region", "US", "--fresh"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "videos" in data

    def test_cli_music_tiktok(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["music", "tiktok", "--region", "US", "--limit", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "sounds" in data
