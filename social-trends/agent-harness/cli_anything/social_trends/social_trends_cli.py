#!/usr/bin/env python3
"""Social Trends CLI — Viral trend research, account optimization, and theme page strategy.

Commands:
  # Setup
  cli-anything-social config setup-youtube --key <API_KEY>
  cli-anything-social config setup-tiktok --session <MS_TOKEN>

  # Trend research
  cli-anything-social trends youtube --region US --category music --max 20
  cli-anything-social trends tiktok --niche motivation
  cli-anything-social trends music --top 15

  # Hashtag tools
  cli-anything-social hashtags niche --niche fitness
  cli-anything-social hashtags mix --niche fashion
  cli-anything-social hashtags youtube --region US --max 20

  # Account management
  cli-anything-social account add --platform instagram --handle @mypage --niche motivation
  cli-anything-social account optimize --platform tiktok --handle @mypage --niche fitness
  cli-anything-social account schedule --platform tiktok --niche fitness
  cli-anything-social account bio-score --platform instagram --bio "Your bio text here"
  cli-anything-social account list

  # Theme pages
  cli-anything-social theme blueprint --niche luxury_lifestyle
  cli-anything-social theme monetize --method affiliate_marketing
  cli-anything-social theme funnel
  cli-anything-social theme scale
  cli-anything-social theme niches

  # Interactive REPL
  cli-anything-social repl
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_trends.utils import config as cfg_mod
from cli_anything.social_trends.utils.formatters import (
    fmt_number, print_json, print_table, print_section, print_bullet, print_score_bar,
)
from cli_anything.social_trends.core import tiktok_trends as tt
from cli_anything.social_trends.core import account_optimizer as ao
from cli_anything.social_trends.core import theme_pages as tp

_json_output = False


def output(data, message: str = ""):
    if _json_output:
        print_json(data)
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
            click.echo(f"{prefix}- {item}")


def _handle_error(e: Exception):
    click.echo(f"Error: {e}", err=True)
    sys.exit(1)


@click.group()
@click.option("--json", "json_flag", is_flag=True, help="Output raw JSON")
def main(json_flag: bool):
    """Social Trends CLI — YouTube/TikTok trends, hashtags, account optimization, theme pages."""
    global _json_output
    _json_output = json_flag


# ---------------------------------------------------------------------------
# CONFIG group
# ---------------------------------------------------------------------------
@main.group()
def config():
    """Configure API keys and preferences."""


@config.command("setup-youtube")
@click.option("--key", required=True, help="YouTube Data API v3 key")
def config_setup_youtube(key: str):
    """Save YouTube Data API key.

    Get a free key at: https://console.developers.google.com/
    Enable the 'YouTube Data API v3' service.
    """
    cfg_mod.set_value("youtube_api_key", key)
    click.echo("YouTube API key saved.")
    click.echo("Test it: cli-anything-social trends youtube --region US")


@config.command("setup-tiktok")
@click.option("--session", required=True, help="TikTok msToken session cookie")
def config_setup_tiktok(session: str):
    """Save TikTok session token (msToken from browser cookies).

    To get msToken:
      1. Open tiktok.com in Chrome
      2. Press F12 → Application tab → Cookies → tiktok.com
      3. Copy the value of 'msToken'
    """
    cfg_mod.set_value("tiktok_session_id", session)
    click.echo("TikTok session token saved.")


@config.command("show")
def config_show():
    """Show current configuration (keys are masked)."""
    data = cfg_mod.load_config()
    masked = {}
    for k, v in data.items():
        if "key" in k.lower() or "secret" in k.lower() or "session" in k.lower() or "token" in k.lower():
            masked[k] = v[:8] + "..." if v and len(v) > 8 else "***"
        else:
            masked[k] = v
    output(masked, "Configuration:")


# ---------------------------------------------------------------------------
# TRENDS group
# ---------------------------------------------------------------------------
@main.group()
def trends():
    """Fetch viral trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO region code (US, GB, IN, etc.)")
@click.option("--category", default="all", show_default=True,
              help="Category: all, music, gaming, entertainment, sports, education, film, comedy")
