"""End-to-end tests for social-trends CLI.

TikTok unofficial scraper tests run without credentials.
YouTube tests require YOUTUBE_API_KEY env var.
TikTok official API tests require TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET.

Run with:
  pytest social-trends/agent-harness/ -v
  pytest social-trends/agent-harness/ -v -k e2e_yt --only-youtube
"""

import json
import os
import subprocess
import sys
import unittest


def _run_cli(*args) -> tuple[int, str, str]:
    cmd = [sys.executable, "-m", "cli_anything.social_trends", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return proc.returncode, proc.stdout, proc.stderr


def _run_cli_json(*args) -> tuple[int, dict]:
    rc, stdout, stderr = _run_cli("--json", *args)
    try:
        return rc, json.loads(stdout)
    except json.JSONDecodeError:
        return rc, {"_parse_error": stdout, "_stderr": stderr}


class TestCLIStructure(unittest.TestCase):
    """Verify CLI entrypoints are wired without hitting real APIs."""

    def test_help_exits_zero(self):
        rc, stdout, _ = _run_cli("--help")
        self.assertEqual(rc, 0)
        self.assertIn("social-trends", stdout)

    def test_tt_help(self):
        rc, stdout, _ = _run_cli("tt", "--help")
        self.assertEqual(rc, 0)
        self.assertIn("trends", stdout)

    def test_yt_help(self):
        rc, stdout, _ = _run_cli("yt", "--help")
        self.assertEqual(rc, 0)

    def test_optimize_help(self):
        rc, stdout, _ = _run_cli("optimize", "--help")
        self.assertEqual(rc, 0)

    def test_theme_help(self):
        rc, stdout, _ = _run_cli("theme", "--help")
        self.assertEqual(rc, 0)


class TestThemePageCLI(unittest.TestCase):
    """Theme page commands need no API keys — always runnable."""

    def test_theme_niches_json(self):
        rc, data = _run_cli_json("theme", "niches")
        self.assertEqual(rc, 0)
        self.assertIn("niches", data)
        self.assertGreater(len(data["niches"]), 0)

    def test_theme_growth_json(self):
        rc, data = _run_cli_json("theme", "growth")
        self.assertEqual(rc, 0)
        self.assertIn("growth_playbook", data)
        phases = data["growth_playbook"]
        self.assertGreaterEqual(len(phases), 4)

    def test_theme_monetize_json(self):
        rc, data = _run_cli_json("theme", "monetize")
        self.assertEqual(rc, 0)
        self.assertIn("monetization_methods", data)

    def test_theme_content_sources_json(self):
        rc, data = _run_cli_json("theme", "content-sources")
        self.assertEqual(rc, 0)
        self.assertIn("content_sources", data)

    def test_theme_playbook_json(self):
        rc, data = _run_cli_json("theme", "playbook")
        self.assertEqual(rc, 0)
        for key in ("niches", "growth_playbook", "monetization_methods", "content_sourcing"):
            self.assertIn(key, data)

    def test_theme_niches_keyword_filter(self):
        rc, data = _run_cli_json("theme", "niches", "--keyword", "fitness")
        self.assertEqual(rc, 0)
        self.assertIn("niches", data)


class TestOptimizerCLI(unittest.TestCase):
    """Optimizer commands that don't require scraping APIs."""

    def test_posting_times_tiktok(self):
        rc, data = _run_cli_json("optimize", "posting-times", "tiktok")
        self.assertEqual(rc, 0)
        self.assertEqual(data["platform"], "tiktok")
        self.assertIn("best_hours_utc", data)

    def test_posting_times_youtube(self):
        rc, data = _run_cli_json("optimize", "posting-times", "youtube")
        self.assertEqual(rc, 0)
        self.assertEqual(data["platform"], "youtube")

    def test_checklist_all_platforms(self):
        for p in ["tiktok", "youtube", "instagram"]:
            rc, data = _run_cli_json("optimize", "checklist", p)
            self.assertEqual(rc, 0, f"checklist failed for {p}")
            self.assertIn("checklist", data)
            self.assertGreater(len(data["checklist"]), 0)

    def test_caption_hooks_json(self):
        rc, data = _run_cli_json("optimize", "caption-hooks", "workout")
        self.assertEqual(rc, 0)
        self.assertIn("hooks", data)
        self.assertEqual(len(data["hooks"]), 5)
        for hook in data["hooks"]:
            self.assertIn("workout", hook)


@unittest.skipUnless(
    os.environ.get("YOUTUBE_API_KEY"),
    "YOUTUBE_API_KEY not set — skipping live YouTube tests",
)
class TestYouTubeLiveE2E(unittest.TestCase):
    def test_yt_trends_live(self):
        rc, data = _run_cli_json("yt", "trends", "--region", "US", "--count", "5")
        self.assertEqual(rc, 0)
        self.assertIn("youtube_trending_videos", data)
        self.assertGreater(len(data["youtube_trending_videos"]), 0)

    def test_yt_music_live(self):
        rc, data = _run_cli_json("yt", "music", "--region", "US", "--count", "5")
        self.assertEqual(rc, 0)
        self.assertIn("youtube_trending_music", data)

    def test_yt_hashtags_live(self):
        rc, data = _run_cli_json("yt", "hashtags", "--region", "US")
        self.assertEqual(rc, 0)
        self.assertIn("youtube_top_hashtags", data)

    def test_yt_search_live(self):
        rc, data = _run_cli_json("yt", "search", "fitness motivation")
        self.assertEqual(rc, 0)
        self.assertIn("youtube_search_results", data)


@unittest.skipUnless(
    os.environ.get("TIKTOK_E2E", ""),
    "TIKTOK_E2E not set — set to 1 to enable live TikTok scraper tests (unofficial)",
)
class TestTikTokLiveE2E(unittest.TestCase):
    """These hit TikTok's public endpoints — may be rate-limited."""

    def test_tt_hashtags_live(self):
        rc, data = _run_cli_json("tt", "hashtags", "--count", "10")
        self.assertEqual(rc, 0)
        self.assertIn("tiktok_trending_hashtags", data)

    def test_tt_sounds_live(self):
        rc, data = _run_cli_json("tt", "sounds", "--count", "10")
        self.assertEqual(rc, 0)
        self.assertIn("tiktok_trending_sounds", data)

    def test_tt_trends_live(self):
        rc, data = _run_cli_json("tt", "trends", "--count", "10")
        self.assertEqual(rc, 0)
        self.assertIn("tiktok_trending_videos", data)

    def test_all_trends_no_yt(self):
        rc, data = _run_cli_json("all-trends", "--no-yt")
        self.assertEqual(rc, 0)
        self.assertIn("tiktok", data)


if __name__ == "__main__":
    unittest.main()
