#!/usr/bin/env python3
"""Social Trends CLI — Scrape YouTube & TikTok trends, optimize accounts, build theme pages.

Usage:
    # Configure API credentials
    cli-anything-social-trends config set-key --youtube-key <KEY>

    # Fetch YouTube trending videos
    cli-anything-social-trends youtube trending

    # Fetch TikTok trending hashtags
    cli-anything-social-trends tiktok hashtags --niche fitness

    # Aggregate trends from both platforms
    cli-anything-social-trends trends aggregate --niche beauty

    # Score your profile
    cli-anything-social-trends account score --platform tiktok --username myhandle

    # Get optimal posting schedule
    cli-anything-social-trends account schedule --platform tiktok --tz-offset -5

    # Score a hashtag set
    cli-anything-social-trends hashtags score "#fyp,#fitness,#workout"

    # Get theme page roadmap
    cli-anything-social-trends theme-page roadmap --niche fitness

    # Interactive REPL
    cli-anything-social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import hashtags as ht_mod
from cli_anything.social_trends.core import account as acc_mod
from cli_anything.social_trends.core import theme_pages as tp_mod
from cli_anything.social_trends.utils import social_backend as backend

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    _print_dict(item)
                    click.echo("─" * 50)
                else:
                    click.echo(str(item))
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
                else:
                    click.echo(f"{prefix}  • {item}")
        else:
            click.echo(f"{prefix}{click.style(k, bold=True)}: {v}")


# ─────────────────────────────────────────────────────────────────────
# Root command group
# ─────────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.version_option("1.0.0", prog_name="cli-anything-social-trends")
def cli(as_json: bool):
    """Social Trends CLI — YouTube & TikTok trend scraping, account optimization, theme pages."""
    global _json_output
    _json_output = as_json


# ─────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Manage API credentials and preferences."""


@config.command("status")
def config_status():
    """Show current configuration status."""
    data = backend.config_status()
    output(data, "Configuration status:")


@config.command("set-key")
@click.option("--youtube-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-session", default=None, help="TikTok session ID (optional, for authenticated requests)")
@click.option("--region", default=None, help="Region code (e.g. US, GB, CA)")
@click.option("--tz-offset", type=int, default=None, help="Your UTC timezone offset (-12 to +14)")
def config_set_key(youtube_key, tiktok_session, region, tz_offset):
    """Store API keys and preferences."""
    if youtube_key:
        backend.save_credential("youtube_api_key", youtube_key)
        click.echo(click.style("✓ YouTube API key saved", fg="green"))
    if tiktok_session:
        backend.save_credential("tiktok_session_id", tiktok_session)
        click.echo(click.style("✓ TikTok session ID saved", fg="green"))
    if region:
        backend.save_preference("region", region.upper())
        click.echo(click.style(f"✓ Region set to {region.upper()}", fg="green"))
    if tz_offset is not None:
        backend.save_preference("timezone_offset", tz_offset)
        click.echo(click.style(f"✓ Timezone offset set to UTC{tz_offset:+d}", fg="green"))
    if not any([youtube_key, tiktok_session, region, tz_offset is not None]):
        click.echo("No values provided. Use --youtube-key, --tiktok-session, --region, or --tz-offset")


@config.command("setup-guide")
def config_setup_guide():
    """Print step-by-step setup instructions."""
    guide = {
        "step_1_youtube_api": {
            "description": "Get a free YouTube Data API v3 key",
            "steps": [
                "Go to https://console.cloud.google.com",
                "Create a project (or select existing)",
                "Enable 'YouTube Data API v3' in API Library",
                "Create credentials → API Key",
                "Run: cli-anything-social-trends config set-key --youtube-key YOUR_KEY",
            ],
            "quota": "10,000 units/day free (trending fetch = ~3 units)",
        },
        "step_2_tiktok_session": {
            "description": "Get TikTok session ID (optional — enables authenticated trend data)",
            "steps": [
                "Open TikTok.com in browser, log in",
                "Open DevTools (F12) → Application → Cookies → tiktok.com",
                "Find 'sessionid' cookie value",
                "Run: cli-anything-social-trends config set-key --tiktok-session YOUR_SESSION_ID",
            ],
            "note": "Without session ID, the tool uses curated seed hashtags as fallback",
        },
        "step_3_region": {
            "description": "Set your target region for trends",
            "example": "cli-anything-social-trends config set-key --region US --tz-offset -5",
        },
    }
    output(guide, "Setup Guide:")