@click.option("--max", "max_results", default=20, show_default=True, help="Max results (1-50)")
@click.option("--shorts", is_flag=True, help="Filter to YouTube Shorts only (≤60s)")
def trends_youtube(region: str, category: str, max_results: int, shorts: bool):
    """Fetch YouTube trending videos for a region and category.

    Requires YouTube API key (see: cli-anything-social config setup-youtube).
    """
    try:
        from cli_anything.social_trends.core import youtube_trends as yt
    except ImportError:
        click.echo("Missing dependency: pip install google-api-python-client isodate", err=True)
        sys.exit(1)

    try:
        videos = yt.fetch_trending_videos(
            region=region.upper(),
            category=category,
            max_results=max_results,
            shorts_only=shorts,
        )
    except Exception as e:
        _handle_error(e)

    if _json_output:
        print_json(videos)
        return

    print_section(f"YouTube Trending — {region.upper()} / {category.title()}")
    if not videos:
        click.echo("  No videos found.")
        return

    rows = [
        {
            "#": i + 1,
            "Title": v["title"][:45],
            "Channel": v["channel"][:20],
            "Views": fmt_number(v["views"]),
            "Likes": fmt_number(v["likes"]),
            "Dur": v["duration"],
            "Short": "✓" if v["is_short"] else "",
        }
        for i, v in enumerate(videos)
    ]
    print_table(rows, ["#", "Title", "Channel", "Views", "Likes", "Dur", "Short"])
    click.echo()

    click.echo("Top Hashtags from these videos:")
    hashtags = yt.extract_trending_hashtags(videos, top_n=15)
    for h in hashtags[:10]:
        click.echo(f"  {h['hashtag']:<25} {fmt_number(h['total_views'])} total views  ({h['count']} videos)")


@trends.command("tiktok")
@click.option("--niche", default="motivation", show_default=True,
              help="Content niche (run 'trends niches' to list all)")
@click.option("--sounds", is_flag=True, help="Also show trending sounds")
def trends_tiktok(niche: str, sounds: bool):
    """Get TikTok viral trend report for a niche: hashtags, content ideas, best times."""
    try:
        report = tt.get_tiktok_trend_report(niche)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    if _json_output:
        print_json(report)
        return

    print_section(f"TikTok Trend Report — #{niche}")

    click.echo("\nTop Hashtags:")
    rows = [
        {
            "Rank": h["virality_rank"],
            "Hashtag": h["hashtag"],
            "Est. Posts": h["estimated_posts_fmt"],
            "Recommended": "★" if h["recommended"] else "",
        }
        for h in report["trending_hashtags"][:12]
    ]
    print_table(rows, ["Rank", "Hashtag", "Est. Posts", "Recommended"])

    click.echo("\nOptimal Hashtag Mix (copy this):")
    mix = report["optimal_hashtag_mix"]
    click.echo("  " + " ".join(mix["hashtags"]))
    click.echo(f"  Strategy: {mix['strategy']}")
    click.echo(f"  Tip: {mix['caption_tip']}")

    click.echo("\nContent Ideas:")
    for idea in report["content_ideas"]:
        click.echo(f"  [{idea['format']} | {idea['duration']}]")
        click.echo(f"    Hook: \"{idea['hook']}\"")

    click.echo("\nBest Posting Times:")
    for t in report["best_posting_times"]:
        click.echo(f"  {t['day']:<12} {t['time']:<15} {t['engagement_multiplier']} engagement  — {t['note']}")

    if sounds:
        click.echo()
        print_section("Trending Sounds")
        for i, s in enumerate(report["trending_sounds"]):
            click.echo(f"  {i+1}. \"{s['title']}\" by {s['artist']}  [{s['category']}]  viral={s['viral_score']}")

    click.echo("\nAlgorithm Tips:")
    print_bullet(report["algorithm_tips"][:5])


@trends.command("music")
@click.option("--category", default="all", show_default=True,
              help="Music category: all, pop, indie, kpop, rnb, afrobeats, classic")
@click.option("--top", default=20, show_default=True, help="Number of sounds to show")
def trends_music(category: str, top: int):
    """Show trending TikTok sounds and music to use in your content."""
    sounds = tt.fetch_trending_sounds(category=category, top_n=top)

    if _json_output:
        print_json(sounds)
        return

    print_section(f"Trending Sounds — {category.title()}")
    rows = [
        {
            "#": i + 1,
            "Title": s["title"][:35],
            "Artist": s["artist"][:25],
            "Category": s["category"],
            "Viral Score": s["viral_score"],
        }
        for i, s in enumerate(sounds)
    ]
    print_table(rows, ["#", "Title", "Artist", "Category", "Viral Score"])
    click.echo("\nTip: Search any of these in TikTok's sound library and use within 24h of trending.")


