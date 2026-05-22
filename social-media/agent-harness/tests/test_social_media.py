"""Tests for social media CLI harness — no network required."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from click.testing import CliRunner
from cli_anything.social_media.social_media_cli import cli
from cli_anything.social_media.core import account_optimizer as opt
from cli_anything.social_media.core import theme_page_guide as tpg
from cli_anything.social_media.core import cache as _cache


# ============================================================================
# Account optimizer tests (no network)
# ============================================================================

def test_optimize_profile_returns_expected_keys():
    result = opt.optimize_profile(platform="tiktok", niche="fitness")
    assert result["platform"] == "tiktok"
    assert result["niche"] == "fitness"
    assert "bio_formula" in result
    assert "profile_tips" in result
    assert len(result["profile_tips"]) > 0


def test_optimize_profile_instagram():
    result = opt.optimize_profile(platform="instagram", niche="fashion")
    assert result["bio_max_chars"] == 150
    assert "instagram" in result["bio_formula"].lower() or result["platform"] == "instagram"


def test_best_posting_times_tiktok():
    result = opt.best_posting_times(platform="tiktok", timezone="EST")
    assert result["platform"] == "tiktok"
    assert len(result["posting_windows"]) > 0
    assert "best_days" in result
    assert "worst_days" in result


def test_best_posting_times_youtube():
    result = opt.best_posting_times(platform="youtube", timezone="PST")
    assert result["timezone"] == "PST"


def test_generate_hashtag_set_structure():
    result = opt.generate_hashtag_set(niche="fitness", platform="tiktok", count=20,
                                      use_cache=False)
    assert result["platform"] == "tiktok"
    assert result["niche"] == "fitness"
    assert isinstance(result["hashtags"], list)
    assert len(result["hashtags"]) > 0
    # All should start with #
    for tag in result["hashtags"]:
        assert tag.startswith("#"), f"Tag {tag!r} doesn't start with #"


def test_hashtag_set_has_rotation_strategy():
    result = opt.generate_hashtag_set(niche="finance", platform="instagram", count=25,
                                      use_cache=False)
    assert "rotation_strategy" in result
    assert "keep_always" in result["rotation_strategy"]


def test_content_strategy_structure():
    result = opt.optimize_content_strategy(niche="luxury", platform="tiktok",
                                            posts_per_week=5, use_cache=False)
    assert result["posts_per_week"] == 5
    assert len(result["content_pillars"]) >= 4
    assert len(result["weekly_calendar"]) == 5
    for day in result["weekly_calendar"]:
        assert "posting_window" in day
        assert "content_pillar" in day


# ============================================================================
# Theme page guide tests (no network)
# ============================================================================

def test_evaluate_niche_luxury():
    result = tpg.evaluate_niche("luxury")
    assert "evaluation" in result
    assert "monetization_potential" in result["evaluation"]
    assert result["niche"] == "luxury"
    assert len(result["best_platforms"]) > 0


def test_evaluate_unknown_niche():
    result = tpg.evaluate_niche("underwater basket weaving")
    assert result["niche"] == "underwater basket weaving"
    assert "evaluation" in result


def test_playbook_has_4_phases():
    result = tpg.get_theme_page_playbook("fitness")
    assert len(result["phases"]) == 4
    for phase in result["phases"]:
        assert "name" in phase
        assert "tasks" in phase
        assert len(phase["tasks"]) > 0


def test_playbook_monetization_roadmap():
    result = tpg.get_theme_page_playbook("finance")
    assert len(result["monetization_roadmap"]) > 0
    for m in result["monetization_roadmap"]:
        assert "method" in m
        assert "potential" in m


def test_monetization_strategies_all_have_setup():
    result = tpg.monetization_strategies("fitness")
    for s in result["strategies"]:
        assert "setup_steps" in s
        assert len(s["setup_steps"]) > 0
    assert len(result["quick_wins"]) >= 1


def test_sub_niche_ideas_fitness():
    result = tpg.evaluate_niche("fitness")
    assert "sub_niche_ideas" in result
    assert len(result["sub_niche_ideas"]) > 0


# ============================================================================
# Cache tests (local filesystem)
# ============================================================================

def test_cache_set_and_get():
    _cache.set("test_key_unit", {"foo": "bar"})
    val = _cache.get("test_key_unit")
    assert val == {"foo": "bar"}


def test_cache_miss_returns_none():
    val = _cache.get("nonexistent_key_xyz_123456")
    assert val is None


def test_cache_clear():
    _cache.set("test_clear_key", {"data": 1})
    result = _cache.clear("test_clear_key")
    assert result["deleted"] == 1
    assert _cache.get("test_clear_key") is None


def test_cache_info():
    _cache.set("test_info_key", {"x": 1})
    result = _cache.info()
    assert "entries" in result
    assert result["entries"] >= 1


# ============================================================================
# CLI integration tests
# ============================================================================

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "trends" in result.output.lower()
    assert "optimize" in result.output.lower()


def test_cli_trends_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["trends", "--help"])
    assert result.exit_code == 0
    assert "youtube" in result.output.lower()
    assert "tiktok" in result.output.lower()


def test_cli_optimize_profile_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "optimize", "profile",
        "--platform", "tiktok", "--niche", "fitness"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["platform"] == "tiktok"
    assert data["niche"] == "fitness"


def test_cli_optimize_schedule_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "optimize", "schedule",
        "--platform", "instagram", "--timezone", "PST"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["platform"] == "instagram"
    assert data["timezone"] == "PST"


def test_cli_theme_page_evaluate_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "theme-page", "evaluate", "--niche", "luxury"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["niche"] == "luxury"
    assert "evaluation" in data


def test_cli_theme_page_playbook_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "theme-page", "playbook", "--niche", "finance", "--followers", "500"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data["phases"]) == 4


def test_cli_theme_page_convert_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "theme-page", "convert",
        "--from-type", "personal", "--niche", "fitness", "--platform", "tiktok"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "immediate_steps" in data
    assert "week_1_plan" in data


def test_cli_optimize_hashtags_json_no_network():
    """Hashtag generation should work even without network (uses curated tags)."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "optimize", "hashtags",
        "--niche", "fitness", "--platform", "tiktok", "--count", "15", "--no-cache"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data["hashtags"], list)
    assert len(data["hashtags"]) > 0


def test_cli_cache_info_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["--json", "cache", "info"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "entries" in data


def test_cli_theme_page_monetize_json():
    runner = CliRunner()
    result = runner.invoke(cli, [
        "--json", "theme-page", "monetize", "--niche", "finance"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "strategies" in data
    assert len(data["strategies"]) > 0
    assert "quick_wins" in data
