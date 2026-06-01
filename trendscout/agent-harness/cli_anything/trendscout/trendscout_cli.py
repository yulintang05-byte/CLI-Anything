"""TrendScout CLI – Agent-native viral trend intelligence for social media.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Optimizes social media accounts. Full theme page creation playbook.

Usage:
    python3 -m cli_anything.trendscout [--json] <command>
    python3 -m cli_anything.trendscout  (launches REPL)

Quick start:
    trendscout trends fetch youtube --category music --region us
    trendscout trends fetch tiktok --limit 30
    trendscout trends cross --category fitness
    trendscout trends hashtags --niche fitness
    trendscout trends times --platform tiktok
    trendscout account add --handle mypage --platform tiktok --niche fitness
    trendscout account audit acc0
    trendscout account optimize-all
    trendscout theme-page playbook
    trendscout theme-page niches --sort opportunity
    trendscout theme-page formats --platform tiktok
    trendscout theme-page monetize --niche fitness
    trendscout theme-page quickstart --niche gaming --platform youtube
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.trendscout.core.session import Session
from cli_anything.trendscout.core import youtube as yt_mod
from cli_anything.trendscout.core import tiktok as tt_mod
from cli_anything.trendscout.core import trends as trends_mod
from cli_anything.trendscout.core import account as acc_mod
from cli_anything.trendscout.core import theme_page as tp_mod

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n  {message}")
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if k in ("videos", "tracks", "hashtags", "sounds", "results", "methods",
                  "niches", "formats", "steps", "phases", "accounts", "all_checklist",
                  "completed_items", "top_priority_actions", "cross_platform_hashtags",
                  "recommended_hashtags"):
            click.echo(f"{pad}{k}: [{len(v)} items]" if isinstance(v, list) else f"{pad}{k}: {v}")
        elif isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list, indent: int = 2) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    pad = " " * indent
    for item in lst:
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo(pad + "  ".join(parts[:6]))
        else:
            click.echo(f"{pad}{item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"  Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, RuntimeError, FileNotFoundError, KeyError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="trendscout")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """TrendScout — viral trend intelligence for social media.

    Scrape YouTube + TikTok trends, audit accounts, and learn the
    theme-page playbook. Designed for AI agents and humans alike.

    \b
    Quick start:
      trendscout trends cross --category fitness
      trendscout trends hashtags --niche beauty
      trendscout account add --handle mypage --platform tiktok --niche fitness
      trendscout account audit acc0
      trendscout theme-page quickstart --niche gaming
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend scraping commands (fetch, cross, hashtags, times)."""
    pass


@trends.command("fetch")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "music"], case_sensitive=False))
@click.option("--category", default="all", show_default=True,
              help="YouTube category: all, music, gaming, beauty, sports, tech, etc.")
@click.option("--region", default="us", show_default=True, help="Region code (us, uk, ca, au, in, ...)")
@click.option("--limit", default=20, show_default=True, help="Max results to fetch")
@handle_error
def trends_fetch(platform: str, category: str, region: str, limit: int) -> None:
    """Fetch trending videos, hashtags or sounds from YouTube or TikTok.

    \b
    PLATFORM choices:
      youtube  — trending videos + hashtags via yt-dlp
      tiktok   — trending hashtags from TikTok explore
      music    — trending music/sounds (YouTube Music charts + TikTok sounds)
    """
    plat = platform.lower()

    if plat == "youtube":
        data = yt_mod.fetch_trending(category=category, region=region, limit=limit)
        if not _json_output:
            from cli_anything.trendscout.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            click.echo(f"\n  YouTube Trending — category={category} region={region.upper()}")
            if data.get("demo_mode"):
                skin.info("Demo mode — install yt-dlp for live data: pip install yt-dlp")
            skin.table(
                ["#", "Title", "Channel", "Views", "Hashtags"],
                [
                    [
                        str(i + 1),
                        v["title"][:40],
                        v["channel"][:25],
                        f"{v['view_count']:,}" if v.get("view_count") else "–",
                        " ".join(v["hashtags"][:3]),
                    ]
                    for i, v in enumerate(data.get("videos", []))
                ]
            )
        else:
            output(data)

    elif plat == "tiktok":
        data = tt_mod.fetch_trending_hashtags(limit=limit)
        if not _json_output:
            from cli_anything.trendscout.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            click.echo(f"\n  TikTok Trending Hashtags")
            if data.get("demo_mode"):
                skin.info("Demo mode — live data requires network access to TikTok")
            skin.table(
                ["#", "Hashtag", "View Count"],
                [
                    [str(i + 1), h["hashtag"], f"{h.get('view_count', 0):,}" if h.get("view_count") else "–"]
                    for i, h in enumerate(data.get("hashtags", []))
                ]
            )
        else:
            output(data)

    elif plat == "music":
        yt_music = yt_mod.fetch_trending_music(region=region, limit=limit)
        tt_sounds = tt_mod.fetch_trending_sounds(limit=limit)
        combined = {
            "youtube_music": yt_music.get("tracks", [])[:10],
            "tiktok_sounds": tt_sounds.get("sounds", [])[:10],
            "demo_mode": yt_music.get("demo_mode") or tt_sounds.get("demo_mode"),
        }
        if not _json_output:
            from cli_anything.trendscout.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            click.echo("\n  Trending Music — YouTube Music Charts")
            skin.table(
                ["#", "Title", "Artist", "Duration"],
                [
                    [str(i + 1), t["title"][:35], t["artist"][:25], str(t.get("duration", "–"))]
                    for i, t in enumerate(combined["youtube_music"])
                ]
            )
            click.echo("\n  Trending Sounds — TikTok")
            skin.table(
                ["#", "Title", "Artist", "Plays"],
                [
                    [str(i + 1), s["title"][:35], s["artist"][:25], f"{s.get('play_count', 0):,}"]
                    for i, s in enumerate(combined["tiktok_sounds"])
                ]
            )
        else:
            output(combined)


@trends.command("cross")
@click.option("--category", default="all", show_default=True, help="Content category")
@click.option("--region", default="us", show_default=True, help="Region code")
@click.option("--limit", default=20, show_default=True, help="Entries to analyze")
@handle_error
def trends_cross(category: str, region: str, limit: int) -> None:
    """Aggregate cross-platform trends (YouTube + TikTok) into a unified ranking."""
    data = trends_mod.cross_platform_trends(category=category, region=region, limit=limit)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Cross-Platform Trends — category={category} region={region.upper()}")
        if any(data["sources_demo_mode"].values()):
            skin.info("Partial demo mode — install yt-dlp for full live data")

        skin.table(
            ["#", "Hashtag", "YT Freq", "TT Freq", "TT Views (B)", "Cross-Platform"],
            [
                [
                    str(i + 1),
                    item["tag"],
                    str(item["youtube_freq"]),
                    str(item["tiktok_freq"]),
                    f"{item['tiktok_views'] / 1_000_000_000:.1f}B" if item.get("tiktok_views") else "–",
                    "YES" if (item["youtube_freq"] > 0 and item["tiktok_freq"] > 0) else "",
                ]
                for i, item in enumerate(data.get("cross_platform_hashtags", [])[:20])
            ]
        )
    else:
        output(data)


@trends.command("hashtags")
@click.option("--niche", required=True, help="Content niche (gaming, beauty, fitness, food, tech, ...)")
@click.option("--region", default="us", show_default=True, help="Region code")
@click.option("--limit", default=30, show_default=True, help="Max hashtags to return")
@handle_error
def trends_hashtags(niche: str, region: str, limit: int) -> None:
    """Generate a hashtag strategy report for a specific content niche."""
    data = trends_mod.niche_hashtag_report(niche=niche, region=region, limit=limit)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Hashtag Report — niche={niche} region={region.upper()}")
        click.echo(f"\n  Strategy tip: {data['strategy_tip']}")
        click.echo(f"\n  Recommended hashtags ({len(data['recommended_hashtags'])} total):")
        tags = data["recommended_hashtags"]
        cols = 4
        for i in range(0, len(tags), cols):
            row = tags[i:i + cols]
            click.echo("    " + "  ".join(t.ljust(22) for t in row))
        click.echo(f"\n  Trending on YouTube: {', '.join(data['trending_on_youtube'][:5])}")
        click.echo(f"  Trending on TikTok:  {', '.join(data['trending_on_tiktok'][:5])}")
    else:
        output(data)


@trends.command("times")
@click.option("--platform", default="both", show_default=True,
              help="Platform: tiktok, youtube, instagram, both")
@click.option("--timezone", "tz", default="EST", show_default=True, help="Your timezone abbreviation")
@handle_error
def trends_times(platform: str, tz: str) -> None:
    """Show research-backed best posting times per platform."""
    data = trends_mod.best_posting_times(platform=platform, timezone_name=tz)
    if not _json_output:
        if "platforms" in data:
            for plat, info in data["platforms"].items():
                click.echo(f"\n  {plat.upper()} — Best Posting Times ({tz})")
                click.echo(f"    Best days:    {', '.join(info['best_days'])}")
                click.echo(f"    Best times:   {' | '.join(info['best_times_est'])}")
                click.echo(f"    Avoid:        {info['worst_times']}")
                click.echo(f"    Frequency:    {info['optimal_frequency']}")
                click.echo(f"    Tip:          {info['notes']}")
        else:
            plat = data.get("platform", "").upper()
            click.echo(f"\n  {plat} — Best Posting Times ({tz})")
            click.echo(f"    Best days:  {', '.join(data['best_days'])}")
            click.echo(f"    Best times: {' | '.join(data['best_times_est'])}")
            click.echo(f"    Avoid:      {data['worst_times']}")
            click.echo(f"    Frequency:  {data['optimal_frequency']}")
            click.echo(f"    Tip:        {data['notes']}")
    else:
        output(data)


@trends.command("fyp")
@click.option("--limit", default=20, show_default=True, help="FYP entries to fetch")
@handle_error
def trends_fyp(limit: int) -> None:
    """Fetch TikTok For You Page (FYP) trending content and extract signals."""
    data = tt_mod.fetch_fyp_trends(limit=limit)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo("\n  TikTok FYP Trends")
        if data.get("demo_mode"):
            skin.info("Demo mode — live TikTok FYP requires network access")
        skin.table(
            ["#", "Author", "Likes", "Plays", "Sound", "Hashtags"],
            [
                [
                    str(i + 1),
                    v["author"][:20],
                    f"{v.get('likes', 0):,}",
                    f"{v.get('plays', 0):,}",
                    v.get("music_title", "")[:20],
                    " ".join(v.get("hashtags", [])[:3]),
                ]
                for i, v in enumerate(data.get("videos", []))
            ]
        )
        click.echo("\n  Top hashtags in this FYP batch:")
        for item in data.get("top_hashtags_in_batch", [])[:10]:
            click.echo(f"    {item['hashtag']:<25} freq={item['frequency']}")
    else:
        output(data)


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account management and optimization (add, list, audit, optimize-all, plan)."""
    pass


