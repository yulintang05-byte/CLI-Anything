"""Tests for social-media-trends CLI — no API keys required."""

import json
import pytest
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import main
from cli_anything.social_trends.core import trends_analyzer as ta
from cli_anything.social_trends.core import account_optimizer as ao
from cli_anything.social_trends.core import theme_page as tp
from cli_anything.social_trends.core import tiktok_scraper as tt


@pytest.fixture
def runner():
    return CliRunner()


# ─── TikTok Creative Center (no API key) ──────────────────────────────────────

class TestTikTokCreativeCenter:
    def test_hashtags_returns_list(self):
        # Mock the CC endpoint to avoid real network calls in CI
        result = tt.extract_hashtags_from_videos([
            {"description": "#fitness is trending #workout", "like_count": 5000, "share_count": 200, "comment_count": 100, "hashtags": ["fitness", "workout"]},
            {"description": "#finance tips #money", "like_count": 8000, "share_count": 400, "comment_count": 200, "hashtags": ["finance", "money"]},
        ])
        assert isinstance(result, list)
        assert len(result) > 0
        assert "hashtag" in result[0]
        assert result[0]["hashtag"].startswith("#")

    def test_hashtag_ranking_by_engagement(self):
        videos = [
            {"description": "#viral content", "like_count": 100000, "share_count": 5000, "comment_count": 2000, "hashtags": ["viral"]},
            {"description": "#small niche", "like_count": 100, "share_count": 10, "comment_count": 5, "hashtags": ["small"]},
        ]
        result = tt.extract_hashtags_from_videos(videos)
        tags = [r["hashtag"] for r in result]
        assert tags.index("#viral") < tags.index("#small")


# ─── Trends Analyzer ──────────────────────────────────────────────────────────

class TestTrendsAnalyzer:
    def test_merge_hashtags(self):
        yt_tags = [{"hashtag": "#fitness", "score": 1000000}, {"hashtag": "#workout", "score": 500000}]
        tt_tags = [{"hashtag": "#fitness", "view_count": 2000000}, {"hashtag": "#gym", "view_count": 800000}]
        merged = ta.merge_hashtags(yt_tags, tt_tags)
        assert len(merged) > 0
        assert merged[0]["hashtag"].startswith("#")
        assert "cross_platform_score" in merged[0]

    def test_merge_hashtag_cross_platform_boost(self):
        yt_tags = [{"hashtag": "#fitness", "score": 1000000}]
        tt_tags = [{"hashtag": "#fitness", "view_count": 1000000}]
        merged = ta.merge_hashtags(yt_tags, tt_tags)
        assert merged[0]["hashtag"] == "#fitness"

    def test_build_hashtag_sets(self):
        tags = [{"hashtag": f"#tag{i}", "cross_platform_score": 100 - i, "rank": i + 1} for i in range(40)]
        sets = ta.build_hashtag_sets(tags, niche="fitness")
        assert "broad" in sets
        assert "mid_tier" in sets
        assert "niche" in sets
        assert "recommended_mix" in sets
        assert "caption_ready" in sets
        assert len(sets["recommended_mix"]) == 15
        assert "#fitness" in sets["niche"]

    def test_score_content_idea_returns_dict(self):
        tags = [{"hashtag": "#money", "cross_platform_score": 90, "rank": 1}]
        topics = [{"topic": "money", "trend_score": 1000, "rank": 1}]
        result = ta.score_content_idea("5 money mistakes to avoid", tags, topics)
        assert "trend_score" in result
        assert "verdict" in result
        assert result["verdict"] in ("viral_potential", "moderate", "low")

    def test_score_range_is_0_to_100(self):
        result = ta.score_content_idea("random idea", [], [])
        assert 0 <= result["trend_score"] <= 100

    def test_identify_trend_topics_filters_stop_words(self):
        yt_videos = [
            {"title": "The best finance tips ever", "description": "These are the best money tips", "view_count": 1000},
        ]
        topics = ta.identify_trend_topics(yt_videos, [])
        topic_words = [t["topic"] for t in topics]
        assert "the" not in topic_words
        assert "best" not in topic_words or "finance" in topic_words or "money" in topic_words


