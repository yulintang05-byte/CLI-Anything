#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, build theme pages.

Usage:
    # Fetch TikTok trending hashtags, sounds, videos
    cli-anything-social-trends trends tiktok --country US --period 7

    # Fetch YouTube trending videos
    cli-anything-social-trends trends youtube --region US

    # Full cross-platform trend report
    cli-anything-social-trends trends all --country US

    # Optimize a social media account
    cli-anything-social-trends account optimize --platform tiktok --niche fitness --followers 1200

    # Generate a theme page blueprint with content calendar
    cli-anything-social-trends theme blueprint --niche fitness_motivation --platform tiktok

    # List available theme niches
    cli-anything-social-trends theme niches

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import click
from pathlib import Path
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import account as account_mod
from cli_anything.social_trends.core import theme_page as theme_mod

_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_youtube_api_key: Optional[str] = None

CONFIG_DIR = Path.home() / ".cli-anything-social-trends"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_session() -> Session:
    global _session
    if _session is None:
        sf = str(CONFIG_DIR / "session.json")
        _session = Session(session_file=sf)
    return _session


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    CONFIG_FILE.chmod(0o600)


def get_youtube_key(cli_key: str | None = None) -> str | None:
    if cli_key:
        return cli_key
    env = os.environ.get("YOUTUBE_API_KEY")
    if env:
        return env
    return load_config().get("youtube_api_key")


def output(data, message: str = ""):
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


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items[:20]):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")
    if len(items) > 20:
        click.echo(f"{prefix}... and {len(items) - 20} more")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, RuntimeError, FileNotFoundError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI ──────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.option("--youtube-api-key", "yt_key", default=None, help="YouTube Data API v3 key")
@click.pass_context
def cli(ctx, use_json, yt_key):
    """Social Trends CLI — viral trends, account optimization, theme pages."""
    global _json_output, _youtube_api_key
    _json_output = use_json
    _youtube_api_key = get_youtube_key(yt_key)
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends ────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping — TikTok, YouTube, cross-platform reports."""
    pass


@trends.command("tiktok")
@click.option("--country", "-c", default="US", show_default=True, help="Country code (US, GB, CA, AU...)")
@click.option("--period", "-p", type=click.Choice(["1", "7", "30"]), default="7", show_default=True, help="Period in days")
@click.option("--hashtags", type=int, default=20, show_default=True, help="Number of hashtags to fetch")
@click.option("--sounds", type=int, default=20, show_default=True, help="Number of sounds to fetch")
@click.option("--videos", type=int, default=10, show_default=True, help="Number of videos to fetch")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@handle_error
def trends_tiktok(country, period, hashtags, sounds, videos, no_cache):
    """Fetch TikTok trending hashtags, sounds, and videos."""
    if not _json_output:
        click.echo(f"Fetching TikTok trends for {country.upper()} (last {period} days)...")
    report = trends_mod.fetch_tiktok_trends(
        country=country,
        period=int(period),
        hashtag_limit=hashtags,
        sound_limit=sounds,
        video_limit=videos,
        use_cache=not no_cache,
    )
    sess = get_session()
    sess.record("trends tiktok", {"country": country, "period": period}, {"fetched": True})

    if not _json_output:
        _print_tiktok_summary(report)
    else:
        output(report)


@trends.command("youtube")
@click.option("--region", "-r", default="US", show_default=True, help="Region code (US, GB, CA...)")
@click.option("--limit", "-n", type=int, default=20, show_default=True, help="Number of results")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@handle_error
def trends_youtube(region, limit, no_cache):
    """Fetch YouTube trending videos and music."""
    if not _json_output:
        mode = "API v3" if _youtube_api_key else "HTML scrape (set YOUTUBE_API_KEY for full data)"
        click.echo(f"Fetching YouTube trends for {region.upper()} [{mode}]...")
    report = trends_mod.fetch_youtube_trends(
        region=region,
        limit=limit,
        api_key=_youtube_api_key,
        use_cache=not no_cache,
    )
    sess = get_session()
    sess.record("trends youtube", {"region": region}, {"fetched": True})

    if not _json_output:
        _print_youtube_summary(report)
    else:
        output(report)


@trends.command("all")
@click.option("--country", "-c", default="US", show_default=True, help="Country/region code")
@click.option("--period", "-p", type=click.Choice(["1", "7", "30"]), default="7", show_default=True)
@click.option("--limit", "-n", type=int, default=15, show_default=True)
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@click.option("--output-file", "-o", default=None, help="Save report to JSON file")
@handle_error
def trends_all(country, period, limit, no_cache, output_file):
    """Cross-platform trend report — TikTok + YouTube with insights."""
    if not _json_output:
        click.echo(f"Fetching cross-platform trends for {country.upper()}...")
    report = trends_mod.cross_platform_report(
        country=country,
        period=int(period),
        youtube_api_key=_youtube_api_key,
        limit=limit,
        use_cache=not no_cache,
    )
    sess = get_session()
    sess.record("trends all", {"country": country}, {"fetched": True})

    if output_file:
        Path(output_file).write_text(json.dumps(report, indent=2, default=str))
        click.echo(f"Report saved to {output_file}")

    if _json_output:
        output(report)
    else:
        _print_cross_platform_summary(report)


@trends.command("cache")
@click.option("--list", "do_list", is_flag=True, help="List cached reports")
@click.option("--clear", is_flag=True, help="Clear all cached reports")
@click.option("--country", default=None, help="Clear cache for specific country")
def trends_cache(do_list, clear, country):
    """Manage trend cache."""
    if clear:
        result = trends_mod.clear_cache(country)
        output(result, f"Cleared {result['cleared']} cached report(s)")
    else:
        items = trends_mod.list_cached()
        if not items:
            output([], "No cached reports")
        else:
            output(items, f"Cached reports ({len(items)}):")


# ── Account ───────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization — platform-specific recommendations."""
    pass


