#!/usr/bin/env python3
"""Social CLI — Trend scraping, account optimisation, and theme page conversion.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Audits and optimises social media accounts across platforms.
Provides theme page launch playbooks and monetisation strategies.

Usage:
    # Scrape YouTube trending (requires API key)
    cli-anything-social trends youtube --yt-key <KEY>

    # Scrape TikTok trending hashtags
    cli-anything-social trends tiktok-hashtags --tt-session <COOKIE>

    # Cross-platform trend report
    cli-anything-social trends all --yt-key <KEY> --tt-session <COOKIE>

    # Audit a TikTok account
    cli-anything-social account audit-tiktok <username>

    # Audit a YouTube channel
    cli-anything-social account audit-youtube <channel-id> --yt-key <KEY>

    # Optimise your bio
    cli-anything-social account bio --platform tiktok --niche fitness

    # Get hashtag strategy
    cli-anything-social account hashtags --platform tiktok --niche fitness

    # Get theme page playbook
    cli-anything-social theme playbook --niche finance --platform tiktok

    # Get monetisation strategies
    cli-anything-social theme monetise --niche fitness --followers 10000

    # Generate content calendar
    cli-anything-social schedule calendar --platform tiktok --niche fitness --weeks 4

    # Get content hooks
    cli-anything-social schedule hooks --niche finance

    # Interactive REPL
    cli-anything-social repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social.core import trends as trends_mod
from cli_anything.social.core import accounts as accounts_mod
from cli_anything.social.core import theme_pages as theme_mod
from cli_anything.social.core import scheduler as sched_mod

_json_output = False
_repl_mode = False


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
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({
                    "error": str(e),
                    "type": type(e).__name__,
                }))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Root ──────────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social CLI — Viral trends, account optimisation, and theme page growth.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Trends ────────────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape viral trends, hashtags, and music from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--yt-key", required=True, envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)")
@click.option("--region", default="US", show_default=True,
              help="Region code (e.g. US, GB, BR, IN)")
@click.option("--category", default="0", show_default=True,
              help="Video category ID (0=All, 10=Music, 17=Sports, 24=Entertainment)")
@click.option("--max", "max_results", type=int, default=20, show_default=True,
              help="Number of videos to fetch (max 50)")
@handle_error
def trends_youtube(yt_key, region, category, max_results):
    """Fetch trending YouTube videos, hashtags, and topics.

    Requires a free YouTube Data API v3 key from Google Cloud Console.
    Free tier allows 10,000 units/day (~100 requests).

    Example:
        cli-anything-social trends youtube --yt-key AIza... --region US
    """
    result = trends_mod.fetch_youtube_trending(
        api_key=yt_key,
        region=region,
        category=category,
        max_results=max_results,
    )
    output(result, f"YouTube trending ({region}, category {category}):")


@trends.command("youtube-search")
@click.argument("query")
@click.option("--yt-key", required=True, envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", type=int, default=20, show_default=True)
@click.option("--order", type=click.Choice(["viewCount", "relevance", "date", "rating"]),
              default="viewCount", show_default=True)
@handle_error
def trends_youtube_search(query, yt_key, region, max_results, order):
    """Search YouTube for content around a trending keyword.

    Example:
        cli-anything-social trends youtube-search "AI tutorial" --yt-key AIza...
    """
    result = trends_mod.fetch_youtube_search_trending(
        api_key=yt_key,
        query=query,
        region=region,
        max_results=max_results,
        order=order,
    )
    output(result, f"YouTube search: '{query}' ({region}):")


@trends.command("tiktok-hashtags")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION",
              help="TikTok sessionid cookie value (or set TIKTOK_SESSION env var)")
@click.option("--count", type=int, default=20, show_default=True,
              help="Number of hashtags to fetch")
@handle_error
def trends_tiktok_hashtags(tt_session, count):
    """Fetch trending TikTok hashtags from the Discover endpoint.

    Provide your TikTok sessionid cookie for authenticated access.
    To get your sessionid: TikTok web → DevTools → Application →
    Cookies → www.tiktok.com → find 'sessionid'.

    Example:
        cli-anything-social trends tiktok-hashtags --tt-session abc123...
    """
    result = trends_mod.fetch_tiktok_trending_hashtags(
        session_cookie=tt_session,
        count=count,
    )
    output(result, "TikTok trending hashtags:")


@trends.command("tiktok-music")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION",
              help="TikTok sessionid cookie value")
@click.option("--count", type=int, default=20, show_default=True)
@handle_error
def trends_tiktok_music(tt_session, count):
    """Fetch trending TikTok music and sounds.

    Example:
        cli-anything-social trends tiktok-music --tt-session abc123...
    """
    result = trends_mod.fetch_tiktok_trending_music(
        session_cookie=tt_session,
        count=count,
    )
    output(result, "TikTok trending music:")


@trends.command("tiktok-feed")
@click.option("--tt-session", required=True, envvar="TIKTOK_SESSION",
              help="TikTok sessionid cookie value")
@click.option("--count", type=int, default=20, show_default=True)
@click.option("--region", default="US", show_default=True)
@handle_error
def trends_tiktok_feed(tt_session, count, region):
    """Fetch TikTok For-You feed trending videos with hashtags and music.

    Requires a valid TikTok session cookie.

    Example:
        cli-anything-social trends tiktok-feed --tt-session abc123 --region US
    """
    result = trends_mod.fetch_tiktok_trending_videos(
        session_cookie=tt_session,
        count=count,
        region=region,
    )
    output(result, f"TikTok trending feed ({region}):")


@trends.command("all")
@click.option("--yt-key", default="", envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION",
              help="TikTok sessionid cookie value")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", type=int, default=20, show_default=True)
@handle_error
def trends_all(yt_key, tt_session, region, max_results):
    """Fetch cross-platform trends from YouTube AND TikTok.

    Returns combined hashtags, music trends, and actionable recommendations.
    Provide at least one platform credential.

    Example:
        cli-anything-social trends all --yt-key AIza... --tt-session abc123 --region US
    """
    if not yt_key and not tt_session:
        raise click.UsageError(
            "Provide at least one: --yt-key (YouTube) or --tt-session (TikTok)."
        )
    result = trends_mod.get_cross_platform_trends(
        youtube_api_key=yt_key,
        tiktok_session=tt_session,
        region=region,
        max_results=max_results,
    )
    output(result, "Cross-platform trend report:")


@trends.command("extract-hashtags")
@click.argument("text")
@handle_error
def trends_extract_hashtags(text):
    """Extract all #hashtags from a given text string.

    Example:
        cli-anything-social trends extract-hashtags "#fitness is great #gym #gains"
    """
    hashtags = trends_mod.extract_hashtags(text)
    output({"text": text, "hashtags": hashtags, "count": len(hashtags)})


# ── Account ───────────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Audit, optimise, and grow your social media accounts."""
    pass


