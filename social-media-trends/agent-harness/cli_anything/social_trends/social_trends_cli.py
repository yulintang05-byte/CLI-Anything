#!/usr/bin/env python3
"""Social Media Trends CLI — scrape YouTube & TikTok for viral trends,
optimize accounts, and generate theme page conversion strategies.

Usage:
    # Scrape trending content
    social-trends youtube trending --region US --limit 25
    social-trends tiktok hashtags --region US --period 7
    social-trends tiktok songs --region US --period 7
    social-trends trends merge --niche finance

    # Account optimization
    social-trends account audit --platform tiktok --username myaccount ...
    social-trends account calendar --platform tiktok --niche fitness --days 7
    social-trends account bio --niche finance --platform tiktok

    # Theme page strategy
    social-trends theme niches
    social-trends theme playbook --niche finance
    social-trends theme funnel
    social-trends theme mistakes

    # Score a content idea
    social-trends score --title "5 money mistakes killing your savings" --niche finance
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core import youtube_scraper as yt
from cli_anything.social_trends.core import tiktok_scraper as tt
from cli_anything.social_trends.core import trends_analyzer as ta
from cli_anything.social_trends.core import account_optimizer as ao
from cli_anything.social_trends.core import theme_page as tp
from cli_anything.social_trends.utils.formatters import fmt_table, fmt_list

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
        _pretty_print(data)


def _pretty_print(data, indent: int = 0):
    prefix = "  " * indent
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i + 1}]")
                _pretty_print(item, indent + 1)
            else:
                click.echo(f"{prefix}  {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{click.style(str(k), fg='cyan', bold=True)}:")
                _pretty_print(v, indent + 1)
            else:
                click.echo(f"{prefix}{click.style(str(k), fg='cyan')}: {v}")
    else:
        click.echo(f"{prefix}{data}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EnvironmentError as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": "config_error"}))
            else:
                click.echo(click.style(f"Config Error: {e}", fg="red"), err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(click.style(f"Error: {e}", fg="red"), err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    return wrapper


_repl_mode = False


@click.group()
@click.option("--json", "use_json", is_flag=True, default=False, help="Output as JSON")
def main(use_json: bool):
    """Social Media Trends CLI — viral trends, account optimization, theme page strategy."""
    global _json_output
    _json_output = use_json


# ─── YouTube Commands ─────────────────────────────────────────────────────────

@main.group()
def youtube():
    """YouTube trending data (requires YOUTUBE_API_KEY)."""


@youtube.command("trending")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 region code")
@click.option("--category", default="0", show_default=True, help="YouTube category ID (0=all, 10=music)")
@click.option("--limit", default=25, show_default=True, type=int, help="Number of videos (max 50)")
@handle_error
def yt_trending(region, category, limit):
    """Fetch trending YouTube videos."""
    videos = yt.get_trending_videos(region_code=region, category_id=category, max_results=limit)
    output(videos, f"Top {len(videos)} trending YouTube videos in {region}")


@youtube.command("hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=25, show_default=True, type=int)
@click.option("--top", default=30, show_default=True, type=int, help="Top N hashtags")
@handle_error
def yt_hashtags(region, limit, top):
    """Extract trending hashtags from YouTube trending videos."""
    videos = yt.get_trending_videos(region_code=region, max_results=limit)
    hashtags = yt.extract_trending_hashtags(videos, top_n=top)
    output(hashtags, f"Top {len(hashtags)} trending YouTube hashtags")


@youtube.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=15, show_default=True, type=int)
@handle_error
def yt_music(region, limit):
    """Fetch trending YouTube music videos."""
    videos = yt.get_trending_music_videos(region_code=region, max_results=limit)
    output(videos, f"Top {len(videos)} trending YouTube music videos")


@youtube.command("search-sounds")
@click.argument("query")
@click.option("--limit", default=10, show_default=True, type=int)
@handle_error
def yt_search_sounds(query, limit):
    """Search YouTube for trending sounds matching a query."""
    results = yt.search_trending_sounds(query=query, max_results=limit)
    output(results, f"YouTube sounds matching '{query}'")


# ─── TikTok Commands ──────────────────────────────────────────────────────────

@main.group()
def tiktok():
    """TikTok trending data (Creative Center — no key needed; Research API optional)."""


@tiktok.command("hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=int, help="Days: 7, 30, 120")
@click.option("--limit", default=30, show_default=True, type=int)
@handle_error
def tt_hashtags(region, period, limit):
    """Fetch trending TikTok hashtags (Creative Center — no auth needed)."""
    tags = tt.get_trending_hashtags_cc(region=region, period=period, limit=limit)
    output(tags, f"Top {len(tags)} trending TikTok hashtags ({period}d, {region})")


@tiktok.command("songs")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=int)
@click.option("--limit", default=30, show_default=True, type=int)
@handle_error
def tt_songs(region, period, limit):
    """Fetch trending TikTok songs/sounds (Creative Center — no auth needed)."""
    songs = tt.get_trending_songs_cc(region=region, period=period, limit=limit)
    output(songs, f"Top {len(songs)} trending TikTok songs ({period}d, {region})")


@tiktok.command("creators")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=int)
@click.option("--limit", default=20, show_default=True, type=int)
@handle_error
def tt_creators(region, period, limit):
    """Fetch trending TikTok creators."""
    creators = tt.get_trending_creators_cc(region=region, period=period, limit=limit)
    output(creators, f"Top {len(creators)} trending TikTok creators ({period}d, {region})")


@tiktok.command("videos")
@click.option("--region", default="US", show_default=True)
@click.option("--days", default=7, show_default=True, type=int)
@click.option("--limit", default=20, show_default=True, type=int)
@handle_error
def tt_videos(region, days, limit):
    """Fetch trending TikTok videos (requires TIKTOK_RESEARCH_TOKEN)."""
    videos = tt.get_trending_videos_research(max_results=limit, region=region, days_back=days)
    output(videos, f"TikTok trending videos ({days}d, {region})")


# ─── Cross-Platform Trends ────────────────────────────────────────────────────

@main.group()
def trends():
    """Cross-platform trend analysis — merges YouTube + TikTok signals."""


@trends.command("merge")
@click.option("--region", default="US", show_default=True)
@click.option("--niche", default="", help="Optional niche to include niche-specific tags")
@click.option("--yt-weight", default=0.4, type=float, show_default=True)
@click.option("--tt-weight", default=0.6, type=float, show_default=True)
@handle_error
def trends_merge(region, niche, yt_weight, tt_weight):
    """Merge YouTube + TikTok hashtag signals into a unified ranking."""
    click.echo("Fetching YouTube trending hashtags...", err=True)
    yt_videos = yt.get_trending_videos(region_code=region, max_results=25)
    yt_tags = yt.extract_trending_hashtags(yt_videos)

    click.echo("Fetching TikTok trending hashtags...", err=True)
    tt_tags = tt.get_trending_hashtags_cc(region=region, period=7, limit=30)

    merged = ta.merge_hashtags(yt_tags, tt_tags, yt_weight=yt_weight, tt_weight=tt_weight)
    sets = ta.build_hashtag_sets(merged, niche=niche)

    output(
        {"ranked_hashtags": merged[:25], "hashtag_sets": sets},
        "Cross-platform trending hashtags",
    )


@trends.command("topics")
@click.option("--region", default="US", show_default=True)
@handle_error
def trends_topics(region):
    """Extract trending topics from both platforms."""
    click.echo("Fetching data...", err=True)
    yt_videos = yt.get_trending_videos(region_code=region, max_results=25)
    tt_videos = tt.get_trending_videos_research(max_results=20, region=region)
    topics = ta.identify_trend_topics(yt_videos, tt_videos)
    output(topics, f"Top {len(topics)} trending topics across platforms")


@trends.command("hashtag-sets")
@click.option("--region", default="US", show_default=True)
@click.option("--niche", default="", required=True, help="Your niche (e.g. fitness, finance)")
@handle_error
def trends_hashtag_sets(region, niche):
    """Generate ready-to-paste hashtag sets for your niche."""
    click.echo("Fetching trending data...", err=True)
    yt_videos = yt.get_trending_videos(region_code=region, max_results=25)
    yt_tags = yt.extract_trending_hashtags(yt_videos)
    tt_tags = tt.get_trending_hashtags_cc(region=region, period=7, limit=30)
    merged = ta.merge_hashtags(yt_tags, tt_tags)
    sets = ta.build_hashtag_sets(merged, niche=niche)
    output(sets, f"Hashtag sets for #{niche}")


# ─── Account Optimizer ────────────────────────────────────────────────────────

@main.group()
def account():
    """Account auditing, content calendars, and bio generation."""


@account.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--username", required=True)
@click.option("--bio", default="", help="Current profile bio text")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--posts", default=0, type=int)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--niche", default="", help="Account niche (fitness, finance, beauty...)")
@click.option("--has-link/--no-link", default=True)
@handle_error
def account_audit(platform, username, bio, followers, following, posts,
                  avg_views, avg_likes, avg_comments, niche, has_link):
    """Audit an account and get a prioritized list of improvements."""
    result = ao.audit_account_profile(
        username=username,
        platform=platform,
        bio=bio,
        follower_count=followers,
        following_count=following,
        post_count=posts,
        avg_views=avg_views,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        niche=niche,
        profile_has_link=has_link,
    )
    output(result, f"Account audit: @{username} on {platform}")


@account.command("calendar")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "youtube_shorts", "instagram_reels"]))
@click.option("--niche", required=True)
@click.option("--days", default=7, type=int, show_default=True)
@click.option("--region", default="US", show_default=True)
@handle_error
def account_calendar(platform, niche, days, region):
    """Generate a data-driven content calendar for the next N days."""
    click.echo("Fetching trending data for calendar...", err=True)
    yt_videos = yt.get_trending_videos(region_code=region, max_results=20)
    yt_tags = yt.extract_trending_hashtags(yt_videos)
    tt_tags = tt.get_trending_hashtags_cc(region=region, period=7, limit=20)
    merged = ta.merge_hashtags(yt_tags, tt_tags)
    tt_videos = tt.get_trending_videos_research(max_results=10, region=region)
    topics = ta.identify_trend_topics(yt_videos, tt_videos)
    calendar = ao.generate_content_calendar(
        platform=platform,
        niche=niche,
        trending_hashtags=merged,
        trending_topics=topics,
        days=days,
    )
    output(calendar, f"{days}-day content calendar for #{niche} on {platform}")


@account.command("bio")
@click.option("--niche", required=True)
@click.option("--platform", default="tiktok", show_default=True)
@click.option("--cta-url", default="", help="Your link-in-bio URL")
@handle_error
def account_bio(niche, platform, cta_url):
    """Generate 3 optimized bio templates for your niche."""
    templates = ao.generate_bio_templates(niche=niche, platform=platform, cta_url=cta_url)
    output(
        [{"option": i + 1, "bio": t} for i, t in enumerate(templates)],
        f"Bio templates for #{niche}",
    )


@account.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube"]))
@handle_error
def account_schedule(platform):
    """Show the best posting times for a platform."""
    schedule = ao.BEST_POST_TIMES.get(platform.lower(), {})
    freq = ao.IDEAL_POSTING_FREQUENCY.get(platform.lower(), {})
    output({"best_times": schedule, "ideal_frequency": freq}, f"Optimal posting schedule for {platform}")


# ─── Theme Page Strategy ──────────────────────────────────────────────────────

@main.group()
def theme():
    """Theme page strategy — niches, conversion funnels, 90-day roadmaps."""


@theme.command("niches")
@handle_error
def theme_niches():
    """Rank profitable niches by trend score and monetization potential."""
    niches = tp.list_profitable_niches()
    output(niches, "Profitable niches ranked by trend score")


@theme.command("playbook")
@click.option("--niche", required=True, help="e.g. finance, fitness, tech, beauty, luxury_lifestyle")
@handle_error
def theme_playbook(niche):
    """Full monetization + growth playbook for a niche."""
    playbook = tp.get_niche_playbook(niche)
    output(playbook, f"Theme page playbook: {niche}")


@theme.command("funnel")
@click.option("--niche", default="", help="Optional niche for context")
@handle_error
def theme_funnel(niche):
    """Show the 6-stage conversion funnel (viewer → buyer)."""
    funnel = tp.get_conversion_funnel(niche)
    output(funnel, "Conversion funnel: viewer → buyer")


@theme.command("mistakes")
@handle_error
def theme_mistakes():
    """List the most common theme page mistakes to avoid."""
    mistakes = tp.get_mistakes_to_avoid()
    output(mistakes, "Common theme page mistakes (avoid these)")


# ─── Content Scoring ──────────────────────────────────────────────────────────

@main.command("score")
@click.option("--title", required=True, help="Content title or idea to score")
@click.option("--niche", default="", help="Your niche for context")
@click.option("--region", default="US", show_default=True)
@handle_error
def score_content(title, niche, region):
    """Score a content idea against current trends (0-100)."""
    click.echo("Fetching trend data for scoring...", err=True)
    yt_videos = yt.get_trending_videos(region_code=region, max_results=20)
    yt_tags = yt.extract_trending_hashtags(yt_videos)
    tt_tags = tt.get_trending_hashtags_cc(region=region, period=7, limit=20)
    merged = ta.merge_hashtags(yt_tags, tt_tags)
    tt_videos = tt.get_trending_videos_research(max_results=10, region=region)
    topics = ta.identify_trend_topics(yt_videos, tt_videos)
    result = ta.score_content_idea(title, merged, topics)
    output(result, f"Trend score for: '{title}'")


if __name__ == "__main__":
    main()
