"""End-to-end CLI tests for cli-anything-social-trends.

All network calls are mocked — tests verify CLI command output and JSON mode.
"""

import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock


@pytest.fixture
def runner():
    return CliRunner()


def _main():
    from cli_anything.social_trends.social_trends_cli import main
    return main


# ── trends fetch youtube ──────────────────────────────────────────────────────

class TestTrendsYouTubeE2E:
    def _mock_videos(self):
        from cli_anything.social_trends.core.youtube_trends import YouTubeVideo
        return [
            YouTubeVideo(
                video_id=f"vid{i}", title=f"Trending Video {i}", channel=f"Channel{i}",
                view_count=i * 100_000, like_count=i * 5_000, comment_count=i * 500,
                tags=[f"tag{i}", "trending"], description_snippet="Great content",
                published_at="2024-01-15T10:00:00Z", duration=f"{i+1}:00",
                category="all", thumbnail_url=f"https://img.youtube.com/vi/vid{i}/hq.jpg",
            )
            for i in range(1, 6)
        ]

    def test_youtube_command_exits_zero(self, runner):
        videos = self._mock_videos()
        with patch("cli_anything.social_trends.core.youtube_trends.fetch_trending", return_value=videos):
            result = runner.invoke(_main(), ["trends", "fetch", "youtube", "--region", "US"])
        assert result.exit_code == 0

    def test_youtube_shows_video_titles(self, runner):
        videos = self._mock_videos()
        with patch("cli_anything.social_trends.core.youtube_trends.fetch_trending", return_value=videos):
            result = runner.invoke(_main(), ["trends", "fetch", "youtube"])
        for v in videos:
            assert v.title[:30] in result.output

    def test_youtube_json_output_valid(self, runner):
        videos = self._mock_videos()
        with patch("cli_anything.social_trends.core.youtube_trends.fetch_trending", return_value=videos):
            result = runner.invoke(_main(), ["--json", "trends", "fetch", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == len(videos)
        assert "video_id" in data[0]

    def test_youtube_shows_top_tags(self, runner):
        videos = self._mock_videos()
        with patch("cli_anything.social_trends.core.youtube_trends.fetch_trending", return_value=videos):
            result = runner.invoke(_main(), ["trends", "fetch", "youtube"])
        assert "Top Tags" in result.output or "trending" in result.output

    def test_youtube_error_exits_nonzero(self, runner):
        with patch("cli_anything.social_trends.core.youtube_trends.fetch_trending",
                   side_effect=RuntimeError("API error")):
            result = runner.invoke(_main(), ["trends", "fetch", "youtube"])
        assert result.exit_code != 0


# ── trends fetch tiktok ───────────────────────────────────────────────────────

class TestTrendsTikTokE2E:
    def _mock_hashtags(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag
        return [
            TikTokHashtag(name=f"tag{i}", post_count=i*1_000_000,
                          view_count=i*10_000_000, trend_score=float(i*10), rank=i)
            for i in range(1, 6)
        ]

    def _mock_sounds(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokSound
        return [
            TikTokSound(id=str(i), title=f"Song {i}", artist=f"Artist {i}",
                        clip_count=i*100_000, trend_score=float(i*10),
                        rank=i, duration_seconds=30, cover_url="")
            for i in range(1, 4)
        ]

    def _mock_videos(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokVideo
        return [
            TikTokVideo(video_id=f"vid{i}", description=f"Caption {i} #fyp",
                        author=f"creator{i}", play_count=i*50_000,
                        like_count=i*5_000, comment_count=i*200, share_count=i*100,
                        hashtags=["fyp", "viral"], music_title="Song", music_artist="Artist",
                        cover_url="")
            for i in range(1, 4)
        ]

    def test_tiktok_command_exits_zero(self, runner):
        with patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_hashtags",
                   return_value=self._mock_hashtags()), \
             patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_sounds",
                   return_value=self._mock_sounds()), \
             patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_videos",
                   return_value=self._mock_videos()):
            result = runner.invoke(_main(), ["trends", "fetch", "tiktok"])
        assert result.exit_code == 0

    def test_tiktok_json_output(self, runner):
        with patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_hashtags",
                   return_value=self._mock_hashtags()), \
             patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_sounds",
                   return_value=self._mock_sounds()), \
             patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_videos",
                   return_value=self._mock_videos()):
            result = runner.invoke(_main(), ["--json", "trends", "fetch", "tiktok"])
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "sounds" in data
        assert "videos" in data


# ── hashtags suggest ──────────────────────────────────────────────────────────

