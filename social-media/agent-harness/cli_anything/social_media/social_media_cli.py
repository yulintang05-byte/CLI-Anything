#!/usr/bin/env python3
"""Social Media CLI — Viral trend scraping, account optimization, and theme page conversion.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Optimizes social media accounts with 2026 algorithm strategies.
Provides a complete theme page creation and monetization framework.

Usage:
    # Scrape YouTube trending
    python3 -m cli_anything.social_media trends youtube --category music --limit 20

    # Scrape TikTok trending hashtags
    python3 -m cli_anything.social_media trends tiktok --niche fitness --limit 30

    # Analyze cross-platform trends
    python3 -m cli_anything.social_media trends analyze --niche business

    # Audit an account
    python3 -m cli_anything.social_media optimize audit --platform tiktok --username @myaccount --followers 5000 --avg-views 1200 --niche fitness

    # Create a theme page plan
    python3 -m cli_anything.social_media theme create --niche finance --archetype educator

    # Generate content calendar
    python3 -m cli_anything.social_media theme calendar --niche business --weeks 4

    # List profitable niches
    python3 -m cli_anything.social_media theme niches

    # Interactive REPL
    python3 -m cli_anything.social_media repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.core.session import Session
from cli_anything.social_media.core import youtube_scraper as yt
from cli_anything.social_media.core import tiktok_scraper as tt
from cli_anything.social_media.core import trend_analyzer as analyzer
from cli_anything.social_media.core import account_optimizer as optimizer
from cli_anything.social_media.core import theme_page as theme_page_mod

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


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
            click.echo(f"{prefix}  {item}")


# ---------------------------------------------------------------------------
# Main group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON for agent consumption.")
@click.pass_context
def main(ctx, json_out):
    """Social Media CLI — trend scraping, account optimization, and theme page conversion."""
    global _json_output
    _json_output = json_out
    ctx.ensure_object(dict)


# ---------------------------------------------------------------------------
# TRENDS commands
# ---------------------------------------------------------------------------

@main.group()
def trends():
    """Scrape and analyze viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", default="now", type=click.Choice(["now", "music", "gaming", "movies"]),
              help="Trending category to scrape.")
@click.option("--limit", default=25, type=int, help="Maximum videos to return.")
@click.option("--use-ytdlp", is_flag=True, help="Use yt-dlp backend instead of direct scrape.")
@click.option("--region", default="US", help="Country code for regional trends.")
@click.option("--save", default="", help="Save results to JSON file at this path.")
def trends_youtube(category, limit, use_ytdlp, region, save):
    """Scrape YouTube trending videos, hashtags, and viral signals."""
    click.echo(f"Scraping YouTube trending ({category})...", err=True)
    result = yt.scrape_trending(
        category=category,
        region=region,
        limit=limit,
        use_ytdlp=use_ytdlp,
    )
    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"Saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== YouTube Trending ({category.upper()}) ===")
        click.echo(f"Videos found: {result['total_videos']}  |  Method: {result['method']}")
        click.echo(f"\nTop Hashtags:")
        for h in result["top_hashtags"][:10]:
            click.echo(f"  {h['tag']:25s} ({h['count']} appearances)")
        click.echo(f"\nTop Videos:")
        for i, v in enumerate(result["videos"][:10], 1):
            tags = " ".join(v.get("hashtags", [])[:3])
            click.echo(f"  {i:2d}. {v['title'][:55]:<55s} | {v['channel'][:25]} | {v['views']}")
            if tags:
                click.echo(f"       Tags: {tags}")
        if result.get("error"):
            click.echo(f"\nWarning: {result['error']}", err=True)
    else:
        output(result)


@trends.command("tiktok")
@click.option("--niche", default="", help="Filter hashtags by niche (fitness, beauty, business, etc.).")
@click.option("--limit", default=30, type=int, help="Maximum hashtags to return.")
@click.option("--live/--no-live", default=True, help="Attempt live scrape (falls back to curated list).")
@click.option("--save", default="", help="Save results to JSON file at this path.")
def trends_tiktok(niche, limit, live, save):
    """Scrape TikTok trending hashtags and viral sounds."""
    click.echo("Scraping TikTok trends...", err=True)
    result = tt.scrape_trending_hashtags(live=live, niche=niche, limit=limit)
    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"Saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== TikTok Trending Hashtags ===")
        click.echo(f"Method: {result['method']}  |  Total: {result['total']}")
        if niche:
            click.echo(f"Filter: {niche}")
        click.echo()
        for i, h in enumerate(result["hashtags"][:20], 1):
            cat = h.get("category", "")
            views = h.get("avg_views", "")
            click.echo(f"  {i:2d}. {h['hashtag']:25s} {cat:15s} {views}")
        if result["trending_sounds"]:
            click.echo(f"\nTrending Sounds:")
            for s in result["trending_sounds"][:5]:
                click.echo(f"  - {s.get('title', '')} by {s.get('author', '')}")
        if result.get("tip"):
            click.echo(f"\nTip: {result['tip']}")
    else:
        output(result)


