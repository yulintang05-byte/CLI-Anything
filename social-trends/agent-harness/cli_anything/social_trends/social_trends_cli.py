#!/usr/bin/env python3
"""Social Trends CLI — Scrape YouTube/TikTok for viral trends, optimize accounts,
and learn the theme page conversion playbook.

Usage:
    # Fetch trending content
    cli-anything-social-trends trends fetch --platform youtube --region US
    cli-anything-social-trends trends fetch --platform tiktok
    cli-anything-social-trends trends music --platform tiktok --limit 20
    cli-anything-social-trends trends viral --niche fitness

    # Hashtag optimization
    cli-anything-social-trends hashtags optimize --niche fitness --platform tiktok
    cli-anything-social-trends hashtags sets --niche finance --platform instagram
    cli-anything-social-trends hashtags analyze --tag fitness
    cli-anything-social-trends hashtags niches
    cli-anything-social-trends hashtags strategy --platform tiktok

    # Account optimization
    cli-anything-social-trends account bio --platform tiktok
    cli-anything-social-trends account strategy --platform tiktok --niche fitness
    cli-anything-social-trends account schedule --platform instagram --niche food
    cli-anything-social-trends account engagement --platform tiktok
    cli-anything-social-trends account audit --platform tiktok --niche fitness

    # Theme page
    cli-anything-social-trends theme guide
    cli-anything-social-trends theme niches
    cli-anything-social-trends theme plan --niche fitness --days 7
    cli-anything-social-trends theme monetize --niche finance
    cli-anything-social-trends theme convert

    # Config
    cli-anything-social-trends config set youtube_api_key <key>
    cli-anything-social-trends config get

    # Interactive REPL
    cli-anything-social-trends
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import optimizer as optimizer_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.utils.social_backend import (
    load_config, save_config, list_niches,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False


def get_session() -> Session:
    global _session
    if _session is None:
        from pathlib import Path
        sf = str(Path.home() / ".cli-anything-social-trends" / "session.json")
        _session = Session(session_file=sf)
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
    prefix = "  " * (indent + 1)
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
    prefix = "  " * (indent + 1)
    for i, item in enumerate(items):
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo(f"{prefix}[{i}] " + "  ".join(parts))
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, RuntimeError, FileNotFoundError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Trends CLI — viral trends, hashtag optimization, account growth, theme pages."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch viral trends from YouTube and TikTok."""
    pass


@trends.command("fetch")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              show_default=True, help="Platform to fetch from")
@click.option("--region", "-r", default="US", show_default=True, help="Region code (e.g. US, GB, AU)")
@click.option("--category", "-c", default="all", show_default=True,
              help="Category: all, music, gaming, news, sports, entertainment, tech")
@click.option("--limit", "-n", type=int, default=20, show_default=True, help="Number of results")
@handle_error
def trends_fetch(platform, region, category, limit):
    """Fetch trending content from YouTube and/or TikTok."""
    sess = get_session()
    p = platform.lower()
    if p == "youtube":
        result = trends_mod.get_youtube_trending(region=region, category=category, limit=limit)
        sess.record("trends fetch", {"platform": p, "region": region, "category": category})
        if not _json_output:
            click.echo(f"\n  YouTube Trending — {region} / {category} ({result['count']} videos)\n")
            from cli_anything.social_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            skin.table(
                ["#", "Title", "Channel", "Views", "Tags"],
                [[str(i + 1), v["title"][:40], v["channel"][:20], v["views"], ", ".join(v.get("tags", [])[:3])]
                 for i, v in enumerate(result["videos"])],
            )
            if result["extracted_tags"]:
                click.echo(f"\n  Top tags: {' '.join(['#' + t for t in result['extracted_tags'][:10]])}\n")
        else:
            output(result)
    elif p == "tiktok":
        result = trends_mod.get_tiktok_trending(limit=limit)
        sess.record("trends fetch", {"platform": p})
        if not _json_output:
            click.echo(f"\n  TikTok Trending Hashtags ({result['hashtag_count']} tags)\n")
            from cli_anything.social_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()
            skin.table(
                ["Rank", "Tag", "Post Count", "Source"],
                [[str(h["rank"]), h["tag"], h.get("post_count", ""), h.get("source", "")]
                 for h in result["hashtags"][:limit]],
            )
            click.echo(f"\n  Trending Sounds:")
            for s in result.get("trending_sounds", []):
                click.echo(f"    #{s['rank']} {s['title']} — {s['artist']} ({s.get('uses', '')} uses)")
            click.echo()
        else:
            output(result)
    else:
        result = trends_mod.get_all_trending(region=region, category=category, limit=limit)
        sess.record("trends fetch", {"platform": "all", "region": region})
        if not _json_output:
            click.echo(f"\n  Combined Trending ({region})\n")
            click.echo(f"  YouTube: {result['youtube']['count']} videos")
            click.echo(f"  TikTok:  {result['tiktok']['hashtag_count']} hashtags")
            click.echo(f"\n  Cross-platform tags:")
            for tag in result["combined_tags"][:15]:
                click.echo(f"    {tag}")
            click.echo()
        else:
            output(result)


