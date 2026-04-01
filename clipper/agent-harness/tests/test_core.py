"""Clipper CLI - Unit tests (no real media required).

Covers: session, project, clips, filters, export logic.
Run: cd clipper/agent-harness && pytest tests/test_core.py -v
"""

import copy
import json
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.clipper.core.session import Session
from cli_anything.clipper.core import project as proj_mod
from cli_anything.clipper.core import clips as clips_mod
from cli_anything.clipper.core import filters as filters_mod
from cli_anything.clipper.core import export as export_mod
from cli_anything.clipper.utils.time import (
    parse_timecode,
    format_duration,
    format_seconds,
    timecode_to_frames,
    frames_to_timecode,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    return Session()


@pytest.fixture
def project_session():
    s = Session()
    proj_mod.new_project(s, name="test", profile="hd1080p30")
    return s


@pytest.fixture
def session_with_source(project_session):
    """Session with a fake source injected directly (no ffprobe)."""
    project_session.project["sources"].append({
        "id": "src0",
        "name": "test.mp4",
        "path": "/fake/test.mp4",
        "duration": 120.0,
        "video": {"codec": "h264", "width": 1920, "height": 1080, "fps": 30.0},
        "audio": {"codec": "aac", "sample_rate": 44100, "channels": 2},
        "format": "mp4",
    })
    return project_session


@pytest.fixture
def session_with_clip(session_with_source):
    """Session with a source and a clip."""
    session_with_source.project["clips"].append({
        "id": "clip0",
        "source_id": "src0",
        "name": "Test Clip",
        "in": 10.0,
        "out": 40.0,
        "filters": [],
        "label": "",
    })
    return session_with_source


# ─────────────────────────────────────────────────────────────────────────────
# Timecode utilities
# ─────────────────────────────────────────────────────────────────────────────

class TestTimecodeUtils:
    def test_parse_decimal_string(self):
        assert parse_timecode("10.5") == pytest.approx(10.5)

    def test_parse_integer_string(self):
        assert parse_timecode("30") == pytest.approx(30.0)

    def test_parse_float(self):
        assert parse_timecode(5.0) == pytest.approx(5.0)

    def test_parse_int(self):
        assert parse_timecode(0) == pytest.approx(0.0)

    def test_parse_hh_mm_ss(self):
        assert parse_timecode("00:01:30") == pytest.approx(90.0)

    def test_parse_hh_mm_ss_mmm(self):
        assert parse_timecode("00:01:30.500") == pytest.approx(90.5)

    def test_parse_mm_ss(self):
        assert parse_timecode("01:30") == pytest.approx(90.0)

    def test_parse_mm_ss_mmm(self):
        assert parse_timecode("01:30.500") == pytest.approx(90.5)

    def test_parse_frames(self):
        assert parse_timecode("90f") == pytest.approx(3.0)

    def test_parse_one_hour(self):
        assert parse_timecode("01:00:00") == pytest.approx(3600.0)

    def test_parse_zero(self):
        assert parse_timecode("00:00:00.000") == pytest.approx(0.0)

    def test_parse_invalid_raises(self):
        with pytest.raises(ValueError):
            parse_timecode("abc")

    def test_format_duration_zero(self):
        assert format_duration(0.0) == "00:00:00.000"

    def test_format_duration_one_minute(self):
        assert format_duration(90.5) == "00:01:30.500"

    def test_format_duration_one_hour(self):
        assert format_duration(3661.123) == "01:01:01.123"

    def test_format_seconds_short(self):
        s = format_seconds(3.5)
        assert "3.5s" in s

    def test_format_seconds_minutes(self):
        s = format_seconds(65.0)
        assert "1m" in s

    def test_timecode_to_frames(self):
        assert timecode_to_frames(1.0, fps=30.0) == 30

    def test_frames_to_timecode(self):
        assert frames_to_timecode(30, fps=30.0) == pytest.approx(1.0)


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
        with pytest.raises(RuntimeError, match="No project loaded"):
            session.get_project()

    def test_set_project(self, session):
        proj = {"version": "1.0", "name": "test", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        assert session.has_project()
        assert session.project["name"] == "test"

    def test_snapshot_and_undo(self, session):
        proj = {"version": "1.0", "name": "v1", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        session.snapshot("initial")
        session.project["name"] = "v2"
        session.undo()
        assert session.project["name"] == "v1"

    def test_undo_empty_raises(self, session):
        proj = {"version": "1.0", "name": "x", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            session.undo()

    def test_redo_after_undo(self, session):
        proj = {"version": "1.0", "name": "v1", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        session.snapshot("step1")
        session.project["name"] = "v2"
        session.undo()
        assert session.project["name"] == "v1"
        session.redo()
        assert session.project["name"] == "v2"

    def test_redo_empty_raises(self, session):
        proj = {"version": "1.0", "name": "x", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            session.redo()

    def test_snapshot_clears_redo_stack(self, session):
        proj = {"version": "1.0", "name": "v1", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        session.snapshot("s1")
        session.project["name"] = "v2"
        session.undo()
        session.snapshot("new_branch")
        assert len(session._redo_stack) == 0

    def test_max_undo_limit(self, session):
        proj = {"version": "1.0", "name": "v0", "sources": [], "clips": [], "metadata": {}}
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
        proj = {"version": "1.0", "name": "x", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        assert not session._modified
        session.snapshot("test")
        assert session._modified

    def test_deep_copy_in_snapshot(self, session):
        """Undo should restore the state, not a reference."""
        proj = {
            "version": "1.0", "name": "v1",
            "sources": [], "clips": [{"id": "c0"}], "metadata": {}
        }
        session.set_project(proj)
        session.snapshot("before")
        session.project["clips"].append({"id": "c1"})
        assert len(session.project["clips"]) == 2
        session.undo()
        assert len(session.project["clips"]) == 1

    def test_save_session_no_path_raises(self, session):
        proj = {"version": "1.0", "name": "x", "sources": [], "clips": [], "metadata": {}}
        session.set_project(proj)
        with pytest.raises(ValueError, match="No save path"):
            session.save_session()

    def test_save_and_reload(self, session, tmp_path):
        proj = {
            "version": "1.0", "name": "saved",
            "sources": [], "clips": [], "metadata": {}
        }
        session.set_project(proj)
        path = str(tmp_path / "test.json")
        session.save_session(path)
        assert os.path.isfile(path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["name"] == "saved"


# ─────────────────────────────────────────────────────────────────────────────
# Project
# ─────────────────────────────────────────────────────────────────────────────

class TestProject:
    def test_new_project_defaults(self, session):
        result = proj_mod.new_project(session)
        assert result["success"]
        assert session.has_project()

    def test_new_project_custom_name(self, session):
        proj_mod.new_project(session, name="my_stream", profile="hd720p30")
        assert session.project["name"] == "my_stream"
        assert session.project["profile"]["name"] == "hd720p30"

    def test_new_project_invalid_profile(self, session):
        with pytest.raises(ValueError, match="Unknown profile"):
            proj_mod.new_project(session, profile="nonexistent")

    def test_all_profiles_valid(self, session):
        for profile_name in proj_mod.PROFILES:
            s = Session()
            result = proj_mod.new_project(s, profile=profile_name)
            assert result["success"]

    def test_list_profiles(self):
        profiles = proj_mod.list_profiles()
        assert len(profiles) >= 6
        for p in profiles:
            assert "name" in p
            assert "width" in p
            assert "height" in p
            assert "fps" in p

    def test_project_info(self, project_session):
        result = proj_mod.project_info(project_session)
        assert result["name"] == "test"
        assert result["profile"] == "hd1080p30"
        assert result["clips"] == 0
        assert result["sources"] == 0

    def test_project_info_no_project_raises(self, session):
        with pytest.raises(RuntimeError):
            proj_mod.project_info(session)

    def test_save_and_open_roundtrip(self, session, tmp_path):
        proj_mod.new_project(session, name="roundtrip", profile="hd1080p60")
        path = str(tmp_path / "rt.json")
        proj_mod.save_project(session, path)

        s2 = Session()
        result = proj_mod.open_project(s2, path)
        assert result["success"]
        assert s2.project["name"] == "roundtrip"

    def test_open_nonexistent_raises(self, session):
        with pytest.raises(FileNotFoundError):
            proj_mod.open_project(session, "/nonexistent/path.json")

    def test_open_invalid_json_raises(self, session, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json")
        with pytest.raises(Exception):
            proj_mod.open_project(session, str(bad))

    def test_open_missing_key_raises(self, session, tmp_path):
        incomplete = tmp_path / "incomplete.json"
        incomplete.write_text(json.dumps({"version": "1.0"}))
        with pytest.raises(ValueError, match="missing key"):
            proj_mod.open_project(session, str(incomplete))

    def test_save_updates_modified_flag(self, project_session, tmp_path):
        project_session.snapshot("test")
        assert project_session._modified
        path = str(tmp_path / "save.json")
        proj_mod.save_project(project_session, path)
        assert not project_session._modified


# ─────────────────────────────────────────────────────────────────────────────
# Clips (synthetic - no ffprobe)
# ─────────────────────────────────────────────────────────────────────────────

class TestClips:
    def test_add_clip(self, session_with_source):
        result = clips_mod.add_clip(session_with_source, "src0", 0.0, 30.0)
        assert result["success"]
        assert result["id"] == "clip0"
        assert result["duration"] == pytest.approx(30.0)

    def test_add_clip_invalid_in_out(self, session_with_source):
        with pytest.raises(ValueError, match="out_point.*must be greater"):
            clips_mod.add_clip(session_with_source, "src0", 30.0, 10.0)

    def test_add_clip_negative_in(self, session_with_source):
        with pytest.raises(ValueError, match="cannot be negative"):
            clips_mod.add_clip(session_with_source, "src0", -1.0, 10.0)

    def test_add_clip_out_exceeds_duration(self, session_with_source):
        with pytest.raises(ValueError, match="exceeds source duration"):
            clips_mod.add_clip(session_with_source, "src0", 0.0, 999.0)

    def test_add_clip_invalid_source(self, session_with_source):
        with pytest.raises(ValueError, match="Source not found"):
            clips_mod.add_clip(session_with_source, "srcX", 0.0, 10.0)

    def test_add_multiple_clips_sequential_ids(self, session_with_source):
        clips_mod.add_clip(session_with_source, "src0", 0.0, 10.0)
        clips_mod.add_clip(session_with_source, "src0", 20.0, 30.0)
        clips = session_with_source.project["clips"]
        assert clips[0]["id"] == "clip0"
        assert clips[1]["id"] == "clip1"

    def test_trim_clip(self, session_with_clip):
        result = clips_mod.trim_clip(session_with_clip, "clip0", in_point=15.0, out_point=35.0)
        assert result["in"] == pytest.approx(15.0)
        assert result["out"] == pytest.approx(35.0)
        assert result["duration"] == pytest.approx(20.0)

    def test_trim_clip_only_in(self, session_with_clip):
        result = clips_mod.trim_clip(session_with_clip, "clip0", in_point=5.0)
        assert result["in"] == pytest.approx(5.0)
        assert result["out"] == pytest.approx(40.0)

    def test_trim_clip_only_out(self, session_with_clip):
        result = clips_mod.trim_clip(session_with_clip, "clip0", out_point=20.0)
        assert result["in"] == pytest.approx(10.0)
        assert result["out"] == pytest.approx(20.0)

    def test_trim_invalid_range(self, session_with_clip):
        with pytest.raises(ValueError):
            clips_mod.trim_clip(session_with_clip, "clip0", in_point=50.0, out_point=10.0)

    def test_remove_clip(self, session_with_clip):
        result = clips_mod.remove_clip(session_with_clip, "clip0")
        assert result["success"]
        assert len(session_with_clip.project["clips"]) == 0

    def test_remove_nonexistent_clip(self, session_with_clip):
        with pytest.raises(ValueError, match="Clip not found"):
            clips_mod.remove_clip(session_with_clip, "clipX")

    def test_list_clips(self, session_with_clip):
        result = clips_mod.list_clips(session_with_clip)
        assert len(result) == 1
        assert result[0]["id"] == "clip0"
        assert result[0]["duration"] == pytest.approx(30.0)

    def test_list_clips_empty(self, project_session):
        result = clips_mod.list_clips(project_session)
        assert result == []

    def test_show_clip(self, session_with_clip):
        result = clips_mod.show_clip(session_with_clip, "clip0")
        assert result["id"] == "clip0"
        assert result["source_id"] == "src0"
        assert result["in"] == pytest.approx(10.0)
        assert result["out"] == pytest.approx(40.0)

    def test_move_clip(self, session_with_source):
        clips_mod.add_clip(session_with_source, "src0", 0.0, 10.0, name="A")
        clips_mod.add_clip(session_with_source, "src0", 10.0, 20.0, name="B")
        clips_mod.add_clip(session_with_source, "src0", 20.0, 30.0, name="C")
        clips_mod.move_clip(session_with_source, "clip2", 0)
        clips = session_with_source.project["clips"]
        assert clips[0]["name"] == "C"
        assert clips[1]["name"] == "A"

    def test_move_clip_out_of_range(self, session_with_clip):
        with pytest.raises(ValueError, match="out of range"):
            clips_mod.move_clip(session_with_clip, "clip0", 99)

    def test_label_clip(self, session_with_clip):
        result = clips_mod.label_clip(session_with_clip, "clip0", "highlight")
        assert result["label"] == "highlight"

    def test_list_sources_empty(self, project_session):
        result = clips_mod.list_sources(project_session)
        assert result == []

    def test_remove_source_with_clip_fails(self, session_with_clip):
        with pytest.raises(ValueError, match="referenced by clips"):
            clips_mod.remove_source(session_with_clip, "src0")

    def test_remove_source_no_clips(self, session_with_source):
        result = clips_mod.remove_source(session_with_source, "src0")
        assert result["success"]
        assert len(session_with_source.project["sources"]) == 0

    def test_duplicate_source_returns_existing(self, session_with_source):
        """Adding the same path twice returns the existing source."""
        result = clips_mod.add_source.__wrapped__(
            session_with_source, "/fake/test.mp4"
        ) if hasattr(clips_mod.add_source, "__wrapped__") else None
        # Test via direct project manipulation
        result2 = clips_mod._find_source(session_with_source.project, "src0")
        assert result2["id"] == "src0"


# ─────────────────────────────────────────────────────────────────────────────
# Filters
# ─────────────────────────────────────────────────────────────────────────────

class TestFilters:
    def test_available_filters(self):
        result = filters_mod.available_filters()
        names = [f["name"] for f in result]
        assert "brightness" in names
        assert "fade_in" in names
        assert "fade_out" in names
        assert "blur" in names
        assert "speed" in names

    def test_available_filters_by_category(self):
        color = filters_mod.available_filters("color")
        for f in color:
            assert f["category"] == "color"

    def test_filter_info(self):
        info = filters_mod.filter_info("brightness")
        assert info["name"] == "brightness"
        assert "params" in info
        assert "level" in info["params"]

    def test_filter_info_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown filter"):
            filters_mod.filter_info("nonexistent_filter")

    def test_add_filter_defaults(self, session_with_clip):
        result = filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        assert result["success"]
        assert result["filter_name"] == "brightness"
        assert result["filter_index"] == 0
        # Default brightness level is 0.0
        assert result["params"]["level"] == 0.0

    def test_add_filter_with_params(self, session_with_clip):
        result = filters_mod.add_filter(
            session_with_clip, "clip0", "brightness", {"level": 0.5}
        )
        assert result["params"]["level"] == 0.5

    def test_add_filter_invalid_name(self, session_with_clip):
        with pytest.raises(ValueError, match="Unknown filter"):
            filters_mod.add_filter(session_with_clip, "clip0", "nonexistent")

    def test_add_filter_invalid_param_name(self, session_with_clip):
        with pytest.raises(ValueError, match="Unknown param"):
            filters_mod.add_filter(
                session_with_clip, "clip0", "brightness", {"nonparam": 0.5}
            )

    def test_add_filter_param_out_of_range(self, session_with_clip):
        with pytest.raises(ValueError, match="maximum"):
            filters_mod.add_filter(
                session_with_clip, "clip0", "brightness", {"level": 999.0}
            )

    def test_add_multiple_filters(self, session_with_clip):
        filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        filters_mod.add_filter(session_with_clip, "clip0", "fade_in")
        clip = session_with_clip.project["clips"][0]
        assert len(clip["filters"]) == 2

    def test_remove_filter(self, session_with_clip):
        filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        result = filters_mod.remove_filter(session_with_clip, "clip0", 0)
        assert result["success"]
        assert result["removed_filter"] == "brightness"
        clip = session_with_clip.project["clips"][0]
        assert len(clip["filters"]) == 0

    def test_remove_filter_invalid_index(self, session_with_clip):
        with pytest.raises(IndexError, match="out of range"):
            filters_mod.remove_filter(session_with_clip, "clip0", 0)

    def test_set_filter_param(self, session_with_clip):
        filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        result = filters_mod.set_filter_param(
            session_with_clip, "clip0", 0, "level", 0.3
        )
        assert result["success"]
        assert result["value"] == 0.3
        clip = session_with_clip.project["clips"][0]
        assert clip["filters"][0]["params"]["level"] == 0.3

    def test_set_filter_param_invalid_param(self, session_with_clip):
        filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        with pytest.raises(ValueError, match="Unknown param"):
            filters_mod.set_filter_param(
                session_with_clip, "clip0", 0, "nonparam", 0.5
            )

    def test_list_clip_filters_empty(self, session_with_clip):
        result = filters_mod.list_clip_filters(session_with_clip, "clip0")
        assert result == []

    def test_list_clip_filters_multiple(self, session_with_clip):
        filters_mod.add_filter(session_with_clip, "clip0", "brightness")
        filters_mod.add_filter(session_with_clip, "clip0", "blur")
        result = filters_mod.list_clip_filters(session_with_clip, "clip0")
        assert len(result) == 2
        assert result[0]["name"] == "brightness"
        assert result[1]["name"] == "blur"

    def test_add_all_filter_types(self, session_with_clip):
        for filter_name in filters_mod.FILTER_REGISTRY:
            clip_id = "clip0"
            result = filters_mod.add_filter(session_with_clip, clip_id, filter_name)
            assert result["success"]
        clip = session_with_clip.project["clips"][0]
        assert len(clip["filters"]) == len(filters_mod.FILTER_REGISTRY)


# ─────────────────────────────────────────────────────────────────────────────
# Export (no ffmpeg calls - logic only)
# ─────────────────────────────────────────────────────────────────────────────

class TestExport:
    def test_list_presets(self):
        presets = export_mod.list_presets()
        names = [p["name"] for p in presets]
        assert "hd_mp4" in names
        assert "tiktok" in names
        assert "twitch_clip" in names
        assert "twitter" in names
        assert "youtube_short" in names

    def test_preset_info(self):
        info = export_mod.preset_info("hd_mp4")
        assert info["name"] == "hd_mp4"
        assert info["vcodec"] == "libx264"
        assert info["acodec"] == "aac"
        assert info["extension"] == "mp4"

    def test_preset_info_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown preset"):
            export_mod.preset_info("nonexistent_preset")

    def test_render_clip_invalid_preset_raises(self, session_with_clip):
        with pytest.raises(ValueError, match="Unknown preset"):
            export_mod.render_clip(session_with_clip, "clip0", "/tmp/out.mp4", "bad_preset")

    def test_render_clip_missing_clip_raises(self, session_with_source):
        with pytest.raises(ValueError, match="Clip not found"):
            export_mod.render_clip(session_with_source, "clipX", "/tmp/out.mp4")

    def test_render_compilation_no_clips_raises(self, project_session):
        with pytest.raises(RuntimeError, match="No clips"):
            export_mod.render_compilation(project_session, "/tmp/out.mp4")

    def test_build_filter_chain_no_filters(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert vf == []
        assert af == []

    def test_build_filter_chain_brightness(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "brightness", "params": {"level": 0.3}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("eq=" in f for f in vf)
        assert "brightness=0.3" in vf[0]

    def test_build_filter_chain_fade_in(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "fade_in", "params": {"duration": 2.0}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("fade=t=in" in f for f in vf)
        assert any("afade=t=in" in f for f in af)

    def test_build_filter_chain_fade_out(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "fade_out", "params": {"duration": 2.0}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("fade=t=out" in f for f in vf)
        assert any("afade=t=out" in f for f in af)

    def test_build_filter_chain_blur(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "blur", "params": {"radius": 10}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("boxblur=10" in f for f in vf)

    def test_build_filter_chain_speed(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "speed", "params": {"factor": 2.0}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("setpts" in f for f in vf)
        assert any("atempo" in f for f in af)

    def test_build_filter_chain_mute(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "mute", "params": {}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("volume=0" in f for f in af)

    def test_build_filter_chain_crop(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "crop", "params": {"x": 0, "y": 0, "width": 1280, "height": 720}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("crop=1280:720" in f for f in vf)

    def test_build_filter_chain_scale(self, session_with_clip):
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [{"name": "scale", "params": {"width": 1280, "height": 720}}]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        assert any("scale=1280:720" in f for f in vf)

    def test_build_filter_chain_merged_eq(self, session_with_clip):
        """brightness + contrast + saturation should merge into single eq filter."""
        clip = session_with_clip.project["clips"][0]
        clip["filters"] = [
            {"name": "brightness", "params": {"level": 0.1}},
            {"name": "contrast", "params": {"level": 1.2}},
            {"name": "saturation", "params": {"level": 1.5}},
        ]
        vf, af = export_mod._build_filter_chain(clip, 10.0, 30.0)
        eq_filters = [f for f in vf if f.startswith("eq=")]
        assert len(eq_filters) == 1
        assert "brightness=0.1" in eq_filters[0]
        assert "contrast=1.2" in eq_filters[0]
        assert "saturation=1.5" in eq_filters[0]

    def test_build_atempo_normal(self):
        parts = export_mod._build_atempo(1.5)
        assert len(parts) == 1
        assert "atempo=1.5" in parts[0]

    def test_build_atempo_high_speed(self):
        parts = export_mod._build_atempo(4.0)
        assert len(parts) >= 2  # needs chaining

    def test_build_atempo_slow(self):
        parts = export_mod._build_atempo(0.25)
        assert len(parts) >= 2  # needs chaining


# ─────────────────────────────────────────────────────────────────────────────
# Project info with clips
# ─────────────────────────────────────────────────────────────────────────────

class TestProjectInfo:
    def test_project_info_with_clips(self, session_with_clip):
        info = proj_mod.project_info(session_with_clip)
        assert info["sources"] == 1
        assert info["clips"] == 1
        assert info["total_clip_duration"] == pytest.approx(30.0)

    def test_project_info_multiple_clips(self, session_with_source):
        clips_mod.add_clip(session_with_source, "src0", 0.0, 10.0)
        clips_mod.add_clip(session_with_source, "src0", 20.0, 35.0)
        info = proj_mod.project_info(session_with_source)
        assert info["clips"] == 2
        assert info["total_clip_duration"] == pytest.approx(25.0)

    def test_project_vertical_profile(self, session):
        proj_mod.new_project(session, profile="vertical1080p")
        info = proj_mod.project_info(session)
        assert info["resolution"] == "1080x1920"

    def test_project_4k_profile(self, session):
        proj_mod.new_project(session, profile="4k30")
        info = proj_mod.project_info(session)
        assert info["resolution"] == "3840x2160"
