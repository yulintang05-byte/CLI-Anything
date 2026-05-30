"""Unit tests for Social Trends core logic — no network calls required."""

import pytest
from cli_anything.social_trends.core.trends import merge_platform_trends, _generate_insights
from cli_anything.social_trends.optimizer.account import (
    analyze_account, bulk_optimize, _score_account, _score_to_grade
)
from cli_anything.social_trends.theme_pages.niches import (
    get_niche, list_niches, search_niches
)
from cli_anything.social_trends.theme_pages.guide import (
    get_full_playbook, get_section, get_quick_start, get_conversion_guide
)
from cli_anything.social_trends.theme_pages.content_calendar import (
    generate_weekly_calendar, generate_monthly_calendar
)
from cli_anything.social_trends.utils.export import to_json, to_csv, to_markdown


# ============================================================================
# Trend merging
# ============================================================================

SAMPLE_YT = {
    "hashtags": [
        {"hashtag": "#fitness", "weighted_views": 500000},
        {"hashtag": "#gym", "weighted_views": 300000},
        {"hashtag": "#workout", "weighted_views": 200000},
    ],
    "music_tracks": [
        {"track": "Test Song", "artist": "Test Artist", "video_count": 3, "total_views": 100000},
    ],
    "videos": [
        {"title": "Video 1", "views": 100000, "channel": "Chan1", "hashtags": ["#fitness"]},
    ],
}

SAMPLE_TT = {
    "hashtags": [
        {"hashtag": "#fitness", "video_count": 50, "total_views": 800000, "score": 40000000},
        {"hashtag": "#fyp", "video_count": 200, "total_views": 5000000, "score": 1000000000},
        {"hashtag": "#gym", "video_count": 30, "total_views": 400000, "score": 12000000},
    ],
    "trending_sounds": [
        {"title": "Viral Sound", "artist": "DJ Test", "video_count": 100, "total_views": 2000000},
    ],
    "videos": [
        {"title": "TT Video 1", "views": 200000, "author": "creator1", "hashtags": ["#fitness", "#fyp"]},
    ],
}


def test_merge_platform_trends_both():
    report = merge_platform_trends(SAMPLE_YT, SAMPLE_TT, region="US")
    assert "youtube" in report.platforms
    assert "tiktok" in report.platforms
    assert len(report.top_hashtags) > 0
    assert len(report.top_music) > 0


def test_merge_cross_platform_identifies_shared_hashtags():
    report = merge_platform_trends(SAMPLE_YT, SAMPLE_TT, region="US")
    cross_tags = [h["hashtag"].lower() for h in report.cross_platform_hashtags]
    assert "#fitness" in cross_tags
    assert "#gym" in cross_tags


def test_merge_youtube_only():
    report = merge_platform_trends(SAMPLE_YT, None, region="US")
    assert "youtube" in report.platforms
    assert "tiktok" not in report.platforms
    assert len(report.top_hashtags) > 0


def test_merge_tiktok_only():
    report = merge_platform_trends(None, SAMPLE_TT, region="US")
    assert "tiktok" in report.platforms
    assert "youtube" not in report.platforms


def test_merge_insights_generated():
    report = merge_platform_trends(SAMPLE_YT, SAMPLE_TT)
    assert isinstance(report.insights, list)
    assert len(report.insights) > 0


def test_trend_report_to_dict():
    report = merge_platform_trends(SAMPLE_YT, SAMPLE_TT)
    d = report.to_dict()
    assert isinstance(d, dict)
    assert "top_hashtags" in d
    assert "insights" in d


# ============================================================================
# Account optimizer
# ============================================================================

SAMPLE_PROFILE_TIKTOK = {
    "platform": "tiktok",
    "username": "testaccount",
    "follower_count": 5000,
    "following_count": 500,
    "post_count": 100,
    "avg_views": 1000,
    "avg_likes": 80,
    "avg_comments": 10,
    "avg_shares": 5,
    "bio": "Daily fitness tips for busy people | Link below",
    "niche": "fitness",
    "posting_frequency_per_week": 3.0,
    "account_age_days": 180,
    "has_link_in_bio": True,
    "profile_pic_set": True,
    "recent_hashtags": ["#fitness", "#gym", "#workout"],
}

