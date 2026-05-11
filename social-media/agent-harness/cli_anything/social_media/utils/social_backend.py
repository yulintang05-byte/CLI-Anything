"""Social Media backend utilities — dependency checks and health validation."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass


@dataclass
class DependencyStatus:
    name: str
    available: bool
    version: str
    install_command: str
    required: bool


def check_ytdlp() -> DependencyStatus:
    """Check whether yt-dlp is installed and working."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        available = result.returncode == 0
        version = result.stdout.strip() if available else ""
        return DependencyStatus(
            name="yt-dlp",
            available=available,
            version=version,
            install_command="pip install yt-dlp",
            required=True,
        )
    except Exception:
        return DependencyStatus(
            name="yt-dlp",
            available=False,
            version="",
            install_command="pip install yt-dlp",
            required=True,
        )


def check_all_dependencies() -> list[DependencyStatus]:
    """Check all dependencies for the social media harness."""
    deps = [check_ytdlp()]

    # Optional: ffmpeg for media processing
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
        )
        available = result.returncode == 0
        version = result.stdout.splitlines()[0] if available else ""
        deps.append(DependencyStatus(
            name="ffmpeg",
            available=available,
            version=version,
            install_command="apt install ffmpeg  OR  brew install ffmpeg",
            required=False,
        ))
    except Exception:
        deps.append(DependencyStatus(
            name="ffmpeg",
            available=False,
            version="",
            install_command="apt install ffmpeg  OR  brew install ffmpeg",
            required=False,
        ))

    return deps


def assert_ytdlp_installed() -> None:
    """Raise RuntimeError with install instructions if yt-dlp is missing."""
    status = check_ytdlp()
    if not status.available:
        raise RuntimeError(
            "yt-dlp is required for scraping. Install it with:\n"
            "  pip install yt-dlp\n\n"
            "Then verify: python -m yt_dlp --version"
        )