# ─────────────────────────────────────────────────────────────────────
# YouTube
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trends: videos, hashtags, music."""


def _yt_client():
    key = backend.get_youtube_api_key()
    if not key:
        raise click.ClickException(
            "YouTube API key not configured. Run: cli-anything-social-trends config set-key --youtube-key KEY\n"
            "Or set env var: export YOUTUBE_API_KEY=your_key"
        )
    region = backend.get_region()
    return yt_mod.YouTubeTrendsClient(api_key=key, region_code=region)


@youtube.command("trending")
@click.option("--category", default="0", help="Category ID: 0=all, 10=music, 17=sports, 24=entertainment, 28=science")
@click.option("--count", default=25, type=int, help="Number of videos (max 50)")
def youtube_trending(category, count):
    """Fetch currently trending YouTube videos."""
    client = _yt_client()
    try:
        videos = client.trending_videos(category_id=category, max_results=count)
        output(videos, f"Top {len(videos)} trending YouTube videos:")
    except yt_mod.YouTubeTrendsError as e:
        raise click.ClickException(str(e))


@youtube.command("hashtags")
@click.option("--count", default=50, type=int, help="Number of videos to scan for tags")
def youtube_hashtags(count):
    """Extract trending hashtags from top YouTube videos."""
    client = _yt_client()
    try:
        tags = client.trending_hashtags(max_videos=count)
        output(tags, f"Top {len(tags)} trending YouTube hashtags:")
    except yt_mod.YouTubeTrendsError as e:
        raise click.ClickException(str(e))


@youtube.command("music")
@click.option("--count", default=25, type=int, help="Number of music videos")
def youtube_music(count):
    """Fetch trending music videos on YouTube."""
    client = _yt_client()
    try:
        music = client.trending_music(max_results=count)
        output(music, f"Top {len(music)} trending music videos:")
    except yt_mod.YouTubeTrendsError as e:
        raise click.ClickException(str(e))


@youtube.command("search")
@click.argument("query")
@click.option("--count", default=20, type=int)
def youtube_search(query, count):
    """Search YouTube for trending content around a topic."""
    client = _yt_client()
    try:
        results = client.search_trending_topic(query=query, max_results=count)
        output(results, f"YouTube search results for '{query}':")
    except yt_mod.YouTubeTrendsError as e:
        raise click.ClickException(str(e))


@youtube.command("categories")
def youtube_categories():
    """List YouTube video categories for your region."""
    client = _yt_client()
    try:
        cats = client.video_categories()
        output(cats, "YouTube video categories:")
    except yt_mod.YouTubeTrendsError as e:
        raise click.ClickException(str(e))


# ─────────────────────────────────────────────────────────────────────
# TikTok
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trends: hashtags, sounds, niche tags."""


def _tt_client():
    session = backend.get_tiktok_session()
    return tt_mod.TikTokTrendsClient(session_cookie=session)


@tiktok.command("hashtags")
@click.option("--niche", default=None, help="Niche filter (run 'tiktok niches' to see options)")
@click.option("--count", default=30, type=int, help="Number of hashtags to return")
def tiktok_hashtags(niche, count):
    """Fetch trending TikTok hashtags."""
    client = _tt_client()
    tags = client.trending_hashtags(niche=niche, count=count)
    output(tags, f"Trending TikTok hashtags{' for #' + niche if niche else ''}:")


@tiktok.command("sounds")
@click.option("--count", default=20, type=int)
def tiktok_sounds(count):
    """Fetch trending TikTok sounds/music."""
    client = _tt_client()
    sounds = client.trending_sounds(count=count)
    output(sounds, f"Trending TikTok sounds:")


@tiktok.command("niche-tags")
@click.argument("niche")
def tiktok_niche_tags(niche):
    """Get curated hashtags for a specific niche."""
    client = _tt_client()
    tags = client.niche_hashtags(niche=niche)
    output(tags, f"Hashtags for niche '{niche}':")


@tiktok.command("niches")
def tiktok_niches():
    """List available niches for curated hashtag sets."""
    client = _tt_client()
    niches = client.available_niches()
    output(niches, "Available niches:")


