"""Unit tests for cli-anything-trends core modules."""

import json
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.trends.utils.youtube_backend import (
    extract_hashtags_from_text,
    aggregate_hashtags,
    aggregate_music_trends,
    CATEGORY_IDS,
    REGION_CODES,
)
from cli_anything.trends.utils.tiktok_backend import (
    _extract_hashtags_from_desc,
    _aggregate_hashtags_from_videos,
    _walk_for_trending,
)
from cli_anything.trends.core.analyzer import (
    merge_hashtags,
    merge_videos,
    extract_trending_topics,
    identify_content_themes,
    build_trend_report,
)
from cli_anything.trends.core.optimizer import (
    generate_hashtag_pack,
    generate_content_calendar,
    generate_account_optimization,
    _determine_growth_phase,
)
from cli_anything.trends.utils.config import (
    load_config,
    save_config,
    _parse_cookie_string,
)
from cli_anything.trends.core.session import Session


# ── YouTube backend tests ─────────────────────────────────────────────────


class TestYouTubeBackend:
    def test_extract_hashtags_from_text_basic(self):
        text = "Check out #fitness and #workout tips! #healthylife"
        result = extract_hashtags_from_text(text)
        assert "#fitness" in result
        assert "#workout" in result
        assert "#healthylife" in result

    def test_extract_hashtags_from_text_empty(self):
        assert extract_hashtags_from_text("") == []

    def test_extract_hashtags_from_text_no_hashtags(self):
        assert extract_hashtags_from_text("No hashtags here") == []

    def test_extract_hashtags_lowercase(self):
        result = extract_hashtags_from_text("#FitnessGoals #WorkOut")
        assert all(h == h.lower() for h in result)

    def test_aggregate_hashtags_empty(self):
        assert aggregate_hashtags([]) == []

    def test_aggregate_hashtags_scoring(self):
        videos = [
            {"views": 1_000_000, "likes": 50_000, "hashtags": ["#viral", "#fitness"]},
            {"views": 500_000, "likes": 20_000, "hashtags": ["#viral", "#gym"]},
            {"views": 200_000, "likes": 10_000, "hashtags": ["#fitness"]},
        ]
        result = aggregate_hashtags(videos)
        assert len(result) > 0
        # #viral appears in 2 videos so should score higher
        tag_names = [r["hashtag"] for r in result]
        assert "#viral" in tag_names
        viral_entry = next(r for r in result if r["hashtag"] == "#viral")
        assert viral_entry["video_count"] == 2

    def test_aggregate_hashtags_sorted(self):
        videos = [
            {"views": 1_000_000, "likes": 100_000, "hashtags": ["#big"]},
            {"views": 100, "likes": 10, "hashtags": ["#small"]},
        ]
        result = aggregate_hashtags(videos)
        assert result[0]["hashtag"] == "#big"

    def test_aggregate_music_trends_basic(self):
        videos = [
            {"channel": "ArtistA", "views": 5_000_000, "title": "Hit Song"},
            {"channel": "ArtistA", "views": 3_000_000, "title": "Another Hit"},
            {"channel": "ArtistB", "views": 1_000_000, "title": "New Song"},
        ]
        result = aggregate_music_trends(videos)
        assert result[0]["artist"] == "ArtistA"
        assert result[0]["video_count"] == 2
        assert result[0]["total_views"] == 8_000_000

    def test_category_ids_has_music(self):
        assert "music" in CATEGORY_IDS
        assert CATEGORY_IDS["music"] == "10"

    def test_region_codes_has_us(self):
        assert "us" in REGION_CODES
        assert REGION_CODES["us"] == "US"


# ── TikTok backend tests ──────────────────────────────────────────────────