@trends.command("hashtag")
@click.argument("hashtag")
@click.option("--limit", default=20, type=int, help="Max videos to fetch.")
def trends_hashtag(hashtag, limit):
    """Fetch videos and stats for a specific TikTok hashtag."""
    click.echo(f"Fetching TikTok videos for #{hashtag.lstrip('#')}...", err=True)
    result = tt.scrape_hashtag_videos(hashtag, limit=limit)
    if not _json_output:
        click.echo(f"\n=== #{hashtag.lstrip('#')} ===")
        click.echo(f"Videos found: {result['video_count']}")
        for i, v in enumerate(result["videos"][:10], 1):
            views = v.get("views", "")
            desc = v.get("title", v.get("description", ""))[:50]
            music = v.get("music_title", "")
            click.echo(f"  {i:2d}. {desc:<52s} | {views} views")
            if music:
                click.echo(f"       Sound: {music}")
    else:
        output(result)


@trends.command("analyze")
@click.option("--niche", default="", help="Focus analysis on a specific niche.")
@click.option("--yt-category", default="now", type=click.Choice(["now", "music", "gaming", "movies"]))
@click.option("--limit", default=20, type=int)
@click.option("--save", default="", help="Save merged analysis to JSON file.")
def trends_analyze(niche, yt_category, limit, save):
    """Cross-platform trend analysis: merge YouTube + TikTok for maximum signal."""
    click.echo("Fetching YouTube trends...", err=True)
    yt_data = yt.scrape_trending(category=yt_category, limit=limit)
    click.echo("Fetching TikTok trends...", err=True)
    tt_data = tt.scrape_trending_hashtags(niche=niche, limit=40)
    click.echo("Merging and analyzing...", err=True)
    merged = analyzer.merge_platform_trends(yt_data, tt_data)

    if save:
        with open(save, "w") as f:
            json.dump(merged, f, indent=2, default=str)
        click.echo(f"Saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== Cross-Platform Trend Analysis ===")
        click.echo(f"Total tags analyzed: {merged['total_tags_analyzed']}")

        click.echo(f"\nCross-Platform Hits (both YT + TikTok):")
        for h in merged["cross_platform_hits"][:8]:
            score = h["virality_score"]
            click.echo(f"  {h['hashtag']:25s} score={score:5.1f}  yt={h['yt_appearances']}  tt={h['tt_appearances']}")

        click.echo(f"\nTop Overall Hashtags (by virality score):")
        for h in merged["top_hashtags"][:10]:
            platforms = ("YT+TT" if h["cross_platform"] else ("YT" if h["on_youtube"] else "TT"))
            click.echo(f"  {h['hashtag']:25s} {platforms:6s} score={h['virality_score']:5.1f}")

        mix = merged["recommended_hashtag_mix"]
        click.echo(f"\nRecommended Hashtag Mix:")
        click.echo(f"  {' '.join(mix['hashtags'])}")
        click.echo(f"\nStrategy: {mix['strategy']}")
        click.echo(f"Posting: {mix['posting_frequency']}")

        if merged["content_signals"]:
            click.echo(f"\nContent Format Signals:")
            for sig in merged["content_signals"][:5]:
                click.echo(f"  {sig['format']:20s} ({sig['trending_videos']} videos)")
                click.echo(f"    → {sig['recommendation']}")
    else:
        output(merged)


