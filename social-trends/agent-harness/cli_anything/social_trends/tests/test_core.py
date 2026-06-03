"""Unit tests for social-trends core modules — no external deps required."""

import json
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# ── Session ────────────────────────────────────────────────────────────

from cli_anything.social_trends.core.session import Session, HistoryEntry


class TestSession:
    def test_record_and_history(self, tmp_path):
        s = Session(session_file=str(tmp_path / "session.json"))
        s.record("trends scrape", {"platform": "tiktok"}, {"count": 30})
        h = s.history()
        assert len(h) == 1
        assert h[0]["command"] == "trends scrape"
        assert h[0]["args"]["platform"] == "tiktok"

    def test_undo_redo(self, tmp_path):
        s = Session(session_file=str(tmp_path / "session.json"))
        s.record("cmd1", {}, {"a": 1})
        s.record("cmd2", {}, {"b": 2})
        entry = s.undo()
        assert entry.command == "cmd2"
        assert len(s.history()) == 1
        redone = s.redo()
        assert redone.command == "cmd2"
        assert len(s.history()) == 2

    def test_undo_empty(self, tmp_path):
        s = Session(session_file=str(tmp_path / "session.json"))
        assert s.undo() is None

    def test_redo_empty(self, tmp_path):
        s = Session(session_file=str(tmp_path / "session.json"))
        assert s.redo() is None

    def test_persistence(self, tmp_path):
        sf = str(tmp_path / "session.json")
        s1 = Session(session_file=sf)
        s1.record("saved", {}, {"x": 1})
        s2 = Session(session_file=sf)
        assert len(s2.history()) == 1
        assert s2.history()[0]["command"] == "saved"

    def test_status(self, tmp_path):
        s = Session(session_file=str(tmp_path / "session.json"))
        status = s.status()
        assert "history_count" in status
        assert "undo_available" in status

    def test_history_entry_to_dict(self):
        e = HistoryEntry(command="test", args={"k": "v"}, result={"r": 1})
        d = e.to_dict()
        assert d["command"] == "test"
        assert d["args"]["k"] == "v"
        assert d["result"]["r"] == 1

    def test_history_entry_from_dict(self):
        data = {"command": "x", "args": {}, "result": None, "timestamp": 1234.0}
        e = HistoryEntry.from_dict(data)
        assert e.command == "x"
        assert e.timestamp == 1234.0


# ── Backend helpers ────────────────────────────────────────────────────

from cli_anything.social_trends.utils.social_trends_backend import (
    _extract_hashtags,
    _normalize_tiktok_video,
    get_trending_hashtags,
    get_tiktok_trending_sounds,
    load_cache,
    save_cache,
)


class TestExtractHashtags:
    def test_basic(self):
        tags = _extract_hashtags("Check out #fitness and #gym tips!")
        assert "#fitness" in tags
        assert "#gym" in tags

    def test_no_tags(self):
        assert _extract_hashtags("No hashtags here") == []

    def test_deduplicate(self):
        tags = _extract_hashtags("#test #test #other")
        assert tags.count("#test") == 1

    def test_empty_string(self):
        assert _extract_hashtags("") == []


class TestNormalizeTikTokVideo:
    def _sample_video(self):
        return {
            "id": "123456",
            "desc": "Amazing workout #fitness #gym",
            "author": {"uniqueId": "fitnessguru", "nickname": "Fitness Guru"},
            "stats": {
                "playCount": 1000000,
                "diggCount": 50000,
                "shareCount": 5000,
                "commentCount": 2000,
            },
            "music": {
                "title": "Pump It Up",
                "authorName": "DJ Energy",
                "id": "987",
                "duration": 30,
            },
            "video": {"cover": "https://example.com/thumb.jpg", "duration": 60},
            "createTime": 1700000000,
            "challenges": [{"title": "FitnessChallenge"}, {"title": "WorkoutMotivation"}],
        }

    def test_basic_fields(self):
        v = _normalize_tiktok_video(self._sample_video())
        assert v["platform"] == "tiktok"
        assert v["channel"] == "fitnessguru"
        assert v["views"] == 1000000
        assert v["likes"] == 50000

    def test_hashtag_extraction(self):
        v = _normalize_tiktok_video(self._sample_video())
        assert "#fitness" in v["hashtags"] or "#FitnessChallenge" in v["hashtags"]

    def test_music_normalized(self):
        v = _normalize_tiktok_video(self._sample_video())
        assert v["music_used"]["title"] == "Pump It Up"
        assert v["music_used"]["artist"] == "DJ Energy"

    def test_url_built(self):
        v = _normalize_tiktok_video(self._sample_video())
        assert "tiktok.com" in v["url"]
        assert "123456" in v["url"]

    def test_missing_music(self):
        raw = self._sample_video()
        raw["music"] = {}
        v = _normalize_tiktok_video(raw)
        assert v["music_used"] is None

    def test_empty_video(self):
        v = _normalize_tiktok_video({})
        assert v["platform"] == "tiktok"
        assert v["views"] == 0


