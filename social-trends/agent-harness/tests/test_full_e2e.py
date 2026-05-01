"""End-to-end tests for social-trends CLI commands.

Tests the Click CLI via CliRunner — covers every command group and subcommand.
All tests run in demo mode (no API keys needed).
"""

import sys
import os
import json
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture(autouse=True)
def clear_api_keys(monkeypatch):
    """Ensure all tests run in demo mode — clear API key env vars and config."""
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.delenv("TIKTOK_RAPIDAPI_KEY", raising=False)
    # Patch the get_api_key functions to return None so config file is bypassed
    import cli_anything.social_trends.utils.youtube_backend as yt_mod
    import cli_anything.social_trends.utils.tiktok_backend as tt_mod
    monkeypatch.setattr(yt_mod, "get_api_key", lambda cli_key=None: None)
    monkeypatch.setattr(tt_mod, "get_api_key", lambda cli_key=None: None)


@pytest.fixture
def runner():
    return CliRunner()


# ── CLI root ──────────────────────────────────────────────────────────────────

class TestCLIRoot:

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "social-trends" in result.output

    def test_version(self, runner):
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_json_flag_is_global(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--limit", "2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "items" in data
        assert data["total"] == 2


# ── trends youtube ────────────────────────────────────────────────────────────

class TestTrendsYouTube:

    def test_basic(self, runner):
        result = runner.invoke(cli, ["trends", "youtube"])
        assert result.exit_code == 0
        assert "YouTube Trending" in result.output

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--limit", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_limit_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--limit", "5"])
        data = json.loads(result.output)
        assert data["total"] == 5

    def test_region_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--region", "GB"])
        data = json.loads(result.output)
        assert data["region"] == "GB"

    def test_category_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--category", "music"])
        data = json.loads(result.output)
        assert data["category"] == "music"

    def test_demo_mode_note_shown(self, runner):
        result = runner.invoke(cli, ["trends", "youtube", "--limit", "3"])
        assert "Demo" in result.output or "demo" in result.output

    def test_item_fields_present(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "youtube", "--limit", "1"])
        data = json.loads(result.output)
        item = data["items"][0]
        assert "rank" in item
        assert "title" in item
        assert "views" in item
        assert "likes" in item

    def test_help(self, runner):
        result = runner.invoke(cli, ["trends", "youtube", "--help"])
        assert result.exit_code == 0
        assert "region" in result.output.lower()


# ── trends tiktok ─────────────────────────────────────────────────────────────

class TestTrendsTikTok:

    def test_basic(self, runner):
        result = runner.invoke(cli, ["trends", "tiktok"])
        assert result.exit_code == 0
        assert "TikTok Trending" in result.output

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "tiktok", "--limit", "3"])
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert data["total"] == 3

    def test_limit_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "tiktok", "--limit", "4"])
        data = json.loads(result.output)
        assert data["total"] == 4

    def test_region_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "tiktok", "--region", "UK"])
        data = json.loads(result.output)
        assert data["region"] == "UK"

    def test_item_fields(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "tiktok", "--limit", "1"])
        data = json.loads(result.output)
        item = data["items"][0]
        assert "desc" in item
        assert "author" in item
        assert "plays" in item
        assert "music" in item

    def test_help(self, runner):
        result = runner.invoke(cli, ["trends", "tiktok", "--help"])
        assert result.exit_code == 0


# ── trends hashtags ───────────────────────────────────────────────────────────

class TestTrendsHashtags:

    def test_tiktok_basic(self, runner):
        result = runner.invoke(cli, ["trends", "hashtags", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_youtube_basic(self, runner):
        result = runner.invoke(cli, ["trends", "hashtags", "--platform", "youtube"])
        assert result.exit_code == 0

    def test_with_niche(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "hashtags", "--platform", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "fitness"
        assert data["total"] > 0

    def test_json_output_schema(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "hashtags", "--limit", "5"])
        data = json.loads(result.output)
        assert "items" in data
        assert data["total"] == 5

    def test_all_platform(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "hashtags", "--platform", "all"])
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" in data

    def test_limit_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "hashtags", "--platform", "tiktok", "--limit", "3"])
        data = json.loads(result.output)
        assert data["total"] == 3

    def test_help(self, runner):
        result = runner.invoke(cli, ["trends", "hashtags", "--help"])
        assert result.exit_code == 0


# ── trends music ──────────────────────────────────────────────────────────────

class TestTrendsMusic:

    def test_tiktok_basic(self, runner):
        result = runner.invoke(cli, ["trends", "music", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_youtube_basic(self, runner):
        result = runner.invoke(cli, ["trends", "music", "--platform", "youtube"])
        assert result.exit_code == 0

    def test_all_platform(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "music", "--platform", "all", "--limit", "3"])
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" in data

    def test_json_tiktok(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "music", "--platform", "tiktok", "--limit", "3"])
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert data["type"] == "sounds"
        assert len(data["items"]) == 3

    def test_json_youtube(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "music", "--platform", "youtube", "--limit", "3"])
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert data["type"] == "music"

    def test_limit_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "music", "--limit", "4"])
        data = json.loads(result.output)
        assert data["total"] == 4


