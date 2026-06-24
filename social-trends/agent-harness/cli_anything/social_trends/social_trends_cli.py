#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, and build theme pages.

Wraps the YouTube Data API v3 and TikTok Research API to surface:
  - Trending videos, music, and hashtags from both platforms
  - Cross-platform viral potential scoring
  - Account optimization reports (posting schedule, hashtag strategy, content mix)
  - Theme page creation guides and monetization playbooks

Usage:
    # Configure APIs
    social-trends auth youtube --api-key <KEY>
    social-trends auth tiktok --client-key <K> --client-secret <S>

    # Pull trending data
    social-trends youtube trending --region US --category music
    social-trends tiktok trending --region US
    social-trends trends all --region US --niche fitness

    # Hashtags and music
    social-trends hashtags merge --region US --niche fitness
    social-trends music trending --region US

    # Optimize your accounts
    social-trends optimize report --platforms tiktok,youtube --niche fitness
    social-trends optimize schedule --platforms tiktok,instagram --tz-offset -5

    # Theme pages
    social-trends theme guide --niche luxury --platform tiktok
    social-trends theme niches
    social-trends theme monetize --strategy affiliate_marketing
    social-trends theme calendar --template 30_day_growth_sprint

    # Interactive REPL
    social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.utils import trends_backend as backend
from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

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
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI ─────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — viral trends, account optimization, theme page intelligence."""
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth ─────────────────────────────────────────────────────────────────────

@cli.group()
def auth():
    """Configure API credentials."""
    pass


@auth.command("youtube")
@click.option("--api-key", required=True, help="YouTube Data API v3 key")
@handle_error
def auth_youtube(api_key):
    """Save YouTube Data API v3 key.

    Get a key at: console.cloud.google.com → APIs & Services → Credentials
    Enable 'YouTube Data API v3' in the API Library first.
    """
    backend.save_youtube_key(api_key)
    output({"status": "saved", "platform": "youtube"}, "YouTube API key saved.")


@auth.command("tiktok")
@click.option("--client-key", required=True, help="TikTok Research API client key")
@click.option("--client-secret", required=True, help="TikTok Research API client secret")
@handle_error
def auth_tiktok(client_key, client_secret):
    """Save TikTok Research API credentials.

    Apply at: developers.tiktok.com → Research API
    Approval takes 1–5 business days. Without credentials, public scraping
    is used as fallback (less data richness).
    """
    backend.save_tiktok_creds(client_key, client_secret)
    output({"status": "saved", "platform": "tiktok"}, "TikTok credentials saved.")


@auth.command("status")
@handle_error
def auth_status():
    """Show which API credentials are configured."""
    result = {
        "youtube": {
            "configured": backend.check_youtube_configured(),
            "note": "YouTube Data API v3 key",
        },
        "tiktok": {
            "configured": backend.check_tiktok_configured(),
            "note": "TikTok Research API (optional — public scraping works without it)",
        },
    }
    output(result)


@auth.command("clear-cache")
@handle_error
def auth_clear_cache():
    """Clear the local trends cache (forces fresh API calls)."""
    result = backend.clear_cache()
    output(result, "Cache cleared. Next requests will hit the APIs.")


# ── YouTube commands ─────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trend intelligence."""
    pass


@youtube.command("trending")
@click.option("--region", "-r", default="US", help="ISO region code (e.g. US, GB, KR)")
@click.option("--category", "-c", default="all",
              type=click.Choice(["all", "music", "gaming", "entertainment", "howto",
                                 "comedy", "news", "sports", "travel", "education", "science"]),
              help="Video category filter")
@click.option("--limit", "-n", default=25, type=int, help="Number of results (max 50)")
@handle_error
def yt_trending(region, category, limit):
    """Fetch trending YouTube videos.

    Requires YouTube API key (run: social-trends auth youtube --api-key <KEY>).
    """
    result = yt_mod.get_trending_videos(region=region, category=category, max_results=limit)
    output(result, f"Trending YouTube videos [{region}] [{category}]:")


