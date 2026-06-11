"""Unit tests for account_optimizer.py."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from social_trends.agent_harness.utils.account_optimizer import (
    calculate_engagement_rate,
    engagement_health,
    project_growth,
    full_account_audit,
    monetization_readiness,
    OPTIMAL_TIMES,
)


# ---------------------------------------------------------------------------
# calculate_engagement_rate
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("followers,likes,comments,shares,expected", [
    (10_000, 500,  50,  20,  5.70),
    (1_000,  100,  10,  5,   11.50),
    (0,      100,  10,  5,   0.0),
    (50_000, 0,    0,   0,   0.0),
])
def test_calculate_engagement_rate(followers, likes, comments, shares, expected):
    assert calculate_engagement_rate(followers, likes, comments, shares) == pytest.approx(expected, abs=0.1)


# ---------------------------------------------------------------------------
# engagement_health
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rate,platform,expected_level", [
    (6.0, "tiktok",    "Excellent"),
    (3.5, "tiktok",    "Good"),
    (1.5, "tiktok",    "Average"),
    (0.3, "tiktok",    "Poor — action needed"),
    (4.5, "youtube",   "Excellent"),
    (7.0, "instagram", "Excellent"),
])
def test_engagement_health_levels(rate, platform, expected_level):
    result = engagement_health(rate, platform)
    assert result["level"] == expected_level


def test_engagement_health_contains_advice():
    result = engagement_health(0.2, "tiktok")
    assert len(result["advice"]) > 10


# ---------------------------------------------------------------------------
# project_growth
# ---------------------------------------------------------------------------

def test_project_growth_returns_correct_weeks():
    proj = project_growth(1_000, 200, weeks=4)
    assert len(proj) == 4


def test_project_growth_increases():
    proj = project_growth(1_000, 200, weeks=5)
    followers = [p["followers"] for p in proj]
    assert all(followers[i] < followers[i+1] for i in range(len(followers)-1))


def test_project_growth_starts_from_base():
    proj = project_growth(5_000, 300, weeks=3)
    assert proj[0]["followers"] == 5_300  # 5000 + 300 gain in week 1 (approx)


def test_project_growth_gain_positive():
    proj = project_growth(1_000, 100, weeks=6)
    assert all(p["gain"] > 0 for p in proj)


# ---------------------------------------------------------------------------
# full_account_audit
# ---------------------------------------------------------------------------

_STATS_HEALTHY = {
    "followers": 10_000,
    "following": 500,
    "avg_likes": 800,
    "avg_comments": 50,
    "avg_shares": 30,
    "avg_views": 20_000,
    "post_frequency": 5.0,
    "account_age_days": 180,
    "niche": "fitness",
}

def test_full_account_audit_returns_dict():
    audit = full_account_audit(_STATS_HEALTHY, "tiktok")
    assert isinstance(audit, dict)


def test_full_account_audit_has_required_keys():
    audit = full_account_audit(_STATS_HEALTHY, "tiktok")
    for key in ["platform", "phase", "overall_score", "engagement_rate",
                "ff_ratio", "priority_actions", "optimal_times"]:
        assert key in audit, f"Missing key: {key}"


def test_full_account_audit_phase_classification():
    audit_seed   = full_account_audit({**_STATS_HEALTHY, "followers": 500}, "tiktok")
    audit_rising = full_account_audit({**_STATS_HEALTHY, "followers": 50_000}, "tiktok")
    audit_mega   = full_account_audit({**_STATS_HEALTHY, "followers": 2_000_000}, "tiktok")

    assert audit_seed["phase"] == "seed"
    assert audit_rising["phase"] == "rising"
    assert audit_mega["phase"] == "mega"


def test_full_account_audit_score_range():
    audit = full_account_audit(_STATS_HEALTHY, "tiktok")
    assert 0 <= audit["overall_score"] <= 100


def test_full_account_audit_ff_ratio():
    stats = {**_STATS_HEALTHY, "followers": 1_000, "following": 2_000}
    audit = full_account_audit(stats, "tiktok")
    assert audit["ff_ratio"] == pytest.approx(0.5, abs=0.01)
    assert "unfollow" in audit["ff_advice"].lower()


def test_full_account_audit_low_engagement_adds_action():
    stats = {**_STATS_HEALTHY, "avg_likes": 10}
    audit = full_account_audit(stats, "tiktok")
    assert any("hook" in a.lower() for a in audit["priority_actions"])


def test_full_account_audit_optimal_times_present():
    audit = full_account_audit(_STATS_HEALTHY, "tiktok")
    assert len(audit["optimal_times"]) >= 1


# ---------------------------------------------------------------------------
# monetization_readiness
# ---------------------------------------------------------------------------

def test_monetization_readiness_returns_all_tiers():
    result = monetization_readiness(15_000, 4.0, "tiktok")
    expected_tiers = ["brand_deals", "affiliate_marketing",
                      "platform_monetization", "digital_products"]
    for tier in expected_tiers:
        assert tier in result


def test_monetization_readiness_brand_deals_ready():
    result = monetization_readiness(15_000, 4.0, "tiktok")
    assert result["brand_deals"]["ready"] is True


def test_monetization_readiness_brand_deals_not_ready():
    result = monetization_readiness(500, 1.0, "tiktok")
    assert result["brand_deals"]["ready"] is False


def test_monetization_readiness_progress_0_to_100():
    result = monetization_readiness(5_000, 2.0, "tiktok")
    for tier, info in result.items():
        assert 0 <= info["progress_pct"] <= 100


# ---------------------------------------------------------------------------
# OPTIMAL_TIMES
# ---------------------------------------------------------------------------

def test_optimal_times_all_platforms_present():
    for platform in ["tiktok", "youtube", "instagram"]:
        assert platform in OPTIMAL_TIMES
        assert len(OPTIMAL_TIMES[platform]) >= 3