class TestTikTokBackend:
    def test_extract_hashtags_from_desc(self):
        desc = "Check this out #fyp #viral #fitness"
        result = _extract_hashtags_from_desc(desc)
        assert "#fyp" in result
        assert "#viral" in result
        assert "#fitness" in result

    def test_extract_hashtags_empty(self):
        assert _extract_hashtags_from_desc("") == []

    def test_aggregate_hashtags_from_videos(self):
        videos = [
            {"views": 100_000, "likes": 5_000, "hashtags": ["#fyp", "#trend"]},
            {"views": 50_000, "likes": 2_000, "hashtags": ["#fyp"]},
        ]
        result = _aggregate_hashtags_from_videos(videos)
        assert len(result) > 0
        fyp = next((r for r in result if r["hashtag"] == "#fyp"), None)
        assert fyp is not None
        assert fyp["video_count"] == 2

    def test_walk_for_trending_finds_hashtags(self):
        data = {
            "some_key": {
                "challengeName": "fitness",
                "videoCount": 500_000,
            }
        }
        result = _walk_for_trending(data)
        assert any(r["hashtag"] == "#fitness" for r in result)

    def test_walk_for_trending_empty(self):
        assert _walk_for_trending({}) == []

    def test_walk_for_trending_depth_limit(self):
        # Should not recurse infinitely
        nested = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": {"i": {}}}}}}}}}}
        result = _walk_for_trending(nested)
        assert isinstance(result, list)


# ── Analyzer tests ────────────────────────────────────────────────────────


class TestAnalyzer:
    def test_merge_hashtags_cross_platform(self):
        yt = [{"hashtag": "#fitness", "score": 10.0, "total_views": 1_000_000, "video_count": 5}]
        tt = [{"hashtag": "#fitness", "score": 8.0, "total_views": 500_000, "video_count": 3}]
        result = merge_hashtags(yt, tt)
        assert len(result) == 1
        fitness = result[0]
        assert fitness["cross_platform"] is True
        # Score should be doubled for cross-platform
        assert fitness["combined_score"] > 18.0

    def test_merge_hashtags_single_platform(self):
        yt = [{"hashtag": "#youtube_only", "score": 5.0, "total_views": 500_000, "video_count": 2}]
        tt = [{"hashtag": "#tiktok_only", "score": 5.0, "total_views": 500_000, "video_count": 2}]
        result = merge_hashtags(yt, tt)
        assert len(result) == 2
        assert all(not r.get("cross_platform") for r in result)

    def test_merge_hashtags_empty(self):
        assert merge_hashtags([], []) == []

    def test_merge_videos_combined(self):
        yt = [{"views": 5_000_000, "likes": 100_000, "platform": "youtube"}]
        tt = [{"views": 10_000_000, "likes": 800_000, "platform": "tiktok"}]
        result = merge_videos(yt, tt)
        assert len(result) == 2
        assert result[0]["views"] == 10_000_000  # sorted by views

    def test_merge_videos_engagement_rate(self):
        videos = [{"views": 1_000, "likes": 100, "platform": "youtube"}]
        result = merge_videos(videos, [])
        assert result[0]["engagement_rate"] == 10.0

    def test_merge_videos_zero_views(self):
        videos = [{"views": 0, "likes": 0, "platform": "tiktok"}]
        result = merge_videos([], videos)
        assert result[0]["engagement_rate"] == 0

    def test_extract_trending_topics_basic(self):
        videos = [
            {"title": "Fitness workout routine", "description": "Best fitness tips"},
            {"title": "Fitness motivation guide", "description": "Workout every day"},
            {"title": "Gym fitness results", "description": "Transform your body"},
        ]
        result = extract_trending_topics(videos, top_n=10)
        assert len(result) > 0
        topics = [r["topic"] for r in result]
        assert "fitness" in topics

    def test_extract_trending_topics_filters_stopwords(self):
        videos = [
            {"title": "The the and or but", "description": "is was are"},
            {"title": "The the and or but", "description": "is was are"},
        ]
        result = extract_trending_topics(videos)
        topics = [r["topic"] for r in result]
        assert "the" not in topics
        assert "and" not in topics

    def test_identify_content_themes(self):
        videos = [
            {"title": "Best workout routine for beginners", "description": "gym fitness"},
            {"title": "Morning workout exercise tips", "description": "fitness health body"},
            {"title": "Delicious pasta recipe tonight", "description": "cooking food"},
        ]
        result = identify_content_themes(videos)
        themes = [r["theme"] for r in result]
        assert "fitness" in themes
        assert "food" in themes

    def test_identify_content_themes_empty(self):
        result = identify_content_themes([])
        assert result == []

    def test_build_trend_report_empty(self):
        report = build_trend_report()
        assert "top_hashtags" in report
        assert "content_themes" in report
        assert "trending_topics" in report

    def test_build_trend_report_with_data(self):
        yt_data = {
            "platform": "youtube",
            "videos": [{"views": 1_000_000, "likes": 50_000, "title": "fitness video",
                         "description": "workout tips", "hashtags": ["#fitness"]}],
            "hashtags": [{"hashtag": "#fitness", "score": 10.0, "total_views": 1_000_000, "video_count": 1}],
            "music_trends": [],
        }
        tt_data = {
            "platform": "tiktok",
            "videos": [],
            "hashtags": [{"hashtag": "#fitness", "score": 8.0, "total_views": 500_000, "video_count": 3}],
            "sounds": [],
        }
        report = build_trend_report(yt_data, tt_data, region="US")
        assert report["region"] == "US"
        assert len(report["top_hashtags"]) > 0
        cross = report["cross_platform_hashtags"]
        assert any(h["hashtag"] == "#fitness" for h in cross)


