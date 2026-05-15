#!/usr/bin/env python3
"""
social-trends CLI — Viral trend scraping + account optimization for YouTube & TikTok.

Usage:
    social-trends scrape youtube [--region US] [--limit 30] [--type videos|music]
    social-trends scrape tiktok [--region US] [--period 7] [--type hashtags|sounds|videos|creators]
    social-trends hashtags --platform tiktok --niche fitness [--region US]
    social-trends music [--source billboard|spotify|tiktok] [--limit 25]
    social-trends optimize account --platform tiktok --niche fitness --followers 5000
    social-trends optimize schedule --platform tiktok [--tz-offset -5] [--posts-week 7]
    social-trends theme-pages list
    social-trends theme-pages strategy --niche fitness_motivation
    social-trends theme-pages roadmap [--followers 0]
    social-trends theme-pages revenue --platform tiktok --niche fitness_motivation --followers 10000
    social-trends dashboard [--region US] [--niche fitness]
"""

import json
import sys
import os
import click

_json_output = False


def _out(data, message: str = ""):
    """Output JSON or human-readable."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    _print_dict(item)
                    click.echo("")
                else:
                    click.echo(f"  • {item}")
        elif isinstance(data, dict):
            _print_dict(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{click.style(k, bold=True)}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{click.style(k, bold=True)}:")
            for item in v:
                if isinstance(item, dict):
                    _print_dict(item, indent + 1)
                    click.echo("")
                else:
                    click.echo(f"{prefix}  • {item}")
        else:
            click.echo(f"{prefix}{click.style(k, bold=True)}: {v}")


@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def cli(use_json: bool):
    """social-trends: Scrape viral trends and optimize social media accounts."""
    global _json_output
    _json_output = use_json


# ─── SCRAPE ──────────────────────────────────────────────────────────────────

@cli.group()
def scrape():
    """Scrape trending content from YouTube or TikTok."""


@scrape.command("youtube")
@click.option("--region", default="US", show_default=True, help="Country code (US, GB, AU...)")
@click.option("--limit", default=20, show_default=True, help="Max results to return")
@click.option(
    "--type",
    "content_type",
    default="videos",
    type=click.Choice(["videos", "music", "hashtags"]),
    show_default=True,
    help="Type of content to fetch",
)
def scrape_youtube(region: str, limit: int, content_type: str):
    """Fetch YouTube trending videos, music, or derived hashtags."""
    from cli_anything.social_trends.scrapers import youtube

    click.echo(f"Fetching YouTube trending {content_type} for region {region}...")

    if content_type == "videos":
        items = youtube.get_trending_videos(region=region, max_results=limit)
        if not items:
            click.echo("No results — ensure yt-dlp is installed or check network.", err=True)
            sys.exit(1)
        _out(items, f"\n{'='*50}\nYouTube Trending Videos ({region})\n{'='*50}")

    elif content_type == "music":
        items = youtube.get_trending_music(region=region, max_results=limit)
        if not items:
            click.echo("No music results.", err=True)
            sys.exit(1)
        _out(items, f"\n{'='*50}\nYouTube Trending Music ({region})\n{'='*50}")

    elif content_type == "hashtags":
        videos = youtube.get_trending_videos(region=region, max_results=30)
        tags = youtube.extract_hashtags_from_titles(videos)
        if not tags:
            click.echo("No hashtags extracted.", err=True)
        _out(
            tags[:limit],
            f"\n{'='*50}\nYouTube Trending Hashtags (derived from titles, {region})\n{'='*50}",
        )

    click.echo(f"\nTotal results: {limit}")


@scrape.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Country code")
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]), show_default=True)
@click.option("--limit", default=20, show_default=True)
@click.option(
    "--type",
    "content_type",
    default="hashtags",
    type=click.Choice(["hashtags", "sounds", "videos", "creators"]),
    show_default=True,
)
def scrape_tiktok(region: str, period: str, limit: int, content_type: str):
    """Fetch TikTok trending hashtags, sounds, videos, or creators."""
    from cli_anything.social_trends.scrapers import tiktok

    period_int = int(period)
    click.echo(f"Fetching TikTok trending {content_type} ({region}, last {period} days)...")

    if content_type == "hashtags":
        items = tiktok.get_trending_hashtags(region=region, period=period_int, limit=limit)
        _out(
            items,
            f"\n{'='*50}\nTikTok Trending Hashtags ({region})\n{'='*50}",
        )
        if items:
            tags_line = "  ".join(t["hashtag"] for t in items[:10])
            click.echo(f"\nQuick copy: {tags_line}")

    elif content_type == "sounds":
        items = tiktok.get_trending_sounds(region=region, period=period_int, limit=limit)
        _out(
            items,
            f"\n{'='*50}\nTikTok Trending Sounds ({region})\n{'='*50}",
        )

    elif content_type == "videos":
        items = tiktok.get_trending_videos(region=region, period=period_int, limit=limit)
        _out(
            items,
            f"\n{'='*50}\nTikTok Trending Videos ({region})\n{'='*50}",
        )

    elif content_type == "creators":
        items = tiktok.get_trending_creators(region=region, period=period_int, limit=limit)
        _out(
            items,
            f"\n{'='*50}\nTikTok Trending Creators ({region})\n{'='*50}",
        )

    if not _json_output:
        count = len(items) if items else 0
        click.echo(f"\nTotal results: {count}")


# ─── HASHTAGS ─────────────────────────────────────────────────────────────────

@cli.command("hashtags")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", required=True, help='Your niche e.g. "fitness" "cooking" "gaming"')
@click.option("--region", default="US")
@click.option("--max-tags", default=8, show_default=True)
def hashtags(platform: str, niche: str, region: str, max_tags: int):
    """Build an optimized hashtag set for your niche and platform."""
    from cli_anything.social_trends.scrapers import tiktok, youtube
    from cli_anything.social_trends.optimizer import build_hashtag_set

    click.echo(f"Building hashtag set for '{niche}' on {platform}...")

    # Get trending tags based on platform
    if platform in ("tiktok", "instagram"):
        trending = tiktok.get_trending_hashtags(region=region, limit=50)
    else:
        videos = youtube.get_trending_videos(region=region, max_results=30)
        trending = youtube.extract_hashtags_from_titles(videos)

    result = build_hashtag_set(trending, niche, platform, max_tags)
    _out(result, f"\n{'='*50}\nOptimized Hashtag Set\n{'='*50}")

    if not _json_output:
        click.echo(f"\nCopy-paste: {' '.join(result['hashtags'])}")


# ─── MUSIC ────────────────────────────────────────────────────────────────────

@cli.command("music")
@click.option(
    "--source",
    default="billboard",
    type=click.Choice(["billboard", "spotify", "tiktok"]),
    show_default=True,
)
@click.option("--limit", default=20, show_default=True)
@click.option("--region", default="US", help="Country (for Spotify/TikTok)")
@click.option("--content-type", default="general",
              type=click.Choice(["general", "motivation", "lifestyle", "gaming", "beauty", "fitness"]))
def music(source: str, limit: int, region: str, content_type: str):
    """Get trending music ranked for content suitability."""
    from cli_anything.social_trends.scrapers import music as music_mod

    click.echo(f"Fetching trending music from {source}...")

    if source == "billboard":
        tracks = music_mod.get_billboard_hot100(limit=limit)
    elif source == "spotify":
        country = "global" if region == "US" else region.lower()
        tracks = music_mod.get_spotify_viral_50(country=country)
    else:
        tracks = music_mod.get_tiktok_trending_sounds_from_cc(region=region)

    if not tracks:
        click.echo(f"No results from {source}. Try --source tiktok as fallback.", err=True)
        sys.exit(1)

    scored = music_mod.score_music_for_content(tracks, content_type)
    _out(
        scored[:limit],
        f"\n{'='*50}\nTrending Music — {source.title()} (scored for '{content_type}' content)\n{'='*50}",
    )


# ─── OPTIMIZE ────────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization tools."""