@account.command("add")
@click.option("--handle", required=True, help="Account handle (without @)")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter"], case_sensitive=False),
              help="Social media platform")
@click.option("--niche", default="general", show_default=True, help="Content niche")
@click.option("--followers", default=0, show_default=True, type=int, help="Current follower count")
@click.option("--notes", default="", help="Optional notes")
@handle_error
def account_add(handle: str, platform: str, niche: str, followers: int, notes: str) -> None:
    """Register a social media account for tracking and optimization."""
    sess = get_session()
    result = acc_mod.add_account(sess, handle, platform, niche, followers, notes)
    output(result, f"Added @{result['handle']} on {result['platform']} (niche: {result['niche']})")


@account.command("remove")
@click.argument("account_id")
@handle_error
def account_remove(account_id: str) -> None:
    """Remove an account by ID."""
    sess = get_session()
    result = acc_mod.remove_account(sess, account_id)
    output(result, f"Removed account {account_id}")


@account.command("list")
@handle_error
def account_list() -> None:
    """List all tracked accounts."""
    sess = get_session()
    result = acc_mod.list_accounts(sess)
    if not _json_output:
        if not result:
            click.echo("  No accounts. Use 'account add' to register one.")
            return
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Handle", "Platform", "Niche", "Followers", "Score"],
            [
                [a["id"], f"@{a['handle']}", a["platform"], a["niche"],
                 f"{a['followers']:,}", str(a.get("profile_score") or "–")]
                for a in result
            ]
        )
    else:
        output(result)