@account.command("optimize")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube_shorts"], case_sensitive=False),
              help="Platform")
@click.option("--niche", "-n", required=True, help="Account niche (e.g., fitness, finance, cooking)")
@click.option("--followers", type=int, default=0, help="Current follower count")
@click.option("--avg-views", type=int, default=0, help="Average views per post")
@click.option("--posts-per-week", type=int, default=0, help="Current posting frequency")
@click.option("--goals", default="grow_followers", help="Comma-separated goals (grow_followers,monetize,drive_traffic)")
@click.option("--use-trends", is_flag=True, help="Fetch live trend data to enhance recommendations")
@click.option("--country", default="US", help="Country for trend data (if --use-trends)")
@handle_error
def account_optimize(platform, niche, followers, avg_views, posts_per_week, goals, use_trends, country):
    """Generate optimization recommendations for a social media account."""
    trending_hashtags = None
    trending_sounds = None

    if use_trends:
        click.echo(f"Fetching live trend data for {country.upper()}...")
        try:
            tiktok_data = trends_mod.fetch_tiktok_trends(country=country, period=7)
            trending_hashtags = [h["name"] for h in tiktok_data.get("hashtags", [])]
            trending_sounds = tiktok_data.get("sounds", [])
        except Exception as e:
            click.echo(f"Warning: Could not fetch trend data: {e}", err=True)

    goal_list = [g.strip() for g in goals.split(",")]
    report = account_mod.optimize_account(
        platform=platform,
        niche=niche,
        current_followers=followers,
        avg_views=avg_views,
        post_frequency_per_week=posts_per_week,
        trending_hashtags=trending_hashtags,
        trending_sounds=trending_sounds,
        account_goals=goal_list,
    )
    sess = get_session()
    sess.record("account optimize", {"platform": platform, "niche": niche}, {
        "critical_count": report["critical_count"],
        "high_count": report["high_count"],
    })

    if _json_output:
        output(report)
    else:
        _print_account_report(report)


