"""Social Trends CLI — agent-native viral trend intelligence & account optimizer.

Usage:
    social-trends [--json] <command>
    social-trends  (launches REPL)

Commands:
    trends fetch youtube   Fetch YouTube trending videos + hashtags + music
    trends fetch tiktok    Fetch TikTok trending hashtags + sounds
    trends fetch all       Fetch from both platforms and combine signals
    trends music           Get trending music/sounds across platforms
    account add            Register an account for tracking
    account list           List tracked accounts
    account optimize       Generate optimization report for an account
    account schedule       Generate posting schedule for accounts
    hashtags strategy      Build tiered hashtag strategy for a niche
    hashtags recommend     Quick hashtag recommendations
    calendar generate      Generate content calendar with video ideas
    theme-page niches      List all theme page niches ranked by opportunity
    theme-page strategy    Full strategy for a specific niche
    theme-page roadmap     Complete theme page creation roadmap
    theme-page conversion  Conversion and monetization playbook
    config set             Set API keys and settings
    config show            Show current configuration
    session status         Show session cache status
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core import (
    youtube as yt_mod,
    tiktok as tt_mod,
    optimizer as opt_mod,
    theme_pages as tp_mod,
    config as cfg_mod,
)
from cli_anything.social_trends.core.session import Session

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(click.style(f"\n  {message}", fg="bright_white", bold=True))
        _pretty(data, indent=2)


def _pretty(data: Any, indent: int = 2) -> None:
    pad = " " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{click.style(str(k), fg='cyan')}:")
                _pretty(v, indent + 2)
            else:
                click.echo(f"{pad}{click.style(str(k), fg='cyan')}: {v}")
    elif isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for i, item in enumerate(data):
            if isinstance(item, dict):
                parts = [f"{click.style(k, fg='bright_black')}={v}" for k, v in item.items()
                         if not isinstance(v, (dict, list))]
                click.echo(f"{pad}[{i}] " + "  ".join(parts))
            else:
                click.echo(f"{pad}- {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(click.style(f"\n  Error: {msg}", fg="red"), err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, PermissionError, FileNotFoundError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """social-trends — viral trend intelligence & account optimizer.

    Scrape YouTube and TikTok for viral trends, hashtags, and music.
    Build hashtag strategies, content calendars, and theme pages.

    \b
    Quick start:
      social-trends config set --youtube-key YOUR_KEY
      social-trends trends fetch youtube --region US
      social-trends hashtags strategy --niche finance --platform tiktok
      social-trends theme-page niches
      social-trends theme-page roadmap
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend discovery — fetch viral trends from YouTube and TikTok."""
    pass


@trends.group("fetch")
def trends_fetch():
    """Fetch trending content from a platform."""
    pass


@trends_fetch.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO country code (US, GB, IN, etc.)")
@click.option("--category", default="all", show_default=True,
              help="Category: all/music/gaming/entertainment/education/howto/sports/film")
@click.option("--max", "max_results", default=25, show_default=True, type=int, help="Videos to fetch (max 50)")
@click.option("--api-key", default=None, help="YouTube Data API v3 key (overrides config)")
@handle_error
def trends_fetch_youtube(region: str, category: str, max_results: int, api_key: Optional[str]) -> None:
    """Fetch trending YouTube videos with hashtags and music."""
    sess = get_session()
    key = api_key or cfg_mod.get_key("youtube_api_key")
    if not key:
        raise ValueError(
            "No YouTube API key configured.\n"
            "  Get a free key: https://console.cloud.google.com/apis/library/youtube.googleapis.com\n"
            "  Then run: social-trends config set --youtube-key YOUR_KEY"
        )

    click.echo(click.style(f"\n  Fetching YouTube trending ({region}, {category})...", fg="cyan"))
    data = yt_mod.fetch_trending(key, region, max_results, category)
    sess.cache_trends("youtube", data)

    if not _json_output:
        _print_youtube_report(data)
    else:
        output(data)


def _print_youtube_report(data: dict) -> None:
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    click.echo(click.style(f"\n  YouTube Trending — {data['region']} / {data['category']}", fg="yellow", bold=True))
    click.echo(click.style(f"  {data['video_count']} trending videos  |  {data['fetched_at'][:19]}\n", fg="bright_black"))

    click.echo(click.style("  TOP VIDEOS", fg="cyan", bold=True))
    skin.table(
        ["#", "Title", "Channel", "Views", "Likes"],
        [
            [
                str(i + 1),
                v["title"][:40],
                v["channel"][:20],
                f"{v['views']:,}",
                f"{v['likes']:,}",
            ]
            for i, v in enumerate(data["videos"][:10])
        ],
    )

    click.echo(click.style("\n  TRENDING HASHTAGS", fg="cyan", bold=True))
    skin.table(
        ["Hashtag", "Videos", "Total Views"],
        [
            [f"#{h['hashtag']}", str(h["video_count"]), f"{h['total_views']:,}"]
            for h in data["trending_hashtags"][:15]
        ],
    )

    if data.get("trending_music"):
        click.echo(click.style("\n  TRENDING MUSIC", fg="cyan", bold=True))
        skin.table(
            ["Title", "Mentions", "Total Views"],
            [
                [m["title"][:45], str(m["mention_count"]), f"{m['total_views']:,}"]
                for m in data["trending_music"][:8]
            ],
        )


@trends_fetch.command("tiktok")
@click.option("--count", default=20, show_default=True, type=int, help="Number of hashtags to fetch")
@click.option("--session-cookie", default=None, help="TikTok sessionid cookie for live data")
@handle_error
def trends_fetch_tiktok(count: int, session_cookie: Optional[str]) -> None:
    """Fetch trending TikTok hashtags and sounds."""
    sess = get_session()
    cookie = session_cookie or cfg_mod.get_key("tiktok_session_cookie")

    click.echo(click.style("\n  Fetching TikTok trending data...", fg="cyan"))
    data = tt_mod.fetch_trending_all(cookie or None)
    sess.cache_trends("tiktok", data)

    if not _json_output:
        _print_tiktok_report(data)
    else:
        output(data)


def _print_tiktok_report(data: dict) -> None:
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    source_label = "live" if data.get("hashtags", {}).get("source") == "live_api" else "curated"
    click.echo(click.style(f"\n  TikTok Trending  [{source_label}]  |  {data['fetched_at'][:19]}", fg="magenta", bold=True))

    viral = data.get("summary", {}).get("viral_hashtags", [])
    rising = data.get("summary", {}).get("rising_hashtags", [])

    if viral:
        click.echo(click.style("\n  VIRAL RIGHT NOW", fg="red", bold=True))
        click.echo("  " + "  ".join(click.style(f"#{h}", fg="red", bold=True) for h in viral[:8]))

    if rising:
        click.echo(click.style("\n  RISING FAST", fg="yellow", bold=True))
        click.echo("  " + "  ".join(click.style(f"#{h}", fg="yellow") for h in rising[:8]))

    hashtags = data.get("hashtags", {}).get("hashtags", [])
    if hashtags:
        click.echo(click.style("\n  TOP HASHTAGS", fg="cyan", bold=True))
        skin.table(
            ["Hashtag", "Category", "Videos", "Views", "Growth"],
            [
                [
                    f"#{h['hashtag']}",
                    h.get("category", "-"),
                    f"{h.get('video_count', 0):,}",
                    f"{h.get('view_count', 0):,}",
                    h.get("growth", "-"),
                ]
                for h in hashtags[:15]
            ],
        )

    sounds = data.get("sounds", {}).get("sounds", [])
    if sounds:
        click.echo(click.style("\n  TRENDING SOUNDS", fg="cyan", bold=True))
        skin.table(
            ["Title", "Artist", "Category", "Mood", "Videos"],
            [
                [s["title"][:35], s.get("artist", "")[:20], s.get("category", ""), s.get("mood", ""), f"{s.get('video_count', 0):,}"]
                for s in sounds[:8]
            ],
        )


@trends_fetch.command("all")
@click.option("--region", default="US", show_default=True)
@click.option("--api-key", default=None)
@click.option("--session-cookie", default=None)
@handle_error
def trends_fetch_all(region: str, api_key: Optional[str], session_cookie: Optional[str]) -> None:
    """Fetch trending data from YouTube and TikTok and combine signals."""
    sess = get_session()

    results: dict = {"combined": True, "region": region}

    # TikTok (no key required)
    cookie = session_cookie or cfg_mod.get_key("tiktok_session_cookie")
    click.echo(click.style("  Fetching TikTok...", fg="cyan"))
    tt_data = tt_mod.fetch_trending_all(cookie or None)
    sess.cache_trends("tiktok", tt_data)
    results["tiktok"] = tt_data

    # YouTube (key required)
    key = api_key or cfg_mod.get_key("youtube_api_key")
    if key:
        click.echo(click.style("  Fetching YouTube...", fg="cyan"))
        try:
            yt_data = yt_mod.fetch_trending(key, region, 25)
            sess.cache_trends("youtube", yt_data)
            results["youtube"] = yt_data
        except Exception as e:
            click.echo(click.style(f"  YouTube fetch failed: {e}", fg="yellow"))
            results["youtube"] = {"error": str(e)}
    else:
        click.echo(click.style("  Skipping YouTube (no API key — run: social-trends config set --youtube-key KEY)", fg="yellow"))
        results["youtube"] = {"skipped": "no api key"}

    # Cross-platform viral tags
    tt_viral = tt_data.get("summary", {}).get("viral_hashtags", [])
    yt_tags = [h["hashtag"] for h in results.get("youtube", {}).get("trending_hashtags", [])[:10]] if isinstance(results.get("youtube"), dict) and "trending_hashtags" in results.get("youtube", {}) else []
    cross_platform = [t for t in tt_viral if t in yt_tags]

    results["cross_platform_viral"] = cross_platform or tt_viral[:5]

    output(results, "Cross-Platform Trend Report")


@trends.command("music")
@click.option("--platform", default="tiktok", show_default=True, help="Platform: tiktok/youtube/all")
@click.option("--count", default=12, show_default=True, type=int)
@handle_error
def trends_music(platform: str, count: int) -> None:
    """Get trending music and sounds for content creation."""
    sess = get_session()

    if platform in ("tiktok", "all"):
        data = tt_mod.fetch_trending_sounds(count=count)
        output(data, "Trending TikTok Sounds")

    if platform in ("youtube", "all"):
        cached = sess.get_cached_trends("youtube")
        if cached and cached.get("trending_music"):
            output({"platform": "youtube", "trending_music": cached["trending_music"][:count]}, "Trending YouTube Music")
        else:
            click.echo(click.style(
                "  Run 'trends fetch youtube' first to get YouTube music trends.", fg="yellow"
            ))


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account management — add, list, optimize, and schedule."""
    pass