@account.command("update")
@click.argument("account_id")
@click.option("--followers", default=None, type=int, help="Updated follower count")
@click.option("--niche", default=None, help="Updated niche")
@click.option("--notes", default=None, help="Updated notes")
@handle_error
def account_update(account_id: str, followers: Optional[int], niche: Optional[str], notes: Optional[str]) -> None:
    """Update an account's stats."""
    sess = get_session()
    result = acc_mod.update_account(sess, account_id, followers=followers, niche=niche, notes=notes)
    output(result, f"Updated account {account_id}")


@account.command("audit")
@click.argument("account_id")
@click.option(
    "--completed", default="",
    help="Comma-separated list of completed checklist item IDs (e.g. bio_keywords,profile_pic)"
)
@handle_error
def account_audit(account_id: str, completed: str) -> None:
    """Run a profile optimization audit. Returns score, grade, and action plan.

    \b
    Example:
      trendscout account audit acc0 --completed bio_keywords,profile_pic,pinned_videos
    """
    sess = get_session()
    completed_list = [c.strip() for c in completed.split(",") if c.strip()] if completed else []
    result = acc_mod.audit_account(sess, account_id, completed_items=completed_list)

    if not _json_output:
        click.echo(f"\n  Profile Audit: @{result['handle']} ({result['platform']}) — niche={result['niche']}")
        click.echo(f"\n  Score: {result['score']}/100  Grade: {result['grade']}")
        click.echo(f"  Completed: {result['completed_count']} / {result['completed_count'] + result['todo_count']} items\n")
        click.echo("  Top Priority Actions:")
        for i, action in enumerate(result["top_priority_actions"], 1):
            click.echo(f"    {i}. [{action['impact']} pts] {action['action']}")
            click.echo(f"       {action['tip']}")
        click.echo()
    else:
        output(result)


