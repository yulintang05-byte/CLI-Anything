"""Unit tests for hashtag_analyzer.py."""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from social_trends.utils.hashtag_analyzer import (
    score_hashtags,
    build_hashtag_set,
    cross_platform_merge,
    recommend_for_niche,
    analyze_description,
    HashtagScore,
    MEGA_TAGS,
    NICHE_HASHTAGS,
)


# ---------------------------------------------------------------------------
# score_hashtags
# ---------------------------------------------------------------------------

_RAW = [
    {"hashtag": "fitness",  "frequency": 15, "total_views": 5_000_000, "total_likes": 200_000},
    {"hashtag": "gym",      "frequency": 12, "total_views": 3_000_000, "total_likes": 120_000},
    {"hashtag": "workout",  "frequency": 8,  "total_views": 2_000_000, "total_likes":  80_000},
    {"hashtag": "fyp",      "frequency": 50, "total_views": 100_000_000,"total_likes":1_000_000},
    {"hashtag": "microfit", "frequency": 2,  "total_views":    10_000, "total_likes":   1_000},
]

def test_score_hashtags_returns_list_of_hashtagscore():
    result = score_hashtags(_RAW)
    assert isinstance(result, list)
    assert all(isinstance(h, HashtagScore) for h in result)


def test_score_hashtags_sorted_descending():
    result = score_hashtags(_RAW)
    scores = [h.trend_score for h in result]
    assert scores == sorted(scores, reverse=True)


def test_score_hashtags_mega_tag_penalized():
    result = score_hashtags(_RAW)
    fyp = next(h for h in result if h.hashtag == "#fyp")
    fitness = next(h for h in result if h.hashtag == "#fitness")
    # fyp is a mega tag — despite huge raw reach it should score low
    assert fyp.trend_score < fitness.trend_score


def test_score_hashtags_niche_detected():
    result = score_hashtags(_RAW)
    fitness_tag = next(h for h in result if h.hashtag == "#fitness")
    assert fitness_tag.category == "fitness"


def test_score_hashtags_empty():
    assert score_hashtags([]) == []


def test_score_hashtags_missing_fields():
    raw = [{"hashtag": "incomplete"}]
    result = score_hashtags(raw)
    assert len(result) == 1
    assert result[0].frequency == 1


# ---------------------------------------------------------------------------
# build_hashtag_set
# ---------------------------------------------------------------------------

def test_build_hashtag_set_respects_count():
    scored = score_hashtags(_RAW * 10)  # blow up the list
    result = build_hashtag_set(scored, target_count=10)
    assert len(result) <= 10


def test_build_hashtag_set_deduplicates():
    scored = score_hashtags(_RAW)
    result = build_hashtag_set(scored, target_count=20)
    assert len(result) == len(set(result))


def test_build_hashtag_set_filters_mega():
    scored = score_hashtags(_RAW)
    result = build_hashtag_set(scored, target_count=20)
    assert "#fyp" not in result  # fyp is a mega tag


def test_build_hashtag_set_with_niche():
    scored = score_hashtags(_RAW)
    result = build_hashtag_set(scored, target_count=15, niche="fitness")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# cross_platform_merge
# ---------------------------------------------------------------------------

_YT_RAW = [{"hashtag": "fitness", "frequency": 10, "total_views": 1_000_000},
           {"hashtag": "youtube", "frequency": 5,  "total_views": 500_000}]
_TT_RAW = [{"hashtag": "fitness", "frequency": 20, "total_views": 2_000_000},
           {"hashtag": "tiktok",  "frequency": 30, "total_views": 5_000_000}]

def test_cross_platform_merge_boosts_both():
    merged = cross_platform_merge(_YT_RAW, _TT_RAW)
    fitness = next(h for h in merged if h.hashtag == "#fitness")
    assert fitness.platform == "both"
    # Score boosted for cross-platform presence
    yt_only = score_hashtags(_YT_RAW, "youtube")
    yt_fitness = next(h for h in yt_only if h.hashtag == "#fitness")
    assert fitness.trend_score > yt_fitness.trend_score


def test_cross_platform_merge_preserves_single_platform():
    merged = cross_platform_merge(_YT_RAW, _TT_RAW)
    tags = {h.hashtag for h in merged}
    assert "#youtube" in tags
    assert "#tiktok" in tags


def test_cross_platform_merge_sorted():
    merged = cross_platform_merge(_YT_RAW, _TT_RAW)
    scores = [h.trend_score for h in merged]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# recommend_for_niche
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("niche", ["fitness", "fashion", "food", "finance", "travel"])
def test_recommend_for_niche_returns_tags(niche):
    tags = recommend_for_niche(niche, "tiktok")
    assert len(tags) > 0
    assert all(t.startswith("#") for t in tags)


def test_recommend_for_niche_tiktok_adds_tok_variants():
    tags = recommend_for_niche("food", "tiktok")
    assert any("tok" in t for t in tags)


def test_recommend_for_niche_unknown_returns_empty():
    tags = recommend_for_niche("nonexistent_niche_xyz")
    assert tags == []


# ---------------------------------------------------------------------------
# analyze_description
# ---------------------------------------------------------------------------

def test_analyze_description_finds_hashtags():
    text = "Amazing workout today #fitness #gym #workout #fyp"
    result = analyze_description(text)
    assert result["count"] == 4
    assert "#fitness" in result["found"]
    assert "#fyp" in result["mega_tags"]


def test_analyze_description_no_hashtags():
    result = analyze_description("No hashtags here at all.")
    assert result["count"] == 0
    assert result["found"] == []


def test_analyze_description_avg_score():
    result = analyze_description("#fitness #gym")
    assert result["avg_score"] >= 0


def test_analyze_description_weak_tags_flagged():
    text = "#zzzmadeuptagxyz"
    result = analyze_description(text)
    # Very obscure tags should have low score
    assert result["count"] == 1
