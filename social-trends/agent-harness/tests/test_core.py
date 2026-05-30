"""Unit tests for Social Trends CLI core modules."""

import json
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.social_trends.core.session import Session, HistoryEntry
from cli_anything.social_trends.core.trends import aggregate_trends, build_hashtag_set, _niche_hashtags
from cli_anything.social_trends.core.optimizer import (
    get_posting_schedule,
    optimize_account,
    generate_bio,
    _determine_growth_stage,
    _kpis_for_platform,
    PLATFORM_BEST_TIMES,
    POSTING_FREQUENCY,
)
from cli_anything.social_trends.core.theme_pages import (
    list_niches,
    get_niche_detail,
    get_launch_checklist,
    get_monetization_guide,
    get_content_repurposing_guide,
    get_legal_sources,
    generate_content_plan,
    NICHES,
    MONETIZATION_METHODS,
    LEGAL_CONTENT_SOURCES,
)


# ── Session tests ─────────────────────────────────────────────────────────────

class TestSession:
    def test_record_adds_to_history(self):
        s = Session()
        s.record("test cmd", {"arg": 1}, {"result": "ok"})
        assert s.history_count == 1

    def test_undo_moves_to_redo(self):
        s = Session()
        s.record("cmd1", {})
        s.record("cmd2", {})
        entry = s.undo()
        assert entry is not None
        assert entry.command == "cmd2"
        assert s.can_redo

    def test_redo_restores(self):
        s = Session()
        s.record("cmd1", {})
        s.undo()
        entry = s.redo()
        assert entry is not None
        assert entry.command == "cmd1"
        assert not s.can_redo

    def test_undo_empty_returns_none(self):
        s = Session()
        assert s.undo() is None

    def test_redo_empty_returns_none(self):
        s = Session()
        assert s.redo() is None

    def test_status_dict(self):
        s = Session()
        s.record("x", {})
        st = s.status()
        assert "history_count" in st
        assert "can_undo" in st
        assert "can_redo" in st
        assert st["history_count"] == 1
        assert st["can_undo"] is True

    def test_history_limit(self):
        s = Session()
        for i in range(10):
            s.record(f"cmd{i}", {})
        hist = s.history(limit=5)
        assert len(hist) == 5

    def test_record_clears_redo(self):
        s = Session()
        s.record("cmd1", {})
        s.undo()
        assert s.can_redo
        s.record("cmd2", {})
        assert not s.can_redo

    def test_history_entry_to_dict(self):
        entry = HistoryEntry(command="test", args={"k": "v"}, result={"r": 1})
        d = entry.to_dict()
        assert d["command"] == "test"
        assert d["args"] == {"k": "v"}
        assert d["result"] == {"r": 1}
        assert "timestamp" in d

    def test_history_entry_from_dict(self):
        d = {"command": "x", "args": {}, "timestamp": "2024-01-01T00:00:00Z", "result": None}
        entry = HistoryEntry.from_dict(d)
        assert entry.command == "x"

    def test_save_and_load(self, tmp_path):
        sf = str(tmp_path / "session.json")
        s = Session(session_file=sf)
        s.record("saved_cmd", {"arg": 42}, {"ok": True})
        s2 = Session(session_file=sf)
        assert s2.history_count == 1
        assert s2.history()[0]["command"] == "saved_cmd"

    def test_load_nonexistent_file(self, tmp_path):
        sf = str(tmp_path / "nonexistent.json")
        s = Session(session_file=sf)
        assert s.history_count == 0

    def test_history_returns_dicts(self):
        s = Session()
        s.record("cmd", {"x": 1})
        hist = s.history()
        assert isinstance(hist[0], dict)


# ── Trends aggregation tests ──────────────────────────────────────────────────

