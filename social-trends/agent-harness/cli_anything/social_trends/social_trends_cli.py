#!/usr/bin/env python3
"""Social Trends CLI — Viral trend research, hashtag analysis, music discovery, and account optimization.

Pulls real-time trending data from YouTube (via YouTube Data API v3) and TikTok (public endpoints),
analyzes viral hashtags and music, and provides actionable account optimization and theme page strategies.

Usage:
    # Setup YouTube API key
    social-trends auth setup --youtube-api-key <YOUR_KEY>

    # Fetch YouTube trending videos (US, all categories)
    social-trends youtube trending

    # Fetch TikTok trending hashtags
    social-trends tiktok hashtags

    # Analyze trending sounds/music
    social-trends music guide

    # Get account optimization checklist
    social-trends optimize checklist --platform tiktok

    # Explore theme page strategies
    social-trends theme list
    social-trends theme guide
    social-trends theme research --niche finance

    # Interactive REPL
    social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.utils.social_backend import (
    load_config, save_config, CONFIG_FILE,
)

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    """Print output in JSON or human-readable format."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
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
            click.echo(f"{prefix}{click.style(str(k), bold=True)}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{click.style(str(k), bold=True)}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{click.style(str(k), bold=True)}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i + 1}]")
            _print_dict(item, indent + 1)
        else:
            click.echo(f"{prefix}• {item}")


