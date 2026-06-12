#!/usr/bin/env python3
"""social-trends CLI — Viral trend intelligence for YouTube & TikTok.

Scrapes trending videos, hashtags, and sounds; generates optimized hashtag sets;
audits social accounts; builds content calendars; guides theme page creation.

Usage:
    # Fetch trending YouTube videos
    social-trends youtube trending --category music --region US

    # Fetch TikTok viral trends
    social-trends tiktok trending --limit 30

    # Get hashtags for a niche
    social-trends hashtags generate --topic fitness --platform tiktok --strategy balanced

    # Analyze trending music/sounds
    social-trends music analyze --platform tiktok

    # Audit your account
    social-trends account audit --platform tiktok --handle @yourhandle

    # Generate a content calendar
    social-trends account calendar --niche fitness --platform tiktok --weeks 4

    # Get theme page playbook
    social-trends theme playbook --niche motivation --platform tiktok

    # Interactive REPL
    social-trends repl
"""

import sys
import os
import json
from datetime import date
from typing import Optional, List

import click

from cli_anything.social_trends.core import (
    youtube_trends as yt,
    tiktok_trends as tt,
    hashtag_analyzer as ha,
    music_tracker as mt,
    account_optimizer as ao,
    theme_page_strategy as tp,
)

# ── Global state ──────────────────────────────────────────────────────────────

_json_output = False

# ── Output helpers ────────────────────────────────────────────────────────────

def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(message, bold=True)
        _print_value(data)


def _print_value(val, indent: int = 0):
    prefix = "  " * indent
    if isinstance(val, dict):
        for k, v in val.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{prefix}{click.style(k, bold=True)}:")
                _print_value(v, indent + 1)
            else:
                click.echo(f"{prefix}{click.style(k, fg='cyan')}: {v}")
    elif isinstance(val, list):
        for i, item in enumerate(val):
            if isinstance(item, dict):
                click.echo(f"{prefix}[{i}]")
                _print_value(item, indent + 1)
            else:
                click.echo(f"{prefix}  {item}")
    else:
        click.echo(f"{prefix}{val}")


def success(msg: str):
    if not _json_output:
        click.secho(f"  {msg}", fg="green")


def warn(msg: str):
    if not _json_output:
        click.secho(f"  {msg}", fg="yellow")


def info(msg: str):
    if not _json_output:
        click.secho(f"  {msg}", fg="blue")


def _table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None):
    if _json_output:
        return
    if not col_widths:
        col_widths = [max(len(str(r[i])) for r in ([headers] + rows)) + 2 for i in range(len(headers))]
    header_line = "  " + "".join(
        click.style(str(h).ljust(w), bold=True, fg="cyan") for h, w in zip(headers, col_widths)
    )
    sep = "  " + "─" * sum(col_widths)
    click.echo(sep)
    click.echo(header_line)
    click.echo(sep)
    for row in rows:
        click.echo("  " + "".join(str(c).ljust(w) for c, w in zip(row, col_widths)))
    click.echo(sep)


# ── Root group ────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON.")
@click.version_option("1.0.0", prog_name="social-trends")
def cli(use_json: bool):
    """social-trends — viral trend intelligence for YouTube & TikTok.

    Scrape trending content, analyze hashtags and sounds, optimize accounts,
    and build theme pages that convert.

    Set environment variables for enhanced data access:
      YOUTUBE_API_KEY           — YouTube Data API v3 (optional, improves data)
      TIKTOK_CLIENT_KEY         — TikTok Research API client key
      TIKTOK_CLIENT_SECRET      — TikTok Research API client secret
      TIKTOK_MS_TOKEN           — TikTok session token for TikTokApi
    """
    global _json_output
    _json_output = use_json


# ── youtube group ─────────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trend scraping commands."""


@youtube.command("trending")
@click.option("--category", "-c", default="all",
              type=click.Choice(list(yt.CATEGORIES.keys())),
              show_default=True, help="Content category.")
@click.option("--region", "-r", default="US", show_default=True,
              help="ISO 3166-1 alpha-2 region code (US, GB, IN, …).")