# ─────────────────────────────────────────────────────────────────────
# Trends (cross-platform aggregation)
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Cross-platform trend aggregation and analysis."""


@trends.command("aggregate")
@click.option("--niche", default=None, help="Niche to focus on")
@click.option("--platform", type=click.Choice(["all", "youtube", "tiktok"]), default="all")
def trends_aggregate(niche, platform):
    """Aggregate trends from YouTube and TikTok into a unified report."""
    result: dict = {"niche": niche or "general", "timestamp": _now_iso()}
    tt_client = _tt_client()

    if platform in ("all", "tiktok"):
        tt_tags = tt_client.trending_hashtags(niche=niche, count=20)
        result["tiktok_hashtags"] = tt_tags[:10]
        tt_sounds = tt_client.trending_sounds(count=10)
        result["tiktok_sounds"] = tt_sounds[:5]

    if platform in ("all", "youtube"):
        yt_key = backend.get_youtube_api_key()
        if yt_key:
            yt_client = yt_mod.YouTubeTrendsClient(api_key=yt_key, region_code=backend.get_region())
            try:
                yt_tags = yt_client.trending_hashtags(max_videos=30)
                result["youtube_hashtags"] = yt_tags[:10]
                yt_music = yt_client.trending_music(max_results=5)
                result["youtube_music"] = yt_music
            except yt_mod.YouTubeTrendsError as e:
                result["youtube_error"] = str(e)
        else:
            result["youtube_note"] = "YouTube API key not configured — set with: config set-key --youtube-key KEY"

    # Cross-platform common tags
    tt_names = {t["hashtag"].lstrip("#").lower() for t in result.get("tiktok_hashtags", [])}
    yt_names = {t["hashtag"].lstrip("#").lower() for t in result.get("youtube_hashtags", [])}
    common = tt_names & yt_names
    result["cross_platform_tags"] = [f"#{t}" for t in sorted(common)]

    # Build optimal content strategy
    all_tags = list(tt_names | yt_names)
    viral_seeds = ["fyp", "foryou", "viral", "trending"]
    broad = [f"#{t}" for t in all_tags if t in viral_seeds]
    niche_specific = [f"#{t}" for t in all_tags if t not in viral_seeds]
    result["recommended_caption_hashtags"] = broad[:3] + niche_specific[:7]

    output(result, "Cross-platform trend report:")


@trends.command("content-ideas")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--count", default=10, type=int)
def trends_content_ideas(niche, count):
    """Generate content ideas based on current trends for your niche."""
    tt_client = _tt_client()
    tags = tt_client.niche_hashtags(niche=niche)
    tag_names = [t["hashtag"].lstrip("#") for t in tags]

    ideas = _generate_content_ideas(niche, tag_names, count)
    output(ideas, f"Content ideas for niche '{niche}':")


def _generate_content_ideas(niche: str, tags: list[str], count: int) -> list[dict]:
    templates = [
        {"format": "Before/After", "hook": f"I transformed my {niche} results in 30 days", "cta": "Follow for more transformations"},
        {"format": "Day in My Life", "hook": f"Day in the life of a {niche} creator", "cta": "Drop a '🔥' if you want part 2"},
        {"format": "Tutorial", "hook": f"3 {niche} tips nobody talks about (they changed everything)", "cta": "Save this for later"},
        {"format": "Reaction/Commentary", "hook": f"Responding to the most controversial {niche} takes", "cta": "Comment your opinion below"},
        {"format": "Myth vs Fact", "hook": f"Stop believing these {niche} myths — here's the truth", "cta": "Share with someone who needs this"},
        {"format": "Product Review", "hook": f"I tried 5 {niche} products so you don't have to", "cta": "Link in bio for the winner"},
        {"format": "Challenge", "hook": f"I tried the viral {niche} challenge for 7 days — here's what happened", "cta": "Comment if you'd try this"},
        {"format": "Storytime", "hook": f"The {niche} mistake that cost me 3 months", "cta": "Follow so this doesn't happen to you"},
        {"format": "List/Countdown", "hook": f"Top 5 {niche} accounts you NEED to follow right now", "cta": "Drop your fav in comments"},
        {"format": "POV/Skit", "hook": f"POV: You finally nail your {niche} goal", "cta": "Tag someone who needs to see this"},
    ]
    for i, idea in enumerate(templates[:count]):
        idea["suggested_hashtags"] = tags[:5]
        idea["content_index"] = i + 1
    return templates[:count]


# ─────────────────────────────────────────────────────────────────────
# Hashtags
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag scoring, optimization, and set building."""


