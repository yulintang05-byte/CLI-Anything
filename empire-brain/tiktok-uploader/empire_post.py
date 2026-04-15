#!/usr/bin/env python3
"""
Empire TikTok Post Pipeline
Connects Deep-Live-Cam output → TiktokAutoUploader → TikTok

Verified against makiisthenes/TiktokAutoUploader cli.py (upload subcommand):
  -u/--users        cookie name (from `login -n`)
  -v/--video        filename inside ./VideosDirPath
  -yt/--youtube     YouTube URL (mutually exclusive with -v)
  -t/--title        caption
  -sc/--schedule    int seconds from now (TikTok: 15min..10days)
  -ct/--comment     0|1 (default 1)
  -vi/--visibility  0 public, 1 private (default 0)

Cookies live at ./CookiesDir/tiktok_session-<name>.cookie

Usage:
  python3 empire_post.py --video path/to/video.mp4 --title "Your title" [--schedule "2026-04-16 18:00"]
  python3 empire_post.py --youtube "https://youtube.com/shorts/..." --title "Repost title"
  python3 empire_post.py --watch-folder ~/passive-income/output/ --auto
"""

import subprocess
import sys
import os
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime

EMPIRE_DIR = Path.home() / "passive-income"
UPLOADER_DIR = EMPIRE_DIR / "TiktokAutoUploader"
VIDEOS_DIR = UPLOADER_DIR / "VideosDirPath"
COOKIES_DIR = UPLOADER_DIR / "CookiesDir"
LOG_FILE = EMPIRE_DIR / "post_log.json"
ACCOUNT = "luckylefty0511"


def log_post(video, title, status, error=None):
    """Append post result to log."""
    log = []
    if LOG_FILE.exists():
        log = json.loads(LOG_FILE.read_text())
    log.append({
        "timestamp": datetime.now().isoformat(),
        "video": str(video),
        "title": title,
        "status": status,
        "error": error,
        "account": ACCOUNT,
    })
    LOG_FILE.write_text(json.dumps(log, indent=2))


def stage_video(video_path):
    """Copy video into ./VideosDirPath (CLI requires it there) and return filename."""
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    dest = VIDEOS_DIR / video_path.name
    if not dest.exists() or dest.stat().st_size != video_path.stat().st_size:
        shutil.copy2(video_path, dest)
    return dest.name


def schedule_to_seconds(schedule_str):
    """Convert 'YYYY-MM-DD HH:MM' to seconds from now. TikTok allows 15min..10days."""
    when = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M")
    delta = int((when - datetime.now()).total_seconds())
    if delta < 15 * 60:
        raise ValueError("Schedule must be at least 15 minutes in the future")
    if delta > 10 * 24 * 3600:
        raise ValueError("Schedule cannot be more than 10 days in the future")
    return delta


def upload_video(video_path, title, schedule=None, user=ACCOUNT, visibility="public"):
    """Upload a single local video to TikTok."""
    filename = stage_video(video_path)
    vi = 0 if visibility == "public" else 1

    cmd = [
        "python3", "cli.py", "upload",
        "-u", user,
        "-v", filename,
        "-t", title,
        "-ct", "1",
        "-vi", str(vi),
    ]
    if schedule:
        cmd += ["-sc", str(schedule_to_seconds(schedule))]

    print(f"\n📤 Uploading: {video_path.name}")
    print(f"   Title: {title}")
    if schedule:
        print(f"   Scheduled: {schedule}")

    result = subprocess.run(cmd, cwd=UPLOADER_DIR, capture_output=True, text=True)

    if result.returncode == 0:
        print("   ✅ Upload success")
        log_post(video_path, title, "success")
        return True
    err = result.stderr or result.stdout
    print(f"   ❌ Upload failed: {err[:200]}")
    log_post(video_path, title, "failed", err[:500])
    return False


def upload_youtube(url, title, user=ACCOUNT, visibility="public"):
    """Repost a YouTube video to TikTok (uploader downloads it)."""
    vi = 0 if visibility == "public" else 1
    cmd = [
        "python3", "cli.py", "upload",
        "-u", user,
        "-yt", url,
        "-t", title,
        "-ct", "1",
        "-vi", str(vi),
    ]
    print(f"\n📤 Uploading from YouTube: {url}")
    result = subprocess.run(cmd, cwd=UPLOADER_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Upload success")
        log_post(url, title, "success")
        return True
    err = result.stderr or result.stdout
    print(f"   ❌ Upload failed: {err[:200]}")
    log_post(url, title, "failed", err[:500])
    return False


def watch_folder(folder, auto=False):
    """Watch a folder and upload any new .mp4 files."""
    folder = Path(folder)
    uploaded_tracker = folder / ".uploaded.json"
    uploaded = set()
    if uploaded_tracker.exists():
        uploaded = set(json.loads(uploaded_tracker.read_text()))

    print(f"\n👁️  Watching: {folder}")
    print(f"   Auto-title: {'on' if auto else 'off (will prompt)'}")

    for video in sorted(folder.glob("*.mp4")):
        if str(video) in uploaded:
            continue

        if auto:
            title = video.stem.replace("_", " ").replace("-", " ").title()
        else:
            title = input(f"\nTitle for {video.name} (Enter to skip): ").strip()
            if not title:
                continue

        if upload_video(video, title):
            uploaded.add(str(video))
            uploaded_tracker.write_text(json.dumps(list(uploaded)))


def check_login():
    """Verify a TikTok session cookie exists for the account."""
    cookie_file = COOKIES_DIR / f"tiktok_session-{ACCOUNT}.cookie"
    if not cookie_file.exists():
        print(f"\n⚠️  No saved login found for @{ACCOUNT}")
        print(f"   Expected: {cookie_file}")
        print(f"   Run: cd {UPLOADER_DIR}")
        print(f"        python3 cli.py login -n {ACCOUNT}")
        sys.exit(1)
    print(f"✓ Login found for @{ACCOUNT}")


def main():
    parser = argparse.ArgumentParser(description="Empire TikTok Post Pipeline")
    parser.add_argument("--video", help="Path to local video file")
    parser.add_argument("--youtube", help="YouTube URL to repost")
    parser.add_argument("--title", help="Video title/caption")
    parser.add_argument("--schedule", help="Schedule datetime: 'YYYY-MM-DD HH:MM' (15min..10days)")
    parser.add_argument("--visibility", default="public", choices=["public", "private"])
    parser.add_argument("--watch-folder", help="Watch folder for new .mp4 files")
    parser.add_argument("--auto", action="store_true", help="Auto-generate titles from filenames")
    parser.add_argument("--user", default=ACCOUNT, help=f"TikTok account (default: {ACCOUNT})")
    parser.add_argument("--log", action="store_true", help="Show post history")
    args = parser.parse_args()

    if args.log:
        if LOG_FILE.exists():
            log = json.loads(LOG_FILE.read_text())
            print(f"\n📋 Post History ({len(log)} posts):")
            for entry in log[-10:]:
                icon = "✅" if entry["status"] == "success" else "❌"
                print(f"  {icon} {entry['timestamp'][:16]} | {entry['title'][:40]}")
        else:
            print("No posts yet.")
        return

    check_login()

    if args.watch_folder:
        watch_folder(args.watch_folder, auto=args.auto)
    elif args.video:
        if not args.title:
            args.title = Path(args.video).stem.replace("_", " ").title()
        upload_video(Path(args.video), args.title, args.schedule, args.user, args.visibility)
    elif args.youtube:
        if not args.title:
            print("❌ --title required for YouTube uploads")
            sys.exit(1)
        upload_youtube(args.youtube, args.title, args.user, args.visibility)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