@account.command("add")
@click.option("--platform", required=True, type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.option("--handle", required=True, help="Account handle/username (without @)")
@click.option("--niche", default="general", help="Account niche")
@handle_error
def account_add(platform: str, handle: str, niche: str) -> None:
    """Register an account for tracking and optimization."""
    cfg_mod.add_account(platform, handle, {"niche": niche})
    output(
        {"success": True, "platform": platform, "handle": handle, "niche": niche},
        f"Added {platform} account @{handle} ({niche})"
    )


@account.command("list")
@handle_error
def account_list() -> None:
    """List all tracked accounts."""
    accounts = cfg_mod.list_accounts()
    if not accounts:
        click.echo("  No accounts registered. Use 'account add' to add one.")
        return

    if _json_output:
        output(accounts)
        return

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    rows = []
    for platform, handles in accounts.items():
        for handle, meta in handles.items():
            rows.append([platform, f"@{handle}", meta.get("niche", "-")])

    skin.table(["Platform", "Handle", "Niche"], rows)


@account.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["youtube", "tiktok"]))
@click.option("--handle", default=None, help="Account handle (for TikTok audit)")
@click.option("--channel-id", default=None, help="YouTube Channel ID (UC...)")
@click.option("--api-key", default=None, help="YouTube API key (overrides config)")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post")
@click.option("--avg-comments", default=0, type=int, help="Average comments per post")
@click.option("--posts-per-week", default=3, type=int, help="Current posting frequency per week")
@handle_error
def account_optimize(
    platform: str,
    handle: Optional[str],
    channel_id: Optional[str],
    api_key: Optional[str],
    followers: int,
    avg_views: int,
    avg_likes: int,
    avg_comments: int,
    posts_per_week: int,
) -> None:
    """Generate a full optimization report for an account."""
    result: dict = {}

    if platform == "tiktok":
        profile_url = f"https://www.tiktok.com/@{handle}" if handle else "https://www.tiktok.com/@yourhandle"
        audit = tt_mod.get_account_audit(profile_url)
        result.update(audit)

    elif platform == "youtube":
        key = api_key or cfg_mod.get_key("youtube_api_key")
        if channel_id and key:
            try:
                channel_info = yt_mod.get_channel_info(key, channel_id)
                result.update(channel_info)
            except Exception as e:
                click.echo(click.style(f"  Channel fetch failed: {e} — using manual metrics", fg="yellow"))
        result["best_posting_times"] = yt_mod.get_best_posting_times()

    # Always include metric-based analysis if metrics provided
    if followers or avg_views:
        analysis = opt_mod.analyze_account_metrics(
            platform, followers, avg_views, avg_likes, avg_comments, posts_per_week
        )
        result["metric_analysis"] = analysis

    output(result, f"{platform.title()} Account Optimization Report")