@optimize.command("account")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@click.option("--niche", required=True, help='Your content niche')
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--posts-week", default=0, type=int, help="Current posts per week")
def optimize_account(platform: str, niche: str, followers: int, avg_views: int, posts_week: int):
    """Analyze your account and get optimization recommendations."""
    from cli_anything.social_trends.scrapers import tiktok, youtube
    from cli_anything.social_trends.optimizer import analyze_account

    click.echo(f"Analyzing {platform} account in '{niche}' niche...")

    # Fetch live trending hashtags for recommendations
    if platform in ("tiktok", "instagram"):
        trending = tiktok.get_trending_hashtags(limit=30)
    else:
        videos = youtube.get_trending_videos(max_results=20)
        trending = youtube.extract_hashtags_from_titles(videos)

    result = analyze_account(
        platform=platform,
        niche=niche,
        current_followers=followers,
        avg_views=avg_views,
        posts_per_week=posts_week,
        trending_hashtags=trending,
    )

    _out(result, f"\n{'='*50}\nAccount Analysis Report\n{'='*50}")

    if not _json_output:
        score = result.get("health_score", 0)
        color = "green" if score >= 70 else "yellow" if score >= 40 else "red"
        click.echo(f"\nHealth Score: {click.style(str(score) + '/100', fg=color, bold=True)}")