class TestGetTrendingHashtags:
    def _make_videos(self):
        return [
            {"platform": "tiktok", "hashtags": ["#fitness", "#gym", "#health"], "views": 1000000},
            {"platform": "tiktok", "hashtags": ["#fitness", "#workout"], "views": 500000},
            {"platform": "youtube", "hashtags": ["#fitness", "#motivation"], "views": 2000000},
        ]

    def test_returns_ranked_list(self):
        tags = get_trending_hashtags(self._make_videos(), top_n=10)
        assert isinstance(tags, list)
        assert len(tags) <= 10

    def test_fitness_is_top(self):
        tags = get_trending_hashtags(self._make_videos())
        names = [t["hashtag"] for t in tags]
        assert "#fitness" in names
        fitness_idx = names.index("#fitness")
        assert fitness_idx == 0  # highest total_views

    def test_has_required_fields(self):
        tags = get_trending_hashtags(self._make_videos())
        for t in tags:
            assert "hashtag" in t
            assert "appearances" in t
            assert "total_views" in t

    def test_empty_input(self):
        assert get_trending_hashtags([]) == []

    def test_top_n_respected(self):
        videos = [
            {"platform": "tiktok", "hashtags": [f"#tag{i}"], "views": i * 1000}
            for i in range(50)
        ]
        tags = get_trending_hashtags(videos, top_n=5)
        assert len(tags) <= 5


class TestGetTrendingSounds:
    def _make_videos(self):
        return [
            {"platform": "tiktok", "music_used": {"title": "Song A", "artist": "Artist 1", "id": "1"}, "views": 500000},
            {"platform": "tiktok", "music_used": {"title": "Song A", "artist": "Artist 1", "id": "1"}, "views": 300000},
            {"platform": "tiktok", "music_used": {"title": "Song B", "artist": "Artist 2", "id": "2"}, "views": 100000},
            {"platform": "tiktok", "music_used": None, "views": 50000},
        ]

    def test_ranks_by_count(self):
        sounds = get_tiktok_trending_sounds(self._make_videos())
        assert sounds[0]["title"] == "Song A"
        assert sounds[0]["video_count"] == 2

    def test_ignores_none_music(self):
        sounds = get_tiktok_trending_sounds(self._make_videos())
        assert all(s["title"] for s in sounds)

    def test_total_views_accumulated(self):
        sounds = get_tiktok_trending_sounds(self._make_videos())
        song_a = next(s for s in sounds if s["title"] == "Song A")
        assert song_a["total_views"] == 800000

    def test_empty_input(self):
        assert get_tiktok_trending_sounds([]) == []


# ── Trends analysis ────────────────────────────────────────────────────

from cli_anything.social_trends.core.trends import analyze_trends, _extract_content_patterns, _compute_engagement_stats


class TestAnalyzeTrends:
    def _sample_videos(self):
        return [
            {
                "platform": "tiktok",
                "title": "10 Best Fitness Tips",
                "hashtags": ["#fitness", "#gym"],
                "views": 2000000,
                "likes": 100000,
                "comments": 5000,
                "music_used": {"title": "Power Song", "artist": "DJ", "id": "1"},
                "categories": ["fitness"],
            },
            {
                "platform": "youtube",
                "title": "How to Build Muscle Fast",
                "hashtags": ["#fitness", "#muscle"],
                "views": 5000000,
                "likes": 200000,
                "comments": 10000,
                "music_used": None,
                "categories": ["fitness", "health"],
            },
        ]

    def test_returns_expected_keys(self):
        report = analyze_trends(self._sample_videos())
        assert "top_hashtags" in report
        assert "trending_sounds" in report
        assert "content_patterns" in report
        assert "engagement_stats" in report
        assert "platform_breakdown" in report
        assert "recommendations" in report

    def test_platform_breakdown(self):
        report = analyze_trends(self._sample_videos())
        bd = report["platform_breakdown"]
        assert bd["tiktok"] == 1
        assert bd["youtube"] == 1
        assert bd["total"] == 2

    def test_empty_input(self):
        report = analyze_trends([])
        assert "error" in report

    def test_hashtag_ranking(self):
        report = analyze_trends(self._sample_videos())
        names = [h["hashtag"] for h in report["top_hashtags"]]
        assert "#fitness" in names

    def test_recommendations_not_empty(self):
        report = analyze_trends(self._sample_videos())
        assert len(report["recommendations"]) > 0


