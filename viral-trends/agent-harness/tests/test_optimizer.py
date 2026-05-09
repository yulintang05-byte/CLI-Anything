"""Unit tests for the optimizer module (no network calls)."""
import pytest
from cli_anything.viral_trends import optimizer


TRENDING_TAGS = [
    {"hashtag": "#fitness", "yt_frequency": 5, "tt_frequency": 8, "score": 80, "cross_platform": True},
    {"hashtag": "#fyp",     "yt_frequency": 0, "tt_frequency": 10, "score": 60, "cross_platform": False},
    {"hashtag": "#gym",     "yt_frequency": 3, "tt_frequency": 6,  "score": 48, "cross_platform": True},
    {"hashtag": "#gains",   "yt_frequency": 0, "tt_frequency": 4,  "score": 24, "cross_platform": False},
    {"hashtag": "#workout", "yt_frequency": 1, "tt_frequency": 2,  "score": 16, "cross_platform": True},
]


def test_posting_schedule_returns_windows():
    sched = optimizer.posting_schedule("tiktok")
    assert "optimal_windows_utc" in sched
    assert len(sched["optimal_windows_utc"]) > 0


def test_posting_schedule_unknown_platform():
    sched = optimizer.posting_schedule("twitter")
    assert "optimal_windows_utc" in sched


def test_hashtag_strategy_respects_max():
    strat = optimizer.hashtag_strategy("tiktok", TRENDING_TAGS)
    cfg = {"tiktok": 5}
    assert len(strat["hashtags"]) <= cfg["tiktok"]


def test_hashtag_strategy_prioritizes_cross_platform():
    strat = optimizer.hashtag_strategy("tiktok", TRENDING_TAGS)
    # #fitness and #gym are cross-platform and should appear
    tags = strat["hashtags"]
    assert "#fitness" in tags
    assert "#gym" in tags


def test_hashtag_strategy_includes_niche_tags():
    strat = optimizer.hashtag_strategy("tiktok", TRENDING_TAGS, niche_tags=["mygym"])
    assert "#mygym" in strat["hashtags"]


def test_content_pillars_sums_to_100():
    pillars = optimizer.content_pillars("finance")["pillars"]
    total = sum(int(p["share"].rstrip("%")) for p in pillars)
    assert total == 100


def test_bio_optimization_has_cta():
    bio = optimizer.bio_optimization("tiktok", "fitness", cta="free plan below")
    assert "free plan below" in bio["bio_template"]


def test_full_account_audit_keys():
    report = optimizer.full_account_audit("tiktok", "fitness", TRENDING_TAGS)
    for key in ("posting_schedule", "hashtag_strategy", "content_pillars", "bio_optimization"):
        assert key in report


def test_tiktok_hashtag_caption_placement():
    strat = optimizer.hashtag_strategy("tiktok", TRENDING_TAGS)
    assert "caption" in strat["caption_placement"].lower()


def test_instagram_hashtag_caption_placement():
    strat = optimizer.hashtag_strategy("instagram", TRENDING_TAGS)
    assert "comment" in strat["caption_placement"].lower()