@trends.command("music")
@click.option("--platform", "-p", default="all", show_default=True, help="Platform filter")
@click.option("--limit", "-n", type=int, default=20, show_default=True)
@handle_error
def trends_music(platform, limit):
    """Fetch trending sounds and music."""
    result = trends_mod.get_trending_music(platform=platform, limit=limit)
    if not _json_output:
        click.echo(f"\n  Trending Sounds — {platform.title()} ({result['count']} tracks)\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Rank", "Title", "Artist", "Uses", "Genre"],
            [[str(s.get("rank", i + 1)), s["title"][:35], s["artist"][:25], s.get("uses", ""), s.get("genre", "")]
             for i, s in enumerate(result["sounds"])],
        )
        click.echo()
    else:
        output(result)


@trends.command("viral")
@click.option("--niche", "-n", default="", help="Niche filter (e.g. fitness, finance, food)")
@click.option("--limit", "-l", type=int, default=10)
@handle_error
def trends_viral(niche, limit):
    """Show viral content patterns, hooks, and formats for your niche."""
    result = trends_mod.get_viral_content_signals(niche=niche, limit=limit)
    if not _json_output:
        click.echo(f"\n  Viral Content Signals — {result['niche']}\n")
        click.echo("  Proven Content Patterns:")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Pattern", "Description", "Platforms"],
            [[p["pattern"], p["desc"][:45], ", ".join(p.get("platforms", []))]
             for p in result["viral_patterns"][:8]],
        )
        click.echo("\n  Viral Hooks:")
        for hook in result["proven_hooks"][:6]:
            click.echo(f"    → {hook}")
        click.echo("\n  Best Formats:")
        skin.table(
            ["Format", "Length", "Best For", "Priority"],
            [[f["format"], f["length"], f["best_for"], f["priority"]]
             for f in result["best_formats"]],
        )
        click.echo()
    else:
        output(result)


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag optimization — generate, analyze, and strategize."""
    pass


@hashtags.command("optimize")
@click.option("--niche", "-n", required=True, help="Content niche (fitness, finance, food, etc.)")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "linkedin"], case_sensitive=False),
              show_default=True)
@click.option("--strategy", "-s", default="balanced",
              type=click.Choice(["balanced", "reach", "engagement"], case_sensitive=False),
              show_default=True, help="balanced=mix, reach=max impressions, engagement=max interactions")
@click.option("--count", "-c", type=int, default=0, help="Number of tags (0=platform default)")
@handle_error
def hashtags_optimize(niche, platform, strategy, count):
    """Generate an optimized hashtag set ready to copy-paste."""
    result = hashtags_mod.optimize_hashtags(niche, platform, strategy, count)
    get_session().record("hashtags optimize", {"niche": niche, "platform": platform, "strategy": strategy})
    if not _json_output:
        click.echo(f"\n  Hashtags for #{niche} on {platform} ({strategy} strategy)\n")
        click.echo(f"  Copy-ready ({result['count']} tags):")
        click.echo(f"\n    {result['copy_ready']}\n")
        click.echo(f"  Platform tip: {result['limits']['note']}\n")
        click.echo("  Tier breakdown:")
        for tier, tags in result["tiers_used"].items():
            if tags:
                click.echo(f"    {tier:10s}: {' '.join(tags)}")
        click.echo()
    else:
        output(result)


@hashtags.command("sets")
@click.option("--niche", "-n", required=True, help="Content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "linkedin"], case_sensitive=False),
              show_default=True)
@handle_error
def hashtags_sets(niche, platform):
    """Generate 3 hashtag sets (A/B/C variants) for rotation."""
    result = hashtags_mod.generate_hashtag_sets(niche, platform)
    if not _json_output:
        click.echo(f"\n  Hashtag Sets — {niche} / {platform} (rotate every 3–5 posts)\n")
        for strategy, data in result["sets"].items():
            click.echo(f"  [{strategy.upper()}] {data['use_case']}")
            click.echo(f"    {data['copy_ready']}\n")
        click.echo(f"  Tip: {result['rotation_tip']}\n")
        click.echo(f"  Platform: {result['platform_tip']}\n")
    else:
        output(result)


@hashtags.command("analyze")
@click.option("--tag", "-t", required=True, help="Hashtag to analyze (with or without #)")
@handle_error
def hashtags_analyze(tag):
    """Analyze a hashtag's tier, competition, and best use."""
    result = hashtags_mod.analyze_hashtag(tag)
    if not _json_output:
        click.echo(f"\n  Hashtag Analysis: {result['tag']}\n")
        for k, v in result.items():
            if k != "tag":
                click.echo(f"    {k:25s}: {v}")
        click.echo()
    else:
        output(result)