@youtube.command("music")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=25, type=int, help="Number of results")
@handle_error
def yt_music(region, limit):
    """Fetch trending music videos on YouTube."""
    result = yt_mod.get_trending_music(region=region, max_results=limit)
    output(result, f"Trending YouTube music [{region}]:")


@youtube.command("hashtags")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=30, type=int, help="Number of hashtags")
@handle_error
def yt_hashtags(region, limit):
    """Extract trending hashtags from YouTube trending videos."""
    result = yt_mod.extract_trending_hashtags(region=region, max_results=limit)
    output(result, f"Trending YouTube hashtags [{region}]:")


@youtube.command("search")
@click.argument("query")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--order", "-o",
              type=click.Choice(["relevance", "viewCount", "date", "rating"]),
              default="viewCount", help="Sort order")
@click.option("--limit", "-n", default=20, type=int, help="Number of results")
@click.option("--after", default=None, help="ISO 8601 date filter (e.g. 2025-01-01T00:00:00Z)")
@handle_error
def yt_search(query, region, order, limit, after):
    """Search YouTube for trend research.

    Examples:
        social-trends youtube search "#fitness"
        social-trends youtube search "viral dance challenge" --order viewCount
    """
    result = yt_mod.search_videos(
        query=query, region=region, order=order,
        max_results=limit, published_after=after,
    )
    output(result, f"YouTube search: '{query}' [{region}]:")


@youtube.command("channel")
@click.argument("channel_id")
@handle_error
def yt_channel(channel_id):
    """Get YouTube channel stats for account optimization.

    CHANNEL_ID: YouTube channel ID (starts with UC...).
    """
    result = yt_mod.get_channel_stats(channel_id)
    output(result)


@youtube.command("categories")
@click.option("--region", "-r", default="US", help="ISO region code")
@handle_error
def yt_categories(region):
    """List YouTube video categories for a region."""
    result = yt_mod.get_video_categories(region=region)
    output(result)


# ── TikTok commands ───────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trend intelligence."""
    pass


@tiktok.command("trending")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=25, type=int, help="Number of results")
@click.option("--start-date", default=None, help="YYYYMMDD start date (Research API only)")
@click.option("--end-date", default=None, help="YYYYMMDD end date (Research API only)")
@handle_error
def tt_trending(region, limit, start_date, end_date):
    """Fetch trending TikTok videos.

    Uses TikTok Research API if configured, otherwise falls back to
    public scraping (run: social-trends auth tiktok for richer data).
    """
    result = tt_mod.get_trending_videos(
        region=region, max_results=limit,
        start_date=start_date, end_date=end_date,
    )
    output(result, f"Trending TikTok videos [{region}]:")


@tiktok.command("hashtags")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=30, type=int, help="Number of hashtags")
@handle_error
def tt_hashtags(region, limit):
    """Extract trending hashtags from TikTok."""
    result = tt_mod.get_trending_hashtags(region=region, max_results=limit)
    output(result, f"Trending TikTok hashtags [{region}]:")


@tiktok.command("music")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=25, type=int, help="Number of results")
@handle_error
def tt_music(region, limit):
    """Fetch trending music on TikTok."""
    result = tt_mod.get_trending_music(region=region, max_results=limit)
    output(result, f"Trending TikTok music [{region}]:")


@tiktok.command("search-hashtag")
@click.argument("hashtag")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--limit", "-n", default=20, type=int, help="Number of results")
@click.option("--start-date", default=None, help="YYYYMMDD start date")
@click.option("--end-date", default=None, help="YYYYMMDD end date")
@handle_error
def tt_search_hashtag(hashtag, region, limit, start_date, end_date):
    """Search TikTok videos by hashtag (requires Research API).

    HASHTAG: Hashtag to search (with or without #).

    Example:
        social-trends tiktok search-hashtag fitness --region US
    """
    result = tt_mod.search_hashtag_videos(
        hashtag=hashtag, region=region, max_results=limit,
        start_date=start_date, end_date=end_date,
    )
    output(result, f"TikTok videos with {hashtag} [{region}]:")