@optimize.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]))
@click.option("--tz-offset", default=-5, type=int, show_default=True, help="Timezone offset from UTC (e.g. -5 for EST)")
@click.option("--posts-week", default=7, type=int, show_default=True)
def optimize_schedule(platform: str, tz_offset: int, posts_week: int):
    """Generate an optimal weekly posting schedule."""
    from cli_anything.social_trends.optimizer import get_posting_schedule

    result = get_posting_schedule(platform, timezone_offset=tz_offset, posts_per_week=posts_week)
    _out(result, f"\n{'='*50}\nOptimal Posting Schedule — {platform.title()}\n{'='*50}")


@optimize.command("angles")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--region", default="US")
def optimize_angles(niche: str, platform: str, region: str):
    """Generate viral content angles based on trending topics in your niche."""
    from cli_anything.social_trends.scrapers import youtube
    from cli_anything.social_trends.optimizer import generate_content_angles

    click.echo(f"Generating content angles for '{niche}' based on current YouTube trends...")

    videos = youtube.get_trending_videos(region=region, max_results=20)
    titles = [v["title"] for v in videos]
    angles = generate_content_angles(titles, niche, platform)

    _out(angles, f"\n{'='*50}\nViral Content Angles for '{niche}'\n{'='*50}")


# ─── THEME PAGES ──────────────────────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages():
    """Theme page strategy — build, convert, and monetize niche content pages."""


@theme_pages.command("list")
def tp_list():
    """List all available theme page niches with monetization potential."""
    from cli_anything.social_trends.theme_pages import get_all_niches

    niches = get_all_niches()
    _out(niches, f"\n{'='*60}\nAvailable Theme Page Niches\n{'='*60}")

    if not _json_output:
        click.echo(
            "\nTo see full strategy: social-trends theme-pages strategy --niche <key>"
        )


@theme_pages.command("strategy")
@click.option("--niche", required=True, help="Niche key from 'theme-pages list'")
def tp_strategy(niche: str):
    """Get full strategy for a specific theme page niche."""
    from cli_anything.social_trends.theme_pages import get_niche_strategy

    strategy = get_niche_strategy(niche)
    if not strategy:
        click.echo(f"Unknown niche '{niche}'. Run: social-trends theme-pages list", err=True)
        sys.exit(1)

    _out(strategy, f"\n{'='*60}\nTheme Page Strategy: {strategy['name']}\n{'='*60}")


@theme_pages.command("roadmap")
@click.option("--followers", default=0, type=int, help="Your current follower count")
def tp_roadmap(followers: int):
    """
    Get the step-by-step conversion roadmap.
    Starts from your current growth phase.
    """
    from cli_anything.social_trends.theme_pages import get_conversion_roadmap

    roadmap = get_conversion_roadmap(current_followers=followers)
    _out(roadmap, f"\n{'='*60}\nTheme Page Conversion Roadmap\n{'='*60}")

    if not _json_output:
        click.echo(f"\nStarting from Phase {roadmap[0]['phase']}: {roadmap[0]['name']}")
        click.echo(f"Target: {roadmap[0]['followers_target']} ({roadmap[0]['timeline']})")


