#!/usr/bin/env python3
"""CLI-Anything Social Media — viral trend discovery, hashtag optimizer, account growth, theme pages.

Usage:
    # Discover trending content
    social-media trends youtube --region US --limit 15
    social-media trends tiktok-hashtags --limit 20
    social-media trends tiktok-sounds --limit 10
    social-media trends google --keywords "fitness,gym,workout"

    # Hashtag tools
    social-media hashtags get --niche fitness --platform tiktok --max 25
    social-media hashtags audit "#fyp #like4like #follow4follow"
    social-media hashtags list-niches

    # Account optimizer
    social-media optimize audit --platform tiktok --followers 12000 --views 45000 --likes 800 --comments 50 --days-per-week 5
    social-media optimize schedule --platform tiktok --tz-offset -5
    social-media optimize bio --platform tiktok --account-type themepage --niche motivation
    social-media optimize specs --platform instagram

    # Content tools
    social-media content hooks --niche finance --type curiosity --count 5
    social-media content calendar --niche fitness --weeks 2
    social-media content templates --niche motivation

    # Theme page playbook
    social-media theme-pages playbook
    social-media theme-pages stage --number 3
    social-media theme-pages tools
    social-media theme-pages monetization

    # Interactive REPL
    social-media repl
"""

import sys
import json
import click
from typing import Optional

from cli_anything.social_media.core import trends as _trends
from cli_anything.social_media.core import hashtags as _hashtags
from cli_anything.social_media.core import optimizer as _optimizer
from cli_anything.social_media.core import content as _content
from cli_anything.social_media.core import theme_pages as _theme


# ──────────────────────────────────────────────
#  Output helper
# ──────────────────────────────────────────────

_json_output = False


def out(data, message: str = ""):
    """Render data as JSON or human-readable."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
        return
    if message:
        click.echo(f"\n{message}")
    _render(data)


def _render(data, indent: int = 0):
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}\033[1m{k}\033[0m:")
                _render(v, indent + 1)
            else:
                click.echo(f"{pad}\033[1m{k}\033[0m: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                click.echo(f"{pad}-")
                _render(item, indent + 1)
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{data}")


# ──────────────────────────────────────────────
#  Root CLI
# ──────────────────────────────────────────────

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON")
@click.version_option("1.0.0", prog_name="social-media")
def cli(json_out: bool):
    """Social Media growth toolkit — trends, hashtags, account optimizer, theme pages."""
    global _json_output
    _json_output = json_out


# ──────────────────────────────────────────────
#  trends
# ──────────────────────────────────────────────

@cli.group()
def trends():
    """Discover viral trends across YouTube, TikTok, and Google."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="2-letter country code")
@click.option("--limit", default=15, show_default=True, type=int)
def trends_youtube(region: str, limit: int):
    """Fetch YouTube trending videos."""
    click.echo(f"Fetching YouTube trending ({region})...")
    items = _trends.youtube_trending(region=region, limit=limit)
    data = _trends.trend_items_to_dict(items)
    out(data, f"YouTube Trending — Top {len(data)} ({region})")


@trends.command("tiktok-hashtags")
@click.option("--limit", default=20, show_default=True, type=int)
def trends_tiktok_hashtags(limit: int):
    """Get trending TikTok hashtags with growth metrics."""
    data = _trends.tiktok_trending_hashtags(limit=limit)
    out(data, f"TikTok Trending Hashtags — Top {len(data)}")
    if not _json_output:
        click.echo(
            "\n\033[33mTip:\033[0m For live data visit: "
            "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en"
        )


@trends.command("tiktok-sounds")
@click.option("--limit", default=15, show_default=True, type=int)
def trends_tiktok_sounds(limit: int):
    """Get trending TikTok music / sounds."""
    data = _trends.tiktok_trending_sounds(limit=limit)
    out(data, f"Trending TikTok Sounds — Top {len(data)}")
    if not _json_output:
        click.echo(
            "\n\033[33mTip:\033[0m For live trending sounds: "
            "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en"
        )


@trends.command("google")
@click.option("--keywords", required=True, help="Comma-separated keywords to compare")
@click.option("--geo", default="US", show_default=True)
@click.option("--timeframe", default="now 7-d", show_default=True,
              help="e.g. 'now 7-d', 'today 3-m', 'today 12-m'")