@hashtags.command("niches")
@handle_error
def hashtags_niches():
    """List all supported niches."""
    result = hashtags_mod.list_all_niches()
    if not _json_output:
        click.echo(f"\n  Supported Niches ({len(result)} total)\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Total Tags", "Tiers"],
            [[n["niche"], str(n["total_tags"]), ", ".join(n["tiers"])]
             for n in result],
        )
        click.echo()
    else:
        output(result)


@hashtags.command("strategy")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@handle_error
def hashtags_strategy(platform):
    """Full hashtag strategy guide for a platform."""
    result = hashtags_mod.get_platform_strategy(platform)
    if not _json_output:
        click.echo(f"\n  Hashtag Strategy — {platform.title()}\n")
        click.echo(f"  Strategy: {result.get('strategy', '')}\n")
        click.echo(f"  Limits: {result['limits']['note']}\n")
        click.echo("  DO:")
        for do in result.get("dos", []):
            click.echo(f"    ✓ {do}")
        click.echo("\n  DON'T:")
        for dont in result.get("donts", []):
            click.echo(f"    ✗ {dont}")
        click.echo(f"\n  Growth Hack: {result.get('growth_hack', '')}\n")
    else:
        output(result)


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization — bio, strategy, schedule, engagement, audit."""
    pass


@account.command("bio")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@handle_error
def account_bio(platform):
    """Get an optimized bio formula and examples for your platform."""
    result = optimizer_mod.get_bio_optimization(platform)
    if not _json_output:
        click.echo(f"\n  Bio Optimization — {platform.title()}\n")
        click.echo(f"  Formula: {result['formula']}")
        click.echo(f"  Char limit: {result['char_limit']}\n")
        click.echo("  Examples:")
        for ex in result.get("examples", []):
            click.echo(f"\n    \"{ex}\"")
        click.echo("\n  Tips:")
        for tip in result.get("tips", []):
            click.echo(f"    → {tip}")
        click.echo()
    else:
        output(result)


@account.command("strategy")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"], case_sensitive=False))
@click.option("--niche", "-n", default="general", show_default=True)
@handle_error
def account_strategy(platform, niche):
    """Get a full content strategy: pillars, frequency, and best post times."""
    result = optimizer_mod.get_content_strategy(platform, niche)
    if not _json_output:
        click.echo(f"\n  Content Strategy — {platform.title()} / {niche}\n")
        click.echo("  Content Pillars:")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Pillar", "% of Posts", "Description"],
            [[p["pillar"], f"{p['pct']}%", p["desc"][:50]]
             for p in result["content_pillars"]],
        )
        freq = result["posting_frequency"]
        click.echo(f"\n  Posting Frequency: {freq['recommended']}x {freq['unit']}")
        click.echo(f"  Frequency Note: {freq['note']}")
        if result["best_times"]:
            click.echo(f"\n  Best Times to Post:")
            for t in result["best_times"]:
                click.echo(f"    → {t}")
        click.echo(f"\n  Repurpose Tip: {result['repurposing_tip']}\n")
    else:
        output(result)


@account.command("schedule")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"], case_sensitive=False))
@click.option("--niche", "-n", default="general", show_default=True)
@click.option("--posts-per-week", "-w", type=int, default=7, show_default=True)
@handle_error
def account_schedule(platform, niche, posts_per_week):
    """Generate a weekly posting schedule with time slots and content types."""
    result = optimizer_mod.get_posting_schedule(platform, niche, posts_per_week)
    if not _json_output:
        click.echo(f"\n  Weekly Posting Schedule — {platform.title()} / {niche}\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Day", "Time", "Pillar", "Content Type"],
            [[s["day"], s["time"], s["pillar"], s["content_type"][:35]]
             for s in result["schedule"]],
        )
        click.echo(f"\n  Tip: {result['tip']}\n")
    else:
        output(result)


@account.command("engagement")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@handle_error
def account_engagement(platform):
    """Get engagement tactics ranked by impact."""
    result = optimizer_mod.get_engagement_tactics(platform)
    if not _json_output:
        click.echo(f"\n  Engagement Tactics — {platform.title()} ({result['tactic_count']} tactics)\n")
        for tactic in result["priority_order"]:
            impact_color = "⚡" if tactic["impact"] in ("VERY HIGH", "HIGH") else "○"
            click.echo(f"  {impact_color} [{tactic['impact']}] {tactic['tactic']}")
            click.echo(f"    {tactic['desc']}")
            click.echo(f"    Example: {tactic['example']}\n")
    else:
        output(result)


@account.command("audit")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.option("--niche", "-n", default="general", show_default=True)
@handle_error
def account_audit(platform, niche):
    """Full account optimization audit checklist."""
    result = optimizer_mod.get_account_audit(platform, niche)
    if not _json_output:
        click.echo(f"\n  Account Audit — {platform.title()} / {niche}\n")
        categories: dict[str, list] = {}
        for item in result["audit_checklist"]:
            cat = item["category"]
            categories.setdefault(cat, []).append(item)
        for cat, items in categories.items():
            click.echo(f"  {cat}:")
            for it in items:
                impact = "⚡" if it["impact"] in ("VERY HIGH", "HIGH") else "○"
                click.echo(f"    {impact} [{it['effort']} effort] {it['item']}")
            click.echo()
    else:
        output(result)


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page strategy — niches, content plans, monetization, conversions."""
    pass