@account.command("checklist")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram", "twitter"], case_sensitive=False))
@handle_error
def account_checklist(platform: str) -> None:
    """Show the full optimization checklist for a platform."""
    result = acc_mod.get_checklist(platform)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  {platform.upper()} Optimization Checklist\n")
        skin.table(
            ["ID", "Item", "Weight", "Tip"],
            [
                [item["id"], item["label"][:40], str(item["weight"]), item["tip"][:60]]
                for item in result
            ]
        )
    else:
        output(result)


@account.command("optimize-all")
@handle_error
def account_optimize_all() -> None:
    """Run baseline audit on ALL tracked accounts. Shows priority-ordered action list."""
    sess = get_session()
    result = acc_mod.optimize_all_accounts(sess)

    if not _json_output:
        if not result["accounts"]:
            click.echo("  No accounts tracked. Use 'account add' first.")
            return
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Account Optimization Summary — {result['total_accounts']} accounts")
        click.echo(f"  Average score: {result['overall_avg_score']}/100\n")
        skin.table(
            ["ID", "Handle", "Platform", "Niche", "Score", "Grade", "Top Action"],
            [
                [
                    a["id"],
                    f"@{a['handle']}",
                    a["platform"],
                    a["niche"],
                    str(a["score"]),
                    a["grade"],
                    (a["top_action"]["action"][:40] if a.get("top_action") else "–"),
                ]
                for a in result["accounts"]
            ]
        )
    else:
        output(result)


