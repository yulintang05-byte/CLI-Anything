"""Unit tests for social-trends CLI."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli
from cli_anything.social_trends.optimizer import (
    build_hashtag_set,
    get_posting_schedule,
    generate_content_angles,
    analyze_account,
)
from cli_anything.social_trends.theme_pages import (
    get_all_niches,
    get_niche_strategy,
    get_conversion_roadmap,
    estimate_revenue,
)
from cli_anything.social_trends.scrapers.youtube import extract_hashtags_from_titles
from cli_anything.social_trends.scrapers.tiktok import derive_niche_hashtags


# ── Optimizer tests ──────────────────────────────────────────────────────────

class TestBuildHashtagSet:
    def test_basic_tiktok(self):
        trending = [
            {"hashtag": "#fitness", "post_count": 500_000_000},
            {"hashtag": "#gym", "post_count": 200_000_000},
            {"hashtag": "#workout", "post_count": 50_000_000},
            {"hashtag": "#gains", "post_count": 5_000_000},
        ]
        result = build_hashtag_set(trending, "fitness", "tiktok", max_tags=8)
        assert "hashtags" in result
        assert len(result["hashtags"]) <= 8
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"
        # fyp must be included for TikTok
        assert "#fyp" in result["hashtags"]

    def test_youtube_no_essentials(self):
        trending = [
            {"hashtag": "#python", "post_count": 0},
            {"hashtag": "#coding", "post_count": 0},
        ]
        result = build_hashtag_set(trending, "coding", "youtube", max_tags=5)
        assert len(result["hashtags"]) <= 5

    def test_empty_trending(self):
        result = build_hashtag_set([], "gaming", "tiktok", max_tags=5)
        assert isinstance(result["hashtags"], list)


class TestPostingSchedule:
    def test_returns_schedule(self):
        result = get_posting_schedule("tiktok", timezone_offset=-5, posts_per_week=7)
        assert result["platform"] == "tiktok"
        assert "schedule" in result
        assert len(result["schedule"]) <= 7
        assert "frequency" in result
        assert "video_length" in result

    def test_all_platforms(self):
        for platform in ["tiktok", "youtube", "instagram", "twitter"]:
            result = get_posting_schedule(platform)
            assert result["platform"] == platform
            assert len(result["schedule"]) > 0

    def test_time_format(self):
        result = get_posting_schedule("tiktok", timezone_offset=0, posts_per_week=3)
        for slot in result["schedule"]:
            assert "day" in slot
            assert "time_local" in slot
            assert "priority" in slot


class TestGenerateContentAngles:
    def test_returns_angles(self):
        titles = [
            "10 Fitness Transformations That Will Shock You",
            "I Tried This Viral Workout for 30 Days",
        ]
        angles = generate_content_angles(titles, "fitness", "tiktok")
        assert len(angles) >= 5
        for a in angles:
            assert "angle" in a
            assert "framework" in a
            assert "virality_reason" in a

    def test_niche_adaptation(self):
        titles = ["Trending Video"]
        angles = generate_content_angles(titles, "cooking", "youtube")
        assert any("cooking" in a["angle"].lower() for a in angles)


class TestAnalyzeAccount:
    def test_basic_analysis(self):
        result = analyze_account(
            platform="tiktok",
            niche="fitness",
            current_followers=5000,
            avg_views=300,
            posts_per_week=2,
        )
        assert "health_score" in result
        assert 0 <= result["health_score"] <= 100
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0
        assert "posting_schedule" in result

    def test_priority_ordering(self):
        result = analyze_account("tiktok", "fitness", 500, 10, 1)
        priorities = [r["priority"] for r in result["recommendations"]]
        # HIGH should come before MEDIUM before LOW
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        scores = [priority_order[p] for p in priorities]
        assert scores == sorted(scores)

    def test_no_followers_zero_division(self):
        result = analyze_account("tiktok", "fitness", 0, 0, 0)
        assert result["health_score"] >= 0


# ── Theme Pages tests ─────────────────────────────────────────────────────────

class TestThemePages:
    def test_get_all_niches(self):
        niches = get_all_niches()
        assert len(niches) >= 5
        for n in niches:
            assert "key" in n
            assert "name" in n
            assert "monetization_potential" in n

    def test_get_niche_strategy(self):
        strategy = get_niche_strategy("fitness_motivation")
        assert strategy is not None
        assert "top_hashtags" in strategy
        assert "monetization_paths" in strategy
        assert "posting_strategy" in strategy

    def test_unknown_niche_returns_none(self):
        assert get_niche_strategy("nonexistent_niche_xyz") is None

    def test_roadmap_all_phases(self):
        roadmap = get_conversion_roadmap(0)
        assert len(roadmap) == 5
        phases = [r["phase"] for r in roadmap]
        assert phases == sorted(phases)

    def test_roadmap_midway(self):
        roadmap = get_conversion_roadmap(15_000)
        assert roadmap[0]["phase"] >= 3

    def test_estimate_revenue(self):
        result = estimate_revenue(100_000, "tiktok", "fitness_motivation", 7)
        assert "total_monthly_estimate" in result
        assert "revenue_breakdown" in result
        assert "$" in result["total_monthly_estimate"]

    def test_revenue_zero_followers(self):
        result = estimate_revenue(0, "youtube", "luxury_lifestyle", 3)
        assert result["followers"] == 0


# ── Scraper unit tests (no network) ──────────────────────────────────────────

class TestExtractHashtagsFromTitles:
    def test_explicit_hashtags(self):
        videos = [
            {"title": "My #fitness journey #gym #workout"},
            {"title": "The #fitness grind #motivation"},
        ]
        tags = extract_hashtags_from_titles(videos)
        hashtag_names = [t["hashtag"] for t in tags]
        assert "#fitness" in hashtag_names
        assert "#gym" in hashtag_names

    def test_derived_from_words(self):
        videos = [{"title": "Amazing transformation workout results"} for _ in range(3)]
        tags = extract_hashtags_from_titles(videos)
        assert len(tags) > 0

    def test_empty_videos(self):
        assert extract_hashtags_from_titles([]) == []


class TestDeriveNicheHashtags:
    def test_fitness_niche(self):
        hashtags = [
            {"hashtag": "#fitness", "post_count": 100},
            {"hashtag": "#food", "post_count": 200},
            {"hashtag": "#gym", "post_count": 50},
            {"hashtag": "#workout", "post_count": 75},
        ]
        result = derive_niche_hashtags(hashtags, "fitness gym")
        # Fitness-related tags should score higher
        assert result[0]["niche_score"] >= result[-1]["niche_score"]

    def test_empty_input(self):
        assert derive_niche_hashtags([], "fitness") == []


# ── CLI integration tests ─────────────────────────────────────────────────────

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "social-trends" in result.output.lower() or "Usage" in result.output

    def test_theme_pages_list(self):
        result = self.runner.invoke(cli, ["theme-pages", "list"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower() or "luxury" in result.output.lower()

    def test_theme_pages_list_json(self):
        result = self.runner.invoke(cli, ["--json", "theme-pages", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_theme_pages_strategy_known(self):
        result = self.runner.invoke(cli, ["theme-pages", "strategy", "--niche", "pets_animals"])
        assert result.exit_code == 0

    def test_theme_pages_strategy_unknown(self):
        result = self.runner.invoke(cli, ["theme-pages", "strategy", "--niche", "xyz_fake"])
        assert result.exit_code != 0

    def test_theme_pages_roadmap(self):
        result = self.runner.invoke(cli, ["theme-pages", "roadmap", "--followers", "0"])
        assert result.exit_code == 0
        assert "Phase" in result.output or "phase" in result.output

    def test_theme_pages_revenue_json(self):
        result = self.runner.invoke(cli, [
            "--json", "theme-pages", "revenue",
            "--platform", "tiktok",
            "--niche", "fitness_motivation",
            "--followers", "50000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "total_monthly_estimate" in data

    def test_optimize_schedule(self):
        result = self.runner.invoke(cli, [
            "optimize", "schedule",
            "--platform", "youtube",
            "--tz-offset", "-5",
            "--posts-week", "5",
        ])
        assert result.exit_code == 0
        assert "schedule" in result.output.lower() or "Monday" in result.output

    @patch("cli_anything.social_trends.scrapers.tiktok.get_trending_hashtags")
    @patch("cli_anything.social_trends.scrapers.tiktok.get_trending_sounds")
    @patch("cli_anything.social_trends.scrapers.tiktok.get_trending_videos")
    @patch("cli_anything.social_trends.scrapers.youtube.get_trending_videos")
    @patch("cli_anything.social_trends.scrapers.music.get_billboard_hot100")
    def test_dashboard_mocked(self, mock_bb, mock_yt, mock_tt_vid, mock_tt_sounds, mock_tt_tags):
        mock_yt.return_value = [
            {"title": "Trending Video", "channel": "Channel1", "views": "1M", "video_id": "abc", "url": "", "badges": []}
        ]
        mock_tt_tags.return_value = [
            {"hashtag": "#fitness", "rank": 1, "post_count": 1000000, "video_views": 5000000, "trend": "up", "country": "US"}
        ]
        mock_tt_sounds.return_value = [
            {"rank": 1, "title": "Hot Song", "artist": "Artist A", "duration": 30, "post_count": 50000, "video_views": 1000000, "link": "", "trend": "up", "country": "US"}
        ]
        mock_tt_vid.return_value = []
        mock_bb.return_value = [
            {"rank": 1, "title": "Song Title", "artist": "Artist", "chart": "Hot 100", "platform": "billboard"}
        ]

        result = self.runner.invoke(cli, ["dashboard", "--region", "US"])
        assert result.exit_code == 0
        assert "YOUTUBE" in result.output
        assert "TIKTOK" in result.output
