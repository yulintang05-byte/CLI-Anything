"""End-to-end CLI tests — all commands that don't require API keys."""

import json
import pytest
from click.testing import CliRunner

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_intel.social_intel_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ── auth ─────────────────────────────────────────────────────────

def test_auth_status(runner):
    r = runner.invoke(cli, ["auth", "status"])
    assert r.exit_code == 0
    assert "youtube" in r.output.lower() or "key" in r.output.lower()


def test_auth_status_json(runner):
    r = runner.invoke(cli, ["--json", "auth", "status"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "youtube_key_set" in data
    assert "tiktok_key_set" in data


def test_auth_setup(runner, tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    r = runner.invoke(cli, [
        "auth", "setup",
        "--youtube-api-key", "TESTKEY123",
    ])
    assert r.exit_code == 0


# ── optimize ─────────────────────────────────────────────────────

def test_optimize_tiktok(runner):
    r = runner.invoke(cli, ["optimize", "--platform", "tiktok"])
    assert r.exit_code == 0
    assert "tiktok" in r.output.lower()


def test_optimize_tiktok_json(runner):
    r = runner.invoke(cli, ["--json", "optimize", "--platform", "tiktok", "--niche", "fitness"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["platform"] == "tiktok"
    assert data["niche"] == "fitness"
    assert "hook_formulas" in data
    assert "hashtag_strategy" in data


def test_optimize_youtube(runner):
    r = runner.invoke(cli, ["optimize", "--platform", "youtube"])
    assert r.exit_code == 0


def test_optimize_youtube_shorts_json(runner):
    r = runner.invoke(cli, ["--json", "optimize", "--platform", "youtube_shorts"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "youtube" in data["platform"]


def test_optimize_instagram_reels_json(runner):
    r = runner.invoke(cli, ["--json", "optimize", "--platform", "instagram_reels"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "instagram" in data["platform"]


# ── theme ─────────────────────────────────────────────────────────

def test_theme_niches(runner):
    r = runner.invoke(cli, ["theme", "niches"])
    assert r.exit_code == 0
    assert "fitness" in r.output.lower()


def test_theme_niches_json(runner):
    r = runner.invoke(cli, ["--json", "theme", "niches"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "niches" in data
    assert len(data["niches"]) >= 5


def test_theme_niche_fitness(runner):
    r = runner.invoke(cli, ["theme", "niche", "fitness"])
    assert r.exit_code == 0


def test_theme_niche_fitness_json(runner):
    r = runner.invoke(cli, ["--json", "theme", "niche", "fitness"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["niche"] == "fitness"
    assert "scores" in data
    assert "affiliate_programs" in data


def test_theme_niche_unknown(runner):
    r = runner.invoke(cli, ["--json", "theme", "niche", "unicorn_tears"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "error" in data


def test_theme_roadmap_small(runner):
    r = runner.invoke(cli, ["--json", "theme", "roadmap", "--followers", "500"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["tier"] == "0–1K"
    assert "monetization" in data
    assert "next_tier_preview" in data


def test_theme_roadmap_large(runner):
    r = runner.invoke(cli, ["--json", "theme", "roadmap", "--followers", "500000"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["tier"] == "100K+"


def test_theme_funnel(runner):
    r = runner.invoke(cli, ["theme", "funnel"])
    assert r.exit_code == 0
    assert "awareness" in r.output.lower()


def test_theme_funnel_json(runner):
    r = runner.invoke(cli, ["--json", "theme", "funnel"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "funnel" in data
    assert "awareness" in data["funnel"]
    assert "retention" in data["funnel"]


def test_theme_curation(runner):
    r = runner.invoke(cli, ["theme", "curation"])
    assert r.exit_code == 0
    assert "legal" in r.output.lower()


def test_theme_curation_json(runner):
    r = runner.invoke(cli, ["--json", "theme", "curation"])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert "legal_guidelines" in data
    assert "tools" in data


def test_theme_calendar(runner):
    r = runner.invoke(cli, [
        "theme", "calendar",
        "--niche", "fitness",
        "--platform", "tiktok",
        "--posts-per-week", "7",
    ])
    assert r.exit_code == 0


def test_theme_calendar_json(runner):
    r = runner.invoke(cli, [
        "--json", "theme", "calendar",
        "--niche", "cars",
        "--platform", "instagram",
        "--posts-per-week", "7",
    ])
    assert r.exit_code == 0
    data = json.loads(r.output)
    assert data["niche"] == "cars"
    assert len(data["week_calendar"]) == 7
    assert "reminders" in data


def test_help(runner):
    r = runner.invoke(cli, ["--help"])
    assert r.exit_code == 0
    assert "youtube" in r.output.lower()
    assert "tiktok" in r.output.lower()
    assert "optimize" in r.output.lower()
    assert "theme" in r.output.lower()