@account.command("plan")
@click.argument("account_id")
@click.option("--goal", default=10000, show_default=True, type=int, help="Follower goal")
@click.option("--weeks", default=12, show_default=True, type=int, help="Timeframe in weeks")
@handle_error
def account_plan(account_id: str, goal: int, weeks: int) -> None:
    """Generate a week-by-week growth plan to reach a follower goal."""
    sess = get_session()
    result = acc_mod.growth_plan(sess, account_id, goal_followers=goal, timeframe_weeks=weeks)

    if not _json_output:
        click.echo(f"\n  Growth Plan: @{result['handle']} ({result['platform']})")
        click.echo(f"  {result['current_followers']:,} → {result['goal_followers']:,} followers in {result['timeframe_weeks']} weeks")
        click.echo(f"  Weekly target: ~{result['weekly_follower_target']:,} new followers\n")
        for phase in result["phases"]:
            click.echo(f"  Phase {phase['phase']}: {phase['title']} (Weeks {phase['weeks']})")
            click.echo(f"  Target: +{phase.get('weekly_follower_target', 0):,}/week")
            for task in phase["tasks"]:
                click.echo(f"    • {task}")
            click.echo()
        click.echo("  Key Metrics to Track:")
        for m in result["key_metrics_to_track"]:
            click.echo(f"    • {m}")
    else:
        output(result)


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page creation playbook (playbook, niches, formats, monetize, quickstart)."""
    pass


@theme_page.command("playbook")
@click.option("--step", default=None, type=int, help="Show a specific step (1–7)")
@handle_error
def theme_page_playbook(step: Optional[int]) -> None:
    """Show the complete theme page creation playbook (7 steps).

    Use --step N to drill into a specific step.
    """
    if step is not None:
        data = tp_mod.get_playbook_step(step)
        if not _json_output:
            click.echo(f"\n  Step {data['step']}/{data['total_steps']}: {data['title']}\n")
            for i, action in enumerate(data["action_items"], 1):
                click.echo(f"  {i}. {action}")
            if data.get("next_step"):
                click.echo(f"\n  Next: trendscout theme-page playbook --step {data['next_step']}")
        else:
            output(data)
    else:
        data = tp_mod.get_playbook()
        if not _json_output:
            click.echo(f"\n  {data['title']}\n")
            for step_data in data["steps"]:
                click.echo(f"  Step {step_data['step']}: {step_data['title']}")
                click.echo(f"    {step_data['details'][0]}")
            click.echo(f"\n  Run 'theme-page playbook --step N' for full details on any step.")
        else:
            output(data)


@theme_page.command("niches")
@click.option("--sort", "sort_by", default="opportunity",
              type=click.Choice(["cpm", "competition", "opportunity"], case_sensitive=False),
              show_default=True, help="Sort niches by metric")
@handle_error
def theme_page_niches(sort_by: str) -> None:
    """List profitable niches ranked by CPM, competition, or opportunity score."""
    data = tp_mod.list_niches(sort_by=sort_by)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Profitable Niches (sorted by: {sort_by})\n")
        skin.table(
            ["#", "Niche", "CPM", "Competition", "Audience", "Top Monetization"],
            [
                [
                    str(i + 1),
                    n["niche"][:28],
                    n["cpm"],
                    n["competition"],
                    n["audience_size"],
                    n["monetization"][0] if n["monetization"] else "–",
                ]
                for i, n in enumerate(data["niches"])
            ]
        )
    else:
        output(data)


@theme_page.command("formats")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube"], case_sensitive=False),
              show_default=True, help="Platform")
@handle_error
def theme_page_formats(platform: str) -> None:
    """Show content format recommendations ranked by virality potential."""
    data = tp_mod.list_content_formats(platform=platform)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Content Formats — {platform.upper()} (ranked by virality)\n")
        skin.table(
            ["#", "Format", "Virality", "Effort", "Description"],
            [
                [
                    str(i + 1),
                    f["format"][:20],
                    f["virality"],
                    f["effort"],
                    f["description"][:55],
                ]
                for i, f in enumerate(data["formats"])
            ]
        )
    else:
        output(data)


@theme_page.command("monetize")
@click.option("--niche", default="all", show_default=True, help="Content niche or 'all'")
@handle_error
def theme_page_monetize(niche: str) -> None:
    """List monetization strategies with income potential and how-to guidance."""
    data = tp_mod.list_monetization_methods(niche=niche)
    if not _json_output:
        from cli_anything.trendscout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Monetization Methods — niche={niche}\n")
        for i, m in enumerate(data["methods"], 1):
            click.echo(f"  {i}. {m['method']}")
            click.echo(f"     Difficulty: {m['difficulty']}  |  Time to revenue: {m['time_to_revenue']}")
            click.echo(f"     Potential:  {m['income_potential']}")
            click.echo(f"     How-to:     {m['how_to']}")
            click.echo()
    else:
        output(data)


@theme_page.command("quickstart")
@click.option("--niche", required=True, help="Your content niche (e.g. gaming, fitness, finance)")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube"], case_sensitive=False),
              show_default=True, help="Primary platform")
@handle_error
def theme_page_quickstart(niche: str, platform: str) -> None:
    """Generate a personalized quick-start guide for a niche + platform combo."""
    data = tp_mod.quick_start_guide(niche=niche, platform=platform)
    if not _json_output:
        click.echo(f"\n  Quick-Start Guide: {niche.title()} on {platform.upper()}")
        if data.get("niche_overview"):
            n = data["niche_overview"]
            click.echo(f"\n  Niche overview: CPM={n['cpm']}  Competition={n['competition']}  Audience={n['audience_size']}")

        click.echo(f"\n  Week 1 Action Items:")
        for i, task in enumerate(data["week_1_actions"], 1):
            click.echo(f"    {i}. {task}")

        click.echo(f"\n  Top Content Formats (by virality):")
        for f in data["top_content_formats"]:
            click.echo(f"    • {f['format']} — {f['description'][:60]}")

        click.echo(f"\n  Recommended Monetization:")
        for m in data["recommended_monetization"]:
            click.echo(f"    • {m['method']} ({m['time_to_revenue']})")

        click.echo(f"\n  First milestone: {data['first_milestone']}")
        click.echo(f"\n  Pro tip: {data['pro_tip']}\n")
    else:
        output(data)


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session commands (undo, redo, status, history)."""
    pass


