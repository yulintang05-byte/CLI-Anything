#!/usr/bin/env python3
"""Social Media Automation CLI — Agent-native social media intelligence.

Scrapes viral trends from YouTube and TikTok, optimizes accounts,
and provides a complete theme page conversion playbook.

Usage:
    # Trend scraping
    social-media trends youtube --limit 20 --region US
    social-media trends tiktok --limit 30
    social-media trends music --region US
    social-media trends hashtags --platform all --niche fitness

    # Account optimization
    social-media optimize profile --platform tiktok --niche fitness
    social-media optimize hashtags --platform tiktok --niche finance
    social-media optimize strategy --niche luxury --posts-per-week 7
    social-media optimize schedule --platform tiktok

    # Theme page
    social-media theme-page evaluate --niche luxury
    social-media theme-page playbook --niche finance
    social-media theme-page monetize --niche fitness

    # Cache management
    social-media cache info
    social-media cache clear

    # Interactive REPL
    social-media repl
"""

import json
import sys
import click
from typing import Optional

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    """Output result data — JSON or human-readable."""
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n{message}")
        _pretty(data, indent=0)


def _pretty(obj, indent: int = 0):
    pad = "  " * indent
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("from_cache", "_ts"):
                continue
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{_key(k)}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{_key(k)}: {_val(v)}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                label = item.get("title") or item.get("tag") or item.get("method") or f"[{i}]"
                click.echo(f"{pad}{i + 1}. {label}")
                for k, v in item.items():
                    if k in ("title", "tag", "method", "from_cache"):
                        continue
                    if isinstance(v, (dict, list)):
                        click.echo(f"{pad}   {_key(k)}:")
                        _pretty(v, indent + 2)
                    else:
                        click.echo(f"{pad}   {_key(k)}: {_val(v)}")
            else:
                click.echo(f"{pad}- {item}")
    else:
        click.echo(f"{pad}{_val(obj)}")


def _key(k: str) -> str:
    return click.style(k.replace("_", " ").title(), fg="cyan", bold=True)


def _val(v) -> str:
    if isinstance(v, bool):
        return click.style(str(v), fg="green" if v else "red")
    if isinstance(v, (int, float)):
        return click.style(str(v), fg="yellow")
    return str(v)


def _error(msg: str):
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(click.style(f"Error: {msg}", fg="red"), err=True)


# ============================================================================
# Main CLI group
# ============================================================================

@click.group(invoke_without_command=True)
@click.option("--json", "json_mode", is_flag=True, help="Output in JSON format")
@click.pass_context
def cli(ctx, json_mode):
    """Social Media CLI — Viral trends, account optimization, and theme page playbooks.

    Scrapes YouTube + TikTok in real-time. No API keys required.

    Run without a subcommand to enter interactive REPL mode.
    """
    global _json_output
    _json_output = json_mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl_cmd)


# ============================================================================
# Trends commands
# ============================================================================