@account.command("schedule")
@click.option("--platforms", default="tiktok,youtube", show_default=True,
              help="Comma-separated platforms (tiktok,youtube,instagram)")
@click.option("--niche", default="general", show_default=True)
@click.option("--posts-per-day", default=2, show_default=True, type=int)
@click.option("--timezone", "tz", default="EST", show_default=True)
@handle_error
def account_schedule(platforms: str, niche: str, posts_per_day: int, tz: str) -> None:
    """Generate an optimized posting schedule for all platforms."""
    platform_list = [p.strip() for p in platforms.split(",")]
    schedule = opt_mod.generate_posting_schedule(platform_list, niche, posts_per_day, timezone_label=tz)
    output(schedule, f"7-Day Posting Schedule ({niche})")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag research — build strategies and get recommendations."""
    pass


@hashtags.command("strategy")
@click.option("--niche", required=True, help="Your content niche (finance/fitness/beauty/gaming/etc.)")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--count", default=10, show_default=True, type=int, help="Total hashtags to include")
@handle_error
def hashtags_strategy(niche: str, platform: str, count: int) -> None:
    """Build a tiered hashtag strategy mixing mega/large/niche/micro tags."""
    sess = get_session()
    cached_tt = sess.get_cached_trends("tiktok")
    trending = cached_tt.get("hashtags", {}).get("hashtags", []) if cached_tt else []

    strategy = opt_mod.generate_hashtag_strategy(niche, platform, count, trending)

    if _json_output:
        output(strategy)
        return

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    click.echo(click.style(f"\n  Hashtag Strategy — {niche} / {platform}", fg="yellow", bold=True))
    click.echo()

    click.echo(click.style("  READY-TO-USE SET", fg="cyan", bold=True))
    tags_str = " ".join(f"#{t}" for t in strategy["strategy"])
    click.echo(f"  {tags_str}\n")

    click.echo(click.style("  BY TIER", fg="cyan", bold=True))
    for tier, tags in strategy["by_tier"].items():
        click.echo(f"  {click.style(tier.upper(), fg='bright_white')}: {' '.join('#' + t for t in tags)}")

    click.echo(click.style("\n  CAPTION TEMPLATE", fg="cyan", bold=True))
    for line in strategy["caption_template"].split("\n"):
        click.echo(f"  {line}")

    click.echo(click.style(f"\n  TIP: {strategy['rotation_tip']}", fg="bright_black"))


@hashtags.command("recommend")
@click.option("--niche", required=True)
@click.option("--platform", default="tiktok", show_default=True)
@handle_error
def hashtags_recommend(niche: str, platform: str) -> None:
    """Quick hashtag recommendations for a niche (5 tags, ready to copy-paste)."""
    strategy = opt_mod.generate_hashtag_strategy(niche, platform, 5)
    tags = " ".join(f"#{t}" for t in strategy["strategy"])

    if _json_output:
        output({"niche": niche, "platform": platform, "hashtags": strategy["strategy"]})
        return

    click.echo(click.style(f"\n  Top 5 hashtags for #{niche} on {platform}:", fg="cyan"))
    click.echo(f"\n  {tags}\n")


# ── calendar group ────────────────────────────────────────────────────────────

@cli.group()
def calendar():
    """Content calendar generation — video ideas mapped to trends."""
    pass


@calendar.command("generate")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platforms", default="tiktok,youtube", show_default=True)
@click.option("--weeks", default=2, show_default=True, type=int, help="Weeks of content to generate")
@handle_error
def calendar_generate(niche: str, platforms: str, weeks: int) -> None:
    """Generate a content calendar with video ideas, hooks, and hashtags."""
    sess = get_session()
    platform_list = [p.strip() for p in platforms.split(",")]

    cached_tt = sess.get_cached_trends("tiktok")
    cached_yt = sess.get_cached_trends("youtube")
    trending_hashtags = (cached_tt or {}).get("hashtags", {}).get("hashtags", [])
    trending_sounds = (cached_tt or {}).get("sounds", {}).get("sounds", [])

    cal = opt_mod.generate_content_calendar(niche, platform_list, trending_hashtags, trending_sounds, weeks)

    if _json_output:
        output(cal)
        return

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    click.echo(click.style(f"\n  {weeks}-Week Content Calendar — {niche}", fg="yellow", bold=True))
    click.echo(click.style(f"  {cal['total_posts']} posts planned for: {', '.join(platform_list)}\n", fg="bright_black"))

    skin.table(
        ["Wk", "Day", "Type", "Idea", "Hook", "Sound"],
        [
            [
                str(entry["week"]),
                entry["day_of_week"],
                entry["content_type"],
                entry["video_idea"][:30],
                entry["hook"][:30],
                entry["trending_sound"][:20],
            ]
            for entry in cal["calendar"]
        ],
    )

    click.echo(click.style("\n  HASHTAG STRATEGY BY TIER", fg="cyan", bold=True))
    for tier, tags in cal["hashtag_strategy"].items():
        click.echo(f"  {tier}: {' '.join('#' + t for t in tags)}")


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page strategy — niches, roadmap, conversion, and monetization."""
    pass