@account.command("audit-youtube")
@click.argument("channel_id")
@click.option("--yt-key", required=True, envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key")
@handle_error
def account_audit_youtube(channel_id, yt_key):
    """Audit a YouTube channel — stats, bio score, and optimisation tips.

    CHANNEL_ID: YouTube channel ID (UCxxxxxx) or @handle.

    Example:
        cli-anything-social account audit-youtube @MrBeast --yt-key AIza...
        cli-anything-social account audit-youtube UC-lHJZR3Gqxm24_Vd_AJ5Yw --yt-key AIza...
    """
    result = accounts_mod.audit_youtube_channel(
        channel_id=channel_id,
        api_key=yt_key,
    )
    output(result, f"YouTube channel audit: {channel_id}")


@account.command("audit-tiktok")
@click.argument("username")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION",
              help="TikTok sessionid cookie (optional — improves accuracy)")
@handle_error
def account_audit_tiktok(username, tt_session):
    """Audit a TikTok account — followers, engagement, and optimisation tips.

    USERNAME: TikTok username (with or without @).

    Example:
        cli-anything-social account audit-tiktok @charlidamelio
        cli-anything-social account audit-tiktok khaby.lame
    """
    result = accounts_mod.audit_tiktok_account(
        username=username,
        session_cookie=tt_session,
    )
    output(result, f"TikTok account audit: {username}")


@account.command("bio")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Target platform")
@click.option("--niche", required=True, help="Content niche (e.g. fitness, finance, gaming)")
@click.option("--goal", default="followers",
              type=click.Choice(["followers", "sales", "traffic", "brand"]),
              show_default=True, help="Primary account goal")
@click.option("--current", default="", help="Your current bio text (for comparison)")
@click.option("--cta-url", default="", help="URL for call-to-action (e.g. Linktree)")
@handle_error
def account_bio(platform, niche, goal, current, cta_url):
    """Generate optimised bio templates for your platform and niche.

    Example:
        cli-anything-social account bio --platform tiktok --niche fitness --goal followers
        cli-anything-social account bio --platform youtube --niche finance --current "My channel"
    """
    result = accounts_mod.optimize_bio(
        platform=platform,
        niche=niche,
        goal=goal,
        current_bio=current,
        cta_url=cta_url,
    )
    output(result, f"Bio optimisation for {platform} ({niche}):")


@account.command("hashtags")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", required=True, help="Content niche")
@click.option("--size", default="small",
              type=click.Choice(["small", "medium", "large"]),
              show_default=True,
              help="Account size: small (<10K), medium (10K-100K), large (100K+)")
