"""Clipper CLI - Export via ffmpeg."""

import os
import subprocess
import json
from typing import Dict, Any, List, Optional

from cli_anything.clipper.core.session import Session


EXPORT_PRESETS: Dict[str, Dict[str, Any]] = {
    "hd_mp4": {
        "description": "HD MP4 H.264 (general purpose)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "6000k",
        "abitrate": "192k",
        "extension": "mp4",
        "extra_args": ["-preset", "medium", "-movflags", "+faststart"],
    },
    "youtube_short": {
        "description": "YouTube Shorts / vertical MP4",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "8000k",
        "abitrate": "192k",
        "extension": "mp4",
        "extra_args": ["-preset", "medium", "-movflags", "+faststart"],
    },
    "tiktok": {
        "description": "TikTok optimized (vertical, H.264)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "6000k",
        "abitrate": "192k",
        "extension": "mp4",
        "extra_args": ["-preset", "fast", "-movflags", "+faststart"],
    },
    "twitch_clip": {
        "description": "Twitch Clip style (H.264, 1080p30)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "6000k",
        "abitrate": "160k",
        "extension": "mp4",
        "extra_args": ["-preset", "fast", "-movflags", "+faststart"],
    },
    "twitter": {
        "description": "Twitter/X video (H.264, ≤140s)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "5000k",
        "abitrate": "128k",
        "extension": "mp4",
        "extra_args": ["-preset", "medium", "-movflags", "+faststart"],
    },
    "instagram": {
        "description": "Instagram Reels (H.264, square/vertical)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vbitrate": "3500k",
        "abitrate": "128k",
        "extension": "mp4",
        "extra_args": ["-preset", "medium", "-movflags", "+faststart"],
    },
    "prores": {
        "description": "Apple ProRes 422 (editing master)",
        "vcodec": "prores_ks",
        "acodec": "pcm_s16le",
        "vbitrate": "0",
        "abitrate": "0",
        "extension": "mov",
        "extra_args": ["-profile:v", "2"],
    },
    "lossless": {
        "description": "FFV1 lossless archive",
        "vcodec": "ffv1",
        "acodec": "flac",
        "vbitrate": "0",
        "abitrate": "0",
        "extension": "mkv",
        "extra_args": [],
    },
    "gif": {
        "description": "Animated GIF (no audio)",
        "vcodec": "gif",
        "acodec": "none",
        "vbitrate": "0",
        "abitrate": "0",
        "extension": "gif",
        "extra_args": [],
    },
    "audio_only": {
        "description": "Audio only (AAC .m4a)",
        "vcodec": "none",
        "acodec": "aac",
        "vbitrate": "0",
        "abitrate": "192k",
        "extension": "m4a",
        "extra_args": [],
    },
}


def list_presets() -> List[Dict[str, Any]]:
    """List available export presets."""
    return [
        {
            "name": k,
            "description": v["description"],
            "vcodec": v["vcodec"],
            "acodec": v["acodec"],
            "extension": v["extension"],
        }
        for k, v in EXPORT_PRESETS.items()
    ]


def preset_info(preset_name: str) -> Dict[str, Any]:
    """Return full details for a preset."""
    if preset_name not in EXPORT_PRESETS:
        available = list(EXPORT_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset_name}'. Available: {available}")
    p = EXPORT_PRESETS[preset_name]
    return {"name": preset_name, **p}