@click.option("--limit", "-n", default=20, show_default=True,
              help="Maximum number of videos to show.")
@click.option("--hashtags", is_flag=True, help="Also show trending hashtags.")
def youtube_trending(category: str, region: str, limit: int, hashtags: bool):
    """Fetch trending YouTube videos."""
    info(f"Fetching YouTube trending ({category}, {region})...")
    videos = yt.get_trending(category=category, region=region, max_results=limit)

    if not videos:
        warn("No trending data retrieved. Try setting YOUTUBE_API_KEY.")
        return

    if _json_output:
        output([v.to_dict() for v in videos])
        return

    rows = []
    for i, v in enumerate(videos[:limit], 1):
        views = f"{v.views:,}" if v.views else "N/A"
        tags = ", ".join(v.hashtags[:3]) if v.hashtags else "—"
        rows.append([str(i), v.title[:45], v.channel[:20], views, tags])

    _table(
        ["#", "Title", "Channel", "Views", "Top Hashtags"],
        rows,
        [4, 47, 22, 14, 30],
    )
    success(f"Retrieved {len(videos)} trending videos.")

    if hashtags:
        tags = yt.get_trending_hashtags(videos, top_n=15)
        click.echo()
        click.secho("  Trending Hashtags:", bold=True)
        tag_rows = [[f"#{t.tag.lstrip('#')}", str(t.count), f"{t.avg_views:,}"] for t in tags]
        _table(["Hashtag", "Videos", "Avg Views"], tag_rows, [25, 10, 15])


@youtube.command("hashtags")
@click.option("--limit", "-n", default=25, show_default=True)
def youtube_hashtags(limit: int):
    """Show trending YouTube hashtags (pulls fresh trending data)."""
    info("Fetching YouTube trending videos for hashtag analysis...")
    videos = yt.get_trending(max_results=50)
    tags = yt.get_trending_hashtags(videos, top_n=limit)
    if _json_output:
        output([t.to_dict() for t in tags])
        return
    rows = [[f"#{t.tag.lstrip('#')}", str(t.count), f"{t.avg_views:,}"] for t in tags]
    _table(["Hashtag", "Appearances", "Avg Views"], rows, [28, 14, 18])


# ── tiktok group ──────────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trend scraping commands."""


@tiktok.command("trending")
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--hashtags", is_flag=True, help="Also show trending hashtags.")
@click.option("--sounds", is_flag=True, help="Also show trending sounds.")
def tiktok_trending(limit: int, hashtags: bool, sounds: bool):
    """Fetch trending TikTok videos."""
    info("Fetching TikTok trending videos...")
    videos = tt.get_trending(max_results=limit)

    if not videos:
        warn(
            "No TikTok data retrieved.\n"
            "  → Set TIKTOK_CLIENT_KEY + TIKTOK_CLIENT_SECRET for Research API\n"
            "  → Or set TIKTOK_MS_TOKEN for TikTokApi (requires playwright)"
        )
        return

    if _json_output:
        output([v.to_dict() for v in videos])
        return

    rows = []
    for i, v in enumerate(videos[:limit], 1):
        plays = f"{v.plays:,}" if v.plays else "N/A"
        tags = " ".join(v.hashtags[:2]) if v.hashtags else "—"
        rows.append([str(i), v.description[:40], v.author[:18], plays, tags])

    _table(
        ["#", "Description", "Author", "Plays", "Hashtags"],
        rows,
        [4, 42, 20, 14, 30],
    )
    success(f"Retrieved {len(videos)} trending videos.")

    if hashtags:
        tags = tt.get_trending_hashtags(videos, top_n=15)
        click.echo()
        click.secho("  Trending Hashtags:", bold=True)
        tag_rows = [[t.tag, str(t.video_count), f"{t.view_count:,}"] for t in tags]
        _table(["Hashtag", "Videos", "Total Views"], tag_rows, [25, 10, 18])

    if sounds:
        snd = tt.get_trending_sounds(videos, top_n=10)
        click.echo()
        click.secho("  Trending Sounds:", bold=True)
        snd_rows = [[s.title[:30] or "Original", s.author[:20] or "—", str(s.usage_count)] for s in snd]
        _table(["Sound", "Artist", "Uses"], snd_rows, [32, 22, 8])