@theme_page.command("niches")
@click.option("--sort", default="monetization_potential",
              type=click.Choice(["monetization_potential", "growth_speed", "difficulty"]),
              help="Sort niches by this field")
@handle_error
def theme_page_niches(sort: str) -> None:
    """List all theme page niches ranked by opportunity."""
    niches = tp_mod.get_niches(sort)

    if _json_output:
        output(niches)
        return

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    click.echo(click.style(f"\n  Theme Page Niches (sorted by {sort})\n", fg="yellow", bold=True))
    skin.table(
        ["ID", "Name", "Difficulty", "Competition", "Monetization", "Growth", "Engagement"],
        [
            [
                n["id"],
                n["name"],
                n["difficulty"],
                n["competition"],
                n["monetization_potential"],
                n["growth_speed"],
                n["avg_engagement_rate"],
            ]
            for n in niches
        ],
    )
    click.echo(click.style("\n  Run: social-trends theme-page strategy --niche <ID>  for full details\n", fg="bright_black"))


@theme_page.command("strategy")
@click.option("--niche", required=True, help="Niche ID (from 'theme-page niches')")
@handle_error
def theme_page_strategy(niche: str) -> None:
    """Get the full strategy, action plan, and monetization roadmap for a niche."""
    strategy = tp_mod.get_niche_strategy(niche)

    if _json_output:
        output(strategy)
        return

    click.echo(click.style(f"\n  Strategy: {strategy['name']}", fg="yellow", bold=True))
    click.echo(click.style(f"  Difficulty: {strategy['difficulty']}  |  Competition: {strategy['competition']}  |  Monetization: {strategy['monetization_potential']}\n", fg="bright_black"))

    click.echo(click.style("  DESCRIPTION", fg="cyan", bold=True))
    click.echo(f"  {strategy['description']}\n")

    click.echo(click.style("  CONTENT TYPES", fg="cyan", bold=True))
    click.echo("  " + ", ".join(strategy["content_types"]) + "\n")

    click.echo(click.style("  MONETIZATION PATHS", fg="cyan", bold=True))
    for i, path in enumerate(strategy["monetization_paths"], 1):
        click.echo(f"  {i}. {path}")

    click.echo(click.style("\n  CONVERSION PATH", fg="cyan", bold=True))
    click.echo(f"  {strategy['conversion_path']}\n")

    click.echo(click.style("  HASHTAGS", fg="cyan", bold=True))
    click.echo("  " + " ".join(f"#{h}" for h in strategy["hashtags"]) + "\n")

    click.echo(click.style("  30-DAY ACTION PLAN", fg="cyan", bold=True))
    for week in strategy["30_day_action_plan"]:
        click.echo(click.style(f"\n  Week {week['week']}: {week['focus']}", fg="bright_white"))
        for task in week["tasks"]:
            click.echo(f"    • {task}")

    click.echo(click.style("\n  MONETIZATION ROADMAP", fg="cyan", bold=True))
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.table(
        ["Milestone", "Income/mo", "Focus", "Action"],
        [
            [m["milestone"], m["income"], m["focus"], m["action"][:40]]
            for m in strategy["monetization_roadmap"]
        ],
    )

    if strategy.get("disclaimer"):
        click.echo(click.style(f"\n  ⚠ {strategy['disclaimer']}", fg="yellow"))


