"""Clipper CLI - Clip and source management."""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional

from cli_anything.clipper.core.session import Session
from cli_anything.clipper.utils.time import parse_timecode, format_duration


def _next_id(items: List[Dict[str, Any]], prefix: str) -> str:
    """Generate the next sequential ID for a list of items."""
    used = {item.get("id", "") for item in items}
    i = 0
    while f"{prefix}{i}" in used:
        i += 1
    return f"{prefix}{i}"


def probe_source(path: str) -> Dict[str, Any]:
    """Use ffprobe to get metadata about a video file."""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")

    cmd = [
        "ffprobe", "-v", "error",
        "-print_format", "json",
        "-show_streams", "-show_format",
        path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except FileNotFoundError:
        raise RuntimeError("ffprobe not found. Install ffmpeg to use this feature.")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"ffprobe timed out probing: {path}")

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe error: {result.stderr.strip()}")

    data = json.loads(result.stdout)
    fmt = data.get("format", {})
    streams = data.get("streams", [])

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = float(fmt.get("duration", 0.0))
    size = int(fmt.get("size", 0))

    info: Dict[str, Any] = {
        "path": path,
        "duration": round(duration, 3),
        "size_bytes": size,
        "format": fmt.get("format_name", "unknown"),
        "bit_rate": int(fmt.get("bit_rate", 0)),
    }

    if video_stream:
        r_frame_rate = video_stream.get("r_frame_rate", "0/1")
        try:
            num, den = r_frame_rate.split("/")
            fps = round(int(num) / int(den), 3) if int(den) != 0 else 0
        except Exception:
            fps = 0
        info["video"] = {
            "codec": video_stream.get("codec_name", "unknown"),
            "width": video_stream.get("width", 0),
            "height": video_stream.get("height", 0),
            "fps": fps,
            "pix_fmt": video_stream.get("pix_fmt", "unknown"),
        }

    if audio_stream:
        info["audio"] = {
            "codec": audio_stream.get("codec_name", "unknown"),
            "sample_rate": int(audio_stream.get("sample_rate", 0)),
            "channels": audio_stream.get("channels", 0),
        }

    return info


def add_source(session: Session, path: str, name: Optional[str] = None) -> Dict[str, Any]:
    """Import a video file as a source."""
    project = session.get_project()
    abs_path = os.path.abspath(path)

    # Check for duplicate
    for src in project["sources"]:
        if src["path"] == abs_path:
            return {
                "success": True,
                "id": src["id"],
                "name": src["name"],
                "path": abs_path,
                "duration": src["duration"],
                "already_exists": True,
            }

    probe = probe_source(abs_path)
    src_id = _next_id(project["sources"], "src")
    src_name = name or os.path.basename(abs_path)

    source = {
        "id": src_id,
        "name": src_name,
        "path": abs_path,
        "duration": probe["duration"],
        "video": probe.get("video"),
        "audio": probe.get("audio"),
        "format": probe.get("format", "unknown"),
    }

    session.snapshot(f"Add source {src_name}")
    project["sources"].append(source)

    return {
        "success": True,
        "id": src_id,
        "name": src_name,
        "path": abs_path,
        "duration": probe["duration"],
        "video": probe.get("video"),
        "audio": probe.get("audio"),
    }


def remove_source(session: Session, source_id: str) -> Dict[str, Any]:
    """Remove a source. Fails if any clips reference it."""
    project = session.get_project()

    src = _find_source(project, source_id)
    # Check if any clips reference this source
    dependent_clips = [c["id"] for c in project["clips"] if c["source_id"] == source_id]
    if dependent_clips:
        raise ValueError(
            f"Cannot remove source '{source_id}': "
            f"referenced by clips {dependent_clips}. Remove clips first."
        )

    session.snapshot(f"Remove source {source_id}")
    project["sources"] = [s for s in project["sources"] if s["id"] != source_id]

    return {"success": True, "removed_source_id": source_id, "name": src["name"]}


def list_sources(session: Session) -> List[Dict[str, Any]]:
    """List all sources in the project."""
    project = session.get_project()
    result = []
    for src in project["sources"]:
        result.append({
            "id": src["id"],
            "name": src["name"],
            "path": src["path"],
            "duration": src["duration"],
            "duration_fmt": format_duration(src["duration"]),
            "video": src.get("video"),
            "audio": src.get("audio"),
        })
    return result