@account.command("optimize-all")
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--use-trends", is_flag=True, help="Fetch live trend data")
@click.option("--country", default="US")
@handle_error
def account_optimize_all(config_file, use_trends, country):
    """Optimize multiple accounts from a JSON config file.

    Config file format: list of account objects with platform, niche, etc.
    Example: [{"name": "main", "platform": "tiktok", "niche": "fitness", "current_followers": 5000}]
    """
    with open(config_file) as f:
        accounts = json.load(f)
    if not isinstance(accounts, list):
        raise ValueError("Config file must contain a JSON array of account objects")

    trending_hashtags = None
    trending_sounds = None

    if use_trends:
        click.echo(f"Fetching live trend data for {country.upper()}...")
        try:
            tiktok_data = trends_mod.fetch_tiktok_trends(country=country, period=7)
            trending_hashtags = [h["name"] for h in tiktok_data.get("hashtags", [])]
            trending_sounds = tiktok_data.get("sounds", [])
        except Exception as e:
            click.echo(f"Warning: Could not fetch trend data: {e}", err=True)

    results = account_mod.optimize_all_accounts(
        accounts=accounts,
        trending_hashtags=trending_hashtags,
        trending_sounds=trending_sounds,
    )
    sess = get_session()
    sess.record("account optimize-all", {"config": config_file}, {"count": len(results)})
    output(results, f"Optimization reports for {len(results)} account(s):")


# ── Theme Page ────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page strategy — blueprints, niches, and content calendars."""
    pass


@theme.command("niches")
@click.option("--sort-by", default="avg_cpm_usd",
              type=click.Choice(["avg_cpm_usd", "competition", "growth_speed"]))
def theme_niches(sort_by):
    """List all available theme page niches ranked by CPM, competition, or growth speed."""
    niches = theme_mod.list_niches(sort_by=sort_by)
    if _json_output:
        output(niches)
        return

    click.echo(f"\n{'Niche':<25} {'CPM':>6} {'Competition':<12} {'Growth':<12} Monetization")
    click.echo("-" * 80)
    for n in niches:
        click.echo(
            f"{n['niche']:<25} ${n['avg_cpm_usd']:>5.2f} "
            f"{n['competition']:<12} {n['growth_speed']:<12} "
            f"{n['primary_monetization']}"
        )


@theme.command("blueprint")
@click.option("--niche", "-n", required=True, help="Niche (use 'theme niches' to list)")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube_shorts"]))
@click.option("--target-followers", type=int, default=100_000)
@click.option("--current-followers", type=int, default=0)
@click.option("--goal", "monetization_goal", default="affiliate",
              type=click.Choice(["affiliate", "course", "brand_deals", "product", "coaching"]))
@click.option("--use-trends", is_flag=True, help="Include live trend data in calendar")
@click.option("--country", default="US")
@click.option("--output-file", "-o", default=None, help="Save blueprint to JSON file")
@handle_error
def theme_blueprint(niche, platform, target_followers, current_followers, monetization_goal,
                    use_trends, country, output_file):
    """Generate a complete theme page growth and monetization blueprint with 30-day content calendar."""
    trending_hashtags = None
    trending_sounds = None

    if use_trends:
        click.echo(f"Fetching trend data for {country.upper()}...")
        try:
            tiktok_data = trends_mod.fetch_tiktok_trends(country=country, period=7)
            trending_hashtags = [h["name"] for h in tiktok_data.get("hashtags", [])]
            trending_sounds = tiktok_data.get("sounds", [])
        except Exception as e:
            click.echo(f"Warning: Could not fetch trend data: {e}", err=True)

    blueprint = theme_mod.theme_page_blueprint(
        niche=niche,
        platform=platform,
        target_followers=target_followers,
        current_followers=current_followers,
        monetization_goal=monetization_goal,
        trending_hashtags=trending_hashtags,
        trending_sounds=trending_sounds,
    )
    sess = get_session()
    sess.record("theme blueprint", {"niche": niche, "platform": platform}, {
        "target_followers": target_followers,
    })

    if output_file:
        Path(output_file).write_text(json.dumps(blueprint, indent=2, default=str))
        click.echo(f"Blueprint saved to {output_file}")

    if _json_output:
        output(blueprint)
    else:
        _print_blueprint_summary(blueprint)


