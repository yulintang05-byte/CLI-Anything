"""ViralTrends CLI — Agent-native social media trend intelligence tool.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Provides account optimization and theme page creation tools.

Usage:
    viraltrends [--json] [--region US] COMMAND [ARGS]...
    python3 -m cli_anything.viraltrends
"""

import json
import sys
import click
from typing import Any, Optional

from cli_anything.viraltrends.core import scraper as sc
from cli_anything.viraltrends.core import trends as tr
from cli_anything.viraltrends.core import account as ac
from cli_anything.viraltrends.core import themepage as tp

# ── Global flags ──────────────────────────────────────────────────────────────

_json_output: bool = False
_region: str = "US"


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _render(data)


def _render(data: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for item in data:
            if isinstance(item, dict):
                _render_dict(item, indent)
                click.echo()
            else:
                click.echo(f"{pad}{item}")
    elif isinstance(data, dict):
        _render_dict(data, indent)
    else:
        click.echo(f"{pad}{data}")


def _render_dict(d: dict, indent: int = 0) -> None:
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _render_dict(v, indent + 1)
        elif isinstance(v, list):
            if all(isinstance(x, str) for x in v):
                click.echo(f"{pad}{k}: {', '.join(v)}")
            else:
                click.echo(f"{pad}{k}:")
                for item in v:
                    if isinstance(item, dict):
                        _render_dict(item, indent + 1)
                        click.echo()
                    else:
                        click.echo(f"{'  ' * (indent+1)}- {item}")
        else:
            click.echo(f"{pad}{k}: {v}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(f"Error: {msg}", err=True)
    sys.exit(1)


# ── Root group ────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, JP, ...)")
def main(use_json: bool, region: str) -> None:
    """ViralTrends — YouTube + TikTok trend intelligence for agents and creators."""
    global _json_output, _region
    _json_output = use_json
    _region = region.upper()


# ── trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends() -> None:
    """Fetch trending videos from YouTube or TikTok."""


@trends.command("youtube")
@click.option("--limit", default=20, show_default=True, help="Number of videos to fetch")
@click.option("--category", default="now", type=click.Choice(["now", "music", "gaming"]),
              show_default=True, help="Trending category")
@click.option("--score", is_flag=True, help="Include engagement scores")
def trends_youtube(limit: int, category: str, score: bool) -> None:
    """Fetch YouTube trending videos."""
    videos = sc.youtube_trending(region=_region, category=category, limit=limit)
    if not videos:
        _err("No YouTube trending data returned. Ensure yt-dlp is installed: pip install yt-dlp")
    if score:
        videos = [{"engagement_score": tr.score_video(v), **v} for v in videos]
    output(videos, f"YouTube Trending [{category.upper()}] — {_region} ({len(videos)} videos)")


@trends.command("tiktok")
@click.option("--limit", default=20, show_default=True, help="Number of videos to fetch")
@click.option("--score", is_flag=True, help="Include engagement scores")
def trends_tiktok(limit: int, score: bool) -> None:
    """Fetch TikTok trending videos."""
    videos = sc.tiktok_trending(region=_region, limit=limit)
    if not videos:
        _err("No TikTok trending data returned. TikTok may be rate-limiting; try again or use --json.")
    if score:
        videos = [{"engagement_score": tr.score_video(v), **v} for v in videos]
    output(videos, f"TikTok Trending — {_region} ({len(videos)} videos)")


@trends.command("both")
@click.option("--limit", default=15, show_default=True, help="Videos per platform")
def trends_both(limit: int) -> None:
    """Fetch and merge trending videos from YouTube + TikTok."""
    yt = sc.youtube_trending(region=_region, limit=limit)
    tt = sc.tiktok_trending(region=_region, limit=limit)
    merged = tr.merge_trends(yt, tt)
    output(merged, f"Cross-Platform Trending — {_region} ({len(merged)} videos, ranked by engagement)")


@trends.command("velocity")
@click.option("--platform", default="tiktok", type=click.Choice(["youtube", "tiktok"]),
              show_default=True)
@click.option("--limit", default=20, show_default=True)
def trends_velocity(platform: str, limit: int) -> None:
    """Show trending videos ranked by velocity (engagement / rank position)."""
    if platform == "youtube":
        videos = sc.youtube_trending(region=_region, limit=limit)
    else:
        videos = sc.tiktok_trending(region=_region, limit=limit)
    result = tr.trend_velocity(videos)
    output(result, f"Trend Velocity — {platform.upper()} {_region}")


# ── hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Get trending hashtags and cross-platform hashtag analysis."""


@hashtags.command("youtube")
@click.option("--limit", default=30, show_default=True)
def hashtags_youtube(limit: int) -> None:
    """Get trending YouTube hashtags extracted from top videos."""
    tags = sc.youtube_trending_hashtags(region=_region, limit=limit)
    if not tags:
        _err("Could not extract hashtags. Run 'viraltrends trends youtube' first to check connectivity.")
    output(tags, f"YouTube Trending Hashtags — {_region} (top {len(tags)})")


@hashtags.command("tiktok")
@click.option("--limit", default=30, show_default=True)
def hashtags_tiktok(limit: int) -> None:
    """Get trending TikTok hashtags / challenges."""
    tags = sc.tiktok_trending_hashtags(region=_region, limit=limit)
    if not tags:
        _err("Could not fetch TikTok hashtags.")
    output(tags, f"TikTok Trending Hashtags — {_region} (top {len(tags)})")


@hashtags.command("both")
@click.option("--limit", default=20, show_default=True)
def hashtags_both(limit: int) -> None:
    """Merge and rank hashtags from both platforms."""
    yt_tags = sc.youtube_trending_hashtags(region=_region, limit=50)
    tt_tags = sc.tiktok_trending_hashtags(region=_region, limit=50)
    merged = tr.top_hashtags_across_platforms(yt_tags, tt_tags, limit=limit)
    output(merged, f"Cross-Platform Hashtags — {_region} (top {len(merged)})")


@hashtags.command("gaps")
def hashtags_gaps() -> None:
    """Find hashtag opportunities: trending on one platform but not the other."""
    yt_tags = sc.youtube_trending_hashtags(region=_region, limit=50)
    tt_tags = sc.tiktok_trending_hashtags(region=_region, limit=50)
    gaps = tr.content_gap_analysis(yt_tags, tt_tags)
    output(gaps, f"Content Gap Analysis — {_region}")


# ── music ─────────────────────────────────────────────────────────────────────

@main.group()
def music() -> None:
    """Get trending music and sounds."""


@music.command("tiktok")
@click.option("--limit", default=20, show_default=True)
def music_tiktok(limit: int) -> None:
    """Get trending TikTok sounds and music."""
    sounds = sc.tiktok_trending_music(region=_region, limit=limit)
    if not sounds:
        _err("Could not fetch TikTok music trends.")
    output(sounds, f"TikTok Trending Music — {_region} (top {len(sounds)})")


@music.command("youtube")
@click.option("--limit", default=20, show_default=True)
def music_youtube(limit: int) -> None:
    """Get trending YouTube music videos."""
    tracks = sc.youtube_trending_music(region=_region, limit=limit)
    if not tracks:
        _err("Could not fetch YouTube music trends.")
    output(tracks, f"YouTube Trending Music — {_region} (top {len(tracks)})")


# ── niche ─────────────────────────────────────────────────────────────────────

@main.group()
def niche() -> None:
    """Filter trends by niche keywords."""


@niche.command("filter")
@click.argument("keywords", nargs=-1, required=True)
@click.option("--platform", default="tiktok", type=click.Choice(["youtube", "tiktok"]))
@click.option("--limit", default=30, show_default=True)
def niche_filter(keywords: tuple, platform: str, limit: int) -> None:
    """Filter trending videos by niche keywords. Example: viraltrends niche filter fitness gym workout"""
    kw_list = list(keywords)
    if platform == "youtube":
        videos = sc.youtube_trending(region=_region, limit=limit)
    else:
        videos = sc.tiktok_trending(region=_region, limit=limit)
    filtered = tr.niche_affinity(videos, kw_list)
    output(filtered, f"Niche Filter [{', '.join(kw_list)}] — {platform.upper()} {_region} ({len(filtered)} matches)")


# ── account ───────────────────────────────────────────────────────────────────

@main.group()
def account() -> None:
    """Account optimization tools: schedule, hashtags, bio, audit, content calendar."""


@account.command("schedule")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--tz-offset", default=0, show_default=True, help="Your UTC offset (e.g., -5 for EST)")
def account_schedule(platform: str, tz_offset: int) -> None:
    """Get optimal posting schedule for a platform."""
    sched = ac.posting_schedule(platform, tz_offset)
    output(sched, f"Optimal Posting Schedule — {platform.upper()}")


@account.command("hashtags")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche-name", default="", help="Your niche (e.g., 'fitness', 'finance')")
def account_hashtags(platform: str, niche_name: str) -> None:
    """Build a hashtag strategy for your platform and niche."""
    trending = sc.tiktok_trending_hashtags(region=_region, limit=10) if platform == "tiktok" \
        else sc.youtube_trending_hashtags(region=_region, limit=10)
    trending_list = [t["tag"] for t in trending[:5]]
    strategy = ac.hashtag_strategy(platform, niche=niche_name, trending_tags=trending_list)
    output(strategy, f"Hashtag Strategy — {platform.upper()} / {niche_name or 'General'}")


@account.command("bio")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche-name", required=True, help="Your niche (e.g., 'fitness tips')")
@click.option("--value-prop", required=True, help="What value you offer (e.g., 'daily workout routines')")
@click.option("--cta", required=True, help="Call to action (e.g., 'Free program link below')")
def account_bio(platform: str, niche_name: str, value_prop: str, cta: str) -> None:
    """Generate an optimized bio template."""
    bio = ac.bio_template(platform, niche_name, value_prop, cta)
    output(bio, f"Bio Template — {platform.upper()}")


@account.command("audit")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
def account_audit(platform: str) -> None:
    """Get a profile optimization checklist for a platform."""
    checklist = ac.profile_audit_checklist(platform)
    output(checklist, f"Profile Optimization Checklist — {platform.upper()}")


@account.command("calendar")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche-name", required=True, help="Your niche")
@click.option("--posts-per-week", default=5, show_default=True)
def account_calendar(platform: str, niche_name: str, posts_per_week: int) -> None:
    """Generate a 7-day content calendar."""
    trending = sc.tiktok_trending_hashtags(region=_region, limit=5) if platform in ("tiktok", "instagram") \
        else sc.youtube_trending_hashtags(region=_region, limit=5)
    trending_list = [t["tag"] for t in trending[:3]]
    cal = ac.content_calendar(platform, niche_name, posts_per_week, trending_list)
    output(cal, f"7-Day Content Calendar — {platform.upper()} / {niche_name}")


@account.command("optimize")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche-name", default="", help="Your niche")
@click.option("--tz-offset", default=0)
def account_optimize(platform: str, niche_name: str, tz_offset: int) -> None:
    """Run full account optimization: schedule + hashtags + audit + calendar."""
    trending = sc.tiktok_trending_hashtags(region=_region, limit=10) if platform in ("tiktok", "instagram") \
        else sc.youtube_trending_hashtags(region=_region, limit=10)
    trending_list = [t["tag"] for t in trending[:5]]

    result = {
        "platform": platform,
        "niche": niche_name or "general",
        "region": _region,
        "posting_schedule": ac.posting_schedule(platform, tz_offset),
        "hashtag_strategy": ac.hashtag_strategy(platform, niche_name, trending_list),
        "profile_checklist": ac.profile_audit_checklist(platform),
        "content_calendar": ac.content_calendar(platform, niche_name or "content", 5, trending_list),
        "trending_hashtags_right_now": trending_list,
    }
    output(result, f"Full Account Optimization — {platform.upper()} / {niche_name or 'General'}")


# ── themepage ─────────────────────────────────────────────────────────────────

@main.group()
def themepage() -> None:
    """Theme page creation, niche research, and conversion guides."""


@themepage.command("niches")
def themepage_niches() -> None:
    """List all available niches with key metrics."""
    niches = tp.niche_research()
    output(niches, "Available Niches — Ranked by Growth Rate")


@themepage.command("research")
@click.argument("niche_key")
def themepage_research(niche_key: str) -> None:
    """Get detailed niche research for a specific niche. Example: viraltrends themepage research finance"""
    info = tp.niche_research(niche_key)
    if "error" in info:
        _err(f"{info['error']}. Available: {', '.join(info.get('available', []))}")
    output(info, f"Niche Research — {info.get('name', niche_key)}")


@themepage.command("playbook")
@click.argument("niche_key")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram"]))
def themepage_playbook(niche_key: str, platform: str) -> None:
    """Get full step-by-step theme page playbook for a niche."""
    pb = tp.theme_page_playbook(niche_key, platform)
    output(pb, f"Theme Page Playbook — {pb['niche']} / {platform.upper()}")


@themepage.command("converting")
def themepage_converting() -> None:
    """Learn how to convert theme page followers into revenue."""
    guide = tp.converting_guide()
    output(guide, "Theme Page Conversion Guide")


@themepage.command("selling")
def themepage_selling() -> None:
    """Guide on selling theme page accounts for profit."""
    guide = tp.account_selling_guide()
    output(guide, "Theme Page Selling Guide")


# ── REPL skin ─────────────────────────────────────────────────────────────────

def _launch_repl() -> None:
    """Interactive REPL for ViralTrends."""
    try:
        from cli_anything.viraltrends.utils.repl_skin import run_repl
        run_repl(main)
    except ImportError:
        click.echo("REPL mode: type commands without the 'viraltrends' prefix. Ctrl+C to exit.\n")
        while True:
            try:
                raw = input("viraltrends> ").strip()
                if not raw or raw in ("exit", "quit"):
                    break
                args = raw.split()
                try:
                    main.main(args, standalone_mode=False)
                except SystemExit:
                    pass
                except Exception as exc:  # noqa: BLE001
                    click.echo(f"Error: {exc}")
            except (EOFError, KeyboardInterrupt):
                click.echo("\nGoodbye.")
                break
