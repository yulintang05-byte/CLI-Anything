"""Unit tests for social-trends core modules (no network required)."""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os


# ── Hashtags ──────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_generate_hashtag_set_structure(self):
        from cli_anything.social_trends.core.hashtags import generate_hashtag_set
        with patch("cli_anything.social_trends.core.hashtags._fetch_live_hashtags", return_value=[]):
            result = generate_hashtag_set("fitness", platform="tiktok", post_count=3)

        assert result["niche"] == "fitness"
        assert result["platform"] == "tiktok"
        assert len(result["sets"]) == 3

        for s in result["sets"]:
            assert "mega_tags" in s
            assert "niche_tags" in s
            assert "full_set" in s
            assert "copy_paste" in s
            assert all(t.startswith("#") for t in s["full_set"])

    def test_generate_hashtag_set_unknown_niche(self):
        from cli_anything.social_trends.core.hashtags import generate_hashtag_set
        with patch("cli_anything.social_trends.core.hashtags._fetch_live_hashtags", return_value=[]):
            result = generate_hashtag_set("unknownniche123", post_count=1)

        assert len(result["sets"]) == 1
        assert result["sets"][0]["niche_tags"]  # at least the niche itself

    def test_research_hashtags_with_seeds(self):
        from cli_anything.social_trends.core.hashtags import research_hashtags
        mock_live = [
            {"hashtag": "#fitness", "name": "fitness", "video_count": 1000, "source": "live_trending"}
        ]
        with patch("cli_anything.social_trends.core.hashtags._fetch_live_hashtags", return_value=mock_live):
            result = research_hashtags("fitness", limit=10)

        assert result["topic"] == "fitness"
        assert isinstance(result["hashtags"], list)
        assert len(result["hashtags"]) > 0

    def test_analyze_hashtag_not_in_trending(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag
        mock_response = {"data": {"list": []}}
        with patch("cli_anything.social_trends.core.hashtags.get", return_value=mock_response):
            result = analyze_hashtag("totallyrarehashtag123")

        assert result["found_in_trending"] is False
        assert "recommendation" in result

    def test_analyze_hashtag_found_in_trending(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag
        mock_response = {
            "data": {
                "list": [
                    {
                        "hashtag_name": "fitness",
                        "rank": 1,
                        "video_count": 50_000_000,
                        "view_count": 1_000_000_000,
                        "trend_score": 95,
                    }
                ]
            }
        }
        with patch("cli_anything.social_trends.core.hashtags.get", return_value=mock_response):
            result = analyze_hashtag("fitness")

        assert result["found_in_trending"] is True
        assert result["rank"] == 1
        assert "competition_level" in result
        assert "recommendation" in result

    def test_hashtag_recommendation_by_count(self):
        from cli_anything.social_trends.core.hashtags import _hashtag_recommendation
        assert "saturated" in _hashtag_recommendation(2_000_000_000).lower()
        assert "high competition" in _hashtag_recommendation(200_000_000).lower()
        assert "mid-range" in _hashtag_recommendation(50_000_000).lower()
        assert "niche" in _hashtag_recommendation(5_000_000).lower()
        assert "micro" in _hashtag_recommendation(500_000).lower()

    def test_niche_seeds_coverage(self):
        from cli_anything.social_trends.core.hashtags import NICHE_SEEDS
        niches = ["fitness", "food", "fashion", "beauty", "travel", "gaming",
                  "finance", "motivation", "pets", "comedy"]
        for niche in niches:
            assert niche in NICHE_SEEDS
            assert len(NICHE_SEEDS[niche]) >= 3


# ── Accounts ──────────────────────────────────────────────────────────────────

class TestAccounts:
    def test_optimize_profile_tiktok(self):
        from cli_anything.social_trends.core.accounts import optimize_profile
        result = optimize_profile("tiktok", "fitness")
        assert result["platform"] == "tiktok"
        assert "profile_checklist" in result
        assert "growth_strategies" in result
        assert "posting_frequency" in result
        assert len(result["profile_checklist"]) > 0

    def test_optimize_profile_all(self):
        from cli_anything.social_trends.core.accounts import optimize_profile
        result = optimize_profile("all")
        assert "platforms" in result
        for plat in ("tiktok", "youtube", "instagram"):
            assert plat in result["platforms"]

    def test_get_posting_schedule_structure(self):
        from cli_anything.social_trends.core.accounts import get_posting_schedule
        result = get_posting_schedule("tiktok", "US/Eastern")
        assert result["platform"] == "tiktok"
        assert "weekday_windows" in result
        assert "weekend_windows" in result
        assert "weekly_template" in result
        assert len(result["weekly_template"]) == 7  # all 7 days

    def test_audit_foundation_phase(self):
        from cli_anything.social_trends.core.accounts import audit_account
        result = audit_account("tiktok", "fitness", follower_count=500)
        assert result["growth_phase"] == "foundation"
        assert len(result["priority_actions"]) >= 3

    def test_audit_growth_phase(self):
        from cli_anything.social_trends.core.accounts import audit_account
        result = audit_account("tiktok", "fitness", follower_count=5000)
        assert result["growth_phase"] == "growth"

    def test_audit_scaling_phase(self):
        from cli_anything.social_trends.core.accounts import audit_account
        result = audit_account("youtube", "gaming", follower_count=50000)
        assert result["growth_phase"] == "scaling"

    def test_audit_monetisation_phase(self):
        from cli_anything.social_trends.core.accounts import audit_account
        result = audit_account("instagram", "fashion", follower_count=500000)
        assert result["growth_phase"] == "monetisation"

    def test_monetisation_thresholds_present(self):
        from cli_anything.social_trends.core.accounts import _monetisation_threshold
        for plat in ("tiktok", "youtube", "instagram"):
            result = _monetisation_threshold(plat)
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_weekly_template_all_days(self):
        from cli_anything.social_trends.core.accounts import _build_weekly_template
        for plat in ("tiktok", "youtube", "instagram"):
            template = _build_weekly_template(plat)
            assert len(template) == 7
            days = [t["day"] for t in template]
            assert "Monday" in days
            assert "Sunday" in days

    def test_posting_schedule_all_platforms(self):
        from cli_anything.social_trends.core.accounts import get_posting_schedule
        result = get_posting_schedule("all", "US/Pacific")
        assert "platforms" in result
        for plat in ("tiktok", "youtube", "instagram"):
            assert plat in result["platforms"]


# ── Theme Pages ───────────────────────────────────────────────────────────────

class TestThemePages:
    def test_get_guide_structure(self):
        from cli_anything.social_trends.core.theme_pages import get_guide
        result = get_guide()
        assert "guide" in result
        assert "conversion_strategies" in result
        guide = result["guide"]
        assert "starting_steps" in guide
        assert "content_rights_rules" in guide
        assert len(guide["starting_steps"]) >= 5

    def test_get_guide_with_niche(self):
        from cli_anything.social_trends.core.theme_pages import get_guide
        result = get_guide("luxury")
        assert "niche_data" in result
        assert result["niche_data"]["niche"] == "luxury"
        assert "monetisation_potential" in result["niche_data"]

    def test_get_guide_unknown_niche(self):
        from cli_anything.social_trends.core.theme_pages import get_guide
        result = get_guide("zzz_unknown_niche_xyz")
        assert "niche_not_found" in result

    def test_niche_rankings_structure(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_rankings
        result = get_niche_rankings(top_n=5)
        assert len(result["rankings"]) == 5
        for r in result["rankings"]:
            assert "rank" in r
            assert "niche" in r
            assert "monetisation_potential" in r

    def test_niche_rankings_sorted_correctly(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_rankings, NICHE_DATA
        result = get_niche_rankings(top_n=len(NICHE_DATA))
        scores = [
            int(r["monetisation_potential"].split("/")[0])
            for r in result["rankings"]
        ]
        assert scores == sorted(scores, reverse=True)

    def test_get_monetisation_strategies(self):
        from cli_anything.social_trends.core.theme_pages import get_monetisation_strategies
        result = get_monetisation_strategies("fitness")
        assert result["niche"] == "fitness"
        assert "monetisation_methods" in result
        assert "milestone_plan" in result
        assert "quick_wins" in result
        assert len(result["quick_wins"]) > 0

    def test_get_monetisation_strategies_unknown_niche(self):
        from cli_anything.social_trends.core.theme_pages import get_monetisation_strategies
        result = get_monetisation_strategies("zzz_not_a_niche_xyz")
        assert "error" in result
        assert "available" in result

    def test_get_content_calendar_structure(self):
        from cli_anything.social_trends.core.theme_pages import get_content_calendar
        result = get_content_calendar("fitness", "tiktok", weeks=2)
        assert result["niche"] == "fitness"
        assert result["platform"] == "tiktok"
        assert result["weeks"] == 2
        assert len(result["calendar"]) == 2
        for week in result["calendar"]:
            assert len(week["days"]) == 7
            for day in week["days"]:
                assert "day" in day
                assert "posts" in day

    def test_content_calendar_total_posts(self):
        from cli_anything.social_trends.core.theme_pages import get_content_calendar
        result = get_content_calendar("food", "tiktok", weeks=4)
        assert result["total_posts"] == result["posts_per_day"] * 7 * 4

    def test_all_niches_have_required_fields(self):
        from cli_anything.social_trends.core.theme_pages import NICHE_DATA
        required = ["monetisation_potential", "best_platforms", "competition",
                    "top_monetisation", "content_types", "content_sources"]
        for niche, data in NICHE_DATA.items():
            for field in required:
                assert field in data, f"Niche '{niche}' missing field '{field}'"

    def test_conversion_strategies_structure(self):
        from cli_anything.social_trends.core.theme_pages import CONVERSION_STRATEGIES
        assert "bio_conversion" in CONVERSION_STRATEGIES
        assert "content_conversion" in CONVERSION_STRATEGIES
        assert "funnel_structure" in CONVERSION_STRATEGIES
        assert "email_list_building" in CONVERSION_STRATEGIES


# ── Scraper Backend ────────────────────────────────────────────────────────────

class TestScraperBackend:
    def test_cache_roundtrip(self):
        from cli_anything.social_trends.utils.scraper_backend import (
            _write_cache, _read_cache, _cache_key
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            import cli_anything.social_trends.utils.scraper_backend as backend
            original_cache_dir = backend.CACHE_DIR
            backend.CACHE_DIR = Path(tmpdir)

            try:
                key = _cache_key("https://example.com", {"a": 1})
                data = {"test": "value", "num": 42}
                _write_cache(key, data)
                result = _read_cache(key, ttl=3600)
                assert result == data
            finally:
                backend.CACHE_DIR = original_cache_dir

    def test_cache_key_deterministic(self):
        from cli_anything.social_trends.utils.scraper_backend import _cache_key
        k1 = _cache_key("https://example.com", {"b": 2, "a": 1})
        k2 = _cache_key("https://example.com", {"a": 1, "b": 2})
        assert k1 == k2  # params sorted

    def test_cache_key_different_urls(self):
        from cli_anything.social_trends.utils.scraper_backend import _cache_key
        k1 = _cache_key("https://example.com/a", {})
        k2 = _cache_key("https://example.com/b", {})
        assert k1 != k2

    def test_load_config_missing_file(self):
        from cli_anything.social_trends.utils.scraper_backend import load_config
        import cli_anything.social_trends.utils.scraper_backend as backend
        original = backend.CONFIG_FILE
        backend.CONFIG_FILE = Path("/tmp/nonexistent_test_config_xyz.json")
        try:
            result = load_config()
            assert result == {}
        finally:
            backend.CONFIG_FILE = original

    def test_save_and_load_config(self):
        from cli_anything.social_trends.utils.scraper_backend import save_config, load_config
        import cli_anything.social_trends.utils.scraper_backend as backend

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = backend.CONFIG_DIR
            original_file = backend.CONFIG_FILE
            backend.CONFIG_DIR = Path(tmpdir)
            backend.CONFIG_FILE = Path(tmpdir) / "config.json"

            try:
                save_config({"youtube_api_key": "test123", "default_region": "US"})
                result = load_config()
                assert result["youtube_api_key"] == "test123"
                assert result["default_region"] == "US"
            finally:
                backend.CONFIG_DIR = original_dir
                backend.CONFIG_FILE = original_file


# ── Trends (mocked) ───────────────────────────────────────────────────────────

class TestTrendsMocked:
    def test_youtube_rss_parse(self):
        from cli_anything.social_trends.core.trends import _youtube_trending_rss
        sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry>
    <yt:videoId>abc123</yt:videoId>
    <title>Test Video Title</title>
    <author><name>Test Channel</name></author>
    <published>2024-01-01T00:00:00Z</published>
    <link href="https://www.youtube.com/watch?v=abc123"/>
  </entry>
</feed>"""
        with patch("cli_anything.social_trends.core.trends.get_html", return_value=sample_rss):
            result = _youtube_trending_rss(bypass_cache=True)

        assert result["source"] == "youtube_rss"
        assert len(result["videos"]) == 1
        assert result["videos"][0]["video_id"] == "abc123"
        assert result["videos"][0]["title"] == "Test Video Title"
        assert result["videos"][0]["channel"] == "Test Channel"

    def test_youtube_rss_parse_error(self):
        from cli_anything.social_trends.core.trends import _youtube_trending_rss
        with patch("cli_anything.social_trends.core.trends.get_html", return_value="not xml"):
            result = _youtube_trending_rss(bypass_cache=True)
        assert "error" in result
        assert result["videos"] == []

    def test_tiktok_hashtags_network_error(self):
        from cli_anything.social_trends.core.trends import get_tiktok_trending_hashtags
        with patch("cli_anything.social_trends.core.trends.get",
                   side_effect=Exception("Connection refused")):
            result = get_tiktok_trending_hashtags()
        assert "error" in result
        assert result["hashtags"] == []

    def test_tiktok_videos_network_error(self):
        from cli_anything.social_trends.core.trends import get_tiktok_trending_videos
        with patch("cli_anything.social_trends.core.trends.get",
                   side_effect=Exception("Connection refused")):
            result = get_tiktok_trending_videos()
        assert "error" in result
        assert result["videos"] == []

    def test_youtube_api_no_key(self):
        from cli_anything.social_trends.core.trends import get_youtube_trending
        with patch("cli_anything.social_trends.core.trends.load_config", return_value={}):
            with patch("cli_anything.social_trends.core.trends.get_html") as mock_rss:
                mock_rss.return_value = "<feed xmlns='http://www.w3.org/2005/Atom'></feed>"
                result = get_youtube_trending()
        assert result["source"] == "youtube_rss"

    def test_compare_trends(self):
        from cli_anything.social_trends.core.trends import compare_trends
        yt_data = {"source": "youtube_rss", "videos": [
            {"title": "fitness workout", "tags": ["fitness", "gym"]},
        ]}
        tt_hash_data = {"hashtags": [{"name": "fitness", "hashtag": "#fitness"}]}
        tt_vid_data = {"videos": [{"title": "fitness tips", "hashtags": ["fitness"]}]}

        with patch("cli_anything.social_trends.core.trends.get_youtube_trending", return_value=yt_data):
            with patch("cli_anything.social_trends.core.trends.get_tiktok_trending_hashtags", return_value=tt_hash_data):
                with patch("cli_anything.social_trends.core.trends.get_tiktok_trending_videos", return_value=tt_vid_data):
                    result = compare_trends("fitness", "US")

        assert result["topic"] == "fitness"
        assert result["youtube"]["matched_videos"] == 1
        assert result["tiktok"]["matched_hashtags"] == 1


# ── Music (mocked) ────────────────────────────────────────────────────────────

class TestMusicMocked:
    def test_tiktok_sounds_structure(self):
        from cli_anything.social_trends.core.music import get_tiktok_trending_sounds
        mock_data = {
            "data": {
                "list": [
                    {
                        "music_id": "111",
                        "music_name": "viral sound",
                        "author": "Artist Name",
                        "duration": 30,
                        "video_count": 500000,
                        "rank": 1,
                        "trend_score": 99,
                    }
                ]
            }
        }
        with patch("cli_anything.social_trends.core.music.get", return_value=mock_data):
            result = get_tiktok_trending_sounds()

        assert result["source"] == "tiktok_creative_center"
        assert len(result["sounds"]) == 1
        s = result["sounds"][0]
        assert s["music_id"] == "111"
        assert s["title"] == "viral sound"
        assert s["artist"] == "Artist Name"

    def test_youtube_music_no_api_key(self):
        from cli_anything.social_trends.core.music import get_youtube_trending_music
        with patch("cli_anything.social_trends.core.music.load_config", return_value={}):
            result = get_youtube_trending_music()
        assert "error" in result
        assert "tip" in result
        assert result["videos"] == []

    def test_tiktok_sounds_network_error(self):
        from cli_anything.social_trends.core.music import get_tiktok_trending_sounds
        with patch("cli_anything.social_trends.core.music.get", side_effect=Exception("timeout")):
            result = get_tiktok_trending_sounds()
        assert "error" in result

    def test_search_sounds_fallback(self):
        from cli_anything.social_trends.core.music import search_tiktok_sounds
        mock_trending = {
            "sounds": [
                {"title": "pop song viral", "artist": "Singer A", "video_count": 100},
                {"title": "hip hop beat", "artist": "Rapper B", "video_count": 200},
            ]
        }
        with patch("cli_anything.social_trends.core.music.get", side_effect=Exception("search unavailable")):
            with patch("cli_anything.social_trends.core.music.get_tiktok_trending_sounds",
                       return_value=mock_trending):
                result = search_tiktok_sounds("pop")

        assert result["query"] == "pop"
        assert result["source"] == "filtered_trending"
        assert len(result["sounds"]) == 1
        assert result["sounds"][0]["title"] == "pop song viral"


# ── CLI Integration ───────────────────────────────────────────────────────────

class TestCLI:
    def test_cli_hashtags_generate(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        with patch("cli_anything.social_trends.core.hashtags._fetch_live_hashtags", return_value=[]):
            result = runner.invoke(main, ["hashtags", "generate", "fitness", "--posts", "2"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["sets"]) == 2

    def test_cli_accounts_optimize(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["accounts", "optimize", "tiktok", "--niche", "food"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"

    def test_cli_theme_pages_niches(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme-pages", "niches", "--top", "5"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["rankings"]) == 5

    def test_cli_theme_pages_calendar(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme-pages", "calendar", "fitness", "--weeks", "1"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["weeks"] == 1

    def test_cli_accounts_audit(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["accounts", "audit", "tiktok", "--followers", "500"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["growth_phase"] == "foundation"

    def test_cli_config_set_show(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        import tempfile
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            import cli_anything.social_trends.utils.scraper_backend as backend
            orig_dir = backend.CONFIG_DIR
            orig_file = backend.CONFIG_FILE
            backend.CONFIG_DIR = Path(tmpdir)
            backend.CONFIG_FILE = Path(tmpdir) / "config.json"
            try:
                set_result = runner.invoke(main, ["config", "set", "default_region", "GB"])
                assert set_result.exit_code == 0

                show_result = runner.invoke(main, ["config", "show"])
                assert show_result.exit_code == 0
                data = json.loads(show_result.output)
                assert data.get("default_region") == "GB"
            finally:
                backend.CONFIG_DIR = orig_dir
                backend.CONFIG_FILE = orig_file

    def test_cli_posting_schedule(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["accounts", "schedule", "youtube", "--timezone", "US/Pacific"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert len(data["weekly_template"]) == 7

    def test_cli_hashtags_research(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        with patch("cli_anything.social_trends.core.hashtags._fetch_live_hashtags", return_value=[]):
            result = runner.invoke(main, ["hashtags", "research", "food"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["topic"] == "food"

    def test_cli_theme_pages_guide_no_niche(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme-pages", "guide"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "guide" in data
        assert "conversion_strategies" in data

    def test_cli_theme_pages_monetize(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import main
        runner = CliRunner()
        result = runner.invoke(main, ["theme-pages", "monetize", "luxury"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "luxury"
        assert "milestone_plan" in data
