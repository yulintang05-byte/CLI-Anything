"""TrendScout core unit tests."""

import json
import os
import tempfile
import pytest

from cli_anything.trendscout.core import export as export_mod
from cli_anything.trendscout.core import trends as trends_mod
from cli_anything.trendscout.core import session as session_mod
from cli_anything.trendscout.core.youtube import extract_hashtags_from_videos
from cli_anything.trendscout.core.tiktok import (
    fetch_trending_hashtags,
    _virality_score,
    _estimate_tag_posts,
    _tag_use_advice,
    NICHE_HASHTAGS,
)


# ── session ────────────────────────────────────────────────────────────────────

def test_config_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(session_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(session_mod, "CONFIG_FILE", tmp_path / "config.json")
    monkeypatch.setattr(session_mod, "CACHE_DIR", tmp_path / "cache")
    (tmp_path / "cache").mkdir()

    session_mod.set_api_key("youtube", "test-key-abc")
    assert session_mod.get_api_key("youtube") == "test-key-abc"

    session_mod.set_config_value("region", "GB")
    assert session_mod.get_config_value("region") == "GB"


def test_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(session_mod, "CACHE_DIR", tmp_path)

    data = {"videos": [{"id": "abc", "title": "Test"}]}
    session_mod.set_cache("test_key", data)
    result = session_mod.get_cache("test_key")
    assert result == data


def test_cache_miss_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(session_mod, "CACHE_DIR", tmp_path)
    assert session_mod.get_cache("nonexistent") is None


def test_clear_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(session_mod, "CACHE_DIR", tmp_path)
    session_mod.set_cache("k1", {"a": 1})
    session_mod.set_cache("k2", {"b": 2})
    count = session_mod.clear_cache()
    assert count == 2
    assert session_mod.get_cache("k1") is None


# ── youtube ────────────────────────────────────────────────────────────────────

def _make_videos():
    return [
        {
            "id": "v1",
            "title": "Best Workout #fitness #gym",
            "description": "Daily workout tips #health",
            "tags": ["fitness", "gym", "workout", "health"],
            "view_count": 1_000_000,
            "like_count": 50_000,
            "comment_count": 2_000,
        },
        {
            "id": "v2",
            "title": "Cooking vlog #food #recipe",
            "description": "Try this recipe #cooking",
            "tags": ["food", "recipe", "cooking"],
            "view_count": 500_000,
            "like_count": 20_000,
            "comment_count": 800,
        },
    ]


def test_extract_hashtags():
    videos = _make_videos()
    result = extract_hashtags_from_videos(videos)
    hashtags = [h["hashtag"] for h in result]
    assert "#fitness" in hashtags or "#gym" in hashtags
    assert "#food" in hashtags or "#recipe" in hashtags
    assert all(h["count"] >= 1 for h in result)


def test_extract_hashtags_empty():
    result = extract_hashtags_from_videos([])
    assert result == []


def test_extract_hashtags_sorted():
    videos = _make_videos()
    result = extract_hashtags_from_videos(videos)
    counts = [h["count"] for h in result]
    assert counts == sorted(counts, reverse=True)


# ── tiktok ─────────────────────────────────────────────────────────────────────

def test_niche_hashtags_coverage():
    assert "fitness" in NICHE_HASHTAGS
    assert "food" in NICHE_HASHTAGS
    assert "gaming" in NICHE_HASHTAGS
    assert len(NICHE_HASHTAGS["fitness"]) >= 3


def test_fetch_trending_hashtags_general():
    tags = fetch_trending_hashtags(niche=None, limit=10)
    assert len(tags) <= 10
    assert all("hashtag" in t for t in tags)
    assert all("virality_score" in t for t in tags)


def test_fetch_trending_hashtags_niche():
    tags = fetch_trending_hashtags(niche="fitness", limit=5)
    assert len(tags) <= 5
    for t in tags:
        assert t["niche"] == "fitness"
        assert t["hashtag"].startswith("#")


def test_virality_score_range():
    assert 0 <= _virality_score("fyp", None) <= 100
    assert 0 <= _virality_score("unknowntag", "fitness") <= 100


def test_virality_fyp_highest():
    assert _virality_score("fyp", None) >= _virality_score("unknowntag", None)


def test_estimate_tag_posts():
    result = _estimate_tag_posts("fyp")
    assert result == "100B+"
    result2 = _estimate_tag_posts("fitness")
    assert "B" in result2


def test_tag_use_advice_known():
    advice = _tag_use_advice("fyp")
    assert len(advice) > 5


def test_tag_use_advice_unknown():
    advice = _tag_use_advice("randomtag123")
    assert len(advice) > 5


# ── trends aggregation ─────────────────────────────────────────────────────────

def _make_yt_data():
    return {
        "platform": "youtube",
        "videos": _make_videos(),
        "top_hashtags": [
            {"hashtag": "#fitness", "count": 3},
            {"hashtag": "#gym", "count": 2},
            {"hashtag": "#viral", "count": 1},
        ],
        "video_count": 2,
        "fetch_method": "test",
    }


def _make_tt_data():
    return {
        "platform": "tiktok",
        "videos": [
            {"description": "gym day", "hashtags": ["fitness", "fyp", "viral"], "view_count": 2000000},
        ],
        "top_hashtags": [
            {"hashtag": "#fitness", "count": 5},
            {"hashtag": "#fyp", "count": 10},
            {"hashtag": "#viral", "count": 4},
        ],
        "video_count": 1,
        "fetch_method": "test",
    }


def test_aggregate_both_platforms():
    result = trends_mod.aggregate(_make_yt_data(), _make_tt_data())
    assert "youtube" in result["platforms"]
    assert "tiktok" in result["platforms"]
    assert result["total_videos_analyzed"] == 3
    assert len(result["top_hashtags"]) > 0


def test_aggregate_crossplatform():
    result = trends_mod.aggregate(_make_yt_data(), _make_tt_data())
    cross_tags = {e["hashtag"] for e in result["crossplatform_trends"]}
    assert "#fitness" in cross_tags
    assert "#viral" in cross_tags


def test_aggregate_youtube_only():
    result = trends_mod.aggregate(_make_yt_data(), None)
    assert result["platforms"] == ["youtube"]
    assert result["crossplatform_trends"] == []


def test_aggregate_tiktok_only():
    result = trends_mod.aggregate(None, _make_tt_data())
    assert result["platforms"] == ["tiktok"]


def test_score_video_potential():
    v = {"view_count": 1_000_000, "like_count": 50_000, "comment_count": 2_000}
    score = trends_mod.score_video_potential(v)
    assert 0 <= score <= 100


def test_recommend_hashtags():
    recs = trends_mod.recommend_hashtags("fitness", "both", _make_yt_data(), _make_tt_data())
    assert len(recs) > 0
    types = {r["type"] for r in recs}
    assert "niche" in types or "trending" in types or "evergreen" in types
    for r in recs:
        assert r["hashtag"].startswith("#")


# ── export ─────────────────────────────────────────────────────────────────────

def test_export_json(tmp_path):
    data = {"test": True, "items": [1, 2, 3]}
    path = str(tmp_path / "out.json")
    result = export_mod.export_json(data, path)
    assert result == path
    loaded = json.loads(open(path).read())
    assert loaded == data


def test_export_csv(tmp_path):
    videos = _make_videos()
    path = str(tmp_path / "out.csv")
    result = export_mod.export_csv(videos, path)
    assert result == path
    content = open(path).read()
    assert "view_count" in content
    assert "v1" in content


def test_export_csv_empty():
    with pytest.raises(ValueError, match="No videos"):
        export_mod.export_csv([], "/tmp/trendscout_test_empty.csv")


def test_generate_report():
    agg = trends_mod.aggregate(_make_yt_data(), _make_tt_data())
    report = export_mod.generate_report(agg)
    assert "TrendScout Report" in report
    assert "Top Hashtags" in report
    assert "Cross-Platform" in report
    assert "Platform Summary" in report


def test_export_hashtags_csv(tmp_path):
    tags = fetch_trending_hashtags("fitness", 5)
    path = str(tmp_path / "tags.csv")
    result = export_mod.export_hashtags_csv(tags, path)
    assert result == path
    content = open(path).read()
    assert "hashtag" in content
