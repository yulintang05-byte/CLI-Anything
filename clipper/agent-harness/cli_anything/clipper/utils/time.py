"""Clipper CLI - Timecode utilities."""

import re
from typing import Union


def parse_timecode(tc: Union[str, float, int]) -> float:
    """Parse a timecode string or number into seconds (float).

    Accepts:
        - Decimal seconds: "10.5", 10.5
        - HH:MM:SS.mmm: "00:01:30.500"
        - HH:MM:SS: "00:01:30"
        - MM:SS.mmm: "01:30.500"
        - MM:SS: "01:30"
        - Frames at 30fps: "45f" -> 1.5s

    Returns:
        Seconds as a float.
    """
    if isinstance(tc, (int, float)):
        return float(tc)

    tc = str(tc).strip()

    # Frames notation (e.g. "90f" at 30fps)
    frame_match = re.fullmatch(r"(\d+)f", tc)
    if frame_match:
        return int(frame_match.group(1)) / 30.0

    # HH:MM:SS.mmm or HH:MM:SS
    hms_match = re.fullmatch(
        r"(\d+):(\d{2}):(\d{2})(?:[.,](\d+))?", tc
    )
    if hms_match:
        h, m, s = int(hms_match.group(1)), int(hms_match.group(2)), int(hms_match.group(3))
        frac = hms_match.group(4)
        seconds = h * 3600 + m * 60 + s
        if frac:
            seconds += int(frac) / (10 ** len(frac))
        return float(seconds)

    # MM:SS.mmm or MM:SS
    ms_match = re.fullmatch(r"(\d+):(\d{2})(?:[.,](\d+))?", tc)
    if ms_match:
        m, s = int(ms_match.group(1)), int(ms_match.group(2))
        frac = ms_match.group(3)
        seconds = m * 60 + s
        if frac:
            seconds += int(frac) / (10 ** len(frac))
        return float(seconds)

    # Plain decimal or integer
    try:
        return float(tc)
    except ValueError:
        raise ValueError(
            f"Cannot parse timecode: {tc!r}. "
            "Expected formats: 10.5 | 00:01:30.500 | 01:30 | 90f"
        )


def format_duration(seconds: float) -> str:
    """Format a duration in seconds to HH:MM:SS.mmm string.

    Examples:
        0.0      -> "00:00:00.000"
        90.5     -> "00:01:30.500"
        3661.123 -> "01:01:01.123"
    """
    if seconds < 0:
        seconds = 0.0

    total_ms = round(seconds * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60

    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def format_seconds(seconds: float) -> str:
    """Format seconds as a compact human-readable string.

    Examples:
        65.0  -> "1m 5s"
        3.5   -> "3.5s"
        3661  -> "1h 1m 1s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def timecode_to_frames(seconds: float, fps: float = 30.0) -> int:
    """Convert seconds to frame number at given FPS."""
    return round(seconds * fps)


def frames_to_timecode(frames: int, fps: float = 30.0) -> float:
    """Convert frame number to seconds at given FPS."""
    return frames / fps
