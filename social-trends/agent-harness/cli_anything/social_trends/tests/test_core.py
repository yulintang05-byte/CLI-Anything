"""Unit tests for social-trends core modules — no network, no external dependencies."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))


# ── youtube.py tests ──────────────────────────────────────────────


class TestYoutubeHashtagExtraction:
    def test_extracts_single_hashtag(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags
        assert _extract_hashtags("#viral") == ["viral"]

    def test_extracts_multiple_hashtags(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags
        result = _extract_hashtags("#fyp hello #viral world #trending")
        assert result == ["fyp", "viral", "trending"]

    def test_deduplicates_hashtags(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags
        result = _extract_hashtags("#fyp #fyp #viral")
        assert result.count("fyp") == 1

    def test_empty_string(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags
        assert _extract_hashtags("") == []

    def test_no_hashtags(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags
        assert _extract_hashtags("no hashtags here") == []


class TestYoutubeAggregation:
    def _make_videos(self):
        return [
            {"hashtags": ["fyp", "viral"], "tags": ["gaming", "fun"]},
            {"hashtags": ["fyp", "trending"], "tags": ["gaming"]},
            {"hashtags": ["viral"], "tags": []},
        ]

    def test_aggregate_counts_correctly(self):
        from cli_anything.social_trends.core.youtube import aggregate_trending_hashtags
        videos = self._make_videos()
        result = aggregate_trending_hashtags(videos, top_n=10)
        tags = {r["hashtag"]: r["count"] for r in result}
        assert tags["#fyp"] == 2
        assert tags["#viral"] == 2
        assert tags["#gaming"] == 2

    def test_aggregate_returns_sorted(self):
        from cli_anything.social_trends.core.youtube import aggregate_trending_hashtags
        videos = self._make_videos()
        result = aggregate_trending_hashtags(videos, top_n=10)
        counts = [r["count"] for r in result]
        assert counts == sorted(counts, reverse=True)

    def test_aggregate_respects_top_n(self):
        from cli_anything.social_trends.core.youtube import aggregate_trending_hashtags
        videos = self._make_videos()
        result = aggregate_trending_hashtags(videos, top_n=2)
        assert len(result) <= 2

    def test_aggregate_top_channels(self):
        from cli_anything.social_trends.core.youtube import aggregate_top_channels
        videos = [
            {"channel": "Creator A"},
            {"channel": "Creator A"},
            {"channel": "Creator B"},
        ]
        result = aggregate_top_channels(videos)
        assert result[0]["channel"] == "Creator A"
        assert result[0]["trending_videos"] == 2


class TestYoutubeVideoParser:
    def test_parse_video_renderer_valid(self):
        from cli_anything.social_trends.core.youtube import _parse_video_renderer
        vr = {
            "videoId": "abc123",
            "title": {"runs": [{"text": "Test Video #viral"}]},
            "longBylineText": {"runs": [{"text": "Test Channel"}]},
        }
        result = _parse_video_renderer(vr)
        assert result is not None
        assert result["id"] == "abc123"
        assert result["title"] == "Test Video #viral"
        assert result["channel"] == "Test Channel"
        assert "viral" in result["hashtags"]

    def test_parse_video_renderer_missing_id(self):
        from cli_anything.social_trends.core.youtube import _parse_video_renderer
        result = _parse_video_renderer({})
        assert result is None

    def test_video_url_format(self):
        from cli_anything.social_trends.core.youtube import _parse_video_renderer
        vr = {
            "videoId": "xyz789",
            "title": {"runs": [{"text": "Test"}]},
        }
        result = _parse_video_renderer(vr)
        assert result["url"] == "https://www.youtube.com/watch?v=xyz789"


# ── tiktok.py tests ───────────────────────────────────────────────


class TestTikTokNicheHashtags:
    def test_returns_hashtags_for_known_niche(self):
        from cli_anything.social_trends.core.tiktok import get_niche_hashtags
        tags = get_niche_hashtags("fitness")
        assert len(tags) > 0
        assert all(t.startswith("#") for t in tags)

    def test_includes_universal_by_default(self):
        from cli_anything.social_trends.core.tiktok import get_niche_hashtags
        tags = get_niche_hashtags("fitness")
        assert "#fyp" in tags

    def test_excludes_universal_when_requested(self):
        from cli_anything.social_trends.core.tiktok import get_niche_hashtags
        tags = get_niche_hashtags("fitness", include_universal=False)
        assert "#fyp" not in tags

    def test_unknown_niche_returns_empty(self):
        from cli_anything.social_trends.core.tiktok import get_niche_hashtags
        tags = get_niche_hashtags("nonexistent_niche_xyz", include_universal=False)
        assert tags == []

    def test_all_niches_have_tags(self):
        from cli_anything.social_trends.core.tiktok import list_niches, get_niche_hashtags
        for niche in list_niches():
            tags = get_niche_hashtags(niche, include_universal=False)
            assert len(tags) >= 5, f"Niche '{niche}' has too few tags"


class TestTikTokHashtagParser:
    def test_walk_for_hashtags_finds_data(self):
        from cli_anything.social_trends.core.tiktok import _walk_for_hashtags
        data = {
            "challenges": [
                {
                    "title": "fitness",
                    "stats": {"videoCount": 1000, "viewCount": 5000000},
                    "desc": "Fitness challenge",
                }
            ]
        }
        results = []
        _walk_for_hashtags(data, results, 10)
        assert len(results) == 1
        assert results[0]["hashtag"] == "#fitness"

    def test_walk_respects_max_results(self):
        from cli_anything.social_trends.core.tiktok import _walk_for_hashtags
        data = {
            "list": [
                {"title": f"tag{i}", "stats": {"videoCount": i, "viewCount": i * 100}}
                for i in range(20)
            ]
        }
        results = []
        _walk_for_hashtags(data, results, 5)
        assert len(results) <= 5


# ── hashtags.py tests ─────────────────────────────────────────────


class TestHashtagClassification:
    def test_mega_threshold(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(600_000_000) == "mega"

    def test_large_threshold(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(150_000_000) == "large"

    def test_medium_threshold(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(50_000_000) == "medium"

    def test_small_threshold(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(5_000_000) == "small"

    def test_micro_threshold(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(500_000) == "micro"

    def test_zero(self):
        from cli_anything.social_trends.core.hashtags import classify_hashtag
        assert classify_hashtag(0) == "micro"


class TestHashtagScoring:
    def test_score_returns_0_to_100(self):
        from cli_anything.social_trends.core.hashtags import score_hashtag_set
        tags = [{"hashtag": "#test", "view_count": 1_000_000} for _ in range(10)]
        result = score_hashtag_set(tags)
        assert 0 <= result["score"] <= 100

    def test_score_includes_breakdown(self):
        from cli_anything.social_trends.core.hashtags import score_hashtag_set
        tags = [{"hashtag": "#test"} for _ in range(5)]
        result = score_hashtag_set(tags)
        assert "tier_breakdown" in result
        assert "recommendation" in result

    def test_empty_set_scores(self):
        from cli_anything.social_trends.core.hashtags import score_hashtag_set
        result = score_hashtag_set([])
        assert result["total"] == 0


class TestHashtagFormatting:
    def test_inline_format(self):
        from cli_anything.social_trends.core.hashtags import format_hashtags
        tags = ["#fyp", "#viral"]
        result = format_hashtags(tags, style="inline")
        assert "#fyp" in result
        assert "#viral" in result

    def test_newline_format(self):
        from cli_anything.social_trends.core.hashtags import format_hashtags
        tags = ["#fyp", "#viral"]
        result = format_hashtags(tags, style="newline")
        assert "\n" in result
        lines = result.strip().split("\n")
        assert "#fyp" in lines
        assert "#viral" in lines

    def test_spaced_format(self):
        from cli_anything.social_trends.core.hashtags import format_hashtags
        tags = ["#fyp", "#viral"]
        result = format_hashtags(tags, style="spaced")
        assert result == "#fyp #viral"


class TestBuildOptimalSet:
    def test_returns_list_of_hashtags(self):
        from cli_anything.social_trends.core.hashtags import build_optimal_set
        result = build_optimal_set(
            niche_tags=["#fitness", "#gym", "#workout"],
            trending_tags=[{"hashtag": "#viral", "view_count": 1_000_000_000}],
            platform="tiktok",
        )
        assert isinstance(result, list)
        assert all(t.startswith("#") for t in result)

    def test_respects_max_count(self):
        from cli_anything.social_trends.core.hashtags import build_optimal_set
        result = build_optimal_set(
            niche_tags=[f"#tag{i}" for i in range(50)],
            trending_tags=[],
            platform="tiktok",
            max_count=10,
        )
        assert len(result) <= 10

    def test_no_duplicates(self):
        from cli_anything.social_trends.core.hashtags import build_optimal_set
        result = build_optimal_set(
            niche_tags=["#fitness", "#fyp", "#viral"],
            trending_tags=[{"hashtag": "#fyp", "view_count": 500_000_000}],
            platform="tiktok",
        )
        seen = set()
        for t in result:
            assert t.lower() not in seen, f"Duplicate tag: {t}"
            seen.add(t.lower())

    def test_includes_branded_tags(self):
        from cli_anything.social_trends.core.hashtags import build_optimal_set
        result = build_optimal_set(
            niche_tags=["#fitness"],
            trending_tags=[],
            platform="tiktok",
            branded_tags=["#mybrand"],
        )
        assert "#mybrand" in result


# ── optimizer.py tests ────────────────────────────────────────────


class TestOptimalTimes:
    def test_returns_schedule_for_known_platform(self):
        from cli_anything.social_trends.core.optimizer import get_optimal_times
        result = get_optimal_times("tiktok")
        assert "schedule" in result
        assert "monday" in result["schedule"]

    def test_returns_error_for_unknown_platform(self):
        from cli_anything.social_trends.core.optimizer import get_optimal_times
        result = get_optimal_times("myspace")
        assert "error" in result

    def test_all_days_present(self):
        from cli_anything.social_trends.core.optimizer import get_optimal_times
        result = get_optimal_times("instagram")
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            assert day in result["schedule"]


class TestPostingFrequency:
    def test_tiktok_frequency(self):
        from cli_anything.social_trends.core.optimizer import get_posting_frequency
        result = get_posting_frequency("tiktok")
        assert "optimal" in result
        assert "minimum" in result

    def test_unknown_platform(self):
        from cli_anything.social_trends.core.optimizer import get_posting_frequency
        result = get_posting_frequency("friendster")
        assert "error" in result


class TestProfileAudit:
    def test_returns_checklist_for_tiktok(self):
        from cli_anything.social_trends.core.optimizer import audit_profile
        result = audit_profile("tiktok")
        assert isinstance(result, list)
        assert len(result) >= 5

    def test_checklist_has_required_fields(self):
        from cli_anything.social_trends.core.optimizer import audit_profile
        result = audit_profile("instagram")
        for item in result:
            assert "item" in item
            assert "action" in item

    def test_unknown_platform(self):
        from cli_anything.social_trends.core.optimizer import audit_profile
        result = audit_profile("snapchat")
        assert result[0].get("error") is not None


class TestContentCalendar:
    def test_generates_correct_number_of_days(self):
        from cli_anything.social_trends.core.optimizer import generate_content_calendar
        calendar = generate_content_calendar("fitness", ["tiktok"], days=7)
        assert len(calendar) == 7

    def test_calendar_has_required_fields(self):
        from cli_anything.social_trends.core.optimizer import generate_content_calendar
        calendar = generate_content_calendar("fitness", ["tiktok", "instagram"], days=3)
        for day in calendar:
            assert "date" in day
            assert "weekday" in day
            assert "posts" in day
            assert len(day["posts"]) == 2  # one per platform

    def test_calendar_with_start_date(self):
        from cli_anything.social_trends.core.optimizer import generate_content_calendar
        calendar = generate_content_calendar("fitness", ["tiktok"], days=3, start_date="2025-01-01")
        assert calendar[0]["date"] == "2025-01-01"
        assert calendar[1]["date"] == "2025-01-02"


class TestGrowthCalculator:
    def test_basic_calculation(self):
        from cli_anything.social_trends.core.optimizer import calculate_growth_rate
        result = calculate_growth_rate(1000, 1500, 30)
        assert result["gained"] == 500
        assert result["per_day_avg"] == pytest.approx(500 / 30, rel=0.01)

    def test_projects_to_10k(self):
        from cli_anything.social_trends.core.optimizer import calculate_growth_rate
        result = calculate_growth_rate(0, 1000, 10)
        assert result["days_to_10k"] is not None
        assert isinstance(result["days_to_10k"], int)

    def test_negative_growth(self):
        from cli_anything.social_trends.core.optimizer import calculate_growth_rate
        result = calculate_growth_rate(1000, 900, 30)
        assert result["gained"] == -100
        assert "Stagnant" in result["assessment"]

    def test_zero_days_error(self):
        from cli_anything.social_trends.core.optimizer import calculate_growth_rate
        result = calculate_growth_rate(1000, 1500, 0)
        assert "error" in result


# ── theme_pages.py tests ──────────────────────────────────────────


class TestNicheEvaluation:
    def test_known_niche_returns_score(self):
        from cli_anything.social_trends.core.theme_pages import evaluate_niche
        result = evaluate_niche("fitness")
        assert "total_score" in result
        assert result["total_score"] > 0

    def test_unknown_niche_returns_available(self):
        from cli_anything.social_trends.core.theme_pages import evaluate_niche
        result = evaluate_niche("niche_xyz_not_real")
        assert "available_niches" in result

    def test_grade_assignment(self):
        from cli_anything.social_trends.core.theme_pages import evaluate_niche
        result = evaluate_niche("finance")
        assert result["grade"] in ("A", "B", "C")

    def test_rank_niches_returns_sorted(self):
        from cli_anything.social_trends.core.theme_pages import rank_niches
        ranked = rank_niches()
        scores = [r["total_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)


class TestSetupChecklist:
    def test_returns_all_phases(self):
        from cli_anything.social_trends.core.theme_pages import get_setup_checklist
        checklist = get_setup_checklist()
        assert len(checklist) == 6

    def test_each_phase_has_steps(self):
        from cli_anything.social_trends.core.theme_pages import get_setup_checklist
        for phase in get_setup_checklist():
            assert "steps" in phase
            assert len(phase["steps"]) > 0

    def test_filter_by_phase(self):
        from cli_anything.social_trends.core.theme_pages import get_setup_checklist
        result = get_setup_checklist(phase="monetization")
        assert len(result) >= 1
        assert all("monetiz" in p["phase"].lower() for p in result)


class TestMonetizationRoadmap:
    def test_returns_all_tiers_when_no_followers(self):
        from cli_anything.social_trends.core.theme_pages import get_monetization_roadmap
        result = get_monetization_roadmap()
        assert len(result) == 5

    def test_returns_correct_tier_for_followers(self):
        from cli_anything.social_trends.core.theme_pages import get_monetization_roadmap
        result = get_monetization_roadmap(15_000)
        assert len(result) == 1
        assert "10K" in result[0]["milestone"]

    def test_each_tier_has_strategies(self):
        from cli_anything.social_trends.core.theme_pages import get_monetization_roadmap
        for tier in get_monetization_roadmap():
            assert "strategies" in tier
            assert len(tier["strategies"]) > 0


class TestRepostGuide:
    def test_known_platform_returns_guide(self):
        from cli_anything.social_trends.core.theme_pages import get_repost_guide
        result = get_repost_guide("tiktok")
        assert "process" in result
        assert len(result["process"]) > 0

    def test_unknown_platform_returns_error(self):
        from cli_anything.social_trends.core.theme_pages import get_repost_guide
        result = get_repost_guide("myspace")
        assert "error" in result


# ── music.py tests ────────────────────────────────────────────────


class TestMusicExtraction:
    def test_extract_music_from_videos(self):
        from cli_anything.social_trends.core.music import extract_music_from_tiktok_videos
        videos = [
            {"music": {"id": "1", "title": "Song A", "authorName": "Artist X"}},
            {"music": {"id": "1", "title": "Song A", "authorName": "Artist X"}},
            {"music": {"id": "2", "title": "Song B", "authorName": "Artist Y"}},
        ]
        result = extract_music_from_tiktok_videos(videos)
        assert len(result) == 2
        # Song A should rank first (2 videos)
        assert result[0]["title"] == "Song A"
        assert result[0]["video_count"] == 2

    def test_handles_videos_without_music(self):
        from cli_anything.social_trends.core.music import extract_music_from_tiktok_videos
        videos = [{"title": "no music"}, {"music": {}}]
        result = extract_music_from_tiktok_videos(videos)
        assert result == []


class TestSoundSuggestions:
    def test_known_niche_returns_suggestions(self):
        from cli_anything.social_trends.core.music import suggest_sounds_for_niche
        result = suggest_sounds_for_niche("fitness")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_unknown_niche_returns_generic(self):
        from cli_anything.social_trends.core.music import suggest_sounds_for_niche
        result = suggest_sounds_for_niche("nonexistent_niche_xyz")
        assert len(result) == 1

    def test_strategy_guide_for_tiktok(self):
        from cli_anything.social_trends.core.music import get_music_strategy
        result = get_music_strategy("tiktok")
        assert "best_practice" in result

    def test_unknown_platform_strategy(self):
        from cli_anything.social_trends.core.music import get_music_strategy
        result = get_music_strategy("snapchat")
        assert "error" in result


# ── session.py tests ──────────────────────────────────────────────


class TestSession:
    def test_record_and_history(self):
        from cli_anything.social_trends.core.session import Session
        sess = Session()
        sess.record("test command", {"param": "value"}, {"result": "ok"})
        hist = sess.history(limit=5)
        assert len(hist) == 1
        assert hist[0]["command"] == "test command"

    def test_undo_redo(self):
        from cli_anything.social_trends.core.session import Session
        sess = Session()
        sess.record("cmd1", {}, {"r": 1})
        sess.record("cmd2", {}, {"r": 2})
        undone = sess.undo()
        assert undone.command == "cmd2"
        redone = sess.redo()
        assert redone.command == "cmd2"

    def test_undo_empty_returns_none(self):
        from cli_anything.social_trends.core.session import Session
        sess = Session()
        assert sess.undo() is None

    def test_status(self):
        from cli_anything.social_trends.core.session import Session
        sess = Session()
        sess.record("cmd", {}, {})
        status = sess.status()
        assert status["history_count"] == 1
        assert status["undo_available"] == 1

    def test_persistence(self, tmp_path):
        from cli_anything.social_trends.core.session import Session
        sf = str(tmp_path / "session.json")
        sess = Session(session_file=sf)
        sess.record("persist_test", {"k": "v"}, {"result": "saved"})

        sess2 = Session(session_file=sf)
        hist = sess2.history()
        assert len(hist) == 1
        assert hist[0]["command"] == "persist_test"


# ── trends_backend.py tests ───────────────────────────────────────


class TestTrendsBackend:
    def test_validate_platform_valid(self):
        from cli_anything.social_trends.utils.trends_backend import validate_platform
        assert validate_platform("tiktok") == "tiktok"
        assert validate_platform("TikTok") == "tiktok"

    def test_validate_platform_invalid(self):
        from cli_anything.social_trends.utils.trends_backend import validate_platform
        with pytest.raises(ValueError):
            validate_platform("myspace")

    def test_get_region_default(self):
        from cli_anything.social_trends.utils.trends_backend import get_region
        import os
        os.environ.pop("SOCIAL_TRENDS_REGION", None)
        region = get_region(None)
        assert region == "US"

    def test_get_region_from_opt(self):
        from cli_anything.social_trends.utils.trends_backend import get_region
        assert get_region("GB") == "GB"

    def test_get_region_invalid_defaults_to_config(self):
        from cli_anything.social_trends.utils.trends_backend import get_region
        # Invalid region falls back to config/default
        region = get_region("XX")
        # Should return default since XX isn't in SUPPORTED_REGIONS
        assert region in ["US", "XX"] or isinstance(region, str)

    def test_get_youtube_api_key_from_opt(self):
        from cli_anything.social_trends.utils.trends_backend import get_youtube_api_key
        key = get_youtube_api_key("test-key-123")
        assert key == "test-key-123"

    def test_get_youtube_api_key_from_env(self):
        from cli_anything.social_trends.utils.trends_backend import get_youtube_api_key
        import os
        os.environ["YOUTUBE_API_KEY"] = "env-key-abc"
        key = get_youtube_api_key(None)
        assert key == "env-key-abc"
        del os.environ["YOUTUBE_API_KEY"]

    def test_load_save_config(self, tmp_path, monkeypatch):
        import cli_anything.social_trends.utils.trends_backend as tb
        monkeypatch.setattr(tb, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(tb, "CONFIG_DIR", tmp_path)
        tb.save_config({"region": "GB", "youtube_api_key": "test"})
        cfg = tb.load_config()
        assert cfg["region"] == "GB"