def render_clip(
    session: Session,
    clip_id: str,
    output_path: str,
    preset: str = "hd_mp4",
) -> Dict[str, Any]:
    """Render a single clip to a file using ffmpeg."""
    project = session.get_project()

    clip = _find_clip(project, clip_id)
    src = _find_source(project, clip["source_id"])

    if preset not in EXPORT_PRESETS:
        available = list(EXPORT_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset}'. Available: {available}")

    p = EXPORT_PRESETS[preset]
    in_point = clip["in"]
    out_point = clip["out"]
    duration = out_point - in_point

    # Build filter chain
    vf_parts, af_parts = _build_filter_chain(clip, in_point, duration)

    cmd = ["ffmpeg", "-y"]
    cmd += ["-ss", str(in_point), "-i", src["path"], "-t", str(duration)]

    if vf_parts and p["vcodec"] != "none":
        cmd += ["-vf", ",".join(vf_parts)]
    if af_parts and p["acodec"] != "none":
        cmd += ["-af", ",".join(af_parts)]

    if p["vcodec"] == "none":
        cmd += ["-vn"]
    else:
        cmd += ["-c:v", p["vcodec"]]
        if p["vbitrate"] and p["vbitrate"] != "0":
            cmd += ["-b:v", p["vbitrate"]]

    if p["acodec"] == "none":
        cmd += ["-an"]
    else:
        cmd += ["-c:a", p["acodec"]]
        if p["abitrate"] and p["abitrate"] != "0":
            cmd += ["-b:a", p["abitrate"]]

    cmd += p.get("extra_args", [])

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    cmd.append(output_path)

    result = _run_ffmpeg(cmd)
    probe = _probe_output(output_path)

    return {
        "success": True,
        "clip_id": clip_id,
        "output": output_path,
        "preset": preset,
        "duration": round(duration, 3),
        "probe": probe,
        "ffmpeg_cmd": " ".join(cmd),
    }


def render_compilation(
    session: Session,
    output_path: str,
    preset: str = "hd_mp4",
) -> Dict[str, Any]:
    """Render all clips concatenated into a single output file."""
    project = session.get_project()
    clips = project.get("clips", [])

    if not clips:
        raise RuntimeError("No clips in project to compile.")

    if preset not in EXPORT_PRESETS:
        available = list(EXPORT_PRESETS.keys())
        raise ValueError(f"Unknown preset '{preset}'. Available: {available}")

    p = EXPORT_PRESETS[preset]

    # Write concat list to a temp file
    import tempfile
    segment_files = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for i, clip in enumerate(clips):
            src = _find_source(project, clip["source_id"])
            seg_out = os.path.join(tmp_dir, f"seg_{i:04d}.{p['extension']}")
            _render_segment(
                src_path=src["path"],
                in_point=clip["in"],
                duration=clip["out"] - clip["in"],
                clip=clip,
                output_path=seg_out,
                preset_spec=p,
            )
            segment_files.append(seg_out)

        # Build concat list
        concat_list = os.path.join(tmp_dir, "concat.txt")
        with open(concat_list, "w") as f:
            for seg in segment_files:
                f.write(f"file '{seg}'\n")

        # Concatenate
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            output_path,
        ]

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        _run_ffmpeg(cmd)
        probe = _probe_output(output_path)

        total_duration = sum(c["out"] - c["in"] for c in clips)

        return {
            "success": True,
            "output": output_path,
            "preset": preset,
            "clip_count": len(clips),
            "total_duration": round(total_duration, 3),
            "probe": probe,
        }
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _render_segment(
    src_path: str,
    in_point: float,
    duration: float,
    clip: Dict[str, Any],
    output_path: str,
    preset_spec: Dict[str, Any],
) -> None:
    """Render a single segment to disk (used by render_compilation)."""
    vf_parts, af_parts = _build_filter_chain(clip, in_point, duration)

    cmd = ["ffmpeg", "-y"]
    cmd += ["-ss", str(in_point), "-i", src_path, "-t", str(duration)]

    if vf_parts and preset_spec["vcodec"] != "none":
        cmd += ["-vf", ",".join(vf_parts)]
    if af_parts and preset_spec["acodec"] != "none":
        cmd += ["-af", ",".join(af_parts)]

    if preset_spec["vcodec"] == "none":
        cmd += ["-vn"]
    else:
        cmd += ["-c:v", preset_spec["vcodec"]]
        if preset_spec["vbitrate"] and preset_spec["vbitrate"] != "0":
            cmd += ["-b:v", preset_spec["vbitrate"]]

    if preset_spec["acodec"] == "none":
        cmd += ["-an"]
    else:
        cmd += ["-c:a", preset_spec["acodec"]]
        if preset_spec["abitrate"] and preset_spec["abitrate"] != "0":
            cmd += ["-b:a", preset_spec["abitrate"]]

    cmd += preset_spec.get("extra_args", [])
    cmd.append(output_path)
    _run_ffmpeg(cmd)


