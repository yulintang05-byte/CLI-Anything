#!/usr/bin/env python3
"""Social Media CLI — Viral trend scraping, account optimization, theme page intelligence.

Usage:
    social-cli trends youtube --region US
    social-cli trends tiktok --type hashtags
    social-cli trends cross-platform

    social-cli account add @myhandle --platform tiktok --niche fitness
    social-cli account audit @myhandle --platform tiktok
    social-cli account list

    social-cli theme-page list
    social-cli theme-page guide --niche motivation_luxury
    social-cli theme-page full-guide

    social-cli hashtags strategy --niche fitness --platform tiktok
    social-cli schedule --platform tiktok
"""

import json
import sys
import click

from cli_anything.social_media.core import trends as tr
from cli_anything.social_media.core import account_optimizer as ao
from cli_anything.social_media.core import theme_pages as tp
from cli_anything.social_media.core import account_manager as am

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
        _pretty(data)


def _pretty(data, indent=0):
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}\033[1m{k}:\033[0m")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{prefix}\033[1m{k}:\033[0m {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                click.echo(f"{prefix}[{i}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{prefix}• {item}")
    else:
        click.echo(f"{prefix}{data}")


@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON")
def cli(json_out):
    """Social Media CLI — Trend scraping, account optimization, theme pages."""
    global _json_output
    _json_output = json_out


# ─── TRENDS ───────────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", default="all", help="all, music, gaming, film, entertainment, howto")
@click.option("--region", default="US", help="Country code (US, GB, IN, ...)")
@click.option("--max", "max_results", default=20, type=int)
@click.option("--type", "trend_type", default="videos", help="videos, hashtags, music")
def youtube_trends(category, region, max_results, trend_type):
    """Fetch YouTube trending content."""
    if trend_type == "hashtags":
        result = tr.youtube_trending_hashtags(region=region)
        output(result, f"YouTube Trending Hashtags ({region})")
    elif trend_type == "music":
        result = tr.youtube_trending_music(region=region, max_results=max_results)
        output(result, f"YouTube Music Trending ({region})")
    else:
        result = tr.youtube_trending(category=category, region=region, max_results=max_results)
        output(result, f"YouTube Trending Videos — {category.upper()} ({region})")


@trends.command("tiktok")
@click.option("--region", default="US", help="Country code")
@click.option("--type", "trend_type", default="hashtags", help="hashtags, music, videos")
@click.option("--max", "max_results", default=20, type=int)
def tiktok_trends(region, trend_type, max_results):
    """Fetch TikTok trending content."""
    if trend_type == "music":
        result = tr.tiktok_trending_music(region=region)
        output(result, f"TikTok Trending Music ({region})")
    elif trend_type == "videos":
        result = tr.tiktok_trending_videos(region=region, max_results=max_results)
        output(result, f"TikTok Trending Videos ({region})")
    else:
        result = tr.tiktok_trending_hashtags(region=region)
        output(result, f"TikTok Trending Hashtags ({region})")


@trends.command("cross-platform")
@click.option("--region", default="US", help="Country code")
def cross_platform(region):
    """Aggregate trends across YouTube + TikTok to find cross-platform viral content."""
    result = tr.cross_platform_trends(region=region)
    output(result, f"Cross-Platform Trends ({region})")


# ─── HASHTAGS ─────────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag strategy and analysis."""


@hashtags.command("strategy")
@click.option("--niche", required=True, help="Your content niche (fitness, finance, travel, ...)")
@click.option("--platform", default="tiktok", help="tiktok, youtube, instagram")
def hashtag_strategy(niche, platform):
    """Generate optimal hashtag strategy for your niche."""
    result = ao.hashtag_strategy(niche, platform)
    output(result, f"Hashtag Strategy: {niche} on {platform}")


@hashtags.command("trending")
@click.option("--platform", default="tiktok", help="tiktok or youtube")
@click.option("--region", default="US")
def trending_hashtags(platform, region):
    """Fetch currently trending hashtags."""
    if platform == "youtube":
        result = tr.youtube_trending_hashtags(region=region)
    else:
        result = tr.tiktok_trending_hashtags(region=region)
    output(result, f"Trending Hashtags on {platform} ({region})")


# ─── ACCOUNT ──────────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Manage and optimize social media accounts."""


@account.command("add")
@click.argument("handle")
@click.option("--platform", required=True, help="tiktok, youtube, instagram")
@click.option("--niche", default="", help="Content niche")
@click.option("--bio", default="", help="Current bio text")
@click.option("--followers", default=0, type=int)
@click.option("--notes", default="")
def account_add(handle, platform, niche, bio, followers, notes):
    """Register a social media account for tracking."""
    handle = handle.lstrip("@")
    result = am.add_account(handle, platform, niche, bio, followers, notes)
    output(result, f"Account Added: @{handle} on {platform}")


@account.command("list")
def account_list():
    """List all registered accounts."""
    result = am.list_accounts()
    output(result, "All Registered Accounts")


@account.command("audit")
@click.argument("handle")
@click.option("--platform", required=True, help="tiktok, youtube, instagram")
@click.option("--bio", default="", help="Current bio text (or pull from registered account)")
@click.option("--niche", default="")
@click.option("--followers", default=0, type=int)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
def account_audit(handle, platform, bio, niche, followers, avg_views, avg_likes):
    """Run full optimization audit on an account."""
    handle = handle.lstrip("@")
    # Pull stored account data if bio not provided
    if not bio:
        stored = am.get_account(handle, platform)
        if "error" not in stored:
            bio = stored.get("bio", "")
            niche = niche or stored.get("niche", "")
            followers = followers or stored.get("followers", 0)
    result = ao.full_account_audit(
        handle=handle, bio=bio, platform=platform,
        niche=niche, followers=followers,
        avg_views=avg_views, avg_likes=avg_likes,
    )
    output(result, f"Account Audit: @{handle} ({platform})")


@account.command("update-metrics")
@click.argument("handle")
@click.option("--platform", required=True)
@click.option("--followers", default=None, type=int)
@click.option("--avg-views", default=None, type=int)
@click.option("--avg-likes", default=None, type=int)
def account_update(handle, platform, followers, avg_views, avg_likes):
    """Log a metrics snapshot for growth tracking."""
    handle = handle.lstrip("@")
    result = am.update_metrics(handle, platform, followers, avg_views, avg_likes)
    output(result, f"Metrics Updated: @{handle} ({platform})")


@account.command("remove")
@click.argument("handle")
@click.option("--platform", required=True)
def account_remove(handle, platform):
    """Remove an account from tracking."""
    handle = handle.lstrip("@")
    result = am.remove_account(handle, platform)
    output(result, f"Account Removed: @{handle} ({platform})")


@account.command("optimize-all")
def account_optimize_all():
    """Run optimization audit on all registered accounts."""
    all_accounts = am.list_accounts()
    results = []
    for acct in all_accounts.get("accounts", []):
        stored = am.get_account(acct["handle"], acct["platform"])
        audit = ao.full_account_audit(
            handle=acct["handle"],
            bio=stored.get("bio", ""),
            platform=acct["platform"],
            niche=acct.get("niche", ""),
            followers=acct.get("followers", 0),
        )
        results.append({"account": f"@{acct['handle']} ({acct['platform']})", "audit": audit})
    output({"optimized": len(results), "results": results}, "All Accounts Optimized")


# ─── SCHEDULE ─────────────────────────────────────────────────────────────────

@cli.command("schedule")
@click.option("--platform", required=True, help="tiktok, youtube, instagram")
@click.option("--timezone", default="EST")
def posting_schedule(platform, timezone):
    """Get optimized posting schedule for a platform."""
    result = ao.optimize_posting_schedule(platform, timezone)
    output(result, f"Optimal Posting Schedule: {platform} ({timezone})")


# ─── THEME PAGES ──────────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page strategy: how to build and monetize converting pages."""


@theme_page.command("list")
def theme_list():
    """List all available theme page niches with profitability data."""
    result = tp.list_niches()
    output(result, "Available Theme Page Niches")


@theme_page.command("guide")
@click.option("--niche", required=True, help="Niche key (e.g. motivation_luxury, finance_mindset)")
def theme_guide(niche):
    """Get full playbook for a specific theme page niche."""
    result = tp.get_niche_playbook(niche)
    output(result, f"Theme Page Playbook: {niche}")


@theme_page.command("full-guide")
def theme_full():
    """Complete theme page guide: all niches, conversion funnels, monetization roadmap."""
    result = tp.full_theme_page_guide()
    output(result, "Complete Theme Page Guide")


@theme_page.command("monetize")
def theme_monetize():
    """Step-by-step monetization roadmap from 0 to $10K/month."""
    result = {
        "monetization_roadmap": tp.MONETIZATION_ROADMAP,
        "tools_stack": tp.TOOLS_STACK,
        "conversion_playbook": tp.CONVERSION_PLAYBOOK,
    }
    output(result, "Monetization Roadmap")


if __name__ == "__main__":
    cli()