@session_group.command("undo")
@handle_error
def session_undo() -> None:
    """Undo the last operation."""
    sess = get_session()
    desc = sess.undo()
    output({"success": True, "undone": desc}, f"Undone: {desc}")


@session_group.command("redo")
@handle_error
def session_redo() -> None:
    """Redo the last undone operation."""
    sess = get_session()
    desc = sess.redo()
    output({"success": True, "redone": desc}, f"Redone: {desc}")


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show session status."""
    sess = get_session()
    result = sess.status()
    output(result, "Session status:")


@session_group.command("history")
@handle_error
def session_history() -> None:
    """Show the undo history stack."""
    sess = get_session()
    result = sess.list_history()
    output(result, f"History ({len(result)} entries):")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.trendscout.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    sess = get_session()
    pt_session = skin.create_prompt_session()

    _commands = {
        "trends fetch youtube --category <cat> --region <r>": "Fetch YouTube trending videos",
        "trends fetch tiktok --limit 30": "Fetch TikTok trending hashtags",
        "trends fetch music --region us": "Fetch trending music (YT Music + TikTok)",
        "trends cross --category <cat>": "Cross-platform trend ranking",
        "trends hashtags --niche <niche>": "Hashtag strategy for a niche",
        "trends times --platform tiktok": "Best posting times",
        "trends fyp --limit 20": "TikTok FYP trending signals",
        "account add --handle <h> --platform tiktok --niche <n>": "Add account",
        "account list": "List tracked accounts",
        "account audit <id> --completed <ids>": "Profile audit + score",
        "account checklist <platform>": "Full optimization checklist",
        "account optimize-all": "Audit all accounts",
        "account plan <id> --goal 10000": "Growth plan",
        "theme-page playbook [--step N]": "Theme page creation steps",
        "theme-page niches --sort opportunity": "Profitable niche comparison",
        "theme-page formats --platform tiktok": "Content formats by virality",
        "theme-page monetize --niche <niche>": "Monetization methods",
        "theme-page quickstart --niche <niche>": "Personalized quick-start guide",
        "session undo / redo / status": "Session management",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue

        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_commands)
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