@trends.command("niches")
def trends_niches():
    """List all available content niches for TikTok trend research."""
    niches = tt.list_available_niches()
    print_section("Available Content Niches")
    print_bullet(niches)


# ---------------------------------------------------------------------------
# HASHTAGS group
# ---------------------------------------------------------------------------
@main.group()
def hashtags():
    """Hashtag research and optimization tools."""


@hashtags.command("niche")
@click.option("--niche", required=True, help="Content niche (fitness, motivation, finance, etc.)")
@click.option("--top", default=20, show_default=True, help="Number of hashtags to return")
def hashtags_niche(niche: str, top: int):
    """Get trending hashtags for a specific content niche."""
    try:
        tags = tt.fetch_trending_hashtags_by_niche(niche, top_n=top)
    except ValueError as e:
        _handle_error(e)

    if _json_output:
        print_json(tags)
        return

    print_section(f"Trending Hashtags — #{niche}")
    rows = [
        {
            "Rank": t["virality_rank"],
            "Hashtag": t["hashtag"],
            "Est. Posts": t["estimated_posts_fmt"],
            "★ Top Pick": "★" if t["recommended"] else "",
        }
        for t in tags
    ]
    print_table(rows, ["Rank", "Hashtag", "Est. Posts", "★ Top Pick"])
    click.echo("\n★ = Recommended primary hashtags (highest reach-to-competition ratio)")


@hashtags.command("mix")
@click.option("--niche", required=True, help="Content niche for hashtag mix")
@click.option("--no-broad", is_flag=True, help="Skip broad #fyp/#viral tags")
def hashtags_mix(niche: str, no_broad: bool):
    """Generate an optimized hashtag mix (5-7 tags) ready to paste into your post."""
    try:
        mix = tt.get_optimal_hashtag_mix(niche, include_broad=not no_broad)
    except Exception as e:
        _handle_error(e)

    if _json_output:
        print_json(mix)
        return

    print_section(f"Optimal Hashtag Mix — #{niche}")
    click.echo("\nCopy-paste this into your caption:")
    click.echo(f"\n  {' '.join(mix['hashtags'])}\n")
    click.echo(f"Strategy: {mix['strategy']}")
    click.echo()
    click.echo("Primary niche tags:")
    print_bullet(mix["primary_niche_tags"])
    click.echo("\nBroad reach tags:")
    print_bullet(mix["broad_reach_tags"])
    click.echo(f"\nCaption tip: {mix['caption_tip']}")


@hashtags.command("youtube")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", default=20, show_default=True)
def hashtags_youtube(region: str, max_results: int):
    """Extract top hashtags from YouTube trending videos (requires API key)."""
    try:
        from cli_anything.social_trends.core import youtube_trends as yt
        videos = yt.fetch_trending_videos(region=region.upper(), max_results=min(max_results * 2, 50))
        tags = yt.extract_trending_hashtags(videos, top_n=max_results)
    except Exception as e:
        _handle_error(e)

    if _json_output:
        print_json(tags)
        return

    print_section(f"YouTube Trending Hashtags — {region.upper()}")
    rows = [
        {
            "Hashtag": t["hashtag"],
            "Videos": t["count"],
            "Total Views": fmt_number(t["total_views"]),
        }
        for t in tags
    ]
    print_table(rows, ["Hashtag", "Videos", "Total Views"])


# ---------------------------------------------------------------------------
# ACCOUNT group
# ---------------------------------------------------------------------------
@main.group()
def account():
    """Manage and optimize your social media accounts."""


