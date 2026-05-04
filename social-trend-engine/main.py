#!/usr/bin/env python3
"""
Social Trend Engine — CLI entry point.

Commands:
  scrape      Scrape YouTube/TikTok for viral trends, hashtags, music
  hashtags    Analyze and optimize hashtag sets for a niche
  optimize    Audit and generate optimization plan for an account
  calendar    Generate a weekly content calendar
  theme       Print the full theme page guide and monetization roadmap
  music       Show trending music extracted from scraped data
"""

import argparse
import json
import sys
from pathlib import Path

from trend_scraper import (
    scrape_youtube_trending,
    scrape_tiktok_trending,
    get_trending_hashtags,
    get_trending_music,
    save_results,
)
from hashtag_analyzer import (
    build_optimal_hashtag_set,
    get_niche_hashtag_strategy,
    analyze_scraped_hashtags,
)
from account_optimizer import (
    audit_account,
    generate_content_calendar,
    viral_engagement_tactics,
)
from theme_page_guide import (
    print_full_guide,
    print_roadmap,
    get_niche_analysis,
)


def _sep(title: str = "") -> None:
    width = 64
    if title:
        pad = (width - len(title) - 2) // 2
        print("=" * pad + f" {title} " + "=" * pad)
    else:
        print("=" * width)


def cmd_scrape(args: argparse.Namespace) -> None:
    platform = args.platform.lower()
    results = []

    if platform in ("youtube", "all"):
        category = getattr(args, "category", "general") or "general"
        print(f"Scraping YouTube trending [{category}] — {args.max} videos...")
        yt_data = scrape_youtube_trending(category=category, max_results=args.max)
        results.extend(yt_data)
        _sep("YOUTUBE TRENDING")
        for i, v in enumerate(yt_data[:10], 1):
            print(f"  {i:02d}. {v['title'][:60]}")
            print(f"       Views: {v['views']:,}  |  Channel: {v['channel']}")
            if v.get("hashtags"):
                print(f"       Tags: {' '.join('#'+t for t in v['hashtags'][:6])}")
            if v.get("music"):
                print(f"       Music: {v['music']}")

    if platform in ("tiktok", "all"):
        hashtag = getattr(args, "hashtag", "") or ""
        username = getattr(args, "username", "") or ""
        label = f"#{hashtag}" if hashtag else f"@{username}" if username else "trending"
        print(f"\nScraping TikTok [{label}] — {args.max} videos...")
        tt_data = scrape_tiktok_trending(
            username=username, hashtag=hashtag, max_results=args.max
        )
        results.extend(tt_data)
        _sep("TIKTOK TRENDING")
        for i, v in enumerate(tt_data[:10], 1):
            print(f"  {i:02d}. {v['title'][:60]}")
            print(f"       Views: {v['views']:,}  |  Creator: {v['channel']}")
            if v.get("hashtags"):
                print(f"       Tags: {' '.join('#'+t for t in v['hashtags'][:6])}")
            if v.get("music"):
                print(f"       Music: {v['music']}")

    if not results:
        print("No results scraped. Check network connection or try again.")
        return

    # Show aggregated trends
    _sep("TOP TRENDING HASHTAGS")
    top_tags = get_trending_hashtags(results, top_n=25)
    for rank, (tag, count) in enumerate(top_tags, 1):
        bar = "█" * min(count * 3, 30)
        print(f"  #{tag:<25} {bar} ({count})")

    _sep("TOP TRENDING MUSIC")
    top_music = get_trending_music(results, top_n=10)
    if top_music:
        for rank, (track, count) in enumerate(top_music, 1):
            print(f"  {rank:02d}. {track} ({count} videos)")
    else:
        print("  No music metadata found in this scrape batch.")

    # Save to JSON
    if args.output:
        save_results(results, args.output)
    else:
        outfile = f"trends_{platform}_{getattr(args,'category','general')}.json"
        save_results(results, outfile)
        print(f"\nFull data saved to: {outfile}")


def cmd_hashtags(args: argparse.Namespace) -> None:
    platform = args.platform.lower()
    niche = args.niche

    _sep(f"HASHTAG STRATEGY — {niche.upper()} / {platform.upper()}")

    # Build optimized set
    hs = build_optimal_hashtag_set(platform=platform, niche=niche)
    print(hs.summary())

    print()
    print(get_niche_hashtag_strategy(niche))

    # If a saved scrape file provided, analyze real scraped tags
    if args.data_file and Path(args.data_file).exists():
        with open(args.data_file) as f:
            data = json.load(f)
        scraped_tags = get_trending_hashtags(data, top_n=50)
        _sep("SCRAPED TAG ANALYSIS")
        scored = analyze_scraped_hashtags(scraped_tags, niche=niche)
        print(f"{'TAG':<25} {'TIER':<10} {'ENGAGEMENT':>12} {'TREND':>8}  RECOMMENDED")
        print("-" * 75)
        for s in scored[:20]:
            rec = "YES" if s.recommended else "---"
            print(f"  #{s.tag:<23} {s.tier:<10} {s.engagement_potential:>12.3f} {s.trend_score:>8.1f}  {rec}")


