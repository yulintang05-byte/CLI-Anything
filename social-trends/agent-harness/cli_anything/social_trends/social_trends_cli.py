#!/usr/bin/env python3
"""Social Trends CLI — Discover viral trends, optimize accounts, and build theme pages.

Scrapes YouTube (Data API v3) and TikTok (via yt-dlp) for trending videos,
hashtags, and music. Provides account optimization scoring and a full
theme page creation + monetization guide.

Usage:
    # Set YouTube API key
    cli-anything-social-trends config set-key youtube AIza...

    # Get trending content
    cli-anything-social-trends trends youtube --region US --category music
    cli-anything-social-trends trends tiktok --count 30
    cli-anything-social-trends trends cross-platform --top 20

    # Hashtag tools
    cli-anything-social-trends hashtags trending --platform youtube
    cli-anything-social-trends hashtags optimize --platform tiktok --niche fitness
    cli-anything-social-trends hashtags analyze "#fyp #fitness #gym"

    # Account optimization
    cli-anything-social-trends account add tiktok @myhandle
    cli-anything-social-trends account score tiktok @myhandle
    cli-anything-social-trends account growth-plan tiktok @myhandle --goal 100000

    # Theme page guide
    cli-anything-social-trends theme-pages niches
    cli-anything-social-trends theme-pages guide --niche fitness
    cli-anything-social-trends theme-pages 30-day-plan
    cli-anything-social-trends theme-pages income --followers 50000 --er 3.5

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import shlex
import click
from typing import Optional, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core.youtube_trends import YouTubeTrends, CATEGORIES
from cli_anything.social_trends.core.tiktok_trends import TikTokTrends
from cli_anything.social_trends.core.hashtag_analyzer import HashtagAnalyzer
from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, AccountProfile
from cli_anything.social_trends.core.theme_pages import ThemePageGuide
from cli_anything.social_trends.utils.social_backend import (
    get_youtube_client, get_tiktok_client,
    check_ytdlp_available, check_youtube_api_key,
    merge_platform_trends,
)

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


def _yt_client() -> Optional[YouTubeTrends]:
    key = get_session().get_api_key("youtube")
    if not key:
        if not _json_output:
            click.echo("  [!] No YouTube API key set. Run: cli-anything-social-trends config set-key youtube <KEY>", err=True)
        return None
    return get_youtube_client(key)


def _tt_client() -> TikTokTrends:
    return get_tiktok_client()


# ── Output helpers ─────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0) -> None:
    pad = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{pad}  {k}: {v}")


def _print_list(items: list, indent: int = 0) -> None:
    pad = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{pad}[{i + 1}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{pad}  - {item}")


def _table(headers: list[str], rows: list[list], col_width: int = 22) -> None:
    header_row = "  ".join(str(h).ljust(col_width) for h in headers)
    click.echo(f"\n  {header_row}")
    click.echo("  " + "-" * (col_width * len(headers) + 2 * (len(headers) - 1)))
    for row in rows:
        cells = "  ".join(str(c)[:col_width].ljust(col_width) for c in row)
        click.echo(f"  {cells}")
    click.echo()


def _err(msg: str) -> None:
    click.echo(f"  [error] {msg}", err=True)


def _ok(msg: str) -> None:
    click.echo(f"  [ok] {msg}")


def _info(msg: str) -> None:
    click.echo(f"  [info] {msg}")


# ── Root command ──────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "json_out", is_flag=True, help="Output JSON for agent consumption")
@click.pass_context
def main(ctx: click.Context, json_out: bool) -> None:
    """Social Trends CLI — YouTube & TikTok trend discovery, account optimization, theme pages."""
    global _json_output, _repl_mode
    _json_output = json_out
    if ctx.invoked_subcommand is None:
        _repl_mode = True
        _run_repl()


def _run_repl() -> None:
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        ps = PromptSession(history=InMemoryHistory())
        _print_banner()
        click.echo("  Type a command or 'help'. Ctrl+D or 'exit' to quit.\n")
        while True:
            try:
                raw = ps.prompt("social-trends> ")
            except EOFError:
                break
            line = raw.strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit", "q"):
                break
            if line.lower() == "help":
                click.echo(main.get_help(click.Context(main)))
                continue
            try:
                args = shlex.split(line)
                ctx = main.make_context("social-trends", args, standalone_mode=False)
                main.invoke(ctx)
            except click.exceptions.UsageError as e:
                _err(str(e))
            except SystemExit:
                pass
            except Exception as e:
                _err(str(e))
    except ImportError:
        _err("prompt-toolkit not installed. Run: pip install prompt-toolkit")


def _print_banner() -> None:
    click.echo("\n  \033[38;5;213m╔══════════════════════════════════════════╗\033[0m")
    click.echo("  \033[38;5;213m║\033[0m  \033[1m\033[38;5;80mcli-anything-social-trends\033[0m  v1.0.0       \033[38;5;213m║\033[0m")
    click.echo("  \033[38;5;213m║\033[0m  YouTube · TikTok · Hashtags · Optimizer  \033[38;5;213m║\033[0m")
    click.echo("  \033[38;5;213m╚══════════════════════════════════════════╝\033[0m\n")


# ── config ────────────────────────────────────────────────────────────────────

@main.group()
def config() -> None:
    """Configure API keys, region, and settings."""


@config.command("set-key")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"], case_sensitive=False))
@click.argument("key")
def config_set_key(platform: str, key: str) -> None:
    """Set an API key for a platform."""
    sess = get_session()
    if platform == "youtube":
        result = check_youtube_api_key(key)
        if not result["valid"]:
            _err(f"YouTube key validation failed: {result['message']}")
            return
    sess.set_api_key(platform, key)
    _ok(f"{platform} API key saved to {sess._config_path}")


@config.command("set-region")
@click.argument("region", default="US")
def config_set_region(region: str) -> None:
    """Set default region code (US, GB, JP, etc.)."""
    get_session().set_region(region)
    _ok(f"Default region set to {region.upper()}")


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    sess = get_session()
    data = sess.to_dict()
    output(data, "\n  Current Configuration:")


@config.command("check")
def config_check() -> None:
    """Verify tools and API keys are working."""
    results = {}
    results["yt_dlp_installed"] = check_ytdlp_available()
    yt_key = get_session().get_api_key("youtube")
    if yt_key:
        results["youtube_api_key"] = check_youtube_api_key(yt_key)
    else:
        results["youtube_api_key"] = {"valid": False, "message": "Not set — run: config set-key youtube <KEY>"}
    output(results, "\n  Dependency Check:")


# ── trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends() -> None:
    """Fetch trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default=None, help="Region code (default: session region)")