# ── trends all ────────────────────────────────────────────────────────────────

class TestTrendsAll:

    def test_basic(self, runner):
        result = runner.invoke(cli, ["trends", "all"])
        assert result.exit_code == 0
        assert "YOUTUBE" in result.output
        assert "TIKTOK" in result.output

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "all", "--limit", "3"])
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" in data
        assert "insights" in data
        assert "cross_platform" in data

    def test_region_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "all", "--region", "GB", "--limit", "2"])
        data = json.loads(result.output)
        assert data["region"] == "GB"

    def test_shows_insights(self, runner):
        result = runner.invoke(cli, ["trends", "all", "--limit", "3"])
        assert "INSIGHTS" in result.output

    def test_limit_flag(self, runner):
        result = runner.invoke(cli, ["--json", "trends", "all", "--limit", "2"])
        data = json.loads(result.output)
        assert len(data["youtube"]["trending_videos"]) == 2
        assert len(data["tiktok"]["trending_videos"]) == 2


# ── optimize bio ──────────────────────────────────────────────────────────────

class TestOptimizeBio:

    def test_tiktok_fitness(self, runner):
        result = runner.invoke(cli, ["optimize", "bio", "--platform", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "Template" in result.output

    def test_youtube_finance(self, runner):
        result = runner.invoke(cli, ["optimize", "bio", "--platform", "youtube", "--niche", "finance"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "bio", "--platform", "tiktok", "--niche", "beauty"])
        data = json.loads(result.output)
        assert "templates" in data
        assert "placeholders" in data
        assert "bio_rules" in data
        assert len(data["templates"]) > 0

    def test_missing_platform_errors(self, runner):
        result = runner.invoke(cli, ["optimize", "bio", "--niche", "fitness"])
        assert result.exit_code != 0

    def test_missing_niche_errors(self, runner):
        result = runner.invoke(cli, ["optimize", "bio", "--platform", "tiktok"])
        assert result.exit_code != 0

    def test_shows_bio_rules(self, runner):
        result = runner.invoke(cli, ["optimize", "bio", "--platform", "tiktok", "--niche", "travel"])
        assert "Rules" in result.output or "rules" in result.output.lower()


# ── optimize schedule ─────────────────────────────────────────────────────────

class TestOptimizeSchedule:

    def test_tiktok(self, runner):
        result = runner.invoke(cli, ["optimize", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Frequency" in result.output

    def test_youtube(self, runner):
        result = runner.invoke(cli, ["optimize", "schedule", "--platform", "youtube"])
        assert result.exit_code == 0

    def test_instagram(self, runner):
        result = runner.invoke(cli, ["optimize", "schedule", "--platform", "instagram"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "schedule", "--platform", "tiktok"])
        data = json.loads(result.output)
        assert "frequency" in data
        assert "best_days" in data
        assert "recommended_slots" in data

    def test_timezone_flag(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "schedule", "--platform", "tiktok", "--timezone", "PST"])
        data = json.loads(result.output)
        assert "PST" in data["timezone_note"]


# ── optimize hashtags ─────────────────────────────────────────────────────────

class TestOptimizeHashtags:

    def test_fitness_tiktok(self, runner):
        result = runner.invoke(cli, ["optimize", "hashtags", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "hashtags", "--niche", "finance"])
        data = json.loads(result.output)
        assert "strategy" in data
        assert "recommended_mix" in data["strategy"]
        assert "rules" in data

    def test_count_flag(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "hashtags", "--niche", "beauty", "--count", "5"])
        data = json.loads(result.output)
        assert data["total"] <= 5

    def test_missing_niche_errors(self, runner):
        result = runner.invoke(cli, ["optimize", "hashtags"])
        assert result.exit_code != 0


# ── optimize content-plan ─────────────────────────────────────────────────────

class TestOptimizeContentPlan:

    def test_fitness(self, runner):
        result = runner.invoke(cli, ["optimize", "content-plan", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "content-plan", "--niche", "finance"])
        data = json.loads(result.output)
        assert "content_plan" in data
        assert "viral_hooks" in data
        assert "pro_tips" in data
        assert len(data["content_plan"]) > 0

    def test_days_flag(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "content-plan", "--niche", "fitness", "--days", "3"])
        data = json.loads(result.output)
        assert len(data["content_plan"]) <= 3

    def test_platform_filter_tiktok(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "content-plan", "--niche", "general", "--platform", "tiktok"])
        data = json.loads(result.output)
        for day in data["content_plan"]:
            assert day["platform"] in ("tiktok", "both")


