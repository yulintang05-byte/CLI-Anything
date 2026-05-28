#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, build theme pages.

Unified command-line tool for:
- Scraping YouTube & TikTok for viral trends, hashtags, and music
- Analyzing and recommending hashtag strategies per niche
- Discovering trending sounds and audio
- Auditing and optimizing social media accounts
- Building and converting to niche theme pages

Usage:
    # Configure API keys (optional — improves data quality)
    cli-anything-social-trends auth setup --youtube-api-key <KEY>

    # Get trending videos and hashtags from YouTube
    cli-anything-social-trends trends youtube --region US --max 20

    # Get trending TikTok hashtags
    cli-anything-social-trends trends tiktok --region US

    # Discover trending sounds
    cli-anything-social-trends music trending --platform tiktok

    # Get hashtag recommendations for your niche
    cli-anything-social-trends hashtags recommend --niche fitness --platform tiktok

    # Analyze your account
    cli-anything-social-trends accounts analyze --followers 5000 --avg-views 10000 \
        --avg-likes 800 --avg-comments 50 --platform tiktok --niche fitness

    # Theme page conversion guide
    cli-anything-social-trends theme-page convert --from personal --to fitness --followers 2000

    # Interactive REPL
    cli-anything-social-trends
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
from cli_anything.social_trends.core import music as mu_mod
from cli_anything.social_trends.core import accounts as ac_mod
from cli_anything.social_trends.core import theme_pages as tp_mod
from cli_anything.social_trends.utils.social_backend import (
    load_config, save_config,
)

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


# ── Main CLI Group ──────────────────────────────────────────────────────
@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — Viral trend intelligence and account optimization.

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
@click.option("--youtube-api-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-client-key", default=None, help="TikTok Research API client key")
@click.option("--tiktok-client-secret", default=None, help="TikTok Research API client secret")
@handle_error
def auth_setup(youtube_api_key, tiktok_client_key, tiktok_client_secret):
    """Configure API credentials.

    Without credentials, the CLI uses yt-dlp and web scraping (free, no limits).
    Adding API keys unlocks higher rate limits and richer data.

    YouTube Data API v3: https://console.cloud.google.com/apis/api/youtube.googleapis.com
    TikTok Research API: https://developers.tiktok.com/products/research-api/
    """
    config = load_config()
    if youtube_api_key:
        config["youtube_api_key"] = youtube_api_key
    if tiktok_client_key:
        config["tiktok_client_key"] = tiktok_client_key
    if tiktok_client_secret:
        config["tiktok_client_secret"] = tiktok_client_secret
    save_config(config)
    result = {
        "status": "configured",
        "youtube_api": "configured" if config.get("youtube_api_key") else "not set (using yt-dlp)",
        "tiktok_api": "configured" if config.get("tiktok_client_key") else "not set (using web scraping)",
    }
    output(result, "Credentials saved.")


@auth.command("status")
@handle_error
def auth_status():
    """Show current credential configuration."""
    config = load_config()
    result = {
        "youtube_api_key": "configured" if config.get("youtube_api_key") else "not set",
        "tiktok_client_key": "configured" if config.get("tiktok_client_key") else "not set",
        "mode": (
            "full API mode" if config.get("youtube_api_key") and config.get("tiktok_client_key")
            else "yt-dlp + web scraping mode (no API keys)"
        ),
    }
    output(result)