@trends.command("video")
@click.argument("url")
def trends_video(url):
    """Get detailed metadata and hashtags for a YouTube video URL."""
    click.echo(f"Fetching video data...", err=True)
    result = yt.get_video_details(url)
    if not _json_output:
        click.echo(f"\nTitle:    {result.get('title')}")
        click.echo(f"Channel:  {result.get('channel')}")
        click.echo(f"Views:    {result.get('views', 0):,}")
        click.echo(f"Likes:    {result.get('likes', 0):,}")
        click.echo(f"Tags:     {' '.join(result.get('hashtags', []))}")
        click.echo(f"Keywords: {' | '.join(result.get('tags', [])[:10])}")
    else:
        output(result)


# ---------------------------------------------------------------------------
# OPTIMIZE commands
# ---------------------------------------------------------------------------

@main.group()
def optimize():
    """Audit and optimize social media accounts with 2026 algorithm strategies."""


@optimize.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube_shorts", "youtube_long", "instagram_reels"]))
@click.option("--username", required=True, help="Account username or handle.")
@click.option("--followers", default=0, type=int, help="Follower count.")
@click.option("--avg-views", default=0, type=int, help="Average views per post.")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post.")
@click.option("--avg-comments", default=0, type=int, help="Average comments per post.")
@click.option("--avg-shares", default=0, type=int, help="Average shares per post.")
@click.option("--avg-saves", default=0, type=int, help="Average saves per post.")
@click.option("--posts-per-week", default=3, type=int, help="How many posts per week.")
@click.option("--niche", default="", help="Content niche.")
@click.option("--bio-cta/--no-bio-cta", default=False, help="Does the bio have a CTA?")
@click.option("--link-in-bio/--no-link-in-bio", default=False, help="Is there a link in bio?")
@click.option("--save", default="", help="Save audit to JSON file.")
def optimize_audit(platform, username, followers, avg_views, avg_likes, avg_comments,
                   avg_shares, avg_saves, posts_per_week, niche, bio_cta, link_in_bio, save):
    """Run a full account audit with optimization recommendations."""
    click.echo(f"Auditing @{username} on {platform}...", err=True)
    result = optimizer.audit_account(
        platform=platform,
        username=username,
        followers=followers,
        avg_views=avg_views,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        avg_shares=avg_shares,
        avg_saves=avg_saves,
        posts_per_week=posts_per_week,
        niche=niche,
        bio_has_cta=bio_cta,
        has_link_in_bio=link_in_bio,
    )
    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"Saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== Account Audit: @{username} ({platform}) ===")
        click.echo(f"Health Score:  {result['health_score']}/100")
        click.echo(f"Grade:         {result['grade']}")

        if result["strengths"]:
            click.echo(f"\nStrengths:")
            for s in result["strengths"]:
                click.echo(f"  + {s}")

        if result["issues"]:
            click.echo(f"\nIssues (by priority):")
            for issue in result["issues"]:
                priority_icon = {"critical": "!!!", "high": "!! ", "medium": "!  ", "low": "   "}.get(issue["priority"], "   ")
                click.echo(f"  [{priority_icon}] {issue['issue']}")
                click.echo(f"        {issue['detail']}")
                click.echo(f"        Fix: {issue['fix']}")

        if result["recommendations"]:
            click.echo(f"\nTop Recommendations:")
            for i, rec in enumerate(result["recommendations"][:3], 1):
                click.echo(f"  {i}. {rec}")

        times = result.get("posting_times", {})
        if times:
            click.echo(f"\nBest Posting Times:")
            note = times.pop("note", "")
            for day, slots in list(times.items())[:3]:
                if isinstance(slots, list):
                    click.echo(f"  {day}: {', '.join(slots)}")
            if note:
                click.echo(f"  Note: {note}")
    else:
        output(result)


@optimize.command("signals")
@click.argument("platform", type=click.Choice(["tiktok", "youtube_shorts", "youtube_long", "instagram_reels"]))
def optimize_signals(platform):
    """Show the 2026 algorithm ranking signals for a platform."""
    signals = optimizer.PLATFORM_SIGNALS.get(platform, {})
    if not _json_output:
        click.echo(f"\n=== 2026 Algorithm Signals: {platform.upper()} ===")
        for signal, data in sorted(signals.items(), key=lambda x: x[1]["weight"], reverse=True):
            click.echo(f"  {signal:22s} weight={data['weight']:3d}%  threshold={data['threshold']}")
            click.echo(f"                         {data['description']}")
    else:
        output({platform: signals})