# ── Optimizer tests ───────────────────────────────────────────────────────


class TestOptimizer:
    def _sample_report(self) -> dict:
        return {
            "top_hashtags": [
                {"hashtag": "#fitness", "combined_score": 20.0, "cross_platform": True,
                 "total_views": 5_000_000, "video_count": 10},
                {"hashtag": "#workout", "combined_score": 15.0, "cross_platform": False,
                 "total_views": 3_000_000, "video_count": 7},
                {"hashtag": "#gym", "combined_score": 10.0, "cross_platform": False,
                 "total_views": 1_000_000, "video_count": 5},
            ],
            "cross_platform_hashtags": [
                {"hashtag": "#fitness", "combined_score": 20.0, "cross_platform": True}
            ],
            "trending_topics": [
                {"topic": "workout", "frequency": 5, "total_views": 3_000_000, "score": 28.0},
                {"topic": "fitness", "frequency": 4, "total_views": 2_000_000, "score": 22.0},
            ],
            "content_themes": [
                {"theme": "fitness", "video_count": 5, "total_views": 5_000_000, "sample_titles": []},
            ],
            "tiktok_sounds": [
                {"title": "Trending Sound 1", "artist": "Artist 1", "video_count": 100_000},
            ],
            "music_trends": [
                {"artist": "Artist A", "total_views": 10_000_000, "video_count": 2},
            ],
        }

    def test_generate_hashtag_pack_tiktok(self):
        report = self._sample_report()
        result = generate_hashtag_pack(report, niche="fitness", platform="tiktok")
        assert "tiktok" in result["packs"]
        pack = result["packs"]["tiktok"]
        assert "hashtags" in pack
        assert len(pack["hashtags"]) <= 8

    def test_generate_hashtag_pack_all_platforms(self):
        report = self._sample_report()
        result = generate_hashtag_pack(report, niche="fitness", platform="all")
        assert "tiktok" in result["packs"]
        assert "youtube" in result["packs"]
        assert "instagram" in result["packs"]

    def test_generate_hashtag_pack_copy_paste(self):
        report = self._sample_report()
        result = generate_hashtag_pack(report, platform="tiktok")
        pack = result["packs"]["tiktok"]
        assert "copy_paste" in pack
        assert isinstance(pack["copy_paste"], str)

    def test_generate_content_calendar_structure(self):
        report = self._sample_report()
        cal = generate_content_calendar(
            report, niche="fitness", platforms=["tiktok"], weeks=1
        )
        assert "calendar" in cal
        assert cal["weeks"] == 1
        assert "tiktok" in cal["platforms"]
        assert cal["total_posts"] > 0

    def test_generate_content_calendar_days(self):
        report = self._sample_report()
        cal = generate_content_calendar(
            report, niche="fitness", platforms=["tiktok"], weeks=1
        )
        day_names = {d["day"] for d in cal["calendar"]}
        assert len(day_names) > 0

    def test_generate_content_calendar_2_weeks(self):
        report = self._sample_report()
        cal = generate_content_calendar(
            report, niche="fitness", platforms=["tiktok"], weeks=2
        )
        weeks = {d["week"] for d in cal["calendar"]}
        assert 1 in weeks
        assert 2 in weeks

    def test_determine_growth_phase(self):
        assert _determine_growth_phase(0) == "seed"
        assert _determine_growth_phase(999) == "seed"
        assert _determine_growth_phase(1_000) == "growth"
        assert _determine_growth_phase(9_999) == "growth"
        assert _determine_growth_phase(10_000) == "scaling"
        assert _determine_growth_phase(100_000) == "established"

    def test_generate_account_optimization_structure(self):
        report = self._sample_report()
        result = generate_account_optimization(
            report, platform="tiktok", niche="fitness", current_followers=5_000
        )
        assert "profile" in result
        assert "content_strategy" in result
        assert "hashtag_strategy" in result
        assert "growth_tactics" in result
        assert "monetization_readiness" in result
        assert result["growth_phase"] == "growth"

    def test_generate_account_optimization_platforms(self):
        report = self._sample_report()
        for platform in ["tiktok", "youtube", "instagram"]:
            result = generate_account_optimization(
                report, platform=platform, niche="tech"
            )
            assert result["platform"] == platform