@handle_error
def account_hashtags(platform, niche, size):
    """Generate a tiered hashtag strategy for your account.

    Example:
        cli-anything-social account hashtags --platform tiktok --niche fitness --size small
    """
    result = accounts_mod.get_hashtag_strategy(
        platform=platform,
        niche=niche,
        account_size=size,
    )
    output(result, f"Hashtag strategy for {platform} ({niche}, {size}):")


@account.command("post-times")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--region", default="US", show_default=True,
              help="Audience region (US, UK, AU, global)")
@click.option("--niche", default="", help="Content niche (for niche-specific advice)")
@handle_error
def account_post_times(platform, region, niche):
    """Get optimal posting times and days for your platform.

    Example:
        cli-anything-social account post-times --platform tiktok --region US --niche fitness
    """
    result = accounts_mod.get_optimal_posting_times(
        platform=platform,
        region=region,
        niche=niche,
    )
    output(result, f"Optimal posting times for {platform} ({region}):")


# ── Theme pages ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page strategy — niche research, playbooks, and monetisation."""
    pass


@theme.command("niches")
@handle_error
def theme_niches():
    """List all available niches with competition and monetisation data.

    Example:
        cli-anything-social theme niches
    """
    niches = theme_mod.list_available_niches()
    output({"available_niches": niches, "total": len(niches)})


@theme.command("analyse")
@click.argument("niche")
@handle_error
def theme_analyse(niche):
    """Deep analysis of a content niche — opportunity score, viral formula, sources.

    NICHE: Content niche (fitness, finance, luxury, motivation, etc.)

    Example:
        cli-anything-social theme analyse fitness
        cli-anything-social theme analyse finance
    """
    result = theme_mod.get_niche_analysis(niche)
    output(result, f"Niche analysis: {niche}")


@theme.command("monetise")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--followers", type=int, default=0, show_default=True,
              help="Current follower count")
@handle_error
def theme_monetise(niche, platform, followers):
    """Get ranked monetisation strategies for your account.

    Shows viable strategies based on your current follower count,
    with earnings estimates and step-by-step setup instructions.

    Example:
        cli-anything-social theme monetise --niche fitness --platform tiktok --followers 5000
    """
    result = theme_mod.get_conversion_strategies(
        niche=niche,
        platform=platform,
        followers=followers,
    )
    output(result, f"Monetisation strategies for {niche} ({followers:,} followers):")


@theme.command("revenue")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--followers", type=int, required=True, help="Follower count")
@handle_error
def theme_revenue(niche, platform, followers):
    """Estimate monthly revenue across all monetisation channels.

    Provides low/mid/high estimates for: platform ads, brand deals,
    affiliate marketing, and digital products.

    Example:
        cli-anything-social theme revenue --niche fitness --followers 50000 --platform tiktok
    """
    result = theme_mod.estimate_revenue(
        niche=niche,
        followers=followers,
        platform=platform,
    )
    output(result, f"Revenue estimate: {niche} / {followers:,} followers / {platform}")


@theme.command("playbook")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--goal", type=int, default=10000, show_default=True,
              help="Follower goal")
@handle_error
def theme_playbook(niche, platform, goal):
    """Get a phased theme page launch and growth playbook.

    Includes: setup phase, launch sprint, growth engine, monetisation phase,
    daily tasks, milestones, and recommended tools.

    Example:
        cli-anything-social theme playbook --niche finance --platform tiktok --goal 50000
    """
    result = theme_mod.get_theme_page_playbook(
        niche=niche,
        platform=platform,
        followers_goal=goal,
    )
    output(result, f"Theme page playbook: {niche} on {platform} → {goal:,} followers")


@theme.command("valuation")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platform", default="instagram",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--followers", type=int, required=True, help="Follower count")
@click.option("--monthly-revenue", type=float, default=0.0, show_default=True,
              help="Verified average monthly revenue ($)")
@click.option("--engagement", type=float, default=0.0, show_default=True,
              help="Engagement rate as percentage (e.g. 4.5)")
@handle_error
def theme_valuation(niche, platform, followers, monthly_revenue, engagement):
    """Estimate the sale value of your theme page (account flip).

    Example:
        cli-anything-social theme valuation --niche fitness --followers 25000 --engagement 5.2
        cli-anything-social theme valuation --niche finance --followers 50000 --monthly-revenue 800
    """
    result = theme_mod.get_account_flip_valuation(
        niche=niche,
        platform=platform,
        followers=followers,
        avg_monthly_revenue=monthly_revenue,
        engagement_rate=engagement,
    )
    output(result, f"Account valuation: {niche} / {followers:,} followers")


# ── Schedule ──────────────────────────────────────────────────────────────────