def trends_google(keywords: str, geo: str, timeframe: str):
    """Compare keyword interest via Google Trends (requires: pip install pytrends)."""
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()]
    click.echo(f"Fetching Google Trends for: {kw_list}")
    data = _trends.google_trends(kw_list, geo=geo, timeframe=timeframe)
    out(data, "Google Trends — Interest Over Time")


# ──────────────────────────────────────────────
#  hashtags
# ──────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag research, generation, and auditing."""


@hashtags.command("get")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok", show_default=True)
@click.option("--max", "max_tags", default=25, show_default=True, type=int)
def hashtags_get(niche: str, platform: str, max_tags: int):
    """Generate an optimized hashtag set for your niche."""
    data = _hashtags.build_caption_hashtags(niche, max_tags=max_tags)
    out(data, f"Hashtag Set — {niche} ({platform})")


@hashtags.command("audit")
@click.argument("tags_string")
def hashtags_audit(tags_string: str):
    """Audit a list of hashtags for banned/risky tags. Pass as space-separated string."""
    tags = [t for t in tags_string.split() if t]
    data = _hashtags.hashtag_audit(tags)
    out(data, "Hashtag Audit Results")


@hashtags.command("list-niches")
def hashtags_list_niches():
    """List all available niche databases."""
    niches = _hashtags.list_niches()
    out(niches, "Available Niches")


# ──────────────────────────────────────────────
#  optimize
# ──────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization — audit, schedule, bio, and platform specs."""


@optimize.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--followers", required=True, type=int)
@click.option("--views", "avg_views", required=True, type=int, help="Average views per post")
@click.option("--likes", "avg_likes", required=True, type=int, help="Average likes per post")
@click.option("--comments", "avg_comments", default=0, type=int, help="Average comments per post")
@click.option("--days-per-week", "posting_days", default=3, type=int, help="Posts per week")
@click.option("--has-cta-bio", is_flag=True, help="Bio has a call-to-action")
@click.option("--has-link-bio", is_flag=True, help="Bio has a link")
def optimize_audit(platform, followers, avg_views, avg_likes, avg_comments, posting_days, has_cta_bio, has_link_bio):
    """Full account audit with score, issues, and priority action list."""
    data = _optimizer.audit_account(
        platform=platform,
        follower_count=followers,
        avg_views=avg_views,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        posting_days_per_week=posting_days,
        has_cta_in_bio=has_cta_bio,
        has_link_in_bio=has_link_bio,
    )
    out(data, f"Account Audit — {platform} ({followers:,} followers)")


@optimize.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--tz-offset", default=0, type=int, help="UTC offset (e.g. -5 for EST, +1 for CET)")
def optimize_schedule(platform: str, tz_offset: int):
    """Get optimal posting schedule for a platform."""
    data = _optimizer.get_posting_schedule(platform, timezone_offset=tz_offset)
    out(data, f"Optimal Posting Schedule — {platform} (UTC{tz_offset:+d})")


@optimize.command("bio")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--account-type", required=True,
              type=click.Choice(["themepage", "personal_brand", "business", "fitness", "finance"]))
@click.option("--niche", default="your niche", help="Your content niche keyword")
@click.option("--audience", default="beginners", help="Your target audience")
@click.option("--outcome", default="reach their goals", help="What you help them achieve")
def optimize_bio(platform, account_type, niche, audience, outcome):
    """Generate an optimized profile bio."""
    data = _optimizer.generate_bio(
        platform=platform,
        account_type=account_type,
        niche=niche,
        audience=audience,
        outcome=outcome,
        credibility="",
        cta="Free guide below",
        what_you_do="Helping",
        offer="",
        result_claim="",
        transformation_stat="",
        result_claim2="",
    )
    out(data, f"Bio Generator — {platform} / {account_type}")


@optimize.command("specs")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
def optimize_specs(platform: str):
    """Show full platform specs — algorithm signals, growth tactics, best times."""
    data = _optimizer.platform_specs(platform)
    out(data, f"Platform Specs — {platform}")


# ──────────────────────────────────────────────
#  content
# ──────────────────────────────────────────────

@cli.group()
def content():
    """Content creation tools — hooks, calendars, viral templates."""


@content.command("hooks")
@click.option("--niche", required=True)
@click.option("--type", "hook_type", default="all",
              type=click.Choice(["all", "curiosity", "fear_of_missing_out", "aspirational", "educational", "social_proof"]))