# ── Cross-platform trends ─────────────────────────────────────────────────────

@cli.group()
def trends():
    """Cross-platform viral trend intelligence."""
    pass


@trends.command("all")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--niche", "-n", default="", help="Niche keywords to score relevance")
@click.option("--limit", default=20, type=int, help="Results per platform")
@handle_error
def trends_all(region, niche, limit):
    """Pull trending videos from both YouTube and TikTok and score viral potential.

    Cross-platform view of what's trending right now, with viral scores.
    """
    if not _json_output:
        click.echo(f"Fetching YouTube trending [{region}]...")
    yt_result = yt_mod.get_trending_videos(region=region, max_results=limit)
    yt_videos = yt_result.get("videos", [])

    if not _json_output:
        click.echo(f"Fetching TikTok trending [{region}]...")
    tt_result = tt_mod.get_trending_videos(region=region, max_results=limit)
    tt_videos = tt_result.get("videos", [])

    all_videos = yt_videos + tt_videos
    scored = opt_mod.score_viral_potential(all_videos)

    result = {
        "region": region,
        "niche": niche or "all",
        "total": len(scored),
        "top_viral": scored[:10],
        "youtube_count": len(yt_videos),
        "tiktok_count": len(tt_videos),
        "tiktok_source": tt_result.get("source", "unknown"),
    }
    output(result, f"Cross-platform viral trends [{region}]:")


@trends.command("score")
@click.argument("json_file", type=click.Path(exists=True))
@handle_error
def trends_score(json_file):
    """Score viral potential of a JSON list of videos.

    JSON_FILE: Path to a JSON file containing a list of normalized video dicts.
    """
    with open(json_file) as f:
        videos = json.load(f)
    if isinstance(videos, dict):
        videos = videos.get("videos", [])
    scored = opt_mod.score_viral_potential(videos)
    output({"total": len(scored), "videos": scored})


# ── Hashtag commands ─────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag research and strategy."""
    pass


@hashtags.command("merge")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--niche", "-n", default="", help="Niche keywords for relevance scoring")
@click.option("--limit", default=30, type=int, help="Total hashtags to return")
@handle_error
def hashtags_merge(region, niche, limit):
    """Merge and rank hashtags from YouTube and TikTok by trend + niche relevance.

    Produces a unified hashtag set ready to copy into your posts.
    """
    if not _json_output:
        click.echo("Fetching YouTube hashtags...")
    yt_tags = yt_mod.extract_trending_hashtags(region=region, max_results=50).get("hashtags", [])
    if not _json_output:
        click.echo("Fetching TikTok hashtags...")
    tt_tags = tt_mod.get_trending_hashtags(region=region, max_results=50).get("hashtags", [])

    all_tags = yt_tags + tt_tags
    niche_keywords = [w for w in niche.lower().split() if w] if niche else []

    result = opt_mod.analyze_hashtag_opportunity(all_tags, niche_keywords)
    result["suggested_caption_hashtags"] = " ".join(result.get("suggested_set", [])[:5])
    output(result, f"Merged hashtag analysis [{region}] niche={niche or 'all'}:")


@hashtags.command("analyze")
@click.argument("niche")
@click.option("--region", "-r", default="US", help="ISO region code")
@handle_error
def hashtags_analyze(niche, region):
    """Analyze the best hashtag strategy for a specific niche."""
    if not _json_output:
        click.echo(f"Pulling trends for niche: {niche}...")
    yt_tags = yt_mod.extract_trending_hashtags(region=region, max_results=50).get("hashtags", [])
    tt_tags = tt_mod.get_trending_hashtags(region=region, max_results=50).get("hashtags", [])
    all_tags = yt_tags + tt_tags

    niche_keywords = niche.lower().split()
    result = opt_mod.analyze_hashtag_opportunity(all_tags, niche_keywords)
    output(result, f"Hashtag strategy for '{niche}':")


# ── Music commands ────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending music intelligence."""
    pass


@music.command("trending")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["all", "tiktok", "youtube"]),
              help="Platform to pull from")