SAMPLE_PROFILE_NO_BIO = {
    "platform": "tiktok",
    "username": "newaccount",
    "follower_count": 100,
    "following_count": 800,
    "avg_views": 50,
    "avg_likes": 2,
    "avg_comments": 0,
    "avg_shares": 0,
    "bio": "",
    "niche": "",
    "posting_frequency_per_week": 0.5,
    "has_link_in_bio": False,
    "profile_pic_set": False,
    "recent_hashtags": [],
}


def test_analyze_account_returns_expected_keys():
    result = analyze_account(SAMPLE_PROFILE_TIKTOK)
    assert "overall_score" in result
    assert "grade" in result
    assert "category_scores" in result
    assert "recommendations" in result
    assert "action_plan" in result
    assert "optimal_posting_schedule" in result
    assert "hashtag_strategy" in result


def test_analyze_account_score_range():
    result = analyze_account(SAMPLE_PROFILE_TIKTOK)
    assert 0 <= result["overall_score"] <= 100


def test_analyze_account_grade_valid():
    result = analyze_account(SAMPLE_PROFILE_TIKTOK)
    assert result["grade"] in ["A+", "A", "B", "C", "D", "F"]


def test_score_to_grade():
    assert _score_to_grade(95) == "A+"
    assert _score_to_grade(85) == "A"
    assert _score_to_grade(75) == "B"
    assert _score_to_grade(65) == "C"
    assert _score_to_grade(55) == "D"
    assert _score_to_grade(30) == "F"


def test_weak_account_gets_critical_recommendations():
    result = analyze_account(SAMPLE_PROFILE_NO_BIO)
    priorities = [r["priority"] for r in result["recommendations"]]
    assert "CRITICAL" in priorities


def test_analyze_account_recommends_bio_fix():
    result = analyze_account(SAMPLE_PROFILE_NO_BIO)
    all_titles = [r["title"].lower() for r in result["recommendations"]]
    assert any("bio" in t for t in all_titles)


def test_bulk_optimize_sorted():
    accounts = [SAMPLE_PROFILE_TIKTOK, SAMPLE_PROFILE_NO_BIO]
    results = bulk_optimize(accounts)
    assert len(results) == 2
    # Sorted ascending by score — weakest first
    assert results[0]["overall_score"] <= results[1]["overall_score"]


def test_hashtag_stuffing_flagged():
    profile = {**SAMPLE_PROFILE_TIKTOK, "recent_hashtags": ["#a"] * 20}
    result = analyze_account(profile)
    all_titles = " ".join(r["title"].lower() for r in result["recommendations"])
    assert "hashtag" in all_titles


def test_action_plan_steps_numbered():
    result = analyze_account(SAMPLE_PROFILE_NO_BIO)
    for i, step in enumerate(result["action_plan"], 1):
        assert step["step"] == i


# ============================================================================
# Niche database
# ============================================================================

def test_get_niche_known():
    niche = get_niche("finance_investing")
    assert niche is not None
    assert niche["name"] == "Finance & Investing"
    assert "monetization" in niche
    assert "avg_cpm_usd" in niche


def test_get_niche_unknown():
    assert get_niche("nonexistent_niche_xyz") is None


def test_list_niches_returns_all():
    niches = list_niches()
    assert len(niches) >= 8


def test_list_niches_sorted_by_cpm():
    niches = list_niches(sort_by="avg_cpm_usd")
    cpms = [n["avg_cpm_usd"] for n in niches]
    assert cpms == sorted(cpms, reverse=True)


def test_list_niches_filter_by_platform():
    niches = list_niches(platform="youtube")
    for n in niches:
        assert "youtube" in [p.lower() for p in n.get("best_platforms", [])]