@click.option("--count", default=5, type=int)
def content_hooks(niche: str, hook_type: str, count: int):
    """Generate viral hook variations for your niche."""
    data = _content.generate_hooks(niche, hook_type=hook_type, count=count)
    out(data, f"Viral Hooks — {niche}")


@content.command("calendar")
@click.option("--niche", required=True)
@click.option("--weeks", default=2, type=int, show_default=True)
@click.option("--start", "start_date", default=None, help="YYYY-MM-DD (default: today)")
def content_calendar(niche: str, weeks: int, start_date: Optional[str]):
    """Generate a content calendar with hooks and posting times."""
    data = _content.generate_content_calendar(niche, weeks=weeks, start_date=start_date)
    out(data, f"Content Calendar — {niche} ({weeks} weeks, {data['total_posts']} posts)")


@content.command("templates")
@click.option("--niche", required=True)
def content_templates(niche: str):
    """Get fill-in-the-blank viral post templates."""
    data = _content.get_viral_templates(niche)
    out(data, f"Viral Templates — {niche}")


# ──────────────────────────────────────────────
#  theme-pages
# ──────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages():
    """Complete theme page creation & monetization playbook."""


@theme_pages.command("playbook")
def theme_playbook():
    """Print the full theme page playbook overview."""
    data = _theme.get_playbook()
    # Summarize for readability
    summary = {
        "what_is_a_theme_page": data["what_is_a_theme_page"],
        "stages_overview": [
            {"stage": s["stage"], "name": s["name"], "duration": s["duration"]}
            for s in data["stages"]
        ],
        "30_day_action_plan": data["30_day_action_plan"],
        "kpis_to_track": data["kpis_to_track"],
    }
    out(summary, "Theme Page Playbook — Overview")
    if not _json_output:
        click.echo("\nRun 'social-media theme-pages stage --number 1' to start Stage 1")


@theme_pages.command("stage")
@click.option("--number", required=True, type=int, help="Stage number (1-6)")
def theme_stage(number: int):
    """Show detailed actions for a specific stage."""
    data = _theme.get_stage(number)
    out(data, f"Theme Page — Stage {number}: {data.get('name', '')}")


@theme_pages.command("monetization")
def theme_monetization():
    """Show monetization methods and revenue benchmarks."""
    stages = _theme.THEME_PAGE_PLAYBOOK["stages"]
    mon_stage = next((s for s in stages if s["stage"] == 5), {})
    out(mon_stage, "Monetization Playbook")


@theme_pages.command("tools")
def theme_tools():
    """Print the complete tools stack for running theme pages."""
    data = _theme.THEME_PAGE_PLAYBOOK["tools_stack"]
    out(data, "Theme Page Tools Stack")


@theme_pages.command("copyright")
def theme_copyright():
    """Copyright rules for theme page content — avoid DMCA strikes."""
    data = _theme.THEME_PAGE_PLAYBOOK["copyright_rules"]
    out(data, "Copyright Rules for Theme Pages")


@theme_pages.command("content-pillars")
@click.option("--niche", default=None, help="Filter by niche")
def theme_content_pillars(niche: Optional[str]):
    """Show content pillars by niche."""
    data = _theme.THEME_PAGE_PLAYBOOK["content_pillars"]
    if niche:
        key = niche.lower()
        if key in data:
            out({key: data[key]}, f"Content Pillars — {niche}")
        else:
            out({"error": f"Niche '{niche}' not found", "available": list(data.keys())})
    else:
        out(data, "Content Pillars by Niche")


# ──────────────────────────────────────────────
#  REPL
# ──────────────────────────────────────────────

@cli.command()
def repl():
    """Interactive REPL — explore all commands interactively."""
    try:
        from prompt_toolkit import PromptSession  # type: ignore
        from prompt_toolkit.history import InMemoryHistory  # type: ignore
        session = PromptSession(history=InMemoryHistory())
        use_prompt_toolkit = True
    except ImportError:
        use_prompt_toolkit = False

    click.echo("Social Media CLI REPL — type 'help' for commands, 'exit' to quit\n")

    while True:
        try:
            if use_prompt_toolkit:
                line = session.prompt("social-media> ")
            else:
                line = input("social-media> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if line == "help":
            click.echo(cli.get_help(click.Context(cli)))
            continue

        args = line.split()
        try:
            cli.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            click.echo(f"Error: {exc}", err=True)


if __name__ == "__main__":
    cli()