@optimize.command("times")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"]))
def optimize_times(platform):
    """Show optimal posting times for a platform."""
    times = optimizer.OPTIMAL_POST_TIMES.get(platform, {})
    if not _json_output:
        click.echo(f"\n=== Best Posting Times: {platform.upper()} ===")
        for k, v in times.items():
            if k == "note":
                continue
            if isinstance(v, list):
                click.echo(f"  {k}: {', '.join(v)}")
            else:
                click.echo(f"  {k}: {v}")
        if "note" in times:
            click.echo(f"\n  Note: {times['note']}")
    else:
        output(times)


# ---------------------------------------------------------------------------
# THEME PAGE commands
# ---------------------------------------------------------------------------

@main.group()
def theme():
    """Theme page creation, conversion optimization, and monetization strategy."""


@theme.command("create")
@click.option("--niche", required=True, help="Content niche (finance, fitness, beauty, etc.).")
@click.option("--archetype", default="educator",
              type=click.Choice(["curator", "educator", "entertainer", "product_reviewer", "community_builder"]),
              help="Page style/type.")
@click.option("--platforms", default="tiktok,instagram_reels,youtube_shorts",
              help="Comma-separated list of target platforms.")
@click.option("--monetization", default="", help="Comma-separated monetization goals.")
@click.option("--save", default="", help="Save plan to JSON file.")
def theme_create(niche, archetype, platforms, monetization, save):
    """Generate a complete theme page launch plan with 90-day roadmap."""
    plats = [p.strip() for p in platforms.split(",") if p.strip()]
    monets = [m.strip() for m in monetization.split(",") if m.strip()] if monetization else None
    click.echo(f"Building {archetype} theme page plan for {niche}...", err=True)
    result = theme_page_mod.create_theme_page_plan(
        niche=niche,
        archetype=archetype,
        platforms=plats,
        monetization_goals=monets,
    )
    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"Plan saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== Theme Page Plan: {niche.title()} ({archetype}) ===")
        na = result["niche_analysis"]
        click.echo(f"Monetization Score:  {na['monetization_score']}/100")
        click.echo(f"Avg CPM:             {na['avg_cpm']}")
        click.echo(f"Conversion Rate:     {na['conversion_rate']}")
        click.echo(f"Target Audience:     {na['target_audience']}")

        arch = result["archetype_details"]
        click.echo(f"\nPage Type:           {archetype}")
        click.echo(f"Effort Level:        {arch['effort_level']}")
        click.echo(f"Time to 1K:          {arch['expected_time_to_1k_followers']}")

        click.echo(f"\nLaunch Steps:")
        for i, step in enumerate(result["launch_steps"], 1):
            click.echo(f"  {i}. {step}")

        click.echo(f"\nTop Hashtags:  {' '.join(result['top_hashtags'])}")
        click.echo(f"Conversion Hook:  {result['conversion_hook']}")
        click.echo(f"Monetization:  {' | '.join(result['monetization_path'])}")

        click.echo(f"\n90-Day Roadmap:")
        for phase in result["90_day_roadmap"]:
            click.echo(f"\n  Days {phase['days']} — {phase['phase']}: {phase['focus']}")
            for task in phase["tasks"]:
                click.echo(f"    - {task}")

        click.echo(f"\nContent Pillars:")
        for pillar in result["content_pillars"]:
            click.echo(f"  {pillar['pillar']}")
            click.echo(f"    Purpose: {pillar['purpose']}")
            click.echo(f"    CTA: {pillar['cta']}")

        click.echo(f"\nAccount Setup Checklist:")
        for item in result["account_setup_checklist"]:
            click.echo(f"  [ ] {item['item']:18s} → {item['tip']}")
    else:
        output(result)


@theme.command("niches")
def theme_niches():
    """List all available niches ranked by monetization potential."""
    result = theme_page_mod.get_niche_list()
    if not _json_output:
        click.echo(f"\n=== Profitable Niches (2026) ===")
        click.echo(f"{'Niche':20s} {'Score':7s} {'CPM':12s} {'Conv Rate':12s} {'Top Monetization'}")
        click.echo("-" * 80)
        for n in result["niches"]:
            click.echo(
                f"{n['name']:20s} {n['monetization_score']:5d}/100  "
                f"{n['avg_cpm']:12s} {n['conversion_rate']:12s} {n['top_monetization']}"
            )
        click.echo(f"\nArchetypes: {', '.join(result['archetypes'])}")
        click.echo(f"\nTip: {result['tip']}")
    else:
        output(result)


