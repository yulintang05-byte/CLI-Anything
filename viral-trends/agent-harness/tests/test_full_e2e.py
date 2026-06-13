"""End-to-end tests for viral-trends CLI.

Tests the Click CLI commands via subprocess (when installed) and
via direct invocation using CliRunner.

Run with: pytest tests/test_full_e2e.py -v
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli_anything.viral_trends.viral_trends_cli import main
from cli_anything.viral_trends.core import (
    youtube_scraper,
    tiktok_scraper,
    account_optimizer,
)

SAMPLE_YT = [
    {
        "id": "abc1", "title": "Viral #dance #fyp",
        "channel": "Creator", "views": 3_000_000, "likes": 100_000,
        "duration": 30, "url": "https://youtu.be/abc1",
        "thumbnail": "", "hashtags": ["dance", "fyp"],
        "description": "Dance video", "platform": "youtube", "category": "all",
    }
]

SAMPLE_TT = [
    {"hashtag": "fyp",   "views": 50_000_000_000, "category": "general"},
    {"hashtag": "dance", "views": 8_000_000_000,  "category": "entertainment"},
]

SAMPLE_SOUNDS = [
    {"sound": "As It Was", "category": "pop"},
    {"sound": "Anti-Hero",  "category": "pop"},
]

runner = CliRunner()


# ── trends commands ───────────────────────────────────────────────────────────

class TestTrendsCommands:
    def test_trends_youtube_json(self):
        with patch.object(youtube_scraper, "get_trending", return_value=SAMPLE_YT):
            result = runner.invoke(main, ["--json", "trends", "youtube", "--limit", "1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert data[0]["platform"] == "youtube"

    def test_trends_youtube_human(self):
        with patch.object(youtube_scraper, "get_trending", return_value=SAMPLE_YT):
            result = runner.invoke(main, ["trends", "youtube"])
        assert result.exit_code == 0
        assert "YouTube" in result.output or "youtube" in result.output.lower()

    def test_trends_tiktok_json(self):
        with (
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
            patch.object(tiktok_scraper, "get_trending_sounds", return_value=SAMPLE_SOUNDS),
        ):
            result = runner.invoke(main, ["--json", "trends", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_hashtags" in data
        assert "trending_sounds" in data

    def test_trends_cross_json(self):
        with (
            patch.object(youtube_scraper, "get_trending", return_value=SAMPLE_YT),
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
            patch.object(tiktok_scraper, "get_trending_sounds",   return_value=SAMPLE_SOUNDS),
            patch.object(youtube_scraper, "get_trending_music_from_videos", return_value=[]),
        ):
            result = runner.invoke(main, ["--json", "trends", "cross"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube_trending" in data
        assert "tiktok_trending" in data


# ── hashtags commands ─────────────────────────────────────────────────────────

class TestHashtagsCommands:
    def test_hashtags_analyze_json(self):
        with (
            patch.object(youtube_scraper, "get_all_hashtags", return_value=[
                {"hashtag": "fyp", "frequency": 3, "total_views": 1_000_000}
            ]),
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
        ):
            result = runner.invoke(main, ["--json", "hashtags", "analyze"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_hashtags_build_json(self):
        with (
            patch.object(youtube_scraper, "get_all_hashtags", return_value=[
                {"hashtag": "fyp", "frequency": 5, "total_views": 5_000_000_000}
            ]),
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
        ):
            result = runner.invoke(main, ["--json", "hashtags", "build", "--niche", "dance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "optimal_set" in data
        assert "caption_block" in data

    def test_hashtags_build_caption_block_has_hashes(self):
        with (
            patch.object(youtube_scraper, "get_all_hashtags", return_value=[
                {"hashtag": "fyp", "frequency": 5, "total_views": 5_000_000_000}
            ]),
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
        ):
            result = runner.invoke(main, ["--json", "hashtags", "build"])
        data = json.loads(result.output)
        assert "#" in data["caption_block"]

    def test_hashtags_filter_json(self):
        with patch.object(tiktok_scraper, "get_trending_hashtags", return_value=[
            {"hashtag": "gymtok", "views": 4_000_000_000, "category": "fitness"}
        ]):
            result = runner.invoke(main, ["--json", "hashtags", "filter", "fitness"])
        assert result.exit_code == 0


# ── music commands ────────────────────────────────────────────────────────────

class TestMusicCommands:
    def test_music_guide_json(self):
        result = runner.invoke(main, ["--json", "music", "guide"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tips" in data
        assert "workflow" in data

    def test_music_trending_json(self):
        with (
            patch.object(tiktok_scraper, "get_trending_sounds",
                         return_value=SAMPLE_SOUNDS),
            patch.object(youtube_scraper, "get_trending_music_from_videos",
                         return_value=[]),
        ):
            result = runner.invoke(main, ["--json", "music", "trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok_sounds" in data


# ── account commands ──────────────────────────────────────────────────────────

class TestAccountCommands:
    def test_account_add_and_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(account_optimizer, "CONFIG_DIR", tmp_path)

        result = runner.invoke(main, [
            "--json", "account", "add", "fitnessguru",
            "--platform", "tiktok",
            "--niche", "fitness",
            "--followers", "5000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["handle"] == "fitnessguru"

        result2 = runner.invoke(main, ["--json", "account", "list"])
        assert result2.exit_code == 0
        accounts = json.loads(result2.output)
        assert any(a["handle"] == "fitnessguru" for a in accounts)

    def test_account_analyze(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(account_optimizer, "CONFIG_DIR", tmp_path)
        account_optimizer.add_account("testcreator", "tiktok", "food", 15_000, avg_views=2000)

        result = runner.invoke(main, [
            "--json", "account", "analyze", "testcreator", "--platform", "tiktok"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "engagement_rate" in data
        assert "priority_actions" in data

    def test_account_schedule_json(self):
        result = runner.invoke(main, ["--json", "account", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "best_days" in data

    def test_account_bio_brand(self):
        result = runner.invoke(main, [
            "--json", "account", "bio",
            "--template", "brand",
            "--niche", "fitness",
            "--frequency", "daily",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bio" in data
        assert "fitness" in data["bio"]

    def test_account_playbook_json(self):
        result = runner.invoke(main, ["--json", "account", "playbook", "--stage", "0_1k"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "actions" in data

    def test_account_remove(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(account_optimizer, "CONFIG_DIR", tmp_path)
        account_optimizer.add_account("toremove", "instagram", "beauty", 1000)
        result = runner.invoke(main, ["account", "remove", "toremove", "--platform", "instagram"])
        assert result.exit_code == 0

    def test_account_caption_json(self):
        with (
            patch.object(tiktok_scraper, "get_trending_hashtags", return_value=SAMPLE_TT),
            patch.object(youtube_scraper, "get_all_hashtags", return_value=[
                {"hashtag": "fyp", "frequency": 3, "total_views": 1_000_000}
            ]),
        ):
            result = runner.invoke(main, [
                "--json", "account", "caption",
                "--topic", "fitness tips",
                "--hook", "You need to see this",
                "--body", "Here are 5 fitness tips",
            ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "caption" in data
        assert "hashtags" in data


# ── theme-page commands ───────────────────────────────────────────────────────

class TestThemePageCommands:
    def test_theme_page_guide_json(self):
        result = runner.invoke(main, ["--json", "theme-page", "guide"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "what_is_a_theme_page" in data

    def test_theme_page_guide_section(self):
        result = runner.invoke(main, ["--json", "theme-page", "guide", "--section", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "highest_monetization" in data

    def test_theme_page_guide_invalid_section(self):
        result = runner.invoke(main, ["theme-page", "guide", "--section", "bad_section"])
        assert result.exit_code != 0 or "not found" in result.output.lower() or "error" in result.output.lower()

    def test_theme_page_niches_json(self):
        result = runner.invoke(main, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "highest_monetization" in data
        assert "easiest_to_grow" in data

    def test_theme_page_convert_json(self):
        result = runner.invoke(main, ["--json", "theme-page", "convert"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "conversion_steps" in data

    def test_theme_page_acquire_json(self):
        result = runner.invoke(main, ["--json", "theme-page", "acquire"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "where_to_find" in data
        assert "due_diligence" in data

    def test_theme_page_sections_json(self):
        result = runner.invoke(main, ["--json", "theme-page", "sections"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert "niches" in data


# ── config + history ──────────────────────────────────────────────────────────

class TestConfigAndHistory:
    def test_history_json(self, tmp_path, monkeypatch):
        from cli_anything.viral_trends.utils import state
        monkeypatch.setattr(state, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(state, "CONFIG_DIR", tmp_path)
        state.record_command("test cmd", "summary")
        result = runner.invoke(main, ["--json", "history"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_config_set_and_get(self, tmp_path, monkeypatch):
        from cli_anything.viral_trends.utils import state
        monkeypatch.setattr(state, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(state, "CONFIG_DIR", tmp_path)
        runner.invoke(main, ["config", "set", "my_key", "my_value"])
        result = runner.invoke(main, ["--json", "config", "get", "my_key"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["value"] == "my_value"


# ── CLI subprocess test (installed CLI) ───────────────────────────────────────

class TestCLIInstalled:
    """Tests that verify the installed 'viral-trends' command works."""

    def test_help_flag(self):
        env = os.environ.copy()
        env["CLI_ANYTHING_FORCE_INSTALLED"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.viral_trends", "--help"],
            capture_output=True, text=True, env=env,
        )
        assert result.returncode == 0
        assert "viral-trends" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_trends_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.viral_trends", "trends", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert "youtube" in result.stdout.lower() or "tiktok" in result.stdout.lower()

    def test_theme_page_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.viral_trends", "theme-page", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0

    def test_account_subcommand_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.viral_trends", "account", "--help"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