class TestTrendsAggregation:
    def _make_yt_data(self):
        return {
            "hashtags": [
                {"tag": "#fitness", "score": 1_000_000},
                {"tag": "#gym", "score": 500_000},
                {"tag": "#viral", "score": 300_000},
            ],
            "music": [
                {"title": "Song A", "artist": "Artist X", "platform": "youtube"},
            ],
            "videos": [],
            "source": "youtube_test",
        }

    def _make_tt_data(self):
        return {
            "hashtags": [
                {"tag": "#fitness", "score": 2_000_000},
                {"tag": "#fyp", "score": 50_000_000},
                {"tag": "#dance", "score": 1_000_000},
            ],
            "music": [
                {"title": "Sound B", "artist": "Artist Y", "platform": "tiktok"},
            ],
            "videos": [],
            "source": "tiktok_test",
        }

    def test_aggregate_returns_required_keys(self):
        agg = aggregate_trends(self._make_yt_data(), self._make_tt_data())
        assert "hashtags" in agg
        assert "music" in agg
        assert "cross_platform_hashtags" in agg
        assert "top_videos" in agg
        assert "generated_at" in agg

    def test_cross_platform_detected(self):
        agg = aggregate_trends(self._make_yt_data(), self._make_tt_data())
        cp = agg["cross_platform_hashtags"]
        tags = [h["tag"] for h in cp]
        assert "#fitness" in tags

    def test_virality_score_cross_platform_bonus(self):
        agg = aggregate_trends(self._make_yt_data(), self._make_tt_data())
        fitness = next(h for h in agg["hashtags"] if h["tag"] == "#fitness")
        expected = (1_000_000 + 2_000_000) * 2.0
        assert fitness["virality_score"] == int(expected)

    def test_yt_only(self):
        agg = aggregate_trends(self._make_yt_data(), None)
        assert len(agg["hashtags"]) > 0
        assert all("youtube" in h["platforms"] for h in agg["hashtags"])

    def test_tt_only(self):
        agg = aggregate_trends(None, self._make_tt_data())
        assert len(agg["hashtags"]) > 0

    def test_both_none(self):
        agg = aggregate_trends(None, None)
        assert agg["hashtags"] == []
        assert agg["music"] == []

    def test_music_deduplicated(self):
        yt = {**self._make_yt_data(), "music": [{"title": "Same Song", "artist": "Artist"}]}
        tt = {**self._make_tt_data(), "music": [{"title": "Same Song", "artist": "Artist"}]}
        agg = aggregate_trends(yt, tt)
        titles = [m["title"] for m in agg["music"]]
        assert titles.count("Same Song") == 1

    def test_top_n_limits_hashtags(self):
        agg = aggregate_trends(self._make_yt_data(), self._make_tt_data(), top_n=2)
        assert len(agg["hashtags"]) <= 2


class TestBuildHashtagSet:
    def _base_trends(self):
        return {
            "hashtags": [
                {"tag": "#fitness", "score": 1_000_000, "platforms": ["youtube", "tiktok"], "cross_platform": True},
                {"tag": "#gym", "score": 500_000, "platforms": ["tiktok"], "cross_platform": False},
                {"tag": "#viral", "score": 300_000, "platforms": ["youtube"], "cross_platform": False},
            ],
        }

    def test_returns_all_platform_sets(self):
        result = build_hashtag_set(self._base_trends(), niche="fitness")
        assert "tiktok_set" in result
        assert "youtube_set" in result
        assert "instagram_set" in result

    def test_tiktok_set_max_8(self):
        result = build_hashtag_set(self._base_trends(), niche="fitness")
        assert len(result["tiktok_set"]) <= 8

    def test_youtube_set_max_30(self):
        result = build_hashtag_set(self._base_trends(), niche="fitness")
        assert len(result["youtube_set"]) <= 30

    def test_strategy_field_preserved(self):
        result = build_hashtag_set(self._base_trends(), strategy="viral")
        assert result["strategy"] == "viral"

    def test_niche_tags_included(self):
        result = build_hashtag_set(self._base_trends(), niche="fitness", strategy="niche")
        all_tags = result["tiktok_set"] + result["youtube_set"]
        assert any("fitness" in t.lower() for t in all_tags)

    def test_strategy_notes_present(self):
        result = build_hashtag_set(self._base_trends())
        assert "strategy_notes" in result
        assert "tiktok" in result["strategy_notes"]