@theme.command("guide")
@handle_error
def theme_guide():
    """Complete theme page growth playbook from day 1 to monetization."""
    result = theme_mod.get_theme_page_guide()
    if not _json_output:
        what = result["what_is_a_theme_page"]
        click.echo(f"\n  What is a Theme Page?\n")
        click.echo(f"  {what['definition']}\n")
        click.echo(f"  Why it works: {what['why_it_works']}\n")
        click.echo("  The 4-Phase Playbook:\n")
        for phase in result["phases"]:
            click.echo(f"  Phase {phase['phase']}: {phase['title']} ({phase['duration']})")
            for action in phase["actions"]:
                click.echo(f"    → {action}")
            click.echo()
        click.echo("  Repost / Curation Guide:")
        repost = result["repost_guide"]
        for k, v in repost.items():
            click.echo(f"    {k}: {v}")
        click.echo()
    else:
        output(result)


@theme.command("niches")
@click.option("--sort", "-s", default="monetization",
              type=click.Choice(["monetization", "growth_speed", "difficulty", "ease"], case_sensitive=False),
              show_default=True)
@handle_error
def theme_niches(sort):
    """List profitable theme page niches sorted by key metric."""
    result = theme_mod.get_profitable_niches(sort_by=sort)
    if not _json_output:
        click.echo(f"\n  Profitable Niches — sorted by {sort}\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Monetization", "Growth Speed", "Difficulty", "Brand Deal Range"],
            [[n["display"], n["monetization_potential"], n["growth_speed"],
              n["difficulty"], n.get("brand_deal_range", "")]
             for n in result],
        )
        click.echo()
    else:
        output(result)


