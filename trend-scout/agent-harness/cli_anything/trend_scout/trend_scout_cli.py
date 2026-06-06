"""Trend Scout CLI — agent-native social media trend scraper.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Generates account optimization reports and theme page conversion playbooks.

Usage:
    trend-scout [--json] <command> [subcommand] [options]
    trend-scout                          (launches REPL)

Commands:
    youtube trends      Trending YouTube videos + hashtags
    youtube hashtag     Videos for a specific hashtag
    youtube categories  List available trending categories

    tiktok trends       Trending TikTok videos + hashtags + sounds
    tiktok sounds       Trending TikTok sounds/music
    tiktok hashtag      Look up a TikTok hashtag
    tiktok regions      List available regions

    optimize            Generate account optimization report
    compare             Cross-platform trend comparison
    theme-pages niches  List theme page niches
    theme-pages guide   Full guide for a niche
    theme-pages playbook Phase-by-phase conversion guide
    theme-pages tools   Recommended tools
    theme-pages sell    Platforms to buy/sell accounts

    export              Export trend data to JSON file
    repl                Start interactive REPL
"""

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.trend_scout.core import youtube as yt_mod
from cli_anything.trend_scout.core import tiktok as tt_mod
from cli_anything.trend_scout.core import optimizer as opt_mod
from cli_anything.trend_scout.core import theme_pages as tp_mod

# ── Global flags ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def _progress(msg: str) -> None:
    """Print progress message to stderr in JSON mode, stdout otherwise."""
    click.echo(msg, err=_json_output)


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
            if not v:
                click.echo(f"{pad}{k}: []")
            elif isinstance(v[0], (str, int, float)):
                click.echo(f"{pad}{k}: {', '.join(str(i) for i in v[:15])}{'...' if len(v) > 15 else ''}")
            else:
                click.echo(f"{pad}{k}: [{len(v)} items]")
                for item in v[:5]:
                    if isinstance(item, dict):
                        _print_dict(item, indent + 4)
                if len(v) > 5:
                    click.echo(f"{pad}    ... and {len(v) - 5} more")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo("  " + "  ".join(parts[:6]))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, KeyError, RuntimeError) as e:
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
@click.version_option("1.0.0", prog_name="trend-scout")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Trend Scout — scrape YouTube & TikTok for viral trends, hashtags, and music.

    \b
    Quick start:
      trend-scout youtube trends                          # YouTube trending
      trend-scout tiktok trends --region us               # TikTok US trends
      trend-scout tiktok sounds                           # Trending sounds
      trend-scout optimize --platform tiktok --niche fitness --followers 5000
      trend-scout theme-pages guide fitness               # Theme page playbook
      trend-scout compare                                 # Cross-platform analysis
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl_cmd)


# ── youtube group ─────────────────────────────────────────────────────────────

@cli.group("youtube")
def youtube_group():
    """YouTube trend scraping commands."""
    pass


@youtube_group.command("trends")
@click.option(
    "--category", "-c", default="default", show_default=True,
    help=f"Trending category: {', '.join(yt_mod.trending_categories())}"
)
@click.option("--limit", "-n", default=20, show_default=True, help="Max videos to fetch")
@handle_error
def yt_trends(category: str, limit: int) -> None:
    """Fetch trending YouTube videos with hashtags and sounds."""
    _progress(f"Fetching YouTube trending [{category}]...")
    result = yt_mod.fetch_trending(category=category, limit=limit)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        skin.section(f"YouTube Trending — {category.upper()} ({result['video_count']} videos)")
        if result["videos"]:
            skin.table(
                ["#", "Title", "Channel", "Views", "Duration", "Hashtags"],
                [
                    [
                        str(i + 1),
                        v["title"][:35],
                        v["channel"][:20],
                        f"{v['view_count']:,}" if v["view_count"] else "-",
                        str(v["duration"]),
                        " ".join(f"#{t}" for t in v["hashtags"][:3]),
                    ]
                    for i, v in enumerate(result["videos"][:15])
                ],
            )

        skin.section(f"Top Hashtags ({len(result['top_hashtags'])})")
        skin.bullet_list([f"#{t}" for t in result["top_hashtags"][:20]])

        if result["top_sounds"]:
            skin.section("Trending Sounds / Tracks")
            skin.bullet_list(result["top_sounds"])
    else:
        output(result)