@cli.group()
def trends():
    """Scrape viral trends: hashtags, music, videos from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--limit", default=20, type=int, show_default=True, help="Number of trending videos")
@click.option("--region", default="US", show_default=True, help="Country code (US, GB, IN, etc.)")
@click.option("--category", default="now",
              type=click.Choice(["now", "music", "gaming", "movies"]),
              show_default=True, help="Trending category")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
def trends_youtube(limit, region, category, no_cache):
    """Scrape YouTube trending videos with hashtags and view data."""
    from .core import youtube_scraper as yt
    try:
        result = yt.get_trending(region=region, limit=limit, category=category,
                                 use_cache=not no_cache)
        output(result, f"YouTube Trending ({category.upper()}) — {region}")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@trends.command("tiktok")
@click.option("--limit", default=30, type=int, show_default=True, help="Number of results")
@click.option("--type", "content_type", default="hashtags",
              type=click.Choice(["hashtags", "sounds", "videos"]),
              show_default=True, help="What to fetch")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
def trends_tiktok(limit, content_type, no_cache):
    """Scrape TikTok trending hashtags, sounds, or videos."""
    from .core import tiktok_scraper as tt
    try:
        if content_type == "hashtags":
            result = tt.get_trending_hashtags(limit=limit, use_cache=not no_cache)
            output(result, "TikTok Trending Hashtags")
        elif content_type == "sounds":
            result = tt.get_trending_sounds(limit=limit, use_cache=not no_cache)
            output(result, "TikTok Trending Sounds")
        else:
            result = tt.get_trending_videos(limit=limit, use_cache=not no_cache)
            output(result, "TikTok Trending Videos")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@trends.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=30, type=int, show_default=True)
@click.option("--no-cache", is_flag=True)
def trends_music(region, limit, no_cache):
    """Aggregate trending music/sounds from YouTube Music + TikTok."""
    from .core import trend_aggregator as agg
    try:
        result = agg.aggregate_music(region=region, limit=limit, use_cache=not no_cache)
        output(result, f"Trending Music — {region}")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@trends.command("hashtags")
@click.option("--platform", default="all",
              type=click.Choice(["all", "youtube", "tiktok"]),
              show_default=True, help="Platform to pull from")
@click.option("--niche", default=None, help="Filter hashtags relevant to a niche")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=50, type=int, show_default=True)
@click.option("--no-cache", is_flag=True)
def trends_hashtags(platform, niche, region, limit, no_cache):
    """Aggregate trending hashtags from YouTube and/or TikTok, ranked by score."""
    from .core import trend_aggregator as agg
    try:
        platforms = ["youtube", "tiktok"] if platform == "all" else [platform]

        if niche:
            result = agg.find_opportunities(niche=niche, region=region, use_cache=not no_cache)
            output(result, f"Trending opportunities for niche: {niche}")
        else:
            result = agg.aggregate_hashtags(platforms=platforms, region=region,
                                            limit=limit, use_cache=not no_cache)
            output(result, f"Trending Hashtags ({platform.upper()}) — {region}")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@trends.command("all")
@click.option("--region", default="US", show_default=True)
@click.option("--no-cache", is_flag=True)
def trends_all(region, no_cache):
    """Run all trend scrapers and output a unified summary."""
    from .core import trend_aggregator as agg
    from .core import tiktok_scraper as tt

    results = {}
    errors = []

    click.echo(click.style("Fetching all trends...", fg="blue", bold=True))

    for name, fn, kwargs in [
        ("youtube_trending", "get_trending", {"region": region, "limit": 10, "use_cache": not no_cache}),
    ]:
        from .core import youtube_scraper as yt
        try:
            results["youtube_videos"] = yt.get_trending(region=region, limit=10,
                                                         use_cache=not no_cache)
        except Exception as e:
            errors.append(f"youtube: {e}")

    try:
        results["tiktok_hashtags"] = tt.get_trending_hashtags(limit=20, use_cache=not no_cache)
    except Exception as e:
        errors.append(f"tiktok_hashtags: {e}")

    try:
        results["tiktok_sounds"] = tt.get_trending_sounds(limit=10, use_cache=not no_cache)
    except Exception as e:
        errors.append(f"tiktok_sounds: {e}")

    try:
        results["cross_platform_hashtags"] = agg.aggregate_hashtags(
            region=region, limit=20, use_cache=not no_cache
        )
    except Exception as e:
        errors.append(f"aggregate: {e}")

    results["errors"] = errors
    output(results, "All Trends Summary")


# ============================================================================
# Optimize commands
# ============================================================================

@cli.group()
def optimize():
    """Optimize accounts: profiles, hashtags, content strategy, posting schedule."""
    pass


@optimize.command("profile")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]),
              help="Platform to optimize for")
@click.option("--niche", required=True, help="Your content niche (fitness, finance, etc.)")
def optimize_profile(platform, niche):
    """Generate a profile optimization checklist with actionable steps."""
    from .core import account_optimizer as opt
    result = opt.optimize_profile(platform=platform, niche=niche)
    output(result, f"Profile Optimization — {platform.title()} / {niche.title()}")


@optimize.command("hashtags")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]),
              show_default=True)
@click.option("--niche", required=True, help="Your content niche")
@click.option("--count", default=30, type=int, show_default=True, help="Number of hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--no-cache", is_flag=True)
def optimize_hashtags(platform, niche, count, region, no_cache):
    """Generate an optimized hashtag set mixing trending + niche-specific tags."""
    from .core import account_optimizer as opt
    try:
        result = opt.generate_hashtag_set(niche=niche, platform=platform, count=count,
                                          region=region, use_cache=not no_cache)
        output(result, f"Optimized Hashtag Set — {platform.title()} / {niche.title()}")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@optimize.command("strategy")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]),
              show_default=True)
@click.option("--posts-per-week", default=7, type=int, show_default=True)
@click.option("--region", default="US", show_default=True)
@click.option("--no-cache", is_flag=True)
def optimize_strategy(niche, platform, posts_per_week, region, no_cache):
    """Generate a full content strategy: pillars, hooks, weekly calendar, KPIs."""
    from .core import account_optimizer as opt
    try:
        result = opt.optimize_content_strategy(
            niche=niche, platform=platform, posts_per_week=posts_per_week,
            region=region, use_cache=not no_cache
        )
        output(result, f"Content Strategy — {platform.title()} / {niche.title()}")
    except Exception as e:
        _error(str(e))
        sys.exit(1)


@optimize.command("schedule")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--timezone", default="EST", show_default=True,
              help="Your timezone (EST, PST, GMT, etc.)")
def optimize_schedule(platform, timezone):
    """Show optimal posting times and day-of-week recommendations."""
    from .core import account_optimizer as opt
    result = opt.best_posting_times(platform=platform, timezone=timezone)
    output(result, f"Best Posting Times — {platform.title()} ({timezone})")


# ============================================================================
# Theme page commands
# ============================================================================

@cli.group("theme-page")
def theme_page():
    """Theme page conversion: evaluate niches, get playbooks, and monetization strategies."""
    pass


@theme_page.command("evaluate")
@click.option("--niche", required=True, help="Niche to evaluate (fitness, finance, luxury, etc.)")
def theme_page_evaluate(niche):
    """Score a niche for theme page viability: competition, CPM, monetization potential."""
    from .core import theme_page_guide as tpg
    result = tpg.evaluate_niche(niche=niche)
    output(result, f"Niche Evaluation — {niche.title()}")


@theme_page.command("playbook")
@click.option("--niche", required=True, help="Your theme page niche")
@click.option("--followers", default=0, type=int, show_default=True,
              help="Current follower count")
def theme_page_playbook(niche, followers):
    """Get a complete step-by-step playbook for building a profitable theme page."""
    from .core import theme_page_guide as tpg
    result = tpg.get_theme_page_playbook(niche=niche, current_followers=followers)
    output(result, f"Theme Page Playbook — {niche.title()}")


@theme_page.command("monetize")
@click.option("--niche", required=True, help="Your niche")
def theme_page_monetize(niche):
    """List all monetization strategies for your niche with setup guides."""
    from .core import theme_page_guide as tpg
    result = tpg.monetization_strategies(niche=niche)
    output(result, f"Monetization Strategies — {niche.title()}")


@theme_page.command("convert")
@click.option("--from-type", "from_type", default="personal",
              type=click.Choice(["personal", "blank", "meme"]),
              help="What type the current account is")
@click.option("--niche", required=True, help="Target niche after conversion")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]))
def theme_page_convert(from_type, niche, platform):
    """Step-by-step instructions to convert an existing account to a theme page."""
    from .core import theme_page_guide as tpg
    playbook = tpg.get_theme_page_playbook(niche=niche)

    conversion_steps = playbook["conversion_tips"]["from_personal_to_theme"]
    phase_1 = playbook["phases"][0]

    result = {
        "conversion": {
            "from": from_type,
            "to": f"{niche} theme page",
            "platform": platform,
        },
        "immediate_steps": conversion_steps,
        "week_1_plan": phase_1["tasks"],
        "content_curation_sources": playbook["conversion_tips"]["content_curation_sources"],
        "tools": playbook["tools_and_resources"],
        "warning": (
            "Changing your niche may cause a temporary drop in reach as the "
            "algorithm re-learns your audience. Post 7-10 new niche posts before "
            "worrying about performance — it takes 2-3 weeks to stabilize."
        ),
    }
    output(result, f"Account Conversion — {from_type.title()} → {niche.title()} Theme Page ({platform.title()})")


# ============================================================================
# Cache commands
# ============================================================================

@cli.group()
def cache():
    """Manage local trend data cache."""
    pass


@cache.command("info")
def cache_info():
    """Show cache status and stored entries."""
    from .core import cache as c
    result = c.info()
    output(result, "Cache Info")


@cache.command("clear")
@click.option("--key", default=None, help="Clear a specific cache key only")
def cache_clear(key):
    """Clear cached trend data (forces fresh scrape on next run)."""
    from .core import cache as c
    result = c.clear(key)
    output(result, "Cache cleared")


# ============================================================================
# REPL (Interactive mode)
# ============================================================================

@cli.command("repl")
def repl_cmd():
    """Start an interactive REPL for exploring trends and optimizations."""
    global _repl_mode
    _repl_mode = True

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.styles import Style
        pt_session = PromptSession()
    except ImportError:
        pt_session = None

    click.echo(click.style("\n Social Media CLI — Interactive Mode", fg="magenta", bold=True))
    click.echo(click.style(" Trend Intelligence & Account Optimization\n", fg="magenta"))
    click.echo("  Type 'help' for commands, 'quit' to exit\n")

    HELP_TEXT = {
        "trends youtube [--region US] [--limit 20]": "YouTube trending videos",
        "trends tiktok [--type hashtags|sounds|videos]": "TikTok trending content",
        "trends music [--region US]": "Trending music (both platforms)",
        "trends hashtags [--niche NICHE] [--platform all]": "Trending hashtags",
        "trends all": "Full trend snapshot",
        "optimize profile --platform PLATFORM --niche NICHE": "Profile checklist",
        "optimize hashtags --niche NICHE": "Hashtag set generator",
        "optimize strategy --niche NICHE": "Content strategy",
        "optimize schedule --platform PLATFORM": "Best posting times",
        "theme-page evaluate --niche NICHE": "Niche viability score",
        "theme-page playbook --niche NICHE": "Full theme page playbook",
        "theme-page monetize --niche NICHE": "Monetization strategies",
        "theme-page convert --niche NICHE": "Account conversion guide",
        "cache info": "Show cache status",
        "cache clear": "Clear trend cache",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            if pt_session:
                line = pt_session.prompt("social-media> ").strip()
            else:
                line = input("social-media> ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nBye!")
            break

        if not line:
            continue

        if line.lower() in ("quit", "exit", "q"):
            click.echo("Bye!")
            break

        if line.lower() == "help":
            click.echo(click.style("\nAvailable commands:\n", bold=True))
            for cmd, desc in HELP_TEXT.items():
                click.echo(f"  {click.style(cmd, fg='cyan')}")
                click.echo(f"    {desc}")
            click.echo()
            continue

        # Parse and execute via Click's runner
        from click.testing import CliRunner
        runner = CliRunner(mix_stderr=False)
        args = line.split()

        # Prepend --json if in JSON mode
        if _json_output:
            invoke_args = ["--json"] + args
        else:
            invoke_args = args

        try:
            result = runner.invoke(cli, invoke_args, catch_exceptions=False)
            if result.output:
                click.echo(result.output.rstrip())
            if result.exception:
                click.echo(click.style(f"Error: {result.exception}", fg="red"))
        except SystemExit:
            pass
        except Exception as e:
            click.echo(click.style(f"Error: {e}", fg="red"))


# ============================================================================
# Entry point
# ============================================================================

def main():
    cli()


if __name__ == "__main__":
    main()
