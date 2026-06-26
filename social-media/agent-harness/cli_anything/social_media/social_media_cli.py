"""Social Media CLI — Agent-native trend intelligence + account optimizer.

Scrapes TikTok and YouTube for viral trends, hashtags, and music.
Generates account optimization checklists and theme page playbooks.
Designed for AI agents (Claude Code, OpenCode, Codex) and humans alike.

Usage:
    python3 -m cli_anything.social_media [--json] <command>
    python3 -m cli_anything.social_media  (launches REPL)

Commands:
    trends          Fetch viral trends from TikTok and YouTube
    hashtags        Generate optimized hashtag sets for any niche
    music           List trending audio tracks
    accounts        Get platform-specific account optimization checklists
    themes          Theme page creation + conversion strategy
    optimize        Full account optimization audit
"""

import json
import sys
import shlex
import click
from typing import Any, Optional

from cli_anything.social_media.scrapers import tiktok as tt_scraper
from cli_anything.social_media.scrapers import youtube as yt_scraper
from cli_anything.social_media.core import accounts as acct_mod
from cli_anything.social_media.core import hashtags as ht_mod
from cli_anything.social_media.core import theme_pages as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.secho(message, fg="cyan", bold=True)
        _pretty_print(data)


def _pretty_print(data: Any, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.secho(f"{pad}{k}:", fg="yellow")
                _pretty_print(v, indent + 1)
            else:
                click.echo(f"{pad}  {click.style(k, fg='green')}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.secho(f"{pad}  [{i + 1}]", fg="magenta")
                _pretty_print(item, indent + 2)
            else:
                click.echo(f"{pad}  • {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.secho(f"Error: {msg}", fg="red", err=True)


def _section(title: str) -> None:
    if not _json_output:
        click.secho(f"\n{'─' * 60}", fg="blue")
        click.secho(f"  {title}", fg="blue", bold=True)
        click.secho(f"{'─' * 60}", fg="blue")


# ── CLI root ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output machine-readable JSON")
@click.pass_context
def cli(ctx: click.Context, json_mode: bool) -> None:
    """Social Media CLI — viral trend intelligence + account optimizer."""
    global _json_output
    _json_output = json_mode

    if ctx.invoked_subcommand is None:
        _launch_repl()


# ── trends ────────────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch viral trends from TikTok and/or YouTube."""


@trends.command("tiktok")
@click.option("--live", is_flag=True, help="Attempt live scrape from tokchart.com (requires requests+bs4)")
@click.option("--section", type=click.Choice(["sounds", "hashtags", "formats", "moments", "all"]),
              default="all", help="Which section to show")
def trends_tiktok(live: bool, section: str) -> None:
    """Fetch TikTok viral trends — sounds, hashtags, formats, cultural moments."""
    report = tt_scraper.fetch_trends(use_live=live)

    if _json_output:
        full = {
            "platform": report.platform,
            "fetched_at": report.fetched_at,
            "source": report.source,
            "trending_sounds": report.trending_sounds,
            "trending_hashtags": report.trending_hashtags,
            "trending_formats": report.trending_formats,
            "cultural_moments": report.cultural_moments,
        }
        if section != "all":
            key = {
                "sounds": "trending_sounds",
                "hashtags": "trending_hashtags",
                "formats": "trending_formats",
                "moments": "cultural_moments",
            }.get(section, "trending_sounds")
            full = {"platform": report.platform, key: full[key]}
        click.echo(json.dumps(full, indent=2, default=str))
        return

    _section("TikTok Viral Trends — June 2026")
    if section in ("sounds", "all"):
        output({"trending_sounds": report.trending_sounds}, "Trending Sounds")
    if section in ("hashtags", "all"):
        output({"trending_hashtags": report.trending_hashtags}, "Trending Hashtags")
    if section in ("formats", "all"):
        output({"trending_formats": report.trending_formats}, "Trending Formats & Challenges")
    if section in ("moments", "all"):
        output({"cultural_moments": report.cultural_moments}, "Cultural Moments to Ride")


@trends.command("youtube")
@click.option("--live", is_flag=True, help="Use YouTube Data API (requires YOUTUBE_API_KEY env var)")
@click.option("--section", type=click.Choice(["niches", "hashtags", "strategy", "formats", "all"]),
              default="all", help="Which section to show")
def trends_youtube(live: bool, section: str) -> None:
    """Fetch YouTube Shorts viral trends — niches, hashtags, format tips."""
    report = yt_scraper.fetch_trends(use_live=live)
    _section("YouTube Shorts Trends — June 2026")

    if section in ("niches", "all"):
        output({"trending_niches": report.trending_niches}, "Top Trending Niches")
    if section in ("hashtags", "all"):
        output({"top_hashtags": report.top_hashtags}, "Top Hashtags")
    if section in ("strategy", "all"):
        output({"hashtag_strategy": report.hashtag_strategy}, "Hashtag Strategy")
    if section in ("formats", "all"):
        output({"format_tips": report.format_tips}, "Format Tips")

    if _json_output:
        click.echo(json.dumps({
            "platform": report.platform,
            "fetched_at": report.fetched_at,
            "source": report.source,
            "trending_niches": report.trending_niches,
            "top_hashtags": report.top_hashtags,
            "hashtag_strategy": report.hashtag_strategy,
            "format_tips": report.format_tips,
        }, indent=2, default=str))


@trends.command("all")
@click.option("--live", is_flag=True, help="Attempt live data where available")
def trends_all(live: bool) -> None:
    """Fetch trends from all platforms (TikTok + YouTube)."""
    tt = tt_scraper.fetch_trends(use_live=live)
    yt = yt_scraper.fetch_trends(use_live=live)

    combined = {
        "tiktok": {
            "top_sounds": tt.trending_sounds[:5],
            "top_hashtags": [h["tag"] for h in tt.trending_hashtags[:8]],
            "trending_formats": tt.trending_formats[:5],
        },
        "youtube": {
            "top_niches": yt.trending_niches[:5],
            "top_hashtags": [h["tag"] for h in yt.top_hashtags[:8]],
            "format_tips": yt.format_tips[:5],
        },
        "shared_cultural_moments": tt.cultural_moments,
        "action_items": [
            f"Use '{tt.trending_sounds[0]['title']}' by {tt.trending_sounds[0]['artist']} for TikTok ASAP",
            f"Post World Cup content with #WorldCup2026 — trending on BOTH platforms",
            "Olivia Rodrigo album dropped Jun 12 — lyric/reaction content still viral this week",
            "House of Dragon S3 started Jun 21 — prediction/recap content is hot NOW",
        ],
    }

    _section("Cross-Platform Trend Report — TikTok + YouTube — June 2026")
    if _json_output:
        click.echo(json.dumps(combined, indent=2))
    else:
        output(combined)


# ── hashtags ──────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Target platform")
@click.option("--count", "-n", default=None, type=int, help="Number of hashtags (default: platform optimal)")
@click.option("--no-trending", is_flag=True, help="Exclude trending moment tags")
def hashtags(niche: str, platform: str, count: Optional[int], no_trending: bool) -> None:
    """Generate an optimized hashtag set for NICHE on PLATFORM.

    Examples:
        social-media hashtags fitness --platform tiktok
        social-media hashtags finance --platform youtube --count 5
        social-media hashtags lifestyle --platform instagram
    """
    result = ht_mod.generate_hashtag_set(
        niche=niche,
        platform=platform,
        include_trending=not no_trending,
        count=count,
    )
    _section(f"Hashtag Set — {niche.title()} / {platform.title()}")
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        click.secho(f"\n  Ready to copy:\n  {result['formatted']}\n", fg="green", bold=True)
        output({k: v for k, v in result.items() if k != "formatted"})


# ── music ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "both"]))
@click.option("--category", "-c", default=None, help="Filter by category (e.g. dance, summer, sports)")
def music(platform: str, category: Optional[str]) -> None:
    """List trending audio tracks for TikTok and/or YouTube."""
    _section(f"Trending Music — {platform.title()} — June 2026")

    if platform in ("tiktok", "both"):
        report = tt_scraper.fetch_trends()
        sounds = report.trending_sounds
        if category:
            sounds = [s for s in sounds if category.lower() in s.get("category", "").lower()]
        click.secho("TikTok Trending Sounds:", fg="cyan", bold=True)
        if _json_output:
            click.echo(json.dumps({"tiktok_sounds": sounds}, indent=2))
        else:
            for i, s in enumerate(sounds, 1):
                click.echo(f"\n  [{i}] {click.style(s['title'], bold=True)} — {s['artist']}")
                click.echo(f"      Videos using it: {s['video_count']:,}")
                click.echo(f"      Growth: {s['growth_rate']}")
                click.echo(f"      Best for: {s['use_case']}")

    if platform in ("youtube", "both"):
        click.secho("\nYouTube Shorts Audio Tips:", fg="cyan", bold=True)
        tips = [
            "Use audio from YouTube's built-in Shorts sound library (arrow icon = trending)",
            "DO NOT use TikTok audio rips — YouTube flags and de-distributes these",
            "Trending YT sounds: Olivia Rodrigo tracks (album Jun 12), World Cup anthems",
            "Original audio + voiceover often outperforms music for educational content",
            "Use YouTube Audio Library for royalty-free tracks if doing faceless content",
        ]
        if _json_output:
            click.echo(json.dumps({"youtube_audio_tips": tips}, indent=2))
        else:
            for tip in tips:
                click.echo(f"  • {tip}")


# ── accounts ──────────────────────────────────────────────────────────────────

@cli.group()
def accounts() -> None:
    """Platform-specific account optimization checklists and audits."""


@accounts.command("optimize")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--handle", default="", help="Account handle (for personalized audit)")
@click.option("--niche", default="", help="Your content niche")
@click.option("--followers", default=0, type=int, help="Current follower count")
def accounts_optimize(platform: str, handle: str, niche: str, followers: int) -> None:
    """Get full optimization checklist for PLATFORM.

    Examples:
        social-media accounts optimize tiktok --niche fitness --followers 2500
        social-media accounts optimize all
    """
    platforms = ["tiktok", "youtube", "instagram"] if platform == "all" else [platform]

    for plat in platforms:
        _section(f"Account Optimization — {plat.title()}")
        profile = None
        if handle or followers:
            profile = acct_mod.AccountProfile(
                platform=plat,
                handle=handle,
                niche=niche,
                follower_count=followers,
                bio_set=bool(handle),
                profile_pic_set=bool(handle),
            )
        result = acct_mod.get_optimization_checklist(plat, profile)
        if _json_output:
            click.echo(json.dumps(result, indent=2))
        else:
            output(result)


@accounts.command("audit")
@click.argument("platform")
@click.option("--handle", required=True, help="Your @handle")
@click.option("--followers", default=0, type=int)
@click.option("--niche", default="general")
@click.option("--bio/--no-bio", default=True)
@click.option("--link/--no-link", default=False)
@click.option("--pinned/--no-pinned", default=False)
def accounts_audit(platform: str, handle: str, followers: int, niche: str,
                   bio: bool, link: bool, pinned: bool) -> None:
    """Run a quick audit on a specific account."""
    profile = acct_mod.AccountProfile(
        platform=platform,
        handle=handle,
        niche=niche,
        follower_count=followers,
        bio_set=bio,
        link_in_bio=link,
        pinned_post=pinned,
        profile_pic_set=bool(handle),
    )
    result = acct_mod.get_optimization_checklist(platform, profile)
    _section(f"Account Audit — @{handle} ({platform.title()})")
    if _json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        output(result)


# ── themes ────────────────────────────────────────────────────────────────────

@cli.group()
def themes() -> None:
    """Theme page creation guide, niche finder, and conversion strategy."""


@themes.command("niches")
@click.option("--keywords", "-k", multiple=True, help="Your interests (can use multiple: -k fitness -k motivation)")
@click.option("--monetization", "-m", default="any", help="Preferred monetization: affiliate, digital, coaching, sponsorship")
def themes_niches(keywords: tuple, monetization: str) -> None:
    """Discover high-converting theme page niches matching your interests."""
    kw_list = list(keywords) if keywords else None
    niches = theme_mod.get_niche_recommendations(kw_list, monetization)
    _section("High-Converting Theme Page Niches")
    if _json_output:
        click.echo(json.dumps(niches, indent=2))
    else:
        for n in niches:
            click.secho(f"\n  {n['niche']}", fg="cyan", bold=True)
            click.echo(f"    Why it converts: {n['why_converts']}")
            click.echo(f"    Avg CPM: {n['avg_cpm']}")
            click.echo(f"    Monetization: {', '.join(n['monetization'][:2])}")
            click.echo(f"    Content pillars: {', '.join(n['content_pillars'][:3])}")
            click.echo(f"    CTA strategy: {n['cta_style']}")


@themes.command("setup")
def themes_setup() -> None:
    """Step-by-step guide to launch a theme page from scratch."""
    steps = theme_mod.get_setup_guide()
    _section("Theme Page Setup Guide (7 Steps to Launch)")
    if _json_output:
        click.echo(json.dumps(steps, indent=2))
    else:
        for s in steps:
            click.secho(f"\n  Step {s['step']}: {s['title']}", fg="yellow", bold=True)
            click.echo(f"    {s['action']}")
            click.secho(f"    Tool: {s['tool']}", fg="green")


@themes.command("funnel")
@click.option("--niche", "-n", default="", help="Your specific niche for tailored tips")
def themes_funnel(niche: str) -> None:
    """Show the full viewer → buyer conversion funnel for theme pages."""
    funnel = theme_mod.get_conversion_funnel(niche)
    _section(f"Conversion Funnel{' — ' + niche if niche else ''}")
    if _json_output:
        click.echo(json.dumps(funnel, indent=2))
    else:
        output(funnel)


@themes.command("calendar")
@click.option("--niche", "-n", default="", help="Your niche")
def themes_calendar(niche: str) -> None:
    """Generate a weekly content calendar template."""
    cal = theme_mod.get_content_calendar(niche)
    _section(f"Weekly Content Calendar{' — ' + niche if niche else ''}")
    if _json_output:
        click.echo(json.dumps(cal, indent=2))
    else:
        output(cal)


# ── optimize (top-level shortcut) ─────────────────────────────────────────────

@cli.command()
@click.option("--platform", "-p", default="all",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--niche", "-n", default="general")
@click.option("--followers", "-f", default=0, type=int)
def optimize(platform: str, niche: str, followers: int) -> None:
    """One-shot full optimization report: trends + hashtags + account tips.

    Examples:
        social-media optimize --platform tiktok --niche fitness --followers 500
        social-media optimize --niche finance
    """
    _section(f"Full Optimization Report — {platform.title()} — {niche.title()}")

    # Trends
    if platform in ("tiktok", "all"):
        tt = tt_scraper.fetch_trends()
        click.secho("\nTop TikTok Sound to use NOW:", fg="cyan", bold=True)
        if tt.trending_sounds:
            s = tt.trending_sounds[0]
            click.echo(f"  '{s['title']}' by {s['artist']} — {s['video_count']:,} videos — {s['use_case']}")

    # Hashtags
    for plat in (["tiktok", "youtube", "instagram"] if platform == "all" else [platform]):
        click.secho(f"\nOptimized Hashtags for {plat.title()}:", fg="cyan", bold=True)
        ht = ht_mod.generate_hashtag_set(niche, plat)
        click.secho(f"  {ht['formatted']}", fg="green")

    # Account tips
    platforms = ["tiktok", "youtube", "instagram"] if platform == "all" else [platform]
    for plat in platforms:
        click.secho(f"\n{plat.title()} Quick Wins:", fg="cyan", bold=True)
        profile = acct_mod.AccountProfile(platform=plat, niche=niche, follower_count=followers)
        checklist = acct_mod.get_optimization_checklist(plat, profile)
        if "audit" in checklist:
            for win in checklist["audit"].get("quick_wins", []):
                click.echo(f"  ✓ {win}")
            click.echo(f"  Tier: {checklist['audit']['follower_tier']}")
            click.echo(f"  Next move: {checklist['audit']['recommendation']}")

    # Theme page prompt
    click.secho("\nTheme Page Opportunity:", fg="cyan", bold=True)
    niches = theme_mod.get_niche_recommendations([niche])
    if niches:
        n = niches[0]
        click.echo(f"  Best niche for you: {n['niche']}")
        click.echo(f"  Monetize with: {n['monetization'][0]}")
        click.echo(f"  Start with: {n['cta_style']}")


# ── REPL ──────────────────────────────────────────────────────────────────────

REPL_HELP = """
Social Media CLI — Interactive Mode
Commands:
  trends tiktok [--live] [--section sounds|hashtags|formats|moments|all]
  trends youtube [--live] [--section niches|hashtags|strategy|formats|all]
  trends all [--live]
  hashtags <niche> [--platform tiktok|youtube|instagram] [--count N]
  music [--platform tiktok|youtube|both] [--category <cat>]
  accounts optimize <platform|all> [--niche X] [--followers N]
  accounts audit <platform> --handle @you [--followers N] [--niche X]
  themes niches [-k keyword] [-m monetization]
  themes setup
  themes funnel [--niche X]
  themes calendar [--niche X]
  optimize [--platform X] [--niche X] [--followers N]
  help | quit
"""


def _launch_repl() -> None:
    global _repl_mode
    _repl_mode = True
    click.secho("Social Media CLI  (type 'help' for commands, 'quit' to exit)", fg="cyan", bold=True)
    while True:
        try:
            raw = click.prompt("social-media", prompt_suffix="> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw.lower() in ("quit", "exit", "q"):
            break
        if raw.lower() in ("help", "?"):
            click.echo(REPL_HELP)
            continue
        try:
            args = shlex.split(raw)
            ctx = cli.make_context("social-media", args, standalone_mode=False)
            cli.invoke(ctx)
        except SystemExit:
            pass
        except Exception as exc:
            _err(str(exc))


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    cli(standalone_mode=True)


if __name__ == "__main__":
    main()
