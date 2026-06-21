"""E2E tests for Social Trends CLI — tests CLI subprocess behavior."""

import json
import subprocess
import sys
import os
import pytest

_PKG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
_CLI_MODULE = "cli_anything.social_trends.social_trends_cli"


def run_cli(*args, expect_success=True) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, "-m", _CLI_MODULE] + list(args),
        capture_output=True,
        text=True,
        cwd=_PKG_DIR,
    )
    return result.returncode, result.stdout, result.stderr


def run_cli_json(*args) -> tuple[int, dict | list]:
    code, out, err = run_cli("--json", *args)
    if code != 0:
        return code, {}
    try:
        return code, json.loads(out)
    except json.JSONDecodeError:
        return code, {}


# ─────────────────────────────────────────────────────────────────────
# CLI invocation basics
# ─────────────────────────────────────────────────────────────────────

class TestCLIInvocation:
    def test_help_exits_zero(self):
        code, out, _ = run_cli("--help")
        assert code == 0
        assert "social" in out.lower() or "trend" in out.lower()

    def test_version_flag(self):
        code, out, _ = run_cli("--version")
        assert code == 0
        assert "1.0.0" in out

    def test_config_status_exits_zero(self):
        code, out, _ = run_cli("config", "status")
        assert code == 0

    def test_config_status_json(self):
        code, data = run_cli_json("config", "status")
        assert code == 0
        assert isinstance(data, dict)
        assert "youtube_api_key_set" in data

    def test_config_setup_guide_exits_zero(self):
        code, out, _ = run_cli("config", "setup-guide")
        assert code == 0

    def test_tiktok_help(self):
        code, out, _ = run_cli("tiktok", "--help")
        assert code == 0

    def test_youtube_help(self):
        code, out, _ = run_cli("youtube", "--help")
        assert code == 0

    def test_hashtags_help(self):
        code, out, _ = run_cli("hashtags", "--help")
        assert code == 0

    def test_account_help(self):
        code, out, _ = run_cli("account", "--help")
        assert code == 0

    def test_theme_page_help(self):
        code, out, _ = run_cli("theme-page", "--help")
        assert code == 0

    def test_trends_help(self):
        code, out, _ = run_cli("trends", "--help")
        assert code == 0


# ─────────────────────────────────────────────────────────────────────
# TikTok CLI (uses curated fallback — no API required)
# ─────────────────────────────────────────────────────────────────────

class TestTikTokCLI:
    def test_hashtags_exits_zero(self):
        code, out, _ = run_cli("tiktok", "hashtags")
        assert code == 0

    def test_hashtags_niche_filter(self):
        code, out, _ = run_cli("tiktok", "hashtags", "--niche", "fitness")
        assert code == 0

    def test_hashtags_json_output(self):
        code, data = run_cli_json("tiktok", "hashtags", "--niche", "music")
        assert code == 0
        assert isinstance(data, list)
        assert len(data) > 0
        assert "hashtag" in data[0]

    def test_niches_list(self):
        code, out, _ = run_cli("tiktok", "niches")
        assert code == 0

    def test_niches_json(self):
        code, data = run_cli_json("tiktok", "niches")
        assert code == 0
        assert isinstance(data, list)
        assert "fitness" in data

    def test_niche_tags(self):
        code, out, _ = run_cli("tiktok", "niche-tags", "beauty")
        assert code == 0

    def test_niche_tags_json(self):
        code, data = run_cli_json("tiktok", "niche-tags", "motivation")
        assert code == 0
        assert isinstance(data, list)
        assert all(t["hashtag"].startswith("#") for t in data)

    def test_sounds_exits_zero(self):
        code, out, _ = run_cli("tiktok", "sounds")
        assert code == 0


# ─────────────────────────────────────────────────────────────────────
# Hashtags CLI
# ─────────────────────────────────────────────────────────────────────

class TestHashtagsCLI:
    def test_score_exits_zero(self):
        code, out, _ = run_cli("hashtags", "score", "#fyp,#fitness,#workout")
        assert code == 0

    def test_score_json(self):
        code, data = run_cli_json("hashtags", "score", "#fyp,#foryou,#fitness,#gym", "--platform", "tiktok")
        assert code == 0
        assert "score" in data
        assert "grade" in data
        assert isinstance(data["score"], int)

    def test_score_platform_youtube(self):
        code, data = run_cli_json("hashtags", "score", "#tech,#tutorial,#howto", "--platform", "youtube")
        assert code == 0
        assert "score" in data

    def test_build_exits_zero(self):
        code, out, _ = run_cli("hashtags", "build", "--niche", "fitness")
        assert code == 0

    def test_build_json_has_copy_paste(self):
        code, data = run_cli_json("hashtags", "build", "--niche", "beauty", "--platform", "tiktok")
        assert code == 0
        assert "copy_paste" in data
        assert "#" in data["copy_paste"]

    def test_suggest_exits_zero(self):
        code, out, _ = run_cli("hashtags", "suggest", "My morning workout routine for building muscle")
        assert code == 0

    def test_suggest_json(self):
        code, data = run_cli_json("hashtags", "suggest", "Great recipe for pasta", "--niche", "food")
        assert code == 0
        assert "suggested_hashtags" in data
        assert "copy_paste" in data


# ─────────────────────────────────────────────────────────────────────
# Account CLI
# ─────────────────────────────────────────────────────────────────────

