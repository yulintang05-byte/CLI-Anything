"""Social Trends CLI — Agent-native social media trend intelligence tool.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Provides account optimization, theme page strategy, and posting schedules.
Designed for AI agents (Claude Code) and human operators.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)

Environment variables:
    YOUTUBE_API_KEY       — YouTube Data API v3 key (enables full metadata)
    TIKTOK_RAPIDAPI_KEY   — RapidAPI key for tiktok-api6 (enables live TikTok data)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

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
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            if all(isinstance(i, str) for i in v):
                click.echo(f"{pad}{k}: {', '.join(v)}")
            else:
                click.echo(f"{pad}{k}: [{len(v)} items]")
                for item in v[:5]:
                    if isinstance(item, dict):
                        _print_dict(item, indent + 4)
                    else:
                        click.echo(f"{pad}    {item}")
                if len(v) > 5:
                    click.echo(f"{pad}    ... and {len(v) - 5} more")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for i, item in enumerate(lst, 1):
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo(f"  [{i}] " + "  ".join(parts[:6]))
        else:
            click.echo(f"  {i}. {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(f"Error: {msg}", err=True)


def _ok(msg: str) -> None:
    if not _json_output:
        click.echo(msg)


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, default=False,
              help="Output results as JSON")
@click.option("--session", "session_file", default=None,
              help="Path to persist session history")
@click.pass_context
def cli(ctx: click.Context, use_json: bool, session_file: Optional[str]) -> None:
    """Social Trends CLI — viral trends, hashtags, music, and account optimization.

    \b
    Commands:
      trends     — Fetch trending videos/content from YouTube or TikTok
      hashtags   — Recommend, analyze, and score hashtag sets
      music      — Discover trending sounds and music for your content
      account    — Audit and optimize your social media accounts
      theme      — Theme page strategy, playbooks, and conversion tactics
      status     — Session status
      history    — Command history
      undo/redo  — Undo or redo last action
    """
    global _json_output, _session
    _json_output = use_json
    _session = Session(session_file)

    if ctx.invoked_subcommand is None:
        # Launch REPL
        _launch_repl()


# ── REPL ──────────────────────────────────────────────────────────────────────

def _launch_repl() -> None:
    global _repl_mode
    _repl_mode = True
    click.echo("Social Trends CLI — REPL mode. Type 'help' or 'exit'.")
    click.echo("Set YOUTUBE_API_KEY / TIKTOK_RAPIDAPI_KEY for live data.\n")

    while True:
        try:
            raw = input("trends> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye.")
            break

        if not raw:
            continue
        if raw.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye.")
            break
        if raw.lower() in ("help", "?"):
            click.echo(cli.get_help(click.Context(cli)))
            continue

        try:
            args = shlex.split(raw)
            ctx = cli.make_context("trends", args, resilient_parsing=False)
            with ctx:
                cli.invoke(ctx)
        except SystemExit:
            pass
        except click.UsageError as e:
            _err(str(e))
        except Exception as e:
            _err(str(e))


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch live trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, IN, ...)")
@click.option("--category", default="0", show_default=True,
              help="YouTube category ID (0=all, 10=music, 17=sports, 20=gaming, 24=entertainment, 28=science)")
@click.option("--count", default=15, show_default=True, help="Number of results")
def trends_youtube(region: str, category: str, count: int) -> None:
    """Fetch trending YouTube videos.

    \b
    Requires YOUTUBE_API_KEY for full metadata. Falls back to HTML scrape.
    Category IDs: 0=All  10=Music  17=Sports  20=Gaming  24=Entertainment  28=Science
    """
    _ok(f"Fetching YouTube trending [{region}] category={category}...")
    results = trends_mod.fetch_youtube_trending(region=region, category_id=category, max_results=count)
    get_session().record("trends.youtube", {"region": region, "category": category, "count": count}, {"count": len(results)})
    output(results, f"Found {len(results)} trending videos:")


@trends.command("tiktok")
@click.option("--count", default=15, show_default=True, help="Number of results")
def trends_tiktok(count: int) -> None:
    """Fetch trending TikTok videos/hashtags.

    \b
    Requires TIKTOK_RAPIDAPI_KEY for video-level data. Falls back to HTML scrape.
    """
    _ok("Fetching TikTok trending...")
    results = trends_mod.fetch_tiktok_trending(max_results=count)
    get_session().record("trends.tiktok", {"count": count}, {"count": len(results)})
    output(results, f"Found {len(results)} trending items:")


@trends.command("search")
@click.argument("query")
@click.option("--platform", default="youtube", type=click.Choice(["youtube", "tiktok"]), show_default=True)
@click.option("--count", default=10, show_default=True)
def trends_search(query: str, platform: str, count: int) -> None:
    """Search for trending content by keyword."""
    _ok(f"Searching {platform} for '{query}'...")
    if platform == "youtube":
        results = trends_mod.search_youtube(query, max_results=count)
    else:
        results = trends_mod.search_tiktok_hashtag(query)
        if isinstance(results, dict):
            results = [results]
    get_session().record("trends.search", {"query": query, "platform": platform}, {"count": len(results)})
    output(results, f"Search results for '{query}':")


@trends.command("all")
@click.option("--count", default=10, show_default=True)
def trends_all(count: int) -> None:
    """Fetch trending content from all platforms at once."""
    _ok("Fetching trends from all platforms...")
    yt = trends_mod.fetch_youtube_trending(max_results=count)
    tt = trends_mod.fetch_tiktok_trending(max_results=count)
    combined = {"youtube_trending": yt, "tiktok_trending": tt}
    get_session().record("trends.all", {"count": count}, {"yt": len(yt), "tt": len(tt)})
    output(combined, f"Trends: {len(yt)} YouTube | {len(tt)} TikTok")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Research, recommend, and score hashtag sets."""