def cmd_optimize(args: argparse.Namespace) -> None:
    platform = args.platform.lower()
    handle = args.handle
    niche = args.niche
    followers = args.followers
    avg_views = args.avg_views

    _sep(f"ACCOUNT AUDIT — @{handle}")
    audit = audit_account(
        platform=platform,
        handle=handle,
        followers=followers,
        avg_views=avg_views,
        niche=niche,
    )
    print(audit.summary())

    print()
    _sep("ENGAGEMENT TACTICS")
    print(viral_engagement_tactics(platform))

    print()
    _sep("CONTENT CALENDAR")
    print(generate_content_calendar(platform=platform, niche=niche, posts_per_week=5))


def cmd_calendar(args: argparse.Namespace) -> None:
    _sep("CONTENT CALENDAR")
    print(generate_content_calendar(
        platform=args.platform,
        niche=args.niche,
        posts_per_week=args.posts_per_week,
    ))


def cmd_theme(args: argparse.Namespace) -> None:
    if args.niche:
        print(get_niche_analysis(args.niche))
    if args.roadmap:
        print_roadmap()
    else:
        print_full_guide()
        print_roadmap()


def cmd_music(args: argparse.Namespace) -> None:
    if not Path(args.data_file).exists():
        print(f"File not found: {args.data_file}")
        print("Run 'python main.py scrape' first to generate a data file.")
        sys.exit(1)

    with open(args.data_file) as f:
        data = json.load(f)

    top_music = get_trending_music(data, top_n=args.top)
    _sep("TRENDING MUSIC / SOUNDS")
    if top_music:
        for rank, (track, count) in enumerate(top_music, 1):
            print(f"  {rank:02d}. [{count:2d} videos]  {track}")
    else:
        print("  No music metadata in data file.")
    print(f"\nSource: {args.data_file} ({len(data)} videos)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="social-trend-engine",
        description="Scrape viral trends from YouTube & TikTok. Optimize your accounts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── scrape ────────────────────────────────────────────────────────────────
    p_scrape = sub.add_parser("scrape", help="Scrape trending content from YouTube/TikTok")
    p_scrape.add_argument("--platform", "-p", default="all",
                          choices=["youtube", "tiktok", "all"],
                          help="Platform to scrape (default: all)")
    p_scrape.add_argument("--category", "-c", default="general",
                          choices=["general", "music", "gaming", "films"],
                          help="YouTube category (default: general)")
    p_scrape.add_argument("--hashtag", default="",
                          help="TikTok hashtag to scrape (without #)")
    p_scrape.add_argument("--username", "-u", default="",
                          help="TikTok username to scrape (without @)")
    p_scrape.add_argument("--max", "-n", type=int, default=20,
                          help="Max videos to scrape per platform (default: 20)")
    p_scrape.add_argument("--output", "-o", default="",
                          help="Output JSON filepath (default: auto-named)")
    p_scrape.set_defaults(func=cmd_scrape)

    # ── hashtags ──────────────────────────────────────────────────────────────
    p_hash = sub.add_parser("hashtags", help="Analyze and optimize hashtags for a niche")
    p_hash.add_argument("--niche", "-n", required=True,
                        help="Niche (e.g. fitness, food, comedy, finance)")
    p_hash.add_argument("--platform", "-p", default="tiktok",
                        choices=["tiktok", "youtube"],
                        help="Target platform (default: tiktok)")
    p_hash.add_argument("--data-file", "-d", default="",
                        help="Optional: path to scraped JSON file for real tag analysis")
    p_hash.set_defaults(func=cmd_hashtags)

    # ── optimize ──────────────────────────────────────────────────────────────
    p_opt = sub.add_parser("optimize", help="Audit account and generate optimization plan")
    p_opt.add_argument("--platform", "-p", required=True,
                       choices=["tiktok", "youtube"],
                       help="Platform")
    p_opt.add_argument("--handle", "-H", required=True,
                       help="Account handle (without @ or URL)")
    p_opt.add_argument("--niche", "-n", default="lifestyle",
                       help="Your content niche")
    p_opt.add_argument("--followers", "-f", type=int, default=0,
                       help="Current follower count")
    p_opt.add_argument("--avg-views", "-v", type=int, default=0,
                       help="Average views per post")
    p_opt.set_defaults(func=cmd_optimize)

    # ── calendar ──────────────────────────────────────────────────────────────
    p_cal = sub.add_parser("calendar", help="Generate weekly content calendar")
    p_cal.add_argument("--platform", "-p", default="tiktok",
                       choices=["tiktok", "youtube"],
                       help="Target platform")
    p_cal.add_argument("--niche", "-n", required=True,
                       help="Content niche")
    p_cal.add_argument("--posts-per-week", "-w", type=int, default=5,
                       help="Posts per week (default: 5)")
    p_cal.set_defaults(func=cmd_calendar)

    # ── theme ─────────────────────────────────────────────────────────────────
    p_theme = sub.add_parser("theme", help="Full theme page guide + learning roadmap")
    p_theme.add_argument("--niche", "-n", default="",
                         help="Analyze a specific niche's monetization potential")
    p_theme.add_argument("--roadmap", "-r", action="store_true",
                         help="Show only the 90-day learning roadmap")
    p_theme.set_defaults(func=cmd_theme)

    # ── music ─────────────────────────────────────────────────────────────────
    p_music = sub.add_parser("music", help="Show trending music from a scraped data file")
    p_music.add_argument("--data-file", "-d", required=True,
                         help="Path to scraped JSON file")
    p_music.add_argument("--top", "-t", type=int, default=20,
                         help="Number of top tracks to show (default: 20)")
    p_music.set_defaults(func=cmd_music)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