def handle_error(func):
    """Decorator for consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(click.style(f"Error: {e}", fg="red"), err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI Group ──────────────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — Viral trends, hashtags, music & account optimization.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = use_json
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Auth Commands ───────────────────────────────────────────────────────
@cli.group()
def auth():
    """API key and credential management."""
    pass


@auth.command("setup")
@click.option("--youtube-api-key", default=None, help="YouTube Data API v3 key (from console.cloud.google.com)")
@click.option("--tiktok-client-key", default=None, help="TikTok for Developers client key")
@click.option("--tiktok-client-secret", default=None, help="TikTok for Developers client secret")
@handle_error
def auth_setup(youtube_api_key, tiktok_client_key, tiktok_client_secret):
    """Configure API credentials.

    \b
    To get a YouTube Data API v3 key:
      1. Go to https://console.cloud.google.com/
      2. Create a project, enable 'YouTube Data API v3'
      3. Go to Credentials -> Create API Key
      4. Restrict to YouTube Data API v3

    \b
    For TikTok API access (Research API):
      1. Go to https://developers.tiktok.com/
      2. Apply for Research API access
      3. Provide your client_key and client_secret here
    """
    config = load_config()
    if youtube_api_key:
        config["youtube_api_key"] = youtube_api_key
    if tiktok_client_key:
        config["tiktok_client_key"] = tiktok_client_key
    if tiktok_client_secret:
        config["tiktok_client_secret"] = tiktok_client_secret

    if not any([youtube_api_key, tiktok_client_key, tiktok_client_secret]):
        raise click.UsageError(
            "Provide at least one credential. "
            "Example: social-trends auth setup --youtube-api-key YOUR_KEY"
        )

    save_config(config)
    result = {
        "status": "configured",
        "youtube_api_key": "***set***" if config.get("youtube_api_key") else "not set",
        "tiktok_client_key": "***set***" if config.get("tiktok_client_key") else "not set",
        "config_file": str(CONFIG_FILE),
    }
    output(result, "Credentials saved.")


@auth.command("status")
@handle_error
def auth_status():
    """Check configured credentials."""
    config = load_config()
    result = {
        "youtube_api_key": "configured" if config.get("youtube_api_key") else "not set",
        "tiktok_client_key": "configured" if config.get("tiktok_client_key") else "not set",
        "tiktok_client_secret": "configured" if config.get("tiktok_client_secret") else "not set",
        "config_file": str(CONFIG_FILE),
        "hint": (
            "Run 'social-trends auth setup --youtube-api-key <KEY>' to enable YouTube API features. "
            "TikTok features work without API key using public data endpoints."
        ),
    }
    output(result)


# ── YouTube Commands ────────────────────────────────────────────────────
@cli.group()
def youtube():
    """YouTube trending content and analytics."""
    pass


@youtube.command("trending")
@click.option("--region", "-r", default="US", help="Region code (e.g. US, GB, JP, BR, IN)")
@click.option("--category", "-c", default="0", help="Category ID (0=All, 10=Music, 17=Sports, 20=Gaming, 24=Entertainment)")
@click.option("--limit", "-n", type=int, default=25, help="Number of videos (max 50)")
@handle_error
def youtube_trending(region, category, limit):
    """Fetch YouTube's Most Popular trending videos.

    \b
    Common category IDs:
      0  = All
      10 = Music
      17 = Sports
      20 = Gaming
      22 = People & Blogs
      23 = Comedy
      24 = Entertainment
      25 = News & Politics
      26 = Howto & Style
      28 = Science & Technology

    Requires YouTube API key: social-trends auth setup --youtube-api-key <KEY>
    """
    from cli_anything.social_trends.core.youtube import get_trending
    result = get_trending(region=region, category=category, limit=limit)
    output(result, f"YouTube Trending — Region: {region}, Category: {category}")


@youtube.command("search")
@click.argument("query")
@click.option("--order", "-o", type=click.Choice(["viewCount", "relevance", "date", "rating"]),
              default="viewCount", help="Sort order")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--limit", "-n", type=int, default=20, help="Number of results")
@click.option("--days", "-d", type=int, default=0, help="Filter to last N days (0=no filter)")
@handle_error
def youtube_search(query, order, region, limit, days):
    """Search YouTube for trending content around a keyword.

    Example: social-trends youtube search "morning routine" --order viewCount --days 7
    """
    from cli_anything.social_trends.core.youtube import search_trends
    result = search_trends(query=query, order=order, limit=limit, region=region, days=days)
    output(result, f"YouTube Search: '{query}'")


@youtube.command("categories")
@click.option("--region", "-r", default="US", help="Region code")
@handle_error
def youtube_categories(region):
    """List available YouTube video categories for a region."""
    from cli_anything.social_trends.core.youtube import list_categories
    result = list_categories(region=region)
    output(result, f"YouTube Categories — {region}")


@youtube.command("audit")
@click.argument("channel_id")
@handle_error
def youtube_audit(channel_id):
    """Audit a YouTube channel and get optimization recommendations.

    CHANNEL_ID: YouTube channel ID (starts with UC...) or username.

    Example: social-trends youtube audit UCnUYZLuoy1rq1aVMwx4aTzw
    """
    from cli_anything.social_trends.core.youtube import channel_audit
    result = channel_audit(channel_id)
    output(result, f"Channel Audit: {result.get('channel', {}).get('title', channel_id)}")


@youtube.command("hashtags")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--category", "-c", default="0", help="Category ID")
@click.option("--limit", "-n", type=int, default=50, help="Videos to analyze for hashtag extraction")
@handle_error
def youtube_hashtags(region, category, limit):
    """Extract and rank hashtags from trending YouTube videos."""
    from cli_anything.social_trends.core.youtube import extract_trending_hashtags
    result = extract_trending_hashtags(region=region, category=category, limit=limit)
    output(result, "YouTube Trending Hashtags")


# ── TikTok Commands ─────────────────────────────────────────────────────
@cli.group()
def tiktok():
    """TikTok trending analysis and account optimization."""
    pass


@tiktok.command("hashtags")
@click.option("--count", "-n", type=int, default=30, help="Number of hashtags to fetch")
@handle_error
def tiktok_hashtags(count):
    """Fetch trending TikTok hashtags from public data.

    Note: Uses TikTok's public discover endpoint.
    For Research API access, configure credentials: social-trends auth setup
    """
    from cli_anything.social_trends.core.tiktok import get_trending_hashtags
    result = get_trending_hashtags(count=count)
    output(result, "TikTok Trending Hashtags")


@tiktok.command("sounds")
@handle_error
def tiktok_sounds():
    """Guide to finding and using trending TikTok sounds and music."""
    from cli_anything.social_trends.core.tiktok import get_trending_sounds
    result = get_trending_sounds()
    output(result, "TikTok Trending Sounds Guide")


@tiktok.command("checklist")
@handle_error
def tiktok_checklist():
    """TikTok account optimization checklist."""
    from cli_anything.social_trends.core.tiktok import account_checklist
    result = account_checklist()
    output(result, "TikTok Account Optimization Checklist")


@tiktok.command("calendar")
@click.option("--niche", "-n", default="general",
              type=click.Choice(["general", "finance", "fitness", "motivation"]),
              help="Content niche")
@click.option("--posts-per-day", "-p", type=int, default=2, help="Posts per day (1-3)")
@handle_error
def tiktok_calendar(niche, posts_per_day):
    """Generate a 7-day TikTok content calendar."""
    from cli_anything.social_trends.core.tiktok import content_calendar
    posts_per_day = max(1, min(3, posts_per_day))
    result = content_calendar(niche=niche, posts_per_day=posts_per_day)
    output(result, f"7-Day TikTok Content Calendar — {niche.capitalize()}")


# ── Hashtag Commands ────────────────────────────────────────────────────
@cli.group()
def hashtags():
    """Hashtag research, scoring, and strategy."""
    pass


@hashtags.command("niche")
@click.argument("niche")
@handle_error
def hashtags_niche(niche):
    """Get a curated hashtag set for a content niche.

    \b
    Available niches: finance, fitness, motivation, luxury, tech, aesthetic, pets

    Example: social-trends hashtags niche finance
    """
    from cli_anything.social_trends.core.hashtags import get_niche_hashtags
    result = get_niche_hashtags(niche=niche)
    output(result, f"Hashtags for Niche: {niche.capitalize()}")


@hashtags.command("research")
@click.argument("tag")
@handle_error
def hashtags_research(tag):
    """Research a specific hashtag's trend strength and related tags.

    TAG: The hashtag to research (with or without #).

    Example: social-trends hashtags research fitness
    """
    from cli_anything.social_trends.core.hashtags import research_hashtag
    result = research_hashtag(tag=tag)
    output(result, f"Hashtag Research: #{tag.lstrip('#')}")


@hashtags.command("suggest")
@click.argument("niche")
@click.option("--platform", "-p", type=click.Choice(["tiktok", "youtube", "both"]),
              default="both", help="Target platform")
@handle_error
def hashtags_suggest(niche, platform):
    """Suggest an optimized hashtag combination for posting.

    Example: social-trends hashtags suggest finance --platform tiktok
    """
    from cli_anything.social_trends.core.hashtags import suggest_hashtag_combo
    result = suggest_hashtag_combo(niche=niche, platform=platform)
    output(result, f"Hashtag Combo: {niche.capitalize()} → {platform}")


@hashtags.command("competitor")
@click.argument("channel_id")
@handle_error
def hashtags_competitor(channel_id):
    """Analyze hashtags used by a YouTube competitor channel.

    CHANNEL_ID: YouTube channel ID (starts with UC...).
    Requires YouTube API key.
    """
    from cli_anything.social_trends.core.hashtags import analyze_competitor_hashtags
    result = analyze_competitor_hashtags(channel_id=channel_id)
    output(result, "Competitor Hashtag Analysis")


# ── Music Commands ──────────────────────────────────────────────────────
@cli.group()
def music():
    """Trending music and audio research for social media."""
    pass


@music.command("guide")
@handle_error
def music_guide():
    """Complete guide to finding and using trending music legally."""
    from cli_anything.social_trends.core.music import get_music_guide
    result = get_music_guide()
    output(result, "Trending Music Guide")


@music.command("niche")
@click.argument("niche")
@handle_error
def music_niche(niche):
    """Get music genre recommendations for a content niche.

    \b
    Available niches: finance, fitness, motivation, luxury, aesthetic, tech, pets, general

    Example: social-trends music niche fitness
    """
    from cli_anything.social_trends.core.music import get_music_by_niche
    result = get_music_by_niche(niche=niche)
    output(result, f"Music for Niche: {niche.capitalize()}")


@music.command("find")
@click.argument("niche")
@click.option("--limit", "-n", type=int, default=10, help="Number of results")
@handle_error
def music_find(niche, limit):
    """Search YouTube for free trending music in a niche.

    Requires YouTube API key. Results are copyright-free tracks.

    Example: social-trends music find motivation --limit 15
    """
    from cli_anything.social_trends.core.music import find_viral_music_youtube
    result = find_viral_music_youtube(niche=niche, limit=limit)
    output(result, f"Free Music Search: {niche.capitalize()}")


# ── Optimize Commands ───────────────────────────────────────────────────
@cli.group()
def optimize():
    """Account optimization for YouTube, TikTok, and Instagram."""
    pass


@optimize.command("schedule")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]),
              default="all", help="Platform to get schedule for")
@handle_error
def optimize_schedule(platform):
    """Get optimized posting schedule and content mix for a platform."""
    from cli_anything.social_trends.core.optimize import get_posting_schedule
    result = get_posting_schedule(platform=platform)
    output(result, f"Posting Schedule: {platform.capitalize()}")


@optimize.command("checklist")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "instagram", "all"]),
              default="all", help="Platform checklist")
@handle_error
def optimize_checklist(platform):
    """Get a complete account optimization checklist for a platform."""
    from cli_anything.social_trends.core.optimize import get_optimization_checklist
    result = get_optimization_checklist(platform=platform)
    output(result, f"Optimization Checklist: {platform.capitalize()}")


@optimize.command("mix")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok", help="Platform")
@handle_error
def optimize_mix(platform):
    """Get recommended content type mix and weekly distribution."""
    from cli_anything.social_trends.core.optimize import get_content_mix
    result = get_content_mix(platform=platform)
    output(result, f"Content Mix: {platform.capitalize()}")


@optimize.command("audit")
@click.argument("channel_id")
@handle_error
def optimize_audit(channel_id):
    """Full optimization audit for a YouTube channel.

    CHANNEL_ID: YouTube channel ID (starts with UC...).
    Requires YouTube API key.
    """
    from cli_anything.social_trends.core.optimize import audit_youtube_channel
    result = audit_youtube_channel(channel_id=channel_id)
    output(result, "YouTube Channel Audit")


@optimize.command("plan")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube"]),
              default="tiktok", help="Platform")
@click.option("--niche", "-n", default="general", help="Content niche")
@click.option("--followers", "-f", type=int, default=0, help="Current follower count")
@handle_error
def optimize_plan(platform, niche, followers):
    """Generate a 90-day growth plan for your account.

    Example: social-trends optimize plan --platform tiktok --niche finance --followers 500
    """
    from cli_anything.social_trends.core.optimize import generate_growth_plan
    result = generate_growth_plan(platform=platform, niche=niche, current_followers=followers)
    output(result, f"90-Day Growth Plan: {platform.capitalize()} — {niche.capitalize()}")


# ── Theme Page Commands ─────────────────────────────────────────────────
@cli.group()
def theme():
    """Theme page creation, niche research, and conversion strategy."""
    pass


@theme.command("list")
@click.option("--sort", "-s",
              type=click.Choice(["conversion_rate", "difficulty"]),
              default="conversion_rate", help="Sort order")
@handle_error
def theme_list(sort):
    """List all profitable theme page niches ranked by opportunity."""
    from cli_anything.social_trends.core.theme_pages import list_niches
    result = list_niches(sort_by=sort)
    output(result, "Theme Page Niches — Ranked by Opportunity")


@theme.command("guide")
@handle_error
def theme_guide():
    """Complete step-by-step guide to building a converting theme page."""
    from cli_anything.social_trends.core.theme_pages import get_guide
    result = get_guide()
    output(result, "Theme Page Complete Guide")


@theme.command("research")
@click.option("--niche", "-n", required=True,
              help="Niche to research (e.g. finance, fitness, luxury, motivation)")
@handle_error
def theme_research(niche):
    """Deep-dive research for a specific theme page niche.

    Includes affiliate programs, content templates, bio templates, and starter posts.

    Example: social-trends theme research --niche finance
    """
    from cli_anything.social_trends.core.theme_pages import niche_research
    result = niche_research(niche=niche)
    output(result, f"Theme Page Research: {niche.capitalize()}")


@theme.command("compare")
@click.argument("niche1")
@click.argument("niche2")
@handle_error
def theme_compare(niche1, niche2):
    """Compare two theme page niches side-by-side.

    Example: social-trends theme compare finance fitness
    """
    from cli_anything.social_trends.core.theme_pages import compare_niches
    result = compare_niches(niche1=niche1, niche2=niche2)
    output(result, f"Niche Comparison: {niche1.capitalize()} vs {niche2.capitalize()}")


# ── REPL ────────────────────────────────────────────────────────────────
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
        "auth":      "setup|status",
        "youtube":   "trending|search|categories|audit|hashtags",
        "tiktok":    "hashtags|sounds|checklist|calendar",
        "hashtags":  "niche|research|suggest|competitor",
        "music":     "guide|niche|find",
        "optimize":  "schedule|checklist|mix|audit|plan",
        "theme":     "list|guide|research|compare",
        "help":      "Show this help",
        "quit":      "Exit REPL",
    }

    config = load_config()
    if config.get("youtube_api_key"):
        skin.success("YouTube API configured. All features enabled.")
    else:
        skin.warning("YouTube API key not set. Run: auth setup --youtube-api-key <KEY>")
        skin.info("TikTok public features are available without an API key.")

    while True:
        try:
            line = skin.get_input(pt_session, context="trends")
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


# ── Entry Point ──────────────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