@youtube_group.command("hashtag")
@click.argument("hashtag")
@click.option("--limit", "-n", default=10, show_default=True)
@handle_error
def yt_hashtag(hashtag: str, limit: int) -> None:
    """Fetch YouTube videos for a specific hashtag."""
    _progress(f"Fetching YouTube #{hashtag}...")
    result = yt_mod.fetch_hashtag_videos(hashtag, limit)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"#{hashtag} on YouTube ({result['video_count']} videos)")
        if result["videos"]:
            skin.table(
                ["Title", "Channel", "Views", "Upload"],
                [
                    [v["title"][:40], v["channel"][:25], f"{v['view_count']:,}", v["upload_date"]]
                    for v in result["videos"]
                ],
            )
    else:
        output(result)


@youtube_group.command("categories")
def yt_categories() -> None:
    """List available YouTube trending categories."""
    cats = yt_mod.trending_categories()
    if _json_output:
        output(cats)
    else:
        click.echo("Available YouTube trending categories:")
        for c in cats:
            click.echo(f"  • {c}")


# ── tiktok group ──────────────────────────────────────────────────────────────

@cli.group("tiktok")
def tiktok_group():
    """TikTok trend scraping commands."""
    pass


@tiktok_group.command("trends")
@click.option(
    "--region", "-r", default="us", show_default=True,
    help=f"Region code: {', '.join(tt_mod.available_regions())}"
)
@click.option("--limit", "-n", default=20, show_default=True)
@handle_error
def tt_trends(region: str, limit: int) -> None:
    """Fetch trending TikTok videos, hashtags, and sounds."""
    _progress(f"Fetching TikTok trending [{region.upper()}]...")
    result = tt_mod.fetch_trending(region=region, limit=limit)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        live_note = "" if result["live_data"] else " [curated fallback — live API blocked]"
        skin.section(f"TikTok Trending — {region.upper()}{live_note}")

        if result["videos"]:
            skin.table(
                ["Author", "Plays", "Likes", "Sound", "Hashtags"],
                [
                    [
                        f"@{v['author'][:20]}",
                        f"{v['play_count']:,}" if v["play_count"] else "-",
                        f"{v['like_count']:,}" if v["like_count"] else "-",
                        v["sound"].get("title", "")[:25] if v.get("sound") else "-",
                        " ".join(f"#{t}" for t in v["hashtags"][:3]),
                    ]
                    for v in result["videos"][:15]
                ],
            )

        skin.section(f"Top Hashtags ({len(result['top_hashtags'])})")
        skin.bullet_list([f"#{t}" for t in result["top_hashtags"][:25]])

        skin.section(f"Trending Sounds ({len(result['trending_sounds'])})")
        skin.table(
            ["Title", "Artist", "Video Count"],
            [
                [s.get("title", "")[:35], s.get("artist", "")[:25], f"{s.get('video_count', 0):,}"]
                for s in result["trending_sounds"][:10]
            ],
        )
    else:
        output(result)