@click.option("--category", default="all", help=f"Category: {', '.join(CATEGORIES.keys())}")
@click.option("--count", default=20, help="Number of videos (max 50)")
@click.option("--show-hashtags", is_flag=True, default=False, help="Show hashtags per video")
def trends_youtube(region: str, category: str, count: int, show_hashtags: bool) -> None:
    """Fetch trending YouTube videos."""
    yt = _yt_client()
    if not yt:
        return
    sess = get_session()
    region = region or sess.get_region()
    click.echo(f"\n  Fetching YouTube trending ({category}, {region})...")
    try:
        videos = yt.get_trending_videos(region=region, category=category, max_results=count)
    except Exception as e:
        _err(str(e))
        return
    if _json_output:
        output(videos)
        return
    headers = ["#", "Title", "Channel", "Views", "Likes"]
    rows = []
    for i, v in enumerate(videos[:count], 1):
        rows.append([i, v["title"][:40], v["channel"][:20], f"{v['views']:,}", f"{v['likes']:,}"])
    _table(headers, rows)
    if show_hashtags:
        click.echo("  Top hashtags found:")
        all_tags: list[str] = []
        for v in videos:
            all_tags.extend(v.get("hashtags", []))
        from collections import Counter
        for tag, cnt in Counter(all_tags).most_common(15):
            click.echo(f"    #{tag} ({cnt}x)")
        click.echo()
    sess.cache_trends("youtube_videos", videos)
    _info(f"{len(videos)} videos fetched and cached.")