# ── optimize checklist ────────────────────────────────────────────────────────

class TestOptimizeChecklist:

    def test_tiktok(self, runner):
        result = runner.invoke(cli, ["optimize", "checklist", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Profile" in result.output or "checklist" in result.output.lower()

    def test_youtube(self, runner):
        result = runner.invoke(cli, ["optimize", "checklist", "--platform", "youtube"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "checklist", "--platform", "tiktok"])
        data = json.loads(result.output)
        assert "checklist" in data
        assert len(data["checklist"]) >= 8
        for item in data["checklist"]:
            assert "item" in item
            assert "tip" in item


# ── theme niches ──────────────────────────────────────────────────────────────

class TestThemeNiches:

    def test_basic(self, runner):
        result = runner.invoke(cli, ["theme", "niches"])
        assert result.exit_code == 0
        assert "Niche" in result.output

    def test_filter_easy(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches", "--filter", "easy"])
        data = json.loads(result.output)
        for n in data["niches"]:
            assert n["difficulty"] == "easy"

    def test_filter_high_income(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches", "--filter", "high_income"])
        data = json.loads(result.output)
        for n in data["niches"]:
            assert n["monetization_potential"] in ("very_high", "extreme")

    def test_json_schema(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        data = json.loads(result.output)
        assert "niches" in data
        assert "total" in data
        assert data["total"] > 0


# ── theme strategy ────────────────────────────────────────────────────────────

class TestThemeStrategy:

    def test_luxury(self, runner):
        result = runner.invoke(cli, ["theme", "strategy", "--niche", "luxury"])
        assert result.exit_code == 0
        assert "Luxury" in result.output

    def test_fitness(self, runner):
        result = runner.invoke(cli, ["theme", "strategy", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "strategy", "--niche", "luxury"])
        data = json.loads(result.output)
        assert "niche" in data
        assert "overview" in data
        assert "quick_start" in data
        assert "monetization_roadmap" in data

    def test_unknown_niche_handled(self, runner):
        result = runner.invoke(cli, ["theme", "strategy", "--niche", "quantum_memes"])
        assert result.exit_code in (0, 1)

    def test_platform_flag(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "strategy", "--niche", "fitness", "--platform", "tiktok"])
        data = json.loads(result.output)
        assert "platform_specific" in data


# ── theme convert ─────────────────────────────────────────────────────────────

class TestThemeConvert:

    def test_general_guide(self, runner):
        result = runner.invoke(cli, ["theme", "convert"])
        assert result.exit_code == 0

    def test_specific_conversion(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "convert", "--from-niche", "luxury", "--to-niche", "finance"])
        data = json.loads(result.output)
        assert data["type"] == "specific_conversion"
        assert "steps" in data

    def test_general_json_has_guide(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "convert"])
        data = json.loads(result.output)
        assert data["type"] == "general_conversion_guide"
        assert "guide" in data
        assert "steps" in data["guide"]

    def test_shows_timeline(self, runner):
        result = runner.invoke(cli, ["theme", "convert"])
        assert "Timeline" in result.output or "timeline" in result.output.lower()


# ── theme monetize ────────────────────────────────────────────────────────────

class TestThemeMonetize:

    def test_fitness(self, runner):
        result = runner.invoke(cli, ["theme", "monetize", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "Revenue" in result.output or "revenue" in result.output.lower()

    def test_finance(self, runner):
        result = runner.invoke(cli, ["theme", "monetize", "--niche", "finance"])
        assert result.exit_code == 0

    def test_json_output(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "monetize", "--niche", "fitness"])
        data = json.loads(result.output)
        assert "revenue_streams" in data
        assert "follower_milestones" in data
        assert "platform_revenue" in data

    def test_missing_niche_errors(self, runner):
        result = runner.invoke(cli, ["theme", "monetize"])
        assert result.exit_code != 0


# ── auth ──────────────────────────────────────────────────────────────────────

class TestAuth:

    def test_status(self, runner):
        result = runner.invoke(cli, ["auth", "status"])
        assert result.exit_code == 0
        assert "YouTube" in result.output
        assert "TikTok" in result.output

    def test_status_json(self, runner):
        result = runner.invoke(cli, ["--json", "auth", "status"])
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" in data
        assert "env_vars" in data

    def test_set_youtube_key(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        from cli_anything.social_trends.utils import youtube_backend as yt_fresh
        result = runner.invoke(cli, ["auth", "set-youtube-key", "fake_test_key_abc123"])
        assert result.exit_code == 0
        assert "saved" in result.output.lower() or "YouTube" in result.output

    def test_set_tiktok_key(self, runner, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        result = runner.invoke(cli, ["auth", "set-tiktok-key", "fake_tiktok_key_xyz789"])
        assert result.exit_code == 0

    def test_status_help(self, runner):
        result = runner.invoke(cli, ["auth", "status", "--help"])
        assert result.exit_code == 0