@cli.group()
def schedule():
    """Content scheduling — calendars, frequency, hooks, and repurposing."""
    pass


@schedule.command("calendar")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", required=True, help="Content niche")
@click.option("--weeks", type=int, default=4, show_default=True,
              help="Number of weeks to plan (1-12)")
@click.option("--posts-per-day", type=int, default=0,
              help="Override default posting frequency")
@click.option("--start-date", default="",
              help="Start date (YYYY-MM-DD). Defaults to today.")
@handle_error
def schedule_calendar(platform, niche, weeks, posts_per_day, start_date):
    """Generate a content calendar with post ideas, hooks, and hashtag sets.

    Example:
        cli-anything-social schedule calendar --platform tiktok --niche fitness --weeks 4
        cli-anything-social schedule calendar --platform youtube --niche finance --weeks 2
    """
    result = sched_mod.create_content_calendar(
        platform=platform,
        niche=niche,
        weeks=weeks,
        posts_per_day=posts_per_day,
        start_date=start_date,
    )
    output(result, f"Content calendar: {platform} / {niche} / {weeks} weeks")


@schedule.command("frequency")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--stage", default="starter",
              type=click.Choice(["starter", "growing", "established"]),
              show_default=True,
              help="Account stage: starter (<1K), growing (1K-50K), established (50K+)")
@handle_error
def schedule_frequency(platform, stage):
    """Get posting frequency advice for your account stage.

    Example:
        cli-anything-social schedule frequency --platform tiktok --stage starter
    """
    result = sched_mod.get_posting_frequency(
        platform=platform,
        account_stage=stage,
    )
    output(result, f"Posting frequency: {platform} ({stage}):")


@schedule.command("hooks")
@click.option("--niche", required=True, help="Content niche")
@click.option("--type", "hook_type", default="all",
              type=click.Choice(["all", "curiosity", "value", "social_proof", "controversy"]),
              show_default=True, help="Hook type to generate")
@click.option("--count", type=int, default=10, show_default=True,
              help="Number of hooks to generate")
@handle_error
def schedule_hooks(niche, hook_type, count):
    """Generate content hook templates for your niche.

    Hooks are the first 0.5-1.5 seconds of your video — the most
    important element for watch time and algorithmic distribution.

    Example:
        cli-anything-social schedule hooks --niche fitness
        cli-anything-social schedule hooks --niche finance --type curiosity --count 5
    """
    result = sched_mod.get_content_hooks(
        niche=niche,
        hook_type=hook_type,
        count=count,
    )
    output(result, f"Content hooks: {niche} ({hook_type}):")


@schedule.command("repurpose")
@click.option("--from", "source_platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Platform you originally post on")
@click.option("--to", "target_platforms", multiple=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"]),
              help="Platforms to repurpose to (can specify multiple)")
@click.option("--niche", default="general", help="Content niche")
@handle_error
def schedule_repurpose(source_platform, target_platforms, niche):
    """Get a content repurposing plan across platforms.

    One video → 3-5 platforms = 3-5x reach with ~20% extra effort.

    Example:
        cli-anything-social schedule repurpose --from tiktok --to instagram --to youtube
        cli-anything-social schedule repurpose --from youtube --to tiktok --to instagram
    """
    targets = list(target_platforms) or [
        p for p in ["tiktok", "instagram", "youtube"] if p != source_platform
    ]
    result = sched_mod.get_content_repurposing_plan(
        source_platform=source_platform,
        target_platforms=targets,
        niche=niche,
    )
    output(result, f"Repurposing plan: {source_platform} → {', '.join(targets)}")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start an interactive REPL session."""
    from cli_anything.social.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("social", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends":   "youtube|youtube-search|tiktok-hashtags|tiktok-music|tiktok-feed|all",
        "account":  "audit-youtube|audit-tiktok|bio|hashtags|post-times",
        "theme":    "niches|analyse|monetise|revenue|playbook|valuation",
        "schedule": "calendar|frequency|hooks|repurpose",
        "help":     "Show this help",
        "quit":     "Exit REPL",
    }

    skin.info("Social CLI ready. Use 'trends', 'account', 'theme', or 'schedule' commands.")
    skin.hint("Tip: set YOUTUBE_API_KEY and TIKTOK_SESSION env vars to avoid passing them each time.")

    while True:
        try:
            line = skin.get_input(pt_session)
            if not line:
                continue
            if line.lower() in ("quit", "exit", "q"):
                skin.print_goodbye()
                break
            if line.lower() == "help":
                skin.help(_repl_commands)
                continue

            args = line.split()
            try:
                cli.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                skin.warning(f"Usage error: {e}")
            except Exception as e:
                skin.error(f"{e}")

        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

    _repl_mode = False


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