class TestContentPatterns:
    def test_title_format_detection(self):
        videos = [
            {"title": "10 Best Tips for Fitness", "hashtags": [], "views": 1000},
            {"title": "How to Lose Weight Fast", "hashtags": [], "views": 2000},
            {"title": "Is This Really Worth It?", "hashtags": [], "views": 500},
        ]
        patterns = _extract_content_patterns(videos)
        assert patterns["title_formats"]["list_videos_pct"] > 0
        assert patterns["title_formats"]["howto_videos_pct"] > 0
        assert patterns["title_formats"]["question_videos_pct"] > 0

    def test_top_keywords(self):
        videos = [
            {"title": "fitness workout exercise gym", "hashtags": [], "views": 1000},
            {"title": "fitness tips daily workout", "hashtags": [], "views": 2000},
        ]
        patterns = _extract_content_patterns(videos)
        words = [kw["word"] for kw in patterns["top_keywords"]]
        assert "fitness" in words or "workout" in words


class TestEngagementStats:
    def test_basic(self):
        videos = [
            {"views": 1000000, "likes": 50000, "comments": 2000},
            {"views": 500000, "likes": 25000, "comments": 1000},
        ]
        stats = _compute_engagement_stats(videos)
        assert stats["avg_views"] == 750000
        assert stats["total_videos_analyzed"] == 2
        assert "avg_engagement_rate_pct" in stats

    def test_empty(self):
        assert _compute_engagement_stats([]) == {}


# ── Optimizer ──────────────────────────────────────────────────────────

from cli_anything.social_trends.core.optimizer import (
    optimize_account, add_account, remove_account, list_accounts,
    _build_hashtag_plan, _build_posting_schedule, _monetization_roadmap,
    _next_milestone,
)


class TestOptimizer:
    def _trend_data(self):
        return {
            "top_hashtags": [
                {"hashtag": "#fitness", "appearances": 10, "total_views": 5000000},
                {"hashtag": "#gym", "appearances": 8, "total_views": 3000000},
                {"hashtag": "#workout", "appearances": 6, "total_views": 2000000},
            ],
            "trending_sounds": [
                {"title": "Power Song", "artist": "DJ", "video_count": 5, "total_views": 1000000},
            ],
            "content_patterns": {
                "top_keywords": [{"word": "fitness", "count": 10}, {"word": "workout", "count": 8}],
                "title_formats": {"list_videos_pct": 30, "howto_videos_pct": 20, "question_videos_pct": 10, "reaction_videos_pct": 5},
            },
            "engagement_stats": {"avg_views": 1000000, "avg_engagement_rate_pct": 5.0},
        }

    def test_optimize_account_structure(self):
        plan = optimize_account("tiktok", "fitness", self._trend_data(), followers=5000)
        assert "hashtag_plan" in plan
        assert "posting_schedule" in plan
        assert "content_ideas" in plan
        assert "bio_recommendations" in plan
        assert "monetization_roadmap" in plan
        assert "quick_wins" in plan

    def test_hashtag_plan_has_combo(self):
        plan = _build_hashtag_plan("tiktok", "fitness", self._trend_data()["top_hashtags"])
        assert "example_combo" in plan
        assert len(plan["example_combo"]) <= plan["recommended_total"]

    def test_posting_schedule_has_calendar(self):
        sched = _build_posting_schedule("tiktok")
        assert "7_day_calendar" in sched
        assert len(sched["7_day_calendar"]) == 7
        assert sched["best_times"]

    def test_monetization_roadmap_stages(self):
        stages_low = _monetization_roadmap("tiktok", "fitness", 500)
        assert len(stages_low) >= 1
        stages_high = _monetization_roadmap("tiktok", "fitness", 200000)
        assert len(stages_high) >= 1

    def test_next_milestone(self):
        assert _next_milestone(0) == "100 followers"
        assert _next_milestone(99) == "100 followers"
        assert _next_milestone(100) == "500 followers"
        assert _next_milestone(999999) == "1,000,000 followers"