class TestNicheHashtags:
    def test_known_niche(self):
        tags = _niche_hashtags("fitness")
        assert len(tags) > 0
        assert all(t.startswith("#") for t in tags)

    def test_unknown_niche_returns_generic(self):
        tags = _niche_hashtags("underwater_basket_weaving")
        assert "#underwater_basket_weaving" in tags or any("underwater" in t for t in tags)

    @pytest.mark.parametrize("niche", ["fitness", "food", "finance", "fashion", "beauty", "travel",
                                        "gaming", "tech", "motivation", "comedy", "lifestyle", "music", "business"])
    def test_all_defined_niches(self, niche):
        tags = _niche_hashtags(niche)
        assert isinstance(tags, list)
        assert len(tags) > 0


# ── Optimizer tests ───────────────────────────────────────────────────────────

class TestPostingSchedule:
    def test_returns_all_requested_platforms(self):
        result = get_posting_schedule(["tiktok", "youtube"])
        assert "tiktok" in result["platforms"]
        assert "youtube" in result["platforms"]

    def test_schedule_has_best_times(self):
        result = get_posting_schedule(["tiktok"])
        sched = result["platforms"]["tiktok"]
        assert "best_times" in sched
        assert "monday" in sched["best_times"]

    def test_weekly_plan_has_7_days(self):
        result = get_posting_schedule(["tiktok"])
        assert len(result["weekly_plan"]) == 7

    def test_general_tips_present(self):
        result = get_posting_schedule()
        assert len(result["general_tips"]) > 0

    def test_unknown_platform_skipped(self):
        result = get_posting_schedule(["nonexistent"])
        assert "nonexistent" not in result["platforms"]

    def test_all_platforms_have_frequency(self):
        for platform in ["tiktok", "youtube", "instagram", "twitter"]:
            result = get_posting_schedule([platform])
            freq = result["platforms"][platform]["frequency"]
            assert "min" in freq
            assert "max" in freq
            assert "unit" in freq


