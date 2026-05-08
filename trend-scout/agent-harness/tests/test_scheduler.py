"""Tests for content scheduler."""

import pytest
from cli_anything.trend_scout.core.scheduler import ContentScheduler


@pytest.fixture
def scheduler():
    return ContentScheduler()


class TestWeeklyCalendar:
    def test_generates_7_days(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=1
        )
        assert len(calendar["calendar"]) == 7

    def test_each_day_has_posts(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=2
        )
        for date_str, day in calendar["calendar"].items():
            assert len(day["posts"]) >= 1

    def test_multi_platform_calendar(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok", "youtube", "instagram"], niche="food", posts_per_day=1
        )
        all_platforms = set()
        for day in calendar["calendar"].values():
            for post in day["posts"]:
                all_platforms.add(post["platform"])
        assert "tiktok" in all_platforms
        assert "youtube" in all_platforms
        assert "instagram" in all_platforms

    def test_total_posts_is_correct(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=2
        )
        counted = sum(len(v["posts"]) for v in calendar["calendar"].values())
        assert calendar["total_posts_planned"] == counted

    def test_posts_have_hashtags(self, scheduler):
        hashtags = [{"hashtag": "#fitness"}, {"hashtag": "#gym"}]
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=1,
            trending_hashtags=hashtags
        )
        for day in calendar["calendar"].values():
            for post in day["posts"]:
                if post["platform"] == "tiktok":
                    assert len(post["hashtags"]) > 0

    def test_has_batch_tip(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=2
        )
        assert "batch_recording_tip" in calendar
        assert len(calendar["batch_recording_tip"]) > 0

    def test_tiktok_posts_have_sound(self, scheduler):
        sounds = [{"title": "Trending Song"}, {"title": "Another Hit"}]
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="music", posts_per_day=1,
            trending_sounds=sounds
        )
        for day in calendar["calendar"].values():
            for post in day["posts"]:
                if post["platform"] == "tiktok":
                    assert post.get("suggested_sound") is not None


class TestMonthlyPlan:
    def test_has_4_weeks(self, scheduler):
        plan = scheduler.generate_monthly_plan(
            platforms=["tiktok"], niche="fashion", posts_per_week=10
        )
        assert len(plan["weekly_plans"]) == 4

    def test_total_posts_correct(self, scheduler):
        plan = scheduler.generate_monthly_plan(
            platforms=["tiktok"], niche="fashion", posts_per_week=14
        )
        assert plan["total_posts_target"] == 56

    def test_has_month_goals(self, scheduler):
        plan = scheduler.generate_monthly_plan(platforms=["tiktok"], niche="food", posts_per_week=10)
        assert "month_goals" in plan
        assert len(plan["month_goals"]) > 0

    def test_has_scheduling_tools(self, scheduler):
        plan = scheduler.generate_monthly_plan(platforms=["tiktok"], niche="food", posts_per_week=10)
        assert "tools_for_scheduling" in plan
        assert len(plan["tools_for_scheduling"]) >= 3


class TestFrequencyRecommendation:
    def test_nano_gets_high_frequency(self, scheduler):
        result = scheduler.get_posting_frequency_recommendation("tiktok", 100, "fitness")
        rec = result["recommendation"]
        assert "posts_per_day" in rec
        assert "3" in rec["posts_per_day"] or "4" in rec["posts_per_day"]

    def test_large_accounts_lower_frequency(self, scheduler):
        result = scheduler.get_posting_frequency_recommendation("tiktok", 500_000, "fitness")
        rec = result["recommendation"]
        assert "posts_per_day" in rec
        assert "1" in rec["posts_per_day"]

    def test_has_best_times(self, scheduler):
        result = scheduler.get_posting_frequency_recommendation("tiktok", 1000, "fitness")
        assert "best_times" in result

    def test_youtube_recommendation_differs(self, scheduler):
        result = scheduler.get_posting_frequency_recommendation("youtube", 1000, "gaming")
        rec = result["recommendation"]
        assert "posts_per_week" in rec


class TestExports:
    def test_csv_export_has_header(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=1
        )
        csv = scheduler.export_to_csv(calendar)
        assert csv.startswith("date,day,platform")

    def test_csv_has_data_rows(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="fitness", posts_per_day=1
        )
        csv = scheduler.export_to_csv(calendar)
        lines = csv.strip().split("\n")
        assert len(lines) > 1  # header + at least one row

    def test_notion_export_has_table(self, scheduler):
        calendar = scheduler.generate_weekly_calendar(
            platforms=["tiktok"], niche="food", posts_per_day=1
        )
        notion = scheduler.export_to_notion_format(calendar)
        assert "| Date |" in notion
        assert "|------|" in notion


class TestPostTimes:
    def test_tiktok_has_times(self, scheduler):
        times = scheduler._get_post_times("tiktok", "US", "Tuesday", 2)
        assert len(times) >= 1
        assert all("AM" in t or "PM" in t for t in times)

    def test_fallback_for_unknown_day(self, scheduler):
        times = scheduler._get_post_times("tiktok", "US", "Funday", 2)
        assert len(times) >= 1

    def test_respects_count(self, scheduler):
        times = scheduler._get_post_times("tiktok", "US", "Tuesday", 1)
        assert len(times) == 1

    def test_youtube_has_times(self, scheduler):
        times = scheduler._get_post_times("youtube", "US", "Thursday", 2)
        assert len(times) >= 1


class TestDailyTips:
    def test_all_days_have_tips(self, scheduler):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            tip = scheduler._daily_tip(day)
            assert len(tip) > 0

    def test_thursday_is_engagement_day(self, scheduler):
        tip = scheduler._daily_tip("Thursday")
        assert "Thursday" in tip or "engagement" in tip.lower()