@theme_page.command("roadmap")
@click.option("--level", default="beginner",
              type=click.Choice(["beginner", "intermediate", "advanced"]))
@handle_error
def theme_page_roadmap(level: str) -> None:
    """Get the complete theme page creation and growth roadmap."""
    roadmap = tp_mod.get_roadmap(level)

    if _json_output:
        output(roadmap)
        return

    click.echo(click.style("\n  THEME PAGE ROADMAP\n", fg="yellow", bold=True))

    click.echo(click.style("  WHAT IS A THEME PAGE?", fg="cyan", bold=True))
    click.echo(f"  {roadmap['what_is_a_theme_page']}\n")

    click.echo(click.style("  WHY THEME PAGES WORK", fg="cyan", bold=True))
    for reason in roadmap["why_theme_pages_work"]:
        click.echo(f"  ✓ {reason}")

    click.echo(click.style("\n  SUCCESS FORMULA", fg="cyan", bold=True))
    for key, val in roadmap["success_formula"].items():
        click.echo(f"  {click.style(key.upper(), fg='bright_white')}: {val}")

    click.echo(click.style("\n  PHASES", fg="cyan", bold=True))
    for phase in roadmap["phases"]:
        click.echo(click.style(f"\n  Phase {phase['phase']}: {phase['name']}  [{phase['duration']}]", fg="bright_white"))
        for task in phase["tasks"]:
            click.echo(f"    • {task}")
        click.echo(f"    {click.style('Output:', fg='green')} {phase['output']}")

    click.echo(click.style("\n  INCOME TIMELINE", fg="cyan", bold=True))
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.table(
        ["Month", "Focus", "Income/mo", "Milestone"],
        [
            [str(m["month"]), m["focus"], m["realistic_income"], m["milestone"]]
            for m in roadmap["income_timeline"]
        ],
    )

    click.echo(click.style("\n  COMMON MISTAKES TO AVOID", fg="cyan", bold=True))
    for mistake in roadmap["common_mistakes"]:
        click.echo(f"  ✗ {mistake}")

    click.echo(click.style("\n  RECOMMENDED TOOLS STACK", fg="cyan", bold=True))
    for category, tools in roadmap["tools_stack"].items():
        click.echo(click.style(f"\n  {category.replace('_', ' ').title()}:", fg="bright_white"))
        for tool in tools:
            click.echo(f"    • {tool}")


