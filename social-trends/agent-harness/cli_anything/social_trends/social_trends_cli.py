#!/usr/bin/env python3
"""Social Trends CLI — Agent-native social media trend intelligence.

Fetches viral trends from YouTube and TikTok, optimizes accounts,
and provides a complete theme page creation & monetization guide.

Usage (one-shot):
    social-trends trends fetch --platform youtube
    social-trends trends fetch --platform tiktok --niche fitness
    social-trends trends fetch --platform all --niche beauty --json
    social-trends account optimize --platform tiktok --niche fashion --followers 5000
    social-trends theme-page guide --niche luxury --monetization account_flipping
    social-trends theme-page niches

Interactive REPL:
    social-trends repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.core.youtube_trends import fetch_youtube_trends
from cli_anything.social_trends.core.tiktok_trends import fetch_tiktok_trends
from cli_anything.social_trends.core.account_optimizer import optimize_account
from cli_anything.social_trends.core.theme_page_guide import (
    get_theme_page_guide,
    PROFITABLE_NICHES,
    CONVERSION_STRATEGIES,
)

_json_output = False


# ─── Output helpers ──────────────────────────────────────────────────────────

def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
        _pretty(data)


def _pretty(obj, indent: int = 0):
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}\033[1m{k}:\033[0m")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}\033[1m{k}:\033[0m {v}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                _pretty(item, indent)
                click.echo()
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{obj}")


# ─── Root CLI group ───────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "use_json", is_flag=True, default=False, help="Output as JSON (agent-friendly)")
def cli(use_json: bool):
    """Social Trends CLI — YouTube & TikTok viral trend intelligence for agents."""
    global _json_output
    _json_output = use_json


# ─── trends group ─────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch viral trends, hashtags, and music from YouTube and TikTok."""


@trends.command("fetch")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              default="all", show_default=True,
              help="Platform to scrape trends from.")
@click.option("--niche", "-n", default="general", show_default=True,
              help="Content niche (fitness/fashion/food/beauty/finance/gaming/travel/pets/education/general).")
@click.option("--category", "-c",
              type=click.Choice(["all", "music", "gaming", "movies"], case_sensitive=False),
              default="all", show_default=True,
              help="YouTube category (ignored for TikTok).")
@click.option("--max-items", "-m", default=25, show_default=True,
              help="Max items to fetch per platform.")
def trends_fetch(platform: str, niche: str, category: str, max_items: int):
    """Fetch viral trends from YouTube, TikTok, or both."""
    results: dict = {}

    if platform in ("youtube", "all"):
        click.echo("Fetching YouTube trends...", err=True)
        yt = fetch_youtube_trends(category=category, max_items=max_items)
        results["youtube"] = yt

    if platform in ("tiktok", "all"):
        click.echo("Fetching TikTok trends...", err=True)
        tt = fetch_tiktok_trends(niche=niche, max_items=max_items)
        results["tiktok"] = tt

    # Merge cross-platform insights when fetching all
    if platform == "all" and "youtube" in results and "tiktok" in results:
        yt_tags = set(t.lstrip("#").lower() for t in results["youtube"].get("top_hashtags", []))
        tt_tags = set(h["hashtag"].lstrip("#").lower() for h in results["tiktok"].get("hashtags", []))
        overlap = yt_tags & tt_tags
        results["cross_platform_overlap"] = {
            "tags_trending_on_both": [f"#{t}" for t in sorted(overlap)],
            "pro_tip": (
                "Tags trending on BOTH platforms are your highest-leverage content opportunities. "
                "Create one video and post it on all platforms with platform-native edits."
            ),
        }

    output(results, f"Trends ({platform.upper()}, niche={niche})")


@trends.command("hashtags")
@click.option("--niche", "-n", default="general", show_default=True)
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "all"], case_sensitive=False),
              default="tiktok", show_default=True)
def trends_hashtags(niche: str, platform: str):
    """Get optimized hashtag sets for a specific niche."""
    tt = fetch_tiktok_trends(niche=niche)
    yt = fetch_youtube_trends() if platform in ("youtube", "all") else {}

    result = {
        "niche": niche,
        "tiktok_niche_hashtags": tt.get("niche_hashtags", []),
        "tiktok_live_trending": [h["hashtag"] for h in tt.get("hashtags", [])[:15]],
        "youtube_top_hashtags": yt.get("top_hashtags", []) if yt else [],
        "usage_tip": (
            "Use 3–5 niche hashtags + 1 mega-viral tag per post. "
            "Rotate sets — don't use the same combo twice in a row."
        ),
    }
    output(result, f"Hashtags for niche '{niche}'")


