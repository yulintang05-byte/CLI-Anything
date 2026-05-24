#!/usr/bin/env python3
"""Viral Trends CLI — Scrape YouTube & TikTok for viral trends, optimize accounts.

Usage:
    viral-trends youtube-trending --region us --category music
    viral-trends tiktok-trending --region us --limit 20
    viral-trends all-trends --region us
    viral-trends hashtags --niche finance
    viral-trends sounds --region us
    viral-trends optimize-account --platform tiktok --type theme_page --niche finance
    viral-trends content-calendar --niche finance --platforms tiktok youtube_shorts
    viral-trends growth-hacks --platform tiktok --type theme_page
    viral-trends theme-page --action roadmap --niche finance --followers 0
    viral-trends theme-page --action niches
    viral-trends theme-page --action conversion
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.viral_trends.core import youtube_scraper, tiktok_scraper, trend_analyzer
from cli_anything.viral_trends.core import account_optimizer, theme_page_guide

_json_output = False


def _status(msg: str, **kwargs):
    """Print a status message. Suppressed in JSON mode to keep stdout clean."""
    if not _json_output:
        click.secho(msg, **kwargs)


def _out(data, message: str = ""):
    """Output result. JSON or human-readable."""
    global _json_output
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(f"\n{message}", fg="green", bold=True)
        _pretty(data)


def _pretty(obj, indent: int = 0):
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                click.secho(f"{pad}{k}:", fg="cyan", bold=True)
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{click.style(k, fg='cyan')}: {v}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                click.secho(f"{pad}[{i+1}]", fg="yellow")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{obj}")


@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
def cli(use_json: bool):
    """Viral Trends — YouTube & TikTok trend scraper + social media account optimizer."""
    global _json_output
    _json_output = use_json


# ─── YouTube ──────────────────────────────────────────────────────────────────

@cli.command("youtube-trending")
@click.option("--region", default="us", show_default=True, help="Country code (us, uk, ca, au, in…)")
@click.option("--category", default="now", show_default=True,
              type=click.Choice(["now", "music", "gaming", "films", "shorts"]),
              help="Trending category")
@click.option("--limit", default=20, show_default=True, help="Max videos to return")
def youtube_trending(region: str, category: str, limit: int):
    """Fetch YouTube trending videos, hashtags, and music."""
    _status(f"Fetching YouTube trending [{category}] for region {region.upper()}…", fg="blue")
    data = youtube_scraper.fetch_trending(category=category, region=region, limit=limit)
    _out(data, f"YouTube Trending — {category.upper()} ({region.upper()})")


@cli.command("youtube-music")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=20, show_default=True)
def youtube_music(region: str, limit: int):
    """Fetch YouTube Music trending tracks."""
    _status("Fetching YouTube Music trends…", fg="blue")
    data = youtube_scraper.fetch_music_trends(region=region, limit=limit)
    _out(data, "YouTube Music Trends")


@cli.command("youtube-hashtag")
@click.argument("hashtag")
@click.option("--limit", default=15, show_default=True)
def youtube_hashtag(hashtag: str, limit: int):
    """Fetch top YouTube videos for a specific HASHTAG."""
    _status(f"Fetching YouTube videos for {hashtag}…", fg="blue")
    data = youtube_scraper.search_hashtag(hashtag=hashtag, limit=limit)
    _out(data, f"YouTube Hashtag: {hashtag}")


# ─── TikTok ───────────────────────────────────────────────────────────────────

@cli.command("tiktok-trending")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=20, show_default=True)
def tiktok_trending(region: str, limit: int):
    """Fetch TikTok trending videos, hashtags, and sounds."""
    _status(f"Fetching TikTok trending for region {region.upper()}…", fg="magenta")
    data = tiktok_scraper.fetch_trending(region=region, limit=limit)
    _out(data, f"TikTok Trending ({region.upper()})")


@cli.command("tiktok-sounds")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=20, show_default=True)
def tiktok_sounds(region: str, limit: int):
    """Fetch TikTok trending sounds/music."""
    _status(f"Fetching TikTok trending sounds ({region.upper()})…", fg="magenta")
    data = tiktok_scraper.fetch_trending_sounds(region=region, limit=limit)
    _out(data, "TikTok Trending Sounds")


@cli.command("tiktok-hashtag")
@click.argument("hashtag")
@click.option("--limit", default=15, show_default=True)
def tiktok_hashtag(hashtag: str, limit: int):
    """Fetch top TikTok videos for a specific HASHTAG."""
    _status(f"Fetching TikTok videos for {hashtag}…", fg="magenta")
    data = tiktok_scraper.fetch_hashtag_trends(hashtag=hashtag, limit=limit)
    _out(data, f"TikTok Hashtag: {hashtag}")


@cli.command("tiktok-creators")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=15, show_default=True)
def tiktok_creators(region: str, limit: int):
    """Fetch trending TikTok creators in a region."""
    _status(f"Fetching TikTok trending creators ({region.upper()})…", fg="magenta")
    data = tiktok_scraper.fetch_creator_trends(region=region, limit=limit)
    _out(data, f"TikTok Trending Creators ({region.upper()})")


# ─── Cross-platform analysis ──────────────────────────────────────────────────

@cli.command("all-trends")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=20, show_default=True)
def all_trends(region: str, limit: int):
    """Fetch & aggregate viral trends from BOTH YouTube and TikTok."""
    _status(f"Scraping YouTube + TikTok trends for {region.upper()}…", fg="white", bold=True)

    _status("  → YouTube trending…", fg="blue")
    yt = youtube_scraper.fetch_trending(category="now", region=region, limit=limit)
    _status("  → YouTube Music…", fg="blue")
    yt_music = youtube_scraper.fetch_music_trends(region=region, limit=15)
    _status("  → TikTok trending…", fg="magenta")
    tt = tiktok_scraper.fetch_trending(region=region, limit=limit)

    hashtags = trend_analyzer.aggregate_hashtags(yt_data=yt, tt_data=tt, top_n=30)
    music = trend_analyzer.aggregate_music(
        yt_music=yt_music.get("music_tracks", []),
        tt_music=tt.get("trending_music", []),
        top_n=20,
    )
    opportunities = trend_analyzer.score_content_opportunity(hashtags, music)

    result = {
        "region": region.upper(),
        "youtube_videos": len(yt.get("videos", [])),
        "tiktok_videos": len(tt.get("videos", [])),
        "top_hashtags": hashtags[:15],
        "top_music": music[:10],
        "content_opportunities": opportunities["content_opportunities"][:5],
    }
    _out(result, f"Aggregated Trends — {region.upper()}")


@cli.command("hashtags")
@click.option("--region", default="us", show_default=True)
@click.option("--niche", default="", help="Filter for a specific niche (e.g. finance, fitness)")
@click.option("--limit", default=30, show_default=True)
def hashtags_command(region: str, niche: str, limit: int):
    """Get top viral hashtags for a region, optionally filtered by niche."""
    _status(f"Fetching trending hashtags ({region.upper()})…", fg="white", bold=True)
    yt = youtube_scraper.fetch_trending(region=region, limit=30)
    tt = tiktok_scraper.fetch_trending(region=region, limit=30)
    aggregated = trend_analyzer.aggregate_hashtags(yt_data=yt, tt_data=tt, top_n=limit)

    if niche:
        strategy = trend_analyzer.niche_hashtag_strategy(niche=niche, hashtags=aggregated)
        _out(strategy, f"Hashtag Strategy — {niche}")
    else:
        _out({"top_hashtags": aggregated[:20]}, "Top Viral Hashtags")


@cli.command("sounds")
@click.option("--region", default="us", show_default=True)
@click.option("--limit", default=20, show_default=True)
def sounds(region: str, limit: int):
    """Get trending sounds/music across YouTube + TikTok."""
    _status(f"Fetching trending sounds ({region.upper()})…", fg="white", bold=True)
    yt_music = youtube_scraper.fetch_music_trends(region=region, limit=limit)
    tt_sounds = tiktok_scraper.fetch_trending_sounds(region=region, limit=limit)
    music = trend_analyzer.aggregate_music(
        yt_music=yt_music.get("music_tracks", []),
        tt_music=tt_sounds.get("trending_sounds", []),
        top_n=limit,
    )
    _out({"trending_sounds": music, "total": len(music)}, "Trending Sounds — Cross-Platform")


# ─── Account optimization ─────────────────────────────────────────────────────

@cli.command("optimize-account")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "youtube_shorts", "instagram"]),
              help="Platform to optimize for")
@click.option("--type", "account_type", default="theme_page", show_default=True,
              type=click.Choice(["theme_page", "personal_brand", "entertainment",
                                 "educational", "news", "fitness", "finance", "fashion"]),
              help="Type of account")
@click.option("--niche", default="", help="Your content niche (e.g. finance, fitness)")
@click.option("--bio", default="", help="Your current bio text for audit")
def optimize_account(platform: str, account_type: str, niche: str, bio: str):
    """Generate a full account optimization audit with posting schedule and hashtag strategy."""
    _status(f"Generating optimization audit for {platform} [{account_type}]…", fg="green")
    data = account_optimizer.generate_profile_audit(
        platform=platform,
        account_type=account_type,
        niche=niche,
        current_bio=bio,
    )
    _out(data, f"Account Optimization Audit — {platform.upper()}")


@cli.command("content-calendar")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platforms", default="tiktok,youtube_shorts", show_default=True,
              help="Comma-separated platforms (tiktok,youtube_shorts,instagram_reels)")
@click.option("--days", default=7, show_default=True, help="Days to plan (1–7)")
@click.option("--region", default="us", show_default=True)
def content_calendar(niche: str, platforms: str, days: int, region: str):
    """Generate a content calendar using current trending hashtags and sounds."""
    plat_list = [p.strip() for p in platforms.split(",")]
    _status(f"Fetching trends + building {days}-day calendar for {niche}…", fg="green")

    yt = youtube_scraper.fetch_trending(region=region, limit=20)
    tt = tiktok_scraper.fetch_trending(region=region, limit=20)
    agg_hashtags = trend_analyzer.aggregate_hashtags(yt_data=yt, tt_data=tt, top_n=20)
    agg_music = trend_analyzer.aggregate_music(
        yt_music=yt.get("music_tracks", []),
        tt_music=tt.get("trending_music", []),
        top_n=10,
    )

    calendar = account_optimizer.generate_content_calendar(
        niche=niche,
        platforms=plat_list,
        days=days,
        trending_hashtags=agg_hashtags,
        trending_music=agg_music,
    )
    _out(calendar, f"{days}-Day Content Calendar — {niche}")


@cli.command("growth-hacks")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--type", "account_type", default="theme_page")
def growth_hacks_cmd(platform: str, account_type: str):
    """Get proven growth hacks and monetization milestones for a platform."""
    data = account_optimizer.growth_hacks(platform=platform, account_type=account_type)
    _out(data, f"Growth Hacks — {platform.upper()}")


# ─── Theme page guide ─────────────────────────────────────────────────────────

@cli.command("theme-page")
@click.option("--action", required=True,
              type=click.Choice(["roadmap", "niches", "conversion", "tools"]),
              help="What to show: roadmap | niches | conversion | tools")
@click.option("--niche", default="", help="Your niche (for roadmap)")
@click.option("--followers", default=0, help="Current follower count (determines phase)")
def theme_page_cmd(action: str, niche: str, followers: int):
    """Theme page creation, growth, and monetization guide."""
    if action == "roadmap":
        data = theme_page_guide.get_full_roadmap(niche=niche, current_followers=followers)
        _out(data, f"Theme Page Roadmap — {niche or 'Pick a Niche!'}")
    elif action == "niches":
        data = theme_page_guide.get_niche_recommendations()
        _out(data, "Best Niches for Theme Pages")
    elif action == "conversion":
        data = {"conversion_tactics": theme_page_guide.CONVERSION_TACTICS}
        _out(data, "Conversion Tactics — Turn Followers into Revenue")
    elif action == "tools":
        data = {"tools_stack": theme_page_guide.TOOLS_STACK}
        _out(data, "Essential Tools Stack")


# ─── Proactive daily brief ────────────────────────────────────────────────────

@cli.command("daily-brief")
@click.option("--region", default="us", show_default=True)
@click.option("--niche", default="", help="Filter recommendations for your niche")
@click.option("--platforms", default="tiktok,youtube_shorts", show_default=True)
def daily_brief(region: str, niche: str, platforms: str):
    """
    Proactive daily brief: scrape all trends, generate posting plan + hashtags for today.
    Run this every morning before creating content.
    """
    plat_list = [p.strip() for p in platforms.split(",")]
    _status("\n★ DAILY VIRAL TRENDS BRIEF ★", fg="white", bold=True)
    _status(f"Region: {region.upper()} | Niche: {niche or 'All'}", fg="white")
    _status("─" * 50, fg="white")

    _status("Scraping YouTube…", fg="blue")
    yt = youtube_scraper.fetch_trending(region=region, limit=20)
    yt_music = youtube_scraper.fetch_music_trends(region=region, limit=10)

    _status("Scraping TikTok…", fg="magenta")
    tt = tiktok_scraper.fetch_trending(region=region, limit=20)

    _status("Analyzing cross-platform trends…", fg="white")
    hashtags = trend_analyzer.aggregate_hashtags(yt_data=yt, tt_data=tt, top_n=20)
    music = trend_analyzer.aggregate_music(
        yt_music=yt_music.get("music_tracks", []),
        tt_music=tt.get("trending_music", []),
        top_n=10,
    )
    opportunities = trend_analyzer.score_content_opportunity(hashtags, music)

    niche_strat = {}
    if niche:
        niche_strat = trend_analyzer.niche_hashtag_strategy(niche=niche, hashtags=hashtags)

    calendar = account_optimizer.generate_content_calendar(
        niche=niche or "general",
        platforms=plat_list,
        days=1,
        trending_hashtags=hashtags,
        trending_music=music,
    )

    brief = {
        "date": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%d"),
        "region": region.upper(),
        "top_5_hashtags": hashtags[:5],
        "top_3_sounds": music[:3],
        "top_content_opportunities": opportunities["content_opportunities"][:3],
        "todays_posting_plan": calendar["week_calendar"][0] if calendar["week_calendar"] else {},
        "niche_hashtag_strategy": niche_strat.get("strategy", {}) if niche_strat else {},
        "quick_tip": (
            "Use the top sound within 24h — early adopters get the biggest organic push. "
            "Post at peak time, engage for 30 min after, reply to every comment."
        ),
    }

    _out(brief, "Your Daily Brief")


if __name__ == "__main__":
    cli()
