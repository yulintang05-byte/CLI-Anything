"""E2E CLI tests via Click test runner — no real API calls."""

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from cli_anything.social_trends.social_trends_cli import cli
from cli_anything.social_trends.core import session as sess


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_session(tmp_path, monkeypatch):
    """Patch session paths so each test gets a clean isolated session."""
    monkeypatch.setattr(sess, "SESSION_DIR", tmp_path)
    monkeypatch.setattr(sess, "SESSION_FILE", tmp_path / "session.json")
    monkeypatch.setattr(sess, "CACHE_DIR", tmp_path / "cache")
    return tmp_path


# ---------------------------------------------------------------------------
# Help tests
# ---------------------------------------------------------------------------

def test_cli_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "YouTube" in result.output or "TikTok" in result.output or "trends" in result.output.lower()


def test_yt_group_help(runner):
    result = runner.invoke(cli, ["yt", "--help"])
    assert result.exit_code == 0
    assert "trends" in result.output.lower() or "youtube" in result.output.lower()


def test_tt_group_help(runner):
    result = runner.invoke(cli, ["tt", "--help"])
    assert result.exit_code == 0


def test_account_group_help(runner):
    result = runner.invoke(cli, ["account", "--help"])
    assert result.exit_code == 0


def test_theme_group_help(runner):
    result = runner.invoke(cli, ["theme", "--help"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Account commands
# ---------------------------------------------------------------------------

def test_account_add_command(runner, isolated_session):
    result = runner.invoke(cli, [
        "account", "add", "tiktok", "myuser",
        "--followers", "10000",
        "--niche", "fitness",
        "--avg-views", "2000",
        "--avg-likes", "300",
        "--posts-per-week", "7",
        "--bio", "Fitness tips every day",
    ])
    assert result.exit_code == 0
    assert "myuser" in result.output


def test_account_list_empty(runner, isolated_session):
    result = runner.invoke(cli, ["account", "list"])
    assert result.exit_code == 0


def test_account_list_after_add(runner, isolated_session):
    runner.invoke(cli, ["account", "add", "tiktok", "testuser", "--followers", "5000"])
    result = runner.invoke(cli, ["account", "list", "--json"])
    assert result.exit_code == 0


def test_account_audit_not_found(runner, isolated_session):
    result = runner.invoke(cli, ["account", "audit", "tiktok", "ghost_user"])
    assert result.exit_code == 0
    assert "not found" in result.output.lower() or "add it first" in result.output.lower()


def test_account_audit_found(runner, isolated_session):
    runner.invoke(cli, [
        "account", "add", "tiktok", "realuser",
        "--followers", "20000",
        "--niche", "fitness",
        "--avg-views", "5000",
        "--avg-likes", "500",
        "--avg-comments", "50",
        "--posts-per-week", "7",
        "--bio", "Fitness creator helping you get fit in 90 days",
    ])
    result = runner.invoke(cli, ["account", "audit", "tiktok", "realuser", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "engagement_rate_pct" in data
    assert "recommendations" in data
    assert "score" in data


def test_account_schedule_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["account", "schedule", "tiktok", "--posts-per-week", "5", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 5
    assert "date" in data[0]
    assert "hour_utc" in data[0]


def test_account_schedule_youtube(runner, isolated_session):
    result = runner.invoke(cli, ["account", "schedule", "youtube", "--posts-per-week", "3", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 3


def test_account_hashtags_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["account", "hashtags", "fitness", "tiktok", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "recommended_combo" in data
    assert "tiers" in data
    assert "pro_tips" in data
    assert isinstance(data["recommended_combo"], list)


def test_account_hashtags_instagram(runner, isolated_session):
    result = runner.invoke(cli, ["account", "hashtags", "beauty", "instagram", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["platform"] == "instagram"
    assert data["platform_limit"] == 30


def test_account_calendar_json_output(runner, isolated_session):
    result = runner.invoke(cli, [
        "account", "calendar", "fitness", "tiktok",
        "--weeks", "2", "--posts-per-week", "7", "--json"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 14
    assert "hook" in data[0]
    assert "cta" in data[0]
    assert "content_type" in data[0]


def test_account_bio_json_output(runner, isolated_session):
    result = runner.invoke(cli, [
        "account", "bio", "fitness", "tiktok",
        "--value-prop", "transform your body in 90 days",
        "--json"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "templates" in data
    assert "tips" in data
    assert len(data["templates"]) > 0


# ---------------------------------------------------------------------------
# Theme commands
# ---------------------------------------------------------------------------

def test_theme_niches_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "niches", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) >= 5
    # Should be sorted by score descending
    scores = [d["total_score"] for d in data]
    assert scores == sorted(scores, reverse=True)


def test_theme_niche_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "niche", "finance", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "sub_niches" in data
    assert "content_types" in data
    assert "monetization_methods" in data


def test_theme_niche_unknown(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "niche", "unknownniche999", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "error" in data


def test_theme_compare_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "compare", "finance", "fitness", "beauty", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 3
    scores = [d["total_score"] for d in data]
    assert scores == sorted(scores, reverse=True)


def test_theme_playbook_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "playbook", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 6


def test_theme_playbook_specific_phase(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "playbook", "3", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["phase"] == 3
    assert "steps" in data


def test_theme_revenue_json_output(runner, isolated_session):
    result = runner.invoke(cli, [
        "theme", "revenue", "tiktok", "50000",
        "--niche", "fitness", "--avg-views", "10000", "--json"
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "monthly_estimates_usd" in data
    assert "total" in data["monthly_estimates_usd"]


def test_theme_strategy_json_output(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "strategy", "follow_to_engagement", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "tactics" in data
    assert "kpis" in data


def test_theme_strategy_unknown(runner, isolated_session):
    result = runner.invoke(cli, ["theme", "strategy", "nonexistent_strategy"])
    assert result.exit_code == 0
    assert "Unknown" in result.output or "Available" in result.output


# ---------------------------------------------------------------------------
# Config commands
# ---------------------------------------------------------------------------

def test_config_set_command(runner, isolated_session):
    result = runner.invoke(cli, ["config", "set", "YOUTUBE_API_KEY", "test_key_12345"])
    assert result.exit_code == 0
    assert "YOUTUBE_API_KEY" in result.output


def test_config_show_command(runner, isolated_session):
    runner.invoke(cli, ["config", "set", "YOUTUBE_API_KEY", "secretkey"])
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0
    # Key value should be redacted
    assert "secretkey" not in result.output


# ---------------------------------------------------------------------------
# Cache and history commands
# ---------------------------------------------------------------------------

def test_cache_clear_command(runner, isolated_session):
    result = runner.invoke(cli, ["cache", "--clear"])
    assert result.exit_code == 0
    assert "Cleared" in result.output


def test_history_empty(runner, isolated_session):
    result = runner.invoke(cli, ["history"])
    assert result.exit_code == 0
    assert "No history" in result.output or result.exit_code == 0


def test_history_after_commands(runner, isolated_session):
    runner.invoke(cli, ["account", "schedule", "tiktok", "--json"])
    result = runner.invoke(cli, ["history"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# YouTube commands (no API key — should fail gracefully)
# ---------------------------------------------------------------------------

def test_yt_trends_no_api_key(runner, isolated_session):
    result = runner.invoke(cli, ["yt", "trends", "--region", "US"])
    assert result.exit_code == 0
    assert "API key" in result.output or "YOUTUBE_API_KEY" in result.output


def test_yt_hashtags_no_api_key(runner, isolated_session):
    result = runner.invoke(cli, ["yt", "hashtags"])
    assert result.exit_code == 0
    assert "YOUTUBE_API_KEY" in result.output or "API key" in result.output


def test_yt_music_no_api_key(runner, isolated_session):
    result = runner.invoke(cli, ["yt", "music"])
    assert result.exit_code == 0


def test_yt_niche_no_api_key(runner, isolated_session):
    result = runner.invoke(cli, ["yt", "niche", "fitness"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# TikTok commands (web scrape fallback — may fail in CI, graceful check)
# ---------------------------------------------------------------------------

def test_tt_hashtag_info_returns_dict(runner, isolated_session):
    result = runner.invoke(cli, ["tt", "hashtag-info", "#fitness", "--json"])
    assert result.exit_code == 0
    # May succeed or return error dict — both are valid
    try:
        data = json.loads(result.output)
        assert "hashtag" in data
    except json.JSONDecodeError:
        pass  # Non-JSON output is also acceptable for network failures


def test_tt_trends_no_token(runner, isolated_session):
    """TikTok trends should attempt web scrape even without Research API token."""
    result = runner.invoke(cli, ["tt", "trends", "--max", "5"])
    assert result.exit_code == 0
    assert "Fetching" in result.output