class TestOptimizeAccount:
    def test_returns_required_keys(self):
        result = optimize_account("tiktok", niche="fitness", current_followers=5000)
        assert "growth_stage" in result
        assert "content_recommendations" in result
        assert "growth_tactics" in result
        assert "kpis_to_track" in result
        assert "content_hooks" in result

    def test_growth_stages(self):
        assert _determine_growth_stage(500)["stage"] == "nano"
        assert _determine_growth_stage(5_000)["stage"] == "micro"
        assert _determine_growth_stage(50_000)["stage"] == "mid"
        assert _determine_growth_stage(500_000)["stage"] == "macro"
        assert _determine_growth_stage(5_000_000)["stage"] == "mega"

    def test_monetization_goal_adds_path(self):
        result = optimize_account("tiktok", goals=["monetization"])
        assert len(result.get("monetization_path", [])) > 0

    def test_content_hooks_present(self):
        result = optimize_account("youtube")
        assert len(result["content_hooks"]) > 0

    def test_kpis_for_known_platforms(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            kpis = _kpis_for_platform(platform)
            assert len(kpis) > 0
            assert all("metric" in k and "target" in k and "why" in k for k in kpis)

    def test_kpis_unknown_platform_empty(self):
        kpis = _kpis_for_platform("myspace")
        assert kpis == []


class TestGenerateBio:
    def test_returns_bio_options(self):
        result = generate_bio("tiktok", "Mike", "fitness", "help you get fit")
        assert "bio_options" in result
        assert len(result["bio_options"]) >= 1

    def test_character_limit_correct(self):
        result = generate_bio("tiktok", "X", "fitness", "y")
        assert result["character_limit"] == 80

        result = generate_bio("instagram", "X", "fitness", "y")
        assert result["character_limit"] == 150

        result = generate_bio("youtube", "X", "fitness", "y")
        assert result["character_limit"] == 200

    def test_bio_fits_field_accurate(self):
        result = generate_bio("tiktok", "X", "fitness", "y")
        for opt in result["bio_options"]:
            assert opt["fits"] == (opt["length"] <= 80)

    def test_tips_present(self):
        result = generate_bio("instagram", "X", "fitness", "y")
        assert len(result["tips"]) > 0


# ── Theme page tests ─────────────────────────────────────────────────────────

class TestListNiches:
    def test_returns_list(self):
        niches = list_niches()
        assert isinstance(niches, list)
        assert len(niches) > 0

    def test_each_niche_has_required_keys(self):
        niches = list_niches()
        required = {"id", "name", "difficulty", "monetization_potential", "best_platforms"}
        for n in niches:
            assert required.issubset(set(n.keys())), f"Missing keys in {n.get('id')}"

    def test_filter_by_difficulty(self):
        easy = list_niches(filter_difficulty="easy")
        assert all(n["difficulty"] == "easy" for n in easy)

    def test_filter_by_platform(self):
        yt_niches = list_niches(filter_platform="youtube")
        assert all("youtube" in n["best_platforms"] for n in yt_niches)

    def test_sort_by_monetization(self):
        niches = list_niches(sort_by="monetization_potential")
        pot = [n["monetization_potential"] for n in niches]
        assert "very_high" in pot[:3] or len(niches) < 3

    def test_sort_by_name(self):
        niches = list_niches(sort_by="name")
        names = [n["name"] for n in niches]
        assert names == sorted(names)


class TestGetNicheDetail:
    def test_known_niche(self):
        detail = get_niche_detail("fitness_motivation")
        assert detail["id"] == "fitness_motivation"
        assert "content_types" in detail
        assert "target_audience" in detail

    def test_unknown_niche_raises(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            get_niche_detail("nonexistent_niche_xyz")

    @pytest.mark.parametrize("niche_id", list(NICHES.keys()))
    def test_all_niches_retrievable(self, niche_id):
        detail = get_niche_detail(niche_id)
        assert detail["id"] == niche_id


class TestGetLaunchChecklist:
    def test_returns_list(self):
        checklist = get_launch_checklist()
        assert isinstance(checklist, list)

    def test_each_item_has_step_and_action(self):
        checklist = get_launch_checklist()
        for item in checklist:
            assert "step" in item
            assert "action" in item
            assert "done" in item
            assert item["done"] is False

    def test_steps_are_sequential(self):
        checklist = get_launch_checklist()
        steps = [item["step"] for item in checklist]
        assert steps == list(range(1, len(steps) + 1))


class TestGetMonetizationGuide:
    def test_all_methods_returned_without_arg(self):
        guide = get_monetization_guide()
        assert len(guide) == len(MONETIZATION_METHODS)

    def test_specific_method_returned(self):
        guide = get_monetization_guide("affiliate_marketing")
        assert "affiliate_marketing" in guide

    def test_unknown_method_raises(self):
        with pytest.raises(ValueError):
            get_monetization_guide("magic_money")

    def test_each_method_has_required_fields(self):
        guide = get_monetization_guide()
        for method, info in guide.items():
            assert "description" in info
            assert "follower_minimum" in info


class TestGetContentRepurposing:
    def test_has_workflow_and_tools(self):
        result = get_content_repurposing_guide()
        assert "workflow" in result
        assert "tools" in result

    def test_workflow_is_ordered_list(self):
        result = get_content_repurposing_guide()
        assert isinstance(result["workflow"], list)
        assert len(result["workflow"]) > 0


class TestGetLegalSources:
    def test_returns_list(self):
        sources = get_legal_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0

    def test_each_source_has_required_fields(self):
        sources = get_legal_sources()
        required = {"source", "url", "type", "license"}
        for s in sources:
            assert required.issubset(set(s.keys()))


class TestGenerateContentPlan:
    def test_basic_plan_structure(self):
        plan = generate_content_plan("tech_ai", weeks=2)
        assert "weekly_plan" in plan
        assert len(plan["weekly_plan"]) == 2

    def test_each_week_has_posts(self):
        plan = generate_content_plan("fitness_motivation", weeks=1)
        week = plan["weekly_plan"][0]
        assert "week" in week
        assert "posts" in week
        assert len(week["posts"]) > 0

    def test_custom_platforms(self):
        plan = generate_content_plan("food_recipes", platforms=["tiktok"], weeks=1)
        for week in plan["weekly_plan"]:
            for post in week["posts"]:
                assert "tiktok" in post["platforms"]

    def test_unknown_niche_raises(self):
        with pytest.raises(ValueError):
            generate_content_plan("fantasy_niche_xyz")

    @pytest.mark.parametrize("niche_id", list(NICHES.keys()))
    def test_all_niches_generate_plans(self, niche_id):
        plan = generate_content_plan(niche_id, weeks=1)
        assert len(plan["weekly_plan"]) == 1


# ── YouTube module tests (mock network) ──────────────────────────────────────

class TestYouTubeFetcher:
    def test_extract_hashtags_from_text(self):
        from cli_anything.social_trends.core.youtube import _extract_hashtags_from_text
        tags = _extract_hashtags_from_text("Check out #fitness and #gym content #viral")
        assert "#fitness" not in tags  # _extract returns without #
        assert "fitness" in tags
        assert "gym" in tags
        assert "viral" in tags

    def test_parse_view_count(self):
        from cli_anything.social_trends.core.youtube import _parse_view_count
        assert _parse_view_count("1.5M views") == 1_500_000
        assert _parse_view_count("500K") == 500_000
        assert _parse_view_count("1.2B") == 1_200_000_000
        assert _parse_view_count("12,345") == 12_345

    def test_extract_text(self):
        from cli_anything.social_trends.core.youtube import _extract_text
        runs = [{"text": "Hello"}, {"text": " "}, {"text": "World"}]
        assert _extract_text(runs) == "Hello World"
        assert _extract_text([]) == ""

    def test_extract_music_from_videos(self):
        from cli_anything.social_trends.core.youtube import _extract_music_from_videos
        videos = [
            {"title": "Artist - Song (Official Music Video)", "channel": "ArtistChannel",
             "view_count": 1_000_000, "url": "https://youtube.com/watch?v=abc"},
            {"title": "Random Vlog", "channel": "Vlogger",
             "view_count": 5_000, "url": "https://youtube.com/watch?v=xyz"},
        ]
        music = _extract_music_from_videos(videos)
        assert len(music) >= 1
        assert music[0]["artist"] == "ArtistChannel"

    @patch("cli_anything.social_trends.core.youtube.requests.get")
    def test_fetch_via_data_api_success(self, mock_get):
        from cli_anything.social_trends.core.youtube import _fetch_via_data_api

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "vid123",
                    "snippet": {
                        "title": "Test Video #trending",
                        "channelTitle": "TestChannel",
                        "description": "A #fitness video",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "tags": ["workout", "fitness"],
                        "thumbnails": {"high": {"url": "https://img.jpg"}},
                    },
                    "statistics": {
                        "viewCount": "1000000",
                        "likeCount": "50000",
                        "commentCount": "1000",
                    },
                    "contentDetails": {"duration": "PT10M30S"},
                }
            ]
        }
        mock_get.return_value = mock_response

        result = _fetch_via_data_api("test_key", "all", "US", 25)
        assert "videos" in result
        assert len(result["videos"]) == 1
        assert result["videos"][0]["id"] == "vid123"
        assert result["videos"][0]["view_count"] == 1_000_000
        assert "source" in result
        assert result["source"] == "youtube_data_api_v3"


