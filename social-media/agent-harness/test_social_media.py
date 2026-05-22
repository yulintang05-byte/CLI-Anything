"""Tests for social media trend intelligence and optimizer."""
import json
import subprocess
import sys
import os
import pytest

# Ensure local package is on path
sys.path.insert(0, os.path.dirname(__file__))

from social_media.optimizer import optimize_bio, optimize_post, account_health_report
from social_media.theme_pages import (
    list_niches, niche_analysis, content_calendar, conversion_funnel_guide,
)


# ── optimizer tests ──────────────────────────────────────────────────────────

class TestOptimizeBio:
    def test_short_bio_flags_issue(self):
        result = optimize_bio("hi", "fitness", [], "tiktok")
        assert result["score"] < 100
        assert any("short" in i.lower() for i in result["issues"])

    def test_missing_niche_flags_issue(self):
        result = optimize_bio("Follow for daily tips! Link in bio", "fitness", [], "tiktok")
        assert any("niche" in i.lower() or "fitness" in i.lower() for i in result["issues"])

    def test_good_bio_scores_high(self):
        result = optimize_bio(
            "Fitness tips & workouts | Follow for daily fitness content | Link in bio",
            "fitness",
            ["#fitness", "#gym"],
            "tiktok",
        )
        assert result["score"] >= 70

    def test_suggested_bio_not_empty(self):
        result = optimize_bio("hello", "finance", ["#money"], "tiktok")
        assert len(result["suggested_bio"]) > 10


class TestOptimizePost:
    TRENDING = [
        {"hashtag": "#fyp", "frequency": 50},
        {"hashtag": "#viral", "frequency": 40},
        {"hashtag": "#fitness", "frequency": 30},
    ]

    def test_no_hashtags_penalized(self):
        result = optimize_post("Great workout today!", [], self.TRENDING, [], "tiktok")
        assert result["score"] < 80
        assert len(result["suggestions"]) > 0

    def test_trending_overlap_adds_recommendations(self):
        result = optimize_post("Check this", ["mylife"], self.TRENDING, [], "tiktok")
        assert len(result["recommended_hashtags_to_add"]) > 0

    def test_optimized_hashtags_within_limit(self):
        tags = ["a", "b", "c", "d", "e"]
        result = optimize_post("Caption", tags, self.TRENDING, [], "tiktok")
        assert len(result["optimized_hashtags"]) <= 5  # tiktok hi limit

    def test_engagement_rate_calculated(self):
        result = optimize_post(
            "test", ["fitness"], self.TRENDING, [],
            platform="tiktok", current_likes=500, current_comments=50,
            current_shares=25, followers=1000,
        )
        assert result["engagement_rate"] == pytest.approx(57.5, rel=0.01)


class TestAccountHealthReport:
    TAGS = [{"hashtag": "#fitness"}, {"hashtag": "#gym"}]

    def test_low_engagement_flagged(self):
        result = account_health_report(
            "tiktok", "testuser", 10000, 500, 30,
            avg_views=100, avg_likes=10, avg_comments=1, avg_shares=1,
            niche="fitness", trending_hashtags=self.TAGS,
        )
        assert result["health_score"] < 80
        assert len(result["issues"]) > 0

    def test_growth_playbook_not_empty(self):
        result = account_health_report(
            "tiktok", "testuser", 5000, 200, 50,
            avg_views=2000, avg_likes=300, avg_comments=25, avg_shares=15,
            niche="fitness", trending_hashtags=self.TAGS,
        )
        assert len(result["growth_playbook"]) >= 3

    def test_ff_ratio_calculated(self):
        result = account_health_report(
            "tiktok", "user", 10000, 500, 30,
            avg_views=1000, avg_likes=100, avg_comments=10, avg_shares=5,
            niche="motivation", trending_hashtags=self.TAGS,
        )
        assert result["follower_following_ratio"] == pytest.approx(20.0, rel=0.01)


# ── theme_pages tests ────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_nonempty(self):
        niches = list_niches()
        assert len(niches) >= 5
        assert all("niche" in n and "description" in n for n in niches)

    def test_niche_analysis_valid(self):
        result = niche_analysis("fitness")
        assert "monetization" in result
        assert "revenue_estimates" in result
        assert "10k_followers" in result["revenue_estimates"]

    def test_niche_analysis_unknown(self):
        result = niche_analysis("nonexistent_niche_xyz")
        assert "error" in result
        assert "available_niches" in result

    def test_content_calendar_length(self):
        cal = content_calendar("motivation", days=7)
        assert len(cal) == 7
        for day in cal:
            assert "hook_ideas" in day
            assert len(day["hook_ideas"]) > 0

    def test_conversion_funnel_stages(self):
        funnel = conversion_funnel_guide("finance")
        assert len(funnel["funnel_stages"]) == 4
        assert "tools_recommended" in funnel


# ── CLI integration tests ─────────────────────────────────────────────────────

class TestCLI:
    def _run(self, *args) -> dict:
        result = subprocess.run(
            [sys.executable, "cli.py", *args],
            capture_output=True, text=True, cwd=os.path.dirname(__file__),
        )
        assert result.returncode == 0, f"CLI error: {result.stderr}"
        return json.loads(result.stdout)

    def test_trends_demo_mode(self):
        result = self._run("trends")
        # Demo mode returns a dict with demo_output
        assert "demo_output" in result or "youtube" in result or "error" in result

    def test_niches_command(self):
        result = self._run("niches")
        assert isinstance(result, list)
        assert len(result) >= 5

    def test_niche_command(self):
        result = self._run("niche", "fitness")
        assert "monetization" in result

    def test_calendar_command(self):
        result = self._run("calendar", "motivation")
        assert isinstance(result, list)
        assert len(result) == 7

    def test_funnel_command(self):
        result = self._run("funnel", "finance")
        assert "funnel_stages" in result

    def test_bio_command(self):
        result = self._run(
            "bio",
            "--bio", "I post stuff follow me",
            "--niche", "fitness",
            "--platform", "tiktok",
        )
        assert "score" in result
        assert "suggested_bio" in result

    def test_optimize_command(self):
        result = self._run(
            "optimize",
            "--caption", "My morning routine changed my life!",
            "--hashtags", "morning,routine",
            "--platform", "tiktok",
            "--followers", "5000",
        )
        assert "score" in result
        assert "optimized_hashtags" in result

    def test_account_command(self):
        result = self._run(
            "account",
            "--platform", "tiktok",
            "--username", "testpage",
            "--followers", "8000",
            "--following", "400",
            "--posts", "35",
            "--avg-views", "1500",
            "--avg-likes", "120",
            "--avg-comments", "12",
            "--avg-shares", "8",
            "--niche", "fitness",
        )
        assert "health_score" in result
        assert "growth_playbook" in result
