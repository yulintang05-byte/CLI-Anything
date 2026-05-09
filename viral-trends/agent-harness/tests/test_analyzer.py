"""Unit tests for the analyzer module (no network calls)."""
import pytest
from cli_anything.viral_trends import analyzer


YT_TAGS = [
    {"hashtag": "#fitness", "frequency": 5},
    {"hashtag": "#gym", "frequency": 3},
    {"hashtag": "#motivation", "frequency": 2},
    {"hashtag": "#workout", "frequency": 1},
]

TT_TAGS = [
    {"hashtag": "#fitness", "frequency": 8},
    {"hashtag": "#fyp", "frequency": 10},
    {"hashtag": "#gym", "frequency": 6},
    {"hashtag": "#gains", "frequency": 4},
]


def test_cross_platform_hashtags_merges_correctly():
    results = analyzer.cross_platform_hashtags(YT_TAGS, TT_TAGS, top_n=10)
    tags = [r["hashtag"] for r in results]
    assert "#fitness" in tags
    assert "#gym" in tags


def test_cross_platform_marks_cross_platform():
    results = analyzer.cross_platform_hashtags(YT_TAGS, TT_TAGS, top_n=10)
    by_tag = {r["hashtag"]: r for r in results}
    assert by_tag["#fitness"]["cross_platform"] is True
    assert by_tag["#fyp"]["cross_platform"] is False  # only on TikTok


def test_cross_platform_top_n_respected():
    results = analyzer.cross_platform_hashtags(YT_TAGS, TT_TAGS, top_n=3)
    assert len(results) <= 3


def test_score_weights():
    # TikTok freq=10, YT freq=0 → score = 10*0.6*10 = 60
    score = analyzer.score_hashtag("#fyp", yt_freq=0, tt_freq=10)
    assert score == 60.0


def test_niche_opportunity_tags():
    opps = analyzer.niche_opportunity_tags(YT_TAGS, TT_TAGS, max_yt_freq=2, min_tt_freq=4)
    opp_tags = [o["hashtag"] for o in opps]
    # #fyp: TT=10, YT=0 → qualifies; #gains: TT=4, YT=0 → qualifies
    assert "#fyp" in opp_tags
    assert "#gains" in opp_tags
    # #fitness: YT=5 > max_yt_freq=2 → should NOT appear
    assert "#fitness" not in opp_tags


def test_trending_music_report_tiers():
    sounds = [
        {"music": "Song A", "music_author": "Artist 1", "frequency": 6},
        {"music": "Song B", "music_author": "Artist 2", "frequency": 3},
        {"music": "Song C", "music_author": "Artist 3", "frequency": 1},
    ]
    report = analyzer.trending_music_report(sounds)
    tiers = {r["music"]: r["tier"] for r in report}
    assert tiers["Song A"] == "hot"
    assert tiers["Song B"] == "rising"
    assert tiers["Song C"] == "emerging"
