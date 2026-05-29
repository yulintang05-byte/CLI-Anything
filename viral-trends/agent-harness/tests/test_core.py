"""Viral Trends CLI - Unit tests (no network required).

Covers: session, workspace, trends (mock), optimizer, scheduler, guides.
Run: cd viral-trends/agent-harness && pytest tests/test_core.py -v
"""

import copy
import json
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.viral_trends.core.session import Session
from cli_anything.viral_trends.core import workspace as ws_mod
from cli_anything.viral_trends.core import trends as trends_mod
from cli_anything.viral_trends.core import optimizer as opt_mod
from cli_anything.viral_trends.core import scheduler as sched_mod
from cli_anything.viral_trends.core import theme_pages as guide_mod


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    return Session()


@pytest.fixture
def workspace_session():
    s = Session()
    ws_mod.new_workspace(s, name="test", niche="gaming")
    return s


@pytest.fixture
def session_with_snapshot(workspace_session):
    """Session with a synthetic snapshot injected directly (no network)."""
    workspace_session.project["trend_snapshots"].append({
        "snapshot_id": "snap0",
        "timestamp": "2024-01-01T12:00:00",
        "platform": "youtube",
        "country": "US",
        "niche": "gaming",
        "live": False,
        "youtube": [
            {"rank": 1, "title": "Test Video", "channel": "TestChan",
             "views": 1000, "likes": 50, "category": "Gaming",
             "url": "https://youtube.com/watch?v=x", "duration_seconds": 300}
        ],
        "tiktok": [],
    })
    return workspace_session


@pytest.fixture
def session_with_entry(workspace_session):
    """Session with a synthetic schedule entry injected directly."""
    workspace_session.project["schedule"].append({
        "entry_id": "sched0",
        "day": "monday",
        "time": "19:00",
        "platform": "tiktok",
        "content_type": "video",
        "topic": "gaming tips",
        "hashtag_set": "gaming_viral",
        "hook_type": "curiosity",
        "status": "planned",
        "notes": "",
        "created": "2024-01-01T12:00:00",
    })
    return workspace_session


# ─────────────────────────────────────────────────────────────────────────────
# Session
# ─────────────────────────────────────────────────────────────────────────────