@trends.command("tiktok")
@click.option("--count", default=30, help="Number of videos to fetch")
def trends_tiktok(count: int) -> None:
    """Fetch trending TikTok videos via yt-dlp."""
    if not check_ytdlp_available():
        _err("yt-dlp not found. Install with: pip install yt-dlp")
        return
    click.echo(f"\n  Fetching TikTok trending (this may take 30-60s)...")
    try:
        tt = _tt_client()
        videos = tt.get_trending_videos(count=count)
    except Exception as e:
        _err(str(e))
        return
    if _json_output:
        output(videos)
        return
    if videos and "error" in videos[0]:
        _err(videos[0]["error"])
        click.echo(f"  Tip: {videos[0].get('tip', '')}")
        return
    headers = ["#", "Title", "Author", "Views", "Likes", "Duration"]
    rows = [
        [i, v["title"][:38], v["author"][:18], f"{v['view_count']:,}", f"{v['like_count']:,}", f"{v['duration']}s"]
        for i, v in enumerate(videos[:count], 1)
    ]
    _table(headers, rows)
    get_session().cache_trends("tiktok_videos", videos)
    _info(f"{len(videos)} TikTok videos fetched and cached.")


@trends.command("music")
@click.option("--platform", default="youtube", type=click.Choice(["youtube", "tiktok"]))
@click.option("--region", default=None, help="Region code")
@click.option("--count", default=20)
def trends_music(platform: str, region: str, count: int) -> None:
    """Get trending music/audio."""
    sess = get_session()
    region = region or sess.get_region()
    if platform == "youtube":
        yt = _yt_client()
        if not yt:
            return
        click.echo(f"\n  Fetching YouTube trending music ({region})...")
        try:
            music = yt.get_trending_music(region=region, max_results=count)
        except Exception as e:
            _err(str(e))
            return
        if _json_output:
            output(music)
            return
        headers = ["#", "Title", "Artist/Channel", "Views", "Likes"]
        rows = [
            [i, m["title"][:35], m["artist"][:22], f"{m['views']:,}", f"{m['likes']:,}"]
            for i, m in enumerate(music, 1)
        ]
        _table(headers, rows)
    else:
        if not check_ytdlp_available():
            _err("yt-dlp not found. Install with: pip install yt-dlp")
            return
        click.echo("\n  Fetching TikTok trending sounds (via trending videos)...")
        try:
            tt = _tt_client()
            sounds = tt.get_trending_sounds(top_n=count)
        except Exception as e:
            _err(str(e))
            return
        if _json_output:
            output(sounds)
            return
        headers = ["#", "Music Title", "Artist", "Videos", "Total Views"]
        rows = [
            [i, s["music_title"][:35], s["artist"][:20], s["trending_videos_count"], f"{s['total_views']:,}"]
            for i, s in enumerate(sounds, 1)
        ]
        _table(headers, rows)


@trends.command("cross-platform")
@click.option("--region", default=None)
@click.option("--top", default=20, help="Number of cross-platform hashtags to show")
def trends_cross_platform(region: str, top: int) -> None:
    """Merge YouTube + TikTok trends into unified cross-platform hashtag list."""
    sess = get_session()
    region = region or sess.get_region()
    yt_hashtags: list = []
    tt_hashtags: list = []

    yt = _yt_client()
    if yt:
        click.echo("  Fetching YouTube hashtags...")
        try:
            yt_hashtags = yt.get_trending_hashtags(region=region)
        except Exception as e:
            _info(f"YouTube fetch failed: {e}")

    if check_ytdlp_available():
        click.echo("  Fetching TikTok hashtags (may take 30-60s)...")
        try:
            tt = _tt_client()
            tt_hashtags = tt.get_trending_hashtags(top_n=50)
        except Exception as e:
            _info(f"TikTok fetch failed: {e}")

    merged = merge_platform_trends(yt_hashtags, tt_hashtags, top_n=top)
    if _json_output:
        output(merged)
        return
    headers = ["#", "Hashtag", "Platforms", "YT Score", "TT Views", "Cross Score"]
    rows = [
        [
            i,
            m["hashtag"],
            "+".join(m["platforms"]),
            m["youtube_score"],
            f"{m['tiktok_views']:,}",
            m["cross_platform_score"],
        ]
        for i, m in enumerate(merged, 1)
    ]
    _table(headers, rows, col_width=18)
    sess.cache_trends("cross_platform_hashtags", merged)


# ── hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Hashtag analysis and optimization tools."""