# ── Trends Commands ─────────────────────────────────────────────────────
@cli.group()
def trends():
    """Discover viral trends from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--region", "-r", default="US", help="Region code (US, GB, CA, AU, ...)")
@click.option("--category", "-c", default="0",
              type=click.Choice(list(yt_mod.YOUTUBE_CATEGORIES.keys())),
              help="Category (0=all, 10=music, 17=sports, 20=gaming, 24=entertainment)")
@click.option("--max", "max_results", default=20, type=int, help="Max videos to return")
@click.option("--hashtags", "show_hashtags", is_flag=True, help="Also extract trending hashtags")
@handle_error
def trends_youtube(region, category, max_results, show_hashtags):
    """Fetch YouTube trending videos.

    Uses YouTube Data API v3 if configured, otherwise yt-dlp (no API key needed).

    Examples:
        cli-anything-social-trends trends youtube --region US --max 20
        cli-anything-social-trends trends youtube --category 10 --hashtags
        cli-anything-social-trends --json trends youtube --region GB
    """
    if not _json_output:
        click.echo(f"Fetching YouTube trending for region={region}, category={yt_mod.YOUTUBE_CATEGORIES.get(category, category)}...")
    videos = yt_mod.get_trending(region, category, max_results)

    if not _json_output:
        click.echo(f"\nTop {len(videos)} Trending Videos on YouTube ({region}):\n")
        for i, v in enumerate(videos, 1):
            views = f"{v['views']:,}" if v.get('views') else "N/A"
            er = f"{v['engagement_rate']}%" if v.get('engagement_rate') else "N/A"
            click.echo(f"  {i:2}. {v['title'][:70]}")
            click.echo(f"      Channel: {v['channel']}  |  Views: {views}  |  ER: {er}")
            if v.get("tags"):
                top_tags = [f"#{t}" for t in v["tags"][:4]]
                click.echo(f"      Tags: {' '.join(top_tags)}")
            click.echo()
    else:
        result = {"videos": videos}
        if show_hashtags:
            result["trending_hashtags"] = yt_mod.extract_hashtags_from_videos(videos)
        output(result)
        return

    if show_hashtags:
        hashtag_data = yt_mod.extract_hashtags_from_videos(videos)
        click.echo("\nTop Hashtags from Trending Videos:\n")
        for h in hashtag_data[:15]:
            click.echo(f"  {h['hashtag']:<25}  count: {h['count']}  avg_views: {h['avg_views']:,}")


@trends.command("tiktok")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--max", "max_results", default=30, type=int, help="Max hashtags to return")
@click.option("--sounds", "show_sounds", is_flag=True, help="Also fetch trending sounds")
@handle_error
def trends_tiktok(region, max_results, show_sounds):
    """Fetch TikTok trending hashtags and content.

    Uses TikTok Research API if configured, otherwise curated + web scraping.

    Examples:
        cli-anything-social-trends trends tiktok --region US
        cli-anything-social-trends trends tiktok --sounds
        cli-anything-social-trends --json trends tiktok --region US
    """
    if not _json_output:
        click.echo(f"Fetching TikTok trending for region={region}...")
    hashtags = tt_mod.get_trending_hashtags_web(region, max_results)
    ranked = ht_mod.rank_hashtags(hashtags)

    if _json_output:
        result = {"trending_hashtags": ranked}
        if show_sounds:
            result["trending_sounds"] = tt_mod.get_trending_sounds_web(region)
        output(result)
        return

    click.echo(f"\nTop {len(ranked)} Trending Hashtags on TikTok ({region}):\n")
    click.echo(f"  {'#':30} {'Videos':>12} {'Views':>18} {'Competition'}")
    click.echo(f"  {'─' * 30} {'─' * 12} {'─' * 18} {'─' * 12}")
    for h in ranked[:max_results]:
        vc = f"{h.get('video_count', 0):,}"
        vv = f"{h.get('view_count', 0):,}"
        comp = h.get("competition", "")
        tag = h.get("hashtag", "")[:28]
        click.echo(f"  {tag:<30} {vc:>12} {vv:>18} {comp}")

    if show_sounds:
        sounds = tt_mod.get_trending_sounds_web(region)
        click.echo(f"\nTop Trending Sounds on TikTok ({region}):\n")
        for i, s in enumerate(sounds[:10], 1):
            artist = s.get("artist", "unknown")
            title = s.get("title", "")[:50]
            vc = f"{s.get('video_count', 0):,}"
            click.echo(f"  {i:2}. {title:<50}  by {artist:<25}  {vc} videos")


@trends.command("all")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--max", "max_results", default=10, type=int, help="Results per platform")
@handle_error
def trends_all(region, max_results):
    """Fetch trending content from all platforms simultaneously.

    Combines YouTube and TikTok data for cross-platform trend analysis.
    """
    click.echo(f"Fetching trends from all platforms for region={region}...")

    yt_videos = yt_mod.get_trending(region, "0", max_results)
    tt_hashtags = tt_mod.get_trending_hashtags_web(region, max_results)
    tt_sounds = tt_mod.get_trending_sounds_web(region, max_results)

    result = {
        "region": region,
        "youtube_trending": yt_videos[:max_results],
        "tiktok_trending_hashtags": ht_mod.rank_hashtags(tt_hashtags)[:max_results],
        "tiktok_trending_sounds": tt_sounds[:max_results],
        "cross_platform_hashtags": yt_mod.extract_hashtags_from_videos(yt_videos)[:10],
    }

    if _json_output:
        output(result)
        return

    click.echo("\n=== YOUTUBE TRENDING ===")
    for i, v in enumerate(yt_videos[:5], 1):
        click.echo(f"  {i}. {v['title'][:65]}  ({v['views']:,} views)")

    click.echo("\n=== TIKTOK TRENDING HASHTAGS ===")
    for h in tt_hashtags[:8]:
        click.echo(f"  {h['hashtag']:<25}  {h.get('video_count', 0):,} videos")

    click.echo("\n=== TIKTOK TRENDING SOUNDS ===")
    for i, s in enumerate(tt_sounds[:5], 1):
        click.echo(f"  {i}. {s['title']:<45}  by {s.get('artist', 'unknown')}")


# ── Hashtag Commands ────────────────────────────────────────────────────
@cli.group()
def hashtags():
    """Analyze, discover, and optimize hashtag strategy."""
    pass


@hashtags.command("recommend")
@click.option("--niche", "-n", required=True, help="Your content niche (fitness, cooking, gaming, etc.)")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Target platform")
@handle_error
def hashtags_recommend(niche, platform):
    """Get a recommended hashtag strategy for your niche.

    Generates a balanced mix: broad (mega reach) + medium + niche-specific.
    Platform-specific best practices are applied.

    Examples:
        cli-anything-social-trends hashtags recommend --niche fitness --platform tiktok
        cli-anything-social-trends hashtags recommend --niche cooking --platform youtube
        cli-anything-social-trends --json hashtags recommend --niche gaming
    """
    result = ht_mod.recommend_hashtag_mix(niche, platform)

    if _json_output:
        output(result)
        return

    click.echo(f"\nHashtag Strategy for #{niche} on {platform.title()}:\n")
    click.echo(f"  Strategy:   {result['strategy']}")
    click.echo(f"  Broad:      {' '.join(result['broad'])}")
    click.echo(f"  Medium:     {' '.join(result['medium'])}")
    click.echo(f"  Niche:      {' '.join(result['niche_specific'])}")
    if result.get("recommended_caption"):
        click.echo(f"\n  Caption example: {result['recommended_caption']}")
    click.echo(f"\n  Tip: {result['tip']}")


@hashtags.command("analyze")
@click.argument("hashtags_str")
@handle_error
def hashtags_analyze(hashtags_str):
    """Analyze a set of hashtags for strategy quality.

    HASHTAGS_STR: Space or comma-separated hashtags (e.g., '#fyp #fitness #gym').

    Examples:
        cli-anything-social-trends hashtags analyze '#fyp #fitness #gym #workout'
        cli-anything-social-trends hashtags analyze 'fyp,fitness,gym,workout,gains'
    """
    # Parse comma or space separated
    tags = [t.strip() for t in hashtags_str.replace(",", " ").split() if t.strip()]
    result = ht_mod.analyze_hashtag_set(tags)

    if _json_output:
        output(result)
        return

    click.echo(f"\nHashtag Analysis ({len(tags)} tags):\n")
    click.echo(f"  Quality Score:  {result['quality_score']}/100")
    click.echo(f"  Unique Tags:    {result['unique_count']}")
    click.echo(f"  Broad Tags:     {' '.join(result['broad_tags']) or 'none'}")
    click.echo(f"  Niche Tags:     {' '.join(result['niche_tags'][:5]) or 'none'}")

    if result["issues"]:
        click.echo("\n  Issues:")
        for issue in result["issues"]:
            click.echo(f"    ⚠ {issue}")

    if result["recommendations"]:
        click.echo("\n  Recommendations:")
        for rec in result["recommendations"]:
            click.echo(f"    → {rec}")


@hashtags.command("lookup")
@click.argument("tag")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok"]),
              help="Platform to look up on")
@handle_error
def hashtags_lookup(tag, platform):
    """Look up stats for a specific hashtag.

    TAG: Hashtag name (with or without #).

    Examples:
        cli-anything-social-trends hashtags lookup fitness
        cli-anything-social-trends hashtags lookup '#gymtok'
    """
    result = tt_mod.search_hashtag(tag)
    output(result, f"Stats for {result.get('hashtag', tag)}:")


@hashtags.command("discover")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--max", "max_results", default=20, type=int, help="Number of hashtags to show")
@click.option("--sort", default="opportunity",
              type=click.Choice(["opportunity", "virality", "views", "volume"]),
              help="Sort by metric")
@handle_error
def hashtags_discover(region, max_results, sort):
    """Discover trending hashtags ranked by opportunity score.

    Opportunity score = high views relative to competition (sweet spot for growth).
    """
    click.echo(f"Discovering trending hashtags (region={region})...")
    raw = tt_mod.get_trending_hashtags_web(region, max_results * 2)
    ranked = ht_mod.rank_hashtags(raw)

    if sort == "virality":
        ranked.sort(key=lambda x: x.get("virality_score", 0), reverse=True)
    elif sort == "views":
        ranked.sort(key=lambda x: x.get("view_count", 0), reverse=True)
    elif sort == "volume":
        ranked.sort(key=lambda x: x.get("video_count", 0), reverse=True)
    # default: opportunity (already sorted)

    result = ranked[:max_results]

    if _json_output:
        output(result)
        return

    click.echo(f"\nTop {len(result)} Hashtags by {sort.title()} (TikTok, {region}):\n")
    click.echo(f"  {'Hashtag':<28} {'Opp.':>6} {'Viral':>7} {'Comp.':<15}")
    click.echo(f"  {'─' * 28} {'─' * 6} {'─' * 7} {'─' * 15}")
    for h in result:
        tag = h.get("hashtag", "")[:26]
        opp = f"{h.get('opportunity_score', 0):.0f}"
        viral = f"{h.get('virality_score', 0):.0f}"
        comp = h.get("competition", "")
        click.echo(f"  {tag:<28} {opp:>6} {viral:>7} {comp:<15}")


# ── Music Commands ──────────────────────────────────────────────────────
@cli.group()
def music():
    """Discover trending sounds and music for your content."""
    pass


@music.command("trending")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "all"]),
              help="Platform to fetch from")
@click.option("--region", "-r", default="US", help="Region code")
@click.option("--max", "max_results", default=20, type=int, help="Max results")
@handle_error
def music_trending(platform, region, max_results):
    """Discover currently trending sounds and music.

    Shows trending sounds with genre, mood, and content use cases.

    Examples:
        cli-anything-social-trends music trending --platform tiktok
        cli-anything-social-trends music trending --platform all --max 30
        cli-anything-social-trends --json music trending --platform tiktok
    """
    if not _json_output:
        click.echo(f"Fetching trending {platform} sounds (region={region})...")
    sounds = mu_mod.get_trending_sounds(platform, region, max_results)

    if _json_output:
        output({"trending_sounds": sounds})
        return

    click.echo(f"\nTop {len(sounds)} Trending Sounds ({platform.title()}, {region}):\n")
    click.echo(f"  {'#':<4} {'Title':<45} {'Artist':<25} {'Videos':>10}")
    click.echo(f"  {'─'*4} {'─'*45} {'─'*25} {'─'*10}")
    for i, s in enumerate(sounds, 1):
        title = s.get("title", "unknown")[:43]
        artist = s.get("artist", "")[:23]
        vc = f"{s.get('video_count', 0):,}"
        click.echo(f"  {i:<4} {title:<45} {artist:<25} {vc:>10}")

    click.echo(f"\n  Genre breakdown:")
    genres = {}
    for s in sounds:
        g = s.get("genre", "other")
        genres[g] = genres.get(g, 0) + 1
    for g, count in sorted(genres.items(), key=lambda x: x[1], reverse=True):
        click.echo(f"    {g:<20} {count} sounds")


@music.command("strategy")
@click.option("--niche", "-n", required=True, help="Your content niche")
@handle_error
def music_strategy(niche):
    """Get a music/sound strategy tailored to your content niche.

    Explains which genres and moods work best for your content type,
    with tips on how to leverage trending audio.

    Examples:
        cli-anything-social-trends music strategy --niche fitness
        cli-anything-social-trends music strategy --niche cooking
    """
    result = mu_mod.get_sound_strategy(niche)

    if _json_output:
        output(result)
        return

    click.echo(f"\nSound Strategy for {niche.title()} Content:\n")
    click.echo(f"  Recommended Genres: {', '.join(result['recommended_genres'])}")
    click.echo(f"  Best Moods:         {', '.join(result['moods'])}")
    click.echo(f"\n  Audio Tips:")
    for tip in result["audio_tips"]:
        click.echo(f"    → {tip}")
    click.echo(f"\n  Key Insight: {result['posting_tip']}")


# ── Accounts Commands ───────────────────────────────────────────────────
@cli.group()
def accounts():
    """Analyze and optimize your social media accounts."""
    pass


@accounts.command("analyze")
@click.option("--followers", type=int, required=True, help="Follower count")
@click.option("--following", type=int, default=0, help="Following count")
@click.option("--total-posts", type=int, default=0, help="Total posts")
@click.option("--avg-views", type=int, default=0, help="Average views per post")
@click.option("--avg-likes", type=int, default=0, help="Average likes per post")
@click.option("--avg-comments", type=int, default=0, help="Average comments per post")
@click.option("--avg-shares", type=int, default=0, help="Average shares per post")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              help="Platform")
@click.option("--niche", "-n", default="general", help="Content niche")
@click.option("--account-age-days", type=int, default=365, help="Account age in days")
@click.option("--save-as", default=None, help="Save this profile under a name")
@handle_error
def accounts_analyze(followers, following, total_posts, avg_views, avg_likes,
                      avg_comments, avg_shares, platform, niche, account_age_days,
                      save_as):
    """Perform a full account analysis with optimization recommendations.

    Calculates engagement rate, virality coefficient, monetization eligibility,
    and generates the top 5 most impactful growth recommendations.

    Examples:
        cli-anything-social-trends accounts analyze --followers 5000 \\
            --avg-views 8000 --avg-likes 600 --avg-comments 40 --platform tiktok

        cli-anything-social-trends accounts analyze --followers 50000 \\
            --avg-views 10000 --avg-likes 800 --platform youtube --niche gaming
    """
    stats = {
        "followers": followers,
        "following": following,
        "total_posts": total_posts,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_shares": avg_shares,
        "platform": platform,
        "niche": niche,
        "account_age_days": account_age_days,
    }

    result = ac_mod.analyze_account(stats)

    if save_as:
        path = ac_mod.save_account_profile(save_as, {**stats, **result})
        result["saved_to"] = path

    if _json_output:
        output(result)
        return

    click.echo(f"\nAccount Analysis — {platform.title()} / {niche.title()} niche\n")
    click.echo(f"  Followers:           {followers:,}")
    click.echo(f"  Follow Ratio:        {result['follow_ratio']}  ({result['follow_ratio_health']})")
    click.echo(f"  Posts/Month:         {result['posts_per_month']}  (recommended: {result['recommended_frequency']})")
    click.echo(f"  Avg Views:           {avg_views:,}")
    click.echo(f"  Engagement Rate:     {result['engagement']['engagement_rate']}%  → {result['engagement']['grade']}")
    click.echo(f"  Virality Coeff.:     {result['virality_coefficient']}x  ({result['virality_label']})")
    click.echo(f"  Growth Rate:         {result['estimated_growth_rate']}")
    click.echo(f"  Account Score:       {result['score']}/100")

    click.echo(f"\n  Monetization:")
    for prog, req in result["monetization_status"].get("requirements", {}).items():
        eligible = prog in result["monetization_status"].get("eligible", [])
        status = "✓ ELIGIBLE" if eligible else "✗"
        click.echo(f"    {status}  {prog}: {req}")

    click.echo(f"\n  Top Recommendations:")
    for i, rec in enumerate(result["top_recommendations"], 1):
        click.echo(f"    {i}. {rec}")


@accounts.command("bio")
@click.option("--niche", "-n", required=True, help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              help="Platform")
@click.option("--keywords", default="", help="Custom keywords (comma-separated)")
@click.option("--cta", default="", help="Call-to-action text")
@handle_error
def accounts_bio(niche, platform, keywords, cta):
    """Generate an optimized bio for your profile.

    Produces platform-appropriate bios with character counts and writing tips.

    Examples:
        cli-anything-social-trends accounts bio --niche fitness --platform tiktok
        cli-anything-social-trends accounts bio --niche cooking --platform instagram \\
            --cta 'Free recipes — link in bio'
    """
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
    result = ac_mod.generate_bio(niche, platform, kw_list, cta)

    if _json_output:
        output(result)
        return

    click.echo(f"\nOptimized {platform.title()} Bio for {niche.title()} niche:\n")
    click.echo(f"  ── Bio ──────────────────────────────────────────────")
    click.echo(f"  {result['bio']}")
    click.echo(f"  ─────────────────────────────────────────────────────")
    click.echo(f"  Character count: {result['character_count']}/{result['character_limit']}")
    click.echo(f"\n  Examples:")
    for i, ex in enumerate(result["examples"][:3], 1):
        click.echo(f"\n  [{i}] {ex}")
    click.echo(f"\n  Tips:")
    for tip in result["tips"][:4]:
        click.echo(f"    → {tip}")


@accounts.command("schedule")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram_reels", "youtube_shorts", "youtube"]),
              help="Platform")
@handle_error
def accounts_schedule(platform):
    """Get the optimal posting schedule for your platform.

    Shows best days, times (UTC), and frequency recommendations.
    """
    from cli_anything.social_trends.core.accounts import _POSTING_SCHEDULES
    schedule = _POSTING_SCHEDULES.get(platform, _POSTING_SCHEDULES["tiktok"])

    if _json_output:
        output({**schedule, "platform": platform})
        return

    click.echo(f"\nOptimal Posting Schedule for {platform.replace('_', ' ').title()}:\n")
    click.echo(f"  Best Days:      {', '.join(schedule['best_days'])}")
    click.echo(f"  Best Times UTC: {', '.join(schedule['best_times_utc'])}")
    click.echo(f"  Frequency:      {schedule['frequency']}")
    click.echo(f"\n  Note: {schedule['note']}")


@accounts.command("list")
@handle_error
def accounts_list():
    """List all saved account profiles."""
    profiles = ac_mod.list_account_profiles()
    if not profiles:
        click.echo("No saved profiles. Use 'accounts analyze --save-as <name>' to save one.")
        return
    output(profiles, f"{len(profiles)} saved profiles:")


@accounts.command("load")
@click.argument("name")
@handle_error
def accounts_load(name):
    """Load and re-analyze a saved account profile.

    NAME: Profile name used when saving with --save-as.
    """
    profile = ac_mod.load_account_profile(name)
    output(profile, f"Profile: {name}")


# ── Theme Page Commands ─────────────────────────────────────────────────
@cli.group("theme-page")
def theme_page():
    """Build, convert, and scale niche theme pages."""
    pass


@theme_page.command("niches")
@click.option("--category", "-c", default=None, help="Filter by category")
@click.option("--sort", default="profitability",
              type=click.Choice(["profitability", "competition", "growth"]),
              help="Sort order")
@handle_error
def theme_page_niches(category, sort):
    """Browse profitable niches for theme pages.

    Shows profitability, competition, monetization methods, and examples
    for 13+ proven theme page niches.

    Examples:
        cli-anything-social-trends theme-page niches
        cli-anything-social-trends theme-page niches --category 'money & business'
        cli-anything-social-trends --json theme-page niches
    """
    niches = tp_mod.get_niche_database()

    if category:
        niches = [n for n in niches if category.lower() in n.get("category", "").lower()]

    if sort == "competition":
        order = {"low": 0, "medium": 1, "high": 2, "very high": 3}
        niches.sort(key=lambda n: order.get(n.get("competition", ""), 2))
    elif sort == "growth":
        order = {"slow": 0, "steady": 1, "fast": 2, "very fast": 3, "volatile": 1}
        niches.sort(key=lambda n: order.get(n.get("growth_rate", ""), 1), reverse=True)
    else:  # profitability
        order = {"medium": 0, "high": 1, "very high": 2}
        niches.sort(key=lambda n: order.get(n.get("profitability", ""), 0), reverse=True)

    if _json_output:
        output(niches)
        return

    click.echo(f"\nTheme Page Niches ({len(niches)} total):\n")
    click.echo(f"  {'Niche':<15} {'Profit':>8} {'Comp.':>10} {'Growth':>12} {'Followers to $':>16}")
    click.echo(f"  {'─' * 15} {'─' * 8} {'─' * 10} {'─' * 12} {'─' * 16}")
    for n in niches:
        name = n["name"][:13]
        profit = n["profitability"]
        comp = n["competition"]
        growth = n["growth_rate"]
        ftm = f"{n['avg_followers_to_monetize']:,}"
        click.echo(f"  {name:<15} {profit:>8} {comp:>10} {growth:>12} {ftm:>16}")


@theme_page.command("info")
@click.argument("niche")
@handle_error
def theme_page_info(niche):
    """Get detailed info on a specific niche.

    NICHE: Niche name (e.g., fitness, finance, gaming).

    Examples:
        cli-anything-social-trends theme-page info fitness
        cli-anything-social-trends theme-page info tech
    """
    info = tp_mod.get_niche_info(niche)
    output(info, f"Niche info: {niche}")


@theme_page.command("convert")
@click.option("--from", "from_niche", required=True, help="Current niche/type (e.g., personal, lifestyle)")
@click.option("--to", "to_niche", required=True, help="Target niche for theme page (e.g., fitness, finance)")
@click.option("--followers", type=int, default=0, help="Current follower count")
@handle_error
def theme_page_convert(from_niche, to_niche, followers):
    """Get a step-by-step account conversion playbook.

    Generates a risk-assessed conversion plan with:
    - Whether to start fresh or pivot existing account
    - Week-by-week action roadmap
    - Full branding checklist
    - 30-day action plan
    - Monetization timeline

    Examples:
        cli-anything-social-trends theme-page convert --from personal --to fitness --followers 2000
        cli-anything-social-trends theme-page convert --from lifestyle --to finance --followers 50000
    """
    result = tp_mod.get_conversion_playbook(from_niche, to_niche, followers)

    if _json_output:
        output(result)
        return

    click.echo(f"\nConversion Playbook: {from_niche.title()} → {to_niche.title()} Theme Page\n")
    click.echo(f"  Followers:       {followers:,}")
    click.echo(f"  Strategy:        {result['conversion_type'].replace('_', ' ').title()}")
    click.echo(f"  Risk Level:      {result['risk_level']}")
    click.echo(f"\n  Risk Assessment: {result['risk_note']}")

    click.echo(f"\n  Roadmap:")
    for step in result["roadmap"]:
        click.echo(f"    [{step.get('week', step.get('days', ''))}] {step['action']}")
        click.echo(f"           Focus: {step.get('focus', step.get('actions', [''])[0])}")

    click.echo(f"\n  Branding Checklist:")
    for item in result["branding_checklist"][:6]:
        click.echo(f"    ☐ {item['item']}: {item['guidance']}")

    click.echo(f"\n  30-Day Action Plan:")
    for phase in result["first_30_days"]:
        click.echo(f"\n    Days {phase['days']} — {phase['goal']}:")
        for action in phase["actions"][:3]:
            click.echo(f"      → {action}")

    click.echo(f"\n  Monetization Timeline:")
    for milestone in result["monetization_timeline"]:
        click.echo(f"\n    {milestone['milestone']}")
        if "revenue_streams" in milestone:
            for stream in milestone["revenue_streams"][:3]:
                click.echo(f"      • {stream}")
        if "estimated_monthly" in milestone:
            click.echo(f"      Est. monthly: {milestone['estimated_monthly']}")


@theme_page.command("content")
@click.option("--niche", "-n", required=True, help="Content niche")
@click.option("--posts-per-week", type=int, default=14, help="Target posts per week")
@handle_error
def theme_page_content(niche, posts_per_week):
    """Generate a content strategy and posting schedule for a theme page.

    Produces content pillars, viral format templates, specific video ideas,
    and a weekly posting schedule.

    Examples:
        cli-anything-social-trends theme-page content --niche fitness --posts-per-week 14
        cli-anything-social-trends theme-page content --niche finance --posts-per-week 7
    """
    result = tp_mod.get_content_pillars(niche, posts_per_week)

    if _json_output:
        output(result)
        return

    click.echo(f"\nContent Strategy for {niche.title()} Theme Page ({posts_per_week} posts/week):\n")
    click.echo(f"  Content Pillars:")
    for p in result["pillars"]:
        alloc = result["pillar_allocation"].get(p, "")
        click.echo(f"    • {p:<35}  {alloc}")

    click.echo(f"\n  15 Content Ideas:")
    for i, idea in enumerate(result["content_ideas"][:10], 1):
        click.echo(f"    {i:2}. {idea}")

    click.echo(f"\n  Weekly Posting Schedule (first 7 days):")
    for day in result["posting_schedule_template"]:
        click.echo(f"    {day['day']:<12} {day['pillar']:<35} {day['best_time_utc']} UTC")

    click.echo(f"\n  Top Viral Formats:")
    for fmt in result["viral_formats"][:4]:
        click.echo(f"    • {fmt['format']:<25}  {fmt['avg_retention']} retention  |  ex: {fmt['example'][:50]}")


@theme_page.command("guide")
@handle_error
def theme_page_guide():
    """Print the complete theme page creation guide.

    Covers everything from choosing a niche to scaling to $10K/month.
    """
    guide = _THEME_PAGE_GUIDE

    if _json_output:
        output(guide)
        return

    click.echo("\n" + "═" * 65)
    click.echo("  THE COMPLETE THEME PAGE PLAYBOOK")
    click.echo("  From Zero to $10K/Month with a Niche Account")
    click.echo("═" * 65)

    for section in guide["sections"]:
        click.echo(f"\n## {section['title']}")
        click.echo(f"   {section['summary']}")
        for point in section["key_points"]:
            click.echo(f"   → {point}")


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
        "auth":       "setup|status  — manage API keys",
        "trends":     "youtube|tiktok|all  — discover viral trends",
        "hashtags":   "recommend|analyze|discover|lookup  — hashtag strategy",
        "music":      "trending|strategy  — trending sounds & audio",
        "accounts":   "analyze|bio|schedule|list  — optimize your accounts",
        "theme-page": "niches|info|convert|content|guide  — build theme pages",
        "help":       "show this help",
        "quit":       "exit REPL",
    }

    skin.info("Welcome to Social Trends CLI! Get viral trends, optimize accounts, and build theme pages.")
    skin.info("No API keys required — yt-dlp + web scraping mode active.")
    skin.info("Run 'auth setup --youtube-api-key <KEY>' for enhanced YouTube data.")

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


# ── Static Guide Content ─────────────────────────────────────────────────

_THEME_PAGE_GUIDE = {
    "title": "The Complete Theme Page Playbook",
    "sections": [
        {
            "title": "1. What is a Theme Page?",
            "summary": "A theme page curates content around a single topic. You don't need to be on camera.",
            "key_points": [
                "Curate viral content from your niche with proper credit",
                "Post 2-4x daily using trending sounds and hashtags",
                "Your personal identity is optional — the NICHE is the brand",
                "Examples: @dog_facts, @motivationhub, @techdeals, @fitnessquotes",
            ],
        },
        {
            "title": "2. Choosing Your Niche",
            "summary": "Pick a niche with high profitability, moderate competition, and content availability.",
            "key_points": [
                "Best niches: finance, motivation, tech, fitness, beauty (high CPM)",
                "Avoid: oversaturated niches without a unique angle",
                "Validate: search the niche on TikTok — is there daily viral content to curate?",
                "Run: cli-anything-social-trends theme-page niches for a full comparison",
            ],
        },
        {
            "title": "3. Setting Up the Account",
            "summary": "Brand everything around the niche from day 1.",
            "key_points": [
                "Username: @[niche]daily, @best[niche], @[niche]world",
                "Profile pic: logo or branded image (NOT your face)",
                "Bio: 'Daily [niche] content | Follow for [value proposition]'",
                "Link in bio: Beacons or Linktree with affiliate links from day 1",
            ],
        },
        {
            "title": "4. Content Strategy",
            "summary": "Post 2-4x daily. Mix formats: carousels, reels, duets.",
            "key_points": [
                "Content ratio: 80% curated, 20% original",
                "Always credit original creators — builds goodwill and avoids reports",
                "Trending sound + niche content = maximum algorithmic reach",
                "Hook in first 1-3 seconds: text overlay or bold visual",
            ],
        },
        {
            "title": "5. Growth Tactics",
            "summary": "Compound growth through engagement, collabs, and algorithmic signals.",
            "key_points": [
                "Reply to EVERY comment in the first hour — algorithm boost",
                "S4S (shoutout-for-shoutout) with accounts of similar size",
                "Duet/stitch trending videos in your niche",
                "Post at peak times: 6am, 10am, 7pm, 10pm UTC",
                "Consistency beats volume: 2x/day every day > 10x/day for one week",
            ],
        },
        {
            "title": "6. Monetization at Every Stage",
            "summary": "Start monetizing at 1K followers. Scale with each milestone.",
            "key_points": [
                "1K: Affiliate links (Amazon, impact.com), TikTok Shop",
                "10K: Paid shoutouts $25-$150, micro brand deals",
                "50K: Brand partnerships $200-$1,000/post, digital products",
                "100K+: Premium brand deals, your own course, agency model",
            ],
        },
        {
            "title": "7. Scaling to Multiple Pages",
            "summary": "Once one page is profitable, replicate the system in a new niche.",
            "key_points": [
                "Document your process: content calendar, tools, posting times",
                "Hire a VA ($5-$15/hr) to find and schedule content",
                "Each page is a business unit — track P&L per page",
                "10 pages × $1K/month = $10K/month with one team member",
            ],
        },
    ],
}


# ── Entry Point ──────────────────────────────────────────────────────────
def main():
    cli()


if __name__ == "__main__":
    main()
