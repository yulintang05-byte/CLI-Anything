"""Main CLI entry point for social-trends — YouTube/TikTok trends, account optimization, theme pages."""

import json
import sys
import os
from typing import Optional

import click

from .core import session as _session
from .core import youtube_trends as _yt
from .core import tiktok_trends as _tt
from .core import account_optimizer as _opt
from .core import theme_pages as _theme
from .utils.repl_skin import print_banner, print_help, repl_prompt


def _out(data, json_mode: bool, save: Optional[str] = None) -> None:
    """Print data as JSON or pretty-formatted table."""
    if json_mode or save:
        text = json.dumps(data, indent=2, default=str)
        if save:
            with open(save, "w") as f:
                f.write(text)
            click.echo(f"Saved to {save}")
        if json_mode:
            click.echo(text)
        return
    # Pretty print for human readability
    if isinstance(data, list):
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                click.echo(f"\n{'─'*50}")
                click.echo(f"  #{i}")
                for k, v in item.items():
                    if isinstance(v, (dict, list)):
                        click.echo(f"  {k}: {json.dumps(v, default=str)}")
                    else:
                        click.echo(f"  {k}: {v}")
            else:
                click.echo(f"  {i}. {item}")
    elif isinstance(data, dict):
        click.echo(f"\n{'─'*50}")
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"  {k}:\n    {json.dumps(v, indent=2, default=str)}")
            else:
                click.echo(f"  {k}: {v}")
    else:
        click.echo(str(data))