@hashtags.command("trending")
@click.option("--platform", default="youtube", type=click.Choice(["youtube", "tiktok"]))
@click.option("--region", default=None)
@click.option("--top", default=30)
def hashtags_trending(platform: str, region: str, top: int) -> None:
    """Show trending hashtags for a platform."""
    sess = get_session()
    region = region or sess.get_region()
    if platform == "youtube":
        yt = _yt_client()
        if not yt:
            return
        click.echo(f"\n  Top {top} YouTube trending hashtags ({region})...")
        try:
            tags = yt.get_trending_hashtags(region=region, top_n=top)
        except Exception as e:
            _err(str(e))
            return
        if _json_output:
            output(tags)
            return
        headers = ["#", "Hashtag", "Appearances", "Views (trending)", "Score"]
        rows = [
            [i, t["hashtag"], t["appearances"], f"{t['total_views_on_trending']:,}", t["score"]]
            for i, t in enumerate(tags, 1)
        ]
        _table(headers, rows)
    else:
        if not check_ytdlp_available():
            _err("yt-dlp not found. Install: pip install yt-dlp")
            return
        click.echo(f"\n  Top {top} TikTok trending hashtags...")
        try:
            tt = _tt_client()
            tags = tt.get_trending_hashtags(top_n=top)
        except Exception as e:
            _err(str(e))
            return
        if _json_output:
            output(tags)
            return
        if tags and "hashtag" in tags[0]:
            headers = ["#", "Hashtag", "Views", "Video Count"]
            rows = [
                [i, t["hashtag"], f"{t.get('view_count', t.get('total_views', 0)):,}", t.get("video_count", t.get("appearances_in_trending", 0))]
                for i, t in enumerate(tags, 1)
            ]
            _table(headers, rows)


@hashtags.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.option("--niche", required=True, help="Your content niche (fitness, finance, food, etc.)")
@click.option("--count", default=10, help="How many hashtags to generate")
def hashtags_optimize(platform: str, niche: str, count: int) -> None:
    """Build an optimized hashtag set for your niche + platform."""
    analyzer = HashtagAnalyzer()

    # Gather some trending tags to seed the optimization
    sess = get_session()
    trending: list[str] = []
    cached = sess.get_cached_trends(f"{platform}_videos")
    if cached:
        from collections import Counter
        ctr: Counter = Counter()
        for v in cached:
            for tag in v.get("hashtags", []):
                ctr[tag.lower()] += 1
        trending = [t for t, _ in ctr.most_common(20)]

    result = analyzer.build_optimal_set(
        platform=platform,
        niche=niche,
        trending_tags=trending,
        count=count,
    )
    output(result, f"\n  Optimized {platform} hashtag set for #{niche}:")


@hashtags.command("analyze")
@click.argument("hashtag_string")
def hashtags_analyze(hashtag_string: str) -> None:
    """Analyze a list of hashtags (space or comma separated).

    Example: hashtags analyze "#fyp #fitness #gym workout motivation"
    """
    import re
    tags = re.findall(r"#?\w+", hashtag_string)
    analyzer = HashtagAnalyzer()
    result = analyzer.analyze_hashtags(tags)
    output(result, "\n  Hashtag Analysis:")


@hashtags.command("niches")
def hashtags_niches() -> None:
    """Show available niche hashtag presets."""
    analyzer = HashtagAnalyzer()
    niches = analyzer.list_niches()
    click.echo("\n  Available niches with preset hashtags:")
    for n in niches:
        tags = analyzer.get_niche_tags(n)
        click.echo(f"    {n:15s}  {' '.join(tags[:6])}")
    click.echo()


# ── account ───────────────────────────────────────────────────────────────────

@main.group()
def account() -> None:
    """Track and optimize your social media accounts."""


