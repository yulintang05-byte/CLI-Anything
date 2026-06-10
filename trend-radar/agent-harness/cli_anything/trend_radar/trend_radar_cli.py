"""CLI-Anything Trend Radar — viral trend intelligence for social media.

Commands:
  youtube trending   - Trending YouTube videos by region/category
  youtube hashtags   - Trending YouTube hashtags for a niche
  youtube music      - Trending music on YouTube
  tiktok trending    - Trending TikTok videos
  tiktok hashtags    - Trending TikTok hashtags (Creative Center)
  tiktok sounds      - Trending TikTok sounds/music
  optimize hashtags  - Generate optimized hashtag set for your niche
  optimize schedule  - Best posting schedule by platform
  optimize account   - Full account audit and recommendations
  calendar generate  - Auto-generate a content calendar from trends
  calendar export    - Export calendar to CSV or JSON
  theme guide        - Comprehensive theme page playbook
  theme niches       - Find profitable theme page niches
  theme convert      - Account conversion guide
  theme setup        - New theme page setup checklist
  repl               - Interactive REPL mode
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
from cli_anything.trend_radar.core.tiktok_trends import TikTokTrends
from cli_anything.trend_radar.core.hashtag_optimizer import HashtagOptimizer
from cli_anything.trend_radar.core.content_calendar import ContentCalendar
from cli_anything.trend_radar.core.account_optimizer import AccountOptimizer
from cli_anything.trend_radar.core.theme_page_guide import ThemePageGuide
from cli_anything.trend_radar.utils.repl_skin import ReplSkin

VERSION = "0.1.0"

_yt   = YouTubeTrends()
_tt   = TikTokTrends()
_ho   = HashtagOptimizer()
_cc   = ContentCalendar()
_ao   = AccountOptimizer()
_tg   = ThemePageGuide()
_skin = ReplSkin("trend_radar", VERSION)


# ════════════════════════════════════════════════════════════════════
# Root group
# ════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(VERSION, prog_name="cli-anything-trend-radar")
def main():
    """CLI-Anything Trend Radar — viral trend intelligence for social media."""
    pass


# ════════════════════════════════════════════════════════════════════
# YOUTUBE
# ════════════════════════════════════════════════════════════════════

@main.group()
def youtube():
    """YouTube trend intelligence (requires YOUTUBE_API_KEY)."""
    pass


@youtube.command("trending")
@click.option("--region",   default="US",  show_default=True, help="ISO region code (US, GB, IN…)")
@click.option("--category", default="all", show_default=True,
              help="all, music, gaming, sports, film, news, education, howto")
@click.option("--limit",    default=20,    show_default=True, help="Results to return (max 50)")
@click.option("--api-key",  envvar="YOUTUBE_API_KEY", help="YouTube Data API v3 key")
@click.option("--json",     "as_json",     is_flag=True,      help="Output as JSON")
def yt_trending(region, category, limit, api_key, as_json):
    """Get currently trending YouTube videos."""
    try:
        results = _yt.get_trending(region=region, category=category, limit=limit, api_key=api_key)
    except Exception as e:
        _skin.error(str(e))
        sys.exit(1)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending YouTube Videos · {region.upper()} · {category}")
    _skin.table(
        ["#", "Title", "Channel", "Views", "Likes"],
        [
            [str(i), v["title"][:45], v["channel"][:25],
             _fmt(v.get("views")), _fmt(v.get("likes"))]
            for i, v in enumerate(results, 1)
        ],
    )
    _skin.hint(f"\n  {len(results)} videos  ·  data updated within last 24h")


@youtube.command("hashtags")
@click.option("--niche",    required=True, help="Niche/topic (e.g. fitness, cooking, travel)")
@click.option("--region",   default="US",  show_default=True)
@click.option("--limit",    default=25,    show_default=True)
@click.option("--api-key",  envvar="YOUTUBE_API_KEY")
@click.option("--json",     "as_json",     is_flag=True)
def yt_hashtags(niche, region, limit, api_key, as_json):
    """Find trending YouTube hashtags by analyzing top video tags for a niche."""
    try:
        results = _yt.get_trending_hashtags(niche=niche, region=region, limit=limit, api_key=api_key)
    except Exception as e:
        _skin.error(str(e))
        sys.exit(1)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending YouTube Hashtags · #{niche} · {region.upper()}")
    _skin.table(
        ["Hashtag", "Video Count", "Avg Views", "Score"],
        [
            [f"#{r['tag']}", _fmt(r.get("video_count")),
             _fmt(r.get("avg_views")), str(r.get("score", 0))]
            for r in results
        ],
    )


@youtube.command("music")
@click.option("--region",  default="US", show_default=True)
@click.option("--limit",   default=20,   show_default=True)
@click.option("--api-key", envvar="YOUTUBE_API_KEY")
@click.option("--json",    "as_json",    is_flag=True)
def yt_music(region, limit, api_key, as_json):
    """Get trending music videos on YouTube (Music category)."""
    try:
        results = _yt.get_trending_music(region=region, limit=limit, api_key=api_key)
    except Exception as e:
        _skin.error(str(e))
        sys.exit(1)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending Music on YouTube · {region.upper()}")
    _skin.table(
        ["#", "Title", "Artist / Channel", "Views", "Published"],
        [
            [str(i), r["title"][:40], r["channel"][:25],
             _fmt(r.get("views")), r.get("published_at", "")[:10]]
            for i, r in enumerate(results, 1)
        ],
    )


# ════════════════════════════════════════════════════════════════════
# TIKTOK
# ════════════════════════════════════════════════════════════════════

@main.group()
def tiktok():
    """TikTok trend intelligence (uses Creative Center public data)."""
    pass


@tiktok.command("trending")
@click.option("--region", default="US",  show_default=True)
@click.option("--period", default="7",   type=click.Choice(["7", "30"]), show_default=True,
              help="Trending window: 7 days or 30 days")
@click.option("--limit",  default=20,    show_default=True)
@click.option("--json",   "as_json",     is_flag=True)
def tt_trending(region, period, limit, as_json):
    """Get trending TikTok videos."""
    results = _tt.get_trending_videos(region=region, period=int(period), limit=limit)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending TikTok Videos · {region.upper()} · {period}d")
    _skin.table(
        ["#", "Caption", "Plays", "Likes", "Comments", "Shares"],
        [
            [str(i), r["title"][:40],
             _fmt(r.get("play_count")), _fmt(r.get("like_count")),
             _fmt(r.get("comment_count")), _fmt(r.get("share_count"))]
            for i, r in enumerate(results, 1)
        ],
    )


@tiktok.command("hashtags")
@click.option("--region", default="US",       show_default=True)
@click.option("--period", default="7",        type=click.Choice(["7", "30"]), show_default=True)
@click.option("--limit",  default=30,         show_default=True)
@click.option("--sort",   default="popular",  type=click.Choice(["popular", "rise"]),
              show_default=True, help="popular = most-used  |  rise = fastest-growing")
@click.option("--json",   "as_json",          is_flag=True)
def tt_hashtags(region, period, limit, sort, as_json):
    """Get trending TikTok hashtags from Creative Center."""
    results = _tt.get_trending_hashtags(region=region, period=int(period), limit=limit, sort_by=sort)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending TikTok Hashtags · {region.upper()} · {period}d · {sort}")
    _skin.table(
        ["Rank", "Hashtag", "Posts", "Views", "Trend"],
        [
            [str(r.get("rank", i + 1)),
             f"#{r.get('hashtag_name', '')}",
             _fmt(r.get("publish_cnt")),
             _fmt(r.get("video_views")),
             r.get("trend", "→")]
            for i, r in enumerate(results)
        ],
    )


@tiktok.command("sounds")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default="7",  type=click.Choice(["7", "30"]), show_default=True)
@click.option("--limit",  default=20,   show_default=True)
@click.option("--json",   "as_json",    is_flag=True)
def tt_sounds(region, period, limit, as_json):
    """Get trending TikTok sounds and music tracks."""
    results = _tt.get_trending_sounds(region=region, period=int(period), limit=limit)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Trending TikTok Sounds · {region.upper()} · {period}d")
    _skin.table(
        ["#", "Title", "Artist", "Videos Using", "Trend"],
        [
            [str(i), r["title"][:35], r.get("author", "")[:20],
             _fmt(r.get("video_count")), r.get("trend", "→")]
            for i, r in enumerate(results, 1)
        ],
    )


# ════════════════════════════════════════════════════════════════════
# OPTIMIZE
# ════════════════════════════════════════════════════════════════════

@main.group()
def optimize():
    """Account and content optimization tools."""
    pass


@optimize.command("hashtags")
@click.option("--niche",    required=True, help="Your content niche (fitness, travel, food, etc.)")
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube", "twitter"]))
@click.option("--count",    default=30,   show_default=True, help="Total hashtags to generate")
@click.option("--json",     "as_json",    is_flag=True)
def opt_hashtags(niche, platform, count, as_json):
    """Generate an optimized hashtag set for your niche and platform."""
    result = _ho.generate_set(niche=niche, platform=platform, count=count)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    _skin.section(f"Optimized Hashtag Set · #{niche} · {platform}")
    _skin.info(f"Strategy: {result['strategy']}")
    print()
    for tier, tags in result["tiers"].items():
        if tags:
            _skin.status(tier, f"{len(tags)} tags")
            for tag in tags:
                print(f"    #{tag}")
            print()
    _skin.hint(f"Copy-ready ({result['total']} tags):")
    print(f"\n  {result['copy_ready']}\n")


@optimize.command("schedule")
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube", "twitter", "all"]))
@click.option("--niche",    default="general",   show_default=True)
@click.option("--timezone", default="US/Eastern", show_default=True)
@click.option("--json",     "as_json",    is_flag=True)
def opt_schedule(platform, niche, timezone, as_json):
    """Get the optimal posting schedule for a platform."""
    result = _ao.get_best_times(platform=platform, niche=niche, timezone=timezone)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    platforms = result if platform == "all" else {platform: result}
    for plat, data in platforms.items():
        _skin.section(f"Best Posting Times · {plat.title()}")
        _skin.table(
            ["Day", "Peak Time 1", "Peak Time 2", "Engagement Score"],
            [[d["day"], d.get("peak1", "–"), d.get("peak2", "–"), d.get("score", "–")]
             for d in data.get("schedule", [])],
        )
        _skin.info(f"Frequency: {data.get('frequency', 'daily')}")
        _skin.hint(f"  {data.get('note', '')}")
        print()


@optimize.command("account")
@click.option("--platform", required=True,
              type=click.Choice(["instagram", "tiktok", "youtube", "twitter"]))
@click.option("--niche",    required=True, help="Your content niche")
@click.option("--username", default="",    help="Handle (for display only)")
@click.option("--json",     "as_json",     is_flag=True)
def opt_account(platform, niche, username, as_json):
    """Get a full account audit with actionable recommendations."""
    result = _ao.audit(platform=platform, niche=niche, username=username)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    handle = f"@{username}" if username else platform.title()
    _skin.section(f"Account Audit · {handle} · #{niche}")
    for category, tips in result.items():
        _skin.status(category.replace("_", " ").title(), "")
        for tip in tips:
            print(f"    → {tip}")
        print()


# ════════════════════════════════════════════════════════════════════
# CALENDAR
# ════════════════════════════════════════════════════════════════════

@main.group()
def calendar():
    """Content calendar generation and export."""
    pass


@calendar.command("generate")
@click.option("--niche",           required=True)
@click.option("--platform",        default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube", "all"]))
@click.option("--weeks",           default=4,  show_default=True, help="Calendar length in weeks")
@click.option("--posts-per-week",  default=5,  show_default=True)
@click.option("--output", "-o",    default="", help="Save to file (.json or .csv)")
@click.option("--json",            "as_json",  is_flag=True)
def cal_generate(niche, platform, weeks, posts_per_week, output, as_json):
    """Generate a content calendar from trends."""
    cal = _cc.generate(niche=niche, platform=platform, weeks=weeks, posts_per_week=posts_per_week)

    if output:
        ext = Path(output).suffix.lower()
        if ext == ".csv":
            _cc.export_csv(cal, output)
        else:
            _cc.export_json(cal, output)
        _skin.success(f"Calendar saved to {output} ({cal['total_posts']} posts)")
        return

    if as_json:
        print(json.dumps(cal, indent=2))
        return

    _skin.section(f"Content Calendar · #{niche} · {platform} · {weeks} weeks")
    for week in cal["weeks"]:
        print(f"\n  Week {week['week_number']}  ({week['date_range']})")
        _skin.table(
            ["Day", "Format", "Topic", "Hashtags", "Best Time"],
            [
                [p["day"], p.get("format", "post"), p.get("topic", "")[:35],
                 " ".join(f"#{h}" for h in p.get("hashtags", [])[:3]),
                 p.get("best_time", "")]
                for p in week["posts"]
            ],
        )
    _skin.hint(f"\n  Total: {cal['total_posts']} posts over {weeks} weeks")


@calendar.command("export")
@click.argument("output_file")
@click.option("--niche",          required=True)
@click.option("--platform",       default="instagram", show_default=True)
@click.option("--weeks",          default=4,  show_default=True)
@click.option("--posts-per-week", default=5,  show_default=True)
def cal_export(output_file, niche, platform, weeks, posts_per_week):
    """Export content calendar to a CSV or JSON file."""
    cal = _cc.generate(niche=niche, platform=platform, weeks=weeks, posts_per_week=posts_per_week)
    ext = Path(output_file).suffix.lower()
    if ext == ".csv":
        _cc.export_csv(cal, output_file)
    else:
        _cc.export_json(cal, output_file)
    _skin.success(f"Saved to {output_file}")
    _skin.info(f"{cal['total_posts']} posts scheduled")


# ════════════════════════════════════════════════════════════════════
# THEME PAGE
# ════════════════════════════════════════════════════════════════════

@main.group()
def theme():
    """Theme page creation, conversion, and optimization tools."""
    pass


@theme.command("guide")
@click.option("--topic", default="overview", show_default=True,
              type=click.Choice(["overview", "setup", "content", "growth", "monetize", "all"]))
@click.option("--json",  "as_json", is_flag=True)
def theme_guide(topic, as_json):
    """Get the full theme page playbook."""
    result = _tg.get_guide(topic=topic)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    for section_name, content in result.items():
        _skin.section(section_name)
        if isinstance(content, list):
            for item in content:
                print(f"  • {item}")
        else:
            print(f"  {content}")
        print()


@theme.command("niches")
@click.option("--category", default="all", show_default=True,
              type=click.Choice([
                  "all", "lifestyle", "finance", "entertainment", "sports",
                  "fitness", "fashion", "food", "travel", "tech",
              ]))
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--json",     "as_json", is_flag=True)
def theme_niches(category, platform, as_json):
    """Find profitable theme page niches sorted by growth potential."""
    results = _tg.find_niches(category=category, platform=platform)

    if as_json:
        print(json.dumps(results, indent=2))
        return

    _skin.section(f"Profitable Theme Page Niches · {platform} · {category}")
    _skin.table(
        ["Niche", "Competition", "Growth", "Monetization", "Examples"],
        [
            [r["niche"], r.get("competition", ""), r.get("growth_potential", ""),
             r.get("monetization", "")[:35], r.get("examples", "")[:25]]
            for r in results
        ],
    )
    _skin.hint("\n  Low competition + very high growth = best opportunity")


@theme.command("convert")
@click.option("--from-type", default="personal", show_default=True,
              type=click.Choice(["personal", "meme", "news", "fan", "product"]))
@click.option("--to-type",   default="theme",    show_default=True,
              type=click.Choice(["theme", "brand", "authority", "community"]))
@click.option("--platform",  default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--json",      "as_json", is_flag=True)
def theme_convert(from_type, to_type, platform, as_json):
    """Get a phased account conversion guide."""
    result = _tg.get_conversion_tips(from_type=from_type, to_type=to_type, platform=platform)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    _skin.section(f"Converting {from_type} → {to_type} on {platform}")
    for phase, steps in result.items():
        _skin.status(phase.replace("_", " ").title(), "")
        for step in steps:
            print(f"    {step}")
        print()


@theme.command("setup")
@click.option("--niche",    required=True)
@click.option("--platform", default="instagram", show_default=True,
              type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--json",     "as_json", is_flag=True)
def theme_setup(niche, platform, as_json):
    """Get a complete setup checklist for a new theme page."""
    result = _tg.get_setup_checklist(niche=niche, platform=platform)

    if as_json:
        print(json.dumps(result, indent=2))
        return

    _skin.section(f"Theme Page Setup Checklist · #{niche} · {platform}")
    for phase, items in result.items():
        _skin.status(phase.replace("_", " ").title(), f"{len(items)} items")
        for item in items:
            print(f"    ☐  {item}")
        print()


# ════════════════════════════════════════════════════════════════════
# REPL
# ════════════════════════════════════════════════════════════════════

@main.command()
def repl():
    """Start interactive REPL mode."""
    _skin.print_banner()
    pt_session = _skin.create_prompt_session()

    while True:
        try:
            raw = _skin.get_input(pt_session, context="trend-radar")
            if not raw:
                continue
            if raw.lower() in ("exit", "quit", "q"):
                break
            args = raw.split()
            try:
                main.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except Exception as e:
                _skin.error(str(e))
        except (KeyboardInterrupt, EOFError):
            break

    _skin.print_goodbye()


# ── Helpers ───────────────────────────────────────────────────────────

def _fmt(n) -> str:
    """Format a number with K/M suffix."""
    try:
        n = int(n)
    except (ValueError, TypeError):
        return str(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


if __name__ == "__main__":
    main()