@theme.command("formats")
def theme_formats():
    """List content formats ranked by virality potential."""
    formats = theme_mod.content_formats_guide()
    if _json_output:
        output(formats)
        return
    click.echo(f"\n{'Format':<25} {'Virality':<12} {'Effort':<10} {'Views Multiplier':>16}")
    click.echo("-" * 68)
    for f in formats:
        click.echo(
            f"{f['format']:<25} {f['virality']:<12} {f['effort']:<10} "
            f"{f['avg_views_multiplier']:>16.1f}x"
        )


# ── Config ────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("set")
@click.argument("key", type=click.Choice(["youtube_api_key"]))
@click.argument("value")
def config_set(key, value):
    """Set a config value (youtube_api_key)."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if key.endswith("key") and len(value) > 10 else value
    output({"key": key, "value": display}, f"Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show config value(s)."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        display = val[:10] + "..." if val and key.endswith("key") and len(val) > 10 else val
        output({"key": key, "value": display}, f"{key} = {display}")
    else:
        masked = {k: (v[:10] + "..." if k.endswith("key") and v and len(v) > 10 else v)
                  for k, v in cfg.items()}
        output(masked if masked else {}, "Config:" if masked else "No config set")


# ── Session ───────────────────────────────────────────────────────────

@cli.group()
def session():
    """Session — history, undo, redo."""
    pass


@session.command("status")
def session_status():
    sess = get_session()
    output(sess.status())


@session.command("history")
@click.option("--limit", "-n", type=int, default=20)
def session_history(limit):
    sess = get_session()
    entries = sess.history(limit=limit)
    output(entries, f"History ({len(entries)} entries):")


@session.command("undo")
def session_undo():
    sess = get_session()
    entry = sess.undo()
    if entry:
        output(entry.to_dict(), f"Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session.command("redo")
def session_redo():
    sess = get_session()
    entry = sess.redo()
    if entry:
        output(entry.to_dict(), f"Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


# ── REPL ──────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    try:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin("social-trends", version="1.0.0")
    except ImportError:
        skin = None

    if skin:
        skin.print_banner()
        pt_session = skin.create_prompt_session()
    else:
        click.echo("Social Trends CLI — interactive mode. Type 'help' or 'quit'.")
        pt_session = None

    commands = {
        "trends tiktok [--country US] [--period 7]": "TikTok trending hashtags, sounds, videos",
        "trends youtube [--region US]": "YouTube trending videos",
        "trends all [--country US]": "Cross-platform trend report",
        "trends cache --list": "List cached reports",
        "account optimize --platform tiktok --niche fitness": "Account optimization",
        "account optimize-all accounts.json": "Optimize multiple accounts from JSON file",
        "theme niches": "List theme page niches ranked by CPM",
        "theme blueprint --niche fitness_motivation --platform tiktok": "30-day content blueprint",
        "theme formats": "Content formats ranked by virality",
        "config set youtube_api_key <key>": "Set YouTube API key",
        "session history": "Show command history",
        "help": "Show this help",
        "quit / exit": "Exit",
    }

    while True:
        try:
            if skin and pt_session:
                line = skin.get_input(pt_session, context="social-trends")
            else:
                line = click.prompt("social-trends", prompt_suffix=" > ").strip()
        except (EOFError, KeyboardInterrupt):
            if skin:
                skin.print_goodbye()
            else:
                click.echo("\nGoodbye!")
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            if skin:
                skin.print_goodbye()
            else:
                click.echo("Goodbye!")
            break
        if line == "help":
            if skin:
                skin.help(commands)
            else:
                for cmd, desc in commands.items():
                    click.echo(f"  {cmd:<55} {desc}")
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"Usage error: {e}", err=True)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


# ── Pretty-print helpers ───────────────────────────────────────────────

def _print_tiktok_summary(report: dict):
    click.echo(f"\nTikTok Trends — {report.get('country')} | {report.get('period_days')}d window")
    click.echo(f"Fetched: {report.get('fetched_at', '')} {'(cached)' if report.get('from_cache') else ''}")

    hashtags = report.get("hashtags", [])
    if hashtags:
        click.echo(f"\nTop Hashtags ({len(hashtags)}):")
        for h in hashtags[:10]:
            click.echo(f"  #{h['name']:<30} {h['view_count']:>15,} views")

    sounds = report.get("sounds", [])
    if sounds:
        click.echo(f"\nTop Sounds ({len(sounds)}):")
        for s in sounds[:10]:
            click.echo(f"  {s['rank']:>2}. {s['title'][:35]:<35} by {s['artist'][:20]:<20} | {s['usage_count']:,} videos")

    videos = report.get("videos", [])
    if videos:
        click.echo(f"\nTop Videos ({len(videos)}):")
        for v in videos[:5]:
            click.echo(f"  {v['rank']:>2}. {v['description'][:55]}")
            click.echo(f"      @{v['author']} | {v['view_count']:,} views | tags: {', '.join(('#' + h) for h in v['hashtags'][:3])}")

    errors = report.get("errors", [])
    if errors:
        click.echo("\nErrors:")
        for e in errors:
            click.echo(f"  [{e['category']}] {e['error']}", err=True)


def _print_youtube_summary(report: dict):
    click.echo(f"\nYouTube Trends — {report.get('region')} | Mode: {report.get('api_mode', 'unknown')}")
    click.echo(f"Fetched: {report.get('fetched_at', '')} {'(cached)' if report.get('from_cache') else ''}")

    videos = report.get("trending_all", [])
    if videos:
        click.echo(f"\nTrending Videos ({len(videos)}):")
        for v in videos[:10]:
            views = f"{v['view_count']:,}" if isinstance(v.get("view_count"), int) else v.get("view_count_text", "?")
            click.echo(f"  {v.get('rank', '?'):>2}. {v['title'][:55]}")
            click.echo(f"      {v.get('channel', '')} | {views} views")

    music = report.get("trending_music", [])
    if music:
        click.echo(f"\nTrending Music ({len(music)}):")
        for v in music[:5]:
            click.echo(f"  {v.get('rank', '?'):>2}. {v['title'][:55]}")
            click.echo(f"      {v.get('channel', '')} | {v.get('view_count', 0):,} views")


def _print_cross_platform_summary(report: dict):
    click.echo(f"\nCross-Platform Trends — {report.get('country')} | {report.get('period_days')}d")

    insights = report.get("insights", {})

    hashtags = insights.get("top_tiktok_hashtags", [])
    if hashtags:
        click.echo(f"\nTop TikTok Hashtags: {', '.join('#' + h for h in hashtags[:8])}")

    sounds = insights.get("top_tiktok_sounds", [])
    if sounds:
        click.echo("\nTop TikTok Sounds:")
        for s in sounds[:5]:
            click.echo(f"  - '{s['title']}' by {s['artist']} ({s['usage_count']:,} videos)")

    yt_vids = insights.get("youtube_trending_videos", [])
    if yt_vids:
        click.echo("\nYouTube Trending Topics:")
        for t in yt_vids[:5]:
            click.echo(f"  - {t[:70]}")

    opps = insights.get("content_opportunities", [])
    if opps:
        click.echo("\nContent Opportunities:")
        for o in opps[:6]:
            click.echo(f"  [{o['priority'].upper()}] {o['action'][:80]}")
            click.echo(f"    Platforms: {', '.join(o['platforms'])}")


def _print_account_report(report: dict):
    click.echo(f"\nAccount Optimization — {report['platform']} | Niche: {report['niche']}")
    click.echo(f"Stage: {report['account_stage']} | Followers: {report['current_followers']:,}")
    click.echo(f"Engagement: {report['engagement_rate_pct']}% ({report['engagement_health']})")
    click.echo(f"\nCritical issues: {report['critical_count']} | High priority: {report['high_count']}")

    recs = report.get("recommendations", [])
    if recs:
        click.echo("\nRecommendations:")
        for r in recs:
            p = r["priority"].upper()
            click.echo(f"\n  [{p}] {r['category']}")
            click.echo(f"  Issue:  {r['issue']}")
            action_lines = r["action"]
            for i, line in enumerate(action_lines.split(". ")):
                if line:
                    prefix = "  Action: " if i == 0 else "         "
                    click.echo(f"{prefix}{line}{'.' if not line.endswith('.') else ''}")


def _print_blueprint_summary(bp: dict):
    click.echo(f"\nTheme Page Blueprint — {bp['niche']} | {bp['platform']}")
    click.echo(f"Description: {bp['niche_description']}")
    click.echo(f"Competition: {bp['competition_level']} | Growth speed: {bp['growth_speed']}")
    click.echo(f"Target: {bp['target_followers']:,} followers | Est. time: {bp['estimated_weeks_to_target']}")

    rev = bp.get("revenue_projection", {})
    if rev:
        click.echo(f"\nRevenue Projection at {bp['target_followers']:,} followers:")
        click.echo(f"  YouTube AdSense:   ${rev.get('youtube_adsense_monthly_usd', 0):>8,.0f}/mo")
        click.echo(f"  Affiliate:         ${rev.get('affiliate_monthly_usd', 0):>8,.0f}/mo")
        click.echo(f"  Brand Deals:       ${rev.get('brand_deal_monthly_usd', 0):>8,.0f}/mo")
        click.echo(f"  Total Estimate:    ${rev.get('total_monthly_usd', 0):>8,.0f}/mo")

    ht = bp.get("trending_hashtags_to_use", [])
    if ht:
        click.echo(f"\nTrending Hashtags: {', '.join('#' + h for h in ht[:8])}")

    sounds = bp.get("trending_sounds_to_use", [])
    if sounds:
        click.echo("\nTrending Sounds to Use:")
        for s in sounds[:3]:
            click.echo(f"  - '{s['title']}' by {s['artist']} ({s['usage']:,} videos)")

    calendar = bp.get("content_calendar_30_days", [])
    if calendar:
        click.echo(f"\n30-Day Content Calendar (first 7 days):")
        for day in calendar[:7]:
            click.echo(
                f"  Day {day['day']:>2} ({day['day_of_week'][:3]}): "
                f"[{day['format']}] {day['content_idea'][:55]}"
            )
            if day.get("trending_sound"):
                click.echo(f"          Sound: {day['trending_sound'][:50]}")
            click.echo(f"          CTA: {day['cta']}")

    roadmap = bp.get("monetization_roadmap", [])
    if roadmap:
        click.echo(f"\nMonetization Roadmap:")
        for stage in roadmap[:5]:
            status = "✓" if stage.get("reached") else "○"
            milestone = stage.get("milestone_followers")
            if isinstance(milestone, int):
                milestone_str = f"{milestone:>10,}"
            else:
                milestone_str = f"{str(milestone):>10}"
            click.echo(f"  {status} {milestone_str} followers: {', '.join(stage['unlocks'][:2])}")

    click.echo(f"\nConversion Strategy ({bp['platform']}):")
    for step in bp.get("conversion_strategy", {}).get("steps", [])[:3]:
        click.echo(f"  - {step}")

    click.echo("\nContent Source Guide:")
    for src in bp.get("content_source_guide", [])[:3]:
        click.echo(f"  [{src['source']}] {src['tips'][:80]}")


def main():
    cli()


if __name__ == "__main__":
    main()