@account.command("add")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.argument("handle")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--posts", default=0, type=int)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--niche", default="")
@click.option("--posts-per-week", default=0.0, type=float)
@click.option("--hashtag-count", default=0, type=int)
@click.option("--has-link/--no-link", default=False)
@click.option("--has-bio/--no-bio", default=False)
@click.option("--uses-trending-audio/--no-trending-audio", default=False)
def account_add(
    platform: str, handle: str, followers: int, following: int,
    posts: int, avg_views: int, avg_likes: int, avg_comments: int,
    niche: str, posts_per_week: float, hashtag_count: int,
    has_link: bool, has_bio: bool, uses_trending_audio: bool,
) -> None:
    """Add an account to track."""
    meta = {
        "followers": followers,
        "following": following,
        "total_posts": posts,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "niche": niche,
        "posting_days_per_week": posts_per_week,
        "avg_hashtag_count": hashtag_count,
        "has_link": has_link,
        "has_bio": has_bio,
        "uses_trending_audio": uses_trending_audio,
    }
    get_session().add_account(platform, handle.lstrip("@"), meta)
    _ok(f"Account @{handle.lstrip('@')} ({platform}) saved.")


@account.command("list")
def account_list() -> None:
    """List all tracked accounts."""
    accounts = get_session().list_accounts()
    if not accounts:
        click.echo("  No accounts tracked. Run: account add <platform> <handle>")
        return
    for platform, handles in accounts.items():
        click.echo(f"\n  {platform.upper()}:")
        for handle, meta in handles.items():
            followers = meta.get("followers", 0)
            niche = meta.get("niche", "-")
            click.echo(f"    @{handle:20s}  {followers:>10,} followers  niche={niche}")
    click.echo()


@account.command("score")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.argument("handle")
def account_score(platform: str, handle: str) -> None:
    """Run a full optimization audit on an account."""
    handle = handle.lstrip("@")
    meta = get_session().get_account(platform, handle)
    if not meta:
        _err(f"Account @{handle} ({platform}) not found. Run: account add {platform} @{handle} [options]")
        return
    profile = AccountProfile(
        platform=platform,
        handle=handle,
        followers=meta.get("followers", 0),
        following=meta.get("following", 0),
        total_posts=meta.get("total_posts", 0),
        avg_views=meta.get("avg_views", 0),
        avg_likes=meta.get("avg_likes", 0),
        avg_comments=meta.get("avg_comments", 0),
        has_bio=meta.get("has_bio", False),
        bio_text=meta.get("bio_text", ""),
        has_link=meta.get("has_link", False),
        posting_days_per_week=meta.get("posting_days_per_week", 0.0),
        uses_hashtags=meta.get("avg_hashtag_count", 0) > 0,
        avg_hashtag_count=meta.get("avg_hashtag_count", 0),
        uses_trending_audio=meta.get("uses_trending_audio", False),
        has_cta_in_bio=meta.get("has_cta_in_bio", False),
        niche=meta.get("niche", ""),
    )
    optimizer = AccountOptimizer()
    result = optimizer.score_account(profile)
    output(result, f"\n  Account Optimization Score — @{handle} ({platform})")


@account.command("growth-plan")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.argument("handle")
@click.option("--goal", required=True, type=int, help="Target follower count")
@click.option("--weeks", default=12, type=int)
def account_growth_plan(platform: str, handle: str, goal: int, weeks: int) -> None:
    """Generate a week-by-week growth plan for an account."""
    handle = handle.lstrip("@")
    meta = get_session().get_account(platform, handle)
    if not meta:
        _err(f"Account not found. Add with: account add {platform} @{handle}")
        return
    profile = AccountProfile(
        platform=platform,
        handle=handle,
        followers=meta.get("followers", 0),
        posting_days_per_week=meta.get("posting_days_per_week", 1.0),
    )
    optimizer = AccountOptimizer()
    plan = optimizer.growth_plan(profile, goal_followers=goal, weeks=weeks)
    output(plan, f"\n  {weeks}-Week Growth Plan: @{handle} → {goal:,} followers")


@account.command("remove")
@click.argument("platform")
@click.argument("handle")
def account_remove(platform: str, handle: str) -> None:
    """Remove a tracked account."""
    removed = get_session().remove_account(platform, handle.lstrip("@"))
    if removed:
        _ok(f"@{handle.lstrip('@')} removed.")
    else:
        _err(f"Account not found.")


# ── theme-pages ───────────────────────────────────────────────────────────────

@main.group("theme-pages")
def theme_pages() -> None:
    """Theme page creation, growth, and monetization guide."""