@trends.command("music")
@click.option("--niche", "-n", default="general", show_default=True)
def trends_music(niche: str):
    """Get trending sounds and music for TikTok and YouTube."""
    tt = fetch_tiktok_trends(niche=niche)
    yt = fetch_youtube_trends(category="music")

    result = {
        "tiktok_trending_sounds": tt.get("music", [])[:15],
        "youtube_trending_music_titles": yt.get("trending_music", []),
        "how_to_use_trending_sounds": [
            "Search the sound on TikTok → click 'Videos' → study top-performing videos",
            "Create your video BEFORE the sound hits 500K uses (early = more reach)",
            "Use the sound as background audio while filming native content",
            "Lip-sync or reaction format works instantly with any trending sound",
        ],
    }
    output(result, "Trending Music & Sounds")


# ─── account group ────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization commands."""


@account.command("optimize")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              required=True, help="Social platform.")
@click.option("--niche", "-n", default="general", show_default=True,
              help="Content niche.")
@click.option("--followers", "-f", default=0, show_default=True,
              help="Current follower count.")
@click.option("--avg-views", "-v", default=0, show_default=True,
              help="Average views per post.")
@click.option("--posts-per-week", "-w", default=0, show_default=True,
              help="Current posting frequency (posts per week).")
@click.option("--goals", "-g",
              type=click.Choice(["growth", "monetization", "engagement"], case_sensitive=False),
              default="growth", show_default=True,
              help="Primary account goal.")
def account_optimize(platform: str, niche: str, followers: int, avg_views: int,
                     posts_per_week: int, goals: str):
    """Generate a full account optimization playbook."""
    result = optimize_account(
        platform=platform,
        niche=niche,
        followers=followers,
        avg_views=avg_views,
        posts_per_week=posts_per_week,
        goals=goals,
    )
    output(result, f"Account Optimization — {platform.upper()} | {niche} | Goal: {goals}")


@account.command("audit")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              required=True)
@click.option("--niche", "-n", default="general")
def account_audit(platform: str, niche: str):
    """Quick profile checklist audit."""
    result = optimize_account(platform=platform, niche=niche)
    checklist = {
        "profile_checklist": result["profile_checklist"],
        "content_pillars": result["content_pillars"],
        "hook_formulas": result["hook_formulas"],
    }
    output(checklist, f"Profile Audit — {platform.upper()}")


# ─── theme-page group ─────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page creation and monetization conversion guides."""


@theme_page.command("guide")
@click.option("--niche", "-n", default="general", show_default=True,
              help="Content niche for the theme page.")
@click.option("--monetization", "-m",
              type=click.Choice(
                  ["affiliate", "shoutouts", "digital_products",
                   "account_flipping", "email_list", "ugc_creator"],
                  case_sensitive=False,
              ),
              default="affiliate", show_default=True,
              help="Primary monetization strategy.")
def theme_page_guide(niche: str, monetization: str):
    """Get a complete theme page creation + monetization guide."""
    result = get_theme_page_guide(niche=niche, monetization=monetization)
    output(result, f"Theme Page Guide — {niche} | Strategy: {monetization}")


@theme_page.command("niches")
def theme_page_niches():
    """List all profitable theme page niches ranked by monetization potential."""
    output(
        {"profitable_niches": PROFITABLE_NICHES},
        "Profitable Theme Page Niches (ranked by monetization)",
    )


@theme_page.command("monetize")
@click.argument("strategy",
                type=click.Choice(
                    ["affiliate", "shoutouts", "digital_products",
                     "account_flipping", "email_list", "ugc_creator"],
                    case_sensitive=False,
                ))
def theme_page_monetize(strategy: str):
    """Get detailed breakdown of a specific monetization strategy."""
    info = CONVERSION_STRATEGIES.get(strategy)
    if not info:
        click.echo(f"Unknown strategy: {strategy}", err=True)
        sys.exit(1)
    output(info, f"Monetization Strategy: {strategy}")