@theme.command("plan")
@click.option("--niche", "-n", required=True, help="Theme page niche")
@click.option("--days", "-d", type=int, default=7, show_default=True)
@click.option("--platform", "-p", default="tiktok", show_default=True)
@handle_error
def theme_plan(niche, days, platform):
    """Generate a day-by-day content plan for your theme page."""
    result = theme_mod.generate_content_plan(niche, days, platform)
    if not _json_output:
        click.echo(f"\n  {days}-Day Content Plan — {niche} / {platform}\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Day", "Day", "Pillar", "Format", "Hook Template"],
            [[str(d["day"]), d["day_of_week"], d["pillar"], d["content_format"][:25], d["hook_template"][:40]]
             for d in result["plan"]],
        )
        click.echo(f"\n  Pro Tip: {result['pro_tip']}")
        click.echo(f"  Repurpose: {result['repurpose_tip']}\n")
    else:
        output(result)


@theme.command("monetize")
@click.option("--niche", "-n", default="", help="Niche filter for relevant strategies")
@handle_error
def theme_monetize(niche):
    """Monetization strategies ranked by timeline and earning potential."""
    result = theme_mod.get_monetization_strategies(niche)
    if not _json_output:
        niche_display = result.get("niche", "general")
        click.echo(f"\n  Monetization Strategies — {niche_display}\n")
        if result.get("recommended_order"):
            click.echo(f"  Recommended order: {' → '.join(result['recommended_order'])}\n")
        for s in result["strategies"]:
            click.echo(f"  [{s['timeline']}] {s['method']}")
            click.echo(f"    Earning potential: {s['earning_potential']}")
            click.echo(f"    Effort: {s['effort']}")
            click.echo(f"    How: {s['how']}")
            for tip in s.get("tips", [])[:2]:
                click.echo(f"    → {tip}")
            click.echo()
    else:
        output(result)


@theme.command("convert")
@handle_error
def theme_convert():
    """Follower-to-customer conversion tactics and DM funnel strategies."""
    result = theme_mod.get_conversion_tactics()
    if not _json_output:
        click.echo("\n  Follower → Customer Conversion Playbook\n")
        funnel = result["funnel_overview"]
        click.echo("  Funnel Stages:")
        for k, v in funnel.items():
            click.echo(f"    {v}")
        click.echo("\n  DM Funnel Tactics:")
        for dm in result["dm_funnels"]:
            click.echo(f"\n  [{dm['conversion_rate']} CVR] {dm['tactic']}")
            click.echo(f"    {dm['desc']}")
            click.echo(f"    Example: {dm['example']}")
        click.echo("\n  Link-in-Bio Priority Order:")
        for item in result["link_in_bio_strategy"]["priority_order"]:
            click.echo(f"    {item}")
        click.echo(f"\n  Tip: {result['link_in_bio_strategy']['tip']}")
        click.echo("\n  Email Welcome Sequence:")
        for email in result["email_conversion"]["welcome_sequence"]:
            click.echo(f"    → {email}")
        click.echo(f"\n  Expected: {result['email_conversion']['conversion_rate']}")
        click.echo("\n  Social Proof Plays:")
        for play in result["social_proof_plays"]:
            click.echo(f"    ✓ {play}")
        click.echo()
    else:
        output(result)


