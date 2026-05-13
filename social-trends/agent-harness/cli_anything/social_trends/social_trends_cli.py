#!/usr/bin/env python3
"""Social Trends CLI — Scrape viral trends, optimize accounts, and grow theme pages.

Commands:
    social-trends trends youtube        Fetch YouTube trending videos
    social-trends trends tiktok         Fetch TikTok trending videos
    social-trends trends report         Full cross-platform trend report

    social-trends hashtags suggest      Generate optimized hashtag set for a niche
    social-trends hashtags analyze      Analyze a list of hashtags
    social-trends hashtags cross        Cross-platform hashtag strategy

    social-trends music trending        Fetch trending viral music
    social-trends music recommend       Recommend music for your content type
    social-trends music calendar        Weekly music-content pairing calendar

    social-trends account schedule      Generate optimal posting schedule
    social-trends account audit         Audit your account for optimization gaps
    social-trends account bio           Generate optimized bio template
    social-trends account pillars       Define content pillars for your niche

    social-trends theme-page niches     List all profitable theme page niches
    social-trends theme-page guide      Full guide for a specific niche
    social-trends theme-page funnel     Conversion funnel strategy
    social-trends theme-page sop        Daily/weekly SOP for running a theme page
"""

import json
import sys
import click


def _out(data, json_mode: bool, message: str = ""):
    """Output data in JSON or human-readable format."""
    if json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
        return
    if message:
        click.echo(f"\n{message}\n" + "=" * 60)
    _render(data)


def _render(data, indent: int = 0):
    prefix = "  " * indent
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _render(item, indent)
                click.echo()
            else:
                click.echo(f"{prefix}• {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{click.style(str(k), bold=True)}:")
                _render(v, indent + 1)
            else:
                click.echo(f"{prefix}{click.style(str(k), bold=True)}: {v}")
    else:
        click.echo(f"{prefix}{data}")


# ─── Root ──────────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "json_mode", is_flag=True, default=False, help="Output as JSON")
@click.pass_context
def main(ctx, json_mode: bool):
    """Social Trends CLI — Viral trend scraping, account optimization & theme page growth."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_mode


# ─── Trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends():
    """Scrape trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", "-c", default="now",
              type=click.Choice(["now", "music", "gaming", "movies"]),
              help="Trending category")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--hashtags", is_flag=True, default=False, help="Show aggregated hashtags")
@click.pass_context
def trends_youtube(ctx, category, limit, hashtags):
    """Fetch YouTube trending videos and extract viral signals."""
    json_mode = ctx.obj["json"]
    click.echo(f"Fetching YouTube trending ({category})...", err=True)

    from cli_anything.social_trends.core.youtube import fetch_trending_best, extract_top_hashtags
    try:
        videos = fetch_trending_best(category=category, limit=limit)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if not videos:
        click.echo("No videos found. YouTube may have rate-limited the request.", err=True)
        sys.exit(1)

    if hashtags:
        tags = extract_top_hashtags(videos)
        _out(tags, json_mode, f"Top Hashtags from YouTube Trending ({category})")
    else:
        _out([v.to_dict() for v in videos], json_mode,
             f"YouTube Trending — {category.title()} ({len(videos)} videos)")


