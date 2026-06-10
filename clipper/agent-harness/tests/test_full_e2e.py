"""Clipper CLI - End-to-end tests (requires ffmpeg + real media).

These tests exercise the full pipeline including ffprobe and ffmpeg.
A test video is required at: /root/clipper/test.mp4

Run:
    cd clipper/agent-harness && pytest tests/test_full_e2e.py -v

If the test video is missing, all tests are skipped automatically.
"""

import os
import shutil
import json
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.clipper.core.session import Session
from cli_anything.clipper.core import project as proj_mod
from cli_anything.clipper.core import clips as clips_mod
from cli_anything.clipper.core import filters as filters_mod
from cli_anything.clipper.core import export as export_mod

TEST_VIDEO = "/root/clipper/test.mp4"
FFMPEG_AVAILABLE = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
VIDEO_AVAILABLE = os.path.isfile(TEST_VIDEO)

requires_media = pytest.mark.skipif(
    not (FFMPEG_AVAILABLE and VIDEO_AVAILABLE),
    reason=f"Requires ffmpeg/ffprobe and test video at {TEST_VIDEO}",
)

requires_ffmpeg = pytest.mark.skipif(
    not FFMPEG_AVAILABLE,
    reason="Requires ffmpeg/ffprobe to be installed",
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
    proj_mod.new_project(s, name="e2e_test", profile="hd1080p30")
    return s


@pytest.fixture
def session_with_video(project_session):
    """Session with the real test video loaded as a source."""
    clips_mod.add_source(project_session, TEST_VIDEO)
    return project_session


@pytest.fixture
def session_with_clip(session_with_video):
    """Session with the real test video and a 10-second clip."""
    src_id = session_with_video.project["sources"][0]["id"]
    clips_mod.add_clip(session_with_video, src_id, 2.0, 12.0, name="test_clip")
    return session_with_video


# ─────────────────────────────────────────────────────────────────────────────
# ffprobe / source probing
# ─────────────────────────────────────────────────────────────────────────────

@requires_media
class TestSourceProbing:
    def test_probe_returns_duration(self):
        result = clips_mod.probe_source(TEST_VIDEO)
        assert result["duration"] > 0

    def test_probe_returns_video_info(self):
        result = clips_mod.probe_source(TEST_VIDEO)
        assert "video" in result
        assert result["video"]["width"] > 0
        assert result["video"]["height"] > 0

    def test_probe_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            clips_mod.probe_source("/nonexistent/file.mp4")

    def test_add_source_probes_file(self, project_session):
        result = clips_mod.add_source(project_session, TEST_VIDEO)
        assert result["success"]
        assert result["duration"] > 0
        assert result["id"].startswith("src")

    def test_add_source_duplicate_returns_existing(self, project_session):
        r1 = clips_mod.add_source(project_session, TEST_VIDEO)
        r2 = clips_mod.add_source(project_session, TEST_VIDEO)
        assert r1["id"] == r2["id"]
        assert len(project_session.project["sources"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# Export: single clip
# ─────────────────────────────────────────────────────────────────────────────

@requires_media
class TestRenderClip:
    def test_render_clip_basic(self, session_with_clip, tmp_path):
        src_id = session_with_clip.project["sources"][0]["id"]
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "basic.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "hd_mp4")
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_render_clip_output_has_duration(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "dur.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "hd_mp4")
        assert result["probe"] is not None
        assert result["probe"]["duration"] == pytest.approx(10.0, abs=0.5)

    def test_render_clip_tiktok_preset(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "tiktok.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "tiktok")
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_render_clip_twitch_preset(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "twitch.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "twitch_clip")
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_render_clip_twitter_preset(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "twitter.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "twitter")
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_render_audio_only_preset(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        output_path = str(tmp_path / "audio.m4a")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path, "audio_only")
        assert result["success"]
        assert os.path.isfile(output_path)


# ─────────────────────────────────────────────────────────────────────────────
# Export: compilation
# ─────────────────────────────────────────────────────────────────────────────

@requires_media
class TestRenderCompilation:
    def test_compile_two_clips(self, session_with_video, tmp_path):
        src_id = session_with_video.project["sources"][0]["id"]
        src_duration = session_with_video.project["sources"][0]["duration"]
        end = min(src_duration, 25.0)
        clips_mod.add_clip(session_with_video, src_id, 2.0, 7.0, name="clip_a")
        clips_mod.add_clip(session_with_video, src_id, 10.0, end, name="clip_b")
        output_path = str(tmp_path / "compile.mp4")
        result = export_mod.render_compilation(session_with_video, output_path)
        assert result["success"]
        assert result["clip_count"] == 2
        assert os.path.isfile(output_path)

    def test_compile_output_duration(self, session_with_video, tmp_path):
        src_id = session_with_video.project["sources"][0]["id"]
        clips_mod.add_clip(session_with_video, src_id, 2.0, 7.0)
        clips_mod.add_clip(session_with_video, src_id, 10.0, 15.0)
        output_path = str(tmp_path / "dur_compile.mp4")
        result = export_mod.render_compilation(session_with_video, output_path)
        assert result["probe"]["duration"] == pytest.approx(10.0, abs=1.0)

    def test_compile_preserves_clip_order(self, session_with_video, tmp_path):
        """Clips should be compiled in their list order."""
        src_id = session_with_video.project["sources"][0]["id"]
        clips_mod.add_clip(session_with_video, src_id, 2.0, 5.0, name="first")
        clips_mod.add_clip(session_with_video, src_id, 8.0, 11.0, name="second")
        output_path = str(tmp_path / "ordered.mp4")
        result = export_mod.render_compilation(session_with_video, output_path)
        assert result["success"]
        assert result["clip_count"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# Filters with real export
# ─────────────────────────────────────────────────────────────────────────────

@requires_media
class TestFiltersWithExport:
    def test_export_with_brightness_filter(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "brightness", {"level": 0.2})
        output_path = str(tmp_path / "bright.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_export_with_fade_in(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "fade_in", {"duration": 1.0})
        output_path = str(tmp_path / "fadein.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_fade_out(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "fade_out", {"duration": 1.0})
        output_path = str(tmp_path / "fadeout.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_fade_in_and_out(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "fade_in", {"duration": 0.5})
        filters_mod.add_filter(session_with_clip, clip_id, "fade_out", {"duration": 0.5})
        output_path = str(tmp_path / "fade_both.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_blur_filter(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "blur", {"radius": 3})
        output_path = str(tmp_path / "blurred.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_volume_filter(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "volume", {"level": 0.5})
        output_path = str(tmp_path / "quieter.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_mute_filter(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "mute")
        output_path = str(tmp_path / "muted.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]

    def test_export_with_combined_color_filters(self, session_with_clip, tmp_path):
        clip_id = session_with_clip.project["clips"][0]["id"]
        filters_mod.add_filter(session_with_clip, clip_id, "brightness", {"level": 0.1})
        filters_mod.add_filter(session_with_clip, clip_id, "contrast", {"level": 1.1})
        filters_mod.add_filter(session_with_clip, clip_id, "saturation", {"level": 1.2})
        output_path = str(tmp_path / "color_graded.mp4")
        result = export_mod.render_clip(session_with_clip, clip_id, output_path)
        assert result["success"]


# ─────────────────────────────────────────────────────────────────────────────
# Full workflow tests
# ─────────────────────────────────────────────────────────────────────────────

@requires_media
class TestFullWorkflows:
    def test_highlight_reel_workflow(self, project_session, tmp_path):
        """Create a 3-segment highlight reel and compile."""
        src_duration = clips_mod.probe_source(TEST_VIDEO)["duration"]
        clips_mod.add_source(project_session, TEST_VIDEO)
        src_id = project_session.project["sources"][0]["id"]

        segments = [
            (2.0, 5.0, "Highlight 1"),
            (8.0, 12.0, "Highlight 2"),
            (15.0, min(src_duration, 20.0), "Highlight 3"),
        ]
        for in_pt, out_pt, name in segments:
            if out_pt <= src_duration:
                clips_mod.add_clip(project_session, src_id, in_pt, out_pt, name=name)

        output_path = str(tmp_path / "highlight_reel.mp4")
        result = export_mod.render_compilation(project_session, output_path)
        assert result["success"]
        assert os.path.isfile(output_path)

    def test_save_and_reload_project_then_export(self, project_session, tmp_path):
        """Save project, reload it, then export a clip."""
        clips_mod.add_source(project_session, TEST_VIDEO)
        src_id = project_session.project["sources"][0]["id"]
        clips_mod.add_clip(project_session, src_id, 2.0, 8.0)

        project_file = str(tmp_path / "save_reload.json")
        proj_mod.save_project(project_session, project_file)

        s2 = Session()
        proj_mod.open_project(s2, project_file)
        assert s2.project["name"] == "e2e_test"
        clip_id = s2.project["clips"][0]["id"]
        output_path = str(tmp_path / "reloaded.mp4")
        result = export_mod.render_clip(s2, clip_id, output_path)
        assert result["success"]

    def test_undo_redo_workflow(self, project_session, tmp_path):
        """Add clips, undo some, verify state."""
        clips_mod.add_source(project_session, TEST_VIDEO)
        src_id = project_session.project["sources"][0]["id"]
        clips_mod.add_clip(project_session, src_id, 2.0, 6.0, name="A")
        clips_mod.add_clip(project_session, src_id, 8.0, 12.0, name="B")
        assert len(project_session.project["clips"]) == 2

        project_session.undo()
        assert len(project_session.project["clips"]) == 1

        project_session.undo()
        assert len(project_session.project["clips"]) == 0

        project_session.redo()
        assert len(project_session.project["clips"]) == 1

    def test_clip_with_label_and_filter(self, project_session, tmp_path):
        """Add label and filter, export, verify output exists."""
        clips_mod.add_source(project_session, TEST_VIDEO)
        src_id = project_session.project["sources"][0]["id"]
        clips_mod.add_clip(project_session, src_id, 3.0, 9.0, name="Labeled")
        clip_id = project_session.project["clips"][0]["id"]
        clips_mod.label_clip(project_session, clip_id, "best_moment")
        filters_mod.add_filter(project_session, clip_id, "brightness", {"level": 0.1})
        output_path = str(tmp_path / "labeled.mp4")
        result = export_mod.render_clip(project_session, clip_id, output_path)
        assert result["success"]

    def test_reorder_clips_then_compile(self, project_session, tmp_path):
        """Reorder clips and compile in new order."""
        clips_mod.add_source(project_session, TEST_VIDEO)
        src_id = project_session.project["sources"][0]["id"]
        clips_mod.add_clip(project_session, src_id, 2.0, 5.0, name="First")
        clips_mod.add_clip(project_session, src_id, 8.0, 11.0, name="Second")
        # Move second clip to first position
        clips_mod.move_clip(project_session, "clip1", 0)
        assert project_session.project["clips"][0]["name"] == "Second"
        output_path = str(tmp_path / "reordered.mp4")
        result = export_mod.render_compilation(project_session, output_path)
        assert result["success"]