class TestAccountRegistry:
    def test_add_and_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.optimizer.ACCOUNTS_FILE",
            tmp_path / "accounts.json",
        )
        add_account("tiktok", "testuser", "fitness", 1000)
        accounts = list_accounts()
        assert len(accounts) == 1
        assert accounts[0]["username"] == "testuser"

    def test_add_deduplicates(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.optimizer.ACCOUNTS_FILE",
            tmp_path / "accounts.json",
        )
        add_account("tiktok", "testuser", "fitness", 1000)
        add_account("tiktok", "testuser", "fitness", 2000)
        accounts = list_accounts()
        assert len(accounts) == 1
        assert accounts[0]["follower_count"] == 2000

    def test_remove(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.optimizer.ACCOUNTS_FILE",
            tmp_path / "accounts.json",
        )
        add_account("tiktok", "testuser", "fitness")
        removed = remove_account("tiktok", "testuser")
        assert removed is True
        assert list_accounts() == []

    def test_remove_nonexistent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.optimizer.ACCOUNTS_FILE",
            tmp_path / "accounts.json",
        )
        assert remove_account("tiktok", "nobody") is False


# ── Theme Page ─────────────────────────────────────────────────────────

from cli_anything.social_trends.core.theme_page import (
    get_niche_guide, list_supported_niches, get_conversion_tips,
    PROVEN_NICHES, CONVERTING_ELEMENTS, CONVERSION_FUNNEL,
)


class TestThemePage:
    def test_list_niches(self):
        niches = list_supported_niches()
        assert len(niches) > 5
        assert "fitness" in niches
        assert "finance" in niches

    def test_get_known_niche(self):
        guide = get_niche_guide("fitness")
        assert guide["niche"] == "fitness"
        assert "overview" in guide
        assert "bio_formula" in guide
        assert "growth_playbook" in guide
        assert "conversion_funnel" in guide

    def test_get_unknown_niche_returns_generic(self):
        guide = get_niche_guide("underwater_basket_weaving")
        assert guide["niche"] == "underwater_basket_weaving"
        assert "bio_formula" in guide

    def test_converting_elements_present(self):
        assert "bio_formula" in CONVERTING_ELEMENTS
        assert "link_in_bio_stack" in CONVERTING_ELEMENTS
        assert len(CONVERTING_ELEMENTS["link_in_bio_stack"]) >= 4

    def test_conversion_funnel_stages(self):
        for stage in ("awareness", "interest", "desire", "action"):
            assert stage in CONVERSION_FUNNEL
            assert "tactics" in CONVERSION_FUNNEL[stage]
            assert len(CONVERSION_FUNNEL[stage]["tactics"]) >= 3

    def test_proven_niches_have_required_fields(self):
        required = ["description", "avg_engagement", "monetization", "best_platforms",
                    "posting_cadence", "converting_tip"]
        for niche, data in PROVEN_NICHES.items():
            for field in required:
                assert field in data, f"Niche '{niche}' missing field '{field}'"

    def test_get_conversion_tips_returns_list(self):
        tips = get_conversion_tips("tiktok", "fitness", 5000)
        assert isinstance(tips, list)
        assert len(tips) > 5

    def test_get_conversion_tips_with_followers(self):
        tips_low = get_conversion_tips("tiktok", "fitness", 0)
        tips_high = get_conversion_tips("tiktok", "fitness", 5000)
        assert len(tips_high) > len(tips_low)

    def test_bio_example_exists_for_key_niches(self):
        for niche in ("fitness", "finance", "motivational"):
            guide = get_niche_guide(niche)
            assert guide.get("bio_example"), f"No bio example for {niche}"


# ── Cache ──────────────────────────────────────────────────────────────

class TestCache:
    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.social_trends_backend.CACHE_DIR",
            tmp_path,
        )
        save_cache("test_key", {"data": [1, 2, 3]})
        loaded = load_cache("test_key", max_age_secs=60)
        assert loaded == {"data": [1, 2, 3]}

    def test_expired_cache_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.social_trends_backend.CACHE_DIR",
            tmp_path,
        )
        save_cache("expired_key", {"data": "old"})
        loaded = load_cache("expired_key", max_age_secs=0)
        assert loaded is None

    def test_missing_cache_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.social_trends_backend.CACHE_DIR",
            tmp_path,
        )
        loaded = load_cache("nonexistent_key")
        assert loaded is None