class TestAccountCLI:
    def test_score_exits_zero(self):
        code, out, _ = run_cli(
            "account", "score",
            "--platform", "tiktok",
            "--username", "testuser",
            "--bio", "Daily fitness tips. Link below 👇",
            "--has-photo",
            "--has-link",
            "--followers", "5000",
            "--posts", "30",
        )
        assert code == 0

    def test_score_json_has_grade(self):
        code, data = run_cli_json(
            "account", "score",
            "--platform", "tiktok",
            "--username", "mypage",
            "--display-name", "Fitness Tips | Jake",
            "--bio", "I help people get fit. Free plan in bio ↓",
            "--has-photo",
            "--has-link",
            "--followers", "10000",
            "--posts", "50",
            "--niche", "fitness",
        )
        assert code == 0
        assert "score" in data
        assert "grade" in data
        assert "recommendations" in data

    def test_score_empty_bio_has_critical(self):
        code, data = run_cli_json(
            "account", "score",
            "--platform", "instagram",
            "--username", "emptyprofile",
            "--bio", "",
        )
        assert code == 0
        critical = [r for r in data.get("recommendations", []) if r["priority"] == "critical"]
        assert len(critical) > 0

    def test_schedule_tiktok(self):
        code, out, _ = run_cli("account", "schedule", "--platform", "tiktok", "--tz-offset", "-5")
        assert code == 0

    def test_schedule_json(self):
        code, data = run_cli_json("account", "schedule", "--platform", "youtube", "--tz-offset", "0")
        assert code == 0
        assert "best_times_local" in data
        assert "frequency" in data

    def test_optimize_all_exits_zero(self):
        code, out, _ = run_cli(
            "account", "optimize-all",
            "--platform", "tiktok",
            "--username", "fitnesspage",
            "--niche", "fitness",
            "--tz-offset", "-5",
        )
        assert code == 0

    def test_optimize_all_json(self):
        code, data = run_cli_json(
            "account", "optimize-all",
            "--platform", "instagram",
            "--username", "beautypage",
            "--niche", "beauty",
        )
        assert code == 0
        assert "posting_schedule" in data
        assert "recommended_hashtags" in data
        assert "content_ideas" in data


# ─────────────────────────────────────────────────────────────────────
# Theme Page CLI
# ─────────────────────────────────────────────────────────────────────

class TestThemePageCLI:
    def test_niches_exits_zero(self):
        code, out, _ = run_cli("theme-page", "niches")
        assert code == 0

    def test_niches_json(self):
        code, data = run_cli_json("theme-page", "niches")
        assert code == 0
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_niche_detail(self):
        code, out, _ = run_cli("theme-page", "niche-detail", "fitness_health")
        assert code == 0

    def test_niche_detail_json(self):
        code, data = run_cli_json("theme-page", "niche-detail", "luxury_lifestyle")
        assert code == 0
        assert "monetization" in data
        assert "difficulty" in data

    def test_roadmap_exits_zero(self):
        code, out, _ = run_cli("theme-page", "roadmap", "--niche", "fitness_health")
        assert code == 0

    def test_roadmap_json_has_milestones(self):
        code, data = run_cli_json("theme-page", "roadmap", "--niche", "motivation_mindset", "--followers", "0")
        assert code == 0
        assert "all_milestones" in data
        assert len(data["all_milestones"]) == 4
        assert "current_phase" in data

    def test_roadmap_phase_progression(self):
        code0, d0 = run_cli_json("theme-page", "roadmap", "--niche", "beauty_skincare", "--followers", "500")
        code1, d1 = run_cli_json("theme-page", "roadmap", "--niche", "beauty_skincare", "--followers", "50000")
        assert d0["current_phase"] < d1["current_phase"]

    def test_monetization_exits_zero(self):
        code, out, _ = run_cli("theme-page", "monetization")
        assert code == 0

    def test_monetization_specific_method(self):
        code, data = run_cli_json("theme-page", "monetization", "--method", "affiliate")
        assert code == 0
        assert "how_to_get" in data

    def test_conversion_tips_tiktok(self):
        code, data = run_cli_json("theme-page", "conversion-tips", "--platform", "tiktok")
        assert code == 0
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_full_guide_exits_zero(self):
        code, out, _ = run_cli(
            "theme-page", "full-guide",
            "--niche", "fitness_health",
            "--platform", "tiktok",
            "--followers", "1000",
        )
        assert code == 0

    def test_full_guide_json(self):
        code, data = run_cli_json(
            "theme-page", "full-guide",
            "--niche", "cooking_food",
            "--platform", "instagram",
        )
        assert code == 0
        assert "monetization_options" in data
        assert "conversion_tips" in data
        assert "immediate_actions" in data


# ─────────────────────────────────────────────────────────────────────
# Trends aggregation (no YouTube API key — partial results expected)
# ─────────────────────────────────────────────────────────────────────

class TestTrendsAggregation:
    def test_aggregate_tiktok_only(self):
        code, data = run_cli_json("trends", "aggregate", "--platform", "tiktok", "--niche", "fitness")
        assert code == 0
        assert "tiktok_hashtags" in data
        assert "recommended_caption_hashtags" in data

    def test_aggregate_has_timestamp(self):
        code, data = run_cli_json("trends", "aggregate", "--platform", "tiktok")
        assert code == 0
        assert "timestamp" in data

    def test_content_ideas_exits_zero(self):
        code, out, _ = run_cli("trends", "content-ideas", "--niche", "fitness")
        assert code == 0

    def test_content_ideas_json(self):
        code, data = run_cli_json("trends", "content-ideas", "--niche", "beauty", "--count", "5")
        assert code == 0
        assert isinstance(data, list)
        assert len(data) <= 5
        for idea in data:
            assert "format" in idea
            assert "hook" in idea