@tiktok.command("sounds")
@click.option("--limit", "-n", default=15, show_default=True)
def tiktok_sounds(limit: int):
    """Show trending TikTok sounds/audio."""
    info("Fetching TikTok trending sounds...")
    videos = tt.get_trending(max_results=50)
    sounds = tt.get_trending_sounds(videos, top_n=limit)
    if _json_output:
        output([s.to_dict() for s in sounds])
        return
    rows = [[s.title[:35] or "Original Sound", s.author[:20] or "—", str(s.usage_count)] for s in sounds]
    _table(["Sound Title", "Artist", "Video Uses"], rows, [37, 22, 12])


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag analysis and set generation."""


@hashtags.command("generate")
@click.option("--topic", "-t", required=True, help="Niche or topic (e.g., fitness, beauty, cars).")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]),
              default="tiktok", show_default=True)
@click.option("--strategy", "-s",
              type=click.Choice(["balanced", "growth", "niche", "viral"]),
              default="balanced", show_default=True,
              help="balanced=mix all sizes | growth=medium/small | niche=community | viral=max reach")
@click.option("--live", is_flag=True,
              help="Fetch live trending data first (slower but more accurate).")
def hashtags_generate(topic: str, platform: str, strategy: str, live: bool):
    """Generate an optimized hashtag set for a topic."""
    live_tags = []
    if live:
        info("Fetching live trend data to enhance hashtag recommendations...")
        yt_videos = yt.get_trending(max_results=30)
        yt_tags = yt.get_trending_hashtags(yt_videos, top_n=50)
        tt_videos = tt.get_trending(max_results=30)
        tt_tags = tt.get_trending_hashtags(tt_videos, top_n=50)
        live_tags = ha.merge_platform_hashtags(yt_tags, tt_tags)

    hashtag_set = ha.generate_hashtag_set(
        topic=topic,
        platform=platform,
        strategy=strategy,
        live_tags=live_tags or None,
    )

    if _json_output:
        output(hashtag_set.to_dict())
        return

    click.secho(f"\n  Hashtag Set: {topic.title()} → {platform} ({strategy})", bold=True)
    click.echo(f"  {hashtag_set.rationale}\n")
    click.echo("  " + "  ".join(hashtag_set.tags))
    click.echo()
    success(f"Generated {len(hashtag_set.tags)} hashtags.")


@hashtags.command("niches")
def hashtags_niches():
    """List all supported niche categories."""
    niches = ha.get_niche_list()
    if _json_output:
        output(niches)
        return
    click.secho("  Supported niches:", bold=True)
    for n in niches:
        click.echo(f"    • {n}")


@hashtags.command("merge")
@click.option("--live", is_flag=True, default=True, show_default=True,
              help="Fetch live data from YouTube + TikTok.")
@click.option("--limit", "-n", default=30, show_default=True)
def hashtags_merge(live: bool, limit: int):
    """Merge and rank hashtags from YouTube + TikTok."""
    info("Fetching trends from both platforms...")
    yt_videos = yt.get_trending(max_results=50)
    yt_tags = yt.get_trending_hashtags(yt_videos, top_n=50)
    tt_videos = tt.get_trending(max_results=50)
    tt_tags = tt.get_trending_hashtags(tt_videos, top_n=50)

    merged = ha.merge_platform_hashtags(yt_tags, tt_tags)[:limit]

    if _json_output:
        output([h.to_dict() for h in merged])
        return

    rows = [
        [h.tag, h.bucket, ",".join(h.platforms), f"{h.total_reach:,}", str(h.score)]
        for h in merged
    ]
    _table(["Hashtag", "Bucket", "Platforms", "Total Reach", "Score"], rows,
           [25, 10, 16, 18, 8])


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending music and sound analysis."""


