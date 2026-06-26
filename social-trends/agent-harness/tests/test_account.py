"""Tests for account optimization module."""

import pytest
from cli_anything.social_trends.core.account import (
    get_best_posting_times,
    audit_account,
    generate_growth_roadmap,
    cross_platform_strategy,
    _BEST_TIMES,
    _PLATFORM_SPECS,
)


class TestGetBestPostingTimes:
    def test_tiktok_returns_schedule(self):
        data = get_best_posting_times("tiktok")
        assert "full_schedule" in data
        assert len(data["full_schedule"]) == 7  # 7 days

    def test_instagram_returns_schedule(self):
        data = get_best_posting_times("instagram")
        assert data["platform"] == "instagram"
        assert "top_5_slots" in data

    def test_youtube_schedule_has_all_days(self):
        data = get_best_posting_times("youtube")
        days = [s["day"] for s in data["full_schedule"]]
        assert "Saturday" in days
        assert "Sunday" in days

    def test_invalid_platform_raises(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            get_best_posting_times("myspace")

    def test_timezone_in_output(self):
        data = get_best_posting_times("tiktok", timezone="EST")
        assert "EST" in data["timezone_note"]

    def test_frequency_recommendation_present(self):
        data = get_best_posting_times("tiktok")
        assert data["weekly_frequency_recommendation"] != ""

    def test_all_platforms_have_data(self):
        for platform in _BEST_TIMES:
            data = get_best_posting_times(platform)
            assert len(data["full_schedule"]) > 0


class TestAuditAccount:
    def test_perfect_account_high_score(self):
        result = audit_account(
            platform="tiktok",
            handle="testuser",
            bio="Daily fitness tips for busy moms | Click link 👇",
            follower_count=10000,
            following_count=500,
            post_count=100,
            has_link=True,
            posting_frequency_per_week=5,
            avg_views=5000,
            avg_likes=500,
        )
        assert result["score"] >= 80
        assert result["grade"] in ("A", "B")

    def test_missing_profile_picture_penalized(self):
        result = audit_account(
            platform="instagram",
            handle="testuser",
            has_profile_picture=False,
        )
        assert result["score"] <= 85
        assert any("profile picture" in issue.lower() for issue in result["issues"])

    def test_no_bio_flagged(self):
        result = audit_account(platform="tiktok", handle="testuser")
        assert any("bio" in issue.lower() for issue in result["issues"])

    def test_no_link_flagged_for_relevant_platforms(self):
        result = audit_account(
            platform="instagram",
            handle="testuser",
            bio="Fitness page",
            has_link=False,
        )
        assert any("link" in issue.lower() for issue in result["issues"])

    def test_low_posting_frequency_flagged(self):
        result = audit_account(
            platform="tiktok",
            handle="testuser",
            posting_frequency_per_week=0.5,
        )
        assert any("posting" in issue.lower() or "frequency" in issue.lower() for issue in result["issues"])

    def test_low_engagement_rate_flagged(self):
        result = audit_account(
            platform="instagram",
            handle="testuser",
            follower_count=100000,
            avg_likes=200,
        )
        assert any("engagement" in issue.lower() for issue in result["issues"])

    def test_good_engagement_in_wins(self):
        result = audit_account(
            platform="tiktok",
            handle="testuser",
            follower_count=1000,
            avg_likes=50,  # 5% engagement
        )
        assert any("engagement" in w.lower() for w in result["wins"])

    def test_grade_bc_for_minimal_account(self):
        # bio missing (-10), no link (-10), posting unknown (-5) = score 75 = B
        result = audit_account(platform="tiktok", handle="empty")
        assert result["grade"] in ("B", "C", "D")

    def test_next_actions_max_3(self):
        result = audit_account(platform="tiktok", handle="testuser")
        assert len(result["next_actions"]) <= 3

    def test_platform_specs_included(self):
        result = audit_account(platform="tiktok", handle="testuser")
        assert "platform_specs" in result
        assert result["platform_specs"]["aspect_ratio"] == "9:16 (1080x1920)"


class TestGenerateGrowthRoadmap:
    def test_basic_roadmap_structure(self):
        result = generate_growth_roadmap("tiktok", 0, 10000, "fitness", 90)
        assert "roadmap" in result
        assert len(result["roadmap"]) == 3

    def test_three_phases(self):
        result = generate_growth_roadmap("instagram", 500, 5000, "food", 90)
        phases = [p["phase"] for p in result["roadmap"]]
        assert phases == [1, 2, 3]

    def test_phase_titles_present(self):
        result = generate_growth_roadmap("youtube", 0, 50000, "gaming", 90)
        titles = [p["focus"] for p in result["roadmap"]]
        assert "Foundation" in titles
        assert "Acceleration" in titles

    def test_already_at_target(self):
        result = generate_growth_roadmap("tiktok", 10000, 5000, "fitness", 90)
        assert result["status"] == "already_at_target"

    def test_gap_calculated(self):
        result = generate_growth_roadmap("tiktok", 1000, 10000, "fitness", 90)
        assert result["gap"] == 9000

    def test_daily_growth_needed(self):
        result = generate_growth_roadmap("tiktok", 0, 9000, "fitness", 90)
        assert result["daily_growth_needed"] == 100

    def test_platform_specs_referenced(self):
        result = generate_growth_roadmap("tiktok", 0, 1000, "travel", 90)
        assert result["content_types"] != []

    def test_hook_window_tiktok(self):
        result = generate_growth_roadmap("tiktok", 0, 1000, "fitness", 30)
        assert "3 seconds" in result["hook_window"]


class TestCrossPlatformStrategy:
    def test_basic_strategy(self):
        result = cross_platform_strategy(["tiktok", "instagram", "youtube"], "fitness", "tiktok")
        assert result["primary_platform"] == "tiktok"
        assert len(result["secondary_platforms"]) == 2

    def test_repurpose_plan_present(self):
        result = cross_platform_strategy(["tiktok", "instagram"], "food", "tiktok")
        assert len(result["repurpose_plan"]) >= 1

    def test_tools_listed(self):
        result = cross_platform_strategy(["tiktok", "instagram"], "gaming", "tiktok")
        assert isinstance(result["tools"], list)
        assert len(result["tools"]) > 0

    def test_weekly_schedule_has_7_days(self):
        result = cross_platform_strategy(["tiktok", "instagram"], "motivation", "tiktok")
        schedule = result["weekly_schedule"]
        assert "Monday" in schedule
        assert "Sunday" in schedule
        assert len(schedule) == 7

    def test_posting_order_mentions_primary(self):
        result = cross_platform_strategy(["tiktok", "instagram"], "travel", "instagram")
        assert "instagram" in result["posting_order"].lower()

    def test_single_platform_no_secondary(self):
        result = cross_platform_strategy(["tiktok"], "fitness", "tiktok")
        assert result["secondary_platforms"] == []