# ── config group ──────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration management — API keys and preferences."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
@handle_error
def config_set(key, value):
    """Set a config value (e.g., youtube_api_key, tiktok_api_key, default_niche)."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    display = value[:10] + "..." if "key" in key and len(value) > 10 else value
    output({"key": key, "value": display}, f"Set {key} = {display}")


@config.command("get")
@click.argument("key", required=False)
@handle_error
def config_get(key):
    """Get a config value or list all."""
    cfg = load_config()
    if key:
        val = cfg.get(key)
        if val:
            masked = val[:10] + "..." if "key" in key and len(val) > 10 else val
            output({"key": key, "value": masked}, f"{key} = {masked}")
        else:
            output({"key": key, "value": None}, f"{key} is not set")
    else:
        masked = {}
        for k, v in cfg.items():
            masked[k] = v[:10] + "..." if "key" in k and len(str(v)) > 10 else v
        output(masked, "Configuration:")


@config.command("delete")
@click.argument("key")
@handle_error
def config_delete(key):
    """Delete a config key."""
    cfg = load_config()
    if key in cfg:
        del cfg[key]
        save_config(cfg)
        output({"deleted": key}, f"Deleted {key}")
    else:
        output({"error": f"{key} not found"}, f"{key} not found")


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session management — history, undo, redo."""
    pass


@session_group.command("status")
def session_status():
    """Show session status."""
    output(get_session().status())


@session_group.command("history")
@click.option("--limit", "-n", type=int, default=20)
def session_history(limit):
    """Show command history."""
    entries = get_session().history(limit=limit)
    output(entries, f"History ({len(entries)} entries):")


@session_group.command("undo")
def session_undo():
    """Undo last command."""
    entry = get_session().undo()
    if entry:
        output(entry.to_dict(), f"Undone: {entry.command}")
    else:
        output({"error": "Nothing to undo"}, "Nothing to undo")


@session_group.command("redo")
def session_redo():
    """Redo last undone command."""
    entry = get_session().redo()
    if entry:
        output(entry.to_dict(), f"Redone: {entry.command}")
    else:
        output({"error": "Nothing to redo"}, "Nothing to redo")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "trends fetch --platform <platform>":        "Fetch viral trends (youtube/tiktok/all)",
        "trends music [--limit N]":                  "Trending sounds and music",
        "trends viral --niche <niche>":              "Viral patterns, hooks, formats",
        "hashtags optimize --niche <n> --platform p":"Generate copy-ready hashtag set",
        "hashtags sets --niche <n>":                 "3 hashtag sets for A/B rotation",
        "hashtags analyze --tag <tag>":              "Analyze a single hashtag",
        "hashtags niches":                           "List all supported niches",
        "hashtags strategy --platform <p>":          "Full hashtag strategy guide",
        "account bio --platform <p>":                "Optimized bio formula + examples",
        "account strategy --platform <p> --niche <n>":"Content pillars + posting schedule",
        "account schedule --platform <p> --niche <n>":"Weekly posting schedule",
        "account engagement --platform <p>":         "Ranked engagement tactics",
        "account audit --platform <p> --niche <n>":  "Full account optimization checklist",
        "theme guide":                               "Complete theme page playbook",
        "theme niches [--sort monetization]":        "Profitable niches ranked",
        "theme plan --niche <n> --days 7":           "Day-by-day content calendar",
        "theme monetize --niche <n>":                "Monetization strategies",
        "theme convert":                             "Follower → customer conversion tactics",
        "config set <key> <value>":                  "Set API key or preference",
        "config get":                                "Show current config",
        "session history":                           "Show command history",
        "help":                                      "Show this help",
        "quit / exit":                               "Exit",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line in ("help", "h", "?"):
            skin.help(commands)
            continue

        try:
            parts = shlex.split(line)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


def main():
    cli()


if __name__ == "__main__":
    main()