# ---------------------------------------------------------------------------
# Top-level CLI group
# ---------------------------------------------------------------------------

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool) -> None:
    """Social Trends CLI — scrape YouTube & TikTok trends, optimize accounts, build theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_mode
    ctx.obj["session"] = _session.load_session()
    if ctx.invoked_subcommand is None:
        _run_repl(ctx.obj["session"])


def _run_repl(sess: dict) -> None:
    """Interactive REPL mode."""
    print_banner()
    while True:
        try:
            line = repl_prompt().strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            click.echo("Bye!")
            break
        if line in ("help", "?"):
            print_help()
            continue
        # Parse and dispatch
        parts = line.split()
        try:
            args = parts + (["--json"] if "--json" not in parts and False else [])
            cli.main(args=parts, standalone_mode=False, obj={"json": False, "session": sess})
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
        _session.save_session(sess)


# ---------------------------------------------------------------------------
# YouTube commands
# ---------------------------------------------------------------------------

@cli.group("yt")
@click.pass_context
def yt_group(ctx: click.Context) -> None:
    """YouTube trend commands."""


@yt_group.command("trends")
@click.option("--region", default="US", help="Region code (US, GB, CA, AU...)")
@click.option("--max", "max_results", default=25, help="Max results (1-50)")
@click.option("--category", default=None, help="Category ID (10=Music, 20=Gaming...)")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None, help="Save output to file")
@click.pass_context
def yt_trends(ctx: click.Context, region: str, max_results: int, category: Optional[str], json_mode: bool, save: Optional[str]) -> None:
    """Fetch trending YouTube videos for a region."""
    sess = ctx.obj["session"]
    api_key = _session.get_api_key(sess, "YOUTUBE_API_KEY")
    if not api_key:
        click.echo("YouTube API key not set. Run: social-trends config set YOUTUBE_API_KEY <key>", err=True)
        click.echo("Get a free key at: https://console.cloud.google.com (YouTube Data API v3)")
        return
    click.echo(f"Fetching trending YouTube videos [{region}]...", err=True)
    cache_key = f"yt_trends_{region}_{category or 'all'}"
    cached = _session.cache_get(cache_key)
    if cached:
        click.echo("(from cache)")
        videos = cached
    else:
        videos = _yt.fetch_trending_videos(api_key, region=region, category_id=category, max_results=max_results)
        _session.cache_set(cache_key, videos, ttl_seconds=1800)

    _session.log_history(sess, f"yt trends --region {region}", f"{len(videos)} videos fetched")
    _out(videos, json_mode or ctx.obj.get("json", False), save)


@yt_group.command("hashtags")
@click.option("--region", default="US")
@click.option("--top", default=25)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def yt_hashtags(ctx: click.Context, region: str, top: int, json_mode: bool, save: Optional[str]) -> None:
    """Extract trending hashtags from YouTube trending videos."""
    sess = ctx.obj["session"]
    api_key = _session.get_api_key(sess, "YOUTUBE_API_KEY")
    if not api_key:
        click.echo("YOUTUBE_API_KEY not set.", err=True)
        return
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Extracting trending YouTube hashtags [{region}]...", err=True)
    videos = _yt.fetch_trending_videos(api_key, region=region, max_results=50)
    hashtags = _yt.extract_trending_hashtags(videos, top_n=top)
    _out(hashtags, json_mode or ctx.obj.get("json", False), save)


@yt_group.command("music")
@click.option("--region", default="US")
@click.option("--max", "max_results", default=25)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def yt_music(ctx: click.Context, region: str, max_results: int, json_mode: bool, save: Optional[str]) -> None:
    """Fetch trending music from YouTube."""
    sess = ctx.obj["session"]
    api_key = _session.get_api_key(sess, "YOUTUBE_API_KEY")
    if not api_key:
        click.echo("YOUTUBE_API_KEY not set.", err=True)
        return
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Fetching trending YouTube music [{region}]...", err=True)
    music = _yt.fetch_trending_music(api_key, region=region, max_results=max_results)
    _out(music, json_mode or ctx.obj.get("json", False), save)


@yt_group.command("niche")
@click.argument("query")
@click.option("--max", "max_results", default=20)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def yt_niche(ctx: click.Context, query: str, max_results: int, json_mode: bool, save: Optional[str]) -> None:
    """Search trending YouTube videos in a specific niche."""
    sess = ctx.obj["session"]
    api_key = _session.get_api_key(sess, "YOUTUBE_API_KEY")
    if not api_key:
        click.echo("YOUTUBE_API_KEY not set.", err=True)
        return
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Searching trending YouTube videos for niche: '{query}'...", err=True)
    videos = _yt.search_trending_niche(api_key, niche=query, max_results=max_results)
    _out(videos, json_mode or ctx.obj.get("json", False), save)


@yt_group.command("analyze")
@click.option("--region", default="US")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def yt_analyze(ctx: click.Context, region: str, json_mode: bool, save: Optional[str]) -> None:
    """Full YouTube trend analysis — patterns, top tags, optimal content format."""
    sess = ctx.obj["session"]
    api_key = _session.get_api_key(sess, "YOUTUBE_API_KEY")
    if not api_key:
        click.echo("YOUTUBE_API_KEY not set.", err=True)
        return
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Running full YouTube trend analysis [{region}]...", err=True)
    videos = _yt.fetch_trending_videos(api_key, region=region, max_results=50)
    patterns = _yt.analyze_trending_patterns(videos)
    hashtags = _yt.extract_trending_hashtags(videos, top_n=20)
    result = {"patterns": patterns, "top_hashtags": hashtags, "video_count": len(videos), "region": region}
    _out(result, json_mode or ctx.obj.get("json", False), save)


# ---------------------------------------------------------------------------
# TikTok commands
# ---------------------------------------------------------------------------

@cli.group("tt")
@click.pass_context
def tt_group(ctx: click.Context) -> None:
    """TikTok trend commands."""


@tt_group.command("trends")
@click.option("--region", default="US")
@click.option("--max", "max_results", default=30)
@click.option("--hashtag", default=None, help="Filter by hashtag (requires Research API token)")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def tt_trends(ctx: click.Context, region: str, max_results: int, hashtag: Optional[str], json_mode: bool, save: Optional[str]) -> None:
    """Fetch trending TikTok videos (web scrape or Research API)."""
    sess = ctx.obj["session"]
    token = _session.get_api_key(sess, "TIKTOK_RESEARCH_TOKEN")
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Fetching trending TikTok videos [{region}]...", err=True)
    cache_key = f"tt_trends_{region}_{hashtag or 'all'}"
    cached = _session.cache_get(cache_key)
    if cached:
        click.echo("(from cache)")
        data = cached
    else:
        data = _tt.fetch_tiktok_trends(access_token=token, hashtag=hashtag, region=region, max_results=max_results)
        _session.cache_set(cache_key, data, ttl_seconds=900)
    _session.log_history(sess, f"tt trends --region {region}", f"{data.get('video_count', 0)} videos")
    _out(data, json_mode or ctx.obj.get("json", False), save)


@tt_group.command("hashtags")
@click.option("--region", default="US")
@click.option("--top", default=25)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def tt_hashtags(ctx: click.Context, region: str, top: int, json_mode: bool, save: Optional[str]) -> None:
    """Extract trending TikTok hashtags."""
    sess = ctx.obj["session"]
    token = _session.get_api_key(sess, "TIKTOK_RESEARCH_TOKEN")
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Fetching TikTok trending hashtags [{region}]...", err=True)
    data = _tt.fetch_tiktok_trends(access_token=token, region=region, max_results=50)
    hashtags = data.get("hashtags", [])[:top]
    _out(hashtags, json_mode or ctx.obj.get("json", False), save)


@tt_group.command("sounds")
@click.option("--region", default="US")
@click.option("--top", default=20)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def tt_sounds(ctx: click.Context, region: str, top: int, json_mode: bool, save: Optional[str]) -> None:
    """Extract trending TikTok sounds and music."""
    sess = ctx.obj["session"]
    token = _session.get_api_key(sess, "TIKTOK_RESEARCH_TOKEN")
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Fetching trending TikTok sounds [{region}]...", err=True)
    data = _tt.fetch_tiktok_trends(access_token=token, region=region, max_results=50)
    sounds = data.get("sounds", [])[:top]
    _out(sounds, json_mode or ctx.obj.get("json", False), save)


@tt_group.command("analyze")
@click.option("--region", default="US")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def tt_analyze(ctx: click.Context, region: str, json_mode: bool, save: Optional[str]) -> None:
    """Full TikTok trend analysis — patterns, best durations, top sounds."""
    sess = ctx.obj["session"]
    token = _session.get_api_key(sess, "TIKTOK_RESEARCH_TOKEN")
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Running full TikTok trend analysis [{region}]...", err=True)
    data = _tt.fetch_tiktok_trends(access_token=token, region=region, max_results=50)
    _out(data, json_mode or ctx.obj.get("json", False), save)


@tt_group.command("hashtag-info")
@click.argument("hashtag")
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def tt_hashtag_info(ctx: click.Context, hashtag: str, json_mode: bool) -> None:
    """Get stats for a specific TikTok hashtag."""
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Fetching info for {hashtag}...", err=True)
    info = _tt.fetch_hashtag_info(hashtag)
    _out(info, json_mode or ctx.obj.get("json", False))


# ---------------------------------------------------------------------------
# Account commands
# ---------------------------------------------------------------------------

@cli.group("account")
@click.pass_context
def account_group(ctx: click.Context) -> None:
    """Account optimization commands."""


@account_group.command("add")
@click.argument("platform")
@click.argument("username")
@click.option("--followers", default=0, type=int)
@click.option("--niche", default="general")
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--posts-per-week", default=0, type=int)
@click.option("--bio", default="")
@click.pass_context
def account_add(ctx: click.Context, platform: str, username: str, followers: int,
                niche: str, avg_views: int, avg_likes: int, avg_comments: int,
                posts_per_week: int, bio: str) -> None:
    """Register a social media account to track and optimize."""
    sess = ctx.obj["session"]
    data = {
        "platform": platform,
        "username": username,
        "follower_count": followers,
        "niche": niche,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "posting_frequency_per_week": posts_per_week,
        "bio": bio,
    }
    _session.add_account(sess, platform, username, data)
    _session.save_session(sess)
    click.echo(f"Account @{username} ({platform}) added. Run 'account audit {platform} {username}' to get recommendations.")


@account_group.command("list")
@click.option("--platform", default=None)
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def account_list(ctx: click.Context, platform: Optional[str], json_mode: bool) -> None:
    """List all registered accounts."""
    sess = ctx.obj["session"]
    accounts = _session.get_accounts(sess, platform)
    _out(accounts, json_mode or ctx.obj.get("json", False))


@account_group.command("audit")
@click.argument("platform")
@click.argument("username")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def account_audit(ctx: click.Context, platform: str, username: str, json_mode: bool, save: Optional[str]) -> None:
    """Audit an account and get optimization recommendations."""
    sess = ctx.obj["session"]
    accounts = _session.get_accounts(sess, platform)
    if username not in accounts:
        click.echo(f"Account @{username} not found. Add it first with: account add {platform} {username}", err=True)
        return
    data = accounts[username]
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Auditing @{username} on {platform}...", err=True)
    result = _opt.audit_account(data)
    _out(result, json_mode or ctx.obj.get("json", False), save)


@account_group.command("schedule")
@click.argument("platform")
@click.option("--tz", default="EST", help="Timezone (EST, PST, GMT, etc.)")
@click.option("--posts-per-week", default=7, type=int)
@click.option("--start", default=None, help="Start date YYYY-MM-DD")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def account_schedule(ctx: click.Context, platform: str, tz: str, posts_per_week: int,
                     start: Optional[str], json_mode: bool, save: Optional[str]) -> None:
    """Generate an optimized posting schedule."""
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Generating {platform} posting schedule...", err=True)
    schedule = _opt.generate_posting_schedule(platform, timezone=tz, posts_per_week=posts_per_week, start_date=start)
    _out(schedule, json_mode or ctx.obj.get("json", False), save)


@account_group.command("hashtags")
@click.argument("niche")
@click.argument("platform")
@click.option("--count", default=25)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def account_hashtags(ctx: click.Context, niche: str, platform: str, count: int,
                     json_mode: bool, save: Optional[str]) -> None:
    """Build a tiered hashtag strategy for a niche and platform."""
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Building hashtag strategy for #{niche} on {platform}...", err=True)
    strategy = _opt.build_hashtag_strategy(niche, platform=platform, count=count)
    _out(strategy, json_mode or ctx.obj.get("json", False), save)


@account_group.command("calendar")
@click.argument("niche")
@click.argument("platform")
@click.option("--weeks", default=4, type=int)
@click.option("--posts-per-week", default=7, type=int)
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def account_calendar(ctx: click.Context, niche: str, platform: str, weeks: int,
                     posts_per_week: int, json_mode: bool, save: Optional[str]) -> None:
    """Generate a content calendar."""
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Generating {weeks}-week content calendar for {niche} on {platform}...", err=True)
    calendar = _opt.generate_content_calendar(niche, platform=platform, weeks=weeks, posts_per_week=posts_per_week)
    _out(calendar, json_mode or ctx.obj.get("json", False), save)


@account_group.command("bio")
@click.argument("niche")
@click.argument("platform")
@click.option("--value-prop", default="", help="Your unique value proposition")
@click.option("--cta", default="", help="Call-to-action text")
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def account_bio(ctx: click.Context, niche: str, platform: str, value_prop: str,
                cta: str, json_mode: bool) -> None:
    """Generate optimized bio templates."""
    if not (json_mode or ctx.obj.get("json", False)):
        click.echo(f"Generating optimized {platform} bio for {niche} niche...", err=True)
    result = _opt.optimize_bio(niche, platform, value_prop=value_prop, cta=cta)
    _out(result, json_mode or ctx.obj.get("json", False))


# ---------------------------------------------------------------------------
# Theme page commands
# ---------------------------------------------------------------------------

@cli.group("theme")
@click.pass_context
def theme_group(ctx: click.Context) -> None:
    """Theme page strategy and monetization commands."""


@theme_group.command("niches")
@click.option("--json", "json_mode", is_flag=True)
@click.option("--save", default=None)
@click.pass_context
def theme_niches(ctx: click.Context, json_mode: bool, save: Optional[str]) -> None:
    """List all available niches with scores."""
    results = []
    for key in _theme.NICHES:
        results.append(_theme.score_niche(key))
    results.sort(key=lambda x: x.get("total_score", 0), reverse=True)
    _out(results, json_mode or ctx.obj.get("json", False), save)


@theme_group.command("niche")
@click.argument("niche_name")
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def theme_niche(ctx: click.Context, niche_name: str, json_mode: bool) -> None:
    """Get a full starter kit for a niche."""
    result = _theme.get_niche_starter_kit(niche_name.lower())
    _out(result, json_mode or ctx.obj.get("json", False))


@theme_group.command("compare")
@click.argument("niches", nargs=-1, required=True)
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def theme_compare(ctx: click.Context, niches: tuple, json_mode: bool) -> None:
    """Compare niches side-by-side."""
    results = _theme.compare_niches(list(niches))
    _out(results, json_mode or ctx.obj.get("json", False))


@theme_group.command("playbook")
@click.argument("phase", required=False, type=int)
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def theme_playbook(ctx: click.Context, phase: Optional[int], json_mode: bool) -> None:
    """View the theme page growth playbook."""
    result = _theme.get_playbook(phase)
    _out(result, json_mode or ctx.obj.get("json", False))


@theme_group.command("revenue")
@click.argument("platform")
@click.argument("followers", type=int)
@click.option("--niche", default="lifestyle")
@click.option("--avg-views", default=1000, type=int)
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def theme_revenue(ctx: click.Context, platform: str, followers: int, niche: str,
                  avg_views: int, json_mode: bool) -> None:
    """Estimate monthly revenue potential."""
    result = _theme.estimate_revenue(followers, platform, avg_views, niche)
    _out(result, json_mode or ctx.obj.get("json", False))


@theme_group.command("strategy")
@click.argument("strategy_type", default="follow_to_engagement")
@click.option("--json", "json_mode", is_flag=True)
@click.pass_context
def theme_strategy(ctx: click.Context, strategy_type: str, json_mode: bool) -> None:
    """Get a conversion strategy. Types: follow_to_engagement, engagement_to_leads, leads_to_customers, page_to_brand_deals."""
    result = _theme.CONVERSION_STRATEGIES.get(strategy_type)
    if not result:
        available = list(_theme.CONVERSION_STRATEGIES.keys())
        click.echo(f"Unknown strategy. Available: {', '.join(available)}", err=True)
        return
    _out(result, json_mode or ctx.obj.get("json", False))


# ---------------------------------------------------------------------------
# Config commands
# ---------------------------------------------------------------------------

@cli.group("config")
@click.pass_context
def config_group(ctx: click.Context) -> None:
    """Configuration and API key management."""


@config_group.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set an API key or configuration value."""
    sess = ctx.obj["session"]
    _session.set_api_key(sess, key, value)
    _session.save_session(sess)
    click.echo(f"Set {key} = {'*' * len(value)} (stored in ~/.cli-anything/social-trends/session.json)")