@tiktok_group.command("sounds")
@click.option("--region", "-r", default="us", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
@handle_error
def tt_sounds(region: str, limit: int) -> None:
    """Fetch trending TikTok sounds and music."""
    _progress(f"Fetching TikTok trending sounds [{region.upper()}]...")
    result = tt_mod.fetch_trending_sounds(region=region, limit=limit)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        live_note = "" if result["live_data"] else " [curated fallback]"
        skin.section(f"Trending Sounds — TikTok {region.upper()}{live_note}")
        skin.table(
            ["#", "Title", "Artist", "Video Count"],
            [
                [str(i + 1), s.get("title", "")[:40], s.get("artist", "")[:30], f"{s.get('video_count', 0):,}"]
                for i, s in enumerate(result["sounds"])
            ],
        )
    else:
        output(result)


@tiktok_group.command("hashtag")
@click.argument("hashtag")
@handle_error
def tt_hashtag(hashtag: str) -> None:
    """Look up stats for a TikTok hashtag/challenge."""
    _progress(f"Looking up #{hashtag} on TikTok...")
    result = tt_mod.fetch_hashtag(hashtag)
    output(result, f"TikTok #{result.get('name', hashtag)}")


@tiktok_group.command("regions")
def tt_regions() -> None:
    """List available TikTok regions."""
    regions = tt_mod.available_regions()
    if _json_output:
        output(regions)
    else:
        click.echo("Available TikTok regions:")
        for r in regions:
            click.echo(f"  • {r}")


# ── optimize ──────────────────────────────────────────────────────────────────

@cli.command("optimize")
@click.option(
    "--platform", "-p", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
    help="Social platform"
)
@click.option("--niche", "-n", required=True, help="Content niche (e.g. fitness, travel, finance)")
@click.option("--followers", "-f", default=1000, show_default=True, type=int, help="Current follower count")
@click.option("--pull-trends", is_flag=True, default=False, help="Fetch live trend data to include in report")
@handle_error
def optimize(platform: str, niche: str, followers: int, pull_trends: bool) -> None:
    """Generate an account optimization report with posting times, hashtags, and tactics."""
    trending_hashtags: list[str] = []
    trending_sounds: list[dict] = []

    if pull_trends:
        _progress(f"Pulling live trends for {platform}...")
        if platform in ("tiktok", "instagram"):
            tt_data = tt_mod.fetch_trending(region="us")
            trending_hashtags = tt_data.get("top_hashtags", [])
            trending_sounds = tt_data.get("trending_sounds", [])
        elif platform == "youtube":
            yt_data = yt_mod.fetch_trending()
            trending_hashtags = yt_data.get("top_hashtags", [])

    if not trending_hashtags:
        trending_hashtags = ["fyp", "viral", "trending", "foryou", niche.lower()]

    report = opt_mod.generate_report(
        platform=platform,
        niche=niche,
        follower_count=followers,
        trending_hashtags=trending_hashtags,
        trending_sounds=trending_sounds,
    )

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        skin.section(f"Account Optimization Report — {platform.upper()} / {niche}")
        click.echo(f"  Tier: {report['tier'].upper()} ({report['follower_count']:,} followers)")

        skin.section("Best Posting Times — Today")
        today = report["posting_times"]["today"]
        click.echo(f"  {today['day'].title()}: {', '.join(today['windows']) or 'No specific window'}")

        skin.section("Hashtag Strategy")
        hs = report["hashtag_strategy"]
        click.echo(f"  Recommended count: {hs['recommended_count']}")
        click.echo(f"  Mix: {hs['mix']}")
        click.echo(f"  Note: {hs['note']}")
        click.echo(f"  Top trending to use: {', '.join(hs['top_trending_to_use'][:5])}")
        click.echo(f"  Niche tags: {', '.join(hs['niche_hashtags_to_rotate'][:5])}")

        skin.section("Content Formats")
        skin.bullet_list(report["content_pillars"]["formats"])
        click.echo(f"  Post frequency: {report['content_pillars']['post_frequency']}")

        if report["sound_recommendations"]:
            skin.section("Trending Sounds to Use")
            skin.bullet_list(report["sound_recommendations"])

        skin.section("Growth Tactics")
        skin.bullet_list(report["growth_tactics"][:6])

        skin.section("Monetization Milestones")
        skin.table(
            ["Milestone", "Unlocks"],
            [[m["milestone"], m["unlocks"][:60]] for m in report["monetization_milestones"]],
        )
    else:
        output(report)


# ── compare ───────────────────────────────────────────────────────────────────

@cli.command("compare")
@click.option("--limit", "-n", default=10, show_default=True)
@handle_error
def compare(limit: int) -> None:
    """Compare trends across YouTube and TikTok to find cross-platform opportunities."""
    _progress("Fetching YouTube trends...")
    yt_data = yt_mod.fetch_trending(limit=limit)
    _progress("Fetching TikTok trends...")
    tt_data = tt_mod.fetch_trending()

    result = opt_mod.compare_trends(yt_data, tt_data)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        skin.section("Cross-Platform Trend Analysis")

        if result["cross_platform_hashtags"]:
            skin.section("Hashtags Trending on BOTH YouTube & TikTok")
            skin.bullet_list([f"#{t}" for t in result["cross_platform_hashtags"][:15]])
        else:
            click.echo("  No exact cross-platform hashtag overlap found (normal — platforms use different tag styles)")

        skin.section("YouTube-Only Trending Tags")
        skin.bullet_list([f"#{t}" for t in result["youtube_only_tags"][:10]])

        skin.section("TikTok-Only Trending Tags")
        skin.bullet_list([f"#{t}" for t in result["tiktok_only_tags"][:10]])

        skin.section("Recommendation")
        click.echo(f"  {result['recommendation']}")

        skin.section("Action Items This Week")
        skin.bullet_list(result["action_items"])
    else:
        output(result)


# ── theme-pages group ─────────────────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages_group():
    """Theme page creation, conversion, and monetization guides."""
    pass


@theme_pages_group.command("niches")
@handle_error
def tp_niches() -> None:
    """List all supported theme page niches with key stats."""
    result = tp_mod.list_niches()

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Theme Page Niches ({len(result)} available)")
        skin.table(
            ["Niche", "Description", "Avg CPM", "Competition", "Growth Speed"],
            [
                [
                    n["niche"],
                    n["description"][:35],
                    n["avg_cpm"],
                    n["competition"],
                    n["growth_speed"],
                ]
                for n in result
            ],
        )
    else:
        output(result)


@theme_pages_group.command("guide")
@click.argument("niche")
@handle_error
def tp_guide(niche: str) -> None:
    """Get a complete theme page guide for a specific niche."""
    result = tp_mod.get_niche_guide(niche)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Theme Page Guide — {result['niche'].upper()}")
        click.echo(f"  Description: {result['description']}")
        click.echo(f"  Avg CPM: {result['avg_cpm']}")
        click.echo(f"  Competition: {result['competition']}")
        click.echo(f"  Growth Speed: {result['growth_speed']}")

        skin.section("Monetization Methods")
        skin.bullet_list(result["monetization"])

        skin.section("Content Sources")
        skin.bullet_list(result["content_sources"])

        skin.section("Recommended Tools")
        skin.bullet_list(result["tools"])

        skin.section("Quick Start Checklist")
        for step in result["quick_start_checklist"]:
            click.echo(f"  {step}")
    else:
        output(result)


@theme_pages_group.command("playbook")
@click.option(
    "--phase", default=None,
    type=click.Choice(["1", "2", "3", "4"]),
    help="Show a specific phase only"
)
@handle_error
def tp_playbook(phase: Optional[str]) -> None:
    """Show the 4-phase theme page conversion and monetization playbook."""
    result = tp_mod.get_conversion_playbook(phase)

    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        if phase:
            skin.section(result.get("name", f"Phase {phase}"))
            click.echo(f"  Duration: {result.get('duration', '')}")
            click.echo(f"  Goal: {result.get('goal', '')}")
            skin.section("Actions")
            skin.bullet_list(result.get("actions", []))
            if "revenue_targets" in result:
                skin.section("Revenue Targets")
                _print_dict(result["revenue_targets"])
        else:
            skin.section("Theme Page Conversion Playbook")
            click.echo(f"  {result.get('key_principle', '')}")
            click.echo(f"  Timeline: {result.get('total_timeline', '')}")
            for p in result.get("phases", []):
                skin.section(p.get("name", "Phase"))
                click.echo(f"    Duration: {p.get('duration', '')}")
                click.echo(f"    Goal: {p.get('goal', '')}")
                for action in p.get("actions", [])[:4]:
                    click.echo(f"    • {action}")
    else:
        output(result)


@theme_pages_group.command("tools")
@handle_error
def tp_tools() -> None:
    """List recommended tools for running and growing theme pages."""
    result = tp_mod.get_tools()
    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Recommended Theme Page Tools")
        skin.table(
            ["Tool", "Purpose", "Cost", "Best For"],
            [[t["name"], t["purpose"][:40], t["cost"], t["platform"]] for t in result],
        )
    else:
        output(result)


@theme_pages_group.command("sell")
@handle_error
def tp_sell() -> None:
    """List platforms to buy or sell social media accounts."""
    result = tp_mod.get_selling_platforms()
    if not _json_output:
        from cli_anything.trend_scout.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Account Buying/Selling Platforms")
        skin.table(
            ["Platform", "URL", "Fee", "Best For"],
            [[p["name"], p["url"], p["fee"], p["best_for"]] for p in result],
        )
    else:
        output(result)


# ── export ────────────────────────────────────────────────────────────────────

@cli.command("export")
@click.option("-o", "--output-file", required=True, help="Output JSON file path")
@click.option(
    "--source", "-s", default="both",
    type=click.Choice(["youtube", "tiktok", "both"]),
    help="Which platform(s) to export"
)
@click.option("--region", "-r", default="us", help="TikTok region")
@click.option("--category", "-c", default="default", help="YouTube category")
@handle_error
def export_cmd(output_file: str, source: str, region: str, category: str) -> None:
    """Export trend data to a JSON file for content planning."""
    bundle: dict = {"exported_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime())}

    if source in ("youtube", "both"):
        _progress("Fetching YouTube trends...")
        bundle["youtube"] = yt_mod.fetch_trending(category=category)

    if source in ("tiktok", "both"):
        _progress("Fetching TikTok trends...")
        bundle["tiktok"] = tt_mod.fetch_trending(region=region)

    if source == "both":
        _progress("Running cross-platform analysis...")
        bundle["cross_platform"] = opt_mod.compare_trends(
            bundle.get("youtube", {}), bundle.get("tiktok", {})
        )

    import pathlib
    pathlib.Path(output_file).write_text(json.dumps(bundle, indent=2, default=str))
    click.echo(f"✓ Exported to {output_file}")

    if not _json_output:
        keys = [k for k in bundle.keys() if k != "exported_at"]
        click.echo(f"  Sections: {', '.join(keys)}")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command("repl")
def repl_cmd() -> None:
    """Start the interactive trend-scout REPL."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.trend_scout.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _commands = {
        "youtube trends [-c music|gaming|movies]": "YouTube trending videos + hashtags",
        "youtube hashtag <tag>":                   "Videos for a YouTube hashtag",
        "youtube categories":                      "List trending categories",
        "tiktok trends [-r us|uk|ca|au]":          "TikTok trending videos + hashtags + sounds",
        "tiktok sounds [-r us]":                   "Trending TikTok sounds",
        "tiktok hashtag <tag>":                    "Look up a TikTok hashtag",
        "optimize -p tiktok -n fitness -f 5000":   "Account optimization report",
        "compare":                                 "Cross-platform trend analysis",
        "theme-pages niches":                      "List theme page niches",
        "theme-pages guide <niche>":               "Full guide for a niche",
        "theme-pages playbook [--phase 1|2|3|4]":  "Monetization playbook",
        "theme-pages tools":                       "Recommended tools",
        "theme-pages sell":                        "Where to buy/sell accounts",
        "export -o trends.json":                   "Export trend data to file",
        "help":                                    "Show this help",
        "quit / exit":                             "Exit",
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