# ─── Account Optimizer ────────────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_audit_returns_required_fields(self):
        result = ao.audit_account_profile(
            username="testuser",
            platform="tiktok",
            bio="Daily finance tips | Free guide below",
            follower_count=10000,
            following_count=500,
            post_count=50,
            avg_views=3000,
            avg_likes=400,
            avg_comments=30,
            niche="finance",
            profile_has_link=True,
        )
        assert "overall_score" in result
        assert "grade" in result
        assert "wins" in result
        assert "issues_to_fix" in result
        assert "priority_actions" in result
        assert 0 <= result["overall_score"] <= 100

    def test_audit_penalizes_no_link(self):
        with_link = ao.audit_account_profile(
            "u", "tiktok", "bio", 1000, 100, 20, 500, 50, 5, "fitness", profile_has_link=True
        )
        without_link = ao.audit_account_profile(
            "u", "tiktok", "bio", 1000, 100, 20, 500, 50, 5, "fitness", profile_has_link=False
        )
        assert with_link["overall_score"] > without_link["overall_score"]
        assert any("link" in issue.lower() for issue in without_link["issues_to_fix"])

    def test_audit_rewards_good_engagement(self):
        high_eng = ao.audit_account_profile(
            "u", "tiktok", "great bio here with cta", 10000, 200, 50, 5000, 800, 100, "fitness", True
        )
        low_eng = ao.audit_account_profile(
            "u", "tiktok", "great bio here with cta", 10000, 200, 50, 500, 10, 2, "fitness", True
        )
        assert high_eng["overall_score"] >= low_eng["overall_score"]

    def test_content_calendar_length(self):
        tags = [{"hashtag": f"#tag{i}", "cross_platform_score": 90 - i, "rank": i + 1} for i in range(20)]
        topics = [{"topic": f"topic{i}", "trend_score": 1000 - i * 10, "rank": i + 1} for i in range(10)]
        cal = ao.generate_content_calendar("tiktok", "fitness", tags, topics, days=7)
        assert len(cal) >= 7
        for entry in cal:
            assert "day" in entry
            assert "hook_idea" in entry
            assert "hashtags" in entry
            assert "cta" in entry

    def test_bio_templates_returns_three(self):
        templates = ao.generate_bio_templates("finance", "tiktok", "https://example.com")
        assert len(templates) == 3
        for t in templates:
            assert "example.com" in t


# ─── Theme Page ───────────────────────────────────────────────────────────────

class TestThemePage:
    def test_list_niches_sorted_by_trend(self):
        niches = tp.list_profitable_niches()
        assert len(niches) > 0
        scores = [n["trend_score"] for n in niches]
        assert scores == sorted(scores, reverse=True)

    def test_playbook_has_required_fields(self):
        playbook = tp.get_niche_playbook("finance")
        required = ["niche", "monetization_methods", "content_pillars", "viral_content_formats",
                    "conversion_funnel", "90_day_roadmap"]
        for field in required:
            assert field in playbook

    def test_playbook_90_day_roadmap_has_3_phases(self):
        playbook = tp.get_niche_playbook("fitness")
        assert len(playbook["90_day_roadmap"]) == 3

    def test_playbook_unknown_niche_falls_back(self):
        playbook = tp.get_niche_playbook("underwater basket weaving")
        assert "niche" in playbook
        assert len(playbook["monetization_methods"]) > 0

    def test_funnel_has_6_stages(self):
        funnel = tp.get_conversion_funnel()
        assert len(funnel) == 6
        stages = [f["stage"] for f in funnel]
        assert stages == list(range(1, 7))

    def test_mistakes_list_is_ranked(self):
        mistakes = tp.get_mistakes_to_avoid()
        ranks = [m["rank"] for m in mistakes]
        assert ranks == list(range(1, len(mistakes) + 1))


# ─── CLI Integration Tests ────────────────────────────────────────────────────

class TestCLIIntegration:
    def test_theme_niches_command(self, runner):
        result = runner.invoke(main, ["theme", "niches"])
        assert result.exit_code == 0
        assert "niche" in result.output.lower() or "trend" in result.output.lower()

    def test_theme_niches_json_output(self, runner):
        result = runner.invoke(main, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_theme_playbook_finance(self, runner):
        result = runner.invoke(main, ["theme", "playbook", "--niche", "finance"])
        assert result.exit_code == 0
        assert "finance" in result.output.lower()

    def test_theme_funnel_command(self, runner):
        result = runner.invoke(main, ["theme", "funnel"])
        assert result.exit_code == 0

    def test_theme_mistakes_command(self, runner):
        result = runner.invoke(main, ["theme", "mistakes"])
        assert result.exit_code == 0

    def test_account_bio_command(self, runner):
        result = runner.invoke(main, ["account", "bio", "--niche", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_account_schedule_tiktok(self, runner):
        result = runner.invoke(main, ["account", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0
        assert "Mon" in result.output or "monday" in result.output.lower()

    def test_help_command(self, runner):
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "youtube" in result.output.lower()
        assert "tiktok" in result.output.lower()