@theme_page.command("conversion")
@handle_error
def theme_page_conversion() -> None:
    """Get the conversion and monetization playbook."""
    guide = tp_mod.get_conversion_guide()

    if _json_output:
        output(guide)
        return

    click.echo(click.style("\n  CONVERSION PLAYBOOK\n", fg="yellow", bold=True))

    click.echo(click.style("  FUNNEL", fg="cyan", bold=True))
    funnel = guide["conversion_funnel"]
    click.echo(f"  TOP    → {funnel['top']}")
    click.echo(f"  MIDDLE → {funnel['middle']}")
    click.echo(f"  BOTTOM → {funnel['bottom']}\n")

    click.echo(click.style("  TRAFFIC TO REVENUE PATHS", fg="cyan", bold=True))
    for path in guide["traffic_to_revenue_paths"]:
        click.echo(click.style(f"\n  {path['path'].upper()}", fg="bright_white"))
        click.echo(f"    How: {path['how']}")
        click.echo(f"    When: {path['when']}")
        click.echo(f"    Income: {path['income_range']}")
        click.echo(f"    Best niches: {', '.join(path['best_niches'])}")

    click.echo(click.style("\n  LINK IN BIO OPTIMIZATION", fg="cyan", bold=True))
    bio = guide["link_in_bio_optimization"]
    click.echo(f"  Tools: {', '.join(bio['tool_recommendations'])}")
    click.echo("  Include:")
    for item in bio["what_to_include"]:
        click.echo(f"    • {item}")
    click.echo(f"  CTA formula: {bio['cta_formula']}")

    click.echo(click.style("\n  EMAIL LIST STRATEGY", fg="cyan", bold=True))
    email = guide["email_list_strategy"]
    click.echo("  Lead magnet ideas:")
    for idea in email["lead_magnet_ideas"]:
        click.echo(f"    • {idea}")
    click.echo("\n  Email sequence:")
    for step in email["email_sequence"]:
        click.echo(f"    {step}")
    click.echo(f"\n  Platforms: {', '.join(email['platforms'])}")