def _build_filter_chain(
    clip: Dict[str, Any], in_point: float, duration: float
) -> tuple[List[str], List[str]]:
    """Translate clip filters to ffmpeg vf/af filter strings."""
    vf_parts: List[str] = []
    af_parts: List[str] = []

    eq_params: Dict[str, float] = {}

    for f_entry in clip.get("filters", []):
        name = f_entry["name"]
        params = f_entry.get("params", {})

        if name == "brightness":
            eq_params["brightness"] = float(params.get("level", 0.0))
        elif name == "contrast":
            eq_params["contrast"] = float(params.get("level", 1.0))
        elif name == "saturation":
            eq_params["saturation"] = float(params.get("level", 1.0))
        elif name == "blur":
            r = int(params.get("radius", 5))
            vf_parts.append(f"boxblur={r}:{r}")
        elif name == "fade_in":
            d = float(params.get("duration", 1.0))
            vf_parts.append(f"fade=t=in:st=0:d={d}")
            af_parts.append(f"afade=t=in:st=0:d={d}")
        elif name == "fade_out":
            d = float(params.get("duration", 1.0))
            start = max(0.0, duration - d)
            vf_parts.append(f"fade=t=out:st={start:.3f}:d={d}")
            af_parts.append(f"afade=t=out:st={start:.3f}:d={d}")
        elif name == "crop":
            x = int(params.get("x", 0))
            y = int(params.get("y", 0))
            w = int(params.get("width", 1920))
            h = int(params.get("height", 1080))
            vf_parts.append(f"crop={w}:{h}:{x}:{y}")
        elif name == "scale":
            w = int(params.get("width", 1920))
            h = int(params.get("height", 1080))
            vf_parts.append(f"scale={w}:{h}")
        elif name == "speed":
            factor = float(params.get("factor", 1.0))
            if factor != 1.0:
                pts_factor = round(1.0 / factor, 6)
                vf_parts.append(f"setpts={pts_factor}*PTS")
                # audio speed: atempo supports 0.5-2.0 range, chain for extremes
                af_parts += _build_atempo(factor)
        elif name == "volume":
            level = float(params.get("level", 1.0))
            af_parts.append(f"volume={level}")
        elif name == "mute":
            af_parts.append("volume=0")

    # Merge eq params into a single filter
    if eq_params:
        eq_str = ":".join(f"{k}={v}" for k, v in eq_params.items())
        vf_parts.insert(0, f"eq={eq_str}")

    return vf_parts, af_parts


def _build_atempo(factor: float) -> List[str]:
    """Build atempo filter chain for speed factor (handles 0.5-2.0 limit)."""
    parts = []
    remaining = factor
    while remaining > 2.0:
        parts.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        parts.append("atempo=0.5")
        remaining /= 0.5
    parts.append(f"atempo={remaining:.4f}")
    return parts


def _run_ffmpeg(cmd: List[str]) -> subprocess.CompletedProcess:
    """Run an ffmpeg command, raising on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Install ffmpeg to use export features.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("ffmpeg timed out during export.")

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-2000:]}")

    return result


def _probe_output(path: str) -> Optional[Dict[str, Any]]:
    """Probe the output file with ffprobe for verification."""
    if not os.path.isfile(path):
        return None
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-print_format", "json",
            "-show_streams", "-show_format",
            path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None
        data = json.loads(result.stdout)
        fmt = data.get("format", {})
        return {
            "duration": round(float(fmt.get("duration", 0)), 3),
            "size_bytes": int(fmt.get("size", 0)),
            "format": fmt.get("format_name", ""),
        }
    except Exception:
        return None


def _find_clip(project: Dict[str, Any], clip_id: str) -> Dict[str, Any]:
    for clip in project["clips"]:
        if clip["id"] == clip_id:
            return clip
    available = [c["id"] for c in project["clips"]]
    raise ValueError(f"Clip not found: '{clip_id}'. Available: {available}")


def _find_source(project: Dict[str, Any], source_id: str) -> Dict[str, Any]:
    for src in project["sources"]:
        if src["id"] == source_id:
            return src
    available = [s["id"] for s in project["sources"]]
    raise ValueError(f"Source not found: '{source_id}'. Available: {available}")