@hashtags.command("score")
@click.argument("tags", metavar="HASHTAGS")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
def hashtags_score(tags, platform):
    """Score a comma-separated set of hashtags.

    Example: cli-anything-social-trends hashtags score "#fyp,#fitness,#workout" --platform tiktok
    """
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    result = ht_mod.score_hashtag_set(tag_list, platform=platform)
    output(result, f"Hashtag score for {platform}:")


@hashtags.command("build")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
@click.option("--count", default=10, type=int, help="Number of hashtags to include")
def hashtags_build(niche, platform, count):
    """Build an optimal hashtag set for a niche and platform."""
    tt_client = _tt_client()
    niche_tags = [t["hashtag"] for t in tt_client.niche_hashtags(niche)]
    viral_tags = ["#fyp", "#foryou", "#foryoupage", "#viral", "#trending"]
    optimal = ht_mod.build_optimal_set(niche_tags, viral_tags, platform=platform, count=count)
    score = ht_mod.score_hashtag_set(optimal, platform=platform)
    output({
        "niche": niche,
        "platform": platform,
        "hashtags": optimal,
        "copy_paste": " ".join(optimal),
        "score": score,
    }, f"Optimal {platform} hashtag set for '{niche}':")


@hashtags.command("suggest")
@click.argument("caption")
@click.option("--niche", default=None)
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
def hashtags_suggest(caption, niche, platform):
    """Suggest hashtags based on your caption text."""
    tt_client = _tt_client()
    niche_tags = [t["hashtag"] for t in tt_client.niche_hashtags(niche or "general")]
    viral_tags = ["#fyp", "#foryou", "#viral", "#trending", "#foryoupage"]
    all_tags = viral_tags + niche_tags
    suggested = ht_mod.suggest_caption_hashtags(caption, all_tags, platform=platform)
    output({
        "caption_preview": caption[:100],
        "suggested_hashtags": suggested,
        "copy_paste": " ".join(suggested),
    }, "Suggested hashtags for your caption:")


# ─────────────────────────────────────────────────────────────────────
# Account
# ─────────────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account profile optimization and posting schedules."""


@account.command("score")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), required=True)
@click.option("--username", required=True)
@click.option("--display-name", default="", help="Your display/full name")
@click.option("--bio", default="", help="Your current bio text")
@click.option("--has-photo/--no-photo", default=True, help="Profile photo uploaded?")
@click.option("--has-link/--no-link", default=False, help="Link in bio set?")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--posts", default=0, type=int)
@click.option("--niche", default=None, help="Your content niche")
def account_score(platform, username, display_name, bio, has_photo, has_link,
                  followers, following, posts, niche):
    """Score your social media profile and get actionable recommendations."""
    result = acc_mod.score_profile(
        platform=platform,
        username=username,
        display_name=display_name,
        bio=bio,
        has_profile_photo=has_photo,
        has_link=has_link,
        follower_count=followers,
        following_count=following,
        post_count=posts,
        niche=niche,
    )
    output(result, f"{platform.title()} profile score for @{username}:")


@account.command("schedule")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), required=True)
@click.option("--tz-offset", type=int, default=0, help="Your UTC timezone offset (e.g. -5 for EST)")
def account_schedule(platform, tz_offset):
    """Get optimal posting schedule for a platform."""
    result = acc_mod.posting_schedule(platform=platform, timezone_offset=tz_offset)
    output(result, f"Optimal {platform.title()} posting schedule:")


@account.command("optimize-all")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), required=True)
@click.option("--username", required=True)
@click.option("--niche", default=None)
@click.option("--tz-offset", type=int, default=0)
def account_optimize_all(platform, username, niche, tz_offset):
    """Full account optimization report: profile score + schedule + hashtags + content ideas."""
    if not _json_output:
        click.echo(click.style(f"\nFull Optimization Report for @{username} on {platform.title()}\n", bold=True))

    # Profile tips (no bio info needed — generic)
    profile = acc_mod.score_profile(
        platform=platform,
        username=username,
        display_name="",
        bio="",
        has_profile_photo=False,
        has_link=False,
        niche=niche,
    )

    schedule = acc_mod.posting_schedule(platform=platform, timezone_offset=tz_offset)

    tt_client = _tt_client()
    niche_key = niche or "general"
    tags = [t["hashtag"] for t in tt_client.niche_hashtags(niche_key)]
    optimal_tags = ht_mod.build_optimal_set(tags, ["#fyp", "#foryou", "#viral", "#trending"], platform=platform)

    ideas = _generate_content_ideas(niche_key, tags, count=5)

    result = {
        "account": {"platform": platform, "username": username, "niche": niche},
        "profile_quick_wins": profile["quick_wins"],
        "posting_schedule": schedule,
        "recommended_hashtags": optimal_tags,
        "hashtag_copy_paste": " ".join(optimal_tags),
        "content_ideas": ideas,
    }
    output(result, "")