class TestHashtagsSuggestE2E:
    def test_suggest_fitness_curated_fallback(self, runner):
        with patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_hashtags",
                   side_effect=RuntimeError("offline")):
            result = runner.invoke(_main(), ["hashtags", "suggest", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_suggest_json_returns_list(self, runner):
        with patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_hashtags",
                   side_effect=RuntimeError("offline")):
            result = runner.invoke(_main(), ["--json", "hashtags", "suggest", "--niche", "travel"])
        data = json.loads(result.output)
        assert "hashtags" in data
        assert isinstance(data["hashtags"], list)

    def test_suggest_count_respected(self, runner):
        with patch("cli_anything.social_trends.core.tiktok_trends.fetch_trending_hashtags",
                   side_effect=RuntimeError("offline")):
            result = runner.invoke(_main(), ["--json", "hashtags", "suggest",
                                             "--niche", "food", "--count", "10"])
        data = json.loads(result.output)
        assert len(data["hashtags"]) <= 10


# ── music trending ────────────────────────────────────────────────────────────

class TestMusicTrendingE2E:
    def _mock_tracks(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        return [
            TrackEntry(title=f"Track {i}", artist=f"Artist {i}", platform="tiktok",
                       clip_count=i*500_000, trend_score=float(i*10),
                       duration_seconds=30, cover_url="",
                       track_url=f"https://tiktok.com/music/{i}", rank=i)
            for i in range(1, 6)
        ]

    def test_music_trending_exits_zero(self, runner):
        tracks = self._mock_tracks()
        with patch("cli_anything.social_trends.core.music_tracker.fetch_tiktok_music",
                   return_value=tracks):
            result = runner.invoke(_main(), ["music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_music_trending_json(self, runner):
        tracks = self._mock_tracks()
        with patch("cli_anything.social_trends.core.music_tracker.fetch_tiktok_music",
                   return_value=tracks):
            result = runner.invoke(_main(), ["--json", "music", "trending", "--platform", "tiktok"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["title"] == "Track 1"


# ── account optimize ──────────────────────────────────────────────────────────

class TestAccountOptimizeE2E:
    def test_optimize_shows_checklist(self, runner):
        result = runner.invoke(_main(), ["account", "optimize", "--platform", "tiktok",
                                         "--niche", "fitness"])
        assert result.exit_code == 0
        assert "CRITICAL" in result.output or "critical" in result.output.lower()

    def test_optimize_json(self, runner):
        result = runner.invoke(_main(), ["--json", "account", "optimize",
                                         "--platform", "tiktok", "--niche", "gaming"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "category" in data[0]
        assert "action" in data[0]

    def test_schedule_exits_zero(self, runner):
        result = runner.invoke(_main(), ["account", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Tuesday" in result.output or "Friday" in result.output

    def test_bio_shows_templates(self, runner):
        result = runner.invoke(_main(), ["account", "bio", "--platform", "tiktok",
                                         "--niche", "travel"])
        assert result.exit_code == 0
        assert "travel" in result.output.lower()


# ── theme-page ────────────────────────────────────────────────────────────────

class TestThemePageE2E:
    def test_niches_lists_table(self, runner):
        result = runner.invoke(_main(), ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "Finance" in result.output or "Fitness" in result.output

    def test_niches_json(self, runner):
        result = runner.invoke(_main(), ["--json", "theme-page", "niches"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert any(n["name"] == "Finance / Money" for n in data)

    def test_strategy_shows_phases(self, runner):
        result = runner.invoke(_main(), ["theme-page", "strategy", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "Phase 1" in result.output
        assert "Phase 6" in result.output

    def test_strategy_json(self, runner):
        result = runner.invoke(_main(), ["--json", "theme-page", "strategy", "--niche", "gaming"])
        data = json.loads(result.output)
        assert len(data) == 6

    def test_convert_shows_funnel(self, runner):
        result = runner.invoke(_main(), ["theme-page", "convert", "--niche", "finance"])
        assert result.exit_code == 0
        assert "Awareness" in result.output
        assert "Monetisation" in result.output

    def test_ethics_guide_shows_rules(self, runner):
        result = runner.invoke(_main(), ["theme-page", "ethics"])
        assert result.exit_code == 0
        assert "credit" in result.output.lower() or "permission" in result.output.lower()

    def test_ethics_json(self, runner):
        result = runner.invoke(_main(), ["--json", "theme-page", "ethics"])
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 4


# ── version & help ────────────────────────────────────────────────────────────

class TestCLIMetaE2E:
    def test_version_flag(self, runner):
        result = runner.invoke(_main(), ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help_flag(self, runner):
        result = runner.invoke(_main(), ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output
        assert "hashtags" in result.output
        assert "music" in result.output
        assert "account" in result.output
        assert "theme-page" in result.output

    def test_subcommand_help(self, runner):
        result = runner.invoke(_main(), ["trends", "--help"])
        assert result.exit_code == 0