@theme_pages.command("revenue")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", required=True, help="Niche key from 'theme-pages list'")
@click.option("--followers", required=True, type=int)
@click.option("--posts-week", default=7, type=int)
def tp_revenue(platform: str, niche: str, followers: int, posts_week: int):
    """Estimate monthly revenue potential for your account."""
    from cli_anything.social_trends.theme_pages import estimate_revenue

    result = estimate_revenue(
        followers=followers,
        platform=platform,
        niche_key=niche,
        posts_per_week=posts_week,
    )
    _out(result, f"\n{'='*60}\nRevenue Estimate\n{'='*60}")


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@cli.command("dashboard")
@click.option("--region", default="US", show_default=True)
@click.option("--niche", default="", help="Filter/adapt trends to a niche")
@click.option("--limit", default=10, show_default=True)
def dashboard(region: str, niche: str, limit: int):
    """
    Full trend dashboard — pulls YouTube trends, TikTok hashtags & sounds in one shot.
    Use this daily to stay on top of what's viral.
    """
    from cli_anything.social_trends.scrapers import youtube, tiktok, music as music_mod

    click.echo(f"\n{'='*65}")
    click.echo(f"  SOCIAL TRENDS DASHBOARD  |  Region: {region}  |  Niche: {niche or 'All'}")
    click.echo(f"{'='*65}\n")

    # ── YouTube Trending ──
    click.echo(click.style("▶  YOUTUBE TRENDING VIDEOS", bold=True))
    yt_videos = youtube.get_trending_videos(region=region, max_results=limit)
    if yt_videos:
        for i, v in enumerate(yt_videos, 1):
            click.echo(f"  {i:2}. {v['title'][:60]} — {v['channel']} ({v['views']})")
    else:
        click.echo("  [Could not fetch — install yt-dlp: pip install yt-dlp]")

    click.echo("")

    # ── YouTube Hashtags ──
    click.echo(click.style("▶  YOUTUBE TRENDING HASHTAGS (derived)", bold=True))
    yt_tags = youtube.extract_hashtags_from_titles(yt_videos) if yt_videos else []
    if yt_tags:
        click.echo("  " + "  ".join(t["hashtag"] for t in yt_tags[:12]))
    else:
        click.echo("  [No hashtag data]")

    click.echo("")

    # ── TikTok Hashtags ──
    click.echo(click.style("▶  TIKTOK TRENDING HASHTAGS", bold=True))
    tt_tags = tiktok.get_trending_hashtags(region=region, limit=15)
    if tt_tags:
        for t in tt_tags[:limit]:
            views = f"{t['video_views']:,}" if t.get("video_views") else "N/A"
            posts = f"{t['post_count']:,}" if t.get("post_count") else "N/A"
            click.echo(f"  #{t['hashtag'].lstrip('#'):<30} views: {views:<15} posts: {posts}")
    else:
        click.echo("  [TikTok API unavailable — try with VPN or later]")

    click.echo("")

    # ── TikTok Sounds ──
    click.echo(click.style("▶  TIKTOK TRENDING SOUNDS", bold=True))
    tt_sounds = tiktok.get_trending_sounds(region=region, limit=limit)
    if tt_sounds:
        for i, s in enumerate(tt_sounds, 1):
            click.echo(f"  {i:2}. {s['title'][:45]} — {s['artist']}")
    else:
        click.echo("  [TikTok sounds API unavailable]")

    click.echo("")

    # ── Billboard ──
    click.echo(click.style("▶  BILLBOARD HOT 100 (Top 10)", bold=True))
    bb = music_mod.get_billboard_hot100(limit=10)
    if bb:
        for t in bb:
            click.echo(f"  {t['rank']:2}. {t['title']} — {t['artist']}")
    else:
        click.echo("  [Billboard unavailable]")

    click.echo(f"\n{'='*65}")
    click.echo("  Run  social-trends --help  to explore all commands")
    click.echo(f"{'='*65}\n")


if __name__ == "__main__":
    cli()