@music.command("analyze")
@click.option("--niche", "-n", default="all", help="Content niche for sound strategy.")
def music_analyze(niche: str):
    """Analyze trending music and sounds across YouTube + TikTok."""
    info("Fetching trending content for sound analysis...")
    yt_videos = yt.get_trending(category="music", max_results=30)
    yt_music = yt.get_trending_music(yt_videos)
    tt_videos = tt.get_trending(max_results=50)
    tt_sounds = tt.get_trending_sounds(tt_videos, top_n=30)

    insight = mt.analyze_sounds(tt_sounds, yt_music)

    if _json_output:
        output(insight.to_dict())
        return

    click.secho("\n  Sound Intelligence Report", bold=True)
    click.echo(f"  {insight.insight_summary}\n")

    if insight.rising_sounds:
        click.secho("  Rising Sounds (Use NOW):", bold=True, fg="green")
        for s in insight.rising_sounds[:5]:
            click.echo(
                f"    • {s.title[:30]:<30} {s.artist[:20]:<20} "
                f"[{s.platform}] velocity={s.velocity_score} ({s.recommendation})"
            )

    if insight.top_sounds:
        click.echo()
        click.secho("  Top Sounds (Most Used):", bold=True)
        rows = [
            [s.title[:30] or "Original", s.artist[:18] or "—",
             s.platform, str(s.usage_count), s.recommendation]
            for s in insight.top_sounds[:10]
        ]
        _table(["Sound", "Artist", "Platform", "Uses", "Status"], rows,
               [32, 20, 10, 8, 12])

    if niche and niche != "all":
        strategy = mt.get_sound_strategy(niche)
        click.echo()
        click.secho(f"  Sound Strategy for {niche.title()}:", bold=True)
        click.echo(f"    Timing: {strategy['timing']}")
        click.echo(f"    Best sound types: {', '.join(strategy['sound_types'])}")
        for tip in strategy["tips"]:
            click.echo(f"    • {tip}")


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization, scheduling, and content planning."""


@account.command("audit")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--handle", "-h", required=True, help="Account handle (e.g., @username).")
def account_audit(platform: str, handle: str):
    """Audit your account against optimization best practices.

    Runs an interactive self-assessment checklist. Answer y/n for each item.
    """
    checklist = ao._PROFILE_CHECKLIST.get(platform, ao._PROFILE_CHECKLIST["tiktok"])

    if _json_output:
        audit = ao.audit_account(platform, handle)
        output(audit.to_dict())
        return

    click.secho(f"\n  Account Audit: {handle} ({platform})", bold=True)
    click.echo("  Answer y/n for each checklist item:\n")

    self_assessment = {}
    for key, description, _ in checklist:
        response = click.prompt(f"  [{key}] {description}", type=click.Choice(["y", "n", "?"], case_sensitive=False))
        self_assessment[key] = (response.lower() == "y")

    audit = ao.audit_account(platform, handle, self_assessment)

    color = "green" if audit.score >= 70 else ("yellow" if audit.score >= 40 else "red")
    click.echo()
    click.secho(f"  Audit Score: {audit.score}/100", bold=True, fg=color)

    fails = [i for i in audit.items if i.status == "fail"]
    if fails:
        click.echo()
        click.secho("  Priority Fixes:", bold=True, fg="red")
        for item in fails[:5]:
            click.echo(f"    • {item.recommendation}")

    warns = [i for i in audit.items if i.status == "warn"]
    if warns:
        click.echo()
        click.secho("  Review These:", bold=True, fg="yellow")
        for item in warns[:3]:
            click.echo(f"    • {item.recommendation}")


@account.command("schedule")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--posts-per-week", "-n", default=5, show_default=True)
@click.option("--timezone", "-tz", default=0, show_default=True,
              help="UTC offset (e.g., -5 for EST, +1 for CET).")
def account_schedule(platform: str, posts_per_week: int, timezone: int):
    """Show optimal posting schedule for a platform."""
    slots = ao.get_posting_schedule(platform, posts_per_week, timezone)
    if _json_output:
        output([s.to_dict() for s in slots])
        return
    rows = [[s.day, s.time_local, s.priority.upper(), s.reason] for s in slots]
    _table(["Day", "Time (local)", "Priority", "Reason"], rows, [12, 14, 10, 50])


@account.command("calendar")
@click.option("--niche", "-n", required=True, help="Content niche.")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              default="tiktok", show_default=True)
@click.option("--start", default=str(date.today()), show_default=True,
              help="Start date (YYYY-MM-DD).")
@click.option("--weeks", "-w", default=4, show_default=True)
@click.option("--posts-per-week", default=5, show_default=True)
def account_calendar(niche: str, platform: str, start: str, weeks: int, posts_per_week: int):
    """Generate a content calendar."""
    hashtag_set = ha.generate_hashtag_set(niche, platform, "balanced")
    calendar = ao.generate_content_calendar(
        niche=niche,
        platform=platform,
        start_date=start,
        weeks=weeks,
        posts_per_week=posts_per_week,
        hashtags=hashtag_set.tags,
    )
    if _json_output:
        output([e.to_dict() for e in calendar])
        return
    click.secho(f"\n  Content Calendar: {niche.title()} | {platform} | {weeks} weeks\n", bold=True)
    for entry in calendar:
        click.secho(f"  {entry.date} {entry.day_of_week} {entry.post_time}", bold=True)
        click.echo(f"    Type:  {entry.content_type}")
        click.echo(f"    Topic: {entry.topic_idea}")
        click.echo(f"    Tags:  {' '.join(entry.hashtag_set[:5])}{'…' if len(entry.hashtag_set) > 5 else ''}")
        click.echo(f"    Note:  {entry.notes}")
        click.echo()


@account.command("grow")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube"]),
              required=True)
@click.option("--niche", "-n", required=True)
@click.option("--followers", "-f", required=True, type=int, help="Current follower count.")
@click.option("--avg-views", "-v", required=True, type=int, help="Average views per post.")
@click.option("--posts-per-week", default=5, show_default=True)
def account_grow(platform: str, niche: str, followers: int, avg_views: int, posts_per_week: int):
    """Get personalized growth recommendations."""
    recs = ao.get_growth_recommendations(platform, niche, followers, avg_views, posts_per_week)
    if _json_output:
        output(recs)
        return

    click.secho(f"\n  Growth Analysis: {platform.title()} | {followers:,} followers", bold=True)
    click.echo(f"  Tier: {recs['tier'].upper()} | "
               f"Engagement: {recs['engagement_rate']}% (benchmark: {recs['benchmark_engagement_rate']}%)\n")

    if recs["diagnoses"]:
        click.secho("  Diagnoses:", bold=True, fg="yellow")
        for d in recs["diagnoses"]:
            click.echo(f"    • {d}")

    if recs["quick_wins"]:
        click.echo()
        click.secho("  Quick Wins:", bold=True, fg="green")
        for w in recs["quick_wins"]:
            click.echo(f"    • {w}")

    if recs["thirty_day_action_plan"]:
        click.echo()
        click.secho("  30-Day Action Plan:", bold=True)
        for a in recs["thirty_day_action_plan"]:
            click.echo(f"    • {a}")


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page strategy and conversion guides."""