@trends.command("tiktok")
@click.option("--limit", "-n", default=20, help="Number of results")
@click.option("--hashtags", is_flag=True, default=False, help="Show aggregated hashtags")
@click.option("--sounds", is_flag=True, default=False, help="Show trending sounds instead")
@click.pass_context
def trends_tiktok(ctx, limit, hashtags, sounds):
    """Fetch TikTok trending videos, sounds, and viral signals."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.tiktok import (
        fetch_trending, fetch_trending_sounds, extract_top_hashtags
    )

    if sounds:
        click.echo("Fetching TikTok trending sounds...", err=True)
        tracks = fetch_trending_sounds(limit=limit)
        _out([t.to_dict() for t in tracks], json_mode, f"TikTok Trending Sounds (Top {len(tracks)})")
        return

    click.echo("Fetching TikTok trending videos...", err=True)
    try:
        videos = fetch_trending(limit=limit)
    except Exception as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if hashtags and videos:
        tags = extract_top_hashtags(videos)
        _out(tags, json_mode, "Top Hashtags from TikTok Trending")
    else:
        if videos:
            _out([v.to_dict() for v in videos], json_mode,
                 f"TikTok Trending Videos ({len(videos)} videos)")
        else:
            # TikTok API blocked — return trending hashtags as fallback
            click.echo("TikTok direct API unavailable (IP/region block). Returning trending hashtags instead.", err=True)
            from cli_anything.social_trends.core.tiktok import fetch_trending_hashtags
            tags = fetch_trending_hashtags(limit=limit)
            _out([t.to_dict() for t in tags], json_mode, "TikTok Trending Hashtags (fallback)")


@trends.command("report")
@click.option("--niche", "-n", default="", help="Filter trends for a specific niche")
@click.pass_context
def trends_report(ctx, niche):
    """Generate a full cross-platform viral trend report."""
    json_mode = ctx.obj["json"]
    click.echo("Generating cross-platform trend report...", err=True)

    from cli_anything.social_trends.core.youtube import fetch_trending_best, extract_top_hashtags as yt_tags
    from cli_anything.social_trends.core.tiktok import fetch_trending_sounds, fetch_trending_hashtags
    from cli_anything.social_trends.core.music import fetch_trending_music

    report = {}

    try:
        yt_videos = fetch_trending_best(limit=10)
        report["youtube_trending"] = [v.to_dict() for v in yt_videos[:5]]
        report["youtube_top_hashtags"] = yt_tags(yt_videos, top_n=10)
    except Exception as exc:
        report["youtube_trending"] = []
        report["youtube_error"] = str(exc)

    try:
        tiktok_hashtags = fetch_trending_hashtags(niche=niche or None, limit=15)
        report["tiktok_top_hashtags"] = [t.to_dict() for t in tiktok_hashtags]
    except Exception as exc:
        report["tiktok_top_hashtags"] = []
        report["tiktok_error"] = str(exc)

    trending_sounds = fetch_trending_sounds(limit=5)
    report["trending_music"] = [t.to_dict() for t in trending_sounds]

    if niche:
        from cli_anything.social_trends.core.hashtags import generate_hashtag_set
        hs = generate_hashtag_set(niche, "tiktok")
        report["recommended_hashtag_set"] = hs.to_dict()
        report["niche"] = niche

    _out(report, json_mode, "Cross-Platform Viral Trend Report")


# ─── Hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags():
    """Generate and analyze hashtag strategies."""


@hashtags.command("suggest")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "linkedin"]),
              help="Target platform")
@click.option("--no-viral", is_flag=True, default=False, help="Exclude viral mega-tags (#fyp etc)")
@click.option("--add", multiple=True, help="Add custom tags to the set")
@click.pass_context
def hashtags_suggest(ctx, niche, platform, no_viral, add):
    """Generate an optimized hashtag set for NICHE on PLATFORM."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.hashtags import generate_hashtag_set
    result = generate_hashtag_set(
        niche=niche,
        platform=platform,
        include_viral=not no_viral,
        custom_tags=list(add) if add else None,
    )
    _out(result.to_dict(), json_mode, f"Optimized Hashtag Set — {niche} on {platform}")


@hashtags.command("analyze")
@click.argument("tags", nargs=-1, required=True)
@click.option("--platform", "-p", default="tiktok")
@click.pass_context
def hashtags_analyze(ctx, tags, platform):
    """Analyze TAGS and get optimization recommendations."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.hashtags import analyze_hashtags
    results = analyze_hashtags(list(tags), platform=platform)
    _out([r.to_dict() for r in results], json_mode, f"Hashtag Analysis — {platform}")


@hashtags.command("cross")
@click.argument("niche")
@click.pass_context
def hashtags_cross(ctx, niche):
    """Generate a cross-platform hashtag strategy for NICHE."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.hashtags import cross_platform_strategy
    result = cross_platform_strategy(niche)
    _out(result, json_mode, f"Cross-Platform Hashtag Strategy — {niche}")


# ─── Music ─────────────────────────────────────────────────────────────────────

@main.group()
def music():
    """Track viral music and sounds across platforms."""


@music.command("trending")
@click.option("--platform", "-p", default="all", help="Platform filter (tiktok, youtube, all)")
@click.option("--genre", "-g", default="all", help="Genre filter")
@click.option("--limit", "-n", default=10, help="Number of results")
@click.pass_context
def music_trending(ctx, platform, genre, limit):
    """Show currently trending viral tracks."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.music import fetch_trending_music
    tracks = fetch_trending_music(platform=platform, genre=genre, limit=limit)
    _out([t.to_dict() for t in tracks], json_mode, f"Viral Trending Music (Top {len(tracks)})")


@music.command("recommend")
@click.argument("content_type")
@click.option("--mood", "-m", default="", help="Content mood (upbeat, emotional, energetic, etc.)")
@click.pass_context
def music_recommend(ctx, content_type, mood):
    """Recommend the best trending music for CONTENT_TYPE."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.music import recommend_music_for_content
    tracks = recommend_music_for_content(content_type, mood=mood)
    if not tracks:
        click.echo(f"No specific recommendations for '{content_type}'. Try: GRWM, workout, tutorial, dance, travel")
        sys.exit(1)
    _out([t.to_dict() for t in tracks], json_mode, f"Best Trending Music for '{content_type}'")