# ── TikTok module tests (mock network) ───────────────────────────────────────

class TestTikTokFetcher:
    def test_parse_tiktok_item_list_empty(self):
        from cli_anything.social_trends.core.tiktok import _parse_tiktok_item_list
        result = _parse_tiktok_item_list({"itemList": []}, 30)
        assert result["videos"] == []
        assert result["hashtags"] == []

    def test_parse_tiktok_item_list_with_items(self):
        from cli_anything.social_trends.core.tiktok import _parse_tiktok_item_list

        data = {
            "itemList": [
                {
                    "id": "tt123",
                    "desc": "Cool video #fitness #fyp",
                    "author": {"uniqueId": "creator1", "nickname": "Creator One"},
                    "stats": {"playCount": 1_000_000, "diggCount": 50_000, "shareCount": 10_000, "commentCount": 5_000},
                    "music": {"id": "mus1", "title": "Trending Sound", "authorName": "DJ", "duration": 30, "original": False},
                    "video": {"duration": 15, "cover": "https://cover.jpg"},
                    "challenges": [],
                }
            ]
        }
        result = _parse_tiktok_item_list(data, 30)
        assert len(result["videos"]) == 1
        assert result["videos"][0]["id"] == "tt123"
        assert result["videos"][0]["play_count"] == 1_000_000
        assert len(result["hashtags"]) > 0
        assert len(result["music"]) > 0

    def test_evergreen_hashtags_not_empty(self):
        from cli_anything.social_trends.core.tiktok import _evergreen_tiktok_hashtags
        tags = _evergreen_tiktok_hashtags()
        assert len(tags) >= 10
        assert all("tag" in t and "score" in t for t in tags)
        assert any(t["tag"] == "#fyp" for t in tags)

    def test_evergreen_music_not_empty(self):
        from cli_anything.social_trends.core.tiktok import _evergreen_tiktok_music
        music = _evergreen_tiktok_music()
        assert len(music) >= 1
        assert all("title" in m and "artist" in m for m in music)

    @patch("cli_anything.social_trends.core.tiktok.requests.get")
    def test_fetch_trending_uses_cache_fallback(self, mock_get):
        from cli_anything.social_trends.core.tiktok import _fetch_discover_fallback

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "challengeInfoList": [
                {
                    "challengeInfo": {"challenge": {"title": "fitnesschallenge"}},
                    "stats": {"viewCount": 5_000_000},
                }
            ]
        }
        mock_get.return_value = mock_response

        result = _fetch_discover_fallback("US", 30)
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0