@theme.command("playbook")
@click.option("--niche", "-n", required=True, help="Content niche.")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              default="tiktok", show_default=True)
def theme_playbook(niche: str, platform: str):
    """Get a complete theme page playbook for a niche."""
    playbook = tp.get_playbook(niche, platform)
    if _json_output:
        output(playbook.to_dict())
        return

    click.secho(f"\n  Theme Page Playbook: {niche.title()} → {platform.title()}", bold=True)
    click.echo(f"\n  Username ideas: {playbook.username_formula}")
    click.echo(f"  Bio template:   {playbook.bio_template}")
    click.echo(f"  Posting freq:   {playbook.posting_frequency}")
    click.echo(f"  Hashtag strat:  {playbook.hashtag_strategy}")

    click.echo()
    click.secho("  Content Sources:", bold=True)
    for source in playbook.content_sources:
        click.echo(f"    [{source.platform}] {source.method}")
        click.echo(f"            Query: {source.query}")
        click.echo(f"            Permission: {source.repost_permission}")

    click.echo()
    click.secho("  Monetization Path:", bold=True)
    for tier in playbook.monetization_path:
        click.echo(f"\n    {tier.follower_threshold} → {tier.monthly_revenue_range}")
        for m in tier.methods:
            click.echo(f"      • {m}")

    click.echo()
    click.secho("  Common Mistakes to Avoid:", bold=True, fg="red")
    for m in playbook.common_mistakes:
        click.echo(f"    • {m}")

    click.echo()
    click.secho("  Week 1 Checklist:", bold=True, fg="green")
    for item in playbook.week1_checklist:
        click.echo(f"    {item}")