def add_clip(
    session: Session,
    source_id: str,
    in_point: float,
    out_point: float,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Define a clip segment from a source."""
    project = session.get_project()

    src = _find_source(project, source_id)

    if in_point < 0:
        raise ValueError(f"in_point cannot be negative: {in_point}")
    if out_point <= in_point:
        raise ValueError(f"out_point ({out_point}) must be greater than in_point ({in_point})")
    if out_point > src["duration"] + 0.1:
        raise ValueError(
            f"out_point ({out_point}) exceeds source duration ({src['duration']})"
        )

    clip_id = _next_id(project["clips"], "clip")
    clip_name = name or f"Clip {len(project['clips']) + 1}"

    clip = {
        "id": clip_id,
        "source_id": source_id,
        "name": clip_name,
        "in": round(in_point, 3),
        "out": round(out_point, 3),
        "filters": [],
        "label": "",
    }

    session.snapshot(f"Add clip {clip_name}")
    project["clips"].append(clip)

    return {
        "success": True,
        "id": clip_id,
        "name": clip_name,
        "source_id": source_id,
        "in": clip["in"],
        "out": clip["out"],
        "duration": round(out_point - in_point, 3),
    }


def trim_clip(
    session: Session,
    clip_id: str,
    in_point: Optional[float] = None,
    out_point: Optional[float] = None,
) -> Dict[str, Any]:
    """Adjust in/out points of a clip."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)
    src = _find_source(project, clip["source_id"])

    new_in = in_point if in_point is not None else clip["in"]
    new_out = out_point if out_point is not None else clip["out"]

    if new_in < 0:
        raise ValueError(f"in_point cannot be negative: {new_in}")
    if new_out <= new_in:
        raise ValueError(f"out_point ({new_out}) must be greater than in_point ({new_in})")
    if new_out > src["duration"] + 0.1:
        raise ValueError(
            f"out_point ({new_out}) exceeds source duration ({src['duration']})"
        )

    session.snapshot(f"Trim clip {clip_id}")
    clip["in"] = round(new_in, 3)
    clip["out"] = round(new_out, 3)

    return {
        "success": True,
        "id": clip_id,
        "name": clip["name"],
        "in": clip["in"],
        "out": clip["out"],
        "duration": round(clip["out"] - clip["in"], 3),
    }


def remove_clip(session: Session, clip_id: str) -> Dict[str, Any]:
    """Remove a clip from the project."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)

    session.snapshot(f"Remove clip {clip_id}")
    project["clips"] = [c for c in project["clips"] if c["id"] != clip_id]

    return {"success": True, "removed_clip_id": clip_id, "name": clip["name"]}


def list_clips(session: Session) -> List[Dict[str, Any]]:
    """List all clips in the project."""
    project = session.get_project()
    result = []
    for i, clip in enumerate(project["clips"]):
        duration = round(clip.get("out", 0.0) - clip.get("in", 0.0), 3)
        result.append({
            "index": i,
            "id": clip["id"],
            "name": clip["name"],
            "source_id": clip["source_id"],
            "in": clip["in"],
            "out": clip["out"],
            "duration": duration,
            "duration_fmt": format_duration(duration),
            "filter_count": len(clip.get("filters", [])),
            "label": clip.get("label", ""),
        })
    return result


def show_clip(session: Session, clip_id: str) -> Dict[str, Any]:
    """Show detailed info for a single clip."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)
    src = _find_source(project, clip["source_id"])
    duration = round(clip["out"] - clip["in"], 3)

    return {
        "id": clip["id"],
        "name": clip["name"],
        "label": clip.get("label", ""),
        "source_id": clip["source_id"],
        "source_name": src["name"],
        "source_path": src["path"],
        "in": clip["in"],
        "out": clip["out"],
        "duration": duration,
        "duration_fmt": format_duration(duration),
        "filters": clip.get("filters", []),
    }


def move_clip(session: Session, clip_id: str, new_index: int) -> Dict[str, Any]:
    """Reorder a clip to a new position in the clips list."""
    project = session.get_project()
    clips = project["clips"]

    idx = next((i for i, c in enumerate(clips) if c["id"] == clip_id), None)
    if idx is None:
        raise ValueError(f"Clip not found: {clip_id}")

    if new_index < 0 or new_index >= len(clips):
        raise ValueError(f"Index {new_index} out of range (0-{len(clips) - 1})")

    session.snapshot(f"Move clip {clip_id} to index {new_index}")
    clip = clips.pop(idx)
    clips.insert(new_index, clip)

    return {
        "success": True,
        "id": clip_id,
        "name": clip["name"],
        "new_index": new_index,
    }


def label_clip(session: Session, clip_id: str, label: str) -> Dict[str, Any]:
    """Set a label on a clip."""
    project = session.get_project()
    clip = _find_clip(project, clip_id)

    session.snapshot(f"Label clip {clip_id}")
    clip["label"] = label

    return {"success": True, "id": clip_id, "label": label}


def _find_source(project: Dict[str, Any], source_id: str) -> Dict[str, Any]:
    for src in project["sources"]:
        if src["id"] == source_id:
            return src
    available = [s["id"] for s in project["sources"]]
    raise ValueError(f"Source not found: '{source_id}'. Available: {available}")


def _find_clip(project: Dict[str, Any], clip_id: str) -> Dict[str, Any]:
    for clip in project["clips"]:
        if clip["id"] == clip_id:
            return clip
    available = [c["id"] for c in project["clips"]]
    raise ValueError(f"Clip not found: '{clip_id}'. Available: {available}")