@click.option("--limit", "-n", default=20, type=int, help="Number of results")
@handle_error
def music_trending(region, platform, limit):
    """Fetch trending music from TikTok and/or YouTube.

    Use trending music in your content to boost algorithmic reach.
    """
    results = {}
    if platform in ("all", "tiktok"):
        results["tiktok"] = tt_mod.get_trending_music(region=region, max_results=limit)
    if platform in ("all", "youtube"):
        results["youtube"] = yt_mod.get_trending_music(region=region, max_results=limit)
    output(results, f"Trending music [{region}] [{platform}]:")


# ── Optimize commands ─────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization reports."""
    pass


@optimize.command("report")
@click.option("--platforms", "-p", default="tiktok,youtube",
              help="Comma-separated platforms (tiktok,youtube,instagram)")
@click.option("--niche", "-n", required=True, help="Your account niche (e.g. fitness)")
@click.option("--region", "-r", default="US", help="ISO region code")
@click.option("--tier", "-t",
              type=click.Choice(["micro", "mid", "macro", "mega"]),
              default="micro", help="Follower tier")
@click.option("--tz-offset", type=int, default=0,
              help="Hours from UTC for local time posting schedule")
@click.option("--pull-trends", is_flag=True,
              help="Pull live trend data to power hashtag recommendations")
@handle_error
def optimize_report(platforms, niche, region, tier, tz_offset, pull_trends):
    """Generate a full account optimization report.

    Covers posting schedule, content strategy, hashtag sets, and quick wins.
    Add --pull-trends to fetch live hashtag data from YouTube and TikTok.
    """
    platform_list = [p.strip() for p in platforms.split(",")]
    trending_hashtags = None

    if pull_trends:
        if not _json_output:
            click.echo("Pulling live trend data...")
        try:
            yt_tags = yt_mod.extract_trending_hashtags(region=region, max_results=50).get("hashtags", [])
            tt_tags = tt_mod.get_trending_hashtags(region=region, max_results=50).get("hashtags", [])
            trending_hashtags = yt_tags + tt_tags
        except Exception as e:
            click.echo(f"Warning: Could not pull trend data: {e}", err=True)

    result = opt_mod.get_optimization_report(
        platforms=platform_list,
        niche=niche,
        region=region,
        follower_tier=tier,
        timezone_offset=tz_offset,
        trending_hashtags=trending_hashtags,
        niche_keywords=niche.split(),
    )
    output(result, f"Account Optimization Report — {niche} on {platforms}:")


@optimize.command("schedule")
@click.option("--platforms", "-p", default="tiktok,youtube",
              help="Comma-separated platforms")
@click.option("--tz-offset", type=int, default=0, help="Hours from UTC")
@handle_error
def optimize_schedule(platforms, tz_offset):
    """Get the optimal posting schedule for your platforms."""
    platform_list = [p.strip() for p in platforms.split(",")]
    result = opt_mod.get_posting_schedule(platform_list, timezone_offset=tz_offset)
    output(result, "Optimal posting schedule:")


@optimize.command("strategy")
@click.option("--platforms", "-p", default="tiktok,youtube",
              help="Comma-separated platforms")
@click.option("--niche", "-n", required=True, help="Account niche")
@click.option("--tier", "-t",
              type=click.Choice(["micro", "mid", "macro", "mega"]),
              default="micro", help="Follower tier")
@handle_error
def optimize_strategy(platforms, niche, tier):
    """Get content format strategy for your platforms and niche."""
    platform_list = [p.strip() for p in platforms.split(",")]
    result = opt_mod.get_content_strategy(platform_list, niche=niche, follower_tier=tier)
    output(result, f"Content strategy for '{niche}' [{tier} tier]:")


# ── Theme page commands ───────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page creation, strategy, and monetization."""
    pass


@theme.command("guide")
@click.option("--niche", "-n", required=True, help="Theme page niche (e.g. luxury, fitness)")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              help="Primary platform")
@click.option("--monetize", "-m", default="affiliate_marketing",
              type=click.Choice(["shoutouts", "affiliate_marketing", "digital_products",
                                 "page_flipping", "brand_deals"]),
              help="Primary monetization strategy")