@theme.command("funnel")
def theme_funnel():
    """Show the complete 7-stage conversion funnel for theme pages."""
    if not _json_output:
        click.echo(f"\n=== Theme Page Conversion Funnel (7 Stages) ===")
        for stage in theme_page_mod.CONVERSION_FUNNEL_STAGES:
            click.echo(f"\n[Stage {stage['stage']}] {stage['name'].upper()}")
            click.echo(f"  Goal:      {stage['goal']}")
            click.echo(f"  Metric:    {stage['metric']}")
            click.echo(f"  Benchmark: {stage['benchmark']}")
            click.echo(f"  Tactics:")
            for t in stage["tactics"]:
                click.echo(f"    - {t}")
    else:
        output({"funnel": theme_page_mod.CONVERSION_FUNNEL_STAGES})


@theme.command("calendar")
@click.option("--niche", required=True, help="Content niche.")
@click.option("--platforms", default="tiktok,youtube_shorts", help="Comma-separated platforms.")
@click.option("--posts-per-week", default=4, type=int, help="Posts per week.")
@click.option("--weeks", default=2, type=int, help="Number of weeks to plan.")
@click.option("--save", default="", help="Save calendar to JSON file.")
def theme_calendar(niche, platforms, posts_per_week, weeks, save):
    """Generate a content calendar based on viral format patterns."""
    plats = [p.strip() for p in platforms.split(",") if p.strip()]
    result = analyzer.generate_content_calendar(
        niche=niche,
        platforms=plats,
        posts_per_week=posts_per_week,
        weeks=weeks,
    )
    if save:
        with open(save, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"Calendar saved to {save}", err=True)

    if not _json_output:
        click.echo(f"\n=== Content Calendar: {niche.title()} ({weeks} weeks) ===")
        for entry in result["calendar"]:
            click.echo(f"\n  Week {entry['week']} {entry['day']:10s} | {entry['format']:20s}")
            click.echo(f"    Hook: {entry['hook_template']}")
            click.echo(f"    Tip:  {entry['tip'][:80]}")
        click.echo(f"\nRepurpose tip: {result['repurpose_tip']}")
    else:
        output(result)


# ---------------------------------------------------------------------------
# WORKSPACE commands
# ---------------------------------------------------------------------------

@main.group()
def workspace():
    """Manage saved workspaces (trends + accounts + plans)."""


@workspace.command("new")
@click.argument("name")
@click.option("--niche", default="", help="Primary niche for this workspace.")
def workspace_new(name, niche):
    """Create a new workspace for organizing trends and accounts."""
    from datetime import datetime
    sess = get_session()
    ws = {
        "name": name,
        "niche": niche,
        "created_at": datetime.now().isoformat(),
        "accounts": [],
        "trend_snapshots": [],
        "theme_plans": [],
        "notes": [],
    }
    sess.set_workspace(ws)
    output({"status": "created", "workspace": name, "niche": niche},
           f"Workspace '{name}' created.")


@workspace.command("save")
@click.argument("path")
def workspace_save(path):
    """Save current workspace to a JSON file."""
    sess = get_session()
    saved = sess.save(path)
    output({"status": "saved", "path": saved}, f"Workspace saved to {saved}")


@workspace.command("open")
@click.argument("path")
def workspace_open(path):
    """Open a workspace from a JSON file."""
    sess = get_session()
    ws = sess.load(path)
    output({"status": "opened", "workspace": ws.get("name")}, f"Opened workspace: {ws.get('name')}")


@workspace.command("status")
def workspace_status():
    """Show current workspace status."""
    sess = get_session()
    output(sess.status())


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

@main.command("repl")
def repl():
    """Launch interactive REPL for social media CLI."""
    try:
        from cli_anything.social_media.utils.repl_skin import launch_repl
        launch_repl(main, "social-media")
    except ImportError:
        click.echo("Starting basic REPL (install prompt-toolkit for enhanced mode)...")
        import subprocess
        while True:
            try:
                line = click.prompt("social-media", prompt_suffix="> ")
            except (click.Abort, EOFError):
                click.echo("\nExiting REPL.")
                break
            if line.strip() in ("exit", "quit", "q"):
                click.echo("Exiting REPL.")
                break
            if not line.strip():
                continue
            try:
                args = line.split()
                main.main(args, standalone_mode=False)
            except SystemExit:
                pass
            except Exception as e:
                click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
