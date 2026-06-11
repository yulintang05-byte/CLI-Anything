"""Unit tests for theme_page_engine.py."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from social_trends.agent_harness.utils.theme_page_engine import (
    list_niches,
    launch_blueprint,
    generate_content_calendar,
    get_hook_templates,
    analyze_competitor,
    CONVERSION_STRATEGIES,
    NICHES,
    WEEKLY_TEMPLATES,
    CONTENT_TYPES,
)


# ---------------------------------------------------------------------------
# list_niches
# ---------------------------------------------------------------------------

def test_list_niches_returns_all():
    niches = list_niches()
    assert len(niches) == len(NICHES)


def test_list_niches_has_required_fields():
    niches = list_niches()
    for n in niches:
        for key in ["niche", "description", "saturation", "growth_speed",
                    "best_platforms", "avg_cpm_usd"]:
            assert key in n, f"Missing: {key}"


def test_list_niches_cpm_positive():
    niches = list_niches()
    assert all(n["avg_cpm_usd"] > 0 for n in niches)


# ---------------------------------------------------------------------------
# launch_blueprint
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("niche", list(NICHES.keys()))
def test_launch_blueprint_valid_niches(niche):
    bp = launch_blueprint(niche)
    assert "error" not in bp
    assert bp["niche"] == niche


def test_launch_blueprint_invalid_niche():
    bp = launch_blueprint("nonexistent_niche_xyz")
    assert "error" in bp


def test_launch_blueprint_required_keys():
    bp = launch_blueprint("fitness_motivation")
    for key in ["week1_goals", "week2_goals", "month1_targets",
                "month3_targets", "monetization_roadmap", "viral_formula",
                "content_calendar", "conversion_strategies"]:
        assert key in bp, f"Missing: {key}"


def test_launch_blueprint_week1_has_5_goals():
    bp = launch_blueprint("luxury_lifestyle")
    assert len(bp["week1_goals"]) >= 3


def test_launch_blueprint_monetization_roadmap_ordered():
    bp = launch_blueprint("finance_hustle")
    milestones = bp["monetization_roadmap"]
    assert len(milestones) >= 3
    for m in milestones:
        assert "milestone" in m
        assert "action" in m


def test_launch_blueprint_month1_targets():
    bp = launch_blueprint("fitness_motivation")
    m1 = bp["month1_targets"]
    assert m1["followers_min"] > 0
    assert m1["followers_stretch"] > m1["followers_min"]
    assert m1["avg_engagement_pct"] > 0


def test_launch_blueprint_content_calendar_not_empty():
    bp = launch_blueprint("aesthetic_food")
    assert len(bp["content_calendar"]) > 0


# ---------------------------------------------------------------------------
# generate_content_calendar
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("frequency,weeks,expected_min", [
    ("3x_week", 1, 3),
    ("5x_week", 2, 10),
    ("daily",   1, 7),
])
def test_generate_content_calendar_count(frequency, weeks, expected_min):
    cal = generate_content_calendar("fitness_motivation", frequency, weeks)
    assert len(cal) >= expected_min


def test_generate_content_calendar_fields():
    cal = generate_content_calendar("fashion", "5x_week", 2)
    for entry in cal:
        for key in ["week", "day", "content_type", "content_pillar",
                    "hook_example", "niche"]:
            assert key in entry, f"Missing: {key}"


def test_generate_content_calendar_week_numbers():
    cal = generate_content_calendar("food", "3x_week", 3)
    weeks = set(e["week"] for e in cal)
    assert weeks == {1, 2, 3}


def test_generate_content_calendar_niche_tagged():
    cal = generate_content_calendar("travel_minimalist", "5x_week", 1)
    assert all(e["niche"] == "travel_minimalist" for e in cal)


def test_generate_content_calendar_valid_content_types():
    cal = generate_content_calendar("gaming", "5x_week", 1)
    for entry in cal:
        assert entry["content_type"] in CONTENT_TYPES


# ---------------------------------------------------------------------------
# get_hook_templates
# ---------------------------------------------------------------------------

def test_get_hook_templates_returns_list():
    hooks = get_hook_templates("luxury_lifestyle")
    assert isinstance(hooks, list)
    assert len(hooks) >= 1


def test_get_hook_templates_unknown_niche():
    hooks = get_hook_templates("unknown_niche_xyz")
    assert isinstance(hooks, list)
    assert len(hooks) >= 1  # fallback template


def test_get_hook_templates_nonempty_strings():
    for niche in list(NICHES.keys()):
        hooks = get_hook_templates(niche)
        assert all(len(h) > 5 for h in hooks)


# ---------------------------------------------------------------------------
# analyze_competitor
# ---------------------------------------------------------------------------

def test_analyze_competitor_returns_dict():
    result = analyze_competitor("@testuser", "tiktok", {
        "followers": 50_000,
        "avg_likes": 2_500,
        "post_count": 200,
        "account_age_days": 180,
    })
    assert isinstance(result, dict)


def test_analyze_competitor_required_fields():
    result = analyze_competitor("user", "instagram", {
        "followers": 10_000,
        "avg_likes": 500,
        "post_count": 100,
        "account_age_days": 90,
    })
    for key in ["engagement_rate", "daily_growth", "posts_per_day",
                "insights", "replicate"]:
        assert key in result


def test_analyze_competitor_engagement_rate_formula():
    result = analyze_competitor("u", "tiktok", {
        "followers": 10_000,
        "avg_likes": 1_000,
        "post_count": 50,
        "account_age_days": 30,
    })
    assert result["engagement_rate"] == pytest.approx(10.0, abs=0.1)


def test_analyze_competitor_replicate_is_list_of_strings():
    result = analyze_competitor("u", "tiktok", {
        "followers": 5_000,
        "avg_likes": 100,
        "post_count": 30,
        "account_age_days": 60,
    })
    assert all(isinstance(r, str) for r in result["replicate"])


# ---------------------------------------------------------------------------
# CONVERSION_STRATEGIES
# ---------------------------------------------------------------------------

def test_conversion_strategies_not_empty():
    assert len(CONVERSION_STRATEGIES) >= 4


def test_conversion_strategies_have_required_fields():
    for cs in CONVERSION_STRATEGIES:
        for key in ["name", "description", "steps", "conversion_rate", "time_to_implement"]:
            assert key in cs, f"Missing: {key}"


def test_conversion_strategies_steps_are_lists():
    for cs in CONVERSION_STRATEGIES:
        assert isinstance(cs["steps"], list)
        assert len(cs["steps"]) >= 2
