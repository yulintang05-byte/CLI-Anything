"""End-to-end tests for cli-anything-social-media.

These tests invoke real yt-dlp calls and require network access.
They FAIL (not skip) if yt-dlp is not installed — zero-compromise policy.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from cli_anything.social_media.utils.social_backend import (
    check_ytdlp, check_all_dependencies, assert_ytdlp_installed,
)
from cli_anything.social_media.core.account_optimizer import (
    AccountProfile, register_account, remove_account, optimize_account,
    optimize_all_accounts, list_accounts,
)
from cli_anything.social_media.core.theme_pages import (
    get_playbook, get_conversion_strategies, compare_niches, list_niches,
)
from cli_anything.social_media.core.trends_aggregator import generate_cross_platform_report


# ══════════════════════════════════════════════════════════════════════
# Dependency checks
# ══════════════════════════════════════════════════════════════════════

class TestDependencies:
    """Verify all required dependencies are present."""

    def test_ytdlp_available(self):
        status = check_ytdlp()
        assert status.available, (
            f"yt-dlp is required but not installed.\n"
            f"Install it with: {status.install_command}"
        )

    def test_ytdlp_has_version(self):
        status = check_ytdlp()
        assert status.available
        assert len(status.version) > 0

    def test_assert_ytdlp_does_not_raise(self):
        assert_ytdlp_installed()  # Should not raise

    def test_check_all_dependencies_returns_list(self):
        deps = check_all_dependencies()
        assert isinstance(deps, list)
        assert len(deps) >= 1
        names = [d.name for d in deps]
        assert "yt-dlp" in names

    def test_ytdlp_runs_version_command(self):
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0


# ══════════════════════════════════════════════════════════════════════
# YouTube scraper E2E
# ══════════════════════════════════════════════════════════════════════

class TestYouTubeScraperE2E:
    """Real yt-dlp calls to YouTube — requires network + yt-dlp."""

    def test_scrape_youtube_trending_returns_result(self):
        from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

        result = scrape_youtube_trending(category="trending", region="US", max_results=5)
        assert result.scraped_at
        assert result.region == "US"
        assert isinstance(result.trends, list)
        assert isinstance(result.top_hashtags, list)
        assert isinstance(result.viral_patterns, list)

    def test_scrape_youtube_trending_has_videos(self):
        from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

        result = scrape_youtube_trending(category="trending", region="US", max_results=5)
        assert len(result.trends) > 0, (
            "Expected at least 1 trending video from YouTube scrape. "
            "Check network connectivity and yt-dlp version."
        )

    def test_youtube_trend_fields_populated(self):
        from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

        result = scrape_youtube_trending(category="trending", region="US", max_results=3)
        if not result.trends:
            pytest.skip("No trends returned — network issue or geo-restriction")

        trend = result.trends[0]
        assert isinstance(trend.title, str)
        assert isinstance(trend.video_id, str)
        assert len(trend.video_id) > 0
        assert isinstance(trend.view_count, int)
        assert trend.view_count >= 0
        assert isinstance(trend.hashtags, list)
        assert 0.0 <= trend.engagement_rate < 100.0

    def test_youtube_trending_music_category(self):
        from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

        result = scrape_youtube_trending(category="music", region="US", max_results=3)
        assert isinstance(result.trends, list)
        # Music category should exist even if fewer results

    def test_youtube_to_dict(self):
        from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

        result = scrape_youtube_trending(category="trending", region="US", max_results=2)
        data = result.to_dict()
        assert "scraped_at" in data
        assert "trends" in data
        assert "top_hashtags" in data
        assert "viral_patterns" in data
        # Should be JSON serializable
        json_str = json.dumps(data)
        assert len(json_str) > 10

    def test_youtube_hashtag_search(self):
        from cli_anything.social_media.core.youtube_scraper import search_youtube_hashtag

        results = search_youtube_hashtag("viral", max_results=3)
        assert isinstance(results, list)
        # May be empty depending on network, but should not raise


# ══════════════════════════════════════════════════════════════════════
# TikTok scraper E2E
# ══════════════════════════════════════════════════════════════════════

class TestTikTokScraperE2E:
    """Real yt-dlp TikTok calls — requires network + yt-dlp."""

    def test_scrape_tiktok_trending_returns_result(self):
        from cli_anything.social_media.core.tiktok_scraper import scrape_tiktok_trending

        result = scrape_tiktok_trending(niche="general", region="US", max_results=5)
        assert result.scraped_at
        assert isinstance(result.trends, list)
        assert isinstance(result.top_hashtags, list)
        assert isinstance(result.content_strategy, list)

    def test_tiktok_trending_fitness_niche(self):
        from cli_anything.social_media.core.tiktok_scraper import scrape_tiktok_trending

        result = scrape_tiktok_trending(niche="fitness", region="US", max_results=5)
        assert isinstance(result.trends, list)

    def test_tiktok_to_dict(self):
        from cli_anything.social_media.core.tiktok_scraper import scrape_tiktok_trending

        result = scrape_tiktok_trending(niche="general", region="US", max_results=2)
        data = result.to_dict()
        assert "scraped_at" in data
        assert "trends" in data
        assert "top_hashtags" in data
        json_str = json.dumps(data)
        assert len(json_str) > 10


# ══════════════════════════════════════════════════════════════════════
# Trends aggregator E2E
# ══════════════════════════════════════════════════════════════════════

class TestTrendsAggregatorE2E:
    """Full cross-platform report generation — requires network."""

    def test_generate_report_both_platforms(self):
        report = generate_cross_platform_report(
            niche="general",
            region="US",
            max_results=5,
            include_youtube=True,
            include_tiktok=True,
        )
        assert report.generated_at
        assert isinstance(report.unified_trends, list)
        assert isinstance(report.master_hashtags, list)
        assert isinstance(report.proactive_actions, list)

    def test_generate_report_youtube_only(self):
        report = generate_cross_platform_report(
            niche="general",
            region="US",
            max_results=5,
            include_youtube=True,
            include_tiktok=False,
        )
        assert report.youtube is not None
        assert report.tiktok is None

    def test_generate_report_tiktok_only(self):
        report = generate_cross_platform_report(
            niche="fitness",
            region="US",
            max_results=5,
            include_youtube=False,
            include_tiktok=True,
        )
        assert report.youtube is None
        assert report.tiktok is not None

    def test_report_has_proactive_actions(self):
        report = generate_cross_platform_report(
            niche="general", region="US", max_results=5
        )
        assert len(report.proactive_actions) > 0

    def test_report_to_dict_json_serializable(self):
        report = generate_cross_platform_report(
            niche="general", region="US", max_results=3
        )
        data = report.to_dict()
        json_str = json.dumps(data, default=str)
        assert len(json_str) > 50


# ══════════════════════════════════════════════════════════════════════
# Account optimizer E2E (no network needed, but tests full pipeline)
# ══════════════════════════════════════════════════════════════════════

class TestAccountOptimizerE2E:
    """Full account optimization pipeline tests."""

    E2E_USERNAME = "e2e_test_account_pytest_777"

    def setup_method(self):
        self.profile = AccountProfile(
            platform="tiktok",
            username=self.E2E_USERNAME,
            display_name="E2E Test Account",
            bio="Testing the optimization pipeline with a realistic bio that has enough characters",
            follower_count=8_500,
            following_count=350,
            post_count=90,
            avg_views=25_000,
            avg_likes=2_000,
            avg_comments=150,
            niche="fitness",
            posting_frequency="3x/week",
            content_types=["tutorials", "vlogs"],
            current_hashtags=["fitness", "gym"],
            profile_url="https://www.tiktok.com/@e2e_test",
            notes="E2E test account",
        )
        register_account(self.profile)

    def teardown_method(self):
        remove_account("tiktok", self.E2E_USERNAME)

    def test_full_optimize_pipeline(self):
        report = optimize_account(self.profile)
        assert report is not None
        assert report.account.username == self.E2E_USERNAME
        assert 0 <= report.score.overall <= 100
        assert len(report.quick_wins) >= 2
        assert len(report.strategic_recommendations) >= 3
        assert len(report.content_calendar) == 7
        assert len(report.monetization_opportunities) >= 2
        assert report.bio_rewrite
        assert "add_niche" in report.hashtag_overhaul

    def test_optimize_with_trending_tags(self):
        trending = ["viral", "fyp", "trending2025", "fitness", "gym"]
        report = optimize_account(self.profile, trending_tags=trending)
        # Trending tags should appear in hashtag overhaul
        assert any(
            t in str(report.hashtag_overhaul)
            for t in trending
        )

    def test_optimize_all_accounts(self):
        reports = optimize_all_accounts()
        assert isinstance(reports, list)
        usernames = [r.account.username for r in reports]
        assert self.E2E_USERNAME in usernames

    def test_report_to_dict_complete(self):
        report = optimize_account(self.profile)
        data = report.to_dict()
        required_keys = [
            "generated_at", "account", "score", "critical_fixes",
            "quick_wins", "strategic_recommendations", "hashtag_overhaul",
            "bio_rewrite", "content_calendar", "competitor_gap_analysis",
            "monetization_opportunities",
        ]
        for key in required_keys:
            assert key in data, f"Missing key: {key}"
        # Must be JSON serializable
        json.dumps(data, default=str)


# ══════════════════════════════════════════════════════════════════════
# Theme pages E2E (no network needed)
# ══════════════════════════════════════════════════════════════════════

class TestThemePagesE2E:
    """Full theme page pipeline — no network, pure logic."""

    def test_all_niches_have_complete_data(self):
        for niche in list_niches():
            assert niche.niche
            assert niche.competition_level in ("low", "medium", "high", "very high")
            assert niche.monetization_potential in ("low", "medium", "high", "very high")
            assert niche.avg_cpm > 0
            assert len(niche.top_hashtags) >= 5
            assert len(niche.monetization_paths) >= 3
            assert len(niche.top_platforms) >= 1

    def test_playbook_all_platforms(self):
        for platform in ("tiktok", "instagram", "youtube"):
            playbook = get_playbook("fitness", platform)
            assert playbook.platform == platform
            assert len(playbook.phase_1_launch) >= 5
            assert len(playbook.tools_needed) >= 4

    def test_all_conversion_strategies_complete(self):
        for strategy in get_conversion_strategies():
            assert strategy.strategy_name
            assert strategy.income_potential
            assert len(strategy.steps) >= 4
            assert len(strategy.tools) >= 1
            assert strategy.examples

    def test_compare_all_niches(self):
        all_niches = [n.niche for n in list_niches()]
        results = compare_niches(all_niches)
        assert len(results) == len(all_niches)


# ══════════════════════════════════════════════════════════════════════
# CLI entry point E2E (via subprocess)
# ══════════════════════════════════════════════════════════════════════

class TestCLIEntryPointE2E:
    """Verify CLI can be invoked via command line."""

    def test_cli_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media", "--help"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        assert "social" in result.stdout.lower() or "media" in result.stdout.lower()

    def test_cli_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media", "--version"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_cli_theme_niches(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media",
             "theme", "niches", "--json"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_cli_theme_playbook_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media",
             "theme", "playbook", "--niche", "fitness", "--json"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "phase_1_launch" in data
        assert "monetization_timeline" in data

    def test_cli_theme_convert_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media",
             "theme", "convert", "--json"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_cli_account_list_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media",
             "account", "list", "--json"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        # Should succeed even with empty account list
        assert result.returncode == 0

    def test_cli_theme_compare_json(self):
        result = subprocess.run(
            [sys.executable, "-m", "cli_anything.social_media",
             "theme", "compare", "fitness", "travel", "--json"],
            capture_output=True, text=True, timeout=30,
            cwd="/home/user/CLI-Anything/social-media/agent-harness",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 2