@theme.command("niches")
@click.option("--limit", "-n", default=10, show_default=True)
def theme_niches(limit: int):
    """Score and rank niches by opportunity."""
    scores = tp.score_niches()[:limit]
    if _json_output:
        output([s.to_dict() for s in scores])
        return

    click.secho("\n  Niche Opportunity Rankings:", bold=True)
    rows = [
        [
            s.niche,
            str(s.monetization_potential),
            s.competition_level,
            str(s.content_availability),
            str(s.estimated_months_to_10k),
            ", ".join(s.recommended_platforms[:2]),
        ]
        for s in scores
    ]
    _table(
        ["Niche", "$ Potential", "Competition", "Content Avail", "Months→10K", "Platforms"],
        rows,
        [18, 13, 13, 15, 12, 20],
    )
    click.echo()
    for s in scores[:3]:
        click.echo(f"  {s.niche.title()}: {s.verdict}")
        click.echo()


@theme.command("convert")
def theme_convert():
    """Complete guide to converting a theme page into a business."""
    guide = tp.get_conversion_guide()
    if _json_output:
        output(guide)
        return

    click.secho(f"\n  {guide['title']}", bold=True)

    for phase in guide["phases"]:
        click.echo()
        click.secho(f"  {phase['phase']}", bold=True, fg="cyan")
        click.echo(f"  Goal: {phase['goal']}")
        for action in phase["actions"]:
            click.echo(f"    • {action}")
        kpis_str = " | ".join(phase["kpis"])
        click.secho(f"  KPIs: {kpis_str}", fg="blue")

    click.echo()
    click.secho("  Account Valuations:", bold=True)
    for plat, val in guide["valuation_multiples"].items():
        click.echo(f"    {plat.title():<12} {val}")

    click.echo()
    click.secho("  Key Success Factors:", bold=True, fg="green")
    for f in guide["key_success_factors"]:
        click.echo(f"    • {f}")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command("repl")
def repl():
    """Launch an interactive REPL session."""
    try:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
    except ImportError:
        click.secho("prompt-toolkit not installed. Run: pip install prompt-toolkit", fg="red")
        sys.exit(1)

    skin = ReplSkin("social_trends", version="1.0.0")
    skin.print_banner()
    click.echo("  Social Trends REPL — type 'help' for commands, 'quit' to exit\n")

    hist_dir = os.path.expanduser("~/.cli-anything-social_trends")
    os.makedirs(hist_dir, exist_ok=True)
    session = PromptSession(history=FileHistory(os.path.join(hist_dir, "history")))

    builtin_help = (
        "  Available command groups:\n"
        "    youtube  — YouTube trending videos + hashtags\n"
        "    tiktok   — TikTok trending videos + sounds + hashtags\n"
        "    hashtags — Generate optimized hashtag sets\n"
        "    music    — Analyze trending sounds\n"
        "    account  — Audit, schedule, calendar, growth plan\n"
        "    theme    — Theme page playbooks + niche scoring\n\n"
        "  Examples:\n"
        "    youtube trending --category music\n"
        "    tiktok trending --limit 20 --hashtags --sounds\n"
        "    hashtags generate --topic fitness --platform tiktok\n"
        "    account calendar --niche beauty --weeks 4\n"
        "    theme playbook --niche motivation\n"
        "    theme convert\n"
    )

    while True:
        try:
            raw = session.prompt(skin.prompt(context="trends")).strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue
        if raw.lower() in ("quit", "exit", "q"):
            break
        if raw.lower() in ("help", "?", "h"):
            click.echo(builtin_help)
            continue

        args = raw.split()
        try:
            cli.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            click.secho(f"  Error: {exc}", fg="red")

    skin.print_goodbye()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