def test_list_niches_max_competition_filter():
    niches = list_niches(min_competition="medium")
    competition_rank = {"low": 0, "medium": 1, "high": 2, "very_high": 3}
    for n in niches:
        assert competition_rank.get(n.get("competition", "high"), 2) <= 1


def test_search_niches():
    results = search_niches("luxury")
    assert len(results) > 0
    assert any("luxury" in r["name"].lower() for r in results)


def test_search_niches_no_match():
    results = search_niches("zzznothingmatches999")
    assert results == []


# ============================================================================
# Theme page guide
# ============================================================================

def test_get_full_playbook_has_sections():
    playbook = get_full_playbook()
    assert "sections" in playbook
    assert "phase_1_setup" in playbook
    assert "phase_3_monetization" in playbook
    assert "common_mistakes" in playbook


def test_get_section_exists():
    section = get_section("phase_1_setup")
    assert section is not None
    assert "steps" in section


def test_get_section_not_found():
    assert get_section("nonexistent_section") is None


def test_get_quick_start():
    qs = get_quick_start("fitness")
    assert "week_1" in qs
    assert "week_2_4" in qs
    assert "key_metrics_to_track" in qs
    assert qs["niche"] == "fitness"


def test_get_conversion_guide_phases():
    assert get_conversion_guide(500, "tiktok")["phase"] == "building_trust"
    assert get_conversion_guide(5000, "tiktok")["phase"] == "early_monetization"
    assert get_conversion_guide(50000, "tiktok")["phase"] == "scaling_revenue"
    assert get_conversion_guide(500000, "tiktok")["phase"] == "business_operations"


# ============================================================================
# Content calendar
# ============================================================================

def test_weekly_calendar_structure():
    cal = generate_weekly_calendar(niche="fitness_motivation", platforms=["tiktok"])
    assert "calendar" in cal
    assert len(cal["calendar"]) == 7
    assert cal["total_posts"] == 7 * 2  # default 2 posts/day


def test_weekly_calendar_posts_per_day():
    cal = generate_weekly_calendar(posts_per_day=3, platforms=["tiktok"])
    assert cal["total_posts"] == 7 * 3


def test_monthly_calendar_has_4_weeks():
    cal = generate_monthly_calendar(niche="food_recipes", platforms=["tiktok", "youtube"])
    assert "weeks" in cal
    assert len(cal["weeks"]) == 4


def test_calendar_posts_have_required_fields():
    cal = generate_weekly_calendar(platforms=["tiktok"])
    for day in cal["calendar"]:
        for post in day["posts"]:
            assert "platform" in post
            assert "time_utc" in post
            assert "hook_template" in post
            assert "format" in post


def test_calendar_respects_platform_list():
    cal = generate_weekly_calendar(platforms=["tiktok"])
    for day in cal["calendar"]:
        for post in day["posts"]:
            assert post["platform"] == "tiktok"


def test_calendar_start_date():
    cal = generate_weekly_calendar(start_date="2025-01-01", platforms=["tiktok"])
    assert cal["start_date"] == "2025-01-01"
    assert cal["end_date"] == "2025-01-07"


# ============================================================================
# Export utilities
# ============================================================================

def test_to_json_serializes():
    data = {"key": "value", "num": 42, "list": [1, 2, 3]}
    result = to_json(data)
    import json
    parsed = json.loads(result)
    assert parsed == data


def test_to_csv_basic():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    result = to_csv(data)
    assert "a,b" in result
    assert "1,2" in result


def test_to_csv_empty():
    assert to_csv([]) == ""


def test_to_markdown_generates_headers():
    data = {"title": "Test Report", "top_hashtags": [{"hashtag": "#test", "score": 100}]}
    result = to_markdown(data, "Test Report")
    assert "# Test Report" in result
    assert "Top Hashtags" in result


def test_to_markdown_string():
    result = to_markdown({"info": "hello world"})
    assert isinstance(result, str)
    assert len(result) > 0