@account.command("add")
@click.option("--platform", required=True, type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--handle", required=True, help="Account handle (e.g. @mypage)")
@click.option("--niche", required=True, help="Content niche")
@click.option("--goal", default="growth", type=click.Choice(["growth", "monetize", "brand"]))
def account_add(platform: str, handle: str, niche: str, goal: str):
    """Add a social media account to track and optimize."""
    acc = cfg_mod.add_account(platform, handle.lstrip("@"), niche, goal)
    click.echo(f"Account added: @{acc['handle']} on {platform} (niche: {niche}, goal: {goal})")


@account.command("remove")
@click.option("--platform", required=True, type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--handle", required=True)
def account_remove(platform: str, handle: str):
    """Remove a tracked account."""
    removed = cfg_mod.remove_account(platform, handle.lstrip("@"))
    if removed:
        click.echo(f"Removed @{handle} from {platform}.")
    else:
        click.echo(f"Account @{handle} on {platform} not found.")


@account.command("list")
def account_list():
    """List all tracked accounts with their growth stage."""
    summaries = ao.get_all_accounts_summary()

    if _json_output:
        print_json(summaries)
        return

    if not summaries:
        click.echo("No accounts tracked yet.")
        click.echo("Add one: cli-anything-social account add --platform tiktok --handle @mypage --niche motivation")
        return

    print_section("Tracked Accounts")
    rows = [
        {
            "Platform": a["platform"],
            "Handle": f"@{a['handle']}",
            "Niche": a["niche"],
            "Goal": a["goal"],
            "Stage": a["growth_stage"],
            "Priority": a["priority"][:40],
        }
        for a in summaries
    ]
    print_table(rows, ["Platform", "Handle", "Niche", "Goal", "Stage"])
    for a in summaries:
        click.echo(f"  @{a['handle']}: {a['priority']}")


@account.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--handle", required=True, help="Account handle")
@click.option("--niche", required=True, help="Content niche")
@click.option("--bio", default=None, help="Current bio text (for scoring)")
@click.option("--followers", default=0, help="Current follower count")
@click.option("--goal", default="growth", type=click.Choice(["growth", "monetize", "brand"]))
def account_optimize(platform: str, handle: str, niche: str,
                     bio: Optional[str], followers: int, goal: str):
    """Run a full account optimization audit with 30-day action plan."""
    try:
        result = ao.optimize_account(platform, handle, niche, bio, followers, goal)
    except Exception as e:
        _handle_error(e)

    if _json_output:
        print_json(result)
        return

    acc = result["account"]
    print_section(f"Account Audit: {acc['handle']} on {acc['platform'].title()}")
    click.echo(f"  Niche: {acc['niche']}  |  Goal: {acc['goal']}  |  Followers: {fmt_number(acc['followers'])}")
    click.echo(f"  Growth Stage: {acc['growth_stage']['stage']}")
    click.echo(f"  Current Priority: {acc['growth_stage']['priority']}")

    if result.get("bio_analysis"):
        bio_a = result["bio_analysis"]
        click.echo()
        print_section("Bio Score", "-")
        print_score_bar("Bio Quality", bio_a["score"])
        click.echo(f"  Grade: {bio_a['grade']}  ({bio_a['bio_length']}/{bio_a['max_chars']} chars)")
        click.echo("\n  Feedback:")
        print_bullet(bio_a["feedback"])
        if bio_a["improvements"]:
            click.echo("\n  Improvements Needed:")
            print_bullet(bio_a["improvements"])

    spec = result["platform_specs"]
    click.echo()
    print_section("Platform Best Practices", "-")
    click.echo(f"  Key Metric:    {spec['key_metric']}")
    click.echo(f"  Best Times:    {', '.join(spec['best_times'])}")
    click.echo(f"  Best Days:     {', '.join(spec['best_days'])}")
    click.echo(f"  Content Split: {spec['content_split']}")

    click.echo()
    print_section("30-Day Action Plan", "-")
    for week in result["30_day_action_plan"]:
        click.echo(f"\n  Week {week['week']}: {week['focus']}")
        print_bullet(week["tasks"])


@account.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--niche", required=True)
@click.option("--goal", default="growth")
def account_schedule(platform: str, niche: str, goal: str):
    """Generate an optimized weekly posting schedule."""
    try:
        sched = ao.get_posting_schedule(platform, niche, goal)
    except Exception as e:
        _handle_error(e)

    if _json_output:
        print_json(sched)
        return

    print_section(f"Weekly Posting Schedule — {platform.title()} / #{niche}")
    click.echo(f"  Content split: {sched['content_split']}")
    click.echo(f"  Key metric: {sched['key_metric']}")
    click.echo()

    for day_data in sched["weekly_schedule"]:
        day = day_data["day"]
        posts = day_data.get("posts", [])
        if not posts:
            click.echo(f"  {day:<12} — Rest day")
            continue
        for post in posts:
            click.echo(f"  {day:<12} {post['time']:<12} [{post['content_type']}]")
            click.echo(f"             Pillar: {post['pillar']}")
            click.echo(f"             Format: {post['format_idea']}")


@account.command("bio-score")
@click.option("--platform", required=True, type=click.Choice(["instagram", "tiktok", "youtube"]))
@click.option("--bio", required=True, help="Bio text to analyze")
def account_bio_score(platform: str, bio: str):
    """Score and improve your social media bio."""
    result = ao.score_bio(bio, platform)

    if _json_output:
        print_json(result)
        return

    print_section(f"Bio Score — {platform.title()}")
    print_score_bar("Overall Score", result["score"])
    click.echo(f"  Grade: {result['grade']}  ({result['bio_length']}/{result['max_chars']} chars)")
    click.echo("\n  Feedback:")
    print_bullet(result["feedback"])
    if result["improvements"]:
        click.echo("\n  What to fix:")
        print_bullet(result["improvements"])


# ---------------------------------------------------------------------------
# THEME group
# ---------------------------------------------------------------------------
@main.group()
def theme():
    """Theme page creation, monetization strategies, and scaling systems."""


@theme.command("blueprint")
@click.option("--niche", required=True, help="Theme page niche (run 'theme niches' to list)")
def theme_blueprint(niche: str):
    """Get a complete theme page creation blueprint: setup, content, monetization, 90-day plan."""
    try:
        blueprint = tp.get_theme_page_blueprint(niche)
    except ValueError as e:
        _handle_error(e)

    if _json_output:
        print_json(blueprint)
        return

    overview = blueprint["niche_overview"]
    print_section(f"Theme Page Blueprint — {niche.replace('_', ' ').title()}")
    click.echo(f"  {overview['description']}")
    click.echo(f"  Target audience: {overview['target_audience']}")
    click.echo(f"  Monetization potential: {overview['monetization_potential']}")
    click.echo(f"  Competition: {overview['competition']}")
    click.echo(f"  Avg monthly revenue: {overview['avg_monthly_revenue_range']}")
    click.echo(f"  Time to first revenue: ~{overview['time_to_monetize_days']} days")
    click.echo(f"  Top affiliate programs: {', '.join(overview['affiliate_programs'][:3])}")

    click.echo()
    print_section("Setup Checklist", "-")
    for item in blueprint["setup_checklist"]:
        click.echo(f"  Step {item['step']}: {item['task']} ({item['time']})")
        click.echo(f"    {item['detail']}")

    click.echo()
    print_section("90-Day Plan", "-")
    for phase in blueprint["90_day_plan"]:
        click.echo(f"\n  Days {phase['days']}: {phase['focus']}")
        click.echo(f"  KPI: {phase['kpi']}")
        print_bullet(phase["goals"])

    click.echo()
    print_section("Monetization Roadmap", "-")
    for milestone in blueprint["monetization_roadmap"]:
        revenue = milestone["expected_revenue"]
        progs = (", ".join(milestone["programs"])) if milestone["programs"] else ""
        click.echo(f"  {milestone['milestone']:<15} {milestone['action']}")
        click.echo(f"                Expected: {revenue}" + (f"  |  Programs: {progs}" if progs else ""))


@theme.command("monetize")
@click.option("--method", required=True,
              type=click.Choice(["affiliate_marketing", "paid_promotions", "digital_products",
                                  "subscriptions_memberships", "account_flipping"]),
              help="Monetization method to explore")
def theme_monetize(method: str):
    """Deep-dive into a specific monetization method with step-by-step guide."""
    result = tp.get_monetization_strategy(method)

    if _json_output:
        print_json(result)
        return

    print_section(f"Monetization: {method.replace('_', ' ').title()}")
    click.echo(f"  {result['description']}")
    click.echo()
    click.echo(f"  Difficulty:             {result['difficulty']}")
    click.echo(f"  Startup cost:           {result['startup_cost']}")
    click.echo(f"  Time to first dollar:   {result['time_to_first_dollar']}")
    click.echo(f"  Follower requirement:   {result['follower_requirement']}")
    click.echo(f"  Income ceiling:         {result['income_ceiling']}")

    click.echo()
    click.echo("  Step-by-Step:")
    for i, step in enumerate(result["steps"], 1):
        click.echo(f"    {i}. {step}")

    if result.get("pro_tips"):
        click.echo()
        click.echo("  Pro Tips:")
        print_bullet(result["pro_tips"], prefix="    ★")

    for key in ["best_programs", "rate_calculator", "product_ideas", "platform_comparison", "valuation_guide"]:
        if result.get(key):
            click.echo(f"\n  {key.replace('_', ' ').title()}:")
            val = result[key]
            if isinstance(val, dict):
                for k, v in val.items():
                    if isinstance(v, list):
                        click.echo(f"    {k}: {', '.join(v)}")
                    else:
                        click.echo(f"    {k}: {v}")
            elif isinstance(val, list):
                print_bullet(val, prefix="    •")


@theme.command("funnel")
def theme_funnel():
    """Show the 5-stage follower-to-buyer conversion funnel."""
    funnel = tp.get_conversion_funnel()

    if _json_output:
        print_json(funnel)
        return

    print_section("5-Stage Conversion Funnel: Follower → Buyer")
    for stage in funnel["stages"]:
        click.echo(f"\n  Stage {stage['stage']}: {stage['name']}")
        click.echo(f"  Goal: {stage['goal']}")
        click.echo(f"  Metric: {stage['metric']}")
        click.echo("  Tactics:")
        print_bullet(stage["tactics"])


@theme.command("scale")
def theme_scale():
    """Show the multi-page theme account scaling blueprint (the real business model)."""
    plan = tp.get_multi_page_scaling_plan()

    if _json_output:
        print_json(plan)
        return

    print_section("Multi-Page Scaling System")
    click.echo(f"\n  {plan['concept']}\n")

    for phase in plan["phases"]:
        click.echo(f"\n  Phase {phase['phase']}: {phase['name']}")
        click.echo(f"  Goal: {phase['goal']}")
        print_bullet(phase["actions"])

    click.echo()
    print_section("Essential Tools", "-")
    for category, tools in plan["tools"].items():
        click.echo(f"  {category}:")
        print_bullet(tools)


@theme.command("monetize-list")
def theme_monetize_list():
    """List all monetization methods with quick comparison."""
    methods = tp.get_all_monetization_methods()

    if _json_output:
        print_json(methods)
        return

    print_section("Monetization Methods Comparison")
    rows = [
        {
            "Method": m["method"].replace("_", " ").title()[:25],
            "Difficulty": m["difficulty"],
            "Cost": m["startup_cost"],
            "First $": m["time_to_first_dollar"],
            "Req. Followers": m["follower_requirement"],
        }
        for m in methods
    ]
    print_table(rows, ["Method", "Difficulty", "Cost", "First $", "Req. Followers"])


@theme.command("niches")
def theme_niches():
    """List all available theme page niches with overview."""
    if _json_output:
        print_json(tp.list_available_niches())
        return
    print_section("Available Theme Page Niches")
    print_bullet(tp.list_available_niches())
    click.echo("\nGet full blueprint: cli-anything-social theme blueprint --niche <niche>")


# ---------------------------------------------------------------------------
# REPL mode
# ---------------------------------------------------------------------------
@main.command()
def repl():
    """Interactive REPL mode — run commands in a persistent session."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.completion import WordCompleter
        from prompt_toolkit.history import InMemoryHistory
    except ImportError:
        click.echo("Missing dependency: pip install prompt-toolkit", err=True)
        sys.exit(1)

    commands = [
        "trends youtube", "trends tiktok", "trends music", "trends niches",
        "hashtags niche", "hashtags mix", "hashtags youtube",
        "account add", "account list", "account optimize", "account schedule", "account bio-score",
        "theme blueprint", "theme monetize", "theme funnel", "theme scale", "theme niches",
        "config setup-youtube", "config setup-tiktok", "config show",
        "help", "exit", "quit",
    ]
    completer = WordCompleter(commands, ignore_case=True)
    session = PromptSession(history=InMemoryHistory(), completer=completer)

    click.echo("Social Trends CLI — Interactive Mode")
    click.echo("Commands: trends, hashtags, account, theme, config, help, exit")
    click.echo("Type 'help' for command list or any command to run.\n")

    while True:
        try:
            line = session.prompt("social> ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if line.lower() in ("help", "?"):
            click.echo("\nAvailable commands:")
            for cmd in commands[:-2]:
                click.echo(f"  {cmd}")
            click.echo()
            continue

        args = line.split()
        try:
            main.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