# ── config group ──────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration — API keys and account settings."""
    pass


@config.command("set")
@click.option("--youtube-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-cookie", default=None, help="TikTok sessionid cookie")
@click.option("--region", default=None, help="Default region code (US, GB, etc.)")
@click.option("--niche", default=None, help="Default niche")
@handle_error
def config_set(youtube_key: Optional[str], tiktok_cookie: Optional[str], region: Optional[str], niche: Optional[str]) -> None:
    """Set configuration values (API keys, defaults)."""
    updated = []
    if youtube_key:
        cfg_mod.set_key("youtube_api_key", youtube_key)
        updated.append("youtube_api_key")
    if tiktok_cookie:
        cfg_mod.set_key("tiktok_session_cookie", tiktok_cookie)
        updated.append("tiktok_session_cookie")
    if region:
        cfg_mod.set_key("default_region", region.upper())
        updated.append("default_region")
    if niche:
        cfg_mod.set_key("default_niche", niche.lower())
        updated.append("default_niche")

    if not updated:
        click.echo("  No values provided. Use --help to see options.")
        return

    output(
        {"updated": updated, "config_path": cfg_mod.config_path()},
        f"Updated: {', '.join(updated)}"
    )


@config.command("show")
@handle_error
def config_show() -> None:
    """Show current configuration (secrets masked)."""
    cfg = cfg_mod.mask_secrets(cfg_mod.load())
    output(cfg, f"Config: {cfg_mod.config_path()}")


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session state — cache status and context."""
    pass


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show current session cache status."""
    sess = get_session()
    output(sess.status(), "Session Status")


@session_group.command("clear")
@handle_error
def session_clear() -> None:
    """Clear cached trend data."""
    sess = get_session()
    sess.clear_cache()
    output({"cleared": True}, "Session cache cleared")


@session_group.command("niche")
@click.argument("niche_name")
@handle_error
def session_set_niche(niche_name: str) -> None:
    """Set the active niche for this session."""
    sess = get_session()
    sess.niche = niche_name
    output({"niche": sess.niche}, f"Active niche set to: {sess.niche}")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.print_banner()

    sess = get_session()
    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends fetch youtube [--region US] [--category all]": "Fetch YouTube trending",
        "trends fetch tiktok [--count 20]": "Fetch TikTok trending hashtags + sounds",
        "trends fetch all": "Fetch from both platforms",
        "trends music [--platform tiktok]": "Get trending music",
        "account add --platform tiktok --handle myhandle --niche finance": "Register account",
        "account list": "List tracked accounts",
        "account optimize --platform tiktok --followers 5000 --avg-views 2000": "Optimize account",
        "account schedule --platforms tiktok,youtube --niche finance": "Posting schedule",
        "hashtags strategy --niche finance --platform tiktok": "Build hashtag strategy",
        "hashtags recommend --niche beauty": "Quick hashtag recommendations",
        "calendar generate --niche finance --weeks 2": "Content calendar with video ideas",
        "theme-page niches [--sort monetization_potential]": "List niches ranked by opportunity",
        "theme-page strategy --niche ai-tools": "Full niche strategy + 30-day plan",
        "theme-page roadmap": "Complete theme page creation roadmap",
        "theme-page conversion": "Conversion and monetization playbook",
        "config set --youtube-key KEY": "Set YouTube API key",
        "config show": "Show current config",
        "session status": "Show session cache status",
        "session niche finance": "Set active niche",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session, sess.niche)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue

        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_repl_commands)
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
