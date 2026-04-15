#!/usr/bin/env python3
"""
Empire TikTok Post Pipeline
Connects Deep-Live-Cam output → TiktokAutoUploader → TikTok

Usage:
  python3 empire_post.py --video path/to/video.mp4 --title "Your title" [--schedule "2024-01-15 18:00"]
  python3 empire_post.py --youtube "https://youtube.com/shorts/..." --title "Repost title"
  python3 empire_post.py --watch-folder ~/passive-income/output/ --auto
"""

import subprocess
import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

EMPIRE_DIR = Path.home() / "passive-income"
UPLOADER_DIR = EMPIRE_DIR / "TiktokAutoUploader"
OUTPUT_DIR = EMPIRE_DIR / "output"
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


def upload_video(video_path, title, schedule=None, user=ACCOUNT):
    """Upload a single video to TikTok via TiktokAutoUploader."""
    cmd = [
        "python3", "cli.py", "upload",
        "--user", user,
        "-v", str(video_path),
        "-t", title,
        "--visibility", "PUBLIC",
        "--comment", "1",
    ]
    if schedule:
        cmd += ["--schedule", schedule]

    print(f"\n📤 Uploading: {video_path.name}")
    print(f"   Title: {title}")
    if schedule:
        print(f"   Scheduled: {schedule}")

    result = subprocess.run(cmd, cwd=UPLOADER_DIR, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"   ✅ Upload success")
        log_post(video_path, title, "success")
        return True
    else:
        err = result.stderr or result.stdout
        print(f"   ❌ Upload failed: {err[:200]}")
        log_post(video_path, title, "failed", err[:500])
        return False


def upload_youtube(url, title, user=ACCOUNT):
    """Upload from a YouTube Shorts URL."""
    cmd = [
        "python3", "cli.py", "upload",
        "--user", user,
        "-v", url,
        "-t", title,
        "--visibility", "PUBLIC",
    ]
    print(f"\n📤 Uploading from YouTube: {url}")
    result = subprocess.run(cmd, cwd=UPLOADER_DIR, capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ Upload success")
        log_post(url, title, "success")
        return True
    else:
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
            # Auto-generate title from filename
            title = video.stem.replace("_", " ").replace("-", " ").title()
        else:
            title = input(f"\nTitle for {video.name} (Enter to skip): ").strip()
            if not title:
                continue

        success = upload_video(video, title)
        if success:
            uploaded.add(str(video))
            uploaded_tracker.write_text(json.dumps(list(uploaded)))


def check_login():
    """Verify cookies exist for the account."""
    cookie_file = UPLOADER_DIR / "cookies" / f"{ACCOUNT}.json"
    if not cookie_file.exists():
        print(f"\n⚠️  No saved login found for @{ACCOUNT}")
        print(f"   Run: cd {UPLOADER_DIR}")
        print(f"        python3 cli.py login -n {ACCOUNT}")
        sys.exit(1)
    print(f"✓ Login found for @{ACCOUNT}")


def main():
    parser = argparse.ArgumentParser(description="Empire TikTok Post Pipeline")
    parser.add_argument("--video", help="Path to local video file")
    parser.add_argument("--youtube", help="YouTube Shorts URL to repost")
    parser.add_argument("--title", help="Video title/caption")
    parser.add_argument("--schedule", help="Schedule datetime: 'YYYY-MM-DD HH:MM'")
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
        upload_video(Path(args.video), args.title, args.schedule, args.user)
    elif args.youtube:
        if not args.title:
            print("❌ --title required for YouTube uploads")
            sys.exit(1)
        upload_youtube(args.youtube, args.title, args.user)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