@hashtags.command("recommend")
@click.argument("niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter_x"]),
              show_default=True)
@click.option("--count", default=30, show_default=True)
@click.option("--no-boosters", is_flag=True, default=False)
def hashtags_recommend(niche: str, platform: str, count: int, no_boosters: bool) -> None:
    """Recommend hashtags for a niche and platform.

    \b
    Example niches: fitness, food, travel, fashion, beauty,
                    motivational, gaming, finance, lifestyle, animals
    """
    hs = hashtags_mod.recommend_hashtags(niche, platform, count, not no_boosters)
    get_session().record("hashtags.recommend", {"niche": niche, "platform": platform})
    output(hs.to_dict(), f"Hashtag set for '{niche}' on {platform}:")


@hashtags.command("score")
@click.argument("tags", nargs=-1)
def hashtags_score(tags: tuple) -> None:
    """Score a hashtag set for reach/niche balance.

    \b
    Usage: hashtags score fitness gym workout fyp viral trending
    """
    if not tags:
        _err("Provide hashtags as arguments: hashtags score fitness gym fyp viral")
        return
    clean = [t.lstrip("#") for t in tags]
    result = hashtags_mod.score_hashtag_mix(clean)
    get_session().record("hashtags.score", {"tags": clean})
    output(result, "Hashtag score:")


@hashtags.command("caption")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True)
@click.option("--max-tags", default=30, show_default=True)
def hashtags_caption(niche: str, platform: str, max_tags: int) -> None:
    """Generate a ready-to-paste hashtag caption block."""
    hs = hashtags_mod.recommend_hashtags(niche, platform, max_tags)
    caption = hs.to_caption(max_tags)
    get_session().record("hashtags.caption", {"niche": niche, "platform": platform})
    if _json_output:
        output({"caption": caption, "tag_count": caption.count("#")})
    else:
        click.echo(f"\n--- Copy-paste caption for {niche} on {platform} ---\n")
        click.echo(caption)
        click.echo(f"\n[{caption.count('#')} tags]\n")


@hashtags.command("niches")
def hashtags_niches() -> None:
    """List all supported niche categories."""
    niches = hashtags_mod.list_niches()
    output(niches, "Available niches:")