# ── Config tests ──────────────────────────────────────────────────────────


class TestConfig:
    def test_parse_cookie_string_basic(self):
        result = _parse_cookie_string("sessionid=abc123; ttwid=def456")
        assert result["sessionid"] == "abc123"
        assert result["ttwid"] == "def456"

    def test_parse_cookie_string_single(self):
        result = _parse_cookie_string("key=value")
        assert result["key"] == "value"

    def test_parse_cookie_string_empty(self):
        result = _parse_cookie_string("")
        assert result == {}

    def test_parse_cookie_string_no_equals(self):
        result = _parse_cookie_string("novalue;another=ok")
        assert "another" in result

    def test_load_config_returns_dict(self, tmp_path, monkeypatch):
        import cli_anything.trends.utils.config as config_mod
        monkeypatch.setattr(config_mod, "CONFIG_FILE", tmp_path / "config.json")
        result = load_config()
        assert isinstance(result, dict)

    def test_save_and_load_config(self, tmp_path, monkeypatch):
        import cli_anything.trends.utils.config as config_mod
        config_file = tmp_path / "config.json"
        monkeypatch.setattr(config_mod, "CONFIG_FILE", config_file)
        monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
        save_config({"youtube_api_key": "test_key_123"})
        loaded = load_config()
        assert loaded.get("youtube_api_key") == "test_key_123"


# ── Session tests ─────────────────────────────────────────────────────────


class TestSession:
    def test_session_record_and_history(self, tmp_path):
        sess = Session(str(tmp_path / "session.json"))
        sess.record("test cmd", {"param": "val"}, {"result": "ok"})
        history = sess.history()
        assert len(history) == 1
        assert history[0]["command"] == "test cmd"

    def test_session_undo_redo(self, tmp_path):
        sess = Session(str(tmp_path / "session.json"))
        sess.record("cmd1", {}, {"r": 1})
        sess.record("cmd2", {}, {"r": 2})
        undone = sess.undo()
        assert undone.command == "cmd2"
        redone = sess.redo()
        assert redone.command == "cmd2"

    def test_session_undo_empty(self, tmp_path):
        sess = Session(str(tmp_path / "session.json"))
        assert sess.undo() is None

    def test_session_redo_empty(self, tmp_path):
        sess = Session(str(tmp_path / "session.json"))
        assert sess.redo() is None

    def test_session_status(self, tmp_path):
        sess = Session(str(tmp_path / "session.json"))
        sess.record("cmd", {}, {})
        status = sess.status()
        assert status["history_count"] == 1

    def test_session_persistence(self, tmp_path):
        sf = str(tmp_path / "session.json")
        sess1 = Session(sf)
        sess1.record("persistent cmd", {"x": 1}, {"y": 2})

        sess2 = Session(sf)
        history = sess2.history()
        assert len(history) == 1
        assert history[0]["command"] == "persistent cmd"