# ── CLI integration tests ─────────────────────────────────────────────────────

class TestCLI:
    def test_cli_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output.lower() or "social" in result.output.lower()

    def test_trends_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "--help"])
        assert result.exit_code == 0

    def test_account_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["account", "--help"])
        assert result.exit_code == 0

    def test_theme_page_group_help(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "--help"])
        assert result.exit_code == 0

    def test_config_set_and_get(self, tmp_path, monkeypatch):
        from click.testing import CliRunner
        from cli_anything.social_trends import social_trends_cli
        monkeypatch.setattr(social_trends_cli, "_CONFIG_DIR", tmp_path)
        monkeypatch.setattr(social_trends_cli, "_CONFIG_FILE", tmp_path / "config.json")
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "set", "default_region", "GB"])
        assert result.exit_code == 0

    def test_theme_page_niches_command(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower() or "tech" in result.output.lower()

    def test_theme_page_checklist_command(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["theme-page", "checklist"])
        assert result.exit_code == 0

    def test_theme_page_niches_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_theme_page_detail_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "detail", "tech_ai"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["id"] == "tech_ai"

    def test_account_schedule_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "account", "schedule", "-p", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "platforms" in data

    def test_account_optimize_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "account", "optimize", "-p", "tiktok", "-n", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "growth_stage" in data

    def test_account_bio_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "account", "bio",
            "-p", "tiktok", "-n", "Mike", "--niche", "fitness",
            "-v", "help you get fit"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "bio_options" in data

    def test_theme_page_monetize_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "monetize"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)
        assert "affiliate_marketing" in data

    def test_theme_page_sources_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "sources"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_theme_page_repurpose_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme-page", "repurpose"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "workflow" in data

    @patch("cli_anything.social_trends.core.tiktok.requests.get")
    def test_trends_fetch_tiktok_with_mock(self, mock_get):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "itemList": [
                {
                    "id": "tt_test",
                    "desc": "#fitness content",
                    "author": {"uniqueId": "user1", "nickname": "User One"},
                    "stats": {"playCount": 500_000, "diggCount": 10_000, "shareCount": 1_000, "commentCount": 500},
                    "music": {"id": "m1", "title": "Test Sound", "authorName": "DJ Test", "duration": 30, "original": False},
                    "video": {"duration": 15, "cover": ""},
                    "challenges": [],
                }
            ]
        }
        mock_get.return_value = mock_response

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "trends", "fetch-tiktok", "--no-cache"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "videos" in data or "hashtags" in data

    def test_session_history_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "session", "history"])
        assert result.exit_code == 0

    def test_session_status_json(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "can_undo" in data

    def test_version_flag(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.social_trends_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