@hashtags.command("research")
@click.argument("hashtag")
def hashtags_research(hashtag: str) -> None:
    """Look up stats for a specific TikTok hashtag (requires TIKTOK_RAPIDAPI_KEY)."""
    _ok(f"Researching #{hashtag}...")
    result = trends_mod.search_tiktok_hashtag(hashtag)
    get_session().record("hashtags.research", {"hashtag": hashtag})
    output(result, f"Stats for #{hashtag}:")


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Discover trending sounds and music for your content."""


@music.command("trending")
@click.option("--count", default=20, show_default=True)
def music_trending(count: int) -> None:
    """Fetch trending TikTok sounds (requires TIKTOK_RAPIDAPI_KEY or uses catalog)."""
    _ok("Fetching trending sounds...")
    results = music_mod.fetch_tiktok_trending_sounds(count)
    get_session().record("music.trending", {"count": count}, {"count": len(results)})
    output(results, f"Found {len(results)} trending sounds:")


@music.command("recommend")
@click.argument("niche")
def music_recommend(niche: str) -> None:
    """Recommend music/sounds that fit a content niche.

    \b
    Example niches: fitness, travel, fashion, motivation, gaming, food
    """
    results = music_mod.recommend_sounds_for_niche(niche)
    get_session().record("music.recommend", {"niche": niche})
    output(results, f"Recommended sounds for '{niche}':")


@music.command("catalog")
@click.option("--category", default=None, help="Filter by category")
def music_catalog(category: Optional[str]) -> None:
    """Browse the curated sound catalog.

    \b
    Categories: motivational, chill_aesthetic, viral_dance, hype,
                trendy_2025, royalty_free
    """
    results = music_mod.get_catalog_sounds(category)
    get_session().record("music.catalog", {"category": category})
    output(results, f"Sound catalog ({category or 'all categories'}):")


@music.command("categories")
def music_categories() -> None:
    """List available sound categories in the catalog."""
    cats = music_mod.list_sound_categories()
    output(cats, "Sound categories:")


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account() -> None:
    """Audit and optimize social media accounts."""


@account.command("audit")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter_x"]),
              help="Platform to audit")
@click.option("--username", required=True, help="Account username/handle")
@click.option("--followers", default=0, type=int)
@click.option("--following", default=0, type=int)
@click.option("--posts", default=0, type=int)
@click.option("--avg-likes", default=0.0, type=float)
@click.option("--avg-comments", default=0.0, type=float)
@click.option("--avg-views", default=0.0, type=float)
@click.option("--bio/--no-bio", "bio_complete", default=True)
@click.option("--has-link/--no-link", default=True)
@click.option("--posting", default="unknown",
              type=click.Choice(["daily", "weekly", "sporadic", "unknown"]),
              help="Posting consistency")
def account_audit(
    platform: str, username: str, followers: int, following: int,
    posts: int, avg_likes: float, avg_comments: float, avg_views: float,
    bio_complete: bool, has_link: bool, posting: str,
) -> None:
    """Run a full account audit and get an optimization score.

    \b
    Example:
        account audit --platform tiktok --username @mypage --followers 5000
            --following 500 --posts 80 --avg-likes 200 --avg-comments 15
            --posting weekly
    """
    audit = accounts_mod.AccountAudit(
        platform=platform,
        username=username,
        followers=followers,
        following=following,
        posts=posts,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        avg_views=avg_views,
        bio_complete=bio_complete,
        has_link=has_link,
        posting_consistency=posting,
    )
    result = audit.score()
    get_session().record("account.audit", {"username": username, "platform": platform})
    output(result, f"Audit for @{username} on {platform}:")


@account.command("tips")
@click.argument("platform",
                type=click.Choice(["tiktok", "youtube", "instagram", "twitter_x"]))
def account_tips(platform: str) -> None:
    """Get platform-specific growth tips and best practices."""
    tips = accounts_mod.get_platform_tips(platform)
    get_session().record("account.tips", {"platform": platform})
    output(tips, f"Growth tips for {platform}:")


@account.command("schedule")
@click.argument("platform",
                type=click.Choice(["tiktok", "youtube", "instagram", "twitter_x"]))
@click.option("--goal", default="growth", type=click.Choice(["growth", "engagement", "monetization"]))
def account_schedule(platform: str, goal: str) -> None:
    """Get optimal posting schedule for a platform and goal."""
    schedule = accounts_mod.get_posting_schedule(platform, goal)
    get_session().record("account.schedule", {"platform": platform, "goal": goal})
    output(schedule, f"Posting schedule for {platform} [{goal}]:")


@account.command("checklist")
def account_checklist() -> None:
    """Show the profile optimization checklist for all platforms."""
    checklist = accounts_mod.get_profile_checklist()
    get_session().record("account.checklist", {})
    output(checklist, "Profile optimization checklist:")


@account.command("pillars")
def account_pillars() -> None:
    """Show recommended content pillar frameworks."""
    pillars = accounts_mod.get_content_pillars()
    get_session().record("account.pillars", {})
    output(pillars, "Content pillars:")


@account.command("optimize-all")
def account_optimize_all() -> None:
    """Show full optimization guide covering all major platforms."""
    platforms = ["tiktok", "youtube", "instagram", "twitter_x"]
    result = {}
    for p in platforms:
        tips = accounts_mod.get_platform_tips(p)
        schedule = accounts_mod.get_posting_schedule(p)
        result[p] = {
            "posting_frequency": tips.get("posting_frequency", ""),
            "best_times": tips.get("best_times", []),
            "hook": tips.get("hook", ""),
            "hashtags": tips.get("hashtags", ""),
            "engagement": tips.get("engagement", ""),
            "growth_hack": tips.get("growth_hack", ""),
            "kpis": tips.get("analytics_kpis", []),
        }
    checklist = accounts_mod.get_profile_checklist()
    pillars = accounts_mod.get_content_pillars()
    full = {
        "platform_guides": result,
        "profile_checklist": checklist,
        "content_pillars": pillars,
    }
    get_session().record("account.optimize-all", {})
    output(full, "Full account optimization guide:")


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme() -> None:
    """Theme page creation, growth playbooks, and conversion strategies."""


@theme.command("playbook")
def theme_playbook() -> None:
    """Show the complete 7-phase theme page launch playbook."""
    playbook = theme_mod.get_launch_playbook()
    get_session().record("theme.playbook", {})
    if _json_output:
        output(playbook)
    else:
        for phase in playbook:
            click.echo(f"\n=== Phase {phase['phase']}: {phase['name']} ({phase['days']}) ===")
            for action in phase["actions"]:
                click.echo(f"  - {action}")
            if phase.get("tools"):
                click.echo(f"  Tools: {', '.join(phase['tools'])}")


@theme.command("niches")
@click.option("--niche", default=None, help="Filter to a specific niche")
def theme_niches(niche: Optional[str]) -> None:
    """Show niche viability analysis with monetization potential."""
    result = theme_mod.get_niche_viability(niche)
    get_session().record("theme.niches", {"niche": niche})
    output(result, "Niche viability:")


@theme.command("convert")
def theme_convert() -> None:
    """Show proven conversion strategies for turning followers into revenue."""
    strategies = theme_mod.get_conversion_strategies()
    get_session().record("theme.convert", {})
    if _json_output:
        output(strategies)
    else:
        for s in strategies:
            click.echo(f"\n--- {s['strategy']} ---")
            click.echo(f"  Description: {s['description']}")
            click.echo(f"  Conversion rate: {s['conversion_rate']}")
            click.echo(f"  Steps:")
            for step in s["setup"]:
                click.echo(f"    > {step}")
            if s.get("tools"):
                click.echo(f"  Tools: {', '.join(s['tools'])}")


@theme.command("plan")
@click.option("--niche", required=True, help="Content niche (e.g., fitness, finance)")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--target", default=10000, type=int, show_default=True,
              help="Target followers in 90 days")
@click.option("--goal", default="affiliate",
              type=click.Choice(["affiliate", "digital_products", "coaching", "brand_deals", "shoutouts"]))
def theme_plan(niche: str, platform: str, target: int, goal: str) -> None:
    """Generate a custom theme page roadmap for your niche and goals."""
    plan = theme_mod.ThemePagePlan(niche, platform, target, goal)
    roadmap = plan.generate_roadmap()
    get_session().record("theme.plan", {"niche": niche, "platform": platform, "goal": goal})
    if _json_output:
        output(roadmap)
    else:
        click.echo(f"\n=== Theme Page Roadmap: {niche} on {platform} ===")
        click.echo(f"Target: {target:,} followers in 90 days | Goal: {goal}\n")
        viability = roadmap.get("niche_viability", {})
        if viability:
            click.echo(f"Niche viability:")
            for k, v in viability.items():
                if not isinstance(v, list):
                    click.echo(f"  {k}: {v}")
                else:
                    click.echo(f"  {k}: {', '.join(v)}")
        click.echo("\nRoadmap phases:")
        for phase in roadmap["phases"]:
            click.echo(f"\n  Phase {phase['phase']}: {phase['name']} ({phase['days']})")
            for action in phase["actions"][:3]:
                click.echo(f"    - {action}")
            click.echo(f"    ... ({len(phase['actions'])} total actions)")


@theme.command("list-niches")
def theme_list_niches() -> None:
    """List all available theme page niches."""
    niches = theme_mod.list_niches()
    output(niches, "Available niches:")


# ── session commands ──────────────────────────────────────────────────────────

@cli.command("status")
def cmd_status() -> None:
    """Show current session status."""
    import os
    s = get_session().status()
    s["api_keys"] = {
        "YOUTUBE_API_KEY": "set" if os.environ.get("YOUTUBE_API_KEY") else "NOT set (using scrape fallback)",
        "TIKTOK_RAPIDAPI_KEY": "set" if os.environ.get("TIKTOK_RAPIDAPI_KEY") else "NOT set (using scrape fallback)",
    }
    output(s, "Session status:")


@cli.command("history")
@click.option("--limit", default=20, show_default=True)
def cmd_history(limit: int) -> None:
    """Show command history."""
    entries = get_session().history(limit)
    output(entries, f"Last {limit} commands:")


@cli.command("undo")
def cmd_undo() -> None:
    """Undo last command."""
    entry = get_session().undo()
    if entry:
        output(entry.to_dict(), f"Undid: {entry.command}")
    else:
        _ok("Nothing to undo.")


@cli.command("redo")
def cmd_redo() -> None:
    """Redo last undone command."""
    entry = get_session().redo()
    if entry:
        output(entry.to_dict(), f"Redid: {entry.command}")
    else:
        _ok("Nothing to redo.")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