class TestSession:
    def test_initial_state(self, session):
        assert not session.has_project()
        assert session.project is None
        assert session.project_path is None
        assert not session._modified

    def test_get_project_raises_without_project(self, session):
        with pytest.raises(RuntimeError, match="No workspace loaded"):
            session.get_project()

    def test_set_project(self, session):
        proj = {"version": "1.0", "name": "test", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        assert session.has_project()
        assert session.project["name"] == "test"

    def test_snapshot_and_undo(self, session):
        proj = {"version": "1.0", "name": "v1", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        session.snapshot("initial")
        session.project["name"] = "v2"
        session.undo()
        assert session.project["name"] == "v1"

    def test_undo_empty_raises(self, session):
        proj = {"version": "1.0", "name": "x", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            session.undo()

    def test_redo_after_undo(self, session):
        proj = {"version": "1.0", "name": "v1", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        session.snapshot("step1")
        session.project["name"] = "v2"
        session.undo()
        assert session.project["name"] == "v1"
        session.redo()
        assert session.project["name"] == "v2"

    def test_redo_empty_raises(self, session):
        proj = {"version": "1.0", "name": "x", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            session.redo()

    def test_snapshot_clears_redo_stack(self, session):
        proj = {"version": "1.0", "name": "v1", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        session.snapshot("s1")
        session.project["name"] = "v2"
        session.undo()
        session.snapshot("new_branch")
        assert len(session._redo_stack) == 0

    def test_max_undo_limit(self, session):
        proj = {"version": "1.0", "name": "v0", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        for i in range(Session.MAX_UNDO + 10):
            session.snapshot(f"snap{i}")
        assert len(session._undo_stack) == Session.MAX_UNDO

    def test_status_returns_dict(self, session):
        status = session.status()
        assert "has_project" in status
        assert "modified" in status
        assert "undo_count" in status
        assert "redo_count" in status

    def test_modified_flag_set_on_snapshot(self, session):
        proj = {"version": "1.0", "name": "x", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        assert not session._modified
        session.snapshot("test")
        assert session._modified

    def test_deep_copy_in_snapshot(self, session):
        proj = {"version": "1.0", "name": "v1", "niche": "gaming",
                "trend_snapshots": [{"id": "s0"}], "schedule": [],
                "optimizer_config": {}, "metadata": {}}
        session.set_project(proj)
        session.snapshot("before")
        session.project["trend_snapshots"].append({"id": "s1"})
        assert len(session.project["trend_snapshots"]) == 2
        session.undo()
        assert len(session.project["trend_snapshots"]) == 1

    def test_save_session_no_path_raises(self, session):
        proj = {"version": "1.0", "name": "x", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        with pytest.raises(ValueError, match="No save path"):
            session.save_session()

    def test_save_and_reload(self, session, tmp_path):
        proj = {"version": "1.0", "name": "saved", "niche": "gaming",
                "trend_snapshots": [], "schedule": [], "optimizer_config": {},
                "metadata": {}}
        session.set_project(proj)
        path = str(tmp_path / "test.json")
        session.save_session(path)
        assert os.path.isfile(path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["name"] == "saved"


# ─────────────────────────────────────────────────────────────────────────────
# Workspace
# ─────────────────────────────────────────────────────────────────────────────

class TestWorkspace:
    def test_new_workspace_defaults(self, session):
        result = ws_mod.new_workspace(session)
        assert result["success"]
        assert session.has_project()

    def test_new_workspace_custom(self, session):
        ws_mod.new_workspace(session, name="my_page", niche="finance")
        assert session.project["name"] == "my_page"
        assert session.project["niche"] == "finance"

    def test_new_workspace_invalid_niche(self, session):
        with pytest.raises(ValueError, match="Unknown niche"):
            ws_mod.new_workspace(session, niche="nonexistent")

    def test_all_niches_valid(self, session):
        for niche_name in ws_mod.NICHES:
            s = Session()
            result = ws_mod.new_workspace(s, niche=niche_name)
            assert result["success"]

    def test_list_niches(self):
        niches = ws_mod.list_niches()
        assert len(niches) >= 8
        for n in niches:
            assert "name" in n
            assert "hashtag_seed" in n
            assert "peak_hour" in n

    def test_workspace_info(self, workspace_session):
        result = ws_mod.workspace_info(workspace_session)
        assert result["name"] == "test"
        assert result["niche"] == "gaming"
        assert result["snapshots"] == 0
        assert result["schedule_entries"] == 0

    def test_workspace_info_no_project_raises(self, session):
        with pytest.raises(RuntimeError):
            ws_mod.workspace_info(session)

    def test_save_and_open_roundtrip(self, session, tmp_path):
        ws_mod.new_workspace(session, name="roundtrip", niche="finance")
        path = str(tmp_path / "rt.json")
        ws_mod.save_workspace(session, path)
        s2 = Session()
        result = ws_mod.open_workspace(s2, path)
        assert result["success"]
        assert s2.project["name"] == "roundtrip"
        assert s2.project["niche"] == "finance"

    def test_open_nonexistent_raises(self, session):
        with pytest.raises(FileNotFoundError):
            ws_mod.open_workspace(session, "/nonexistent/path.json")

    def test_open_missing_key_raises(self, session, tmp_path):
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"version": "1.0"}))
        with pytest.raises(ValueError, match="missing key"):
            ws_mod.open_workspace(session, str(incomplete))

    def test_validate_adds_metadata(self, session, tmp_path):
        workspace = {
            "version": "1.0", "name": "test", "niche": "gaming",
            "trend_snapshots": [], "schedule": []
        }
        path = tmp_path / "ws.json"
        path.write_text(json.dumps(workspace))
        ws_mod.open_workspace(session, str(path))
        assert "metadata" in session.project


# ─────────────────────────────────────────────────────────────────────────────
# Trends
# ─────────────────────────────────────────────────────────────────────────────

class TestTrends:
    def test_fetch_youtube_mock(self):
        result = trends_mod.fetch_youtube_trends(live=False)
        assert result["success"]
        assert result["source"] == "mock"
        assert result["count"] > 0
        assert len(result["items"]) > 0

    def test_fetch_tiktok_mock(self):
        result = trends_mod.fetch_tiktok_trends(live=False)
        assert result["success"]
        assert result["source"] == "mock"
        assert result["count"] > 0

    def test_youtube_items_have_required_keys(self):
        result = trends_mod.fetch_youtube_trends(live=False)
        required = {"rank", "title", "channel", "views", "likes", "category", "url", "duration_seconds"}
        for item in result["items"]:
            assert required.issubset(item.keys()), f"Missing keys in {item}"

    def test_tiktok_items_have_required_keys(self):
        result = trends_mod.fetch_tiktok_trends(live=False)
        required = {"rank", "hashtag", "posts", "views", "growth_pct", "niche"}
        for item in result["items"]:
            assert required.issubset(item.keys()), f"Missing keys in {item}"

    def test_youtube_max_results(self):
        result = trends_mod.fetch_youtube_trends(max_results=5, live=False)
        assert len(result["items"]) <= 5

    def test_tiktok_niche_filter(self):
        result = trends_mod.fetch_tiktok_trends(niche="gaming", live=False)
        for item in result["items"]:
            assert item["niche"] == "gaming"

    def test_tiktok_all_niche(self):
        result = trends_mod.fetch_tiktok_trends(niche="all", live=False)
        niches_seen = {item["niche"] for item in result["items"]}
        assert len(niches_seen) > 1  # "all" should return multiple niches

    def test_injected_yt_fetcher_called(self, workspace_session):
        call_log = []

        def mock_fetcher(country, max_results, category):
            call_log.append({"country": country, "max_results": max_results})
            return [{"rank": 1, "title": "Mock", "channel": "Mock",
                     "views": 1, "likes": 0, "category": "Test",
                     "url": "http://example.com", "duration_seconds": 60}]

        result = trends_mod.get_trend_snapshot(
            workspace_session, platform="youtube", live=True,
            yt_fetcher=mock_fetcher
        )
        assert len(call_log) == 1
        assert result["success"]

    def test_injected_tt_fetcher_called(self, workspace_session):
        call_log = []

        def mock_tt_fetcher(niche, max_results):
            call_log.append({"niche": niche, "max_results": max_results})
            return [{"rank": 1, "hashtag": "#test", "posts": 100,
                     "views": 1000, "growth_pct": 50, "niche": "tech"}]

        result = trends_mod.get_trend_snapshot(
            workspace_session, platform="tiktok", live=True,
            tt_fetcher=mock_tt_fetcher
        )
        assert len(call_log) == 1
        assert result["success"]

    def test_fetcher_failure_falls_back_to_mock(self, workspace_session):
        def failing_fetcher(country, max_results, category):
            raise ConnectionError("Network unreachable")

        result = trends_mod.get_trend_snapshot(
            workspace_session, platform="youtube", live=True,
            yt_fetcher=failing_fetcher
        )
        assert result["success"]
        assert len(result["snapshot"]["youtube"]) > 0

    def test_get_trend_snapshot_saves_to_session(self, workspace_session):
        trends_mod.get_trend_snapshot(workspace_session, platform="youtube", live=False)
        assert len(workspace_session.project["trend_snapshots"]) == 1

    def test_list_snapshots_empty(self, workspace_session):
        result = trends_mod.list_snapshots(workspace_session)
        assert result == []

    def test_list_snapshots(self, session_with_snapshot):
        result = trends_mod.list_snapshots(session_with_snapshot)
        assert len(result) == 1
        assert result[0]["snapshot_id"] == "snap0"
        assert result[0]["yt_count"] == 1

    def test_show_snapshot(self, session_with_snapshot):
        result = trends_mod.show_snapshot(session_with_snapshot, "snap0")
        assert result["snapshot_id"] == "snap0"

    def test_show_snapshot_not_found_raises(self, session_with_snapshot):
        with pytest.raises(ValueError, match="Snapshot not found"):
            trends_mod.show_snapshot(session_with_snapshot, "snapX")

    def test_remove_snapshot(self, session_with_snapshot):
        result = trends_mod.remove_snapshot(session_with_snapshot, "snap0")
        assert result["success"]
        assert len(session_with_snapshot.project["trend_snapshots"]) == 0

    def test_sequential_snapshot_ids(self, workspace_session):
        trends_mod.get_trend_snapshot(workspace_session, platform="youtube", live=False)
        trends_mod.get_trend_snapshot(workspace_session, platform="tiktok", live=False)
        snaps = workspace_session.project["trend_snapshots"]
        assert snaps[0]["snapshot_id"] == "snap0"
        assert snaps[1]["snapshot_id"] == "snap1"


# ─────────────────────────────────────────────────────────────────────────────
# Optimizer
# ─────────────────────────────────────────────────────────────────────────────

class TestOptimizer:
    def test_get_hashtags_returns_tags(self):
        result = opt_mod.get_hashtags(niche="gaming")
        assert result["success"]
        assert len(result["tags"]) > 0
        assert all(t.startswith("#") for t in result["tags"])

    def test_get_hashtags_count_respected(self):
        result = opt_mod.get_hashtags(niche="gaming", count=5)
        assert len(result["tags"]) <= 5

    def test_get_hashtags_invalid_niche_raises(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            opt_mod.get_hashtags(niche="nonexistent")

    def test_get_hashtags_by_set_name(self):
        result = opt_mod.get_hashtags(niche="gaming", set_name="gaming_viral")
        assert result["set_name"] == "gaming_viral"

    def test_get_hashtags_invalid_set_raises(self):
        with pytest.raises(ValueError, match="Unknown hashtag set"):
            opt_mod.get_hashtags(niche="gaming", set_name="nonexistent_set")

    def test_get_posting_times_tiktok(self):
        result = opt_mod.get_posting_times(platform="tiktok")
        assert result["success"]
        assert len(result["windows"]) > 0
        for w in result["windows"]:
            assert "start" in w
            assert "end" in w
            assert "score" in w

    def test_get_posting_times_youtube(self):
        result = opt_mod.get_posting_times(platform="youtube")
        assert result["success"]
        assert len(result["windows"]) > 0

    def test_get_posting_times_instagram(self):
        result = opt_mod.get_posting_times(platform="instagram")
        assert result["success"]

    def test_get_posting_times_invalid_platform_raises(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            opt_mod.get_posting_times(platform="snapchat")

    def test_get_posting_times_specific_day(self):
        result = opt_mod.get_posting_times(platform="tiktok", day="friday")
        assert result["day"] == "friday"
        assert len(result["windows"]) > 0

    def test_get_posting_times_invalid_day_raises(self):
        with pytest.raises(ValueError, match="Unknown day"):
            opt_mod.get_posting_times(platform="tiktok", day="funday")

    def test_get_posting_times_top_sorted_by_score(self):
        result = opt_mod.get_posting_times(platform="tiktok")
        scores = [w["score"] for w in result["windows"]]
        assert scores == sorted(scores, reverse=True)

    def test_get_caption_hook(self):
        result = opt_mod.get_caption_hook(hook_type="curiosity", niche="gaming")
        assert result["success"]
        assert len(result["hooks"]) == 3
        assert result["hook_type"] == "curiosity"

    def test_get_caption_hook_fills_niche(self):
        result = opt_mod.get_caption_hook(hook_type="curiosity", niche="finance")
        for hook in result["hooks"]:
            assert "{niche}" not in hook

    def test_get_caption_hook_fill_template(self):
        result = opt_mod.get_caption_hook(
            hook_type="authority", niche="finance",
            fill={"count": "1000", "items": "strategies", "years": "5"}
        )
        assert all("{count}" not in h and "{items}" not in h for h in result["hooks"])

    def test_get_caption_hook_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Unknown hook type"):
            opt_mod.get_caption_hook(hook_type="nonexistent")

    def test_list_hashtag_sets_all(self):
        result = opt_mod.list_hashtag_sets()
        assert len(result) >= 24

    def test_list_hashtag_sets_filtered(self):
        result = opt_mod.list_hashtag_sets(niche="gaming")
        assert all(s["niche"] == "gaming" for s in result)
        assert len(result) >= 3

    def test_list_hook_types(self):
        result = opt_mod.list_hook_types()
        types = [h["hook_type"] for h in result]
        assert "curiosity" in types
        assert "urgency" in types
        assert "authority" in types
        assert "relatability" in types
        assert "controversy" in types

    def test_optimize_profile_returns_required_keys(self):
        result = opt_mod.optimize_profile(niche="gaming", platform="tiktok")
        assert result["success"]
        required = {"hashtag_set", "top_hashtags", "best_posting_day",
                    "best_posting_time", "top_posting_windows", "caption_hooks",
                    "action_plan"}
        assert required.issubset(result.keys())

    def test_optimize_profile_invalid_niche_raises(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            opt_mod.optimize_profile(niche="nonexistent")

    def test_all_niches_have_hashtag_sets(self):
        from cli_anything.viral_trends.core.workspace import NICHES
        for niche in NICHES:
            result = opt_mod.get_hashtags(niche=niche)
            assert len(result["tags"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────────────────────────────────────

class TestScheduler:
    def test_add_entry(self, workspace_session):
        result = sched_mod.add_entry(
            workspace_session, day="monday", time="19:00", platform="tiktok"
        )
        assert result["success"]
        assert result["entry"]["entry_id"] == "sched0"
        assert result["entry"]["day"] == "monday"
        assert result["entry"]["time"] == "19:00"

    def test_add_entry_invalid_day_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Invalid day"):
            sched_mod.add_entry(workspace_session, day="funday", time="19:00", platform="tiktok")

    def test_add_entry_invalid_time_raises(self, workspace_session):
        with pytest.raises(ValueError):
            sched_mod.add_entry(workspace_session, day="monday", time="25:00", platform="tiktok")

    def test_add_entry_invalid_platform_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Invalid platform"):
            sched_mod.add_entry(workspace_session, day="monday", time="19:00", platform="snapchat")

    def test_add_entry_invalid_content_type_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Invalid content_type"):
            sched_mod.add_entry(workspace_session, day="monday", time="19:00",
                                platform="tiktok", content_type="podcast")

    def test_remove_entry(self, session_with_entry):
        result = sched_mod.remove_entry(session_with_entry, "sched0")
        assert result["success"]
        assert len(session_with_entry.project["schedule"]) == 0

    def test_remove_nonexistent_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Schedule entry not found"):
            sched_mod.remove_entry(workspace_session, "sched99")

    def test_update_entry_topic(self, session_with_entry):
        result = sched_mod.update_entry(session_with_entry, "sched0", topic="new topic")
        assert result["entry"]["topic"] == "new topic"

    def test_update_entry_status(self, session_with_entry):
        result = sched_mod.update_entry(session_with_entry, "sched0", status="drafted")
        assert result["entry"]["status"] == "drafted"

    def test_update_entry_invalid_status_raises(self, session_with_entry):
        with pytest.raises(ValueError, match="Invalid status"):
            sched_mod.update_entry(session_with_entry, "sched0", status="deleted")

    def test_update_entry_unknown_field_raises(self, session_with_entry):
        with pytest.raises(ValueError, match="Unknown field"):
            sched_mod.update_entry(session_with_entry, "sched0", color="blue")

    def test_mark_status(self, session_with_entry):
        result = sched_mod.mark_status(session_with_entry, "sched0", "published")
        assert result["entry"]["status"] == "published"

    def test_mark_status_invalid_raises(self, session_with_entry):
        with pytest.raises(ValueError, match="Invalid status"):
            sched_mod.mark_status(session_with_entry, "sched0", "archived")

    def test_list_entries_empty(self, workspace_session):
        result = sched_mod.list_entries(workspace_session)
        assert result == []

    def test_list_entries(self, session_with_entry):
        result = sched_mod.list_entries(session_with_entry)
        assert len(result) == 1
        assert result[0]["entry_id"] == "sched0"

    def test_list_entries_day_filter(self, session_with_entry):
        result = sched_mod.list_entries(session_with_entry, day="monday")
        assert len(result) == 1
        result_wrong_day = sched_mod.list_entries(session_with_entry, day="friday")
        assert len(result_wrong_day) == 0

    def test_list_entries_platform_filter(self, session_with_entry):
        result = sched_mod.list_entries(session_with_entry, platform="tiktok")
        assert len(result) == 1
        result_wrong = sched_mod.list_entries(session_with_entry, platform="youtube")
        assert len(result_wrong) == 0

    def test_list_entries_invalid_day_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Invalid day"):
            sched_mod.list_entries(workspace_session, day="funday")

    def test_show_calendar_has_all_days(self, workspace_session):
        calendar = sched_mod.show_calendar(workspace_session)
        assert set(calendar.keys()) == set(sched_mod.DAYS)

    def test_show_calendar_with_entry(self, session_with_entry):
        calendar = sched_mod.show_calendar(session_with_entry)
        assert len(calendar["monday"]) == 1
        assert len(calendar["friday"]) == 0

    def test_generate_week_creates_entries(self, workspace_session):
        result = sched_mod.generate_week(
            workspace_session, niche="gaming", platforms=["tiktok"], posts_per_day=1
        )
        assert result["success"]
        assert result["entries_created"] == 7  # 7 days × 1 post/day × 1 platform
        assert len(workspace_session.project["schedule"]) == 7

    def test_generate_week_two_posts_per_day(self, workspace_session):
        result = sched_mod.generate_week(
            workspace_session, niche="gaming", platforms=["tiktok"], posts_per_day=2
        )
        assert result["entries_created"] == 14  # 7 days × 2 posts/day

    def test_generate_week_multi_platform(self, workspace_session):
        result = sched_mod.generate_week(
            workspace_session, niche="gaming",
            platforms=["tiktok", "youtube"], posts_per_day=1
        )
        assert result["entries_created"] == 14  # 7 days × 1 × 2 platforms

    def test_generate_week_existing_schedule_raises(self, session_with_entry):
        with pytest.raises(RuntimeError, match="Schedule already has"):
            sched_mod.generate_week(session_with_entry, niche="gaming",
                                    platforms=["tiktok"], posts_per_day=1)

    def test_generate_week_overwrite(self, session_with_entry):
        result = sched_mod.generate_week(
            session_with_entry, niche="gaming", platforms=["tiktok"],
            posts_per_day=1, overwrite=True
        )
        assert result["success"]
        # Old entry should be gone
        assert all(e["topic"] != "gaming tips" for e in session_with_entry.project["schedule"])

    def test_generate_week_invalid_niche_raises(self, workspace_session):
        with pytest.raises(ValueError, match="Unknown niche"):
            sched_mod.generate_week(workspace_session, niche="nonexistent",
                                    platforms=["tiktok"])

    def test_sequential_entry_ids(self, workspace_session):
        sched_mod.add_entry(workspace_session, day="monday", time="09:00", platform="tiktok")
        sched_mod.add_entry(workspace_session, day="tuesday", time="10:00", platform="youtube")
        entries = workspace_session.project["schedule"]
        assert entries[0]["entry_id"] == "sched0"
        assert entries[1]["entry_id"] == "sched1"

    def test_parse_time_valid(self):
        assert sched_mod._parse_time("19:00") == "19:00"
        assert sched_mod._parse_time("9:30") == "09:30"
        assert sched_mod._parse_time("0:00") == "00:00"

    def test_parse_time_invalid_format_raises(self):
        with pytest.raises(ValueError):
            sched_mod._parse_time("7pm")

    def test_parse_time_invalid_hour_raises(self):
        with pytest.raises(ValueError, match="Hour must be"):
            sched_mod._parse_time("25:00")

    def test_parse_time_invalid_minute_raises(self):
        with pytest.raises(ValueError, match="Minute must be"):
            sched_mod._parse_time("10:60")


# ─────────────────────────────────────────────────────────────────────────────
# Guide Content
# ─────────────────────────────────────────────────────────────────────────────

class TestGuideContent:
    def test_all_guide_keys_exist(self):
        for key in ["overview", "theme-page", "converting", "hashtags",
                    "posting-times", "hooks", "youtube", "tiktok", "schedule"]:
            content = guide_mod.guide_content(key)
            assert content is not None

    def test_guide_has_title(self):
        for key in guide_mod.GUIDES:
            content = guide_mod.guide_content(key)
            assert "title" in content
            assert len(content["title"]) > 0

    def test_guide_has_sections(self):
        for key in guide_mod.GUIDES:
            content = guide_mod.guide_content(key)
            assert "sections" in content
            assert len(content["sections"]) > 0

    def test_sections_have_heading_and_body(self):
        for key in guide_mod.GUIDES:
            content = guide_mod.guide_content(key)
            for section in content["sections"]:
                assert "heading" in section
                assert "body" in section
                assert len(section["body"]) > 0

    def test_theme_page_guide_has_niche_content(self):
        content = guide_mod.guide_content("theme-page")
        full_text = " ".join(s["body"] for s in content["sections"])
        assert "niche" in full_text.lower()
        assert "follower" in full_text.lower()

    def test_converting_guide_has_revenue_info(self):
        content = guide_mod.guide_content("converting")
        full_text = " ".join(s["body"] for s in content["sections"])
        assert "$" in full_text
        assert "affiliate" in full_text.lower()

    def test_hashtag_guide_has_platform_info(self):
        content = guide_mod.guide_content("hashtags")
        full_text = " ".join(s["body"] for s in content["sections"])
        assert "tiktok" in full_text.lower()
        assert "youtube" in full_text.lower()

    def test_unknown_guide_raises(self):
        with pytest.raises(ValueError, match="Unknown guide"):
            guide_mod.guide_content("nonexistent-guide")

    def test_list_guides(self):
        result = guide_mod.list_guides()
        assert len(result) >= 8
        keys = [g["key"] for g in result]
        assert "theme-page" in keys
        assert "converting" in keys
        assert "hashtags" in keys

    def test_guide_quick_commands_are_valid_cli_commands(self):
        for key in guide_mod.GUIDES:
            content = guide_mod.guide_content(key)
            for cmd in content.get("quick_commands", []):
                assert cmd.startswith("viral-trends ")
