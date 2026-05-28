"""End-to-end tests for cli-anything-social-trends.

Tests CLI subcommand invocation and output structure.
Run with: python -m pytest cli_anything/social_trends/tests/test_full_e2e.py -v
"""

import pytest
import json
import subprocess
import sys
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli


# ── CLI runner helper ────────────────────────────────────────────────────

@pytest.fixture
def runner():
    return CliRunner()


def invoke(runner, args, input=None):
    result = runner.invoke(cli, args, catch_exceptions=False, input=input)
    return result


# ── Auth commands ────────────────────────────────────────────────────────

class TestAuthCommands:
    def test_auth_status_no_keys(self, runner, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        result = invoke(runner, ["auth", "status"])
        assert result.exit_code == 0
        assert "not set" in result.output

    def test_auth_setup_saves_key(self, runner, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(social_backend, "CONFIG_DIR", tmp_path)
        result = invoke(runner, ["auth", "setup", "--youtube-api-key", "AIzaTest123"])
        assert result.exit_code == 0
        # Config should be saved
        config = social_backend.load_config()
        assert config.get("youtube_api_key") == "AIzaTest123"

    def test_auth_status_json(self, runner, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        result = invoke(runner, ["--json", "auth", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube_api_key" in data
        assert "mode" in data


# ── Trends commands ──────────────────────────────────────────────────────

class TestTrendsTikTok:
    @patch("cli_anything.social_trends.core.tiktok.get_trending_hashtags_web")
    def test_tiktok_trends_output(self, mock_hashtags, runner):
        mock_hashtags.return_value = [
            {"hashtag": "#fitness", "video_count": 5_000_000, "view_count": 50_000_000_000,
             "is_trending": True, "source": "test"},
            {"hashtag": "#gym", "video_count": 1_000_000, "view_count": 10_000_000_000,
             "is_trending": True, "source": "test"},
        ]
        result = invoke(runner, ["trends", "tiktok", "--region", "US"])
        assert result.exit_code == 0
        assert "#fitness" in result.output or "fitness" in result.output

    @patch("cli_anything.social_trends.core.tiktok.get_trending_hashtags_web")
    def test_tiktok_trends_json(self, mock_hashtags, runner):
        mock_hashtags.return_value = [
            {"hashtag": "#fitness", "video_count": 5_000_000, "view_count": 50_000_000_000, "source": "test"},
        ]
        result = invoke(runner, ["--json", "trends", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_hashtags" in data
        assert isinstance(data["trending_hashtags"], list)

    @patch("cli_anything.social_trends.core.tiktok.get_trending_hashtags_web")
    @patch("cli_anything.social_trends.core.tiktok.get_trending_sounds_web")
    def test_tiktok_with_sounds(self, mock_sounds, mock_hashtags, runner):
        mock_hashtags.return_value = [{"hashtag": "#test", "video_count": 100, "view_count": 1000, "source": "test"}]
        mock_sounds.return_value = [{"sound_id": "1", "title": "Test Song", "artist": "Test", "video_count": 1000, "source": "test"}]
        result = invoke(runner, ["trends", "tiktok", "--sounds"])
        assert result.exit_code == 0
        assert "Test Song" in result.output


class TestTrendsYouTube:
    @patch("cli_anything.social_trends.core.youtube.get_trending_ytdlp")
    @patch("cli_anything.social_trends.utils.social_backend.load_config")
    def test_youtube_trends_output(self, mock_config, mock_ytdlp, runner):
        mock_config.return_value = {}
        mock_ytdlp.return_value = [
            {
                "id": "abc", "title": "Best Workout 2024", "channel": "FitnessTV",
                "views": 1_000_000, "likes": 50000, "comments": 2000,
                "engagement_rate": 5.2, "tags": ["fitness", "workout"],
                "url": "https://youtube.com/watch?v=abc", "source": "ytdlp",
                "published": "20240101", "description": "", "thumbnail": "",
                "category_id": "",
            }
        ]
        result = invoke(runner, ["trends", "youtube", "--region", "US"])
        assert result.exit_code == 0
        assert "Best Workout 2024" in result.output

    @patch("cli_anything.social_trends.core.youtube.get_trending_ytdlp")
    @patch("cli_anything.social_trends.utils.social_backend.load_config")
    def test_youtube_trends_json(self, mock_config, mock_ytdlp, runner):
        mock_config.return_value = {}
        mock_ytdlp.return_value = [
            {
                "id": "abc", "title": "Video 1", "channel": "Chan1",
                "views": 100000, "likes": 5000, "comments": 200,
                "engagement_rate": 5.2, "tags": [], "url": "",
                "source": "ytdlp", "published": "", "description": "", "thumbnail": "",
                "category_id": "",
            }
        ]
        result = invoke(runner, ["--json", "trends", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "videos" in data


# ── Hashtag commands ─────────────────────────────────────────────────────

class TestHashtagCommands:
    def test_recommend_fitness_tiktok(self, runner):
        result = invoke(runner, ["hashtags", "recommend", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()
        assert "Strategy" in result.output or "strategy" in result.output

    def test_recommend_unknown_niche(self, runner):
        result = invoke(runner, ["hashtags", "recommend", "--niche", "underwater_weaving", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_recommend_json(self, runner):
        result = invoke(runner, ["--json", "hashtags", "recommend", "--niche", "gaming"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "broad" in data
        assert "niche_specific" in data

    def test_analyze_good_tags(self, runner):
        result = invoke(runner, ["hashtags", "analyze", "#fyp #fitness #gym #workout #fitcheck"])
        assert result.exit_code == 0
        assert "Quality Score" in result.output or "score" in result.output.lower()

    def test_analyze_too_many_tags(self, runner):
        tags = " ".join(f"#tag{i}" for i in range(35))
        result = invoke(runner, ["hashtags", "analyze", tags])
        assert result.exit_code == 0
        # Should warn about too many
        assert "Too many" in result.output or "too many" in result.output.lower() or "issue" in result.output.lower()

    def test_analyze_json(self, runner):
        result = invoke(runner, ["--json", "hashtags", "analyze", "#fitness #gym #workout"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "quality_score" in data
        assert "issues" in data

    @patch("cli_anything.social_trends.core.tiktok.get_trending_hashtags_web")
    def test_discover_hashtags(self, mock_tt, runner):
        mock_tt.return_value = [
            {"hashtag": "#fitness", "video_count": 1_000_000, "view_count": 100_000_000, "source": "test"},
            {"hashtag": "#gym", "video_count": 500_000, "view_count": 80_000_000, "source": "test"},
        ]
        result = invoke(runner, ["hashtags", "discover"])
        assert result.exit_code == 0

    @patch("cli_anything.social_trends.core.tiktok.search_hashtag")
    def test_lookup_hashtag(self, mock_search, runner):
        mock_search.return_value = {
            "hashtag": "#fitness", "title": "fitness", "description": "",
            "video_count": 5_000_000, "view_count": 50_000_000_000, "source": "test",
        }
        result = invoke(runner, ["hashtags", "lookup", "fitness"])
        assert result.exit_code == 0


# ── Music commands ───────────────────────────────────────────────────────

class TestMusicCommands:
    @patch("cli_anything.social_trends.core.tiktok.get_trending_sounds_web")
    def test_music_trending_tiktok(self, mock_sounds, runner):
        mock_sounds.return_value = [
            {"sound_id": "1", "title": "Espresso", "artist": "Sabrina Carpenter",
             "video_count": 3_000_000, "is_original": False, "source": "test"},
        ]
        result = invoke(runner, ["music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Espresso" in result.output

    @patch("cli_anything.social_trends.core.tiktok.get_trending_sounds_web")
    def test_music_trending_json(self, mock_sounds, runner):
        mock_sounds.return_value = [
            {"sound_id": "1", "title": "Test", "artist": "Test Artist",
             "video_count": 1000, "is_original": False, "source": "test"},
        ]
        result = invoke(runner, ["--json", "music", "trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_sounds" in data

    def test_music_strategy_fitness(self, runner):
        result = invoke(runner, ["music", "strategy", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "hip-hop" in result.output.lower() or "genre" in result.output.lower()

    def test_music_strategy_json(self, runner):
        result = invoke(runner, ["--json", "music", "strategy", "--niche", "cooking"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "recommended_genres" in data
        assert "audio_tips" in data


# ── Accounts commands ─────────────────────────────────────────────────────

class TestAccountsCommands:
    def test_analyze_basic(self, runner):
        result = invoke(runner, [
            "accounts", "analyze",
            "--followers", "5000",
            "--avg-views", "10000",
            "--avg-likes", "800",
            "--avg-comments", "50",
            "--platform", "tiktok",
        ])
        assert result.exit_code == 0
        assert "Engagement Rate" in result.output
        assert "Account Score" in result.output

    def test_analyze_json_output(self, runner):
        result = invoke(runner, [
            "--json", "accounts", "analyze",
            "--followers", "10000",
            "--avg-views", "20000",
            "--avg-likes", "1500",
            "--avg-comments", "100",
            "--platform", "tiktok",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "engagement" in data
        assert "monetization_status" in data
        assert "score" in data
        assert "top_recommendations" in data

    def test_analyze_monetization_eligible(self, runner):
        result = invoke(runner, [
            "--json", "accounts", "analyze",
            "--followers", "15000",
            "--avg-views", "150000",
            "--avg-likes", "8000",
            "--platform", "tiktok",
        ])
        data = json.loads(result.output)
        assert "TikTok Creator Rewards Program" in data["monetization_status"]["eligible"]

    def test_bio_fitness_tiktok(self, runner):
        result = invoke(runner, ["accounts", "bio", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Bio" in result.output
        assert "Character" in result.output

    def test_bio_json(self, runner):
        result = invoke(runner, ["--json", "accounts", "bio", "--niche", "gaming", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bio" in data
        assert "character_count" in data
        assert "tips" in data

    def test_schedule_tiktok(self, runner):
        result = invoke(runner, ["accounts", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Best Days" in result.output
        assert "Best Times UTC" in result.output

    def test_schedule_json(self, runner):
        result = invoke(runner, ["--json", "accounts", "schedule", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "best_days" in data
        assert "frequency" in data

    def test_accounts_list_empty(self, runner, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_DIR", tmp_path)
        result = invoke(runner, ["accounts", "list"])
        assert result.exit_code == 0


# ── Theme page commands ──────────────────────────────────────────────────

class TestThemePageCommands:
    def test_niches_list(self, runner):
        result = invoke(runner, ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output
        assert "finance" in result.output

    def test_niches_json(self, runner):
        result = invoke(runner, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 10

    def test_niches_sort_competition(self, runner):
        result = invoke(runner, ["theme-page", "niches", "--sort", "competition"])
        assert result.exit_code == 0

    def test_niche_info(self, runner):
        result = invoke(runner, ["theme-page", "info", "fitness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_niche_info_json(self, runner):
        result = invoke(runner, ["--json", "theme-page", "info", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "monetization_methods" in data

    def test_convert_small_account(self, runner):
        result = invoke(runner, [
            "theme-page", "convert",
            "--from", "personal",
            "--to", "fitness",
            "--followers", "1000",
        ])
        assert result.exit_code == 0
        assert "hard_pivot" in result.output or "Hard Pivot" in result.output

    def test_convert_large_account(self, runner):
        result = invoke(runner, [
            "theme-page", "convert",
            "--from", "lifestyle",
            "--to", "finance",
            "--followers", "100000",
        ])
        assert result.exit_code == 0
        assert "start_fresh" in result.output or "Start Fresh" in result.output

    def test_convert_json(self, runner):
        result = invoke(runner, [
            "--json", "theme-page", "convert",
            "--from", "personal",
            "--to", "gaming",
            "--followers", "5000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "roadmap" in data
        assert "branding_checklist" in data
        assert "monetization_timeline" in data

    def test_content_strategy(self, runner):
        result = invoke(runner, ["theme-page", "content", "--niche", "cooking"])
        assert result.exit_code == 0
        assert "Content Pillar" in result.output or "pillar" in result.output.lower()

    def test_content_strategy_json(self, runner):
        result = invoke(runner, ["--json", "theme-page", "content", "--niche", "fitness", "--posts-per-week", "14"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "pillars" in data
        assert "content_ideas" in data
        assert len(data["content_ideas"]) >= 10

    def test_guide_output(self, runner):
        result = invoke(runner, ["theme-page", "guide"])
        assert result.exit_code == 0
        assert "Theme Page" in result.output or "theme page" in result.output.lower()
        assert "Monetization" in result.output


# ── CLI subprocess test ───────────────────────────────────────────────────

class TestCLIInstalled:
    def test_cli_help_flag(self):
        import os
        force_installed = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED")
        if not force_installed:
            pytest.skip("Set CLI_ANYTHING_FORCE_INSTALLED=1 to run installed CLI tests")

        result = subprocess.run(
            ["cli-anything-social-trends", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "Social Trends" in result.stdout or "social" in result.stdout.lower()

    def test_cli_json_auth_status(self):
        import os
        if not os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
            pytest.skip("Set CLI_ANYTHING_FORCE_INSTALLED=1 to run installed CLI tests")

        result = subprocess.run(
            ["cli-anything-social-trends", "--json", "auth", "status"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "mode" in data