@config_group.command("show")
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration (API keys redacted)."""
    sess = ctx.obj["session"]
    display = dict(sess)
    if "api_keys" in display:
        display["api_keys"] = {k: "*" * min(len(str(v)), 8) + "..." for k, v in display["api_keys"].items()}
    click.echo(json.dumps(display, indent=2, default=str))


@cli.command("cache")
@click.option("--clear", is_flag=True, help="Clear all cached data")
@click.pass_context
def cache_cmd(ctx: click.Context, clear: bool) -> None:
    """Manage trend data cache."""
    if clear:
        count = _session.cache_clear()
        click.echo(f"Cleared {count} cache entries.")
    else:
        cache_dir = _session.CACHE_DIR
        files = list(cache_dir.glob("*.json"))
        click.echo(f"Cache directory: {cache_dir}")
        click.echo(f"Cached entries: {len(files)}")
        for f in files:
            click.echo(f"  {f.stem}")


@cli.command("history")
@click.pass_context
def history_cmd(ctx: click.Context) -> None:
    """Show command history."""
    sess = ctx.obj["session"]
    history = sess.get("history", [])
    if not history:
        click.echo("No history yet.")
        return
    for entry in history[-20:]:
        click.echo(f"  [{entry['timestamp'][:19]}] {entry['command']}")
        if entry.get("result"):
            click.echo(f"    → {entry['result']}")


def main() -> None:
    cli(obj={})


if __name__ == "__main__":
    main()