@music.command("calendar")
@click.argument("niche")
@click.pass_context
def music_calendar(ctx, niche):
    """Generate a weekly music-content pairing calendar for NICHE."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.music import music_content_calendar
    calendar = music_content_calendar(niche)
    _out(calendar, json_mode, f"Weekly Music-Content Calendar — {niche}")


# ─── Account ───────────────────────────────────────────────────────────────────

@main.group()
def account():
    """Optimize your social media accounts."""


@account.command("schedule")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              help="Platform to optimize for")
@click.option("--posts-per-week", "-n", default=7, help="Target posts per week")
@click.option("--niche", default="general", help="Your content niche")
@click.pass_context
def account_schedule(ctx, platform, posts_per_week, niche):
    """Generate an optimal posting schedule for PLATFORM."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.account import generate_posting_schedule
    slots = generate_posting_schedule(platform=platform, posts_per_week=posts_per_week, niche=niche)
    _out([s.to_dict() for s in slots], json_mode,
         f"Optimal Posting Schedule — {platform.title()} ({posts_per_week} posts/week)")


@account.command("audit")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--posts", default=0, type=int, help="Total posts on account")
@click.option("--avg-views", default=0, type=int, help="Average views per post")
@click.option("--bio/--no-bio", default=False, help="Bio is filled")
@click.option("--pic/--no-pic", default=False, help="Profile picture is set")
@click.option("--link/--no-link", default=False, help="Link in bio is set")
@click.option("--posts-per-week", default=0.0, type=float, help="Current posting frequency")
@click.option("--uses-hashtags/--no-hashtags", default=False)
@click.option("--uses-audio/--no-audio", default=False, help="Uses trending audio")
@click.pass_context
def account_audit(ctx, platform, followers, posts, avg_views, bio, pic, link,
                  posts_per_week, uses_hashtags, uses_audio):
    """Audit your account and get prioritized optimization recommendations."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.account import audit_account
    result = audit_account(
        platform=platform,
        followers=followers,
        posts=posts,
        avg_views=avg_views,
        bio_filled=bio,
        profile_pic=pic,
        link_in_bio=link,
        posts_per_week=posts_per_week,
        uses_hashtags=uses_hashtags,
        uses_trending_audio=uses_audio,
    )
    _out(result.to_dict(), json_mode, f"Account Audit — {platform.title()}")


@account.command("bio")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--cta", default="link",
              type=click.Choice(["link", "follow", "dm", "shop"]),
              help="Call-to-action type")
@click.pass_context
def account_bio(ctx, niche, platform, cta):
    """Generate an optimized bio template for NICHE on PLATFORM."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.account import generate_bio
    bio = generate_bio(platform=platform, niche=niche, cta_type=cta)
    _out(bio.to_dict(), json_mode, f"Optimized Bio Template — {niche} on {platform}")


@account.command("pillars")
@click.argument("niche")
@click.option("--posts-per-week", "-n", default=5, type=int)
@click.pass_context
def account_pillars(ctx, niche, posts_per_week):
    """Define content pillars for NICHE."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.account import content_pillars
    result = content_pillars(niche=niche, posts_per_week=posts_per_week)
    _out(result, json_mode, f"Content Pillars — {niche} ({posts_per_week} posts/week)")


# ─── Theme Page ────────────────────────────────────────────────────────────────

@main.group("theme-page")
def theme_page():
    """Create, grow, and monetize theme pages."""


@theme_page.command("niches")
@click.option("--sort", default="monetization",
              type=click.Choice(["monetization", "difficulty", "competition", "speed"]),
              help="Sort niches by metric")
@click.option("--difficulty", default="all",
              type=click.Choice(["all", "Beginner", "Intermediate", "Advanced"]))
@click.option("--platform", default="all", help="Filter by platform")
@click.pass_context
def theme_page_niches(ctx, sort, difficulty, platform):
    """List all profitable theme page niches ranked by your criteria."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.theme_pages import list_niches
    niches = list_niches(sort_by=sort, difficulty=difficulty, platform=platform)
    _out([n.to_dict() for n in niches], json_mode,
         f"Theme Page Niches — sorted by {sort} ({len(niches)} niches)")


@theme_page.command("guide")
@click.argument("niche")
@click.pass_context
def theme_page_guide(ctx, niche):
    """Get a complete growth and monetization guide for NICHE."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.theme_pages import get_niche_guide
    result = get_niche_guide(niche)
    _out(result, json_mode, f"Theme Page Guide — {niche}")


@theme_page.command("funnel")
@click.option("--niche", default="general", help="Your content niche")
@click.pass_context
def theme_page_funnel(ctx, niche):
    """Show the full follower → customer conversion funnel."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.theme_pages import conversion_funnel
    stages = conversion_funnel(niche=niche)
    _out([s.to_dict() for s in stages], json_mode,
         f"Conversion Funnel — {niche}")


@theme_page.command("sop")
@click.option("--niche", default="general", help="Your content niche")
@click.pass_context
def theme_page_sop(ctx, niche):
    """Get a complete daily/weekly Standard Operating Procedure for your theme page."""
    json_mode = ctx.obj["json"]

    from cli_anything.social_trends.core.theme_pages import theme_page_sop
    result = theme_page_sop(niche=niche)
    _out(result, json_mode, f"Theme Page SOP — {niche}")


if __name__ == "__main__":
    main()