# ─────────────────────────────────────────────────────────────────────
# Theme Pages
# ─────────────────────────────────────────────────────────────────────

@cli.group(name="theme-page")
def theme_page():
    """Theme page creation, niche selection, monetization, and conversion."""


@theme_page.command("niches")
def theme_page_niches():
    """List all available theme page niches with quick stats."""
    data = tp_mod.niche_overview()
    output(data, "Available theme page niches:")


@theme_page.command("niche-detail")
@click.argument("niche")
def theme_page_niche_detail(niche):
    """Get detailed info on a specific niche."""
    data = tp_mod.niche_overview(niche=niche)
    output(data, f"Niche detail: {niche}")


@theme_page.command("roadmap")
@click.option("--niche", required=True, help="Your chosen niche (run 'theme-page niches' to see options)")
@click.option("--followers", default=0, type=int, help="Current follower count")
def theme_page_roadmap(niche, followers):
    """Get a milestone-based growth roadmap for your theme page."""
    data = tp_mod.theme_page_roadmap(niche=niche, current_followers=followers)
    output(data, f"Theme page roadmap for '{niche}':")


@theme_page.command("monetization")
@click.option("--method", default=None, help="Specific method (brand_deals, digital_products, affiliate, courses, merch)")
def theme_page_monetization(method):
    """Explore monetization strategies for theme pages."""
    data = tp_mod.monetization_guide(method=method)
    output(data, "Monetization strategies:")


@theme_page.command("conversion-tips")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), required=True)
def theme_page_conversion_tips(platform):
    """Get conversion optimization tactics for turning followers into buyers."""
    tips = tp_mod.conversion_optimization_tips(platform=platform)
    output(tips, f"{platform.title()} conversion optimization tips:")


@theme_page.command("full-guide")
@click.option("--niche", required=True)
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
@click.option("--followers", default=0, type=int)
def theme_page_full_guide(niche, platform, followers):
    """Complete theme page guide: roadmap + monetization + conversion for your niche."""
    roadmap = tp_mod.theme_page_roadmap(niche=niche, current_followers=followers)
    niche_data = tp_mod.niche_overview(niche=niche)
    monetization = tp_mod.monetization_guide()
    conversion = tp_mod.conversion_optimization_tips(platform=platform)

    guide = {
        "niche": niche,
        "platform": platform,
        "current_followers": followers,
        "current_phase": roadmap["current_milestone"],
        "immediate_actions": roadmap["all_milestones"][roadmap["current_phase"]]["actions"][:3],
        "top_hashtags": roadmap.get("top_hashtags", []),
        "content_sources": roadmap.get("content_sources", []),
        "monetization_options": [{"method": m["method"], "when": m["when"]} for m in monetization],
        "conversion_tips": conversion[:3],
        "difficulty": niche_data.get("difficulty", "medium") if isinstance(niche_data, dict) else "medium",
        "notes": niche_data.get("notes", "") if isinstance(niche_data, dict) else "",
    }
    output(guide, f"Complete theme page guide for '{niche}' on {platform.title()}:")


# ─────────────────────────────────────────────────────────────────────
# REPL
# ─────────────────────────────────────────────────────────────────────

@cli.command()
def repl():
    """Launch interactive Social Trends REPL session."""
    try:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin("social_trends", version="1.0.0")
        skin.print_banner()
    except ImportError:
        click.echo(click.style("Social Trends CLI — Interactive Session", bold=True))
        click.echo("Type 'help' for commands, 'exit' to quit\n")

    click.echo("Available commands: youtube, tiktok, trends, hashtags, account, theme-page, config")
    click.echo("Run any command with --help for options\n")

    import subprocess
    while True:
        try:
            raw = input(click.style("social-trends> ", fg="cyan", bold=True)).strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break
        if not raw:
            continue
        if raw.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if raw.lower() == "help":
            click.echo("Commands: youtube trending | tiktok hashtags | trends aggregate | account score | theme-page roadmap")
            continue
        parts = raw.split()
        result = subprocess.run(
            ["cli-anything-social-trends"] + parts,
            capture_output=False,
        )


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    cli()


if __name__ == "__main__":
    main()