@handle_error
def theme_guide(niche, platform, monetize):
    """Generate a complete theme page creation guide.

    Includes niche evaluation, setup checklist, 7-day content calendar,
    30-day growth sprint, and full monetization playbook.
    """
    result = theme_mod.get_full_theme_page_guide(
        niche=niche, platform=platform, monetization_goal=monetize,
    )
    output(result, f"Theme Page Guide: {niche} on {platform}:")


@theme.command("niches")
@handle_error
def theme_niches():
    """List all evaluated niches with difficulty and monetization potential."""
    result = theme_mod.list_available_niches()
    output(result, "Available theme page niches:")


@theme.command("evaluate")
@click.argument("niche")
@handle_error
def theme_evaluate(niche):
    """Evaluate a specific niche for theme page potential.

    NICHE: Niche keyword to evaluate (e.g. 'fitness', 'finance', 'pets').
    """
    result = theme_mod.evaluate_niche(niche)
    output(result, f"Niche evaluation: {niche}")


@theme.command("monetize")
@click.option("--strategy", "-s", required=True,
              type=click.Choice(["shoutouts", "affiliate_marketing", "digital_products",
                                 "page_flipping", "brand_deals"]),
              help="Monetization strategy to get the playbook for")
@handle_error
def theme_monetize(strategy):
    """Get a detailed monetization playbook for a strategy."""
    result = theme_mod.get_monetization_playbook(strategy)
    output(result, f"Monetization playbook: {strategy}")


@theme.command("list-strategies")
@handle_error
def theme_list_strategies():
    """List all available monetization strategies."""
    result = theme_mod.list_monetization_strategies()
    output(result, "Available monetization strategies:")


@theme.command("calendar")
@click.option("--template", "-t",
              type=click.Choice(["7_day_theme_page", "30_day_growth_sprint"]),
              default="7_day_theme_page",
              help="Calendar template")
@handle_error
def theme_calendar(template):
    """Get a content calendar template."""
    result = theme_mod.get_content_calendar(template)
    output(result, f"Content calendar: {template}:")


@theme.command("setup")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--niche", "-n", required=True, help="Account niche")
@handle_error
def theme_setup(platform, niche):
    """Get a complete page setup checklist with monetization milestones."""
    result = theme_mod.get_page_setup_checklist(platform=platform, niche=niche)
    output(result, f"Setup checklist: {niche} on {platform}:")


# ── REPL ─────────────────────────────────────────────────────────────────────

@cli.command()
@handle_error
def repl():
    """Start interactive REPL session."""
    from cli_anything.social_trends.utils.repl_skin import ReplSkin

    global _repl_mode
    _repl_mode = True

    skin = ReplSkin("social-trends", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth":      "youtube|tiktok|status|clear-cache",
        "youtube":   "trending|music|hashtags|search|channel|categories",
        "tiktok":    "trending|hashtags|music|search-hashtag",
        "trends":    "all|score",
        "hashtags":  "merge|analyze",
        "music":     "trending",
        "optimize":  "report|schedule|strategy",
        "theme":     "guide|niches|evaluate|monetize|calendar|setup|list-strategies",
        "help":      "Show this help",
        "quit":      "Exit REPL",
    }

    # Show auth status
    try:
        yt_ok = backend.check_youtube_configured()
        tt_ok = backend.check_tiktok_configured()
        if yt_ok:
            skin.success("YouTube API: configured")
        else:
            skin.warning("YouTube API: not configured. Run: auth youtube --api-key <KEY>")
        if tt_ok:
            skin.success("TikTok API: configured (Research API)")
        else:
            skin.info("TikTok: using public scrape (optional: auth tiktok for richer data)")
    except Exception:
        pass

    while True:
        try:
            line = skin.get_input(pt_session, context="social-trends")
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


def main():
    cli()


if __name__ == "__main__":
    main()