@theme_page.command("90-day-plan")
@click.option("--niche", "-n", default="general")
def ninety_day_plan(niche: str):
    """Get a 90-day actionable theme page growth plan."""
    guide = get_theme_page_guide(niche=niche)
    result = {
        "niche": guide["niche"],
        "90_day_action_plan": guide["90_day_action_plan"],
        "growth_hacks": guide["growth_hacks"],
        "tools_stack": guide["tools_stack"],
        "common_mistakes": guide["common_mistakes_to_avoid"],
    }
    output(result, f"90-Day Theme Page Plan — {niche}")


# ─── proactive full-scan command ──────────────────────────────────────────────

@cli.command("full-scan")
@click.option("--niche", "-n", default="general", show_default=True,
              help="Your content niche.")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "all"], case_sensitive=False),
              default="all", show_default=True)
@click.option("--followers", "-f", default=0)
@click.option("--goals", "-g",
              type=click.Choice(["growth", "monetization", "engagement"]),
              default="growth")
def full_scan(niche: str, platform: str, followers: int, goals: str):
    """
    Full proactive scan: trends + account optimization + theme page guide in one shot.

    This is the agent's go-to command for a complete social media intelligence report.
    """
    click.echo("Running full social media intelligence scan...", err=True)

    report = {}

    # Trends
    if platform in ("youtube", "all"):
        click.echo("  Fetching YouTube trends...", err=True)
        report["youtube_trends"] = fetch_youtube_trends(max_items=15)
    if platform in ("tiktok", "all"):
        click.echo("  Fetching TikTok trends...", err=True)
        report["tiktok_trends"] = fetch_tiktok_trends(niche=niche, max_items=15)

    # Account optimization (for each active platform)
    platforms = ["tiktok", "youtube"] if platform == "all" else [platform]
    report["account_optimization"] = {
        p: optimize_account(platform=p, niche=niche, followers=followers, goals=goals)
        for p in platforms
    }

    # Theme page guide
    report["theme_page_guide"] = get_theme_page_guide(niche=niche)

    # Executive summary
    yt_tags = report.get("youtube_trends", {}).get("top_hashtags", [])
    tt_tags = [h["hashtag"] for h in report.get("tiktok_trends", {}).get("hashtags", [])[:10]]
    top_sounds = report.get("tiktok_trends", {}).get("music", [{}])

    report["executive_summary"] = {
        "top_youtube_hashtags": yt_tags[:8],
        "top_tiktok_hashtags": tt_tags[:8],
        "top_tiktok_sound": top_sounds[0].get("title", "N/A") if top_sounds else "N/A",
        "account_stage": report["account_optimization"].get(platforms[0], {}).get("account_stage", ""),
        "immediate_action_items": [
            f"Post using trending sound NOW: {top_sounds[0].get('title', 'check TikTok discover')}",
            f"Use these hashtags today: {', '.join((yt_tags + tt_tags)[:5])}",
            "Reply to every comment in first 30 min to boost algorithmic push",
            "Set up link-in-bio with affiliate offer if not done yet",
        ],
    }

    output(report, "Full Social Media Intelligence Report")


# ─── REPL ─────────────────────────────────────────────────────────────────────

@cli.command()
def repl():
    """Launch interactive REPL for exploring trends and optimization."""
    click.echo("Social Trends REPL — type 'help' for commands, 'exit' to quit\n")
    import shlex
    while True:
        try:
            line = click.prompt("social-trends", prompt_suffix="> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye!")
            break
        if not line or line in ("exit", "quit", "q"):
            break
        if line in ("help", "?"):
            click.echo(
                "\nCommands:\n"
                "  trends fetch --platform [youtube|tiktok|all] --niche [niche]\n"
                "  trends hashtags --niche [niche]\n"
                "  trends music --niche [niche]\n"
                "  account optimize --platform [tiktok|youtube|instagram] --niche [niche]\n"
                "  account audit --platform [platform]\n"
                "  theme-page guide --niche [niche] --monetization [strategy]\n"
                "  theme-page niches\n"
                "  theme-page 90-day-plan --niche [niche]\n"
                "  full-scan --niche [niche] --platform [all|tiktok|youtube]\n"
                "  exit\n"
            )
            continue
        try:
            args = shlex.split(line)
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            click.echo(f"Error: {exc}", err=True)


if __name__ == "__main__":
    cli()
