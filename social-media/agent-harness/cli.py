#!/usr/bin/env python3
"""
social-media CLI — agent-native social media trend intelligence and account optimizer.

Commands:
  trends      Scrape YouTube + TikTok for viral trends, hashtags, music
  optimize    Score and optimize a post or account profile
  bio         Optimize a profile bio
  account     Full account health report with growth playbook
  niche       Analyze a theme page niche (monetization, calendar, funnel)
  calendar    Generate a content posting calendar
  funnel      Show the full conversion funnel for a niche
  niches      List all available niches
"""
import os
import sys
import json
import argparse
from social_media.scrapers import build_trend_report
from social_media.optimizer import optimize_bio, optimize_post, account_health_report
from social_media.theme_pages import (
    list_niches, niche_analysis, content_calendar, conversion_funnel_guide,
)


def _out(data, human: bool = False):
    """Output JSON (default) or human-readable."""
    if human:
        _pretty(data)
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def _pretty(data, indent=0):
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                print(f"{pad}\033[1m{k}\033[0m:")
                _pretty(v, indent + 1)
            else:
                print(f"{pad}\033[1m{k}\033[0m: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                print(f"{pad}[{i}]")
                _pretty(item, indent + 1)
            else:
                print(f"{pad}- {item}")
    else:
        print(f"{pad}{data}")


def cmd_trends(args):
    yt_key = args.yt_api_key or os.getenv("YOUTUBE_API_KEY")
    tt_key = args.rapidapi_key or os.getenv("RAPIDAPI_KEY")

    if not yt_key and not tt_key:
        _out({
            "error": "No API keys provided.",
            "setup": {
                "youtube": "Set YOUTUBE_API_KEY env var or pass --yt-api-key. "
                           "Get a free key at https://console.cloud.google.com (YouTube Data API v3).",
                "tiktok": "Set RAPIDAPI_KEY env var or pass --rapidapi-key. "
                          "Subscribe to 'tiktok-api23' at rapidapi.com (free tier).",
            },
            "demo_output": {
                "note": "Running in demo mode with sample data.",
                "youtube": {
                    "top_hashtags": [
                        {"hashtag": "#shorts", "frequency": 38},
                        {"hashtag": "#viral", "frequency": 31},
                        {"hashtag": "#trending", "frequency": 28},
                        {"hashtag": "#fyp", "frequency": 22},
                        {"hashtag": "#music", "frequency": 19},
                    ]
                },
                "tiktok": {
                    "top_hashtags": [
                        {"hashtag": "#fyp", "frequency": 45},
                        {"hashtag": "#viral", "frequency": 39},
                        {"hashtag": "#foryou", "frequency": 35},
                        {"hashtag": "#trending", "frequency": 28},
                        {"hashtag": "#tiktok", "frequency": 22},
                    ],
                    "trending_music": [
                        {"title": "Espresso", "author": "Sabrina Carpenter", "use_count": 18},
                        {"title": "Die With A Smile", "author": "Lady Gaga, Bruno Mars", "use_count": 14},
                        {"title": "Harlequin", "author": "Lady Gaga", "use_count": 11},
                    ],
                },
                "cross_platform_hashtags": ["#trending", "#viral"],
            },
        })
        return

    report = build_trend_report(yt_key, tt_key, region=args.region)
    _out(report, args.human)


def cmd_optimize(args):
    # Load trending data from file or use empty defaults
    trending_hashtags = []
    trending_music = []
    if args.trends_file:
        with open(args.trends_file) as f:
            report = json.load(f)
        tt_tags = report.get("tiktok", {}).get("top_hashtags", [])
        yt_tags = report.get("youtube", {}).get("top_hashtags", [])
        trending_hashtags = tt_tags + yt_tags
        trending_music = report.get("trending_music", [])

    hashtags = args.hashtags.split(",") if args.hashtags else []
    result = optimize_post(
        caption=args.caption or "",
        hashtags=hashtags,
        trending_hashtags=trending_hashtags,
        trending_music=trending_music,
        platform=args.platform,
        current_likes=args.likes,
        current_comments=args.comments,
        current_shares=args.shares,
        followers=args.followers,
    )
    _out(result, args.human)


def cmd_bio(args):
    trending_hashtags = []
    if args.trends_file:
        with open(args.trends_file) as f:
            report = json.load(f)
        trending_hashtags = (
            [h["hashtag"] for h in report.get("tiktok", {}).get("top_hashtags", [])]
            + [h["hashtag"] for h in report.get("youtube", {}).get("top_hashtags", [])]
        )
    result = optimize_bio(
        current_bio=args.bio,
        niche=args.niche,
        trending_hashtags=trending_hashtags,
        platform=args.platform,
    )
    _out(result, args.human)


def cmd_account(args):
    trending_hashtags = []
    trending_music = []
    if args.trends_file:
        with open(args.trends_file) as f:
            report = json.load(f)
        trending_hashtags = report.get("tiktok", {}).get("top_hashtags", [])
        trending_music = report.get("trending_music", [])

    result = account_health_report(
        platform=args.platform,
        username=args.username,
        followers=args.followers,
        following=args.following,
        total_posts=args.posts,
        avg_views=args.avg_views,
        avg_likes=args.avg_likes,
        avg_comments=args.avg_comments,
        avg_shares=args.avg_shares,
        niche=args.niche,
        trending_hashtags=trending_hashtags,
    )
    _out(result, args.human)


def cmd_niche(args):
    result = niche_analysis(args.niche)
    _out(result, args.human)


def cmd_calendar(args):
    result = content_calendar(args.niche, days=args.days)
    _out(result, args.human)


def cmd_funnel(args):
    result = conversion_funnel_guide(args.niche)
    _out(result, args.human)


def cmd_niches(_args):
    result = list_niches()
    _out(result)


# ── Argument parser ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="social-media",
        description="Agent-native social media trend intelligence + account optimizer",
    )
    p.add_argument("--human", action="store_true", help="Human-readable output instead of JSON")
    sub = p.add_subparsers(dest="command", required=True)

    # trends
    t = sub.add_parser("trends", help="Scrape YouTube + TikTok viral trends")
    t.add_argument("--yt-api-key", dest="yt_api_key", help="YouTube Data API v3 key")
    t.add_argument("--rapidapi-key", dest="rapidapi_key", help="RapidAPI key for TikTok")
    t.add_argument("--region", default="US", help="Region code (default: US)")

    # optimize (post)
    o = sub.add_parser("optimize", help="Optimize a post caption + hashtags")
    o.add_argument("--caption", default="", help="Post caption text")
    o.add_argument("--hashtags", default="", help="Comma-separated hashtags (no #)")
    o.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube", "instagram"])
    o.add_argument("--likes", type=int, default=0)
    o.add_argument("--comments", type=int, default=0)
    o.add_argument("--shares", type=int, default=0)
    o.add_argument("--followers", type=int, default=1000)
    o.add_argument("--trends-file", dest="trends_file", help="Path to saved trends JSON")

    # bio
    b = sub.add_parser("bio", help="Optimize a profile bio")
    b.add_argument("--bio", required=True, help="Current bio text")
    b.add_argument("--niche", required=True, help="Your niche (e.g. fitness, finance)")
    b.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube", "instagram"])
    b.add_argument("--trends-file", dest="trends_file", help="Path to saved trends JSON")

    # account
    a = sub.add_parser("account", help="Full account health report")
    a.add_argument("--platform", default="tiktok", choices=["tiktok", "youtube", "instagram"])
    a.add_argument("--username", required=True)
    a.add_argument("--followers", type=int, required=True)
    a.add_argument("--following", type=int, default=0)
    a.add_argument("--posts", type=int, default=0)
    a.add_argument("--avg-views", type=float, default=0, dest="avg_views")
    a.add_argument("--avg-likes", type=float, default=0, dest="avg_likes")
    a.add_argument("--avg-comments", type=float, default=0, dest="avg_comments")
    a.add_argument("--avg-shares", type=float, default=0, dest="avg_shares")
    a.add_argument("--niche", required=True)
    a.add_argument("--trends-file", dest="trends_file", help="Path to saved trends JSON")

    # niche
    n = sub.add_parser("niche", help="Analyze a theme page niche")
    n.add_argument("niche", help="Niche name (e.g. fitness, finance, motivation)")

    # calendar
    cal = sub.add_parser("calendar", help="Generate posting calendar")
    cal.add_argument("niche", help="Niche name")
    cal.add_argument("--days", type=int, default=7, help="Number of days (default: 7)")

    # funnel
    fn = sub.add_parser("funnel", help="Show conversion funnel for a niche")
    fn.add_argument("niche", help="Niche name")

    # niches
    sub.add_parser("niches", help="List all available niches")

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "trends": cmd_trends,
        "optimize": cmd_optimize,
        "bio": cmd_bio,
        "account": cmd_account,
        "niche": cmd_niche,
        "calendar": cmd_calendar,
        "funnel": cmd_funnel,
        "niches": cmd_niches,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