@theme_pages.command("niches")
@click.option("--sort", default="monetization", type=click.Choice(["monetization", "growth", "difficulty"]))
def tp_niches(sort: str) -> None:
    """List all theme page niches with difficulty and income potential."""
    guide = ThemePageGuide()
    niches = guide.list_niches()
    if _json_output:
        output(niches)
        return
    headers = ["Niche", "Difficulty", "Income Potential", "Growth", "Platforms"]
    sort_key = {
        "monetization": lambda x: ["medium", "high", "very_high"].index(x.get("monetization_potential", "medium")),
        "growth": lambda x: ["volatile", "slow", "medium", "fast"].index(x.get("growth_rate", "medium")),
        "difficulty": lambda x: ["very_easy", "easy", "medium", "hard"].index(x.get("difficulty", "medium")),
    }
    sorted_niches = sorted(niches, key=sort_key.get(sort, lambda x: 0), reverse=(sort != "difficulty"))
    rows = [
        [
            n["niche"],
            n["difficulty"],
            n["monetization_potential"],
            n["growth_rate"],
            ", ".join(n["platforms"][:2]),
        ]
        for n in sorted_niches
    ]
    _table(headers, rows, col_width=18)


@theme_pages.command("guide")
@click.option("--niche", required=True, help="Niche to get the full guide for")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube"]))
def tp_guide(niche: str, platform: str) -> None:
    """Get a full content strategy guide for a niche + platform."""
    guide = ThemePageGuide()
    result = guide.get_content_strategy(niche=niche, platform=platform)
    output(result, f"\n  Theme Page Strategy — {niche} on {platform}:")


@theme_pages.command("recommend")
@click.option("--fast-growth", is_flag=True)
@click.option("--high-income", is_flag=True)
@click.option("--easy-start", is_flag=True)
def tp_recommend(fast_growth: bool, high_income: bool, easy_start: bool) -> None:
    """Get personalized niche recommendations based on your goals."""
    guide = ThemePageGuide()
    goals = []
    if fast_growth:
        goals.append("fast_growth")
    if high_income:
        goals.append("high_income")
    if easy_start:
        goals.append("easy_start")
    if not goals:
        goals = ["fast_growth", "high_income"]
    recs = guide.recommend_niche(goals)
    output(recs, "\n  Top Recommended Niches:")


@theme_pages.command("30-day-plan")
def tp_30_day_plan() -> None:
    """Show the complete 30-day theme page launch plan."""
    guide = ThemePageGuide()
    plan = guide.get_30_day_plan()
    if _json_output:
        output(plan)
        return
    click.echo("\n  ══ 30-Day Theme Page Launch Plan ══\n")
    for phase in plan:
        click.echo(f"  Days {phase['days']} — {phase['phase'].upper()}")
        for task in phase["tasks"]:
            click.echo(f"    • {task}")
        click.echo()


@theme_pages.command("monetization")
@click.option("--tactic", default=None, help="Specific tactic: affiliate_links, shoutout_sales, digital_products, etc.")
def tp_monetization(tactic: Optional[str]) -> None:
    """Show monetization tactics for theme pages."""
    guide = ThemePageGuide()
    if tactic:
        result = guide.get_conversion_tactic(tactic)
        if not result:
            _err(f"Unknown tactic '{tactic}'. Run without --tactic to see all options.")
            return
        output(result, f"\n  {result['name']}:")
    else:
        tactics = guide.list_conversion_tactics()
        output(tactics, "\n  Monetization Tactics:")


@theme_pages.command("income")
@click.option("--followers", required=True, type=int)
@click.option("--er", default=3.0, type=float, help="Engagement rate %")
@click.option("--platform", default="tiktok", type=click.Choice(["youtube", "tiktok", "instagram"]))
def tp_income(followers: int, er: float, platform: str) -> None:
    """Estimate monthly income potential at a given follower/engagement level."""
    guide = ThemePageGuide()
    result = guide.income_calculator(followers=followers, engagement_rate=er, platform=platform)
    output(result, f"\n  Income Estimate — {followers:,} followers on {platform}:")


# ── status ────────────────────────────────────────────────────────────────────

@main.command("status")
def status() -> None:
    """Show session overview: accounts, cache, and config."""
    sess = get_session()
    data = sess.to_dict()
    accounts = sess.list_accounts()
    data["accounts"] = {p: list(h.keys()) for p, h in accounts.items()}
    output(data, "\n  Session Status:")
